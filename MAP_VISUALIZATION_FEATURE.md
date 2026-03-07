# Map Visualization Feature - Enhanced Version

## Overview
The system now includes **enhanced map visualization** that shows BOTH the reference location and the target location with a connecting line. This provides complete visual confirmation of the mission planning before execution.

## Visual Features

### 🔵 Reference Location (Blue Marker)
- Shows the original known location (e.g., "Desert Square")
- Labeled with "R" for Reference
- Displays exact GPS coordinates
- Clickable popup with location details

### 🔴 Target Location (Red Marker)
- Shows the calculated mission target (after applying offset)
- Labeled with "T" for Target
- Displays exact GPS coordinates
- Clickable popup with offset information

### ➡️ Connecting Line (Orange)
- Visual line connecting reference to target
- Shows direction and distance visually
- Includes arrow pointing to target
- Helps verify the offset was applied correctly

### 📊 Info Panel
- Mission overview sidebar
- Distance and direction display
- Both coordinates shown
- Can be toggled on/off
- Timestamp of map generation

## Available Map Visualizers

### 1. **Enhanced Google Maps** (`map_visualizer_enhanced.py`)
**Best for:** Rich features and detailed satellite imagery

**Features:**
- High-quality satellite imagery
- Street view integration
- Full map controls (zoom, satellite/map toggle)
- Custom styled markers and lines
- Interactive popups

**Requirements:**
- Google Maps API key (for embedded HTML version)
- OR use simple URL mode (no API key needed)

**Usage:**
```python
from map_visualizer_enhanced import open_enhanced_map

ref_coords = [-35.36309804, 149.16348567]  # Desert Square
target_coords = [-35.36942804, 149.16348567]  # 700m south
ref_name = "Desert Square"
distance = 700
direction = "south"

# Open interactive HTML map
open_enhanced_map(ref_coords, target_coords, ref_name, distance, direction)
```

### 2. **OpenStreetMap** (`map_visualizer_osm.py`)
**Best for:** No API key required, open source

**Features:**
- No API key required ✅
- No usage limits ✅
- Open source mapping
- Uses Leaflet.js
- Interactive markers and popups
- Works offline after first load

**Usage:**
```python
from map_visualizer_osm import open_osm_map

ref_coords = [-35.36309804, 149.16348567]
target_coords = [-35.36942804, 149.16348567]
ref_name = "Desert Square"
distance = 700
direction = "south"

# Open OpenStreetMap visualization
open_osm_map(ref_coords, target_coords, ref_name, distance, direction)
```

### 3. **Simple Google Maps URL** (No API key)
**Best for:** Quick viewing without HTML files

**Features:**
- Opens directly in Google Maps website
- No API key required
- Shows path between locations
- Can use Google Maps mobile app

**Usage:**
```python
from map_visualizer_enhanced import open_simple_google_maps

open_simple_google_maps(ref_coords, target_coords, ref_name, distance, direction)
```

## Example Visualization

### Command:
```
User: deliver 700 meters to the south of the desert square
```

### What Opens in Browser:

```
╔════════════════════════════════════════════════════════════════╗
║  🎯 Mission Overview                                [×]         ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       ║
║  Offset: 700 meters south                                      ║
║                                                                 ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       ║
║  🔵  Desert Square                                              ║
║      -35.363098, 149.166742                                    ║
║                                                                 ║
║  🔴  Target Location                                            ║
║      -35.369428, 149.166742                                    ║
║                                                                 ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       ║
║  📅 Generated: 2025-11-09 21:11:14                             ║
╚════════════════════════════════════════════════════════════════╝

                    [MAP VIEW - Satellite/Hybrid]
                    
                           🔵 R  ← Desert Square
                            │
                            │ Orange line (700m)
                            │ with arrow ➡️
                            ↓
                           🔴 T  ← Target Location
                    
                    [Zoom Controls] [Map/Satellite] [Street View]
```

## Integration with Task Extraction

The map visualization is integrated into the task extraction workflow:

### Updated Workflow:
```
1. User enters command
   "deliver 700 meters south of desert square"
   
2. System extracts task information
   ✅ Task type: deliver
   ✅ Reference: Desert Square
   ✅ Offset: 700m south
   ✅ Target coordinates calculated
   
3. System displays extraction results with timestamps
   [2025-11-09 21:11:14.123] 🧭 Extracted offset: 700m south
   [2025-11-09 21:11:14.124] 🗺️ Reference location: Desert Square
   [2025-11-09 21:11:14.125] 📍 Calculated coordinates: [-35.369428, 149.166742]
   
4. System prompts for map visualization
   "Would you like to view this location on a map? (yes/no): "
   
5. If user says "yes":
   - Map opens in browser
   - Shows both reference and target
   - User can verify location visually
   
6. User confirms task
   "Send this task to agents? (yes/no): "
   
7. Mission dispatched to agents
```

## Benefits

