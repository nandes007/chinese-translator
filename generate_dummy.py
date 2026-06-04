import os
import av
from gtts import gTTS

def generate_mandarin_speech(text, output_mp3_path):
    print(f"Membuat text-to-speech untuk: '{text}'...")
    tts = gTTS(text, lang='zh-CN')
    tts.save(output_mp3_path)
    print(f"File MP3 berhasil disimpan ke: {output_mp3_path}")

def convert_mp3_to_wav_16k_mono(mp3_path, wav_path):
    print(f"Mengonversi {mp3_path} ke WAV (16kHz, Mono, PCM 16-bit)...")
    
    # Buka input container (MP3)
    input_container = av.open(mp3_path)
    input_stream = input_container.streams.audio[0]

    # Buka output container (WAV)
    output_container = av.open(wav_path, 'w')
    # Tambahkan audio stream dengan format pcm_s16le, rate 16000Hz
    output_stream = output_container.add_stream('pcm_s16le', rate=16000)
    output_stream.layout = 'mono'

    # Resampler untuk mengubah format input ke s16 (PCM 16-bit), mono, 16000Hz
    resampler = av.AudioResampler(
        format='s16',
        layout='mono',
        rate=16000,
    )

    for packet in input_container.demux(input_stream):
        for frame in packet.decode():
            # Lakukan resample pada frame audio
            resampled_frames = resampler.resample(frame)
            if resampled_frames:
                # Periksa jika resampler mengembalikan list frame
                if isinstance(resampled_frames, list):
                    for r_frame in resampled_frames:
                        for out_packet in output_stream.encode(r_frame):
                            output_container.mux(out_packet)
                else:
                    # Kadang mengembalikan single frame
                    for out_packet in output_stream.encode(resampled_frames):
                        output_container.mux(out_packet)

    # Flush encoder
    for out_packet in output_stream.encode(None):
        output_container.mux(out_packet)

    input_container.close()
    output_container.close()
    print(f"File WAV berhasil disimpan ke: {wav_path}")

if __name__ == "__main__":
    text_mandarin = "你好，欢迎使用实时语音翻译系统。今天的天气非常好，我们来测试一下这个翻译工具。"
    mp3_file = "dummy_chinese.mp3"
    wav_file = "dummy_chinese.wav"
    
    try:
        generate_mandarin_speech(text_mandarin, mp3_file)
        convert_mp3_to_wav_16k_mono(mp3_file, wav_file)
        
        # Hapus file mp3 sementara
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            print("Membersihkan file MP3 sementara.")
            
        print("\n🎉 Sukses! File 'dummy_chinese.wav' siap digunakan untuk pengujian.")
    except Exception as e:
        print(f"Terjadi kesalahan saat pembuatan audio dummy: {e}")
