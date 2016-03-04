function abs(value) {return sqrt(value^2)}
BEGIN {
    FS="[, ]"
    maxminutes=0
    minnum=3
}
{
    if ($1 =="Title:") {
        titlenum=$2*1
        split ($5, time, ":")
        mins=time[2]+60*time[1]
        seconds=time[3]+60*mins
        times[titlenum]=seconds
        # Doctor Who (2005) series 1, disc 4
        # No episodes have same num minutes, so round to nearest 5
        # NB: check this with short things, eg peppa pig
        #numtracksoftime[int(mins/5)*5]++
        numtracksoftime[mins]++

        if (mins>maxminutes) {
            maxminutes=mins
        }
        maxtitle=titlenum
        #printf "DEBUG: track %d, seconds=%d, mins=%d\n", titlenum, seconds, mins
    }
}
END {
    mode=0
    modelength=-1
    for (i=1; i<=maxminutes; i++) {
        if (numtracksoftime[i] > mode) {
            # I think the mode should actually be i. Ho hum.
            mode=numtracksoftime[i]
            modelength=i
        }
    }
    #printf "DEBUG: mode is %d, modelength is %d\n", mode, modelength
    maxvariance=60 + (modelength*60*.15)
    #printf "DEBUG: maxvariance is %d\n", maxvariance
    for (i=1; i<=maxtitle; i++) {
        diff=times[i]-(modelength*60)
        #printf "DEBUG: diff for track %d = %d\n", i, diff
        #printf "DEBUG: times[%d] = %d\n", i, times[i]
        if (abs(diff) < maxvariance) {
            printf "%d ", i
        }
    }
}
