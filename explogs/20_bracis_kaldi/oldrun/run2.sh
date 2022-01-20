#!/usr/bin/env bash
#
# This script had to be created because the HDD in which kaldi models were
# stored suddenly broke, then the models are apparently lost. fortunately,
# however, Larissa had already generated the CTM files from both male and
# female datasets, which are under ../../{male,female}/20_bracis_kaldi/*/ctm
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

WORKDIR=workspace
UFPALIGN_PLUGIN_DIR=/mnt/ext/fb-gitlab/fb-align/kaldi-align/plugin_ufpalign-2.0/UFPAlign

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
while true ; do
  case $1 in
    -r | --reset) echo "$0: removing $WORKDIR" && rm -rf $WORKDIR; shift ;;
    *) break ;;
  esac
done

if [ ! -d $UFPALIGN_PLUGIN_DIR ] ; then
  echo "[$0] error: please download UFPAlign 2.0 plugin."
  echo -n "  the recommended approach is to clone the following repo from Gitlab: "
  echo "gitlab.com/fb-align/kaldi-align.git"
  echo -n "  then extract 'plugin_ufpalign-2.0.tar.gz' and 'UFPAlign.tar.gz' "
  echo "in that order"
  exit 1
fi

rm -rf $WORKDIR/pts
for ctm in $(find ../../{male,female}/20_bracis_kaldi -name "*.phoneids.ctm") ; do
  echo "[$0] processing $ctm" | lolcat
  out_dir=$WORKDIR/pts/$(basename $ctm | cut -d '.' -f 1)
  mkdir -p $out_dir
  steps/ctm2pts2.py \
    $ctm \
    $UFPALIGN_PLUGIN_DIR/exp/dnn_model/phones.txt \
    $out_dir || exit 1
done

echo "[$0] success!" | lolcat -ai -d 36
