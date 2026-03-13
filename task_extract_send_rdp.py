#!/usr/bin/env python3
"""
RDP-Compatible Voice Input for Drone Task System
Uses external audio tools instead of PyAudio to work in remote desktop environments
"""

import json
import socket
import os
import sys
import subprocess
import tempfile
import time
from datetime import datetime
import re
import math
import webbrowser
from typing import Optional

try:
    import sounddevice as sd
    import soundfile as sf
    HAS_PY_AUDIO_BACKEND = True
except Exception:
    HAS_PY_AUDIO_BACKEND = False

def get_timestamp():
    """Get current timestamp for logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def print_with_timestamp(message):
    """Print message with timestamp prefix"""
    print(f"[{get_timestamp()}] {message}")

# Import map visualizers
from map_visualizer import show_mission_on_map, generate_map_with_reference
from map_simple_fallback import show_location_on_google_maps
from geocoding_helper import geocode_location, display_and_confirm_location
from location_handler_unified import process_location_with_offset
try:
    from map_visualizer_enhanced import open_enhanced_map
    from map_visualizer_osm import generate_osm_map_with_reference
    HAS_ENHANCED_MAPS = True
except ImportError:
    HAS_ENHANCED_MAPS = False

from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
import httpx

# Load environment variables from the repo root if present.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
load_dotenv()

class Task(BaseModel):
    task_id: str
    task_type: str
    location: list[float]
    altitude: int
    estimated_duration: str
    weather: str
    terrain: str
    priority: str
    required_drones: int = 1
    search_diameter_m: Optional[int] = None
    search_radius_m: Optional[float] = None
    search_pattern: Optional[str] = None
    partitioning: Optional[str] = None
    lane_spacing_m: Optional[float] = None
    description: str

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print_with_timestamp("❌ Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

print_with_timestamp(f"✅ API key loaded: {api_key[:10]}...")

# Create HTTP client with timeout
http_client = httpx.Client(timeout=60.0)

client = OpenAI(
    api_key=api_key,
    http_client=http_client
)

# Communication setup
TASK_MCAST_GRP = "239.255.0.2"
TASK_MCAST_PORT = 30002
WINDOWS_FFMPEG = "/mnt/c/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"

def check_audio_tools():
    """Check if external audio recording tools are available"""
    tools = []
    
    # Check for parecord (PulseAudio)
    try:
        subprocess.run(['parecord', '--help'], capture_output=True, check=False)
        tools.append(('parecord', 'PulseAudio recording'))
    except FileNotFoundError:
        pass
    
    # Check for arecord (ALSA)
    try:
        subprocess.run(['arecord', '--help'], capture_output=True, check=False)
        tools.append(('arecord', 'ALSA recording'))
    except FileNotFoundError:
        pass

    if HAS_PY_AUDIO_BACKEND:
        tools.append(('sounddevice', 'Python sounddevice recording'))

    if os.path.exists(WINDOWS_FFMPEG):
        tools.append(('windows_ffmpeg', 'Windows ffmpeg microphone recording'))
    
    return tools

def record_audio_external():
    """Record audio using external tools suitable for RDP environments"""
    print_with_timestamp("\n🎤 RDP-Compatible Voice Recording")
    print_with_timestamp("🔴 Recording for 10 seconds...")
    print_with_timestamp("💡 Start speaking clearly now!")
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file.close()
    
    # Try PulseAudio first (works better with RDP)
    try:
        print_with_timestamp("🎙️ Using PulseAudio recording...")
        cmd = [
            'parecord',
            '--format=s16le',
            '--rate=44100', 
            '--channels=1',
            '--device=2',  # RDPSource from diagnostic
            temp_file.name
        ]
        
        # Start recording
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        
        # Record for 10 seconds
        time.sleep(10)
        
        # Stop recording
        process.terminate()
        process.wait()
        
        print_with_timestamp("✅ Recording complete!")
        
    except FileNotFoundError:
        # Fallback to ALSA
        try:
            print_with_timestamp("🎙️ Fallback to ALSA recording...")
            cmd = [
                'arecord',
                '-f', 'cd',
                '-t', 'wav', 
                '-d', '10',
                temp_file.name
            ]
            
            subprocess.run(cmd, check=True)
            print_with_timestamp("✅ Recording complete!")
            
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            if os.path.exists(WINDOWS_FFMPEG):
                try:
                    print_with_timestamp("🎙️ Fallback to Windows ffmpeg recording...")
                    device_probe = subprocess.run(
                        [WINDOWS_FFMPEG, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    device_output = (device_probe.stdout or "") + "\n" + (device_probe.stderr or "")
                    audio_device = None
                    for line in device_output.splitlines():
                        if '(audio)' in line and '"' in line:
                            audio_device = line.split('"')[1]
                            break
                    if not audio_device:
                        raise RuntimeError("No Windows microphone device found")

                    windows_temp = subprocess.check_output(['wslpath', '-w', temp_file.name], text=True).strip()
                    subprocess.run(
                        [
                            WINDOWS_FFMPEG,
                            '-y',
                            '-f', 'dshow',
                            '-i', f'audio={audio_device}',
                            '-t', '10',
                            windows_temp,
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    print_with_timestamp(f"✅ Recorded using Windows microphone: {audio_device}")
                except Exception as windows_audio_error:
                    print_with_timestamp(f"❌ Windows ffmpeg recording failed: {windows_audio_error}")
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    return None
            elif HAS_PY_AUDIO_BACKEND:
                try:
                    print_with_timestamp("🎙️ Fallback to Python sounddevice recording...")
                    duration_s = 10
                    sample_rate = 44100
                    recording = sd.rec(int(duration_s * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
                    sd.wait()
                    sf.write(temp_file.name, recording, sample_rate)
                    print_with_timestamp("✅ Recording complete!")
                except Exception as py_audio_error:
                    print_with_timestamp(f"❌ Recording failed: {py_audio_error}")
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    return None
            else:
                print_with_timestamp(f"❌ Recording failed: {e}")
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                return None
    
    # Check if recording was successful
    if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 1000:
        file_size = os.path.getsize(temp_file.name)
        print_with_timestamp(f"💾 Audio file: {temp_file.name} ({file_size:,} bytes)")
        
        # Quick validation - check if it's a valid WAV file
        try:
            with open(temp_file.name, 'rb') as f:
                header = f.read(12)
                if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    print_with_timestamp("⚠️ Warning: Audio file may be corrupted")
                else:
                    print_with_timestamp("✅ Audio file format validated")
        except Exception:
            print_with_timestamp("⚠️ Warning: Could not validate audio file")
        
        return temp_file.name
    else:
        print_with_timestamp("❌ Recording failed - file too small or missing")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None

def transcribe_audio(audio_file_path):
    """Transcribe audio using OpenAI Whisper API with timeout handling"""
    try:
        print_with_timestamp("🔄 Transcribing audio...")
        print_with_timestamp("⏳ This may take 10-30 seconds depending on audio length...")
        
        # Check file size
        file_size = os.path.getsize(audio_file_path)
        print_with_timestamp(f"📁 Audio file size: {file_size:,} bytes")
        
        # Check if file is too large (OpenAI limit is 25MB)
        if file_size > 25 * 1024 * 1024:
            print_with_timestamp("❌ Audio file too large (>25MB)")
            os.unlink(audio_file_path)
            return None
        
        # Create a client with shorter timeout for transcription
        transcription_client = OpenAI(
            api_key=api_key,
            timeout=120.0  # 2 minute timeout
        )
        
        with open(audio_file_path, "rb") as audio_file:
            # Add progress indicator
            print_with_timestamp("🎯 Sending to Whisper API...")
            
            transcription = transcription_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                response_format="text"  # Use text format for simplicity
            )
        
        print_with_timestamp("✅ Transcription received!")
        
        # Clean up temporary file
        os.unlink(audio_file_path)
        
        result = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        
        if not result:
            print_with_timestamp("⚠️ Empty transcription received")
            return None
            
        return result
        
    except Exception as e:
        error_msg = str(e).lower()
        print_with_timestamp(f"❌ Transcription failed: {e}")
        
        # Provide specific error guidance
        if "timeout" in error_msg:
            print_with_timestamp("🔧 Network timeout - try again or check internet connection")
        elif "rate limit" in error_msg:
            print_with_timestamp("🔧 API rate limit - wait a moment and try again")
        elif "invalid" in error_msg:
            print_with_timestamp("🔧 Audio file invalid - try recording again")
        elif "quota" in error_msg:
            print_with_timestamp("🔧 API quota exceeded - check OpenAI account")
        else:
            print_with_timestamp("🔧 Unknown error - try text input instead")
        
        # Clean up file
        if os.path.exists(audio_file_path):
            os.unlink(audio_file_path)
        return None

def get_user_input():
    """Get input from user - text or RDP-compatible voice"""
    available_tools = check_audio_tools()
    
    print_with_timestamp("\n🎤 Mission Input Options:")
    print_with_timestamp("1. Type your mission description")
    
    if available_tools:
        print_with_timestamp("2. Use voice input (RDP-compatible)")
        print_with_timestamp(f"   Available: {', '.join([desc for _, desc in available_tools])}")
    else:
        print_with_timestamp("2. Voice input (⚠️ audio tools not installed)")
    
    while True:
        try:
            choice = input("\nChoose input method (1 for text, 2 for voice): ").strip()
        except EOFError:
            return None
        
        if choice == "1":
            # Text input
            try:
                mission_text = input("\n🗣️ Describe your mission: ").strip()
            except EOFError:
                return None
            if mission_text:
                return mission_text
            else:
                print_with_timestamp("❌ Please enter a mission description")
                continue
                
        elif choice == "2":
            # Voice input
            if not available_tools:
                print_with_timestamp("❌ No audio recording tools available")
                print_with_timestamp("🔧 Install with: sudo apt-get install pulseaudio-utils alsa-utils")
                print_with_timestamp("💡 Falling back to text input...")
                choice = "1"
                continue
                
            try:
                audio_file = record_audio_external()
                if not audio_file:
                    print_with_timestamp("❌ Recording failed. Please try again or use text input.")
                    continue
                    
                transcribed_text = transcribe_audio(audio_file)
                
                if transcribed_text:
                    print_with_timestamp(f"\n✅ Transcribed: '{transcribed_text}'")
                    
                    # Confirm transcription
                    try:
                        confirm = input("\n✅ Use this transcription? (y/n): ").strip().lower()
                    except EOFError:
                        return None
                    if confirm in ['y', 'yes']:
                        return transcribed_text
                    else:
                        print_with_timestamp("🔄 Let's try again...")
                        continue
                else:
                    print_with_timestamp("❌ Transcription failed. Please try again or use text input.")
                    continue
                    
            except KeyboardInterrupt:
                print_with_timestamp("\n\n👋 Voice input cancelled")
                return None
            except Exception as e:
                print_with_timestamp(f"❌ Voice input error: {e}")
                print_with_timestamp("💡 Falling back to text input...")
                choice = "1"
                continue
        else:
            print_with_timestamp("❌ Invalid choice. Please enter 1 or 2.")

def send_task_multicast(task_data):
    """Send task to swarm via multicast"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        
        message = json.dumps(task_data, indent=2).encode('utf-8')
        sock.sendto(message, (TASK_MCAST_GRP, TASK_MCAST_PORT))
        sock.close()
        
        print_with_timestamp(f"✅ Task sent via multicast to {TASK_MCAST_GRP}:{TASK_MCAST_PORT}")
        return True
        
    except Exception as e:
        print_with_timestamp(f"❌ Multicast failed: {e}")
        return False

