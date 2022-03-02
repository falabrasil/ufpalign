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

. cmd.sh
. path.sh

rm -rf data/alignme_{lores,hires}
utils/copy_data_dir.sh data/alignme data/alignme_lores
utils/copy_data_dir.sh data/alignme data/alignme_hires

echo "[$0] computing low resolution features" | lolcat
steps/make_mfcc.sh --cmd "$train_cmd" --nj 2 data/alignme_lores || exit 1
steps/compute_cmvn_stats.sh data/alignme_lores || exit 1
utils/fix_data_dir.sh data/alignme_lores

echo "[$0] computing high resolution features" | lolcat
steps/make_mfcc.sh --cmd "$train_cmd" --nj 2 --mfcc-config conf/mfcc_hires.conf \
    data/alignme_hires || exit 1
steps/compute_cmvn_stats.sh data/alignme_hires || exit 1
utils/fix_data_dir.sh data/alignme_hires

cd - > /dev/null
