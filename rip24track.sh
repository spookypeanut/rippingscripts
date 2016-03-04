#!/bin/bash

if [ $# -lt 2 ]
then
	echo "Usage: $0 <track_number> <filename> [<dvd_device>]" >&2
	exit 1
fi

HBEXT="mp4"

if [ "$2" == "${2%%$HBEXT}" ]
then
    HBOUTPATH="$(echo $2.$HBEXT | sed 's/:/-/g')"
else
    HBOUTPATH="$(echo $2 | sed 's/:/-/g')"
fi
HBSUBPATH="${HBOUTPATH%%.$HBEXT}.Forced.srt"
if [ -f $HBOUTPATH ]
then
    echo "About to delete $HBOUTPATH: press ctrl-c to abort"
    read  DISCARDED
    rm -v $HBOUTPATH
fi

echo "Ripping tack $1 to '$HBOUTPATH'"

START=$(date +%s)
echo "Ripping mpg"
MPGRIP=tmprip.mpg
mplayer -dumpstream dvd://$1 -nocache -dvd-device /dev/dvd -dumpfile $MPGRIP
echo "Rip file is $MPGRIP"
END=$(date +%s)
RIPTIME=$(($END - $START))

SRC=25
DEST=24
START=$(date +%s)
echo "Getting subtitles"
TMPSUBS="chosen-sub"
rm -v $TMPSUBS
find-subs $MPGRIP $TMPSUBS
if [ ! -f $TMPSUBS ]; then
    SUBTITLEFILTER=
else
    echo "Found subtitles to use"
    SUBDIR="tempsubdir"
    mkdir -p $SUBDIR
    PGMBASE=$SUBDIR/$TMPSUBS 
    subtitle2pgm -o $PGMBASE -c 255,0,255,255 < $TMPSUBS
    pgm2txt $PGMBASE
    srttool -s -w < ${PGMBASE}.srtx > ${PGMBASE}.srt
    cat ${PGMBASE}.srt | rescale_srt > $HBSUBPATH
fi
END=$(date +%s)
SUBTIME=$(($END - $START))

START=$(date +%s)
FILTERS="[0:v]setpts=($SRC/$DEST)*PTS[v];[0:a]atempo=($DEST/$SRC)[a]" 
ffmpeg -i $MPGRIP -crf 21 -r $DEST -vcodec h264 -preset faster -acodec aac -strict -2 -filter_complex "$FILTERS" -map "[v]" -map "[a]" "$HBOUTPATH"
END=$(date +%s)
echo "Rip took ${RIPTIME}s"
echo "Subtitles took ${SUBTIME}s"
echo "Compress took $(($END - $START))s"
echo "\nFilm file is '$HBOUTPATH'"
if [ -f $HBSUBPATH ]; then
    echo "Subtitles are in '$HBSUBPATH'"
fi