def send_task_direct(task_data, ports=[9000, 9003]):
    """Send task directly to specific agent ports (fallback)"""
    success_count = 0
    
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                message = json.dumps(task_data, indent=2).encode('utf-8')
                sock.sendto(message, ("127.0.0.1", port))
                print_with_timestamp(f"✅ Task sent to agent on port {port}")
                success_count += 1
        except Exception as e:
            print_with_timestamp(f"❌ Failed to send to port {port}: {e}")
    
    return success_count > 0

def extract_task_from_prompt(user_prompt):
    """Extract structured task data from natural language prompt using GPT-4, with worldwide location support."""
    try:
        print_with_timestamp("🔄 Extracting task information using AI...")
        print_with_timestamp("⏳ Please wait, this should take 5-15 seconds...")

        # Step 1: Process location (handles both direct and offset locations)
        print_with_timestamp("\n" + "="*70)
        print_with_timestamp("📍 STEP 1: LOCATION EXTRACTION & CONFIRMATION")
        print_with_timestamp("="*70)
        
        location_result = process_location_with_offset(user_prompt)
        
        if not location_result:
            print_with_timestamp("❌ Failed to extract or confirm location")
            return None
        
        # Extract confirmed location data
        confirmed_coords = location_result['coords']
        confirmed_location_name = location_result['name']
        has_offset = location_result['has_offset']
        
        print_with_timestamp(f"\n✅ Location processing complete!")
        print_with_timestamp(f"� Final coordinates: {confirmed_coords[0]:.6f}, {confirmed_coords[1]:.6f}")
        print_with_timestamp(f"🏷️  Location name: {confirmed_location_name}")
        
        if has_offset:
            ref_info = location_result['reference']
            print_with_timestamp(f"🧭 Calculated offset: {ref_info['distance']}m {ref_info['direction']} of {ref_info['name']}")
        
        print_with_timestamp("\n" + "="*70)
        print_with_timestamp("🤖 STEP 2: EXTRACTING MISSION DETAILS WITH AI")
        print_with_timestamp("="*70)
        extraction_client = OpenAI(
            api_key=api_key,
            timeout=30.0
        )
        response = extraction_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Extract task information from the user's mission description. 
                    Fill in reasonable defaults for missing information.
                    
                    Task types: search, search_and_rescue, delivery, survey, inspection
                    Terrain types: flat, mountainous, urban, forest, industrial
                    Priority levels: low, normal, high, emergency
                    Weather: clear, cloudy, light_rain, heavy_rain, fog, storm
                    
                    Generate a unique task_id based on task type and timestamp.
                    Default altitude: 20-40 meters depending on task type.
                    Default duration: Use format "15min", "30min", "45min" (number + "min").
                    Default required_drones: 1.
                    
                    IMPORTANT: The location coordinates have already been extracted and confirmed by the user.
                    Use ONLY the provided coordinates - do NOT try to extract or calculate location coordinates yourself.
                    
                    Focus on extracting:
                    - Task type
                    - Task description
                    - Altitude (if specified)
                    - Duration estimate
                    - Weather conditions
                    - Terrain type
                    - Priority level
                    - Required drone count
                    - Search area diameter if the user explicitly gives one
                    - Search coverage pattern if explicitly stated
                    
                    If the user says things like "by two drones", "with 3 drones", or "using four UAVs",
                    set required_drones to that number. Otherwise set it to 1.

                    For search tasks:
                    - Default search_diameter_m to 300 if the user does not specify a size
                    - Default search_pattern to "lawnmower"
                    - Default partitioning to "voronoi"
                    - Default lane_spacing_m to 30
                    
                    For coordinates, if the user says "negative" interpret as minus sign.
                    Example: "negative thirty-five point three six three" = -35.363"""
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format=Task
        )
        task = response.choices[0].message.parsed

        # Override task location with our confirmed geocoded coordinates
        if task:
            task.location = confirmed_coords
            task.required_drones = max(1, int(task.required_drones or 1))
            if str(task.task_type).lower() == "search":
                search_diameter_m = int(float(task.search_diameter_m or 300))
                task.search_diameter_m = max(200, search_diameter_m)
                task.search_radius_m = task.search_diameter_m / 2.0
                task.search_pattern = task.search_pattern or "lawnmower"
                task.partitioning = task.partitioning or "voronoi"
                task.lane_spacing_m = max(20.0, float(task.lane_spacing_m or 30.0))
            # Store the location name for display
            task._location_name = confirmed_location_name
            print_with_timestamp(f"✅ Using confirmed location: {confirmed_location_name}")
            print_with_timestamp(f"� Final coordinates: {confirmed_coords[0]:.6f}, {confirmed_coords[1]:.6f}")

        print_with_timestamp("✅ Task extraction completed!")
        return task

    except Exception as e:
        error_msg = str(e).lower()
        print_with_timestamp(f"❌ Task extraction failed: {e}")
        
        # Provide specific guidance
        if "timeout" in error_msg:
            print_with_timestamp("🔧 Network timeout - try restarting the script or check internet")
        elif "rate limit" in error_msg:
            print_with_timestamp("🔧 API rate limit - wait 1 minute and try again")
        elif "quota" in error_msg:
            print_with_timestamp("🔧 API quota exceeded - check OpenAI account")
        elif "connection" in error_msg:
            print_with_timestamp("🔧 Connection error - check internet or try restarting")
        else:
            print_with_timestamp("🔧 Try restarting the script or your computer if this persists")
            
        return None

def display_extracted_task(task):
    """Display the extracted task in a formatted way, including location name and offset if available"""
    print_with_timestamp("\n" + "="*60)
    print_with_timestamp("🎯 EXTRACTED MISSION TASK")
    print_with_timestamp("="*60)
    print_with_timestamp(f"📋 Task ID: {task.task_id}")
    print_with_timestamp(f"🎪 Type: {task.task_type}")
    
    # Use stored location name if available
    loc_name = getattr(task, '_location_name', None)
    
    # Determine location name based on coordinates or use stored name
    if not loc_name:
        location_names = {
            (-35.36088387, 149.16674193): "Street Gardens",
            (-35.36309804, 149.16348567): "Desert Square",
            (-35.37111574, 149.17183885): "Alexander Center Area",
            (-35.35723482, 149.17015126): "Village Area",
            (-35.35389604, 149.15062472): "Compound Area",
            (-35.363261, 149.165230): "South Sector Area / Default (CMAC)"
        }
        loc = tuple(round(float(x), 6) for x in (task.location[:2] if task.location and len(task.location) >= 2 else (None, None)))
        loc_name = location_names.get(loc, "Custom Location")
    if task.location and len(task.location) >= 2:
        print_with_timestamp(f"📍 Location: {task.location[0]:.8f}, {task.location[1]:.8f}")
        print_with_timestamp(f"🏷️ Location Name: {loc_name}")
    else:
        print_with_timestamp(f"📍 Location: {task.location if task.location else 'Not specified'}")
    print_with_timestamp(f"🛫 Altitude: {task.altitude} meters")
    print_with_timestamp(f"⏱️ Duration: {task.estimated_duration}")
    print_with_timestamp(f"🤝 Required Drones: {task.required_drones}")
    if str(task.task_type).lower() == "search":
        print_with_timestamp(f"🔎 Search Diameter: {int(task.search_diameter_m or 300)} meters")
        print_with_timestamp(f"📐 Partitioning: {task.partitioning or 'voronoi'}")
        print_with_timestamp(f"🧭 Coverage: {task.search_pattern or 'lawnmower'}")
        print_with_timestamp(f"↔️ Lane Spacing: {float(task.lane_spacing_m or 30.0):.0f} meters")
    print_with_timestamp(f"🌤️ Weather: {task.weather}")
    print_with_timestamp(f"🏔️ Terrain: {task.terrain}")
    print_with_timestamp(f"🚨 Priority: {task.priority}")
    print_with_timestamp(f"📝 Description: {task.description}")
    print_with_timestamp("="*60)
    
    # Note: Location was already shown and confirmed on Google Maps during extraction
    print_with_timestamp("\n💡 Location was confirmed during extraction phase")

def enforce_default_duration(task):
    """Force the estimated_duration of the task to '3min' regardless of input."""
    task.estimated_duration = '3min'
    return task

def main():
    """Main function for RDP-compatible drone task operator"""
    print_with_timestamp("🤖 AI-Powered Drone Task Operator (RDP-Compatible)")
    print_with_timestamp("="*60)
    print_with_timestamp("Convert natural language (text or voice) to drone missions")
    print_with_timestamp("="*60)
    
    # Check available audio tools
    tools = check_audio_tools()
    if tools:
        print_with_timestamp(f"✅ Audio tools available: {', '.join([desc for _, desc in tools])}")
    else:
        print_with_timestamp("⚠️ No audio tools found - text input only")
    
    try:
        while True:
            print_with_timestamp("\n🎤 Natural Language Task Input")
            print_with_timestamp("-" * 40)
            
            # Get user input (text or voice)
            user_prompt = get_user_input()
            
            if not user_prompt:
                print_with_timestamp("👋 Goodbye!")
                break
            
            # Extract task using AI
            task = extract_task_from_prompt(user_prompt)
            
            if not task:
                print_with_timestamp("❌ Failed to extract task information. Please try again.")
                continue
            
            # Enforce 3 minute duration
            task = enforce_default_duration(task)
            
            # Display extracted task
            display_extracted_task(task)
            
            # Confirm before sending
            sys.stdout.flush()  # Ensure all previous output is displayed
            try:
                send_confirm = input("\n✅ Send this task to drone agents? (y/n): ").strip().lower()
            except EOFError:
                print_with_timestamp("👋 Goodbye!")
                break
            if send_confirm not in ['y', 'yes']:
                print_with_timestamp("❌ Task cancelled")
                continue
            
            # Convert to dictionary for transmission
            task_dict = {
                "task_id": task.task_id,
                "type": task.task_type,
                "location": task.location,
                "altitude": task.altitude,
                "estimated_duration": task.estimated_duration,
                "weather": task.weather,
                "terrain": task.terrain,
                "priority": task.priority,
                "required_drones": task.required_drones,
                "search_diameter_m": task.search_diameter_m,
                "search_radius_m": task.search_radius_m,
                "search_pattern": task.search_pattern,
                "partitioning": task.partitioning,
                "lane_spacing_m": task.lane_spacing_m,
                "description": task.description,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send task to agents
            print_with_timestamp("\n📤 Sending task to drone agents...")
            
            # Try multicast first (new system)
            print_with_timestamp("📡 Attempting multicast delivery (new system)...")
            multicast_success = send_task_multicast(task_dict)
            
            if multicast_success:
                print_with_timestamp("✅ Task sent via multicast to swarm!")
            else:
                # Fallback to direct delivery (old system)
                print_with_timestamp("📡 Attempting direct delivery (legacy system)...")
                direct_success = send_task_direct(task_dict)
                
                if direct_success:
                    print_with_timestamp("✅ Task sent via direct delivery!")
                else:
                    print_with_timestamp("❌ Failed to send task to agents")
                    continue
            
            print_with_timestamp("\n🏆 Mission Status:")
            print_with_timestamp("📊 Monitor agent terminals to see the bidding process")
            print_with_timestamp("🥇 The selected drone(s) will execute the mission")
            print_with_timestamp("📤 Task delivery complete!")
            
            # Continue or exit
            try:
                continue_prompt = input("\n🔄 Send another task? (y/n): ").strip().lower()
            except EOFError:
                print_with_timestamp("👋 Goodbye!")
                break
            if continue_prompt not in ['y', 'yes']:
                print_with_timestamp("👋 Goodbye!")
                break
    
    except Exception as e:
        print_with_timestamp(f"❌ Unexpected error: {e}")
        print_with_timestamp("🔧 Try restarting the script or your computer")
        sys.exit(1)

if __name__ == "__main__":
    main()

