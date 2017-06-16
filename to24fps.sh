#!/bin/bash

if [ $# -lt 1 ]
then
	echo "Usage: $0 <filename>" >&2
	exit 1
fi

SRC=25
DEST=24
START=$(date +%s)
echo "Getting subtitles"
SUBDIR="tempsubdir"
mkdir -p $SUBDIR
TMPSUBS="$SUBDIR/chosen-sub"
rm -v $TMPSUBS

echo "Found subtitles to use"
PGMBASE=$TMPSUBS 
subtitle2pgm -o $PGMBASE -c 255,0,255,255 < $TMPSUBS
pgm2txt $PGMBASE
srttool -s -w < ${PGMBASE}.srtx > ${PGMBASE}.srt
cat ${PGMBASE}.srt | rescale_srt > "$HBSUBPATH"
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
echo -e "\nFilm file is '$HBOUTPATH'"
if [ -f "$HBSUBPATH" ]; then
    echo "Subtitles are in '$HBSUBPATH'"
fi
