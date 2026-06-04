import pyaudiowpatch as pyaudio
import websocket # Berasal dari websocket-client
import time
import queue

# 1. Buka koneksi ke server FastAPI di WSL
# URL ini harus sama dengan route yang ada di FastAPI
WS_URL = "ws://localhost:9099/ws/audio"
ws = websocket.WebSocket()

try:
    ws.connect(WS_URL)
    print(f"Berhasil terhubung ke {WS_URL}")
except Exception as e:
    print(f"Gagal terhubung ke server: {e}")
    exit(1)

p = pyaudio.PyAudio()

# Cari perangkat WASAPI Default (Speaker)
wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

# Temukan perangkat loopback yang sesuai
if not default_speakers.get("isLoopbackDevice", False):
    for loopback in p.get_loopback_device_info_generator():
        if default_speakers["name"] in loopback["name"]:
            default_speakers = loopback
            break
    else:
        print("Gagal menemukan perangkat loopback WASAPI default.")
        p.terminate()
        ws.close()
        exit(1)

# Queue untuk menampung data audio secara thread-safe
audio_queue = queue.Queue()

# 2. Fungsi callback untuk menerima data audio dari driver
def callback(in_data, frame_count, time_info, status):
    # Masukkan data audio mentah ke queue, jangan lakukan I/O di sini
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

# 3. Buka stream audio
stream = p.open(
    format=pyaudio.paInt16,
    channels=default_speakers["maxInputChannels"],
    rate=int(default_speakers["defaultSampleRate"]),
    frames_per_buffer=1024,
    input=True,
    input_device_index=default_speakers["index"],
    stream_callback=callback
)

print("Mulai menangkap audio rapat. Tekan Ctrl+C untuk berhenti.")
stream.start_stream()

try:
    while stream.is_active():
        try:
            # Ambil data dari queue dengan timeout agar loop tetap sensitif terhadap KeyboardInterrupt
            data = audio_queue.get(timeout=0.1)
            ws.send_binary(data)
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Koneksi terputus atau error: {e}")
            break
except KeyboardInterrupt:
    print("\nMenghentikan perekaman...")
finally:
    # Pastikan pembersihan dilakukan secara aman
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
        
    print("Selesai.")