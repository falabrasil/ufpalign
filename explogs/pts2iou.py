#!/usr/bin/env python
#
# author: nov 2021
# cassio batista - https://cassota.gitlab.io

import sys
import os
import glob
import io
import pickle
import locale
from collections import OrderedDict
from functools import cmp_to_key

import numpy as np
import pandas as pd
from termcolor import colored

TAG = sys.argv[0]
N = 200


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('usage: %s <ground-truth-pts-dir> <predicted-pts-dir> '
              '<gender-tag> <pb-out-file>' % TAG)
        print('  e.g.: %s {ds2fb,21_csl_mfa_gentle/mfa2fb}/workspace/pts_out/fb/ M /tmp/out.pb' % TAG)
        print('  NOTE: scripts under ds2fb/ and mfa2fb/ dirs should have been '
              'executed beforehand, obviously')
        sys.exit(1)

    truth_dir = sys.argv[1]
    predict_dir = sys.argv[2]
    gender_tag = sys.argv[3]
    pb_file = sys.argv[4]
    for d in (truth_dir, predict_dir):
        if not os.path.isdir(d):
            print('%s: error: dir should exist: "%s"' % (TAG, d))
            sys.exit(1)
    if gender_tag != 'M' and gender_tag != 'F':
        print('%s: error: gender tag should be either "M" of "F"' % TAG)
        sys.exit(1)

    truth_pts_filelist = []
    predict_pts_filelist = []
    for i in range(1, N + 1):
        basefile = '%s-%03d.pts' % (gender_tag, i)
        #print('\r[%s] processing file %s' % (TAG, basefile), end=' ', flush=True)
        truth_pts = os.path.join(truth_dir, basefile)
        predict_pts = os.path.join(predict_dir, basefile)
        if os.path.isfile(truth_pts) and os.path.isfile(predict_pts):
            truth_pts_filelist.append(truth_pts)
            predict_pts_filelist.append(predict_pts)

    intersection_over_union = {}
    intersection_over_union_all = []
    for truth_pts, predicted_pts in zip(truth_pts_filelist,
                                        predict_pts_filelist):
        basefile = os.path.basename(truth_pts)
        with open(truth_pts) as f, open(predicted_pts) as g:
            truth, predicted = f.readlines(), g.readlines()
        if len(truth) != len(predicted):
            print(colored('%s: file sizes differ: %d vs %d. this should not '
                          'be happening' % (TAG, len(truth), len(predicted)), 'yellow'))
            continue
        # https://stackoverflow.com/questions/42171709/creating-pandas-dataframe-from-a-list-of-strings
        ref_df = pd.read_csv(io.StringIO("\n".join(truth)),     names=["phone", "timestamp"], delim_whitespace=True)
        hyp_df = pd.read_csv(io.StringIO("\n".join(predicted)), names=["phone", "timestamp"], delim_whitespace=True)

        ref_ts = [0.0] + ref_df.timestamp.tolist()
        hyp_ts = [0.0] + hyp_df.timestamp.tolist()
        assert len(ref_ts) == len(hyp_ts), "dimensions should match"
        for i in range(len(ref_ts) - 1):
            x1, x2 = ref_ts[i:i+2]
            y1, y2 = hyp_ts[i:i+2]
            # https://stackoverflow.com/questions/3269434/whats-the-most-efficient-way-to-test-two-integer-ranges-for-overlap
            if x1 <= y2 and y1 <= x2:
                vec = sorted(np.array([x1, x2, y1, y2]) * 1000.0)
                iou = [np.abs(vec[2] - vec[1]) / np.abs(vec[0] - vec[3])]
            else:
                iou = [0.0]
            key = hyp_df.iloc[i]["phone"]
            if key in intersection_over_union:
                intersection_over_union[key] += iou
            else:
                intersection_over_union[key] = iou
            intersection_over_union_all.append(iou[0])

    # https://stackoverflow.com/questions/9001509/how-can-i-sort-a-dictionary-by-key
    # https://stackoverflow.com/questions/24728933/sort-dictionary-alphabetically-when-the-key-is-a-string-name
    intersection_over_union["mean"] = np.mean(intersection_over_union_all)
    intersection_over_union["median"] = np.median(intersection_over_union_all)
    with open(pb_file, 'wb') as f:
        pickle.dump(OrderedDict(sorted(intersection_over_union.items(), key=lambda x: x[0].lower())),
                f, pickle.HIGHEST_PROTOCOL)
    #print('ok\toutput written to %s' % pb_file)
