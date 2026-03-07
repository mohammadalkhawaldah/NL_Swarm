#!/usr/bin/env python3
"""
Unified location handler - Handles both direct locations and offsets
Supports worldwide locations with offset calculations
Uses OpenAI Structured Outputs for reliable information extraction
"""

import re
import math
import os
from datetime import datetime
from geocoding_helper import geocode_location, display_and_confirm_location
from map_simple_fallback import show_location_on_google_maps
from location_extractor_ai import extract_location_info_with_ai
from dotenv import load_dotenv

# Load API key
load_dotenv('/home/moham/mavsdk_bin/.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    print(f"[{get_timestamp()}] {message}")

# Known local reference locations (for backward compatibility)
LOCAL_REFERENCE_LOCATIONS = {
    "street gardens": [-35.36088387, 149.16674193],
    "desert square": [-35.36309804, 149.16348567],
    "alexander center area": [-35.37111574, 149.17183885],
    "village area": [-35.35723482, 149.17015126],
    "compound area": [-35.35389604, 149.15062472],
    "south sector area": [-35.363261, 149.165230]
}

def parse_offset_instruction(user_prompt):
    """
    Parse offset instructions like '2km to the west of Amman' or '500 meters north of Paris'
    Returns (distance_m, direction, reference_location) or None if not found.
    """
    # Pattern: NUMBER UNIT DIRECTION of LOCATION
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(km|kilometers?|meters?|m)\s+(?:to the\s+)?(north|south|east|west)\s+of\s+(.+?)(?:\.|$|,)",
        r"(\d+(?:\.\d+)?)\s*(km|kilometers?|meters?|m)\s+(?:to the\s+)?(north|south|east|west)\s+of\s+([A-Z][^\.,!?]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_prompt, re.IGNORECASE)
        if match:
            value_str, unit, direction, ref_location = match.groups()
            value = float(value_str)
            
            # Convert to meters
            if unit.lower().startswith('km'):
                value *= 1000
            
            # Clean up reference location - remove common filler words
            ref_location = ref_location.strip()
            # Remove "the capital", "the city of", etc.
            ref_location = re.sub(r'^(?:the\s+)?(?:capital|city|town|village)(?:\s+of)?\s+', '', ref_location, flags=re.IGNORECASE)
            ref_location = ref_location.strip()
            
            return value, direction.lower(), ref_location
    
    return None

def offset_coordinates(lat, lon, distance_m, direction):
    """
    Calculate new coordinates offset by distance_m (meters) in the given direction.
    Uses proper geodetic calculations.
    """
    direction = direction.lower()
    
    if direction in ["east", "west"]:
        # For east/west: adjust longitude
        # 1 degree longitude = 111,320 * cos(latitude) meters
        meters_per_deg = 111320 * math.cos(math.radians(lat))
        delta_lon = distance_m / meters_per_deg
        
        if direction == "west":
            delta_lon = -delta_lon
        
        return [lat, lon + delta_lon]
    
    elif direction in ["north", "south"]:
        # For north/south: adjust latitude
        # 1 degree latitude ≈ 110,574 meters
        meters_per_deg = 110574
        delta_lat = distance_m / meters_per_deg
        
        if direction == "south":
            delta_lat = -delta_lat
        
        return [lat + delta_lat, lon]
    
    else:
        print_with_timestamp(f"⚠️ Unknown direction: {direction}")
        return [lat, lon]

def get_location_coordinates(location_name, is_offset_reference=False):
    """
    Get coordinates for a location name (local or worldwide).
    
    Args:
        location_name: Name of the location
        is_offset_reference: True if this is a reference location for offset calculation
    
    Returns:
        (coords, display_name) tuple or None
    """
    location_lower = location_name.lower().strip()
    
    # Step 1: Check if it's a known local location
    for local_name, local_coords in LOCAL_REFERENCE_LOCATIONS.items():
        if local_name in location_lower or location_lower in local_name:
            print_with_timestamp(f"✅ Matched local location: {local_name.title()}")
            return local_coords, local_name.title()
    
    # Step 2: Geocode worldwide
    print_with_timestamp(f"🌍 Searching worldwide for: '{location_name}'")
    locations = geocode_location(location_name)
    
    if not locations:
        return None
    
    # Step 3: Let user confirm
    selected = display_and_confirm_location(locations, location_name)
    
    if not selected:
        return None
    
    coords = [selected['lat'], selected['lon']]
    display_name = selected['display_name']
    
    return coords, display_name

def process_location_with_offset(user_prompt):
    """
    Process user prompt to extract location with optional offset.
    Uses OpenAI Structured Outputs for reliable extraction, then Python calculates coordinates.
    
    This is the MAIN function that handles:
    1. Direct locations (e.g., "Delivery to Paris")
    2. Offset locations (e.g., "2km west of Amman")
    
    Returns:
        dict with keys:
        - 'coords': [lat, lon]
        - 'name': location name
        - 'has_offset': boolean
        - 'reference': reference location info (if has_offset)
    
    Or None if failed
    """
    print_with_timestamp("📍 Using AI to analyze location in prompt...")
    
    # Step 1: Use AI to extract location information (structured outputs)
    if not OPENAI_API_KEY:
        print_with_timestamp("❌ OpenAI API key not found")
        return None
    
    location_data = extract_location_info_with_ai(user_prompt, OPENAI_API_KEY)
    
    if not location_data:
        print_with_timestamp("❌ Could not extract location information")
        return None
    
    # Step 2: Process based on whether it's offset or direct
    if location_data.offset_location:
        # OFFSET CASE: AI extracted offset information
        offset = location_data.offset_location
        print_with_timestamp(f"🧭 AI detected OFFSET location:")
        print_with_timestamp(f"   {offset.distance_value} {offset.distance_unit} {offset.direction} of '{offset.reference_location}'")
        
        # Convert distance to meters
        distance_m = offset.distance_value
        if offset.distance_unit in ["km", "kilometers"]:
            distance_m *= 1000
        
        # Get reference location coordinates
        print_with_timestamp(f"\n🔍 Step 1: Finding reference location '{offset.reference_location}'...")
        ref_result = get_location_coordinates(offset.reference_location, is_offset_reference=True)
        
        if not ref_result:
            print_with_timestamp(f"❌ Could not find reference location: '{offset.reference_location}'")
            return None
        
        ref_coords, ref_name = ref_result
        print_with_timestamp(f"✅ Reference location: {ref_name}")
        print_with_timestamp(f"📍 Reference coordinates: {ref_coords[0]:.6f}, {ref_coords[1]:.6f}")
        
        # Show reference location on map
        print_with_timestamp("\n🗺️ Step 2: Showing reference location on map...")
        show_location_on_google_maps(ref_coords[0], ref_coords[1], f"Reference: {ref_name}")
        
        # Calculate offset coordinates (PYTHON DOES THIS, NOT AI!)
        print_with_timestamp(f"\n🧮 Step 3: Calculating offset ({distance_m}m {offset.direction})...")
        target_coords = offset_coordinates(ref_coords[0], ref_coords[1], distance_m, offset.direction)
        print_with_timestamp(f"📍 Target coordinates: {target_coords[0]:.6f}, {target_coords[1]:.6f}")
        
        # Show target location on map
        print_with_timestamp("\n🗺️ Step 4: Showing target location on map...")
        target_name = f"{distance_m}m {offset.direction} of {ref_name}"
        show_location_on_google_maps(target_coords[0], target_coords[1], target_name)
        
        # Confirm with user
        print_with_timestamp("\n💡 Please check both locations on the map")
        confirm = input("✅ Are both locations correct? (y/n): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print_with_timestamp("❌ Locations not confirmed")
            return None
        
        print_with_timestamp("✅ Locations confirmed!")
        
        return {
            'coords': target_coords,
            'name': target_name,
            'has_offset': True,
            'reference': {
                'name': ref_name,
                'coords': ref_coords,
                'distance': distance_m,
                'direction': offset.direction
            }
        }
    
    elif location_data.direct_location:
        # DIRECT CASE: AI extracted direct location
        direct = location_data.direct_location
        print_with_timestamp(f"📍 AI detected DIRECT location: '{direct.location_name}'")
        
        # Get coordinates
        result = get_location_coordinates(direct.location_name)
        
        if not result:
            return None
        
        coords, display_name = result
        
        # Show on map and confirm
        print_with_timestamp("\n🗺️ Showing location on map...")
        show_location_on_google_maps(coords[0], coords[1], display_name)
        
        print_with_timestamp("\n💡 Please check the map in your browser")
        confirm = input("✅ Is this the correct location? (y/n): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print_with_timestamp("❌ Location not confirmed")
            return None
        
        print_with_timestamp("✅ Location confirmed!")
        
        return {
            'coords': coords,
            'name': display_name,
            'has_offset': False,
            'reference': None
        }
    
    else:
        print_with_timestamp("❌ AI did not extract location information")
        return None


if __name__ == "__main__":
    # Test cases
    print_with_timestamp("🧪 Testing Unified Location Handler")
    print_with_timestamp("="*70)
    
    test_cases = [
        "Delivery to Eiffel Tower, Paris",
        "2km west of Amman, Jordan",
        "500 meters north of Sydney Opera House",
        "Search at Desert Square"
    ]
    
    for test in test_cases:
        print_with_timestamp(f"\n\n📝 Test: '{test}'")
        print_with_timestamp("-"*70)
        
        result = process_location_with_offset(test)
        
        if result:
            print_with_timestamp("\n✅ SUCCESS!")
            print_with_timestamp(f"📍 Final coordinates: {result['coords']}")
            print_with_timestamp(f"🏷️  Location name: {result['name']}")
            if result['has_offset']:
                print_with_timestamp(f"🧭 Offset from: {result['reference']['name']}")
        else:
            print_with_timestamp("\n❌ FAILED")
        
        cont = input("\n▶️  Continue to next test? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            break
