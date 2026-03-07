#!/usr/bin/env python3
"""
Test the complete system with Zarqa Jordan like the original issue
"""

import sys
import os
sys.path.append('/home/moham/mavsdk_bin/mini')

from location_extractor_ai import extract_location_info

def test_zarqa_complete_system():
    """Test the complete system with the problematic input"""
    
    test_input = "Search for a red car in Jordan in the city of Zarqa."
    
    print(f"🧪 TESTING COMPLETE SYSTEM")
    print("=" * 60)
    print(f"📝 Input: '{test_input}'")
    print("=" * 60)
    
    try:
        result = extract_location_info(test_input)
        
        if result:
            print("✅ EXTRACTION SUCCESSFUL!")
            print(f"📍 Location Type: {result.get('location_type', 'Unknown')}")
            
            if 'direct_location' in result:
                direct = result['direct_location']
                print(f"🎯 Direct Location:")
                print(f"   Name: {direct.get('name', 'N/A')}")
                if 'coordinates' in direct:
                    coords = direct['coordinates']
                    print(f"   Coordinates: {coords.get('lat', 'N/A')}, {coords.get('lon', 'N/A')}")
                    print(f"   Display Name: {coords.get('display_name', 'N/A')}")
                    
                    # Check if this is the correct Zarqa
                    lat = coords.get('lat', 0)
                    if isinstance(lat, (int, float)) and 32.0 <= lat <= 32.1:
                        print("✅ CORRECT: This appears to be Zarqa city (latitude ~32.06)")
                    else:
                        print("❌ INCORRECT: This doesn't appear to be Zarqa city")
                        
        else:
            print("❌ EXTRACTION FAILED!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_zarqa_complete_system()
