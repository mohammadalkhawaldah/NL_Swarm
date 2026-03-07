#!/usr/bin/env python3
"""
OpenStreetMap-based visualization (no API key required!)
Uses Leaflet.js for interactive maps
"""

import webbrowser
import os
import tempfile
from datetime import datetime

def generate_osm_map_html(latitude, longitude, location_name="Mission Location", task_info=None):
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
    
    # Build info content
    info_content = f"<b>{location_name}</b><br>"
    info_content += f"<b>Coordinates:</b><br>{latitude:.8f}, {longitude:.8f}<br><br>"
    
    if task_info:
        if 'task_id' in task_info:
            info_content += f"<b>Task ID:</b> {task_info['task_id']}<br>"
        if 'task_type' in task_info:
            info_content += f"<b>Type:</b> {task_info['task_type']}<br>"
        if 'altitude' in task_info:
            info_content += f"<b>Altitude:</b> {task_info['altitude']} meters<br>"
        if 'description' in task_info:
            info_content += f"<b>Description:</b><br>{task_info['description']}<br>"
        if 'reference_location' in task_info:
            ref = task_info['reference_location']
            info_content += f"<br><b>Reference:</b> {ref['name']}<br>"
            info_content += f"Offset: {ref['offset'][0]} meters {ref['offset'][1]}"
    
    # Google Maps link for easy navigation
    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    
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
        #header {{
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            z-index: 1000;
            text-align: center;
            max-width: 90%;
        }}
        #header h2 {{
            margin: 0 0 8px 0;
            font-size: 20px;
            color: #202124;
        }}
        #header p {{
            margin: 5px 0;
            font-size: 14px;
            color: #5f6368;
        }}
        .coordinate {{
            font-family: monospace;
            background: #f1f3f4;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .btn {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #4285f4;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 13px;
            transition: background 0.3s;
        }}
        .btn:hover {{
            background: #357ae8;
        }}
        .leaflet-popup-content {{
            font-size: 14px;
            line-height: 1.6;
        }}
        .leaflet-popup-content b {{
            color: #202124;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h2>🎯 {location_name}</h2>
        <p><span class="coordinate">{latitude:.8f}, {longitude:.8f}</span></p>
        <a href="{google_maps_link}" target="_blank" class="btn">📱 Open in Google Maps</a>
    </div>
    
    <div id="map"></div>
    
    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
    
    <script>
        // Initialize map
        const map = L.map('map').setView([{latitude}, {longitude}], 16);
        
        // Add OpenStreetMap tile layer
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19,
        }}).addTo(map);
        
        // Add satellite imagery option
        const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Tiles &copy; Esri',
            maxZoom: 19
        }});
        
        // Layer control
        const baseMaps = {{
            "Street Map": L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}),
            "Satellite": satellite
        }};
        
        L.control.layers(baseMaps).addTo(map);
        
        // Add mission marker
        const marker = L.marker([{latitude}, {longitude}], {{
            icon: L.icon({{
                iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAiIGhlaWdodD0iNDUiIHZpZXdCb3g9IjAgMCAzMCA0NSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTUgMEMxMCAwIDYgNCA2IDE1YzAgOCA5IDE1IDkgMzAgMC0xNSA5LTIyIDktMzAgMC0xMS00LTE1LTktMTV6IiBmaWxsPSIjRkYwMDAwIiBzdHJva2U9IiNGRkYiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==',
                iconSize: [30, 45],
                iconAnchor: [15, 45],
                popupAnchor: [0, -45]
            }})
        }}).addTo(map);
        
        // Add popup with task info
        marker.bindPopup(`{info_content}`, {{
            maxWidth: 300
        }}).openPopup();
        
        // Add circle to show mission area
        L.circle([{latitude}, {longitude}], {{
            color: 'red',
            fillColor: '#ff0000',
            fillOpacity: 0.2,
            radius: 50
        }}).addTo(map);
        
        // Add scale control
        L.control.scale().addTo(map);
    </script>
