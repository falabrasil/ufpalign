#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 1 ; then
  echo "usage: $0 <kaldi-egs-dir>"
  exit 1
fi

proj_dir=$1

cd $proj_dir

steps/make_mfcc.sh --cmd run.pl --nj 8 data/alignme exp/make_mfcc mfcc || exit 1
utils/fix_data_dir.sh data/alignme

steps/compute_cmvn_stats.sh data/alignme exp/make_mfcc mfcc || exit 1
utils/fix_data_dir.sh data/alignme

cd - > /dev/null
