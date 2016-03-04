# Prints out the track number of the longest track, and
# how many chapters it has
BEGIN {
    FS="[, ]"
}
{
    if ($1 =="Title:") {
        titlenum=$2*1
        chapters[titlenum]=$7*1
        #print titlenum, chapters[titlenum]
    }
    if ($1 == "Longest") {
        longesttrack=$3*1
    }
}
END {
    print longesttrack, chapters[longesttrack]
}