### 1. **Visual Verification**
- See exactly where the drone will go
- Verify offset was applied correctly
- Check for obstacles or no-fly zones
- Confirm location makes sense

### 2. **Error Prevention**
- Catch calculation errors before mission starts
- Verify direction (north/south/east/west)
- Ensure distance is appropriate
- Prevent missions to wrong locations

### 3. **Mission Planning**
- Understand terrain and surroundings
- Check proximity to buildings/structures
- Verify altitude requirements
- Plan for obstacles

### 4. **Training & Demonstration**
- Visual aid for understanding offsets
- Clear display of reference locations
- Helps new users learn the system
- Great for mission briefings

### 5. **Documentation**
- Maps are saved as HTML files
- Can be archived with mission logs
- Shareable with team members
- Timestamped for tracking

## Map Files

Generated maps are saved to:
```
/tmp/mission_map_YYYYMMDD_HHMMSS.html
```

Example:
```
/tmp/mission_map_20251109_211114.html
```

You can:
- Open them later for review
- Share them via email/chat
- Archive them with mission logs
- Print them for briefings

## Testing

### Test Enhanced Google Maps:
```bash
cd /home/moham/mavsdk_bin/mini
python map_visualizer_enhanced.py
```

### Test OpenStreetMap:
```bash
cd /home/moham/mavsdk_bin/mini
python map_visualizer_osm.py
```

## Configuration Options

### Choose Map Type
You can select which map provider to use:

```python
# Option 1: Enhanced HTML with Google Maps (requires API key for best features)
from map_visualizer_enhanced import open_enhanced_map
filepath = open_enhanced_map(ref_coords, target_coords, ref_name, distance, direction)

# Option 2: OpenStreetMap (no API key needed)
from map_visualizer_osm import open_osm_map
filepath = open_osm_map(ref_coords, target_coords, ref_name, distance, direction)

# Option 3: Simple Google Maps URL (no HTML file, opens directly)
from map_visualizer_enhanced import open_simple_google_maps
open_simple_google_maps(ref_coords, target_coords, ref_name, distance, direction)
```

### Customize Map Style
In the HTML files, you can change:
- **Map type**: 'roadmap', 'satellite', 'hybrid', 'terrain'
- **Zoom level**: Default 15, adjust for wider/closer view
- **Marker colors**: Change blue/red to your preference
- **Line style**: Color, thickness, dashing
- **Info panel**: Position, size, content

## API Key Setup (Optional)

### For Google Maps Enhanced Version:

1. Get an API key:
   - Visit: https://developers.google.com/maps/documentation/javascript/get-api-key
   - Create a Google Cloud project
   - Enable "Maps JavaScript API"
   - Create credentials

2. Add key to HTML:
   - Open generated HTML file
   - Find: `src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"`
   - Replace `YOUR_API_KEY` with your actual key

3. Or use environment variable:
   ```bash
   export GOOGLE_MAPS_API_KEY="your-key-here"
   ```

### For OpenStreetMap:
**No API key required!** ✅ Just use it directly.

## Troubleshooting

### Map doesn't open in browser
- Check if `webbrowser` module can open files
- Manually open the HTML file from `/tmp/`
- Try a different browser

### Google Maps shows "For development purposes only"
- This is normal without an API key
- Map still works, just shows watermark
- Use OpenStreetMap version instead (no watermark)

### Markers not showing
- Check JavaScript console for errors
- Verify coordinates are valid
- Try OpenStreetMap version

### Map is too zoomed in/out
- Edit the HTML file
- Change zoom level: `zoom: 15` → adjust number (1-20)
- Save and reload

## Future Enhancements (Planned)

### Phase 1 (Current) ✅
- ✅ Show reference and target locations
- ✅ Connecting line with direction
- ✅ Interactive popups
- ✅ Info panel with mission details
- ✅ Both Google Maps and OSM support

### Phase 2 (Future)
- 🔲 Show all agent positions in real-time
- 🔲 Display mission path with waypoints
- 🔲 Add no-fly zones overlay
- 🔲 Show battery consumption heat map
- 🔲 Display communication range circles
- 🔲 Add terrain elevation profile

### Phase 3 (Advanced)
- 🔲 3D visualization with altitude
- 🔲 Live tracking during mission
- 🔲 Historical mission replay
- 🔲 Multiple mission comparison
- 🔲 Export to KML/GeoJSON
- 🔲 Integration with mission logs

## Summary

✅ **Enhanced visualization implemented**  
✅ **Shows both reference and target locations**  
✅ **Visual line connects the two points**  
✅ **Interactive markers and popups**  
✅ **Two map providers available (Google & OSM)**  
✅ **No API key required for OSM version**  
✅ **Maps saved for later review**  
✅ **Integrated into task extraction workflow**  

---
**Status**: ✅ Complete and Tested  
**Files**:
- `/home/moham/mavsdk_bin/mini/map_visualizer_enhanced.py`
- `/home/moham/mavsdk_bin/mini/map_visualizer_osm.py`

**Last Updated**: November 9, 2025
