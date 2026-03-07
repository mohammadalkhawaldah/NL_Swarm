#!/usr/bin/env python3
"""
Quick test of map visualizers
"""

print("Testing map visualizer imports...")
print("="*60)

try:
    from map_visualizer_enhanced import open_enhanced_map, open_simple_google_maps
    print("✅ Enhanced visualizer imports: OK")
except Exception as e:
    print(f"❌ Enhanced visualizer error: {e}")

try:
    from map_visualizer_osm import generate_osm_map_with_reference
    print("✅ OSM visualizer imports: OK")
except Exception as e:
    print(f"❌ OSM visualizer error: {e}")

print("="*60)
print()
print("✅ All imports successful!")
print()
print("You can now run:")
print("  python demo_map_visualization.py")
print()
print("And choose from:")
print("  1) Enhanced HTML (Google Maps)")
print("  2) OpenStreetMap (no API key)")  
print("  3) Simple Google Maps URL")
print()
