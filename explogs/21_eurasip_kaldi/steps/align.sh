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

. cmd.sh
. path.sh

if [[ "$am_tag" == "mono" ]] || [[ "$am_tag" == "tri1" ]] ; then
  steps/align_si.sh --nj 2 --cmd "$train_cmd" \
    data/alignme_lores data/lang exp/$am_tag results/${am_tag}_ali_alignme || exit 1
elif [[ "$am_tag" == "tri"* ]] ; then
  steps/align_fmllr.sh --nj 2 --cmd "$train_cmd" \
    data/alignme_lores data/lang exp/$am_tag results/${am_tag}_ali_alignme || exit 1
elif [[ "$am_tag" == *"tdnn"* ]] ; then
  steps/nnet3/align.sh --nj 2 --cmd "$train_cmd" --use-gpu true \
    --online-ivector-dir exp/tdnn/ivectors_hires \
    --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
    data/alignme_hires data/lang exp/$am_tag results/${am_tag}_ali_alignme || exit 1
else
    echo "[$0] bad acoustic model tag: $am_tag" && exit 1
fi

cd - > /dev/null
