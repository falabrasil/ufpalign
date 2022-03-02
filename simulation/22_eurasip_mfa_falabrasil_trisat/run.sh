#!/usr/bin/env bash
#
# author: feb 2021
# cassio batista - https://cassota.gitlab.io

WORKDIR=workspace

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
MIN_STAGE=1
MAX_STAGE=3
STAGE=$MIN_STAGE
while true ; do
  case $1 in
    -s | --stage) STAGE=$2; shift ;;
    -r | --reset) echo "$0: removing $WORKDIR" && rm -rf $WORKDIR; shift ;;
    *) break ;;
  esac
done

if [ -z $CONDA_PREFIX ] ; then
  echo "$0: warning: it is advised to install things under a conda venv."
  echo "  aborting."
  exit 1
fi

# sanity check
if [ $STAGE -lt $MIN_STAGE ] || [ $STAGE -gt $MAX_STAGE ] ; then
  echo "$0: STAGE flag outta bounds: [$MIN_STAGE, $MAX_STAGE]"
  exit 1
fi

if [ $STAGE -le 1 ] ; then
  mkdir -p $WORKDIR/tg
  echo "[$0] calling align script for male dataset" | lolcat
  steps/align.sh ../../../male   ../../../dict_fb.dict $WORKDIR/tg || exit 1
  echo "[$0] calling align script for female dataset" | lolcat
  steps/align.sh ../../../female ../../../dict_fb.dict $WORKDIR/tg || exit 1
fi

if [ $STAGE -le 2 ] ; then
  echo "[$0] calling tg2pts scripts" | lolcat
  mkdir -p $WORKDIR/pts
  steps/tg2pts.sh $WORKDIR/tg $WORKDIR/pts || exit 1
fi

if [ $STAGE -le 3 ] ; then
  echo "[$0] calling ptsunfold script" | lolcat
  steps/ptsunfold.py $WORKDIR/pts || exit 1
fi

echo "[$0] success!" | lolcat -ai -d 36
