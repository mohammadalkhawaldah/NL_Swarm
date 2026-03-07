#!/usr/bin/env python3
"""
Demo: Enhanced Map Visualization
Shows how the map feature works with different scenarios
"""

import sys
sys.path.append('/home/moham/mavsdk_bin/mini')

from map_visualizer_enhanced import open_enhanced_map, open_simple_google_maps
from map_visualizer_osm import generate_osm_map_with_reference

# Known reference locations
reference_locations = {
    "street gardens": [-35.36088387, 149.16674193],
    "desert square": [-35.36309804, 149.16348567],
    "alexander center area": [-35.37111574, 149.17183885],
    "village area": [-35.35723482, 149.17015126],
    "compound area": [-35.35389604, 149.15062472],
    "south sector area": [-35.363261, 149.165230],
}

def demo_scenario(scenario_num, ref_name, distance, direction, target_coords):
    """Demo a single scenario"""
    print(f"\n{'='*70}")
    print(f"📋 SCENARIO {scenario_num}: {distance}m {direction} of {ref_name}")
    print(f"{'='*70}")
    
    ref_key = ref_name.lower()
    if ref_key in reference_locations:
        ref_coords = reference_locations[ref_key]
        
        print(f"🔵 Reference: {ref_name.title()}")
        print(f"   📍 {ref_coords[0]:.6f}, {ref_coords[1]:.6f}")
        print(f"🔴 Target: {distance}m {direction}")
        print(f"   📍 {target_coords[0]:.6f}, {target_coords[1]:.6f}")
        print()
        
        # Ask user which map to open
        print("Choose map type:")
        print("  1) Enhanced HTML (Google Maps - best visuals)")
        print("  2) OpenStreetMap (no API key needed)")
        print("  3) Simple Google Maps URL (direct link)")
        print("  4) Skip visualization")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🗺️  Opening Enhanced HTML Map...")
            open_enhanced_map(ref_coords, target_coords, ref_name.title(), distance, direction)
        elif choice == "2":
            print("\n🗺️  Opening OpenStreetMap...")
            import webbrowser
            filepath = generate_osm_map_with_reference(target_coords, ref_coords, ref_name.title(), {
                'distance': distance,
                'direction': direction
            })
            webbrowser.open('file://' + filepath)
            print(f"✅ Map saved to: {filepath}")
        elif choice == "3":
            print("\n🗺️  Opening Simple Google Maps...")
            open_simple_google_maps(ref_coords, target_coords, ref_name.title(), distance, direction)
        else:
            print("\n⏭️  Skipping visualization")
    else:
        print(f"❌ Unknown location: {ref_name}")

def main():
    print("🗺️  ENHANCED MAP VISUALIZATION DEMO")
    print("="*70)
    print()
    print("This demo shows how the enhanced map visualization works.")
    print("Each scenario will display BOTH the reference location and target.")
    print()
    
    # Scenario 1: 700m south of Desert Square
    demo_scenario(
        1,
        "Desert Square",
        700,
        "south",
        [-35.36942804, 149.16348567]
    )
    
    # Ask if user wants to see more scenarios
    more = input("\n\nView more scenarios? (yes/no): ").strip().lower()
    if more != 'yes':
        return
    
    # Scenario 2: 500m east of Street Gardens
    demo_scenario(
        2,
        "Street Gardens",
        500,
        "east",
        [-35.36088387, 149.17123393]
    )
    
    more = input("\n\nView more scenarios? (yes/no): ").strip().lower()
    if more != 'yes':
        return
    
    # Scenario 3: 300m northwest of Village Area
    demo_scenario(
        3,
        "Village Area",
        300,
        "northwest",
        [-35.35512241, 149.16802885]
    )
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print()
    print("💡 Key Features You Just Saw:")
    print("   🔵 Blue marker = Reference location")
    print("   🔴 Red marker = Target location")
    print("   ➡️  Orange line = Flight path with direction")
    print("   📊 Info panel = Mission details")
    print("   🗺️  Interactive map = Zoom, pan, click markers")
    print()
    print("📂 Maps are saved to /tmp/ for later review")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
