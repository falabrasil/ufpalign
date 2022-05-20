#!/usr/bin/env bash
#
# author: jan 2021
# cassio batista - https://cassota.gitlab.io

if test $# -ne 1 ; then
  echo "usage: $0 <kaldi-egs-dir>"
  exit 1
fi

proj_dir=$1

cd $proj_dir

. cmd.sh
. path.sh

steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj 2 \
  data/alignme_hires exp/nnet3_online_cmn/extractor exp/tdnn/ivectors_hires || exit 1

cd - > /dev/null
