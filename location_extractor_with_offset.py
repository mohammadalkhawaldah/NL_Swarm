#!/usr/bin/env python3
"""
Enhanced location extraction with offset support for worldwide locations
Handles both:
1. Direct locations: "Delivery to Eiffel Tower"
2. Offset locations: "2km west of Amman"
"""

import re
import math
from geocoding_helper import geocode_location, display_and_confirm_location
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    print(f"[{get_timestamp()}] {message}")

# Known reference locations (local drone testing area)
REFERENCE_LOCATIONS = {
    "street gardens": [-35.36088387, 149.16674193],
    "desert square": [-35.36309804, 149.16348567],
    "alexander center area": [-35.37111574, 149.17183885],
    "village area": [-35.35723482, 149.17015126],
    "compound area": [-35.35389604, 149.15062472],
    "south sector area": [-35.363261, 149.165230]
}

def parse_offset_instruction(user_prompt):
    """
    Parse offset instructions like '2km to the west of Amman'
    Returns (distance_m, direction, reference_location) or None if not found.
    """
    # Pattern: [number] [km/meters] [to the] [direction] of [location]
    pattern = r"(\d+(?:\.\d+)?)\s*(km|kilometers?|m|meters?)\s+(?:to the\s+)?(?:to\s+)?(?:the\s+)?(north|south|east|west)\s+of\s+(.+)"
    
    match = re.search(pattern, user_prompt.lower())
    if not match:
        return None
    
    value, unit, direction, ref_location = match.groups()
    value = float(value)
    
    # Convert to meters
    if unit.startswith("km"):
        value *= 1000
    
    return value, direction, ref_location.strip()

def offset_coordinates(lat, lon, distance_m, direction):
    """Calculate new coordinates offset by distance (meters) in the given direction."""
    if direction in ["east", "west"]:
        # For longitude: 1 degree ≈ 111,320 × cos(latitude) meters
        meters_per_deg = 111320 * math.cos(math.radians(lat))
        delta = distance_m / meters_per_deg
        if direction == "west":
            delta = -delta
        return [lat, lon + delta]
    elif direction in ["north", "south"]:
        # For latitude: 1 degree ≈ 110,574 meters
        meters_per_deg = 110574
        delta = distance_m / meters_per_deg
        if direction == "south":
            delta = -delta
        return [lat + delta, lon]
    else:
        return [lat, lon]

def find_location_coordinates(location_name):
    """
    Find coordinates for a location (local or worldwide)
    Returns (coordinates, display_name) or None
    """
    # First check local locations
    loc_lower = location_name.lower().strip()
    for ref_name, ref_coords in REFERENCE_LOCATIONS.items():
        if ref_name in loc_lower or loc_lower in ref_name:
            print_with_timestamp(f"✅ Matched local location: {ref_name.title()}")
            return ref_coords, ref_name.title()
    
    # Not local, try geocoding
    print_with_timestamp(f"🔍 Searching worldwide for: '{location_name}'")
    locations = geocode_location(location_name)
    
    if not locations:
        return None
    
    # Let user confirm/select
    selected = display_and_confirm_location(locations, location_name)
    if not selected:
        return None
    
    coords = [selected['lat'], selected['lon']]
    return coords, selected['display_name']

