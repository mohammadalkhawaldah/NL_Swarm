#!/usr/bin/env python3
"""
OpenStreetMap-based visualization (no API key required!)
Uses Leaflet.js for interactive maps
"""

import webbrowser
import os
import tempfile
import json
import subprocess
from datetime import datetime
from pathlib import Path
import math

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


def generate_search_partition_map(task, partition_overview):
    """Generate a Leaflet map showing the circular search area and per-drone partitions."""
    center_lat, center_lon = partition_overview["center"]
    task_id = task.get("task_id", "search-task")
    radius_m = partition_overview["search_radius_m"]
    partitioning = partition_overview["partitioning"]
    lane_spacing_m = partition_overview["lane_spacing_m"]

    color_palette = ["#e63946", "#1d3557", "#2a9d8f", "#f4a261", "#6a4c93", "#ffb703"]
    drone_layers = []
    for idx, drone_id in enumerate(partition_overview["selected_drones"]):
        drone_info = partition_overview["drones"][drone_id]
        drone_layers.append(
            {
                "drone_id": drone_id,
                "color": color_palette[idx % len(color_palette)],
                "seed_latlon": drone_info["seed_latlon"],
                "cell_centroid": drone_info["cell_centroid"],
                "cell_area_m2": drone_info["cell_area_m2"],
                "outline": drone_info["outline"],
                "waypoints": drone_info["waypoints"],
            }
        )

    drone_layers_json = json.dumps(drone_layers)
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Search Partition Map - {task_id}</title>
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
            background: rgba(255,255,255,0.95);
            padding: 14px 18px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.25);
            z-index: 1000;
            text-align: center;
            min-width: 320px;
        }}
        #header h2 {{ margin: 0 0 6px 0; font-size: 18px; }}
        #header p {{ margin: 4px 0; font-size: 13px; color: #444; }}
        .legend {{
            position: absolute;
            right: 10px;
            top: 10px;
            background: rgba(255,255,255,0.95);
            padding: 12px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.25);
            z-index: 1000;
            min-width: 220px;
        }}
        .legend-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 6px 0;
            font-size: 13px;
        }}
        .swatch {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h2>Search Partition Map</h2>
        <p><b>Task:</b> {task_id}</p>
        <p><b>Partitioning:</b> {partitioning} | <b>Radius:</b> {radius_m:.0f}m | <b>Lane Spacing:</b> {lane_spacing_m:.0f}m</p>
    </div>
    <div class="legend" id="legend">
        <b>Drone Assignments</b>
    </div>
    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
    <script>
        const map = L.map('map');
        const droneLayers = {drone_layers_json};

        const street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19,
        }});
        const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Tiles &copy; Esri',
            maxZoom: 19
        }});
        street.addTo(map);
        L.control.layers({{"Street": street, "Satellite": satellite}}).addTo(map);

        const bounds = [];
        const searchCircle = L.circle([{center_lat}, {center_lon}], {{
            radius: {radius_m},
            color: '#111',
            weight: 2,
            fillColor: '#111',
            fillOpacity: 0.04
        }}).addTo(map);
        bounds.push([{center_lat}, {center_lon}]);

        const centerMarker = L.circleMarker([{center_lat}, {center_lon}], {{
            radius: 6,
            color: '#111',
            fillColor: '#fff',
            fillOpacity: 1.0,
            weight: 2
        }}).bindPopup('Search center').addTo(map);

        const legend = document.getElementById('legend');
        droneLayers.forEach((drone) => {{
            const row = document.createElement('div');
            row.className = 'legend-row';
            row.innerHTML = `<span class="swatch" style="background:${{drone.color}}"></span><span><b>${{drone.drone_id}}</b> - ${{Math.round(drone.cell_area_m2)}} m²</span>`;
            legend.appendChild(row);

            if (drone.outline.length >= 3) {{
                L.polygon(drone.outline, {{
                    color: drone.color,
                    weight: 2,
                    fillColor: drone.color,
                    fillOpacity: 0.18
                }}).bindPopup(`${{drone.drone_id}} cell`).addTo(map);
                drone.outline.forEach((point) => bounds.push(point));
            }}

            L.polyline(drone.waypoints, {{
                color: drone.color,
                weight: 3,
                opacity: 0.95
            }}).bindPopup(`${{drone.drone_id}} lawnmower path`).addTo(map);
            drone.waypoints.forEach((point) => bounds.push(point));

            L.circleMarker(drone.seed_latlon, {{
                radius: 7,
                color: drone.color,
                fillColor: drone.color,
                fillOpacity: 1.0,
                weight: 2
            }}).bindTooltip(`${{drone.drone_id}} seed`, {{ permanent: true, direction: 'top' }}).addTo(map);

            L.circleMarker(drone.cell_centroid, {{
                radius: 5,
                color: drone.color,
                fillColor: '#fff',
                fillOpacity: 1.0,
                weight: 2
            }}).bindTooltip(`${{drone.drone_id}} centroid`, {{ direction: 'right' }}).addTo(map);
        }});

        map.fitBounds(bounds, {{ padding: [30, 30] }});
        L.control.scale().addTo(map);
    </script>
