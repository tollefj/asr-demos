from pydub import AudioSegment
import os

def split_audio(input_file, output_dir, segment_length_ms=30000, overlap_ms=1000, max_segments=None):
    audio = AudioSegment.from_mp3(input_file)
    
    segment_number = 1
    start_time = 0

    if not max_segments:
        max_segments = 999999
    
    while start_time < len(audio):
        segment = audio[start_time:start_time + segment_length_ms]
        
        output_file = f"{output_dir}/segment_{segment_number}.mp3"
        segment.export(output_file, format="mp3")
        
        start_time += segment_length_ms - overlap_ms
        segment_number += 1
        print(segment_number)
        if segment_number > max_segments:
            break

if __name__ == "__main__":
    input_file = "../mp3s/harstad/kommunestyremote2020.mp3"
    output_dir = "../mp3s-split/harstad/kommunestyremote2020"
    os.makedirs(output_dir, exist_ok=True)
    split_audio(input_file, output_dir)