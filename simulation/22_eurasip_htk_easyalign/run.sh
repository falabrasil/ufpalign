#!/usr/bin/env bash
#
# author: jan 2021
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

# sanity check
if [ $STAGE -lt $MIN_STAGE ] || [ $STAGE -gt $MAX_STAGE ] ; then
  echo "$0: stage flag outta bounds: [$MIN_STAGE, $MAX_STAGE]"
  exit 1
fi

if [ $STAGE -le 1 ] ; then
  msg "[$0] calling HTK aligner script"
  mkdir -p $WORKDIR/rec
  steps/align.sh $DATA_DIR/male   dicionariofonetico.txt $WORKDIR/rec || exit 1
  steps/align.sh $DATA_DIR/female dicionariofonetico.txt $WORKDIR/rec || exit 1
fi

if [ $STAGE -le 2 ] ; then
  msg "[$0] calling rec2pts script"
  mkdir -p $WORKDIR/pts/ea
  steps/rec2pts.py $WORKDIR/rec $WORKDIR/pts/ea || exit 1
fi

if [ $STAGE -le 3 ] ; then
  msg "[$0] calling ea2fb script"
  mkdir -p $WORKDIR/pts/fb
  steps/ea2fb.py $WORKDIR/pts/ea $WORKDIR/pts/fb || exit 1
fi

msg "[$0] success!"
