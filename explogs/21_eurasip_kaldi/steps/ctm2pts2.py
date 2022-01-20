#!/usr/bin/env python
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

import sys
import os
import glob

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: %s <phoneids.ctm> <phones.txt> <pts-out-dir>" % sys.argv[0])
        sys.exit(1)

    phoneids_file = sys.argv[1]
    phones_file = sys.argv[2]
    pts_dir = sys.argv[3]

    if not os.path.isfile(phoneids_file):
        print("[%s] error: phoneids.ctm file '%s' does not exist" % \
              (sys.argv[0], phoneids_file))
        sys.exit(1)
    if not os.path.isfile(phones_file):
        print("[%s] error: phones.txt file '%s' does not exist" % \
              (sys.argv[0], phones_file))
        sys.exit(1)
    if not os.path.isdir(pts_dir):
        print("[%s] error: pts out dir '%s' does not exist" % \
              (sys.argv[0], pts_dir))
        sys.exit(1)

    print("[%s] mapping file '%s'" % (sys.argv[0], phones_file))
    with open(phones_file) as f:
        phones = f.readlines()
    mapping = {}
    for line in phones:
        phone, phoneid = line.split()
        mapping[phoneid] = phone.split("_")[0]

    print("[%s] loading file '%s'" % (sys.argv[0], phoneids_file))
    with open(phoneids_file) as f:
        phoneids = f.readlines()

    while len(phoneids):
        pts = []
        uttid, ch, start, dur, phoneid = phoneids.pop(0).split()
        phone, timestamp = mapping[phoneid], float(start) + float(dur)
        pts.append("%s\t%.3f" % (phone, timestamp))
        while len(phoneids):
            uttid2, ch, start, dur, phoneid = phoneids.pop(0).split()
            if uttid2 == uttid:
                phone, timestamp = mapping[phoneid], float(start) + float(dur)
                pts.append("%s\t%.3f" % (phone, timestamp))
            else:
                uttline = "%s %s %s %s %s" % (uttid2, ch, start, dur, phoneid)
                phoneids.insert(0, uttline)
                break
        pts_file = os.path.join(pts_dir, "%s.pts" % uttid)
        print("\r[%s] writing file '%s'" % (sys.argv[0], pts_file),
              end=" ", flush=True)
        with open(pts_file, "w") as f:
            for item in pts:
                f.write(item.expandtabs(8) + "\n")
    print()
