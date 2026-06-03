from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging

app = FastAPI()

# Konfigurasi logging dasar
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AudioServer")

@app.websocket("/ws/audio")
async def audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Koneksi WebSocket klien (Windows) berhasil terhubung.")
    
    try:
        while True:
            # Menerima raw audio bytes dari klien
            data = await websocket.receive_bytes()
            
            # Di tahap selanjutnya, Anda akan meneruskan 'data' ini ke model AI
            # (Misalnya: dimasukkan ke buffer, atau dikirim ke Kafka/Flink)
            
            logger.info(f"Menerima chunk audio sebesar {len(data)} bytes")
            
    except WebSocketDisconnect:
        logger.info("Klien terputus dari WebSocket.")
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}")