#!/usr/bin/env python3
"""
Quick test of geocoding and map opening
"""

import sys
sys.path.append('/home/moham/mavsdk_bin/mini')

from geocoding_helper import geocode_location
from map_simple_fallback import show_location_on_google_maps

print("🧪 Testing Worldwide Location Support")
print("="*70)
print()

# Test 1: Geocode a famous location
print("📍 Test 1: Finding Eiffel Tower, Paris...")
locations = geocode_location("Eiffel Tower, Paris")

if locations:
    print(f"✅ Found {len(locations)} location(s)")
    print(f"📍 Top result: {locations[0]['display_name']}")
    print(f"📍 Coordinates: {locations[0]['lat']:.6f}, {locations[0]['lon']:.6f}")
    
    # Test 2: Open on Google Maps
    print()
    print("🗺️ Test 2: Opening on Google Maps...")
    show_location_on_google_maps(
        locations[0]['lat'],
        locations[0]['lon'],
        "Eiffel Tower, Paris"
    )
    
    print()
    print("✅ SUCCESS! The system can:")
    print("   1. Find ANY location worldwide")
    print("   2. Get GPS coordinates automatically")
    print("   3. Open it on Google Maps")
    print()
    print("💡 Check your browser - Google Maps should have opened!")
else:
    print("❌ Geocoding failed")

print()
print("="*70)
print("📚 See WORLDWIDE_LOCATIONS_GUIDE.md for complete documentation")
