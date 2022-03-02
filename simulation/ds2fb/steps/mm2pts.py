#!/usr/bin/env python
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# to be executed after news2mm

import sys
import os
from itertools import count

from termcolor import colored

TAG = sys.argv[0]

# total number of pts files that *should* exist, since the number of files in
# the falabrasil dataset is lower due to discards (see BRACIS 2020 paper)
N = 200
SKIP_COUNT = 0


def mm2pts(fin, fout, mm, sil_mark):
    with open(fin) as f:
        pts = f.readlines()
    new_pts, index = [], count(0)
    while len(mm):
        token = mm.pop(0)
        if token == '_':  # deletion detected
            print()
            print(colored('[%s] skipping "%s" due crossword deletion!',
                          'yellow') % (TAG, os.path.basename(fin)))
            global SKIP_COUNT
            SKIP_COUNT += 1
            if os.path.isfile(fout):
                os.remove(fout)
            return
        p, ts = pts[next(index)].split()
        if p == sil_mark:  # skip short pause
            p, ts = pts[next(index)].split()
        if ':' in token:
            for i in range(token.count(':')):
                p, ts = pts[next(index)].split()
        new_pts.append('%s\t%.3f' % (token, float(ts)))

    print('\r[%s] %s -> %s' % (TAG, fin, fout), end=' ', flush=True)
    with open(fout, 'w') as f:
        for item in new_pts:
            f.write(item.expandtabs(8) + '\n')


def ts_ds2fb(ds_f, fb_f):
    if os.path.isfile(ds_f) and os.path.isfile(fb_f):
        with open(ds_f) as f, open(fb_f) as g:
            ds, fb = f.readlines(), g.readlines()
        new_pts = []
        for ds_pts, fb_pts in zip(ds, fb):
            p, _ = fb_pts.split()
            _, ts = ds_pts.split()
            new_pts.append('%s\t%.3f' % (p, float(ts)))
        with open(fb_f, 'w') as f:
            for item in new_pts:
                f.write(item.expandtabs(8) + '\n')
    else:
        if os.path.isfile(ds_f):
            os.remove(ds_f)
        if os.path.isfile(fb_f):
            os.remove(fb_f)


if __name__ == '__main__':
    if len(sys.argv) < 7:
        print('usage: %s <mm-in-file> '
              '<ds-pts-in-dir> <fb-pts-in-dir> '
              '<ds-pts-out-dir> <fb-pts-out-dir> '
              '<gender-tag>' % TAG)
        sys.exit(1)

    mm_file = sys.argv[1]
    ds_pts_in_dir = sys.argv[2]
    fb_pts_in_dir = sys.argv[3]
    ds_pts_out_dir = sys.argv[4]
    fb_pts_out_dir = sys.argv[5]
    gender_tag = sys.argv[6]

    # sanity check
    if not os.path.isfile(mm_file):
        print('[%s] error: mm file must exist: %s' % (TAG, mm_file))
        sys.exit(1)
    elif not os.path.isdir(ds_pts_in_dir):
        print('[%s] error: ds in dir must exist: %s' % (TAG, ds_pts_in_dir))
        sys.exit(1)
    elif not os.path.isdir(fb_pts_in_dir):
        print('[%s] error: fb in dir must exist: %s' % (TAG, fb_pts_in_dir))
        sys.exit(1)
    elif not os.path.isdir(ds_pts_out_dir):
        print('[%s] error: ds out dir must exist: %s' % (TAG, ds_pts_out_dir))
        sys.exit(1)
    elif not os.path.isdir(fb_pts_out_dir):
        print('[%s] error: fb out dir must exist: %s' % (TAG, fb_pts_out_dir))
        sys.exit(1)
    elif gender_tag != 'M' and gender_tag != 'F':
        print('[%s] error: gender tag should be either "M" or "F"' % \
              (TAG, gender_tag))
        sys.exit(1)

    # store filenames in a list to be later accessed by indices that correspond
    # to the lines of the mm file
    ds_pts_filelist = []
    fb_pts_filelist = []
    for i in range(1, N + 1):
        basefile = '%s-%03d.pts' % (gender_tag, i)
        ds_pts = os.path.join(ds_pts_in_dir, basefile)
        fb_pts = os.path.join(fb_pts_in_dir, basefile)
        if os.path.isfile(ds_pts) and os.path.isfile(fb_pts):
            ds_pts_filelist.append(ds_pts)
            fb_pts_filelist.append(fb_pts)

    # load mm alignments into RAM
    with open(mm_file) as f:
        mm = f.readlines()

    # now the game begins
    for i, ali in enumerate(mm):
        # first get two str, then split str into a list of phoneme tokens
        ds_mm, fb_mm = ali.split()
        ds_mm, fb_mm = ds_mm.split('|')[:-1], fb_mm.split('|')[:-1]

        # load ds pts files into a list in RAM
        ds_fin, fb_fin = ds_pts_filelist[i], fb_pts_filelist[i]
        ds_fout = os.path.join(ds_pts_out_dir, os.path.basename(ds_fin))
        fb_fout = os.path.join(fb_pts_out_dir, os.path.basename(fb_fin))
        mm2pts(ds_fin, ds_fout, list(ds_mm), '"_"')
        mm2pts(fb_fin, fb_fout, list(fb_mm), '"_"')
        ts_ds2fb(ds_fout, fb_fout)
    print()
    print(colored('[%s] %d files skipped for tag %s', 'green') % \
          (TAG, SKIP_COUNT, gender_tag))
