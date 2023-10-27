import shutil
import os
from pydub import AudioSegment
from pydub.playback import play
from rich import print
from argparse import ArgumentParser
from transformers import pipeline
from util import make_timestamp


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-f", "--folder", type=str, help="Input folder with segments of mp3, wav, etc.", required=True)
    argparser.add_argument("-s", "--speed", type=str, help="Model speed (superfast (151MB)/fast (290MB)/normal (967MB)/slow(3.06GB)). Slow is more precise.", default="normal")
    argparser.add_argument("-a", "--audio", action="store_true", help="Play audio while transcribing")
    args = argparser.parse_args()
    
    model_size = {
        "superfast": "tiny",
        "fast": "base",
        "normal": "small",
        "slow": "medium",
    }
    model_id = f"NbAiLab/nb-whisper-{model_size[args.speed]}-beta"
    print(f"[yellow]Loading model {model_id}[/yellow]")
    asr = pipeline("automatic-speech-recognition", model_id)
    print(f"[yellow]Transcribing segments...[/yellow]")

    valid_files = [f for f in os.listdir(args.folder) if ".txt" not in f]
    output_id = os.path.split(args.folder)[-1]
    srt_filename = output_id + ".srt"
    print(f"[yellow]Writing output to {srt_filename}[/yellow]")
    print(output_id)
    counter = 1
    total_time = 0

    with open(srt_filename, "w", encoding="utf-8") as srt_file:
        for sample in sorted(valid_files, key=lambda x: int(x.split("out")[-1].split(".")[0])):
            fpath = os.path.join(args.folder, sample)
            audio = AudioSegment.from_file(fpath)
            kwargs = {"task": "transcribe", "language": "no"}
            res = asr(fpath, generate_kwargs=kwargs, return_timestamps=True)
            chunks = res["chunks"]
            timestamps = [c["timestamp"] for c in chunks]
            text = [c["text"] for c in chunks]

            for (start, end), txt in zip(timestamps, text):
                start_time = float(start) * 1000
                end_time = float(end) * 1000
                txt = txt.strip()
                start_srt = make_timestamp(total_time, start)
                end_srt = make_timestamp(total_time, end)
                srt_entry = f"{counter}\n{start_srt} --> {end_srt}\n{txt}\n"
                srt_file.write(srt_entry)
                if args.audio:
                    print(srt_entry)
                    play(audio[start_time:end_time])
                counter += 1
            total_time += 30
    
    
    