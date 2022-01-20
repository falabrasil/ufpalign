#!/usr/bin/env python
#
# author: feb 2021
# cassio batista - https://cassota.gitlab.io

import sys
import os
import glob

import numpy as np


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s <pts-dir>' % sys.argv[0])
        sys.exit(1)

    pts_dir = sys.argv[1]
    if not os.path.isdir(pts_dir):
        print('error: pts dir must exist: \'%s\'' % pts_dir)
        sys.exit(1)

    for pts_file in sorted(glob.glob(os.path.join(pts_dir, '*.pts'))):
        print('\r[%s] processing file %s' % \
              (sys.argv[0], os.path.basename(pts_file)), end=' ', flush=True)

        with open(pts_file) as f:
            pts = f.readlines()

        phonemes = []
        timestamps = []
        for line in pts:
            p, ts = line.split()
            if p == '""' or p == '"sp"' or p == '"sil"':
                continue
            phonemes.append(p.replace('"', ''))
            timestamps.append(float(ts))

        with open(pts_file, 'w') as f:
            for p, ts in zip(phonemes, timestamps):
                pts = '%s\t%.3f' % (p, ts)
                f.write(pts.expandtabs(8) + '\n')
    print()
