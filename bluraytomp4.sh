#!/bin/bash
INPUT=$(echo "$1"| sed 's@\"@\\\"@g')
if [ $# -lt 2 ]; then
    OUTPUT=$(echo "${INPUT%.*}.mp4" | sed 's@\"@\\\"@g')
    if [ "$INPUT" = "$OUTPUT" ]; then
        OUTPUT=$(echo "${INPUT%.*}.converted.mp4" | sed 's@\"@\\\"@g')
    fi
else
    OUTPUT=$(echo "$2"| sed 's@\"@\\\"@g')
fi
echo "input is $INPUT, output is $OUTPUT"

_HBSUBFLAGS=`python -c 'from rip import get_subtitle_flags; print(" ".join(get_subtitle_flags()))'`
ENCODECMD="HandBrakeCLI --preset-import-gui -Z frombluray $_HBSUBFLAGS -i \"$INPUT\" -o \"$OUTPUT\""
echo "Running: $ENCODECMD"
eval "$ENCODECMD"
