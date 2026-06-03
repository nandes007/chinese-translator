from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging
import numpy as np
from faster_whisper import WhisperModel
import io

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AudioServer")

# 1. Inisialisasi Model STT
# Menggunakan model 'small' untuk keseimbangan kecepatan dan akurasi.
# Jika Anda punya GPU di WSL, ubah device="cuda". Jika tidak, biarkan "cpu".
logger.info("Memuat model AI (ini mungkin memakan waktu sebentar)...")
model = WhisperModel("small", device="cpu", compute_type="int8")
logger.info("Model siap!")

# Parameter Audio
SAMPLE_RATE = 16000
CHANNELS = 2  # VooV/Windows default biasanya stereo. Sesuaikan jika mono (1)
BYTES_PER_SAMPLE = 2
# Hitung target ukuran byte untuk 3 detik audio
TARGET_BUFFER_SIZE = SAMPLE_RATE * CHANNELS * BYTES_PER_SAMPLE * 3 

@app.websocket("/ws/audio")
async def audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Klien Windows terhubung. Mulai mendengarkan...")
    
    audio_buffer = bytearray()
    
    try:
        while True:
            # Terima chunk
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            # Jika buffer sudah mencapai ~3 detik, proses dengan AI
            if len(audio_buffer) >= TARGET_BUFFER_SIZE:
                # Ambil data dari buffer dan kosongkan buffer untuk chunk berikutnya
                process_data = audio_buffer[:TARGET_BUFFER_SIZE]
                audio_buffer = audio_buffer[TARGET_BUFFER_SIZE:]
                
                # 2. Konversi byte mentah (PCM 16-bit) ke Float32 Array untuk Whisper
                audio_np = np.frombuffer(process_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Jika audio stereo, ubah ke mono (karena Whisper hanya menerima mono)
                if CHANNELS == 2:
                    audio_np = audio_np.reshape(-1, 2).mean(axis=1)

                # 3. Jalankan Transkripsi STT
                # Kita set language="zh" agar model fokus mendengarkan bahasa Mandarin
                segments, info = model.transcribe(audio_np, beam_size=5, language="zh")
                
                # Kumpulkan hasil teks
                text_result = "".join([segment.text for segment in segments])
                
                if text_result.strip():
                    logger.info(f"🗣️ Mandarin: {text_result}")
                
    except WebSocketDisconnect:
        logger.info("Klien Windows terputus.")
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}")