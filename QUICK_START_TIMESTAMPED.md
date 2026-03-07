# Quick Start: Timestamped Multi-UAV System

## Run the System

```bash
cd /home/moham/mavsdk_bin/mini
python task_extract_send_rdp.py
```

## Example Input (with spelling errors - now handled!)

All of these will work correctly:

### Exact Names
```
deliver to the desert square
search the street gardens
fly to alexander center area
```

### With Spelling Errors (Fuzzy Matching)
```
deliver to the deserrt square    ← extra 'r', will match "desert square"
search the streat gardens        ← typo, will match "street gardens"  
fly to alexader center          ← missing 'n', will match "alexander center"
```

### With Offset Instructions
```
look for a person 700 meters to the south of the desert square
deliver 500 meters to the east of street gardens
search 1 km to the west of village area
```

### Even With Spelling Errors in Offset Instructions!
```
look for a person 700 meters to the south of the deserrt square
   ↑ Will fuzzy match to "desert square" and calculate correct offset
```

## Expected Output Format

```
[2025-11-09 19:54:28.940] ✅ API key loaded: sk-proj-80...
[2025-11-09 19:54:28.977] 🤖 AI-Powered Drone Task Operator (RDP-Compatible)
[2025-11-09 19:54:28.985] ✅ Audio tools available: PulseAudio recording
[2025-11-09 19:55:12.381] 🔄 Extracting task information using AI...
[2025-11-09 19:55:18.503] 🧭 Extracted offset: 700.0 meters to the south of 'deserrt square'
[2025-11-09 19:55:18.503] 🔍 Fuzzy matched 'deserrt square' to 'desert square' (similarity: 1.00)
[2025-11-09 19:55:18.503] 🗺️ Reference location: Desert Square at [-35.36309804, 149.16348567]
[2025-11-09 19:55:18.503] 📍 Calculated new coordinates: [-35.36942804, 149.16348567]
[2025-11-09 19:55:18.503] ✅ Task extraction completed!
[2025-11-09 19:55:18.503] 
============================================================
[2025-11-09 19:55:18.503] 🎯 EXTRACTED MISSION TASK
[2025-11-09 19:55:18.503] ============================================================
[2025-11-09 19:55:18.503] 📋 Task ID: search_20231130000001
[2025-11-09 19:55:18.503] 🎪 Type: search
[2025-11-09 19:55:18.504] 📍 Location: -35.36942804, 149.16348567
[2025-11-09 19:55:18.504] 🏷️ Location Name: Desert Square (offset applied)
[2025-11-09 19:55:18.504] 🛫 Altitude: 30 meters
[2025-11-09 19:55:18.504] ⏱️ Duration: 1min
[2025-11-09 19:55:18.504] 🌤️ Weather: clear
[2025-11-09 19:55:18.504] 🏔️ Terrain: urban
[2025-11-09 19:55:18.504] 🚨 Priority: normal
[2025-11-09 19:55:18.504] 📝 Description: search for a person 700 meters to the south of Desert Square
[2025-11-09 19:55:18.504] 🗺️ Reference Location: Desert Square at -35.36309804, 149.16348567
[2025-11-09 19:55:18.504] ↔️ Offset: 700.0 meters to the south
[2025-11-09 19:55:18.504] ============================================================
```

## Key Features

✅ **Every line has a timestamp** - Format: `[YYYY-MM-DD HH:MM:SS.mmm]`  
✅ **Fuzzy location matching** - Handles spelling errors automatically  
✅ **Offset calculation** - Precise GPS coordinate computation  
✅ **Reference tracking** - Shows original location and offset applied  
✅ **Complete audit trail** - Every operation is logged with millisecond precision  

## Collect Research Data

All logs are timestamped for easy analysis:

1. **Task Extraction Logs** - From terminal output (pipe to file)
2. **Agent Logs** - `/home/moham/mavsdk_bin/mini/V3/logs/uav*.csv`
3. **Timing Logs** - `/home/moham/mavsdk_bin/mini/V3/timing_logs/*.csv`

### Save Terminal Output
```bash
python task_extract_send_rdp.py | tee task_extraction_$(date +%Y%m%d_%H%M%S).log
```

### Analyze Timing
```bash
cd /home/moham/mavsdk_bin/mini/V3
python calculate_recovery_times.py
```

## Reference Locations

| Name | Coordinates |
|------|-------------|
| Street Gardens | -35.36088387, 149.16674193 |
| Desert Square | -35.36309804, 149.16348567 |
| Alexander Center Area | -35.37111574, 149.17183885 |
| Village Area | -35.35723482, 149.17015126 |
| Compound Area | -35.35389604, 149.15062472 |
| South Sector Area | -35.363261, 149.165230 |

## Tips

1. **Spelling doesn't have to be perfect** - The system will fuzzy match
2. **Use natural language** - "look for", "search for", "deliver to" all work
3. **Offsets are flexible** - "500 meters", "0.5 km", "1 km" all supported
4. **Timestamps are automatic** - Every operation is logged precisely

---
Ready to collect high-quality timestamped data for your research! 🚁📊
