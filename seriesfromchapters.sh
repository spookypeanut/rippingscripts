#!/bin/bash
HBDVDDEV="/dev/dvd"
HBRIPLOG="./rip.log"

if [ "$1" == "" ]
then
    HBTRACKINFO=$(lsdvd $HBDVDDEV | awk -f ~/rippingscripts/serieschaptersfind.awk)
else 
    HBTRACKINFO="$@"
fi
HBTRACKNUM=$(echo $HBTRACKINFO | sed 's/[[:space:]].*//')
HBEPISODES=$(echo $HBTRACKINFO | sed 's/.*[[:space:]]//')

echo "Series looks like $HBEPISODES episodes (in track $HBTRACKNUM)"
echo "Enter program name:"
read HBPROGRAM
echo "Enter series number (blank for none):"
read HBSERIES

echo "What number to start at? [1]"
read HBSTARTING

if [ "$HBSERIES" == "" ]
then
    HBBASE="$HBPROGRAM"
else
    HBBASE="$HBPROGRAM/Series $HBSERIES"
fi

if [ "$HBSTARTING" == "" ]
then
    HBSTARTING=1
fi
j=$HBSTARTING

echo "Ripping $HBEPISODES episodes (track $HBTRACKNUM) starting at $j"
mkdir -p "$HBBASE"
cd "$HBBASE"
echo "Series: $HBBASE, Chapters from track number: $HBTRACKNUM" > $HBRIPLOG

for i in $(seq $HBEPISODES)
do
    HBOUT="./$HBPROGRAM.s$(printf "%02d" $HBSERIES)e$(printf "%02d" $j)"
    echo "Track number: $HBTRACKNUM, chapter number: $i"
    echo "********************************************************"
    echo "Ripping chapter $i from track $HBTRACKNUM to file $HBOUT"
    echo "********************************************************"
    CMD="riptrack.py $HBTRACKNUM \"$HBOUT\" --chapter $i --device $HBDVDDEV | tee -a $HBRIPLOG"
    echo "Running: $CMD"
    #eval $CMD
    j=$(($j+1))
done
echo "Finished ripping to $HBBASE ($HBEPISODES episodes)"

#eject $HBDVDDEV
