# Multi-UAV Competitive Bidding System - Communication Setup Report

## Executive Summary

This document outlines the complete communication infrastructure required for deploying a multi-UAV competitive bidding system in real-world operations. The system currently operates in simulation using local UDP networking but requires specific hardware components for field deployment.

## Current System Architecture (Simulation)

### Three-Layer Communication Model

1. **Peer Heartbeat Communication** (Multicast UDP)
2. **Task Distribution** (Multicast UDP) 
3. **Competitive Bidding** (Point-to-Point UDP)

## Real-World Hardware Requirements

### 1. Ground Control Station (GCS) Hardware

#### Primary Ground Station
- **Computer Requirements:**
  - Intel i7 or AMD Ryzen 7 (minimum)
  - 16GB RAM (minimum), 32GB recommended
  - 1TB SSD storage
  - Multiple USB 3.0+ ports
  - Ethernet port for wired connections
  - Linux-compatible (Ubuntu 20.04+ recommended)

#### Communication Hardware for GCS
- **Primary Radio System:**
  - **SiK Telemetry Radio (915MHz/433MHz)**
    - 3DR Radio V2 or compatible
    - Range: 1-5km (depending on antenna)
    - Data rate: 57.6 kbps
    - Purpose: MAVSDK telemetry and control
    - Quantity: 1 per drone + 1 for GCS

- **Secondary Communication (Optional but Recommended):**
  - **LoRa Module (915MHz/868MHz)**
    - Dragino LG308 Gateway or similar
    - Range: 10-15km in open areas
    - Low power, reliable for status updates
    - Purpose: Backup communication and extended range

- **High-Bandwidth Option:**
  - **4G/5G Cellular Modem**
    - Huawei E3372 USB dongle or similar
    - Unlimited data plan required
    - Purpose: Task distribution and video streaming
    - Fallback when other methods fail

#### Antenna Systems for GCS
- **Directional Antenna:**
  - Yagi antenna for SiK radio (900MHz)
  - 10-15 dBi gain
  - Antenna rotator for tracking drones
  - Purpose: Extended range communication

- **Omnidirectional Antenna:**
  - Fiberglass whip antenna
  - 5-8 dBi gain
  - Purpose: Multi-drone communication

### 2. Individual Drone Communication Hardware

#### Per-Drone Communication Stack

**Primary Flight Control Communication:**
- **SiK Telemetry Radio**
  - 3DR Radio V2 or RFD900x
  - Matched frequency with GCS
  - Integrated with autopilot (Pixhawk)
  - Purpose: MAVSDK connection and flight control

**Peer-to-Peer Communication:**
- **WiFi Module (Short Range)**
  - ESP32 with WiFi capability
  - 2.4GHz/5GHz dual-band
  - Range: 100-500m (line of sight)
  - Purpose: Fast bidding exchange
  - Alternative: Ubiquiti Bullet M2/M5

**Long-Range Communication:**
- **LoRa Transceiver Module**
  - RFM95W or SX1276 chipset
  - 915MHz/868MHz frequency
  - Range: 5-15km
  - Low power consumption
  - Purpose: Extended range peer communication

**Backup/High-Bandwidth:**
- **4G/LTE Module**
  - SIM7600G or Quectel EC25 module
  - Requires cellular data plan per drone
  - Purpose: Emergency communication and data upload

#### Drone-Mounted Antenna Requirements
- **Telemetry Antenna:** Quarter-wave whip (915MHz)
- **WiFi Antenna:** Dual-band omnidirectional
- **LoRa Antenna:** 915MHz helical or whip
- **GPS Antenna:** Active GPS/GNSS patch antenna

### 3. Communication Network Topology

#### Layer 1: Ground-to-Air Communication
```
Ground Control Station
    ↕ (SiK Radio 915MHz, 1-5km range)
Individual Drones (UAV1, UAV2, UAV3, UAV4)
```

**Hardware per Link:**
- GCS: 1× SiK Radio + Directional Antenna
- Per Drone: 1× SiK Radio + Omnidirectional Antenna
- **Total Cost:** ~$200 per drone + $300 for GCS setup

#### Layer 2: Drone-to-Drone Communication (Fast Bidding)
```
UAV1 ←→ UAV2
 ↕       ↕
UAV4 ←→ UAV3
```

**Hardware per Drone:**
- WiFi Module (ESP32 or Ubiquiti)
- Omnidirectional antenna
- **Range:** 100-500m
- **Latency:** <50ms
- **Total Cost:** ~$100 per drone

#### Layer 3: Extended Range Backup Communication
```
All Drones ←→ LoRa Gateway at GCS
```

**Hardware Requirements:**
- GCS: LoRa Gateway (Dragino LG308)
- Per Drone: LoRa module (RFM95W)
- **Range:** 10-15km
- **Total Cost:** ~$50 per drone + $200 for gateway

## Detailed Hardware Shopping List

### Ground Control Station Components

| Component | Model/Specification | Quantity | Unit Price | Total |
|-----------|-------------------|----------|------------|--------|
| GCS Computer | Intel NUC or equivalent | 1 | $800 | $800 |
| SiK Telemetry Radio | 3DR Radio V2 (915MHz) | 1 | $75 | $75 |
| LoRa Gateway | Dragino LG308 | 1 | $200 | $200 |
| Directional Antenna | 915MHz Yagi (10dBi) | 1 | $50 | $50 |
| Antenna Rotator | G-5500 or similar | 1 | $400 | $400 |
| 4G/5G Modem | Huawei E3372 | 1 | $50 | $50 |
| Cables & Connectors | Various RF cables | 1 set | $100 | $100 |
| **GCS Subtotal** |  |  |  | **$1,675** |

### Per-Drone Communication Components