</body>
</html>
"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = os.path.join(tempfile.gettempdir(), f"search_partition_map_{timestamp}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return html_file


def generate_search_partition_plot(task, partition_overview):
    task_id = task.get("task_id", "search-task")
    radius_m = float(partition_overview["search_radius_m"])
    lane_spacing_m = float(partition_overview["lane_spacing_m"])
    colors = ["#e63946", "#1d3557", "#2a9d8f", "#f4a261", "#6a4c93", "#ffb703"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle, Rectangle

        fig, ax = plt.subplots(figsize=(9, 9), dpi=160)
        ax.set_aspect("equal")
        ax.set_facecolor("#f7f3ea")
        fig.patch.set_facecolor("#ffffff")

        boundary = Circle((0, 0), radius_m, edgecolor="#111111", facecolor="#000000", alpha=0.04, linewidth=2)
        ax.add_patch(boundary)

        for idx, drone_id in enumerate(partition_overview["selected_drones"]):
            info = partition_overview["drones"][drone_id]
            color = colors[idx % len(colors)]
            cell_size = float(info.get("sample_step_m", 20.0))
            half = cell_size / 2.0

            for x_m, y_m in info.get("cells_local", []):
                rect = Rectangle(
                    (x_m - half, y_m - half),
                    cell_size,
                    cell_size,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=0.4,
                    alpha=0.18,
                )
                ax.add_patch(rect)

            waypoints = info.get("waypoints_local", [])
            if len(waypoints) >= 2:
                xs = [pt[0] for pt in waypoints]
                ys = [pt[1] for pt in waypoints]
                ax.plot(xs, ys, color=color, linewidth=2.2)

        centroid_x, centroid_y = info.get("cell_centroid_local", [0.0, 0.0])
        ax.scatter([centroid_x], [centroid_y], color=color, edgecolors="white", s=60, zorder=4)
        ax.text(centroid_x + 4, centroid_y + 4, drone_id, fontsize=9, weight="bold", color=color)

        ax.scatter([0], [0], color="#111111", s=40, zorder=5)
        ax.text(0, 0, " Center", fontsize=9, color="#111111", va="bottom")
        ax.set_xlim(-radius_m - 25, radius_m + 25)
        ax.set_ylim(-radius_m - 25, radius_m + 25)
        ax.set_title(f"Search Area Assignment\nTask: {task_id} | Radius: {radius_m:.0f} m | Lane Spacing: {lane_spacing_m:.0f} m")
        ax.set_xlabel("East/West (m)")
        ax.set_ylabel("North/South (m)")
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)

        image_file = os.path.join(tempfile.gettempdir(), f"search_partition_map_{timestamp}.png")
        fig.tight_layout()
        fig.savefig(image_file, bbox_inches="tight")
        plt.close(fig)
        return image_file
    except Exception:
        pass

    canvas_size = 1000
    margin = 60
    scale = (canvas_size - 2 * margin) / max(1.0, 2 * (radius_m + 25))

    def sx(x_m):
        return canvas_size / 2 + x_m * scale

    def sy(y_m):
        return canvas_size / 2 - y_m * scale

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{canvas_size/2}" y="28" text-anchor="middle" font-family="Arial" font-size="20">Search Area Assignment</text>',
        f'<text x="{canvas_size/2}" y="52" text-anchor="middle" font-family="Arial" font-size="12">Task: {task_id} | Radius: {radius_m:.0f} m | Lane Spacing: {lane_spacing_m:.0f} m</text>',
        f'<circle cx="{sx(0)}" cy="{sy(0)}" r="{radius_m * scale}" fill="rgba(0,0,0,0.04)" stroke="#111111" stroke-width="2"/>',
        f'<circle cx="{sx(0)}" cy="{sy(0)}" r="4" fill="#111111"/>',
    ]

    for idx, drone_id in enumerate(partition_overview["selected_drones"]):
        info = partition_overview["drones"][drone_id]
        color = colors[idx % len(colors)]
        cell_size = float(info.get("sample_step_m", 20.0))
        half = cell_size / 2.0
        for x_m, y_m in info.get("cells_local", []):
            parts.append(
                f'<rect x="{sx(x_m - half):.2f}" y="{sy(y_m + half):.2f}" width="{cell_size * scale:.2f}" height="{cell_size * scale:.2f}" fill="{color}" fill-opacity="0.18" stroke="{color}" stroke-width="0.3"/>'
            )
        waypoints = info.get("waypoints_local", [])
        if len(waypoints) >= 2:
            path = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in waypoints)
            parts.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        centroid_x, centroid_y = info.get("cell_centroid_local", [0.0, 0.0])
        parts.append(f'<circle cx="{sx(centroid_x):.2f}" cy="{sy(centroid_y):.2f}" r="6" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        parts.append(f'<text x="{sx(centroid_x) + 8:.2f}" y="{sy(centroid_y) - 8:.2f}" font-family="Arial" font-size="12" fill="{color}">{drone_id}</text>')

    parts.append("</svg>")
    image_file = os.path.join(tempfile.gettempdir(), f"search_partition_map_{timestamp}.svg")
    with open(image_file, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return image_file


def generate_search_partition_payload(task, partition_overview):
    task_id = task.get("task_id", "search-task")
    color_palette = ["#e63946", "#1d3557", "#2a9d8f", "#f4a261", "#6a4c93", "#ffb703"]
    drones = {}
    for idx, drone_id in enumerate(partition_overview["selected_drones"]):
        info = partition_overview["drones"][drone_id]
        drones[drone_id] = {
            "color": color_palette[idx % len(color_palette)],
            "sample_step_m": info.get("sample_step_m", 20.0),
            "cells_local": info.get("cells_local", []),
            "waypoints_local": info.get("waypoints_local", []),
            "cell_centroid_local": info.get("cell_centroid_local", [0.0, 0.0]),
        }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload_file = os.path.join(tempfile.gettempdir(), f"search_partition_map_{timestamp}.json")
    with open(payload_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "task_id": task_id,
                "search_radius_m": partition_overview["search_radius_m"],
                "lane_spacing_m": partition_overview["lane_spacing_m"],
                "selected_drones": partition_overview["selected_drones"],
                "drones": drones,
            },
            f,
        )
    return payload_file


def open_search_partition_map(task, partition_overview):
    payload_file = generate_search_partition_payload(task, partition_overview)
    popup_script = os.path.join(os.path.dirname(__file__), "search_partition_popup.py")
    success = False

    try:
        subprocess.Popen(
            ["python3", popup_script, payload_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        success = True
    except Exception:
        pass

    if not success:
        image_file = generate_search_partition_plot(task, partition_overview)
        abs_path = os.path.abspath(image_file)
        file_url = Path(abs_path).as_uri()
        try:
            subprocess.Popen(["xdg-open", abs_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success = True
        except Exception:
            pass

    print(f"🗺️ Search partition map {'opened' if success else 'generated'}: {payload_file}")
    return payload_file

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
