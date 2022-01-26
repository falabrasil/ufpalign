#!/usr/bin/env python
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

import sys
import os
from datetime import timedelta

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s <start-time> <end-time>')
        print('  <*-time> is a string in the format %H:%M:%S')
        sys.exit(1)

    s_time = sys.argv[1]
    e_time = sys.argv[2]

    hs, ms, ss = s_time.split(':')
    he, me, se = e_time.split(':')
    h, m, s = int(he) - int(hs), int(me) - int(ms), int(se) - int(ss)
    t = timedelta(seconds=h * 3600 + m * 60 + s)
    print(str(t))
