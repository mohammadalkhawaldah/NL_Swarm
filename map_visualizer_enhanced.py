#!/usr/bin/env python3
"""
Enhanced Map Visualizer - Shows BOTH Reference and Target Locations
Displays reference location (blue), target location (red), and connecting line
"""

import webbrowser
import os
import tempfile
from datetime import datetime

def generate_dual_marker_map(ref_coords, target_coords, ref_name, distance, direction, task_info=None):
    """
    Generate interactive HTML map with both reference and target locations
    
    Args:
        ref_coords: [lat, lon] of reference location
        target_coords: [lat, lon] of target location
        ref_name: Name of reference location (e.g., "Desert Square")
        distance: Distance of offset in meters
        direction: Direction of offset (e.g., "south", "east")
        task_info: Optional dictionary with additional task details
    
    Returns:
        Path to generated HTML file
    """
    ref_lat, ref_lon = ref_coords
    target_lat, target_lon = target_coords
    
    # Calculate center point between reference and target
    center_lat = (ref_lat + target_lat) / 2
    center_lon = (ref_lon + target_lon) / 2
    
    # Build task info display
    task_details = ""
    if task_info:
        if 'task_id' in task_info:
            task_details += f"<p><strong>Task ID:</strong> {task_info['task_id']}</p>"
        if 'task_type' in task_info:
            task_details += f"<p><strong>Type:</strong> {task_info['task_type']}</p>"
        if 'altitude' in task_info:
            task_details += f"<p><strong>Altitude:</strong> {task_info['altitude']} meters</p>"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mission Map: {ref_name} → Target</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }}
        #map {{
            height: 100vh;
            width: 100%;
        }}
        .info-panel {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 350px;
            font-size: 14px;
        }}
        .info-panel h2 {{
            margin: 0 0 15px 0;
            color: #1a73e8;
            font-size: 18px;
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 8px;
        }}
        .info-row {{
            margin: 10px 0;
            display: flex;
            align-items: flex-start;
        }}
        .info-label {{
            font-weight: bold;
            margin-right: 8px;
            min-width: 80px;
        }}
        .info-value {{
            color: #555;
        }}
        .marker-legend {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}
        .legend-dot {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .ref-dot {{ background-color: #4285f4; }}
        .target-dot {{ background-color: #ea4335; }}
        .legend-text {{
            font-size: 13px;
        }}
        .coords {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #666;
        }}
        .timestamp {{
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #888;
            text-align: center;
        }}
        .close-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: #f1f1f1;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 18px;
            line-height: 28px;
            text-align: center;
        }}
        .close-btn:hover {{
            background: #ddd;
        }}
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
    <script>
        let map;
        let refMarker;
        let targetMarker;
        let flightPath;
        
        function initMap() {{
            // Initialize map centered between reference and target
            const center = {{ lat: {center_lat}, lng: {center_lon} }};
            
            map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 15,
                center: center,
                mapTypeId: 'hybrid',  // Satellite view with labels
                mapTypeControl: true,
                streetViewControl: true,
                fullscreenControl: true,
                zoomControl: true
            }});
            
            // Reference location marker (Blue)
            refMarker = new google.maps.Marker({{
                position: {{ lat: {ref_lat}, lng: {ref_lon} }},
                map: map,
                title: '{ref_name}',
                label: {{
                    text: 'R',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '14px'
                }},
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: '#4285f4',
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 3
                }},
                animation: google.maps.Animation.DROP
            }});
            
            // Target location marker (Red)
            targetMarker = new google.maps.Marker({{
                position: {{ lat: {target_lat}, lng: {target_lon} }},
                map: map,
                title: 'Target Location',
                label: {{
                    text: 'T',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '14px'
                }},
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: '#ea4335',
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 3
                }},
                animation: google.maps.Animation.DROP
            }});
            
            // Draw flight path line with arrow
            flightPath = new google.maps.Polyline({{
                path: [
                    {{ lat: {ref_lat}, lng: {ref_lon} }},
                    {{ lat: {target_lat}, lng: {target_lon} }}
                ],
                geodesic: true,
                strokeColor: '#FF9800',
                strokeOpacity: 0.9,
                strokeWeight: 4,
                icons: [{{
                    icon: {{
                        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                        scale: 4,
                        strokeColor: '#FF9800',
                        fillColor: '#FF9800',
                        fillOpacity: 1
                    }},
                    offset: '100%'
                }}]
            }});
            
            flightPath.setMap(map);
            
            // Create info windows
            const refInfoWindow = new google.maps.InfoWindow({{
                content: `
                    <div style="padding:12px; max-width:250px;">
                        <h3 style="margin:0 0 10px 0; color:#4285f4;">🔵 {ref_name}</h3>
                        <p style="margin:5px 0;"><strong>Reference Location</strong></p>
                        <p style="margin:5px 0; font-family:monospace; font-size:12px; color:#666;">
                            {ref_lat:.8f}<br>{ref_lon:.8f}
                        </p>
                    </div>
                `
            }});
            
            const targetInfoWindow = new google.maps.InfoWindow({{
                content: `
                    <div style="padding:12px; max-width:250px;">
                        <h3 style="margin:0 0 10px 0; color:#ea4335;">🔴 Target Location</h3>
                        <p style="margin:5px 0;"><strong>{distance} meters {direction}</strong></p>
                        <p style="margin:5px 0;">of {ref_name}</p>
                        <p style="margin:5px 0; font-family:monospace; font-size:12px; color:#666;">
                            {target_lat:.8f}<br>{target_lon:.8f}
                        </p>
                        {task_details}
                    </div>
                `
            }});
            
            // Add click listeners
            refMarker.addListener('click', () => {{
                targetInfoWindow.close();
                refInfoWindow.open(map, refMarker);
            }});
            
            targetMarker.addListener('click', () => {{
                refInfoWindow.close();
                targetInfoWindow.open(map, targetMarker);
            }});
            
            // Auto-open target info window
            setTimeout(() => {{
                targetInfoWindow.open(map, targetMarker);
            }}, 800);
        }}
        
        function toggleInfoPanel() {{
            const panel = document.getElementById('infoPanel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }}
        
        // Initialize map when page loads
        window.onload = initMap;
    </script>
</head>
<body>
    <div id="map"></div>
    
    <div class="info-panel" id="infoPanel">
        <button class="close-btn" onclick="toggleInfoPanel()">×</button>
        <h2>🎯 Mission Overview</h2>
        
        <div class="info-row">
            <span class="info-label">Offset:</span>
            <span class="info-value">{distance} meters {direction}</span>
        </div>
        
        <div class="marker-legend">
            <div class="legend-item">
                <div class="legend-dot ref-dot"></div>
                <div>
                    <div class="legend-text"><strong>{ref_name}</strong></div>
                    <div class="coords">{ref_lat:.6f}, {ref_lon:.6f}</div>
                </div>
            </div>
            
            <div class="legend-item">
                <div class="legend-dot target-dot"></div>
                <div>
                    <div class="legend-text"><strong>Target Location</strong></div>
                    <div class="coords">{target_lat:.6f}, {target_lon:.6f}</div>
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            📅 Generated: {timestamp}
        </div>
    </div>
    
    <div style="position:absolute; bottom:10px; right:10px; background:white; padding:10px; border-radius:8px; 
         box-shadow:0 2px 6px rgba(0,0,0,0.3); font-size:12px; max-width:300px;">
        ⚠️ <strong>Note:</strong> Replace <code>YOUR_API_KEY</code> in the HTML source with a valid 
        <a href="https://developers.google.com/maps/documentation/javascript/get-api-key" target="_blank">
        Google Maps API key</a> for production use.
    </div>
</body>
</html>
"""
    
    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"mission_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(temp_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath


def open_enhanced_map(ref_coords, target_coords, ref_name, distance, direction, task_info=None):
    """
    Generate and open enhanced map in browser
    
    Args:
        ref_coords: [lat, lon] of reference location
        target_coords: [lat, lon] of target location
        ref_name: Name of reference location
        distance: Distance offset in meters
        direction: Direction of offset
        task_info: Optional task details
    
    Returns:
        Path to generated HTML file
    """
    print(f"🗺️  Generating enhanced map visualization...")
    print(f"    🔵 Reference: {ref_name} at {ref_coords}")
    print(f"    🔴 Target: {distance}m {direction} at {target_coords}")
    
    filepath = generate_dual_marker_map(ref_coords, target_coords, ref_name, distance, direction, task_info)
    
    print(f"✅ Map saved to: {filepath}")
    print(f"🌐 Opening in browser...")
    
    try:
        webbrowser.open('file://' + filepath)
        return filepath
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"📋 Please manually open: {filepath}")
        return filepath


def generate_google_maps_url(ref_coords, target_coords):
    """
    Generate simple Google Maps URL (fallback if HTML doesn't work)
    Opens Google Maps directions showing path between locations
    """
    ref_lat, ref_lon = ref_coords
    target_lat, target_lon = target_coords
    
    # Google Maps directions URL
    url = f"https://www.google.com/maps/dir/{ref_lat},{ref_lon}/{target_lat},{target_lon}"
    return url


def open_simple_google_maps(ref_coords, target_coords, ref_name, distance, direction):
    """
    Open simple Google Maps view (no API key required)
    """
    url = generate_google_maps_url(ref_coords, target_coords)
    print(f"🗺️  Opening Google Maps: {ref_name} → Target ({distance}m {direction})")
    print(f"🔗 URL: {url}")
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"📋 Please manually open: {url}")
        return False


if __name__ == "__main__":
    # Test the enhanced map visualizer
    print("🧪 Testing Enhanced Map Visualizer")
    print("=" * 70)
    
    # Example: 700m south of Desert Square
    ref_coords = [-35.36309804, 149.16348567]  # Desert Square
    target_coords = [-35.36942804, 149.16348567]  # 700m south
    ref_name = "Desert Square"
    distance = 700
    direction = "south"
    
    task_info = {
        'task_id': 'TASK_001',
        'task_type': 'deliver',
        'altitude': 50
    }
    
    print(f"📍 Reference Location: {ref_name}")
    print(f"   Coordinates: {ref_coords}")
    print(f"🎯 Target Location: {distance}m {direction}")
    print(f"   Coordinates: {target_coords}")
    print()
    
    # Test enhanced HTML map
    print("Option 1: Enhanced HTML Map (with both markers and line)")
    print("-" * 70)
    filepath = open_enhanced_map(ref_coords, target_coords, ref_name, distance, direction, task_info)
    print()
    
    # Test simple Google Maps
    print("Option 2: Simple Google Maps (no API key needed)")
    print("-" * 70)
    open_simple_google_maps(ref_coords, target_coords, ref_name, distance, direction)
    print()
    
    print("✅ Test complete!")
    print(f"📂 Enhanced map file: {filepath}")
