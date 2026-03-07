#!/usr/bin/env python3
"""
Test automatic browser opening with multiple fallback methods
"""

import webbrowser
import subprocess
import os
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    print(f"[{get_timestamp()}] {message}")

def open_url_in_browser(url, location_name="Location"):
    """
    Open URL in browser with multiple fallback methods
    """
    print_with_timestamp(f"🗺️ Opening {location_name} in Google Maps...")
    print_with_timestamp(f"🔗 URL: {url}")
    print_with_timestamp("")
    
    success = False
    
    # Method 1: Python webbrowser module (standard)
    try:
        print_with_timestamp("📍 Method 1: Using Python webbrowser module...")
        webbrowser.open(url)
        print_with_timestamp("✅ Browser opened successfully!")
        success = True
    except Exception as e:
        print_with_timestamp(f"⚠️ Method 1 failed: {e}")
    
    # Method 2: Try xdg-open (Linux default)
    if not success:
        try:
            print_with_timestamp("📍 Method 2: Using xdg-open...")
            subprocess.run(['xdg-open', url], check=True, capture_output=True)
            print_with_timestamp("✅ Browser opened with xdg-open!")
            success = True
        except Exception as e:
            print_with_timestamp(f"⚠️ Method 2 failed: {e}")
    
    # Method 3: Try Firefox directly
    if not success:
        try:
            print_with_timestamp("📍 Method 3: Using Firefox directly...")
            subprocess.Popen(['firefox', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print_with_timestamp("✅ Firefox opened!")
            success = True
        except Exception as e:
            print_with_timestamp(f"⚠️ Method 3 failed: {e}")
    
    # Method 4: Try Chrome/Chromium
    if not success:
        for browser in ['google-chrome', 'chromium-browser', 'chromium']:
            try:
                print_with_timestamp(f"📍 Method 4: Using {browser}...")
                subprocess.Popen([browser, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print_with_timestamp(f"✅ {browser} opened!")
                success = True
                break
            except Exception:
                continue
    
    if success:
        print_with_timestamp("🎉 Google Maps should now be open in your browser!")
    else:
        print_with_timestamp("⚠️ Could not auto-open browser. Please click the link above.")
    
    return success

# Test
print_with_timestamp("🧪 Testing Automatic Browser Opening")
print_with_timestamp("="*70)
print_with_timestamp("")

url = "https://www.google.com/maps?q=-35.36309804,149.16348567"
open_url_in_browser(url, "Desert Square")

print_with_timestamp("")
print_with_timestamp("="*70)
print_with_timestamp("💡 Check if Google Maps opened in your browser automatically!")