</body>
</html>
"""
    
    # Create temporary HTML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(tempfile.gettempdir(), f"mission_map_{timestamp}.html")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

def generate_osm_map_with_reference(task_location, ref_location, location_name="Mission Location", task_info=None):
    """
    Generate a map showing both the task location and reference location using OpenStreetMap
    """
    task_lat, task_lon = task_location
    ref_lat, ref_lon = ref_location
    
    # Calculate center
    center_lat = (task_lat + ref_lat) / 2
    center_lon = (task_lon + ref_lon) / 2
    
    # Build info content
    info_content = f"<b>{location_name}</b><br>"
    info_content += f"<b>Mission:</b> {task_lat:.8f}, {task_lon:.8f}<br>"
    
    if task_info and 'reference_location' in task_info:
        ref = task_info['reference_location']
        info_content += f"<b>Reference:</b> {ref['name']}<br>"
        info_content += f"<b>Offset:</b> {ref['offset'][0]} meters {ref['offset'][1]}"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mission Location - {location_name}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
        crossorigin=""/>
    
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        #header {{
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            z-index: 1000;
            text-align: center;
        }}
        #header h2 {{ margin: 0; font-size: 18px; color: #202124; }}
        .leaflet-popup-content {{ font-size: 13px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div id="header">
        <h2>🎯 {location_name}</h2>
    </div>
    
    <div id="map"></div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
    
    <script>
        const map = L.map('map').setView([{center_lat}, {center_lon}], 15);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);
        
        // Task marker (red)
        const taskMarker = L.marker([{task_lat}, {task_lon}], {{
            icon: L.icon({{
                iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAiIGhlaWdodD0iNDUiIHZpZXdCb3g9IjAgMCAzMCA0NSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTUgMEMxMCAwIDYgNCA2IDE1YzAgOCA5IDE1IDkgMzAgMC0xNSA5LTIyIDktMzAgMC0xMS00LTE1LTktMTV6IiBmaWxsPSIjRkYwMDAwIiBzdHJva2U9IiNGRkYiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==',
                iconSize: [30, 45],
                iconAnchor: [15, 45],
                popupAnchor: [0, -45]
            }})
        }}).addTo(map);
        
        // Reference marker (blue)
        const refMarker = L.marker([{ref_lat}, {ref_lon}], {{
            icon: L.icon({{
                iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMzYiIHZpZXdCb3g9IjAgMCAyNCAzNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMEM4IDAgNCAzIDQgMTJjMCA2IDggMTIgOCAyNCAwLTEyIDgtMTggOC0yNCAwLTktNC0xMi04LTEyeiIgZmlsbD0iIzQyODVGNCIgc3Ryb2tlPSIjRkZGIiBzdHJva2Utd2lkdGg9IjIiLz48L3N2Zz4=',
                iconSize: [24, 36],
                iconAnchor: [12, 36],
                popupAnchor: [0, -36]
            }})
        }}).addTo(map);
        
        // Draw line between reference and task
        L.polyline([[{ref_lat}, {ref_lon}], [{task_lat}, {task_lon}]], {{
            color: '#FFAA00',
            weight: 3,
            dashArray: '10, 5',
            opacity: 0.8
        }}).addTo(map);
        
        // Add popups
        taskMarker.bindPopup(`{info_content}`).openPopup();
        refMarker.bindPopup("<b>Reference Location</b><br>{ref_lat:.6f}, {ref_lon:.6f}");
        
        // Fit map to show both markers
        const bounds = L.latLngBounds([[{task_lat}, {task_lon}], [{ref_lat}, {ref_lon}]]);
        map.fitBounds(bounds, {{padding: [50, 50]}});
    </script>
</body>
</html>
"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(tempfile.gettempdir(), f"mission_map_{timestamp}.html")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    webbrowser.open('file://' + os.path.abspath(html_file))
    print(f"🗺️ Map opened in browser: {html_file}")
    
    return html_file

def show_mission_on_osm_map(latitude, longitude, location_name="Mission Location", task_info=None):
    """
    Generate OpenStreetMap and open it in browser
    """
    html_file = generate_osm_map_html(latitude, longitude, location_name, task_info)
    webbrowser.open('file://' + os.path.abspath(html_file))
    print(f"🗺️ Map opened in browser: {html_file}")
    return html_file


# Example usage
if __name__ == "__main__":
    # Test with Desert Square
    show_mission_on_osm_map(
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
