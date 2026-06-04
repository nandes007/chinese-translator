import asyncio
import websockets
import json
import wave

async def send_audio(websocket, wav_path):
    print(f"Membuka file {wav_path}...")
    with wave.open(wav_path, 'rb') as wav_file:
        params = wav_file.getparams()
        print(f"Format Audio: {params.nchannels} channel, {params.sampwidth} bytes/sample, {params.framerate}Hz")
        
        # Kirim data per chunk (4096 frame = 8192 bytes = 256ms audio)
        chunk_size = 4096
        
        print("Mulai mengirimkan data audio stream...")
        while True:
            data = wav_file.readframes(chunk_size)
            if not data:
                break
            
            # Kirim data biner PCM ke websocket
            await websocket.send(data)
            
            # Simulasi pengiriman real-time dengan memberi jeda 250ms
            await asyncio.sleep(0.25)
            
        print("Pengiriman data audio selesai. Menunggu respons sisa dari server...")
        await asyncio.sleep(18.0)

async def receive_responses(websocket):
    try:
        async for message in websocket:
            try:
                payload = json.loads(message)
                print("\n==========================================")
                print(f"🗣️  [Mandarin STT]   : {payload.get('zh')}")
                print(f"🇮🇩  [Terjemahan ID]  : {payload.get('id')}")
                print("==========================================")
            except json.JSONDecodeError:
                print(f"Pesan non-JSON diterima: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Koneksi WebSocket ditutup.")
    except asyncio.CancelledError:
        pass

async def main():
    uri = "ws://127.0.0.1:9000/ws/audio"
    wav_path = "dummy_chinese.wav"
    
    print(f"Mencoba menyambung ke server di {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Berhasil tersambung ke WebSocket server!")
            
            # Jalankan sender dan receiver secara konkuren
            send_task = asyncio.create_task(send_audio(websocket, wav_path))
            receive_task = asyncio.create_task(receive_responses(websocket))
            
            # Jalankan hingga pengiriman selesai
            await send_task
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            print("Pengujian mandiri selesai.")
    except Exception as e:
        print(f"Terjadi kesalahan saat pengujian: {e}")

if __name__ == "__main__":
    asyncio.run(main())
