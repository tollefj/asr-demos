#!/bin/bash
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is not installed. Please install it first."
    exit 1
fi
if [ -z "$1" ]; then
    echo "Usage: $0 <input_video_file>"
    exit 1
fi
input_file="$1"
output_file="${input_file%.*}.mp3"
ffmpeg -i "$input_file" -vn -acodec libmp3lame -ar 16000 -q:a 2 "$output_file"
echo "Audio extracted and saved as: $output_file"