from subprocess import check_call

INPUT_FILES = ["test_boo.flac", "test_flick.flac", "test_sale.flac"]
BITRATE = "192"
# vorbis, aac, lame, ac3
COMMAND_TEMPLATES = {
    "default": ("ffmpeg -i '%s' -map 0:0 -b:a %bk -v 0 -f mp3 -", "mp3")
}
PLAYBACK_CMD = "audacious"


def flac_segment(input_file, start, duration=3):
    output_file = input_file.replace(".flac", ".%s.flac" % start)
    cmd = ["sox", input_file, output_file, "trim", str(start), str(duration)]
    check_call(cmd)
    return output_file


def split_flac(input_file):
    outputs = []
    for start in [0, 3, 6]:
        outputs.append(flac_segment(input_file, start))
    return outputs


def main():
    output = []
    for input_file in INPUT_FILES:
        split_input = split_flac(input_file)
        output.append("%s %s" % (PLAYBACK_CMD, " ".join(split_input)))
        for name, (cmd, ext) in COMMAND_TEMPLATES.items():
            split_out = []
            for eachsplit in split_input:
                outfile = eachsplit.replace(".flac", ".%s.%s" % (name, ext))
                split_out.append(outfile)
                runcmd = cmd.replace("%s", eachsplit)
                runcmd = runcmd.replace("%b", BITRATE)
                runcmd += "> %s" % outfile
                check_call(runcmd, shell=True)
            output.append("%s %s" % (PLAYBACK_CMD, " ".join(split_out)))
    for eachline in output:
        print(eachline)


if __name__ == "__main__":
    main()
