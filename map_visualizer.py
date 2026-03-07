#!/usr/bin/env python3
"""
OpenStreetMap visualization for extracted task locations
Generates an interactive HTML map and opens it in the browser
Uses Leaflet.js - NO API KEY REQUIRED!
"""

import webbrowser
import os
import tempfile
import subprocess
import shutil
from datetime import datetime

def generate_map_html(latitude, longitude, location_name="Mission Location", task_info=None):
    """
    Generate an interactive OpenStreetMap HTML file (NO API KEY NEEDED!)
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        location_name: Name to display on the marker
        task_info: Dictionary with task details (optional)
    
    Returns:
        Path to the generated HTML file
    """
    
    # Build info window content
    info_content = f"<h3>{location_name}</h3>"
    info_content += f"<p><strong>Coordinates:</strong><br>{latitude:.8f}, {longitude:.8f}</p>"
    
    if task_info:
        if 'task_id' in task_info:
            info_content += f"<p><strong>Task ID:</strong> {task_info['task_id']}</p>"
        if 'task_type' in task_info:
            info_content += f"<p><strong>Type:</strong> {task_info['task_type']}</p>"
        if 'altitude' in task_info:
            info_content += f"<p><strong>Altitude:</strong> {task_info['altitude']} meters</p>"
        if 'description' in task_info:
            info_content += f"<p><strong>Description:</strong><br>{task_info['description']}</p>"
        if 'reference_location' in task_info:
            ref = task_info['reference_location']
            info_content += f"<p><strong>Reference:</strong> {ref['name']}<br>"
            info_content += f"Offset: {ref['offset'][0]} meters {ref['offset'][1]}</p>"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mission Location - {location_name}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossorigin=""/>
    
    <!-- Leaflet JavaScript -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
            crossorigin=""></script>
    
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            height: 100vh;
            width: 100%;
        }}
        #controls {{
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            z-index: 1000;
            text-align: center;
        }}
        #controls h2 {{
            margin: 0 0 5px 0;
            font-size: 18px;
            color: #202124;
        }}
        #controls p {{
            margin: 0;
            font-size: 14px;
            color: #5f6368;
        }}
        .coordinate {{
            font-family: monospace;
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .no-api-badge {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: #4CAF50;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            z-index: 1000;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div id="controls">
        <h2>🎯 {location_name}</h2>
        <p><span class="coordinate">{latitude:.8f}, {longitude:.8f}</span></p>
    </div>
    <div id="map"></div>
    <div class="no-api-badge">✅ No API Key Required!</div>
    
    <script>
        // Initialize map with OpenStreetMap
        const map = L.map('map').setView([{latitude}, {longitude}], 16);
        
        // Add OpenStreetMap tile layer (no API key needed!)
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }}).addTo(map);
        
        // Create custom marker icon
        const customIcon = L.divIcon({{
            html: '<div style="background-color:#FF0000; width:24px; height:24px; border-radius:50%; border:3px solid white; box-shadow:0 2px 6px rgba(0,0,0,0.4);"></div>',
            className: '',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        }});
        
        // Add marker
        const marker = L.marker([{latitude}, {longitude}], {{ icon: customIcon }}).addTo(map);
        
        // Add popup with mission info
        marker.bindPopup(`
            <div style="padding:10px; min-width:200px;">
                <h3 style="margin:0 0 10px 0;">{location_name}</h3>
                {info_content}
            </div>
        `).openPopup();
        
        // Add circle to show approximate area
        L.circle([{latitude}, {longitude}], {{
            color: '#FF0000',
            fillColor: '#FF0000',
            fillOpacity: 0.2,
            radius: 50 // 50 meters
        }}).addTo(map);
        
        // Auto-open popup after a short delay
        setTimeout(() => {{
            marker.openPopup();
        }}, 500);
    </script>
    
    <noscript>
        <div style="padding: 20px; text-align: center;">
            <h2>JavaScript is required to view this map</h2>
            <p>Mission Location: {latitude:.8f}, {longitude:.8f}</p>
            <p><a href="https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}&zoom=16" target="_blank">
                Open in OpenStreetMap
            </a></p>
            <p><a href="https://www.google.com/maps?q={latitude},{longitude}" target="_blank">
                Open in Google Maps
            </a></p>
        </div>
    </noscript>
