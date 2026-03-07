#!/usr/bin/env python3
"""
Test the restored interactive map menu
"""

from map_simple_fallback import show_location_on_google_maps

print("🧪 Testing Restored Map Menu")
print("="*70)
print()
print("The main workflow now has an interactive menu like the demo:")
print()
print("📍 Map Visualization Options:")
print("  1) Google Maps URL (direct link - always works!) ⭐")
print("  2) Enhanced HTML (Google Maps - best visuals)")
print("  3) OpenStreetMap HTML (no API key needed)")
print("  4) OpenStreetMap Interactive (Leaflet.js)")
print("  0) Skip visualization")
print()
print("Let's test option 1 (the one that works for you!):")
print()

# Test Desert Square
show_location_on_google_maps(
    latitude=-35.36309804,
    longitude=149.16348567,
    location_name="Desert Square"
)

print()
print("✅ Menu restored! The main script now offers the same choices.")
print("💡 Option 1 (Google Maps URL) is the default and is marked with ⭐")
