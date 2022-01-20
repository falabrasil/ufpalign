#!/usr/bin/env python3
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

import sys
import os
import glob

FACTOR = 10 ** -7

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: %s <rec-in-dir> <pts-out-dir>" % sys.argv[0])
        sys.exit(1)

    rec_dir = sys.argv[1]
    pts_dir = sys.argv[2]
    if not os.path.isdir(rec_dir):
        print("[%s] error: rec dir must exist: %s" % (sys.argv[0], rec_dir))
        sys.exit(1)
    elif not os.path.isdir(pts_dir):
        print("[%s] error: pts dir must exist: %s" % (sys.argv[0], pts_dir))
        sys.exit(1)

    for rec_file in sorted(glob.glob(os.path.join(rec_dir, "*.rec"))):
        pts_file = os.path.basename(rec_file.replace(".rec", ".pts"))
        pts_file = os.path.join(pts_dir, pts_file)
        print("\r[%s] %s -> %s" % (sys.argv[0], rec_file, pts_file),
              end=" ", flush=True)
        # load rec file from disk
        with open(rec_file) as f:
            rec = f.readlines()
        pts = []
        for line in rec:
            start, stop, phone = line.split()[:3]
            if phone == "sil":  # FIXME should I be doing this?
                continue
            pts.append("%s\t%.3f" % (phone, float(stop) * FACTOR))
        # write pts file to disk
        with open(pts_file, "w") as f:
            for item in pts:
                f.write(item.expandtabs(8) + "\n")
    print()
