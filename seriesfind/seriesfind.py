import os
from glob import glob
from subprocess import Popen, PIPE

# If two tracks are within this percentage, they could be part of a
# series
LENGTHDIFF = 25

tests = {"csi_s1_p2_d1": [1, 2, 3, 4], "csi_s1_p2_d2": [1, 2, 3, 4],
         "csi_s1_p2_d3": [1, 2, 3, 4], "csi_s2_p1_d1": [1, 2, 3, 4],
         "csi_s2_p1_d3": [1, 2, 3, 4], "csi_s2_p2_d1": [1, 2, 3, 4],
         "csi_s2_p2_d3": [1, 2, 3], "fatherted_s2_d1": [1, 2, 3, 4, 5],
         "doctorwho_s1_d1": [3, 4, 5], "mightboosh_s2_d1": [2, 3, 4, 5, 6, 7],
         "tomandjerry_v4_s1": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
         "doctorwho_s1_d4": [7, 8, 9], "doctorwho_s1_d2": [4, 5, 6],
         "csi_s3_p1_d1": [2, 3, 4, 5], "csi_s3_p1_d2": [2, 3, 4, 5],
         "csi_s3_p1_d3": [2, 3, 4, 5], "csi_s3_p2_d1": [2, 3, 4, 5],
         "csi_s3_p2_d2": [4, 5, 6, 7], "csi_s3_p2_d3": [2, 3, 4],
         "csi_s4_p1_d3": [2, 3, 5, 6], "friends_27": [1, 2, 3, 4, 5, 6]}

# csi_s3_p2_d1: contains a 1h episode. Matches if LENGTHDIFF goes to 40,
#               but that seems rather extreme


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
        if name not in tests:
            print("No expected result for %s" % filepath)
            print("Output: %s" % (result,))
            continue
        expected_result = tests[name]
        if result == expected_result:
            print("Success: %s" % name)
        else:
            print("ERROR: %s" % name)
            print("result: %s, expected: %s" % (result, expected_result))


def get_lsdvd():
    p = Popen(["lsdvd"], stdout=PIPE)
    stdout, _ = p.communicate()
    return stdout.split("\n")


def is_close(l1, l2):
    diff = l1 * LENGTHDIFF / 100
    if abs(l1 - l2) < diff:
        return True
    return False


class Finder(object):
    def __init__(self, lsdvd=None):
        self._parsed = None
        if lsdvd is None:
            self.lsdvd = get_lsdvd()
        else:
            self.lsdvd = lsdvd

    @property
    def lengths(self):
        if self._parsed is not None:
            return self._parsed
        parsed = {}
        for line in self.lsdvd:
            if not line.startswith("Title"):
                continue
            splitteded = line.split()
            tracknum = splitteded[1].strip(",")
            lengthstr = splitteded[3]
            h, m, s = lengthstr.split(":")
            sec = float(s) + int(m) * 60 + int(h) * 3600
            parsed[int(tracknum)] = sec
        self._parsed = parsed
        return parsed

    def get_series_length(self, series):
        return sum([self.lengths[track] for track in series])

    def get_potential(self):
        close = {}
        for track in self.lengths:
            for match in self.lengths:
                if track == match:
                    continue
                if is_close(self.lengths[track], self.lengths[match]):
                    if track not in close:
                        close[track] = []
                    close[track].append(match)
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
        series_lengths = {}
        for series in potential:
            length = self.get_series_length(series)
            series_lengths[length] = series
        if not series_lengths:
            return []
        return series_lengths[max(series_lengths.keys())]


if __name__ == "__main__":
    run_tests()
