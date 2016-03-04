#!/bin/bash
# Copied from https://gist.github.com/tacofumi/3041eac2f59da7a775c6
echo $(date)

echo ">>>Disk found"
echo ">>>Setting the title..."

title=$(makemkvcon -r info)
title=`echo "$title" | grep "DRV:0\+"`
title=${title:53}
len=${#title}-12
title=${title:0:$len}

if [[ -z $title ]]; then
    echo ">>>Couldn't set the title - No disk found"
    echo ">>>Exit->"
    exit;
else
    echo ">>>Title set: $title"
    echo ">>>Starting ripping..."

    makemkvcon --minlength=4800 -r --decrypt --directio=true --progress=-same mkv disc:0 all $HOME/tmp/video

    mv "./*.mkv" "$title.mkv"

    echo ">>>title: $title.mkv created."
fi
