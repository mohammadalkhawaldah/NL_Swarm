#!/usr/bin/env python3
"""
Test geocoding for Zarqa Jordan to debug the issue
"""

import sys
import os
sys.path.append('/home/moham/mavsdk_bin/mini')

from geocoding_helper import geocode_location
import requests
from dotenv import load_dotenv

load_dotenv()

def test_google_maps_direct():
    """Test Google Maps API directly with different variations"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ No Google Maps API key found")
        return
    
    test_queries = [
        "Zarqa Jordan",
        "Az Zarqa Jordan", 
        "Zarqa, Jordan",
        "Az Zarqa, Jordan",
        "Zarqa city Jordan",
        "Zarqa Governorate Jordan"
    ]
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("=" * 50)
        
        params = {
            'address': query,
            'key': api_key
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data.get('results'):
                for i, result in enumerate(data['results'][:3]):  # Show top 3
                    geometry = result['geometry']['location']
                    print(f"  Result {i+1}:")
                    print(f"    Name: {result['formatted_address']}")
                    print(f"    Coordinates: {geometry['lat']}, {geometry['lng']}")
                    print(f"    Types: {', '.join(result.get('types', []))}")
                    print(f"    Place ID: {result.get('place_id', 'N/A')}")
            else:
                print(f"    Status: {data.get('status', 'unknown')}")
                
        except Exception as e:
            print(f"    Error: {e}")

def test_system_geocoding():
    """Test our system's geocoding function"""
    print("\n🧪 Testing our system's geocoding...")
    print("=" * 50)
    
    result = geocode_location("Zarqa Jordan")
    if result:
        print(f"✅ System result:")
        for i, loc in enumerate(result):
            print(f"  Location {i+1}:")
            print(f"    Name: {loc['display_name']}")
            print(f"    Coordinates: {loc['lat']}, {loc['lon']}")
            print(f"    Type: {loc['type']}")
    else:
        print("❌ System returned no results")

if __name__ == "__main__":
    print("🔍 DEBUGGING ZARQA JORDAN GEOCODING ISSUE")
    print("=" * 60)
    
    # Test Google Maps API directly with variations
    test_google_maps_direct()
    
    # Test our system
    test_system_geocoding()
    
    print("\n💡 EXPECTED RESULT:")
    print("   Zarqa (or Az Zarqa) should be around:")
    print("   Latitude: ~32.07")
    print("   Longitude: ~36.09") 
    print("   It's a major city in Jordan, east of Amman")
