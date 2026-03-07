#!/usr/bin/env python3
"""
Geocoding helper - Convert location names to coordinates
Uses Google Maps API (primary) with OpenStreetMap Nominatim fallback
"""

import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    """Print message with timestamp prefix"""
    print(f"[{get_timestamp()}] {message}")

def geocode_with_google_maps(location_name, timeout=10):
    """
    Convert a location name to coordinates using Google Maps Geocoding API
    
    Args:
        location_name: Name of the location
        timeout: Request timeout in seconds
    
    Returns:
        list of location dicts or None if not found
    """
    try:
        # Get API key from environment
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            print_with_timestamp("⚠️ Google Maps API key not found in .env file")
            return None
        
        print_with_timestamp(f"🗺️ Looking up location with Google Maps: '{location_name}'...")
        
        # Google Maps Geocoding API endpoint
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        
        # Prepare request parameters
        params = {
            'address': location_name,
            'key': api_key
        }
        
        # Make request
        response = requests.get(base_url, params=params, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # Check status
        if data['status'] == 'OK' and data.get('results'):
            locations = []
            for result in data['results'][:10]:  # Top 10 results
                geometry = result['geometry']['location']
                locations.append({
                    'lat': float(geometry['lat']),
                    'lon': float(geometry['lng']),
                    'display_name': result['formatted_address'],
                    'type': result.get('types', ['unknown'])[0],
                    'importance': 1.0  # Google doesn't provide importance score
                })
            
            print_with_timestamp(f"✅ Google Maps found {len(locations)} location(s)")
            return locations
        elif data['status'] == 'ZERO_RESULTS':
            print_with_timestamp(f"❌ Google Maps: No results for '{location_name}'")
            return None
        elif data['status'] == 'OVER_QUERY_LIMIT':
            print_with_timestamp(f"⚠️ Google Maps: Query limit exceeded (quota/billing issue)")
            return None
        else:
            print_with_timestamp(f"⚠️ Google Maps error: {data.get('status', 'unknown')}")
            return None
            
    except requests.exceptions.Timeout:
        print_with_timestamp(f"⚠️ Google Maps timeout after {timeout}s")
        return None
    except requests.exceptions.RequestException as e:
        print_with_timestamp(f"⚠️ Google Maps request failed: {e}")
        return None
    except Exception as e:
        print_with_timestamp(f"⚠️ Google Maps unexpected error: {e}")
        return None

def geocode_location(location_name, timeout=10):
    """
    Convert a location name to coordinates with smart query formatting
    Tries multiple query formats and prioritizes city/locality results
    
    Args:
        location_name: Name of the location (e.g., "Eiffel Tower, Paris" or "Sydney Opera House")
        timeout: Request timeout in seconds
    
    Returns:
        dict with 'lat', 'lon', 'display_name' or None if not found
    """
    print_with_timestamp(f"🔍 Looking up location: '{location_name}'...")
    
    # Generate query variations to improve accuracy
    query_variations = generate_query_variations(location_name)
    
    best_results = None
    best_score = 0
    
    # Try each query variation
    for i, query in enumerate(query_variations):
        if i > 0:  # Don't log the first one as it's the original
            print_with_timestamp(f"� Trying alternative format: '{query}'...")
        
        google_results = geocode_with_google_maps(query, timeout)
        if google_results:
            # Score results based on type and relevance
            scored_results = score_geocoding_results(google_results, location_name)
            if scored_results and scored_results[0]['score'] > best_score:
                best_results = scored_results
                best_score = scored_results[0]['score']
                
                # If we found a high-confidence city/locality result, use it
                if best_score >= 0.9:
                    print_with_timestamp(f"✅ High-confidence result found (score: {best_score:.2f})")
                    break
    
    if best_results:
        # Remove score from results before returning
        clean_results = []
        for result in best_results:
            clean_result = {k: v for k, v in result.items() if k != 'score'}
            clean_results.append(clean_result)
        return clean_results
    
    # Fall back to OpenStreetMap if Google Maps fails
    print_with_timestamp("🔄 Falling back to OpenStreetMap Nominatim...")
    return geocode_with_openstreetmap(location_name, timeout)

def generate_query_variations(location_name):
    """Generate multiple query formats to improve geocoding accuracy"""
    variations = [location_name]  # Original query first
    
    # If location doesn't have a comma, try adding one
    if ',' not in location_name:
        parts = location_name.split()
        if len(parts) >= 2:
            # Try "City, Country" format
            variations.append(f"{parts[0]}, {' '.join(parts[1:])}")
            
            # Try "Az City Country" format for Arabic cities
            if not parts[0].lower().startswith('az'):
                variations.append(f"Az {location_name}")
                variations.append(f"Az {parts[0]}, {' '.join(parts[1:])}")
    
    # Try adding "city" keyword
    if 'city' not in location_name.lower():
        variations.append(f"{location_name} city")
    
    return variations

def score_geocoding_results(results, original_query):
    """Score geocoding results based on type and relevance"""
    # Type priority scores (higher is better)
    type_scores = {
        'locality': 1.0,           # Cities, towns
        'political': 0.9,          # Administrative areas
        'colloquial_area': 0.95,   # Well-known areas (like "Sydney NSW")
        'administrative_area_level_1': 0.85,  # States, provinces
        'administrative_area_level_2': 0.8,   # Counties
        'sublocality': 0.75,       # Neighborhoods
        'route': 0.6,              # Streets
        'establishment': 0.4,      # Businesses, points of interest
        'lodging': 0.3,            # Hotels, etc.
        'point_of_interest': 0.5,  # POIs
    }
    
    scored_results = []
    for result in results:
        score = 0.5  # Base score
        
        # Score based on primary type
        primary_type = result.get('type', 'unknown')
        if primary_type in type_scores:
            score = type_scores[primary_type]
        
        # Bonus for exact name matches
        display_name = result.get('display_name', '').lower()
        query_parts = original_query.lower().split()
        
        for part in query_parts:
            if len(part) > 2 and part in display_name:
                score += 0.1
        
        result['score'] = min(score, 1.0)  # Cap at 1.0
        scored_results.append(result)
    
    # Sort by score (highest first)
    scored_results.sort(key=lambda x: x['score'], reverse=True)
    return scored_results

def geocode_with_openstreetmap(location_name, timeout=10):
    """
    Convert a location name to coordinates using OpenStreetMap Nominatim (fallback)
    
    Args:
        location_name: Name of the location
        timeout: Request timeout in seconds
    
    Returns:
        list of location dicts or None if not found
    """
    try:
        print_with_timestamp(f"🔍 Looking up location: '{location_name}'...")
        
        # Nominatim API endpoint (free, no API key needed!)
        base_url = "https://nominatim.openstreetmap.org/search"
        
        # Prepare request parameters with typo tolerance
        params = {
            'q': location_name,
            'format': 'json',
            'limit': 10,  # Get more results for better fuzzy matching
            'addressdetails': 1,
            'dedupe': 0,  # Don't remove near-duplicates (helps with typos)
            'namedetails': 1  # Include alternative names
        }
        
        # Required: User-Agent header (Nominatim policy)
        headers = {
            'User-Agent': 'DroneTaskSystem/1.0 (Educational Project)'
        }
        
        # Make request
        response = requests.get(base_url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        results = response.json()
        
        # If no results with exact match, try with typo tolerance
        if not results:
            print_with_timestamp(f"⚠️ No exact match found, trying fuzzy search...")
            # Try adding country/region hints based on common patterns
            alternate_queries = []
            
            # Common typo corrections
            typo_map = {
                "austrailia": "australia",
                "queanbey": "queanbeyan",
                "sydeny": "sydney",
                "melborne": "melbourne",
                "brisban": "brisbane",
                "canberrra": "canberra",
                "adelade": "adelaide",
                "perth": "perth"
            }
            
            # Apply typo corrections
            corrected = location_name.lower()
            for typo, correction in typo_map.items():
                if typo in corrected:
                    corrected = corrected.replace(typo, correction)
                    alternate_queries.append(corrected)
                    print_with_timestamp(f"💡 Auto-correcting '{typo}' → '{correction}'")
            
            # Try removing extra spaces
            cleaned = ' '.join(location_name.split())
            if cleaned != location_name and cleaned not in alternate_queries:
                alternate_queries.append(cleaned)
            
            # Try each alternate query
            for alt_query in alternate_queries:
                print_with_timestamp(f"🔄 Trying: '{alt_query}'...")
                params['q'] = alt_query
                response = requests.get(base_url, params=params, headers=headers, timeout=timeout)
                response.raise_for_status()
                results = response.json()
                if results:
                    print_with_timestamp(f"✅ Found results with corrected spelling")
                    location_name = alt_query  # Update for display
                    break
        
        if not results:
            print_with_timestamp(f"❌ Location '{location_name}' not found")
            print_with_timestamp(f"💡 Tip: Check spelling (e.g., 'Australia' not 'Austrailia')")
            return None
        
        # Return multiple results for user to choose
        locations = []
        for idx, result in enumerate(results[:5]):  # Top 5 results
            locations.append({
                'lat': float(result['lat']),
                'lon': float(result['lon']),
                'display_name': result['display_name'],
                'type': result.get('type', 'unknown'),
                'importance': float(result.get('importance', 0))
            })
        
        print_with_timestamp(f"✅ Found {len(locations)} location(s)")
        return locations
        
    except requests.exceptions.Timeout:
        print_with_timestamp(f"⚠️ Geocoding timeout after {timeout}s")
        return None
    except requests.exceptions.RequestException as e:
        print_with_timestamp(f"⚠️ Geocoding failed: {e}")
        return None
    except Exception as e:
        print_with_timestamp(f"⚠️ Unexpected error: {e}")
        return None


def display_and_confirm_location(locations, location_name):
    """
    Display found locations and let user choose/confirm
    
    Args:
        locations: List of location dictionaries
        location_name: Original location name from user
    
    Returns:
        Selected location dict or None if cancelled
    """
    if not locations:
        print_with_timestamp(f"❌ Could not find location: '{location_name}'")
        print_with_timestamp("💡 Tips:")
        print_with_timestamp("   - Try being more specific (e.g., 'Eiffel Tower, Paris, France')")
        print_with_timestamp("   - Check spelling")
        print_with_timestamp("   - Use well-known landmarks or cities")
        return None
    
    if len(locations) == 1:
        # Only one result - show and confirm
        loc = locations[0]
        print_with_timestamp("\n📍 Found location:")
        print_with_timestamp(f"   Name: {loc['display_name']}")
        print_with_timestamp(f"   Coordinates: {loc['lat']:.6f}, {loc['lon']:.6f}")
        print_with_timestamp(f"   Type: {loc['type']}")
        
        confirm = input(f"\n✅ Is this the correct location? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            return loc
        else:
            print_with_timestamp("❌ Location not confirmed")
            return None
    
    # Multiple results - let user choose
    print_with_timestamp(f"\n📍 Found {len(locations)} locations for '{location_name}':")
    print_with_timestamp("="*70)
    
    for idx, loc in enumerate(locations, 1):
        print_with_timestamp(f"\n{idx}. {loc['display_name']}")
        print_with_timestamp(f"   📍 {loc['lat']:.6f}, {loc['lon']:.6f}")
        print_with_timestamp(f"   🏷️  Type: {loc['type']}")
        print_with_timestamp(f"   ⭐ Relevance: {loc['importance']:.2f}")
    
    print_with_timestamp("\n" + "="*70)
    
    while True:
        choice = input(f"\nSelect location (1-{len(locations)}) or 'n' to cancel: ").strip().lower()
        
        if choice == 'n':
            print_with_timestamp("❌ Location selection cancelled")
            return None
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(locations):
                selected = locations[choice_idx]
                print_with_timestamp(f"\n✅ Selected: {selected['display_name']}")
                return selected
            else:
                print_with_timestamp(f"❌ Please enter a number between 1 and {len(locations)}")
        except ValueError:
            print_with_timestamp("❌ Please enter a valid number or 'n'")


if __name__ == "__main__":
    # Test the geocoding
    print_with_timestamp("🧪 Testing Geocoding Helper")
    print_with_timestamp("="*70)
    
    test_locations = [
        "Eiffel Tower, Paris",
        "Sydney Opera House",
        "Times Square, New York",
        "Desert Square, Canberra"  # Your existing location
    ]
    
    for test_loc in test_locations:
        print_with_timestamp(f"\n🔍 Testing: {test_loc}")
        locations = geocode_location(test_loc)
        if locations:
            selected = display_and_confirm_location(locations, test_loc)
            if selected:
                print_with_timestamp(f"✅ Final: {selected['lat']:.6f}, {selected['lon']:.6f}")
        time.sleep(1)  # Be nice to the API