def extract_location_from_prompt(user_prompt):
    """
    Extract location from prompt (direct or with offset) and geocode it.
    
    Handles:
    - Direct: "Delivery to Eiffel Tower, Paris"
    - Offset: "2km west of Amman"
    - Local: "Search at Desert Square"
    - Local with offset: "500m north of Desert Square"
    
    Returns:
        Tuple of (coordinates, location_name, reference_info) or None
        reference_info is dict with 'ref_name', 'ref_coords', 'offset_distance', 'offset_direction' if offset was used
    """
    
    # Step 1: Check for offset pattern
    offset_info = parse_offset_instruction(user_prompt)
    
    if offset_info:
        # Handle offset location
        distance_m, direction, ref_location = offset_info
        print_with_timestamp(f"🧭 Detected offset: {distance_m}m to the {direction} of '{ref_location}'")
        
        # Find reference location
        result = find_location_coordinates(ref_location)
        if not result:
            print_with_timestamp(f"❌ Could not find reference location: '{ref_location}'")
            return None
        
        ref_coords, ref_display_name = result
        print_with_timestamp(f"📍 Reference location: {ref_display_name}")
        print_with_timestamp(f"   Coordinates: {ref_coords[0]:.6f}, {ref_coords[1]:.6f}")
        
        # Calculate offset coordinates
        new_coords = offset_coordinates(ref_coords[0], ref_coords[1], distance_m, direction)
        print_with_timestamp(f"📍 Calculated target: {distance_m}m {direction}")
        print_with_timestamp(f"   Coordinates: {new_coords[0]:.6f}, {new_coords[1]:.6f}")
        
        # Create descriptive name
        if distance_m >= 1000:
            distance_str = f"{distance_m/1000:.1f}km"
        else:
            distance_str = f"{int(distance_m)}m"
        
        target_name = f"{distance_str} {direction} of {ref_display_name}"
        
        # Return with reference info
        reference_info = {
            'ref_name': ref_display_name,
            'ref_coords': ref_coords,
            'offset_distance': distance_m,
            'offset_direction': direction
        }
        
        return new_coords, target_name, reference_info
    
    else:
        # Handle direct location (no offset)
        user_lower = user_prompt.lower()
        
        # Check local locations first
        for ref_name, ref_coords in REFERENCE_LOCATIONS.items():
            if ref_name in user_lower:
                print_with_timestamp(f"✅ Matched local location: {ref_name.title()}")
                print_with_timestamp(f"📍 Coordinates: {ref_coords[0]:.6f}, {ref_coords[1]:.6f}")
                return ref_coords, ref_name.title(), None
        
        # Try to extract worldwide location name
        print_with_timestamp("🔍 Not a known local location, searching worldwide...")
        
        # Extract location name from prompt
        location_name = None
        patterns = [
            r"(?:at|in|to|near|around|over)\s+([A-Z][A-Za-z\s,'\-]+)",
            r"delivery (?:to|at)\s+([A-Z][A-Za-z\s,'\-]+)",
            r"search (?:at|in|around|over)\s+([A-Z][A-Za-z\s,'\-]+)",
            r"survey\s+(?:of|at|over)?\s*([A-Z][A-Za-z\s,'\-]+)",
            r"inspect\s+(?:at|the)?\s*([A-Z][A-Za-z\s,'\-]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_prompt)
            if match:
                location_name = match.group(1).strip()
                location_name = re.sub(r'\s+(area|zone|sector)$', '', location_name, flags=re.IGNORECASE)
                break
        
        if not location_name:
            print_with_timestamp("⚠️ Could not extract location name from prompt")
            print_with_timestamp("💡 Try using patterns like:")
            print_with_timestamp("   - 'Deliver to Eiffel Tower, Paris'")
            print_with_timestamp("   - '2km west of Amman'")
            print_with_timestamp("   - 'Search at Desert Square'")
            return None
        
        print_with_timestamp(f"🔍 Extracted location: '{location_name}'")
        
        # Geocode the location
        result = find_location_coordinates(location_name)
        if not result:
            return None
        
        coords, display_name = result
        print_with_timestamp(f"✅ Location confirmed: {display_name}")
        print_with_timestamp(f"📍 Coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
        
        return coords, display_name, None


if __name__ == "__main__":
    # Test
    print_with_timestamp("🧪 Testing Enhanced Location Extraction with Offsets")
    print_with_timestamp("="*70)
    
    test_prompts = [
        "Search at Desert Square",  # Local direct
        "Delivery to Eiffel Tower, Paris",  # Worldwide direct
        "Survey 2km west of Amman",  # Worldwide with offset
        "Inspect 500 meters north of Desert Square",  # Local with offset
        "Search 1.5km east of Sydney Opera House"  # Worldwide with offset
    ]
    
    for prompt in test_prompts:
        print_with_timestamp(f"\n📝 Testing: '{prompt}'")
        print_with_timestamp("-"*70)
        result = extract_location_from_prompt(prompt)
        if result:
            coords, name, ref_info = result
            print_with_timestamp(f"✅ Result: {name}")
            print_with_timestamp(f"📍 Coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
            if ref_info:
                print_with_timestamp(f"🗺️ Reference: {ref_info['ref_name']}")
                print_with_timestamp(f"↔️ Offset: {ref_info['offset_distance']}m {ref_info['offset_direction']}")
        else:
            print_with_timestamp("❌ Failed")
        print_with_timestamp("")
