# NL_Swarm Project Handoff

## Purpose
`NL_Swarm` is a natural-language multi-UAV mission system. It lets an operator describe a mission in plain English or voice, converts that request into a structured task, resolves the target location, distributes the task to a swarm of drones, and executes the mission in simulation through MAVSDK and ArduPilot SITL.

This file is intended as a handoff summary for another AI system, especially for generating presentation slides that emphasize the project's strengths.

## High-Level Summary

### What the system does
- Accepts mission requests in text or voice.
- Extracts mission intent with an LLM.
- Resolves named locations or offset-based locations into coordinates.
- Sends the mission to multiple drone agents.
- Lets the agents bid for the task based on suitability.
- Assigns one or more winning drones depending on mission type.
- Executes missions in SITL through MAVSDK.
- Supports coordinated multi-drone search with partitioned coverage.

### Main mission flow
1. Operator enters a request such as `search the desert square by 2 drones`.
2. The operator pipeline extracts task type, location, duration, drone count, search settings, and metadata.
3. The location pipeline geocodes and confirms the target position.
4. The task is multicast to all drone agents.
5. Each drone evaluates itself and computes a bid.
6. The best drone or best `N` drones are selected.
7. For search missions, selected drones rendezvous near the search center, receive partition assignments, and execute coordinated lawnmower coverage.
8. The drones return to launch after the mission completes.

### Current deployed shape of the project
- 4 UAV system
- 4 ArduPilot SITL vehicles
- 4 MAVSDK servers
- 4 drone agents
- 1 natural-language operator
- 1 local search coordinator for cooperative coverage
- 1 Python popup map for search partition visualization

## Strengths To Highlight In Slides

### Core strengths
- Natural-language mission specification instead of manual waypoint entry
- End-to-end mission pipeline from human intent to UAV execution
- Multi-agent task allocation through distributed bidding
- Cooperative search with multi-drone area partitioning
- Automatic location interpretation and confirmation
- Voice input support
- Rich visualization of search-area assignment
- Modular architecture with clear separation between operator, location handling, coordination, and execution
- Simulation-first workflow using ArduPilot SITL and MAVSDK

### Research/demo strengths
- Demonstrates human-swarm interaction
- Shows AI-based intent extraction in a robotics workflow
- Combines LLM reasoning with deterministic geometry and control logic
- Good for demonstrations of task allocation, coordinated autonomy, and search coverage
- Easy to present because the system has visible operator input, visible drone behavior, and visible partition maps

## System Architecture

### Main layers

#### 1. Operator layer
Responsible for collecting mission input and sending structured tasks.

Primary file:
- [task_extract_send_rdp.py](/home/mohd/NL_Swarm/task_extract_send_rdp.py)

Responsibilities:
- Text input
- Voice input
- Whisper transcription
- LLM task extraction
- Location confirmation
- Task normalization
- Multicast transmission

#### 2. Location layer
Responsible for turning human place descriptions into usable coordinates.

Primary files:
- [location_handler_unified.py](/home/mohd/NL_Swarm/location_handler_unified.py)
- [location_extractor_ai.py](/home/mohd/NL_Swarm/location_extractor_ai.py)
- [geocoding_helper.py](/home/mohd/NL_Swarm/geocoding_helper.py)

Responsibilities:
- Distinguish direct locations from offset instructions
- Extract reference place and offset direction
- Geocode worldwide locations
- Confirm the final location with the operator

#### 3. Swarm/agent layer
Responsible for bidding, winner selection, and execution.

Primary files:
- [D1_agent_new.py](/home/mohd/NL_Swarm/D1_agent_new.py)
- [D2_agent_new.py](/home/mohd/NL_Swarm/D2_agent_new.py)
- [D3_agent_new.py](/home/mohd/NL_Swarm/D3_agent_new.py)
- [D4_agent_new.py](/home/mohd/NL_Swarm/D4_agent_new.py)

