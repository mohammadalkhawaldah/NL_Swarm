#!/usr/bin/env python3
"""
Test the improved geocoding for Zarqa Jordan
"""

import sys
import os
sys.path.append('/home/moham/mavsdk_bin/mini')

from geocoding_helper import geocode_location

def test_improved_geocoding():
    """Test the improved geocoding system"""
    test_locations = [
        "Zarqa Jordan",
        "Balama Jordan", 
        "Paris France",
        "Sydney Australia",
        "Newcastle Australia"
    ]
    
    for location in test_locations:
        print(f"\n🧪 Testing: '{location}'")
        print("=" * 50)
        
        result = geocode_location(location)
        if result:
            print(f"✅ Found {len(result)} result(s):")
            for i, loc in enumerate(result[:3]):  # Show top 3
                print(f"  Result {i+1}:")
                print(f"    Name: {loc['display_name']}")
                print(f"    Coordinates: {loc['lat']}, {loc['lon']}")
                print(f"    Type: {loc['type']}")
        else:
            print("❌ No results found")

if __name__ == "__main__":
    print("🧪 TESTING IMPROVED GEOCODING SYSTEM")
    print("=" * 60)
    test_improved_geocoding()
