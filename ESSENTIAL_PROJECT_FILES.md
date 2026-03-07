# 📋 ESSENTIAL PROJECT FILES

## Core Mission System Files

### Main Application
- **`task_extract_send_rdp.py`** - Main mission workflow (voice/text input, AI extraction, sends to drones)

### Location Handling (NEW - AI-based)
- **`location_handler_unified.py`** - Unified location processor (direct + offset locations, uses AI extraction)
- **`location_extractor_ai.py`** - AI-based location extraction using OpenAI Structured Outputs
- **`geocoding_helper.py`** - Worldwide geocoding (OpenStreetMap Nominatim)
- **`map_simple_fallback.py`** - Auto-opens Google Maps in browser for user confirmation

### Legacy Location Files (kept for compatibility)
- **`location_extractor.py`** - Direct location extraction (legacy)
- **`map_visualizer.py`** - Map visualization with reference points
- **`map_visualizer_enhanced.py`** - Enhanced map with HTML
- **`map_visualizer_osm.py`** - OpenStreetMap integration

### Drone Agent Files
- **`D1_agent_new.py`** - Drone 1 agent (with conflict resolution)
- **`D2_agent_new.py`** - Drone 2 agent (with conflict resolution)
- **`D3_agent_new.py`** - Drone 3 agent (with conflict resolution)
- **`D4_agent_new.py`** - Drone 4 agent (with conflict resolution)
- **`D5_agent_new.py`** - Drone 5 agent (minimal implementation)

### Configuration Files
- **`drone_config.json`** - Drone configuration (ports, IDs, locations)
- **`battery_config.parm`** - Battery parameters
- **`mav.parm`** - MAVLink parameters
- **`.env`** (in parent directory) - OpenAI API key

## Documentation Files

### Implementation Documentation
- **`CONFLICT_RESOLUTION_UPDATE.md`** - UAV bidding conflict resolution implementation
- **`TWO_STEP_LOCATION_PROCESS.md`** - Explains AI extraction + Python calculation architecture
- **`UNIFIED_INTEGRATION_COMPLETE.md`** - Integration summary and quick start
- **`FINAL_SUMMARY.md`** - Quick reference guide
- **`VISUAL_ARCHITECTURE.md`** - Visual flow diagrams
- **`WORLDWIDE_LOCATIONS_GUIDE.md`** - Worldwide location support guide
- **`INTEGRATION_SUMMARY.md`** - Previous integration notes
- **`IMPLEMENTATION_COMPLETE.md`** - Implementation completion notes
- **`How_to_start_new_system.md`** - System startup guide

### Previous Documentation
- **`README_Voice_Input.md`** (in structured output/) - Voice input documentation

## Important Notes

### What Each Core File Does:

1. **`task_extract_send_rdp.py`**
   - Entry point for missions
   - Gets voice or text input from user
   - Calls `location_handler_unified.py` to extract location
   - Calls AI to extract mission details (task type, altitude, etc.)
   - Sends task to drone swarm via multicast

2. **`location_extractor_ai.py`**
   - Uses OpenAI Structured Outputs (Pydantic models)
   - AI extracts: direct location OR (distance + direction + reference)
   - Cleans up filler words ("the capital Amman" → "Amman")
   - Returns structured data for Python to process

3. **`location_handler_unified.py`**
   - Calls `location_extractor_ai.py` to get AI extraction
   - For offset: geocodes reference, calculates new coordinates in Python
   - For direct: geocodes location
   - Shows both locations on Google Maps
   - User confirms before proceeding

4. **`geocoding_helper.py`**
   - Queries OpenStreetMap Nominatim API
   - Returns multiple results for ambiguous locations
   - User selects correct location

5. **`map_simple_fallback.py`**
   - Opens Google Maps in browser (multiple fallback methods)
   - Shows coordinates with label

6. **Drone Agents (D1-D5)**
   - Listen for tasks via multicast
   - Perform self-assessment and bidding
   - **Winner announcement and conflict resolution protocol**
   - Execute missions (takeoff, fly to location, land)
   - Report status back

## Files NOT Essential (Can be removed)

- `test_*.py` files in root and structured output/ (test scripts)
- `demo_*.py` files (demo scripts)
- `*.parm:Zone.Identifier` files (Windows zone markers)
- `*.py:Zone.Identifier` files (Windows zone markers)
- `eeprom.bin` (temporary files)
- `mav.tlog` / `mav.tlog.raw` (log files)

## Key Architecture

```
User Input
    ↓
task_extract_send_rdp.py
    ↓
location_handler_unified.py
    ↓
location_extractor_ai.py (AI extraction)
    ↓
geocoding_helper.py (get coordinates)
    ↓
Python calculates offset (if needed)
    ↓
map_simple_fallback.py (show on Google Maps)
    ↓
User confirms
    ↓
AI extracts mission details
    ↓
Send to drone agents (D1-D5)
```

## To Run System

```bash
# Start main mission system
python3 task_extract_send_rdp.py

# Try prompts like:
# - "deliver at 2 km to the north of Amman"
# - "deliver at Paris"
# - "search at Eiffel Tower"
```

## Dependencies

Required Python packages:
- `openai` (for AI extraction)
- `pydantic` (for structured outputs)
- `requests` (for geocoding)
- `python-dotenv` (for API key)
- `mavsdk` (for drone control)

Install:
```bash
pip install openai pydantic requests python-dotenv mavsdk
```
