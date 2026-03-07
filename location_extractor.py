#!/usr/bin/env python3
"""
Simplified worldwide location extraction with geocoding confirmation
"""

import re
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

def extract_location_from_prompt(user_prompt):
    """
    Extract location from prompt and geocode it.
    Returns (coordinates, location_name) or None
    
    Process:
    1. Check if it's a known local reference location
    2. If not, try to extract location name and geocode it worldwide
    3. Show results on map and ask for confirmation
    """
    user_lower = user_prompt.lower()
    
    # Step 1: Check known local locations first
    for ref_name, ref_coords in REFERENCE_LOCATIONS.items():
        # Check if any keyword from the reference name appears in the prompt
        if ref_name in user_lower:
            print_with_timestamp(f"✅ Matched local location: {ref_name.title()}")
            print_with_timestamp(f"📍 Coordinates: {ref_coords[0]:.6f}, {ref_coords[1]:.6f}")
            return ref_coords, ref_name.title()
    
    # Step 2: Try to extract worldwide location name
    print_with_timestamp("🔍 Not a known local location, searching worldwide...")
    
    # Try to extract location name from the prompt
    location_name = None
    
    # Pattern 1: "at/in/to/near [Location]"
    patterns = [
        r"(?:at|in|to|near|around|over)\s+([A-Z][A-Za-z\s,'\-]+(?:Tower|Bridge|Square|Park|Building|Street|Avenue|City|Airport|Stadium|Museum|Church|Temple|Palace|Castle|Harbor|Beach|Mountain|Lake|River|Island|Hall|Center)?)",
        r"delivery (?:to|at)\s+([A-Z][A-Za-z\s,'\-]+)",
        r"search (?:at|in|around|over)\s+([A-Z][A-Za-z\s,'\-]+)",
        r"survey\s+(?:of|at|over)?\s*([A-Z][A-Za-z\s,'\-]+)",
        r"inspect\s+(?:at|the)?\s*([A-Z][A-Za-z\s,'\-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_prompt)
        if match:
            location_name = match.group(1).strip()
            # Clean up trailing words that aren't part of the location
            location_name = re.sub(r'\s+(area|zone|sector)$', '', location_name, flags=re.IGNORECASE)
            break
    
    if not location_name:
        print_with_timestamp("⚠️ Could not extract location name from prompt")
        print_with_timestamp("💡 Try using a clear location like:")
        print_with_timestamp("   - 'Deliver to Eiffel Tower, Paris'")
        print_with_timestamp("   - 'Search at Sydney Opera House'")
        print_with_timestamp("   - 'Survey Times Square, New York'")
        return None
    
    print_with_timestamp(f"🔍 Extracted location: '{location_name}'")
    
    # Step 3: Geocode the location
    locations = geocode_location(location_name)
    if not locations:
        print_with_timestamp("❌ Could not find location. Try being more specific.")
        return None
    
    # Step 4: Let user confirm/select
    selected = display_and_confirm_location(locations, location_name)
    if not selected:
        print_with_timestamp("❌ Location not confirmed")
        return None
    
    # Step 5: Return confirmed coordinates
    coords = [selected['lat'], selected['lon']]
    display_name = selected['display_name']
    
    print_with_timestamp(f"✅ Location confirmed: {display_name}")
    print_with_timestamp(f"📍 Coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
    
    return coords, display_name


if __name__ == "__main__":
    # Test
    print_with_timestamp("🧪 Testing Location Extraction")
    print_with_timestamp("="*70)
    
    test_prompts = [
        "Search at Desert Square",  # Local
        "Delivery to Eiffel Tower, Paris",  # Worldwide
        "Survey Sydney Opera House",  # Worldwide
        "Inspect at Street Gardens"  # Local
    ]
    
    for prompt in test_prompts:
        print_with_timestamp(f"\n📝 Testing: '{prompt}'")
        result = extract_location_from_prompt(prompt)
        if result:
            coords, name = result
            print_with_timestamp(f"✅ Result: {name} at {coords}")
        else:
            print_with_timestamp("❌ Failed")
        print_with_timestamp("-"*70)
