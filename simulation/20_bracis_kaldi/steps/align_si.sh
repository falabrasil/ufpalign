#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 2 ; then
  echo "usage: $0 <kaldi-egs-dir> <am-tag>"
  exit 1
fi

proj_dir=$1
am_tag=$2  # mono, tri1, tri2, tri3

cd $proj_dir

steps/align_si.sh --nj 8 --cmd run.pl \
  data/alignme data/lang exp/$am_tag exp/${am_tag}_ali || exit 1

cd - > /dev/null
