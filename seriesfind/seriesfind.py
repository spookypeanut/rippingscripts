import os
from glob import glob
from subprocess import Popen, PIPE

# If two tracks are within this percentage, they could be part of a
# series
LENGTHDIFF = 20

TESTS = {
    "csi_s1_p2_d1": [1, 2, 3, 4], "csi_s1_p2_d2": [1, 2, 3, 4],
    "csi_s1_p2_d3": [1, 2, 3, 4], "csi_s2_p1_d1": [1, 2, 3, 4],
    "csi_s2_p1_d3": [1, 2, 3, 4], "csi_s2_p2_d1": [1, 2, 3, 4],
    "csi_s2_p2_d3": [1, 2, 3], "fatherted_s2_d1": [1, 2, 3, 4, 5],
    "doctorwho_s1_d1": [3, 4, 5], "mightboosh_s2_d1": [2, 3, 4, 5, 6, 7],
    "tomandjerry_v4_s1": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "doctorwho_s1_d4": [7, 8, 9], "doctorwho_s1_d2": [4, 5, 6],
    "csi_s3_p1_d1": [2, 3, 4, 5], "csi_s3_p1_d2": [2, 3, 4, 5],
    "csi_s3_p1_d3": [2, 3, 4, 5], "csi_s3_p2_d1": [2, 3, 4, 5],
    "csi_s3_p2_d2": [4, 5, 6, 7], "csi_s3_p2_d3": [2, 3, 4],
    "csi_s4_p1_d3": [2, 3, 5, 6], "friends_27": [1, 2, 3, 4, 5, 6],
    "clonewars_s1_v3": [2, 3, 4, 5, 6, 7],
    "csi_s7_p1_d2": [3, 4, 6, 7], "buffy_s2_d6": [1, 2],
    "dinnerladies_s1": [2, 3, 4, 5, 6, 7],
    "simpsons_s3_d1": [1, 2, 3, 4, 5, 6],
    "simpsons_s3_d2": [1, 2, 3, 4, 5, 6],
    "simpsons_s3_d3": [1, 2, 3, 4, 5, 6],
    "simpsons_s3_d4": [1, 2, 3, 4, 5, 6],
    "simpsons_s4_d1": [1, 2, 3, 4],
    "simpsons_s4_d3": [1, 2, 3, 4, 5, 6],
    "simpsons_s4_d4": [1, 2, 3, 4, 5, 6],
    "24_s5_d3": [2, 3, 4, 5],
    "withoutatrace_s6_d1_s1": [2, 3, 4, 5],
    "withoutatrace_s6_d1_s2": [2, 3, 4, 5],
    "withoutatrace_s6_d2_s1": [2, 3, 4, 5],
    "withoutatrace_s6_d2_s2": [2, 3, 4, 5],
    "withoutatrace_s6_d3": [2, 3],
    "futurama_s1_d1": [1, 2, 3, 4],
    "futurama_s1_d2": [1, 2, 3, 4, 5]
}


EXPECTED_ERRORS = {"csi_s3_p2_d1": "contains a 1h episode. Matches if "
                   "LENGTHDIFF goes to 40, but that seems rather extreme"}


def run_tests():
    f = Finder()
    print("Current DVD in drive: %s" % f.find_series())
    basepath = os.path.dirname(__file__)
    test_path = os.path.join(basepath, "seriesfindtest")
    all_lsdvds = sorted(glob(os.path.join(test_path, "*.txt")))
    for filepath in all_lsdvds:
        name = os.path.basename(filepath).rpartition(".txt")[0]
        with open(filepath, "r") as f:
            lsdvd = f.readlines()
        f = Finder(lsdvd)
        result = f.find_series()
        if name not in TESTS:
            print("No expected result for %s" % filepath)
            print("Output: %s" % (result,))
            continue
        expected_result = TESTS[name]
        if result == expected_result:
            print("Success: %s" % name)
        else:
            print("ERROR: %s" % name)
            print("result: %s, expected: %s" % (result, expected_result))
            if name in EXPECTED_ERRORS:
                print("Expected: %s" % EXPECTED_ERRORS[name])


def get_lsdvd():
    p = Popen(["lsdvd"], stdout=PIPE)
    stdout, _ = p.communicate()
    return stdout.decode().split("\n")


def is_close(l1, l2):
    diff = l1 * LENGTHDIFF / 100
    if abs(l1 - l2) < diff:
        return True
    return False


class Finder(object):
    def __init__(self, lsdvd=None, skip_duplicates=True):
        """
        :param lsdvd: The output of lsdvd. If not provided, run lsdvd.
        :param skip_duplicates: If two tracks have exactly the same duration,
                                throw a warning and skip the entry with the
                                greater track number.
        """
        self._parsed = None
        self.skip_duplicates = skip_duplicates
        if lsdvd is None:
            self.lsdvd = get_lsdvd()
        else:
            self.lsdvd = lsdvd

    @property
    def lengths(self):
        """ The duration of the tracks, as a list. """
        if self._parsed is not None:
            return self._parsed
        parsed = {}
        for line in self.lsdvd:
            if not line.startswith("Title"):
                continue
            # Really, we should do this by regex
            splitteded = line.split()
            tracknum = int(splitteded[1].strip(","))
            lengthstr = splitteded[3]
            h, m, s = lengthstr.split(":")
            sec = float(s) + int(m) * 60 + int(h) * 3600
            if self.skip_duplicates and sec in parsed.values():
                continue
            parsed[tracknum] = sec
        self._parsed = parsed
        return parsed

    def get_series_length(self, series):
        """ Get the total duration (in seconds) of the given series of tracks.
        """
        return sum([self.lengths[track] for track in series])

    def get_potential(self):
        """ Find multiple potential serieses. This means finding all sets of
        tracks that are within the given threshold of each other, and returning
        all of them. E.g. on a disc with 6 30 minute episodes and 2 hour long
        special features, it might return [[1, 2, 3, 4, 5, 6], [8, 9]]
        """
        # Create a dictionary with keys of track numbers, and value of a
        # list of all tracks that are close in length to it
        close = {}
        for track in self.lengths:
            for match in self.lengths:
                if track == match:
                    continue
                if is_close(self.lengths[track], self.lengths[match]):
                    if track not in close:
                        close[track] = []
                    close[track].append(match)
        # Now go through that dictionary, create set of the track numbers (and
        # the current track), and add it to our potential serieses.
        # TODO: This is overly complicated. I feel like this could be
        # all one small loop.
        potential_series = []
        for track, near_tracks in close.items():
            one_series = set(near_tracks)
            one_series.add(track)
            one_series = sorted(list(one_series))
            if one_series not in potential_series:
                potential_series.append(one_series)
        return potential_series

    def find_series(self):
        potential = self.get_potential()
        # Go through all the potential serieses, and assume that the one
        # with the longest duration is the one we're after.
        series_lengths = {}
        for series in potential:
            length = self.get_series_length(series)
            series_lengths[length] = series
        if not series_lengths:
            return []
        return series_lengths[max(series_lengths.keys())]


if __name__ == "__main__":
    run_tests()
