#!/usr/bin/env bash
#
# author: feb 2021
# cassio batista - https://cassota.gitlab.io

. ../env.sh || exit 1

WORKDIR=workspace
FB_PTSDIR=../../ds2fb/workspace/pts_out/fb

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
MIN_STAGE=1
MAX_STAGE=6
STAGE=$MIN_STAGE
while true ; do
  case $1 in
    -s | --stage) STAGE=$2; shift ;;
    -r | --reset) echo "$0: removing $WORKDIR" && rm -rf $WORKDIR; shift ;;
    *) break ;;
  esac
done

# XXX this is probably gonna be a problem under a docker container
if [ -z $CONDA_PREFIX ] ; then
  echo "$0: warning: it is advised to install things under a conda venv."
  echo "  aborting."
  exit 1
fi

# sanity check
if [ $STAGE -lt $MIN_STAGE ] || [ $STAGE -gt $MAX_STAGE ] ; then
  echo "$0: STAGE flag outta bounds: [$MIN_STAGE, $MAX_STAGE]"
  exit 1
elif [ ! -d $FB_PTSDIR ] ; then
  echo "$0: have you run 'ds2fb' scripts? fb pts files couldn't be found: '$FB_PTSDIR'"
fi

if [ $STAGE -le 1 ] ; then
  msg "[$0] calling MFA aligner script"
  mkdir -p $WORKDIR/tg
  steps/align.sh $DATA_DIR/male   ../dict_mfa.dict $WORKDIR/tg || exit 1
  steps/align.sh $DATA_DIR/female ../dict_mfa.dict $WORKDIR/tg || exit 1
fi

if [ $STAGE -le 2 ] ; then
  msg "[$0] calling tg2pts scripts"
  mkdir -p $WORKDIR/pts_in/{mfa,fb}
  steps/tg2pts.sh $WORKDIR/tg $WORKDIR/pts_in/mfa || exit 1
  ln -rsf $FB_PTSDIR/*.pts    $WORKDIR/pts_in/fb  || exit 1
fi

if [ $STAGE -le 3 ] ; then
  msg "[$0] calling pts2news script"
  steps/pts2news.sh $WORKDIR/pts_in/{mfa,fb} "M" $WORKDIR/ali_male.news   || exit 1
  steps/pts2news.sh $WORKDIR/pts_in/{mfa,fb} "F" $WORKDIR/ali_female.news || exit 1
fi

if [ $STAGE -le 4 ] ; then
  msg "[$0] calling news2mm script (it takes a while)"
  rm -f .fail
  (steps/news2mm.sh $WORKDIR/ali_male.{news,mm}   /tmp/ali_male.model   || touch .fail)&
  (steps/news2mm.sh $WORKDIR/ali_female.{news,mm} /tmp/ali_female.model || touch .fail)&
  wait
  [ -f .fail ] && echo "$0: there's something wrong" && exit 1
  rm -f .fail
fi

if [ $STAGE -le 5 ] ; then
  msg "[$0] calling mm2pts script"
  mkdir -p $WORKDIR/pts_out/{mfa,fb}
  steps/mm2pts.py \
    $WORKDIR/ali_male.mm \
    $WORKDIR/pts_in/{mfa,fb} \
    $WORKDIR/pts_out/{mfa,fb} "M" || exit 1
  steps/mm2pts.py \
    $WORKDIR/ali_female.mm \
    $WORKDIR/pts_in/{mfa,fb} \
    $WORKDIR/pts_out/{mfa,fb} "F" || exit 1
  utils/assert_equal_pts.sh $WORKDIR/pts_out  # sanity check. thanks, João
fi

if [ $STAGE -le 6 ] ; then
  msg "[$0] calling ptsunfold script"
  steps/ptsunfold.py $WORKDIR/pts_out/fb/ || exit 1
fi

msg "[$0] success!"
