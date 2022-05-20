#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

. ../env.sh || exit 1

WORKDIR=workspace

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
MIN_STAGE=1
MAX_STAGE=7
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
  msg "[$0] calling tg2pts scripts"
  mkdir -p $WORKDIR/pts_in/ds
  steps/ds_tg2pts.sh $DATA_DIR/male   $WORKDIR/pts_in/ds || exit 1
  steps/ds_tg2pts.sh $DATA_DIR/female $WORKDIR/pts_in/ds || exit 1
fi

if [ $STAGE -le 2 ] ; then
  msg "[$0] calling txt2pts scripts"
  mkdir -p $WORKDIR/pts_in/fb
  steps/fb_txt2pts.py $DATA_DIR/male   $DATA_DIR/dict_fb.dict $WORKDIR/pts_in/fb || exit 1
  steps/fb_txt2pts.py $DATA_DIR/female $DATA_DIR/dict_fb.dict $WORKDIR/pts_in/fb || exit 1
fi

if [ $STAGE -le 3 ] ; then
  msg "[$0] calling pts2news script"
  (steps/pts2news.sh $WORKDIR/pts_in/fb $WORKDIR/ali_male.news   "M" || touch .fail)&
  (steps/pts2news.sh $WORKDIR/pts_in/fb $WORKDIR/ali_female.news "F" || touch .fail)&
  wait
  [ -f .fail ] && rm .fail && exit 1
fi

if [ $STAGE -le 4 ] ; then
  msg "[$0] calling news2mm script (it takes a while)"
  (steps/news2mm.sh $WORKDIR/ali_male.{news,mm}   /tmp/ali_male.model   || touch .fail)&
  (steps/news2mm.sh $WORKDIR/ali_female.{news,mm} /tmp/ali_female.model || touch .fail)&
  wait
  [ -f .fail ] && rm .fail && exit 1
fi

if [ $STAGE -le 5 ] ; then
  msg "[$0] calling mmfix script"
  steps/mmfix.py $WORKDIR/ali_male.mm   || exit 1
  steps/mmfix.py $WORKDIR/ali_female.mm || exit 1
fi

if [ $STAGE -le 6 ] ; then
  msg "[$0] calling mm2pts script"
  mkdir -p $WORKDIR/pts_out/{ds,fb}
  steps/mm2pts.py $WORKDIR/ali_male.mm \
    $WORKDIR/pts_in/{ds,fb} \
    $WORKDIR/pts_out/{ds,fb} "M" || exit 1
  steps/mm2pts.py $WORKDIR/ali_female.mm \
    $WORKDIR/pts_in/{ds,fb} \
    $WORKDIR/pts_out/{ds,fb} "F" || exit 1
  utils/assert_equal_pts.sh  # sanity check. thanks, João
fi

if [ $STAGE -le 7 ] ; then
  msg "[$0] calling ptsunfold script"
  steps/ptsunfold.py $WORKDIR/pts_out/fb || exit 1
fi

msg "[$0] success!!"
