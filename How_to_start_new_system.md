# How to Start the Multi-UAV Task Selection System

## Overview
This system implements a two-phase drone selection process:
1. **Phase 1**: Each drone performs self-assessment (capabilities, battery, environment)
2. **Phase 2**: Eligible drones bid competitively, highest score wins and executes mission

## System Components

### Communication Setup
- **Peer Communication**: Multicast UDP `239.255.0.1:30001` (proven working, no cross-talk)
- **Task Communication**: Multicast UDP `239.255.0.2:30002` (operator tasks and bidding)
- **MAVSDK Servers**: UAV1 on port `50040`, UAV2 on port `50041`

### Files
- `D1_agent_new.py` - UAV1 agent with two-phase task selection
- `D2_agent_new.py` - UAV2 agent with two-phase task selection  
- `operator_send_task_new.py` - Operator console for sending missions

## Startup Sequence

### Step 1: Start SITL Instances
```bash
# Terminal 1: UAV1 SITL (Canberra, Australia)
sim_vehicle.py -v ArduCopter --console --map \
  --out=udp:127.0.0.1:14550 \
  --out=udp:127.0.0.1:14540 \
  -L CMAC \
  --add-param-file=battery_config.parm

# Terminal 2: UAV2 SITL (100m east of UAV1 in Canberra)
sim_vehicle.py -v ArduCopter -I 1 --sysid 2 --console --map \
  --out=udp:127.0.0.1:14550 \
  --out=udp:127.0.0.1:14541 \
  -L CMAC_100M_EAST \
  --add-param-file=battery_config.parm
```
sim_vehicle.py -v ArduCopter -I 2 --sysid 3 --console --map   --out=udp:127.0.0.1:14550   --out=udp:127.0.0.1:14542   -L SITL_3_LOCATION   --add-param-file=battery_config.parm

sim_vehicle.py -v ArduCopter -I 3 --sysid 4 --console --map   --out=udp:127.0.0.1:14550   --out=udp:127.0.0.1:14543   -L SITL_4_LOCATION   --add-param-file=battery_config.parm

sim_vehicle.py -v ArduCopter -I 4 --sysid 5 --console --map   --out=udp:127.0.0.1:14550   --out=udp:127.0.0.1:14544   -L SITL_5_LOCATION   --add-param-file=battery_config.parm
### Step 2: Start MAVSDK Servers
```bash
# Terminal 3: UAV1 MAVSDK Server
mavsdk_server -p 50040 udp://:14540

# Terminal 4: UAV2 MAVSDK Server  
mavsdk_server -p 50041 udp://:14541

# Additional UAVs MAVSDK Servers
mavsdk_server -p 50042 udp://:14542
mavsdk_server -p 50043 udp://:14543
mavsdk_server -p 50044 udp://:14544
```

### Step 3: Start Drone Agents
```bash
# Terminal 5: UAV1 Agent
python D1_agent_new.py

# Terminal 6: UAV2 Agent
python D2_agent_new.py
```
moham@Jad:~/mavsdk_bin/structured output$ python task_extract_send_rdp.py
### Step 4: Start Operator Console

Choose one of the following operator interfaces:

#### Option A: Manual Task Entry (Structured)
```bash
# Terminal 7: Structured Task Operator
python operator_send_task_new.py
```

#### Option B: Natural Language Task Input (AI-Powered)
```bash
# Terminal 7: Natural Language Operator
cd "structured output"
python task_extract_send.py
moham@Jad:~/mavsdk_bin/structured output$ python task_extract_send_rdp.py

```

**Natural Language Examples:**
- "Search for missing hiker at coordinates 47.1234, 8.5678 at 30 meters altitude"
- "Deliver medical supplies to location 47.125, 8.567, should take about 20 minutes"
- "Emergency search and rescue mission in mountain area, urgent priority"

> **Note**: The natural language interface requires OpenAI API key in `.env` file

## Expected Behavior

### Agent Startup
Each agent will:
1. Connect to its MAVSDK server (no cross-talk)
2. Wait for sensor health
3. Begin peer heartbeat communication
4. Display "Ready for missions!"

### Mission Flow
1. **Operator** sends task via multicast to both agents
2. **Phase 1**: Each agent performs self-assessment
   - ✅ Capabilities check
   - ✅ Battery/resources check  
   - ✅ Environment check
   - Only agents passing ALL THREE proceed to Phase 2
