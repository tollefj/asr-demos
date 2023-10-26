from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os

def split_audio(input_file, output_dir, segment_length_ms=30000, max_segments=None):
    audio = AudioSegment.from_mp3(input_file)
    print("Audio length:", len(audio))
    # print detailed audio info:
    print(audio)
    
    segment_number = 1
    start_time = 0
    if not max_segments:
        max_segments = 999999
    
    while start_time < len(audio) or segment_number > max_segments:
        segment = audio[start_time:start_time + segment_length_ms]
        silence_ranges = detect_nonsilent(segment, min_silence_len=2000)

        # If there is silence at the end of the segment, extend it to the end of silence
        if silence_ranges and silence_ranges[-1][1] >= len(segment) - 2000:
            segment = segment[:silence_ranges[-1][1]]
            start_time += silence_ranges[-1][1]
        else:
            start_time += segment_length_ms
        
        output_file = f"{output_dir}/segment_{segment_number}.mp3"
        segment.export(output_file, format="mp3")
        segment_number += 1

if __name__ == "__main__":
    _in = "mp3s/harstad/kommunestyremote2020.mp3"  # Replace with your input MP3 file
    _out = "output_segments"  # Output directory where the segmented files will be saved
    # delete the _out dir if it exists
    if os.path.exists(_out):
        for f in os.listdir(_out):
            os.remove(os.path.join(_out, f))

    # Create the output directory if it doesn't exist
    os.makedirs(_out, exist_ok=True)

    split_audio(_in, _out, segment_length_ms=10000, max_segments=10)