Responsibilities:
- Capability/resource checks
- Bid score calculation
- Peer-to-peer bid exchange
- Winner selection
- MAVSDK-based execution
- Search mission coordination

#### 4. Search coordination layer
Responsible for partitioning search space and assigning regions.

Primary files:
- [swarm_search.py](/home/mohd/NL_Swarm/swarm_search.py)
- [nl_coverage_coordinator.py](/home/mohd/NL_Swarm/nl_coverage_coordinator.py)

Responsibilities:
- Default search normalization
- Search geometry and partition logic
- Circular area representation
- Coverage cell assignment
- Stable multi-drone search coordination

#### 5. Visualization layer
Responsible for displaying mission geometry and search assignments.

Primary files:
- [map_visualizer_osm.py](/home/mohd/NL_Swarm/map_visualizer_osm.py)
- [search_partition_popup.py](/home/mohd/NL_Swarm/search_partition_popup.py)

Responsibilities:
- Generate a Python-rendered search assignment map
- Show circular search area
- Show per-drone assigned cells
- Show planned lawnmower paths

## Low-Level Runtime Flow

### Operator task extraction
In [task_extract_send_rdp.py](/home/mohd/NL_Swarm/task_extract_send_rdp.py):
- User chooses text or voice input
- Voice can use:
  - `parecord`
  - `arecord`
  - Windows `ffmpeg` microphone capture fallback
- Audio is transcribed with OpenAI Whisper
- Mission text is sent to the LLM
- The LLM returns a structured `Task`
- Search defaults are normalized
- Task is multicast on `239.255.0.2:30002`

### Search defaults currently used
- Default search diameter: `300 m`
- Default lane spacing: `30 m`
- Default duration: `3 min`
- Default partitioning: `voronoi`
- Default coverage pattern: `lawnmower`

### Bidding and selection
Each drone agent:
- receives the multicast task
- checks capabilities
- checks resources and state
- computes a bid score
- exchanges bids with peers over local UDP
- sorts all bids
- selects top `N` winners where `N = required_drones`

### Search mission behavior
For search tasks:
- selected drones rendezvous near the search center with about `10 m` separation
- all selected drones must become ready before the coordinator assigns search regions
- the coordinator partitions the circular search space across the selected drones
- the leader drone opens the partition map popup
- each selected drone flies its assigned lawnmower region

### Search coordination details
In [nl_coverage_coordinator.py](/home/mohd/NL_Swarm/nl_coverage_coordinator.py):
- task state stores:
  - center coordinates
  - radius
  - cell size
  - selected drones
  - explored cells
- drones send:
  - `search_registration`
  - `state_update`
  - `coverage_update`
- coordinator sends:
  - `region_assignment`
- coordinator now keeps assignments stable during normal coverage, so drones do not re-fly the same row repeatedly

### Search geometry details
In [swarm_search.py](/home/mohd/NL_Swarm/swarm_search.py):
- search space is modeled as a circle
- local metric coordinates are used for planning
- seed positions are placed around the search center
- Voronoi or sector fallback partitioning is computed
- row-based lawnmower paths are generated
- the visualization uses the same geometry basis as the planner

## Networking Overview

### Main channels
- Task multicast:
  - `239.255.0.2:30002`
- Peer heartbeat/broadcast:
  - `239.255.0.1:30001`
- Search assignment multicast:
  - `239.255.0.3:30003`
- Coordinator local socket:
  - `127.0.0.1:61000`

### Drone config
Primary config file:
- [drone_config.json](/home/mohd/NL_Swarm/drone_config.json)

Contains:
- drone IDs
- MAVSDK gRPC ports
- bid ports
- SITL UDP ports

## Simulation Stack

### Main simulation components
- ArduPilot SITL for vehicle simulation
- MAVSDK server for API access
- QGroundControl for visualization and control