| Component | Model/Specification | Quantity | Unit Price | Total |
|-----------|-------------------|----------|------------|--------|
| SiK Telemetry Radio | 3DR Radio V2 (915MHz) | 1 | $75 | $75 |
| WiFi Module | ESP32 DevKit | 1 | $25 | $25 |
| LoRa Module | RFM95W breakout | 1 | $20 | $20 |
| 4G Module (Optional) | SIM7600G | 1 | $80 | $80 |
| Telemetry Antenna | 915MHz whip | 1 | $15 | $15 |
| WiFi Antenna | 2.4GHz/5GHz dual | 1 | $20 | $20 |
| LoRa Antenna | 915MHz helical | 1 | $10 | $10 |
| Integration Board | Custom PCB | 1 | $50 | $50 |
| **Per-Drone Subtotal** |  |  |  | **$295** |

### 4-Drone Fleet Total Cost

| Item | Cost |
|------|------|
| Ground Control Station | $1,675 |
| 4× Drone Communication | $1,180 |
| **Total Communication Hardware** | **$2,855** |

*Note: Prices are estimates and may vary by supplier and region*

## Communication Protocol Mapping

### Current (Simulation) → Real-World Translation

| Current Method | Real-World Implementation | Hardware Required |
|----------------|-------------------------|-------------------|
| Local UDP Multicast (Peer Heartbeat) | LoRa broadcast network | LoRa modules + Gateway |
| Local UDP Multicast (Task Distribution) | SiK Radio + WiFi hybrid | SiK radios + WiFi modules |
| Local UDP P2P (Bidding) | WiFi direct connections | ESP32 modules |
| MAVSDK gRPC (Flight Control) | SiK telemetry radio | 3DR Radio V2 |

## Network Configuration Requirements

### Frequency Allocation
- **915MHz Band:** SiK telemetry radios
- **2.4GHz Band:** WiFi peer-to-peer
- **5GHz Band:** WiFi backup channel
- **Cellular Band:** 4G/LTE modules

### Software Configuration Changes Required

#### 1. Replace UDP Multicast with LoRa
```python
# Current
PEER_MCAST_GRP = "239.255.0.1"
PEER_MCAST_PORT = 30001

# Real-world replacement
LORA_FREQUENCY = 915000000  # 915MHz
LORA_SPREADING_FACTOR = 7
LORA_BANDWIDTH = 125000
```

#### 2. Replace Local P2P with WiFi Direct
```python
# Current
bid_tx.sendto(msg_bytes, ("127.0.0.1", port))

# Real-world replacement
wifi_direct.send_to_peer(drone_ip, msg_bytes)
```

#### 3. Add Communication Redundancy
```python
async def send_with_fallback(message, target):
    try:
        return await send_via_wifi(message, target)
    except:
        try:
            return await send_via_lora(message, target)
        except:
            return await send_via_cellular(message, target)
```

## Range and Performance Specifications

### Communication Range Comparison

| Method | Typical Range | Data Rate | Latency | Power Usage |
|--------|--------------|-----------|---------|-------------|
| SiK Radio | 1-5km | 57.6 kbps | 50-100ms | Medium |
| WiFi Direct | 100-500m | 54 Mbps | 10-20ms | High |
| LoRa | 5-15km | 0.3-50 kbps | 200-500ms | Very Low |
| 4G/LTE | Unlimited* | 1-100 Mbps | 100-300ms | High |

*Cellular range depends on tower coverage

### Expected Performance in Field Operations
- **Peer Discovery:** 2-5 seconds (LoRa heartbeat)
- **Task Distribution:** 1-3 seconds (SiK radio)
- **Competitive Bidding:** 500ms-2 seconds (WiFi direct)
- **Mission Execution:** Real-time (SiK telemetry)

## Regulatory Considerations

### Frequency Licensing Requirements
- **915MHz ISM Band:** License-free in most regions
- **2.4GHz/5GHz:** WiFi certified equipment required
- **Cellular Bands:** Requires data plan and carrier agreement

### Aviation Regulations
- **FAA Part 107 (US):** Commercial drone operation certification
- **CASA (Australia):** ReOC (Remote Operator Certificate)
- **Radio Equipment:** Must meet local EMC standards

## Deployment Phases

### Phase 1: Laboratory Testing (Current)
- ✅ Simulated UDP communication
- ✅ MAVSDK integration
- ✅ Competitive bidding logic

### Phase 2: Hardware Integration
- Purchase and integrate communication modules
- Develop hardware abstraction layer
- Ground testing with real radios

### Phase 3: Field Trials
- Short-range testing (100m)
- Extended range validation (1-5km)
- Multi-drone coordination tests

### Phase 4: Operational Deployment
- Full-scale mission testing
- Emergency procedure validation
- Performance optimization

## Risk Assessment and Mitigation

### Communication Risks
1. **RF Interference:** Use frequency hopping, multiple bands
2. **Range Limitations:** Deploy repeater stations if needed
3. **Hardware Failure:** Redundant communication paths
4. **Latency Issues:** Optimize protocols, reduce message size

### Recommended Mitigations
- **Multiple Communication Channels:** Never rely on single method
- **Local Processing:** Reduce dependence on real-time communication
- **Emergency Protocols:** Autonomous return-to-home capabilities
- **Regular Testing:** Validate communication range before missions

## Conclusion

The transition from simulation to real-world deployment requires significant investment in communication hardware (~$2,855 for 4-drone fleet) but provides a robust, scalable foundation for autonomous multi-UAV operations. The three-layer communication architecture ensures redundancy and optimizes performance for different operational requirements.

The system is designed to scale from 4 drones to larger fleets by simply adding communication modules per drone and expanding the ground station capabilities.

---

**Document Version:** 1.0  
**Date:** November 2025  
**Next Review:** Before hardware procurement
