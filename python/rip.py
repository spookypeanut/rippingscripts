from datetime import datetime
from subprocess import Popen, PIPE, check_call
from copy import copy

HBDVDDEV = "/dev/dvd"
HBEXT = ".m4v"
HBCODEC = "x264"
HBAUDIOBITRATE = 160
HBVIDEOQUALITY = 21
DEFAULT_SUBTITLE_FLAGS = ["--subtitle", "scan", "--subtitle-forced", "scan"]
DEFAULT_CODEC_FLAGS = {"ref": 1, "weightp": 1, "subq": 2,
                       "rc-lookahead": 10, "trellis": 0, "8x8dct": 0}


def warning(msg):
    with_warning = "WARNING: %s" % msg
    print("*" * len(with_warning))
    print(with_warning)
    print("*" * len(with_warning))


def rip_track(track_num, filename, device=None, chapter=None, animation=False,
              decomb=False, deinterlace=False, subtitleflags=None):
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

    if device is None:
        device = HBDVDDEV
    print("Using DVD device %s" % device)

    starttime = datetime.now()
    print("Starting at %s" % starttime)
    HBCMD = ["HandBrakeCLI", "-v0", "-i", device, "-t", str(track_num)]
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
        print(stderr)
    endtime = datetime.now()
    print("Finished at %s" % endtime)
    print("Took %ss" % (endtime - starttime).seconds)
    try:
        cmd = ["checklength", "--file", outpath, "--track", track_num]
        if chapter is not None:
            cmd.extend(["--chapter", chapter])
        print("Checking: %s" % (cmd,))
        check_call(cmd)
        print("Length of video file matches length of track")
    except Exception:
        warning("TIMES DO NOT MATCH!")
