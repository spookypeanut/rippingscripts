#!/usr/bin/env python
import os
from argparse import ArgumentParser
from datetime import datetime
from subprocess import Popen, PIPE, check_call

HBDVDDEV = "/dev/dvd"
HBEXT = ".m4v"
HBCODEC = "x264"
HBAUDIOBITRATE = 160
HBVIDEOQUALITY = 21
DEFAULT_CODEC_FLAGS = {"ref": 1, "weightp": 1, "subq": 2,
                       "rc-lookahead": 10, "trellis": 0, "8x8dct": 0}


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("tracknum")
    parser.add_argument("filename")
    msg = "The dvd device to use"
    parser.add_argument("--device", help=msg)
    msg = "Only rip this chapter of the track"
    parser.add_argument("--chapter", help=msg)
    parser.add_argument("--animation", action="store_true")
    parser.add_argument("--decomb", action="store_true")
    parser.add_argument("--deinterlace", action="store_true")
    return parser.parse_args()


def warning(msg):
    with_warning = "WARNING: %s" % msg
    print("*" * len(with_warning))
    print(with_warning)
    print("*" * len(with_warning))


def main():
    args = parse_args()
    if "HBSUBTITLEFLAGS" in os.environ:
        subtitleflags = os.environ["HBSUBTITLEFLAGS"].split()
    else:
        subtitleflags = ["--subtitle", "scan", "--subtitle-forced", "scan"]
    subtitleflags = ["-m"] + subtitleflags

    print("Subtitle flags: %s" % subtitleflags)
    # Don't think this does anything
    #export DVDCSS_VERBOSE=0

    codecflags = DEFAULT_CODEC_FLAGS
    compiled_flags = ":".join(["%s=%s" % a for a in codecflags.items()])
    codec_args = ["-x", compiled_flags]
    if args.animation is True:
        warning("Using animation tuning")
        codec_args = ["--x264-tune", "animation"] + codec_args

    if args.filename.endswith(HBEXT):
        outpath = args.filename
    else:
        outpath = args.filename + HBEXT

    device = HBDVDDEV
    if args.device is not None:
        device = args.device
    print("Using DVD device %s" % device)

    starttime = datetime.now()
    print("Starting at %s" % starttime)
    HBCMD = ["HandBrakeCLI", "-v0", "-i", device, "-t", str(args.tracknum)]
    if args.chapter is not None:
        HBCMD.extend(["-c", args.chapter])
    HBCMD.extend(["-o", outpath])
    HBCMD.extend(subtitleflags)
    if args.decomb is True:
        warning("Using decomb")
        HBCMD.append("--decomb")
    if args.deinterlace is True:
        warning("Using deinterlace")
        HBCMD.append("--deinterlace")
    HBCMD.extend(["-e", HBCODEC, "-q", str(HBVIDEOQUALITY),
                  "-B", str(HBAUDIOBITRATE)])
    HBCMD.extend(codec_args)
    print("Running %s" % HBCMD)
    p = Popen(HBCMD, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(stderr)
    endtime = datetime.now()
    print("Finished at %s" % endtime)
    print("Took %ss" % (endtime - starttime).seconds)
    try:
        cmd = ["checklength", "--file", outpath, "--track", args.tracknum]
        check_call(cmd)
        print("Length of video file matches length of track")
    except Exception:
        warning("TIMES DO NOT MATCH!")

if __name__ == "__main__":
    main()
