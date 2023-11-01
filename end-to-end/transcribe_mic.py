import pyaudio
import wave 
from argparse import ArgumentParser
from transformers import pipeline
from pydub import AudioSegment
from util import make_timestamp
from rich import print

FORMAT = pyaudio.paInt16 # data type formate
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def record(filename="tmp.wav", seconds=10):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-s", "--seconds", type=int, help="Seconds per recording, up to 30 seconds, defaults to 10", default=10)
    argparser.add_argument("-m", "--model", type=str, help="Model type (superfast (151MB)/fast (290MB)/normal (967MB)/slow(3.06GB)). Slow is more precise.", default="normal")
    argparser.add_argument("-o", "--output", type=str, help="Output SRT file. Defaults to 'output.srt'", default="output.srt")

    args = argparser.parse_args()

    model_size = {
        "superfast": "tiny",
        "fast": "base",
        "normal": "small",
        "slow": "medium",
    }
    model_id = f"NbAiLab/nb-whisper-{model_size[args.model]}-beta"
    print(f"[yellow]Loading model {model_id}[/yellow]")
    asr = pipeline("automatic-speech-recognition", model_id)
    print(f"[yellow]Transcribing segments to {args.output}[/yellow]")
    
    counter = 1
    total_time = 0
    wave_file = "tmp.wav"

    recording = True
    with open(args.output, "w", encoding="utf-8") as srt_file:
        while recording:
            print("Snakk!!! (si 'stopp' for å avbryte)")
            record(seconds=args.seconds)
            print("transkriberer")
            audio = AudioSegment.from_file(wave_file)
            kwargs = {"task": "transcribe", "language": "no"}
            res = asr(wave_file, generate_kwargs=kwargs, return_timestamps=True)
            chunks = res["chunks"]
            timestamps = [c["timestamp"] for c in chunks]
            text = [c["text"] for c in chunks]
            for (start, end), txt in zip(timestamps, text):
                if "stopp" in txt.lower():
                    recording = False
                    break
                start_time = float(start) * 1000
                end_time = float(end) * 1000
                txt = txt.strip()
                start_srt = make_timestamp(total_time, start)
                end_srt = make_timestamp(total_time, end)
                srt_entry = f"{counter}\n{start_srt} --> {end_srt}\n{txt}\n"
                srt_file.write(srt_entry)
                print(srt_entry)
                counter += 1
            total_time += args.seconds
            
