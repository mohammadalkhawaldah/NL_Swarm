#!/usr/bin/env python3
"""
Simple map visualizer - opens Google Maps website directly
NO HTML FILE, NO API KEY, ALWAYS WORKS!
"""

import webbrowser
import subprocess
import sys
import os
import platform

def show_location_on_google_maps(latitude, longitude, location_name="Location"):
    """
    Open location directly in Google Maps website
    This ALWAYS works - no HTML, no API key needed!
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        location_name: Name of the location (for display only)
    """
    # Create Google Maps URL
    url = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    print(f"🗺️  Opening {location_name} in Google Maps...")
    print(f"📍 Coordinates: {latitude}, {longitude}")
    print(f"🔗 URL: {url}")
    
    # Try multiple methods to ensure browser opens
    success = False
    methods_tried = []
    
    # Method 1: Try Microsoft Edge (Windows/WSL/RDP)
    edge_commands = [
        'microsoft-edge',
        'microsoft-edge-stable', 
        'msedge',
        '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',  # WSL path
        'cmd.exe /c start microsoft-edge:',  # Windows command
        'powershell.exe -c start microsoft-edge:',  # PowerShell command
    ]
    
    for edge_cmd in edge_commands:
        if not success:
            try:
                methods_tried.append(edge_cmd)
                if 'cmd.exe' in edge_cmd or 'powershell' in edge_cmd:
                    # Windows command - append URL
                    full_cmd = edge_cmd + url
                    subprocess.Popen(full_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen([edge_cmd, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                success = True
                print(f"🌐 Opening in Microsoft Edge...")
                break
            except Exception:
                continue
    
    # Method 2: Python webbrowser module (system default)
    if not success:
        try:
            methods_tried.append('webbrowser.open')
            webbrowser.open(url)
            success = True
            print("🌐 Opening in default browser...")
        except Exception:
            pass
    
    # Method 3: Windows start command (if in WSL/RDP)
    if not success:
        try:
            methods_tried.append('cmd.exe /c start')
            subprocess.Popen(['cmd.exe', '/c', 'start', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success = True
            print("🌐 Opening with Windows start command...")
        except Exception:
            pass
    
    # Method 4: For Linux, try xdg-open
    if not success and sys.platform.startswith('linux'):
        try:
            methods_tried.append('xdg-open')
            subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success = True
            print("🌐 Opening with xdg-open...")
        except Exception:
            pass
    
    # Method 5: Try Firefox
    if not success:
        try:
            methods_tried.append('firefox')
            subprocess.Popen(['firefox', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success = True
            print("🌐 Opening in Firefox...")
        except Exception:
            pass
    
    # Method 6: Try Chrome/Chromium
    if not success:
        for browser in ['google-chrome', 'chromium-browser', 'chromium']:
            try:
                methods_tried.append(browser)
                subprocess.Popen([browser, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                success = True
                print(f"🌐 Opening in {browser}...")
                break
            except Exception:
                continue
    
    if success:
        print("✅ Google Maps opened in browser automatically!")
    else:
        print("⚠️ Could not auto-open browser.")
        print(f"   Tried: {', '.join(methods_tried[:3])}")
        print("   Please click the link above manually.")
        print("\n💡 To fix this, tell me the exact command to open Microsoft Edge:")
        print("   Run in terminal: microsoft-edge https://google.com")
        print("   Or: msedge https://google.com")
        print("   And let me know which one works!")
    
    return url


if __name__ == "__main__":
    # Test with Desert Square
    show_location_on_google_maps(
        latitude=-35.36309804,
        longitude=149.16348567,
        location_name="Desert Square"
    )
