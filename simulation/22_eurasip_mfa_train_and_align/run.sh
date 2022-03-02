#!/usr/bin/env bash
#
# author: feb 2021
# cassio batista - https://cassota.gitlab.io

. ../env.sh || exit 1

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

# FIXME docker?
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
  msg "[$0] calling train and align script for male dataset"
  steps/train_and_align.sh $DATA_DIR/male   $DATA_DIR/dict_fb.dict $WORKDIR/tg || exit 1
  msg "[$0] calling train and align script for female dataset"
  steps/train_and_align.sh $DATA_DIR/female $DATA_DIR/dict_fb.dict $WORKDIR/tg || exit 1
fi

if [ $STAGE -le 2 ] ; then
  msg "[$0] calling tg2pts scripts"
  mkdir -p $WORKDIR/pts
  steps/tg2pts.sh $WORKDIR/tg $WORKDIR/pts || exit 1
fi

if [ $STAGE -le 3 ] ; then
  msg "[$0] calling ptsunfold script"
  steps/ptsunfold.py $WORKDIR/pts || exit 1
fi

msg "[$0] success!"
