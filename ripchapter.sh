#!/bin/bash
HBDVDDEV="/dev/dvd"
HBEXT="m4v"
HBCODEC="x264"
HBAUDIOBITRATE="160"
HBVIDEOQUALITY="22"
HBSUBTITLEFLAGS="--subtitle scan"
HBCODECFLAGS="-x ref=1:weightp=1:subq=2:rc-lookahead=10:trellis=0:8x8dct=0"

if [ $# -lt 2 ]
then
	echo "Usage: $0 <track_number> <chapter_number> <filename> [<dvd_device>]" >&2
	exit 1
fi

HBTRACK=$1
HBCHAPTER=$2

if [ "$3" == "${3%%$HBEXT}" ]
then
    HBOUTPATH="$3.$HBEXT"
else
    HBOUTPATH="$3"
fi

if [ "$4" != "" ]
then
	HBDVDDEV=$4
fi
echo "Using DVD device $HBDVDDEV"

echo "Current settings: copy video and audio"
echo -n "Time now: " >&2
date >&2
HBCMD="HandBrakeCLI -i $HBDVDDEV -t $HBTRACK -c $HBCHAPTER -o \"$HBOUTPATH\" $HBSUBTITLEFLAGS -e $HBCODEC -q $HBVIDEOQUALITY -B $HBAUDIOBITRATE $HBCODECFLAGS"
echo "Running $HBCMD ..."
eval $HBCMD
echo -n "Time now: " >&2
date >&2
