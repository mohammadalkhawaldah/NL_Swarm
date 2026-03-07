#!/usr/bin/env python3
"""
Location information extractor using OpenAI Structured Outputs
Extracts location and offset details from natural language, then Python calculates coordinates
"""

from pydantic import BaseModel
from typing import Optional, Literal
from openai import OpenAI
import os
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    print(f"[{get_timestamp()}] {message}")

# Pydantic models for structured extraction
class OffsetInfo(BaseModel):
    """Information about an offset from a reference location"""
    has_offset: Literal[True]
    distance_value: float
    distance_unit: Literal["meters", "km", "kilometers"]
    direction: Literal["north", "south", "east", "west"]
    reference_location: str

class DirectLocation(BaseModel):
    """Information about a direct location (no offset)"""
    has_offset: Literal[False]
    location_name: str

class LocationExtraction(BaseModel):
    """
    Extracted location information from user prompt.
    Either a direct location or an offset-based location.
    """
    # Use exactly ONE of these two
    offset_location: Optional[OffsetInfo] = None
    direct_location: Optional[DirectLocation] = None

def extract_location_info_with_ai(user_prompt: str, api_key: str) -> Optional[LocationExtraction]:
    """
    Use OpenAI Structured Outputs to extract location information
    
    Args:
        user_prompt: User's natural language input
        api_key: OpenAI API key
    
    Returns:
        LocationExtraction object or None if extraction failed
    """
    try:
        print_with_timestamp("🤖 Using AI to extract location information...")
        
        client = OpenAI(api_key=api_key, timeout=30.0)
        
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at extracting location information from natural language.

Extract location details from the user's prompt. There are two types of locations:

1. DIRECT LOCATION: Just a place name
   Examples:
   - "deliver to Paris" → location_name: "Paris"
   - "search at Eiffel Tower" → location_name: "Eiffel Tower"
   - "deliver at Balama in Jordan" → location_name: "Balama Jordan"
   - "go to Tokyo Japan" → location_name: "Tokyo Japan"
   - "survey Street Gardens Canberra" → location_name: "Street Gardens Canberra"

2. OFFSET LOCATION: Distance + direction + reference location
   Examples:
   - "2km north of Amman" → distance: 2, unit: "km", direction: "north", reference: "Amman"
   - "500 meters west of the capital" → distance: 500, unit: "meters", direction: "west", reference: "the capital" 
   - "1 kilometer east of Paris France" → distance: 1, unit: "km", direction: "east", reference: "Paris France"

IMPORTANT RULES:
- ALWAYS include country/region names if specified (e.g., "Balama in Jordan" → "Balama Jordan", NOT just "Balama")
- Keep important context words: "Paris France", "Tokyo Japan", "Amman Jordan"
- Remove ONLY obvious filler words like "the", "a", "an", "at", "in", "to" UNLESS they affect meaning
- For "the capital Amman" → keep "Amman" (the capital is filler, Amman is the actual place)
- For "Balama in Jordan" → keep "Balama Jordan" (Jordan specifies which Balama)
- Convert "kilometer" to "km", keep "meters" as "meters"
- Directions must be: north, south, east, or west (lowercase)
- If there's an offset, set offset_location. If direct, set direct_location.
- NEVER set both offset_location and direct_location at the same time.

Return the structured location information."""
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format=LocationExtraction
        )
        
        location_data = response.choices[0].message.parsed
        
        if location_data:
            print_with_timestamp("✅ AI extraction successful")
            return location_data
        else:
            print_with_timestamp("❌ AI extraction returned no data")
            return None
            
    except Exception as e:
        print_with_timestamp(f"❌ AI extraction failed: {e}")
        return None

if __name__ == "__main__":
    # Test the extractor
    from dotenv import load_dotenv
    load_dotenv('/home/moham/mavsdk_bin/.env')
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    print_with_timestamp("🧪 Testing AI Location Extractor")
    print_with_timestamp("="*70)
    
    test_prompts = [
        "deliver at 2 km to the north of the capital Amman",
        "deliver at 2 km to the north Amman",
        "deliver at paris",
        "search at Eiffel Tower, Paris",
        "survey 500 meters west of Street Gardens"
    ]
    
    for prompt in test_prompts:
        print_with_timestamp(f"\n📝 Testing: '{prompt}'")
        print_with_timestamp("-"*70)
        
        result = extract_location_info_with_ai(prompt, api_key)
        
        if result:
            if result.offset_location:
                offset = result.offset_location
                print_with_timestamp(f"✅ OFFSET LOCATION:")
                print_with_timestamp(f"   Distance: {offset.distance_value} {offset.distance_unit}")
                print_with_timestamp(f"   Direction: {offset.direction}")
                print_with_timestamp(f"   Reference: {offset.reference_location}")
            elif result.direct_location:
                direct = result.direct_location
                print_with_timestamp(f"✅ DIRECT LOCATION:")
                print_with_timestamp(f"   Name: {direct.location_name}")
            else:
                print_with_timestamp("❌ No location information extracted")
        else:
            print_with_timestamp("❌ Extraction failed")
        
        print()