</body>
</html>
"""
    
    # Create temporary HTML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(tempfile.gettempdir(), f"mission_map_{timestamp}.html")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

def show_mission_on_map(latitude, longitude, location_name="Mission Location", task_info=None, auto_open=True):
    """
    Generate map and optionally open it in browser
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        location_name: Name to display on the marker
        task_info: Dictionary with task details (optional)
        auto_open: Whether to automatically open the map in browser
    
    Returns:
        Path to the generated HTML file
    """
    html_file = generate_map_html(latitude, longitude, location_name, task_info)
    
    if auto_open:
        # Try to open in web browser (not text editor!)
        import subprocess
        import shutil
        
        # Try multiple methods to ensure it opens in a browser
        file_url = 'file://' + os.path.abspath(html_file)
        
        # Method 1: Try specific browsers
        browsers = ['firefox', 'google-chrome', 'chromium-browser', 'chromium']
        browser_found = False
        
        for browser in browsers:
            if shutil.which(browser):
                try:
                    subprocess.Popen([browser, html_file], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    print(f"🗺️ Map opened in {browser}: {html_file}")
                    browser_found = True
                    break
                except:
                    continue
        
        # Method 2: Fallback to webbrowser module
        if not browser_found:
            webbrowser.open(file_url, new=2)  # new=2 opens in new tab
            print(f"🗺️ Map opened in browser: {html_file}")
    else:
        print(f"🗺️ Map generated: {html_file}")
        print(f"   Open manually in browser: file://{os.path.abspath(html_file)}")
    
    return html_file

def generate_map_with_reference(task_location, ref_location, location_name="Mission Location", task_info=None):
    """
    Generate a map showing both the task location and reference location
    
    Args:
        task_location: [lat, lon] for the task
        ref_location: [lat, lon] for the reference point
        location_name: Name to display
        task_info: Dictionary with task details
    
    Returns:
        Path to the generated HTML file
    """
    task_lat, task_lon = task_location
    ref_lat, ref_lon = ref_location
    
    # Build info content
    info_content = f"<h3>{location_name}</h3>"
    info_content += f"<p><strong>Mission Coordinates:</strong><br>{task_lat:.8f}, {task_lon:.8f}</p>"
    
    if task_info:
        if 'reference_location' in task_info:
            ref = task_info['reference_location']
            info_content += f"<p><strong>Reference:</strong> {ref['name']}<br>"
            info_content += f"<span style='font-size:12px;'>{ref['coords'][0]:.8f}, {ref['coords'][1]:.8f}</span><br>"
            info_content += f"<strong>Offset:</strong> {ref['offset'][0]} meters {ref['offset'][1]}</p>"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mission Location - {location_name}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            height: 100vh;
            width: 100%;
        }}
        .info-content {{
            padding: 10px;
            min-width: 250px;
        }}
        .info-content h3 {{
            margin: 0 0 10px 0;
            color: #202124;
        }}
        .info-content p {{
            margin: 5px 0;
            color: #5f6368;
            line-height: 1.5;
        }}
        .info-content strong {{
            color: #202124;
        }}
        #controls {{
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            z-index: 5;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div id="controls">
        <h2>🎯 {location_name}</h2>
    </div>
    <div id="map"></div>
    
    <script>
        function initMap() {{
            // Calculate center point between task and reference
            const centerLat = ({task_lat} + {ref_lat}) / 2;
            const centerLng = ({task_lon} + {ref_lon}) / 2;
            
            // Create map
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 15,
                center: {{ lat: centerLat, lng: centerLng }},
                mapTypeId: 'hybrid',
            }});
            
            // Task location marker (red)
            const taskMarker = new google.maps.Marker({{
                position: {{ lat: {task_lat}, lng: {task_lon} }},
                map: map,
                title: "Mission Location",
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: "#FF0000",
                    fillOpacity: 0.9,
                    strokeColor: "#FFFFFF",
                    strokeWeight: 3,
                }},
                animation: google.maps.Animation.DROP,
            }});
            
            // Reference location marker (blue)
            const refMarker = new google.maps.Marker({{
                position: {{ lat: {ref_lat}, lng: {ref_lon} }},
                map: map,
                title: "Reference Location",
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: "#4285F4",
                    fillOpacity: 0.8,
                    strokeColor: "#FFFFFF",
                    strokeWeight: 2,
                }},
            }});
            
            // Draw line between reference and task
            const line = new google.maps.Polyline({{
                path: [
                    {{ lat: {ref_lat}, lng: {ref_lon} }},
                    {{ lat: {task_lat}, lng: {task_lon} }}
                ],
                geodesic: true,
                strokeColor: "#FFAA00",
                strokeOpacity: 0.8,
                strokeWeight: 3,
                map: map,
            }});
            
            // Info window
            const infoWindow = new google.maps.InfoWindow({{
                content: `<div class="info-content">{info_content}</div>`
            }});
            
            infoWindow.open(map, taskMarker);
            
            taskMarker.addListener("click", () => {{
                infoWindow.open(map, taskMarker);
            }});
            
            // Fit map to show both markers
            const bounds = new google.maps.LatLngBounds();
            bounds.extend({{ lat: {task_lat}, lng: {task_lon} }});
            bounds.extend({{ lat: {ref_lat}, lng: {ref_lon} }});
            map.fitBounds(bounds);
        }}
        
        window.initMap = initMap;
    </script>
    
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY_HERE&callback=initMap" async defer></script>
</body>
</html>
"""
    
    # Create temporary HTML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(tempfile.gettempdir(), f"mission_map_{timestamp}.html")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in browser
    webbrowser.open('file://' + os.path.abspath(html_file))
    print(f"🗺️ Map with reference location opened in browser")
    
    return html_file


# Example usage
if __name__ == "__main__":
    # Test with a simple location
    show_mission_on_map(
        latitude=-35.36309804,
        longitude=149.16348567,
        location_name="Desert Square",
        task_info={
            'task_id': 'delivery_001',
            'task_type': 'delivery',
            'altitude': 30,
            'description': 'Package delivery to Desert Square'
        }
    )
