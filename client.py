import pyaudiowpatch as pyaudio
import websocket # From websocket-client
import time
import queue

# 1. Open connection to FastAPI server in WSL
# This URL must match the route in FastAPI
WS_URL = "ws://localhost:9099/ws/audio"
ws = websocket.WebSocket()

try:
    ws.connect(WS_URL)
    print(f"Successfully connected to {WS_URL}")
except Exception as e:
    print(f"Failed to connect to server: {e}")
    exit(1)

p = pyaudio.PyAudio()

# Search for Default WASAPI device (Speaker)
wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

# Find the appropriate loopback device
if not default_speakers.get("isLoopbackDevice", False):
    for loopback in p.get_loopback_device_info_generator():
        if default_speakers["name"] in loopback["name"]:
            default_speakers = loopback
            break
    else:
        print("Failed to find default WASAPI loopback device.")
        p.terminate()
        ws.close()
        exit(1)

# Queue to hold audio data in a thread-safe manner
audio_queue = queue.Queue()

# 2. Callback function to receive audio data from the driver
def callback(in_data, frame_count, time_info, status):
    # Put raw audio data into the queue, do not perform I/O here
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

# 3. Open audio stream
stream = p.open(
    format=pyaudio.paInt16,
    channels=default_speakers["maxInputChannels"],
    rate=int(default_speakers["defaultSampleRate"]),
    frames_per_buffer=1024,
    input=True,
    input_device_index=default_speakers["index"],
    stream_callback=callback
)

print("Start capturing meeting audio. Press Ctrl+C to stop.")
stream.start_stream()

try:
    while stream.is_active():
        try:
            # Get data from the queue with a timeout so the loop remains sensitive to KeyboardInterrupt
            data = audio_queue.get(timeout=0.1)
            ws.send_binary(data)
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Connection lost or error: {e}")
            break
except KeyboardInterrupt:
    print("\nStopping recording...")
finally:
    # Ensure clean-up is done safely
    try:
        if stream.is_active():
            stream.stop_stream()
    except Exception:
        pass
    
    try:
        stream.close()
    except Exception:
        pass
        
    p.terminate()
    
    try:
        ws.close()
    except Exception:
        pass
        
    print("Finished.")