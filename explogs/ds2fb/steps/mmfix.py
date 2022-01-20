#!/usr/bin/env python
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

import sys
import os
from collections import OrderedDict


mappings = OrderedDict()
mappings['~|n:t'] = '~:n|t'
mappings['~|n:s'] = '~:n|s'
mappings['~|n:k'] = '~:n|k'
mappings['~|n:d'] = '~:n|d'
mappings['~|m:p'] = '~:m|p'
mappings['t|S:i'] = 't:S|i'
mappings['d|Z:i'] = 'd:Z|i'
mappings['|j:s'] = ':j|s'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s <mm-file>')
        sys.exit(1)

    mm_file = sys.argv[1]
    if not os.path.isfile(mm_file):
        print('error: mm file must exist: \'%s\'' % mm_file)
        sys.exit(1)

    with open(mm_file) as f:
        mm = f.readlines()

    ds_new, fb_new = [], []
    for i, ali in enumerate(mm):
        print('\r[%s] processing alignment %03d' % (sys.argv[0], (i + 1)),
              end=' ', flush=True)
        ds_mm, fb_mm = ali.split()
        for k, v in mappings.items():
            ds_mm = ds_mm.replace(k, v)
            fb_mm = fb_mm.replace(k, v)
        ds_new.append(ds_mm)
        fb_new.append(fb_mm)

    with open(mm_file, 'w') as f:
        for ds, fb in zip(ds_new, fb_new):
            f.write('%s\t%s\n' % (ds, fb))
    print()
