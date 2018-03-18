#!/usr/bin/env python
from argparse import ArgumentParser
from rip import rip_track, add_handbrake_flags, get_handbrake_flags


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("tracknum")
    parser.add_argument("filename")
    msg = "The dvd device to use"
    parser.add_argument("--device", help=msg)
    msg = "Only rip this chapter of the track"
    parser.add_argument("--chapter", help=msg)
    parser = add_handbrake_flags(parser)
    return parser.parse_args()


def warning(msg):
    with_warning = "WARNING: %s" % msg
    print("*" * len(with_warning))
    print(with_warning)
    print("*" * len(with_warning))


def main():
    args = parse_args()
    hbflags = get_handbrake_flags(args)

    rip_track(args.filename, track_num=args.tracknum, device=args.device,
              chapter=args.chapter, handbrake_flags=hbflags)

if __name__ == "__main__":
    main()
