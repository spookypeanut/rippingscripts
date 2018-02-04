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
ENCODECMD="HandBrakeCLI --preset-import-gui -Z frombluray -i \"$INPUT\" -o \"$OUTPUT\""
eval "$ENCODECMD"
