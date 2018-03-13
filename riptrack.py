#!/usr/bin/env python
from argparse import ArgumentParser
from rip import rip_track, get_subtitle_flags


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

    rip_track(args.filename, track_num=args.tracknum, device=args.device,
              chapter=args.chapter, animation=args.animation,
              decomb=args.decomb, deinterlace=args.deinterlace,
              subtitleflags=get_subtitle_flags())

if __name__ == "__main__":
    main()
