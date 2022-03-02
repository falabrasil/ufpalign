#!/usr/bin/env python
#
# author: nov 2020
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
        timestamps = [0.0]  # mark zero as first position
        for line in pts:
            p, ts = line.split()
            phonemes.append(p)
            timestamps.append(float(ts))

        new_phonemes = []
        new_timestamps = []
        for i, p in enumerate(phonemes):
            i += 1  # consider for the zero inserted as first ts mark
            if ':' in p:
                n = p.count(':') + 1
                for j, ts in enumerate(np.linspace(timestamps[i - 1], timestamps[i], n + 1)):
                    if j > 0:
                        new_timestamps.append(float(ts))
                new_phonemes += p.split(':')  # multi append to list w/o loop
            else:
                ts = timestamps[i]
                new_phonemes.append(p)
                new_timestamps.append(ts)

        with open(pts_file, 'w') as f:
            for p, ts in zip(new_phonemes, new_timestamps):
                pts = '%s\t%.3f' % (p, ts)
                f.write(pts.expandtabs(8) + '\n')
    print()
