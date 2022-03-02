#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

. env.sh || exit 1

WORKDIR=workspace
nj=10

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
MIN_STAGE=1
MAX_STAGE=2
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
  msg "[$0] calling HTK aligner script (parallel in $nj CPU cores)"
  mkdir -p $WORKDIR/rec/
  s_time=$(date +'%T')
  steps/align.sh $DATA_DIR/male   $DATA_DIR/dict_fb.dict $WORKDIR/rec $nj || exit 1
  steps/align.sh $DATA_DIR/female $DATA_DIR/dict_fb.dict $WORKDIR/rec $nj || exit 1
  e_time=$(date +'%T')
  msg "[$0] elapsed time: $(utils/elapsed_time.py $s_time $e_time)"
fi

if [ $STAGE -le 2 ] ; then
  msg "[$0] calling rec2pts script" | lolcat
  mkdir -p $WORKDIR/pts/
  steps/rec2pts.py $WORKDIR/rec $WORKDIR/pts || exit 1
fi

msg "[$0] success!"