3. **Phase 2**: Eligible agents bid competitively
   - Calculate bid score (base + distance + specialization)
   - Exchange scores via multicast
   - Highest score wins and executes mission
   - Loser returns to standby

### Bid Scoring
- **UAV1**: Gets 10% bonus for search/SAR missions
- **UAV2**: Gets 10% bonus for delivery missions
- Distance factor: Closer drones get higher scores
- Random base score: Introduces controlled uncertainty

## Battery Configuration

For longer missions, the system uses `battery_config.parm`:
```
BATT_CAPACITY 20000    # 20Ah battery (instead of 5Ah default)
SIM_BATT_VOLTAGE 15.7  # Higher voltage
BATT_LOW_VOLT 0.0      # Disable low battery warnings  
BATT_FS_LOW_ACT 0      # Disable low battery failsafe
```

## Testing Scenarios

### Scenario 1: Both Agents Eligible
- Both agents pass self-assessment
- Both calculate bid scores
- Higher score wins and executes mission
- Loser stands by for next mission

### Scenario 2: One Agent Ineligible  
- One agent fails battery/capability check
- Only eligible agent proceeds to execution
- No competitive bidding needed

### Scenario 3: No Agents Eligible
- Both agents fail self-assessment
- Mission remains unassigned
- Agents ready for next suitable mission

### Scenario 4: Battery Limit Testing
Send "LONG_MISSION_001" (60min duration) to test battery filtering

### Scenario 5: Natural Language Task Testing
Use the AI-powered interface to test various mission descriptions:
```bash
cd "structured output"
python test_task_extraction.py  # Test extraction without sending
python task_extract_send.py     # Full natural language interface
```

Example mission descriptions:
- "Search the forest area for missing campers, 30 meter altitude"
- "Deliver emergency supplies to mountain rescue station, high priority"
- "Survey the industrial area near the river, take about 25 minutes"

## Troubleshooting

### No Agent Response
- Check SITL and MAVSDK servers are running
- Verify agents show "Ready for missions!"
- Check multicast communication: `239.255.0.2:30002`

### MAVSDK Connection Issues
- Verify correct ports: UAV1=50040, UAV2=50041
- Check no port conflicts with other processes
- Restart MAVSDK servers if needed

### Cross-Talk Issues
- This system uses proven multicast setup with no cross-talk
- Each agent connects to its own MAVSDK server
- Peer communication is clearly separated from MAVSDK

## Mission Restart

For new missions (without full restart):
1. Stop agents: `Ctrl+C` in agent terminals
2. Restart agents: `python D1_agent_new.py` and `python D2_agent_new.py`
3. SITL and MAVSDK servers can keep running

For full reset:
1. Stop all processes
2. Restart in sequence: SITL → MAVSDK → Agents

## Communication Verification

Monitor terminals to see:
- **Agents**: Peer heartbeats, task reception, bidding process
- **Operator**: Task transmission confirmations
- **Phase 1**: Self-assessment results for each agent
- **Phase 2**: Competitive bidding and winner selection

## Named Location Support

The system now supports **named locations** that are automatically mapped to specific coordinates:

- **"street gardens"** or **"Street Gardens"** → Coordinates: -35.36088387, 149.16674193

### Example Usage:
```
# Voice or text input examples:
"Search for survivors in street gardens"
"Emergency delivery to Street Gardens" 
"Survey the street gardens area"
```

The AI will automatically recognize these named locations and convert them to the correct coordinates for mission planning.

## System Capabilities Summary

✅ **Multi-UAV SITL Simulation** - Two drones with 100m separation
✅ **Australian CMAC Locations** - Custom locations in Canberra
✅ **Natural Language Input** - GPT-4 powered task extraction 
✅ **Voice Input Support** - Speech-to-text with OpenAI Whisper
✅ **Named Location Mapping** - "street gardens" automatically mapped
✅ **RDP/Remote Environment Support** - Works over remote desktop
✅ **Robust Error Handling** - Graceful fallback and troubleshooting
✅ **Agent Bidding System** - Competitive task assignment
✅ **Real-time Monitoring** - Live mission execution tracking

The system is ready for operational use with natural language mission assignment!
