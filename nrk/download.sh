#!/bin/bash
if ! command -v youtube-dl &> /dev/null; then
    echo "youtube-dl is not installed. Please install it first."
    exit 1
fi
if [ -z "$1" ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi
URL="$1"
youtube-dl --write-sub --sub-format ttml --convert-subtitles srt --embed-subs "$URL"
