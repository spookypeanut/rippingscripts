from ast import literal_eval
import os
from datetime import datetime
from subprocess import Popen, PIPE
from copy import copy

HBDVDDEV = "/dev/dvd"
HBEXT = ".m4v"
HBCODEC = "x264"
HBAUDIOBITRATE = 160
HBVIDEOQUALITY = 21
DEFAULT_SUBTITLE_FLAGS = ["--subtitle", "scan", "--subtitle-forced", "scan"]
DEFAULT_CODEC_FLAGS = {"ref": 1, "weightp": 1, "subq": 2,
                       "rc-lookahead": 10, "trellis": 0, "8x8dct": 0}
STDERR_DUMP = "/tmp/rip.log"

class RippingError(Exception):
    pass

def get_lsdvd(track_num=None, chapter=False, device=None):
    if device is None:
        device = HBDVDDEV
    cmd = ["lsdvd"]
    if track_num is not None:
        cmd.extend(["-t", str(track_num)])
    if chapter is not False:
        cmd.append("-c")
    cmd.extend(["-Oy", device])
    p = Popen(cmd, stdout=PIPE)
    stdout, stderr = p.communicate()
    return literal_eval(stdout[8:])


def get_track_len(track_num, chapter=None, device=None):
    lsdvd = get_lsdvd(track_num=track_num, chapter=(chapter is not None),
                      device=device)
    trackdict = [t for t in lsdvd["track"] if t["ix"] == int(track_num)][0]
    if chapter is not None:
        cdict = [c for c in trackdict["chapter"] if c["ix"] == int(chapter)][0]
        return cdict["length"]
    return trackdict["length"]


def get_file_len(eachfile):
    cmd = ["ffmpeg", "-i", eachfile]
    p = Popen(cmd, stderr=PIPE)
    stdout, stderr = p.communicate()
    for line in stderr.split("\n"):
        if "Duration" in line:
            break
    else:
        raise RuntimeError
    line = line.strip()
    rawdur = line.split()[1]
    rawdur = rawdur.rstrip(",")
    return time_string_to_seconds(rawdur)


def check_length(filename, track_num, chapter_num=None, device=None):
    track_len = get_track_len(track_num, chapter=chapter_num)
    file_len = get_file_len(filename)
    diff = abs(1.0 * track_len - file_len)
    print("Track: %ss, File: %ss (diff: %ss)" % (track_len, file_len, diff))
    if diff <= 5:
        return True
    return False


def time_string_to_seconds(rawdur):
    rawdur = rawdur.strip(",")
    rawdur, _, milli = rawdur.rpartition(".")
    milli = int(milli)
    rawdur, _, sec = rawdur.rpartition(":")
    sec = int(sec)
    rawdur, _, mins = rawdur.rpartition(":")
    mins = int(mins)
    hours = int(rawdur)
    return (3600 * hours + 60 * mins + sec + (milli / 1000))


def get_subtitle_flags():
    if "HBSUBTITLEFLAGS" in os.environ:
        return os.environ["HBSUBTITLEFLAGS"].split()
    return DEFAULT_SUBTITLE_FLAGS


def warning(msg):
    with_warning = "WARNING: %s" % msg
    print("*" * len(with_warning))
    print(with_warning)
    print("*" * len(with_warning))


def dump_stderr(text):
    with open(STDERR_DUMP, "w") as f:
        f.write(text)
    print("stderr of rip written to %s" % STDERR_DUMP)


def rip_track(filename, track_num=None, device=None, inputfile=None,
              chapter=None, animation=False, decomb=False, deinterlace=False,
              subtitleflags=None):
    codecflags = copy(DEFAULT_CODEC_FLAGS)
    compiled_flags = ":".join(["%s=%s" % a for a in codecflags.items()])
    codec_args = ["-x", compiled_flags]
    if animation is True:
        warning("Using animation tuning")
        codec_args = ["--x264-tune", "animation"] + codec_args

    if filename.endswith(HBEXT):
        outpath = filename
    else:
        outpath = filename + HBEXT

    if device is not None and inputfile is not None:
        raise RippingError("Both device and inputfile specified")
    if device is None:
        if inputfile is None:
            device = HBDVDDEV
        else:
            device = inputfile
    print("Input: %s" % device)

    starttime = datetime.now()
    print("Starting at %s" % starttime)
    HBCMD = ["HandBrakeCLI", "-v0", "-i", device]
    if inputfile is None:
        HBCMD.extend(["-t", str(track_num)])
    if chapter is not None:
        HBCMD.extend(["-c", chapter])
    HBCMD.extend(["-o", outpath, "-m"])
    if subtitleflags is None:
        HBCMD.extend(DEFAULT_SUBTITLE_FLAGS)
    else:
        HBCMD.extend(subtitleflags)
    if decomb is True:
        warning("Using decomb")
        HBCMD.append("--decomb")
    if deinterlace is True:
        warning("Using deinterlace")
        HBCMD.append("--deinterlace")
    HBCMD.extend(["-e", HBCODEC, "-q", str(HBVIDEOQUALITY),
                  "-B", str(HBAUDIOBITRATE)])
    HBCMD.extend(codec_args)
    print("Running %s" % HBCMD)
    p = Popen(HBCMD, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        dump_stderr(stderr)
        msg = "Error occurred while ripping %s to %s" % (track_num, outpath)
        raise RippingError(msg)
    endtime = datetime.now()
    print("Finished at %s" % endtime)
    print("Took %ss" % (endtime - starttime).seconds)
    if inputfile is not None:
        return
    if check_length(outpath, track_num, chapter, device):
        print("Length of video file matches length of track")
    else:
        dump_stderr(stderr)
        msg = "Length of %s doesn't match track %s" % (outpath, track_num)
        raise RippingError(msg)
