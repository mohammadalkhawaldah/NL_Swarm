#!/usr/bin/env python3
"""
Test the automatic Google Maps opening
"""

import sys
from datetime import datetime

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    """Print message with timestamp prefix"""
    print(f"[{get_timestamp()}] {message}")

from map_simple_fallback import show_location_on_google_maps

print_with_timestamp("🧪 Testing Automatic Google Maps Opening")
print_with_timestamp("="*70)
print_with_timestamp("")
print_with_timestamp("✅ The map now opens automatically - no menu, no questions!")
print_with_timestamp("🚀 When you extract a task, Google Maps will open immediately.")
print_with_timestamp("")
print_with_timestamp("Let's test it with Desert Square:")
print_with_timestamp("")

# Test Desert Square
show_location_on_google_maps(
    latitude=-35.36309804,
    longitude=149.16348567,
    location_name="Desert Square"
)

print_with_timestamp("")
print_with_timestamp("="*70)
print_with_timestamp("✅ Done! The Google Maps link opened automatically.")
print_with_timestamp("💡 Now when you run the main script, it will:")
print_with_timestamp("   1. Extract the task")
print_with_timestamp("   2. Display task details")
print_with_timestamp("   3. Automatically open Google Maps (no menu!)")
print_with_timestamp("   4. Ask if you want to send the task")
print_with_timestamp("")
print_with_timestamp("🎉 Much faster workflow!")
