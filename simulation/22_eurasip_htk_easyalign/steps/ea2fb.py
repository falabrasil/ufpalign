#!/usr/bin/env python
#
# align.sh performs some phonetic mapping and this script undoes those in order
# to get back to original falabrasil phoneset
#
# author: jan 2021
# cassio batista - https://cassota.gitlab.io

import sys
import os
import glob
import random


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: %s <easyalign-pts-in-dir> <falabrasil-pts-out-dir>" %
              sys.argv[0])
        sys.exit(1)

    ea_dir = sys.argv[1]
    fb_dir = sys.argv[2]
    if not os.path.isdir(ea_dir):
        print("[%s] error: ea dir must exist: %s" % (sys.argv[0], ea_dir))
        sys.exit(1)
    elif not os.path.isdir(fb_dir):
        print("[%s] error: fb dir must exist: %s" % (sys.argv[0], fb_dir))
        sys.exit(1)

    for ea_file in sorted(glob.glob(os.path.join(ea_dir, "*.pts"))):
        fb_file = os.path.join(fb_dir, os.path.basename(ea_file))
        print("\r[%s] %s -> %s" % (sys.argv[0], ea_file, fb_file),
              end=" ", flush=True)
        # load ea file from disk
        with open(ea_file) as f:
            ea = f.readlines()
        ea_p, ea_ts = [], []
        for line in ea:
            ea_p.append(line.split()[0])
            ea_ts.append(line.split()[1])
        fb = []
        while len(ea_p):
            p_curr, ts_curr = ea_p.pop(0), ea_ts.pop(0)
            if p_curr == "t" or p_curr == "d":
                while len(ea_p):
                    p_next, ts_next = ea_p.pop(0), ea_ts.pop(0)
                    if (p_curr == "t" and p_next == "S") or \
                            (p_curr == "d" and p_next == "Z"):
                        p, ts = p_curr + p_next, float(ts_next)  # merge
                    else:
                        p, ts = p_curr, float(ts_curr)
                        ea_p.insert(0, p_next)
                        ea_ts.insert(0, ts_next)
                    break
            else:
                p = p_curr.replace("n4", "r")\
                          .replace("hh", random.choice(["R", "X"]))
                ts = float(ts_curr)
            fb.append("%s\t%.3f" % (p, ts))
        # write pts file to disk
        with open(fb_file, "w") as f:
            for item in fb:
                f.write(item.expandtabs(8) + "\n")
    print()
