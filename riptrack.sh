#!/bin/bash
HBDVDDEV="/dev/dvd"
HBEXT="m4v"
HBCODEC="x264"
HBAUDIOBITRATE="160"
HBVIDEOQUALITY="21"
HBDEFAULTSUB="--subtitle scan --subtitle-forced scan"
HBSUBTITLEFLAGS=${HBSUBTITLEFLAGS-$HBDEFAULTSUB}
echo "Subtitle flags: $HBSUBTITLEFLAGS"
HBCODECFLAGS="-x ref=1:weightp=1:subq=2:rc-lookahead=10:trellis=0:8x8dct=0"

if [ $# -lt 2 ]
then
	echo "Usage: $0 <track_number> <filename> [<dvd_device>]" >&2
	exit 1
fi

if [ "$2" == "${2%%$HBEXT}" ]
then
    HBOUTPATH="$(echo $2.$HBEXT | sed 's/:/-/g')"
else
    HBOUTPATH="$($2 | sed 's/:/-/g')"
fi

if [ "$3" != "" ]
then
	HBDVDDEV=$3
fi
echo "Using DVD device $HBDVDDEV"

echo "Current settings: copy video and audio"
echo -n "Time now: " >&2
date >&2
HBCMD="HandBrakeCLI -i $HBDVDDEV -t $1 -o \"$HBOUTPATH\" -m $HBSUBTITLEFLAGS -e $HBCODEC -q $HBVIDEOQUALITY -B $HBAUDIOBITRATE $HBCODECFLAGS"
echo "Running $HBCMD ..."
eval $HBCMD
echo -n "Time now: " >&2
date >&2
