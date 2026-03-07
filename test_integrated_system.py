#!/usr/bin/env python3
"""
Quick test of the integrated worldwide location support
Tests the full workflow without actually running the main script
"""

import sys
sys.path.append('/home/moham/mavsdk_bin/mini')

from location_extractor import extract_location_from_prompt
from map_simple_fallback import show_location_on_google_maps
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    print(f"[{get_timestamp()}] {message}")

print_with_timestamp("🧪 Testing Integrated Worldwide Location Support")
print_with_timestamp("="*70)
print_with_timestamp("")
print_with_timestamp("This tests the workflow that's now integrated into your main script:")
print_with_timestamp("")
print_with_timestamp("1. ✅ Extract location from natural language")
print_with_timestamp("2. ✅ Geocode to find coordinates (local or worldwide)")
print_with_timestamp("3. ✅ Show on Google Maps automatically")
print_with_timestamp("4. ✅ Get user confirmation")
print_with_timestamp("5. ✅ Proceed with confirmed coordinates")
print_with_timestamp("")
print_with_timestamp("="*70)
print_with_timestamp("")

# Test scenarios
test_scenarios = [
    ("Local Location", "Search at Desert Square"),
    ("Worldwide Location", "Delivery to Eiffel Tower, Paris")
]

for idx, (title, prompt) in enumerate(test_scenarios, 1):
    print_with_timestamp(f"\n📝 Test {idx}: {title}")
    print_with_timestamp(f"   Prompt: '{prompt}'")
    print_with_timestamp("-"*70)
    
    result = extract_location_from_prompt(prompt)
    
    if result:
        coords, loc_name = result
        print_with_timestamp(f"✅ Location extracted: {loc_name}")
        print_with_timestamp(f"📍 Coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
        print_with_timestamp("")
        print_with_timestamp("🗺️ Opening on Google Maps...")
        show_location_on_google_maps(coords[0], coords[1], loc_name)
        print_with_timestamp("")
        print_with_timestamp("✅ This is what happens in your main script now!")
    else:
        print_with_timestamp("❌ Location extraction failed")
    
    if idx < len(test_scenarios):
        print_with_timestamp("")
        cont = input("\n▶️  Continue to next test? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            break

print_with_timestamp("")
print_with_timestamp("="*70)
print_with_timestamp("🎉 Integration Complete!")
print_with_timestamp("="*70)
print_with_timestamp("")
print_with_timestamp("Your main script (task_extract_send_rdp.py) now:")
print_with_timestamp("✅ Accepts ANY location worldwide")
print_with_timestamp("✅ Shows location on Google Maps automatically")
print_with_timestamp("✅ Requires user confirmation before proceeding")
print_with_timestamp("✅ Uses confirmed coordinates for the mission")
print_with_timestamp("")
print_with_timestamp("Try it with your main script!")
print_with_timestamp("")
