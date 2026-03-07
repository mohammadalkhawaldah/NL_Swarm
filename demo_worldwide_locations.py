#!/usr/bin/env python3
"""
Demo: Worldwide Location Support with Google Maps Confirmation
Shows how users can specify ANY location worldwide and confirm on Google Maps
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

def demo_workflow(user_prompt):
    """Demonstrate the complete workflow"""
    print_with_timestamp("\n" + "="*70)
    print_with_timestamp(f"📝 User says: '{user_prompt}'")
    print_with_timestamp("="*70)
    
    # Step 1: Extract and geocode location
    result = extract_location_from_prompt(user_prompt)
    
    if not result:
        print_with_timestamp("❌ Failed to extract location")
        return False
    
    coords, location_name = result
    
    # Step 2: Show on Google Maps automatically
    print_with_timestamp("\n🗺️ Opening location on Google Maps...")
    show_location_on_google_maps(coords[0], coords[1], location_name)
    
    # Step 3: Ask user to confirm after viewing map
    print_with_timestamp("\n✅ Please check the map in your browser")
    confirm = input("Is this the correct location for your mission? (y/n): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        print_with_timestamp("✅ Location confirmed! Mission can proceed.")
        print_with_timestamp(f"📍 Final coordinates: {coords[0]:.6f}, {coords[1]:.6f}")
        return True
    else:
        print_with_timestamp("❌ Location not confirmed. Please try again with a more specific description.")
        return False

def main():
    print_with_timestamp("🌍 WORLDWIDE LOCATION SUPPORT DEMO")
    print_with_timestamp("="*70)
    print_with_timestamp("")
    print_with_timestamp("This demo shows how you can specify ANY location worldwide!")
    print_with_timestamp("")
    print_with_timestamp("How it works:")
    print_with_timestamp("1. You describe your mission with a location")
    print_with_timestamp("2. System extracts and finds the location")
    print_with_timestamp("3. Google Maps opens automatically to show the location")
    print_with_timestamp("4. You confirm if it's correct")
    print_with_timestamp("5. Mission proceeds with confirmed coordinates")
    print_with_timestamp("")
    print_with_timestamp("="*70)
    
    # Demo scenarios
    scenarios = [
        {
            "title": "🗼 Famous Landmark",
            "prompt": "Delivery to Eiffel Tower, Paris"
        },
        {
            "title": "🏛️ Historic Site",
            "prompt": "Survey Sydney Opera House"
        },
        {
            "title": "🌆 City Location", 
            "prompt": "Search at Times Square, New York"
        },
        {
            "title": "📍 Local Testing Area",
            "prompt": "Inspect Desert Square"
        }
    ]
    
    for idx, scenario in enumerate(scenarios, 1):
        print_with_timestamp(f"\n\n{'#'*70}")
        print_with_timestamp(f"DEMO {idx}/{len(scenarios)}: {scenario['title']}")
        print_with_timestamp(f"{'#'*70}")
        
        success = demo_workflow(scenario['prompt'])
        
        if idx < len(scenarios):
            cont = input(f"\n▶️  Continue to next demo? (y/n): ").strip().lower()
            if cont not in ['y', 'yes']:
                break
    
    print_with_timestamp("\n\n" + "="*70)
    print_with_timestamp("🎉 DEMO COMPLETE!")
    print_with_timestamp("="*70)
    print_with_timestamp("")
    print_with_timestamp("💡 Key Features:")
    print_with_timestamp("✅ Supports ANY location worldwide")
    print_with_timestamp("✅ Finds location automatically via geocoding")
    print_with_timestamp("✅ Shows location on Google Maps")
    print_with_timestamp("✅ You confirm before proceeding")
    print_with_timestamp("✅ No API key needed for basic geocoding")
    print_with_timestamp("")
    print_with_timestamp("📍 Example prompts you can use:")
    print_with_timestamp("   - 'Deliver to Big Ben, London'")
    print_with_timestamp("   - 'Search at Golden Gate Bridge'")
    print_with_timestamp("   - 'Survey Statue of Liberty'")
    print_with_timestamp("   - 'Inspect Burj Khalifa, Dubai'")
    print_with_timestamp("   - 'Delivery to Tokyo Tower'")
    print_with_timestamp("")

if __name__ == "__main__":
    main()
