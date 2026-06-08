import asyncio
import websockets
import json
import wave

async def send_audio(websocket, wav_path):
    print(f"Opening file {wav_path}...")
    with wave.open(wav_path, 'rb') as wav_file:
        params = wav_file.getparams()
        print(f"Audio Format: {params.nchannels} channel, {params.sampwidth} bytes/sample, {params.framerate}Hz")
        
        # Send data per chunk (4096 frames = 8192 bytes = 256ms audio)
        chunk_size = 4096
        
        print("Started sending audio stream data...")
        while True:
            data = wav_file.readframes(chunk_size)
            if not data:
                break
            
            # Send binary PCM data to websocket
            await websocket.send(data)
            
            # Simulate real-time sending by adding a 250ms delay
            await asyncio.sleep(0.25)
            
        print("Audio data transmission finished. Waiting for remaining responses from server...")
        await asyncio.sleep(18.0)

async def receive_responses(websocket):
    try:
        async for message in websocket:
            try:
                payload = json.loads(message)
                print("\n==========================================")
                print(f"🗣️  [Mandarin STT]   : {payload.get('zh')}")
                print(f"🇮🇩  [ID Translation]  : {payload.get('id')}")
                print("==========================================")
            except json.JSONDecodeError:
                print(f"Non-JSON message received: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed.")
    except asyncio.CancelledError:
        pass

async def main():
    uri = "ws://127.0.0.1:9099/ws/audio"
    wav_path = "dummy_chinese.wav"
    
    print(f"Attempting to connect to server at {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to WebSocket server!")
            
            # Run sender and receiver concurrently
            send_task = asyncio.create_task(send_audio(websocket, wav_path))
            receive_task = asyncio.create_task(receive_responses(websocket))
            
            # Run until transmission is complete
            await send_task
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            print("Self-test finished.")
    except Exception as e:
        print(f"An error occurred during testing: {e}")

if __name__ == "__main__":
    asyncio.run(main())