### Startup scripts
- [scripts/start_sitl_4.sh](/home/mohd/NL_Swarm/scripts/start_sitl_4.sh)
- [scripts/start_mavsdk_4.sh](/home/mohd/NL_Swarm/scripts/start_mavsdk_4.sh)
- [scripts/start_agents_4.sh](/home/mohd/NL_Swarm/scripts/start_agents_4.sh)
- [scripts/start_coordinator.sh](/home/mohd/NL_Swarm/scripts/start_coordinator.sh)
- [scripts/start_operator_tmux.sh](/home/mohd/NL_Swarm/scripts/start_operator_tmux.sh)
- [scripts/stop_all.sh](/home/mohd/NL_Swarm/scripts/stop_all.sh)

## Important Current Behaviors

### Search visualization
- The search partition map is generated in Python, not as a browser page.
- It opens as a popup window and shows:
  - circular search boundary
  - per-drone assigned region cells
  - planned path
  - center point

### Voice input
- Voice input works through a Windows microphone capture fallback using `ffmpeg.exe`.
- This was added because Linux-side `parecord` and `arecord` were not available in the runtime environment.

### Search execution improvements already made
- drones no longer stack on one exact center point
- search rendezvous points are separated
- row assignments are stable during coverage
- duplicated same-row replanning was removed

## Files Most Important For Presentation-Oriented Discussion

If another AI only needs a minimal understanding, these are the best files to mention:
- [task_extract_send_rdp.py](/home/mohd/NL_Swarm/task_extract_send_rdp.py)
- [location_handler_unified.py](/home/mohd/NL_Swarm/location_handler_unified.py)
- [geocoding_helper.py](/home/mohd/NL_Swarm/geocoding_helper.py)
- [D1_agent_new.py](/home/mohd/NL_Swarm/D1_agent_new.py)
- [D2_agent_new.py](/home/mohd/NL_Swarm/D2_agent_new.py)
- [D3_agent_new.py](/home/mohd/NL_Swarm/D3_agent_new.py)
- [D4_agent_new.py](/home/mohd/NL_Swarm/D4_agent_new.py)
- [swarm_search.py](/home/mohd/NL_Swarm/swarm_search.py)
- [nl_coverage_coordinator.py](/home/mohd/NL_Swarm/nl_coverage_coordinator.py)
- [map_visualizer_osm.py](/home/mohd/NL_Swarm/map_visualizer_osm.py)
- [search_partition_popup.py](/home/mohd/NL_Swarm/search_partition_popup.py)
- [drone_config.json](/home/mohd/NL_Swarm/drone_config.json)

## Suggested Slide Angles For ChatGPT

### Slide angle 1: Problem and motivation
- UAV mission setup is often manual and slow
- Swarm coordination is complex for human operators
- Natural-language interaction can reduce friction

### Slide angle 2: Solution overview
- AI extracts mission intent
- Location system resolves the target
- Drone agents bid and self-select
- Search coordinator partitions the area

### Slide angle 3: System architecture
- Operator
- LLM extraction
- Location pipeline
- Drone agents
- Search coordinator
- MAVSDK/SITL/QGC

### Slide angle 4: Key strengths
- Human-friendly tasking
- Distributed autonomy
- Multi-drone coordination
- Visual search partitioning
- Modular design

### Slide angle 5: Search mission showcase
- Multi-drone rendezvous
- Voronoi area split
- Stable row-based coverage
- Live execution in SITL

### Slide angle 6: Engineering value
- Rapid experimentation
- Safe simulation environment
- Extensible architecture
- Good platform for research demos

## Short One-Paragraph Description For Reuse
`NL_Swarm` is an AI-enabled multi-UAV mission system that converts natural-language or voice commands into executable swarm missions. It combines LLM-based task extraction, intelligent location resolution, distributed drone bidding, and coordinated multi-drone search planning on top of ArduPilot SITL and MAVSDK. The system is designed to demonstrate practical human-swarm interaction, especially for missions such as cooperative area search, where multiple UAVs divide a circular search space and execute structured coverage patterns with visual assignment feedback.
