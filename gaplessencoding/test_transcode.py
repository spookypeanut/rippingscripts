from subprocess import check_call
from time import time

INPUT_FILES = ["test_boo.flac", "test_flick.flac", "test_sale.flac",
               "test_polv.flac"]
BITRATE = "192"
# vorbis, aac, lame, ac3
CMDBASE = "ffmpeg -i '%s' -map 0:0 -v 0"
COMMAND_TEMPLATES = {
    "default": (CMDBASE + " -b:a %bk -f mp3 -", "mp3"),
    "aac_std": (CMDBASE + " -b:a %bk -f adts -", "aac"),
    "vorbis_std": (CMDBASE + " -c:a libvorbis -b:a %bk -f ogg -", "ogg"),
    "vorbis_var": (CMDBASE + " -c:a libvorbis -q:a 4 -f ogg -", "ogg"),
    "oggenc": ("oggenc -q3 -o - '%s'", "ogg"),
    "opusenc": ("opusenc '%s' -", "opus")
}
PLAYBACK_CMD = "audacious"


def flac_segment(input_file, start, duration=1):
    output_file = input_file.replace(".flac", ".%s.flac" % start)
    cmd = ["sox", input_file, output_file, "trim", str(start), str(duration)]
    check_call(cmd)
    return output_file


def split_flac(input_file):
    outputs = []
    for start in range(9):
        outputs.append(flac_segment(input_file, start))
    return outputs


def main():
    output = []
    times = {}
    for input_file in INPUT_FILES:
        split_input = split_flac(input_file)
        output.append("%s %s" % (PLAYBACK_CMD, " ".join(split_input)))
        for name, (cmd, ext) in COMMAND_TEMPLATES.items():
            times[name] = 0
            split_out = []
            for eachsplit in split_input:
                outfile = eachsplit.replace(".flac", ".%s.%s" % (name, ext))
                split_out.append(outfile)
                runcmd = cmd.replace("%s", eachsplit)
                runcmd = runcmd.replace("%b", BITRATE)
                runcmd += "> %s" % outfile
                start = time()
                check_call(runcmd, shell=True)
                times[name] += time() - start
            output.append("%s %s" % (PLAYBACK_CMD, " ".join(split_out)))
    for eachline in output:
        print(eachline)
    for name, duration in sorted(times.items(), key=lambda x: x[1]):
        print("%12s: %.3f" % (name, duration))


if __name__ == "__main__":
    main()
