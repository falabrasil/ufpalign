#!/usr/bin/env python3
#
# author: oct 2021
# cassio batista - https://cassota.gitlab.io

import sys
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.set_printoptions(threshold=1000)

DEBUG=False

if __name__ == "__main__":

    pb_m_dict = {}
    pb_f_dict = {}
    print(sys.argv)
    for log in sys.argv[1:]:
        with open(log) as f:
            contents = f.read()
        model_list = re.findall(r"ok\toutput written to ([\w\./]+)", contents)
        pb_m_list = re.findall(r"ali_m\s+\t(.*)\t", contents)
        pb_f_list = re.findall(r"ali_f\s+\t(.*)\t", contents)

        for model, pb_m, pb_f in zip(model_list, pb_m_list, pb_f_list):
            model = model.split("/")[-2].replace("tdnn_", "").replace("_sp_ali", "")
            m = pb_m.split("|")[1].replace("%", "").split()
            f = pb_f.split("|")[1].replace("%", "").split()
            if DEBUG:
                print("%-40s" % model, "m", m)
                print("%-40s" % model, "f", f)
            for g, d in zip((m, f), (pb_m_dict, pb_f_dict)):
                g = [float(s) for s in g]
                for i in range(len(g) - 1, 0, -1):
                    g[i] -= g[i-1]  # un-accumulative
                if model in d:
                    d[model].append(g)
                else:
                    d[model] = [g]

    df_m = pd.DataFrame(columns=["model", "means", "stds"])
    df_f = pd.DataFrame(columns=["model", "means", "stds"])

    # male
    means = np.round(np.array([np.mean(v, axis=0) for v in pb_m_dict.values()]), 3)
    stds  = np.round(np.array([np.std(v, axis=0)  for v in pb_m_dict.values()]), 3)
    for k, μ, σ in zip(pb_m_dict.keys(), means, stds):
        k = re.sub(r"^(\w+)_(chain|nochain)", "\g<2>", k)  # remove model id
        k = re.sub(r"_ivector", "+ivector", k)
        if DEBUG:
            print("%-40s" % k, μ, σ)
        df = pd.DataFrame({
            "model": k,
            "means": [μ],
            "stds":  [σ]
        })
        df_m = pd.concat([df_m, df], axis=0)

    # female
    means = np.round(np.array([np.mean(v, axis=0) for v in pb_f_dict.values()]), 3)
    stds  = np.round(np.array([np.std(v, axis=0)  for v in pb_f_dict.values()]), 3)
    for k, μ, σ in zip(pb_f_dict.keys(), means, stds):
        k = re.sub(r"^(\w+)_(chain|nochain)", "\g<2>", k)  # remove model id
        k = re.sub(r"_ivector", "+ivector", k)
        if DEBUG:
            print("%-40s" % k, μ, σ)
        df = pd.DataFrame({
            "model": k,
            "means": [μ],
            "stds":  [σ]
        })
        df_f = pd.concat([df_f, df], axis=0)

    # https://stackoverflow.com/questions/15325182/how-to-filter-rows-in-pandas-by-regex/48884429
    # nochain, chain, chain
    #(r"ivector$", r"_fs3$", r"_nofs$"),
    #("No Chain", "Chain FS=3", "Chain FS=1")
    fig, ax = plt.subplots(2, 1)
    for i, (bucket, label) in enumerate(
            zip( (r"ivector$", r"_fs3$"), ("No chain", "Chain") )
        ):
        mdf = df_m[df_m.model.str.contains(bucket)]
        fdf = df_f[df_f.model.str.contains(bucket)]
        mμ, mσ = np.array(mdf.means.tolist()), np.array(mdf.stds.tolist())
        fμ, fσ = np.array(fdf.means.tolist()), np.array(fdf.stds.tolist())
        prev_mμ, prev_fμ = None, None
        assert mμ.shape == fμ.shape, 'unmatched shapes'
        ind = np.arange(mμ.shape[1])
        alphas = 1.0 - np.linspace(0.2, 0.8, mμ.shape[0])
        for row, tol in zip(range(mμ.shape[0]), (10, 25, 50, 100)):
            if tol == 100:
                break
            curr_mμ, curr_mσ = mμ.T[row, :], mσ.T[row, :]
            curr_fμ, curr_fσ = fμ.T[row, :], fσ.T[row, :]
            mb = ax[i].bar(ind, curr_mμ, 0.4, yerr=curr_mσ,
                    bottom=prev_mμ, capsize=7.5, label=r"$<%d~$ms" % tol,
                    color="C0", alpha=alphas[row], zorder=3)
            fb = ax[i].bar(ind + 0.4, curr_fμ, 0.4, yerr=curr_fσ,
                    bottom=prev_fμ, capsize=7.5, label=r"$<%d~$ms" % tol,
                    color="C3", alpha=alphas[row], zorder=3)
            ax[i].bar_label(mb, label_type='edge', fmt="%.2f%%", fontsize=20, rotation=0)
            ax[i].bar_label(fb, label_type='edge', fmt="%.2f%%", fontsize=20, rotation=0)
            for pos in ('top', 'right', 'bottom', 'left'):
                ax[i].spines[pos].set_visible(False)
            # make
            if prev_mμ is None:
                prev_mμ = curr_mμ
            else:  # re-accumulate
                prev_mμ += curr_mμ
            # female
            if prev_fμ is None:
                prev_fμ = curr_fμ
            else:  # re-accumulate
                prev_fμ += curr_fμ
        if i == 0:
            ax[i].set_xticklabels(["" for x in mdf.model])
        else:
            ax[i].legend(loc='right', bbox_to_anchor=(1.09, 1.0), ncol=1, fontsize=18)
            ax[i].set_xticklabels([re.sub(r"chain_|nochain_|_fs3|_nofs|_noivector", "", x) for x in mdf.model], fontsize=28)
        ax[i].grid(axis='y')
        ax[i].set_ylabel(label, fontsize=24)
        ax[i].set_yticks(range(0, 101, 20))
        #ax[i].set_yticklabels([])
        ax[i].set_ylim([29, 105])
        ax[i].set_xlim([-0.25, 3.75])
        ax[i].set_xticks(ind + 0.4 / 2)
    plt.subplots_adjust(left=0.04, bottom=0.10, right=0.925, top=0.95,
            hspace=0.1, wspace=0.01)
    plt.show()
