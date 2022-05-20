#!/usr/bin/env python3
#
# this scripts reads intersection over union *.iou files from a dir 
# (the files must be in the same dir) in order to plot a boxplot of
# the distrubution per phoneme
#
# authors: nov 2021
# cassio batista - https://cassota.gitlab.io/

import sys
import os
import re
import glob
import pickle

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

MAP = {
    'Kaldi (tri-Δ) - M':           'UFPAlign\n(tri-Δ)',
    'Kaldi (tri-Δ) - F':           'UFPAlign\n(tri-Δ)',
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: %s <iou-file>" % sys.argv[0])
        print("  <iou-file> is the the phone boundary log file")
        sys.exit(1)

    iou_list = []
    for iou_file in sys.argv[1:]:
        if not os.path.isfile(iou_file) or not iou_file.endswith(".iou"):
            print("%s: error: file '%s' does not exist or has invalid "
                  "format." % (sys.argv[0], iou_file))
            sys.exit(1)
        iou_list.append(iou_file)

    fig, ax = plt.subplots(figsize=(10.8, 4.8))
    for i, filename in enumerate(iou_list):
        key = os.path.basename(filename).replace(".iou", "")
        gender = "male" if key.endswith("M") else "female"
        with open(filename, "rb") as f:
            iou_contents = pickle.load(f)
        mean, median = iou_contents["mean"], iou_contents["median"]
        del    iou_contents["mean"]
        del    iou_contents["median"]
        ax.axhline(mean, 0, len(iou_contents),
                c="g", ls="dashed", lw=1.25, zorder=0)
        ax.axhline(median, 0, len(iou_contents),
                c="r", ls="dashed", lw=1.25, zorder=0)
        sns.boxplot(ax=ax, data=list(iou_contents.values()),
                palette=["white"] * len(iou_contents), showmeans=True)
        ax.yaxis.tick_right()
        ax.set_yticks(np.arange(0.0, 1.1, 0.1))
        ax.set_yticklabels(["%.1f" % f for f in np.arange(0.0, 1.1, 0.1)], fontsize=12)
        ax.set_ylabel(MAP[key].replace("\n", " "), fontsize=14)
        ax.set_xticklabels([])
        for pos in ("top", "right", "bottom", "left"):
            ax.spines[pos].set_visible(False)
    ax.set_xticklabels(iou_contents.keys(), fontsize=14, rotation=0, ha="center", va="top")
    plt.subplots_adjust(left=0.05, bottom=0.075, right=0.95, top=0.975, wspace=0.01, hspace=0.01)
    plt.savefig("/tmp/iou_%s_trideltas.png" % gender)
