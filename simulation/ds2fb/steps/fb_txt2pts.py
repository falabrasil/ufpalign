#!/usr/bin/env python
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# NOTE: to be called first, no direct dependency

import sys
import os
import glob


def l2d(l):
    d = {}
    for entry in l:
        entry = entry.split()
        g, p = entry[0], entry[1:]
        d[g] = p
    return d


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage: %s <txt-in-dir> <dict-file> <pts-out-dir>' % sys.argv[0])
        sys.exit(1)

    txt_dir = sys.argv[1]
    dict_file = sys.argv[2]
    pts_dir = sys.argv[3]

    if not os.path.isdir(txt_dir):
        print('error: transcriptions dir must exist: \'%s\'' % txt_dir)
        sys.exit(1)
    if not os.path.isfile(dict_file):
        print('error: dctionary file must exist: \'%s\'' % dict_file)
        sys.exit(1)

    with open(dict_file) as f:
        dictionary = l2d(f.readlines())

    for txt_file in glob.glob(os.path.join(txt_dir, '*.txt')):
        basefile = os.path.basename(txt_file)
        print('\r[%s] processing file %s' % (sys.argv[0], basefile),
              end=' ', flush=True)

        with open(txt_file) as f:
            txt = f.read().split()

        pts = []
        for word in txt:
            for phone in dictionary[word]:
                pts.append('%s\t%.3f' % (phone, 0.0))

        pts_file = os.path.join(pts_dir, basefile.replace('.txt', '.pts'))
        if os.path.isfile(pts_file):
            os.remove(pts_file)
        with open(pts_file, 'w') as f:
            for item in pts:
                f.write(item.expandtabs(8) + '\n')
    print()
