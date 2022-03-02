#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

. env.sh || exit 1

WORKDIR=workspace
MODEL_EGS_DIR=$HOME/git-all/kaldi/egs/21_eurasip/s5
DUMMY_EGS_DIR=$HOME/git-all/kaldi/egs/21_dumbdummy/s5

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
MIN_STAGE=0
MAX_STAGE=9
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

if [ $STAGE -le 0 ] ; then
  msg "[$0] calling setup environment script"
  steps/setup_env.sh $MODEL_EGS_DIR $DUMMY_EGS_DIR || exit 1
fi

if [ $STAGE -le 1 ] ; then
  msg "[$0] calling lang ext script"
  steps/lang_ext.sh $DUMMY_EGS_DIR $DATA_DIR/dict_fb.dict || exit 1
fi

if [ $STAGE -le 2 ] ; then
  msg "[$0] calling data preparation script"
  find $DATA_DIR/{male,female} -name "*.wav" | \
    xargs readlink -f | sort | sed 's/\.wav//g' > filelist.tmp
  steps/data_prep.sh $DUMMY_EGS_DIR filelist.tmp || exit 1
  rm filelist.tmp
fi

if [ $STAGE -le 3 ] ; then
  msg "[$0] calling mfcc + cmvn"
  steps/make_mfcc.sh $DUMMY_EGS_DIR || exit 1
fi

################################
### align routines start here
################################

if [ $STAGE -le 4 ] ; then
  msg "[$0] calling gmm mono alignment script"
  am_tag="mono"
  mkdir -p $WORKDIR/{ctm,pts}/$am_tag
  steps/align.sh      $DUMMY_EGS_DIR $am_tag || exit 1
  steps/create_ctm.sh $DUMMY_EGS_DIR $am_tag $WORKDIR/ctm/$am_tag || exit 1
  steps/ctm2pts.py    $DUMMY_EGS_DIR $WORKDIR/ctm/$am_tag $WORKDIR/pts/$am_tag || exit 1
fi

if [ $STAGE -le 5 ] ; then
  msg "[$0] calling gmm tri-Δ+ΔΔ alignment script"
  am_tag="tri1"
  mkdir -p $WORKDIR/{ctm,pts}/$am_tag
  steps/align.sh      $DUMMY_EGS_DIR $am_tag || exit 1
  steps/create_ctm.sh $DUMMY_EGS_DIR $am_tag $WORKDIR/ctm/$am_tag || exit 1
  steps/ctm2pts.py    $DUMMY_EGS_DIR $WORKDIR/ctm/$am_tag $WORKDIR/pts/$am_tag || exit 1
fi

if [ $STAGE -le 6 ] ; then
  msg "[$0] calling gmm tri-lda-mllt alignment script"
  am_tag="tri2b"
  mkdir -p $WORKDIR/{ctm,pts}/$am_tag
  steps/align.sh      $DUMMY_EGS_DIR $am_tag || exit 1
  steps/create_ctm.sh $DUMMY_EGS_DIR $am_tag $WORKDIR/ctm/$am_tag || exit 1
  steps/ctm2pts.py    $DUMMY_EGS_DIR $WORKDIR/ctm/$am_tag $WORKDIR/pts/$am_tag || exit 1
fi

if [ $STAGE -le 7 ] ; then
  msg "[$0] calling gmm tri-sat alignment script"
  am_tag="tri3b"
  mkdir -p $WORKDIR/{ctm,pts}/$am_tag
  steps/align.sh      $DUMMY_EGS_DIR $am_tag || exit 1
  steps/create_ctm.sh $DUMMY_EGS_DIR $am_tag $WORKDIR/ctm/$am_tag || exit 1
  steps/ctm2pts.py    $DUMMY_EGS_DIR $WORKDIR/ctm/$am_tag $WORKDIR/pts/$am_tag || exit 1
fi

if [ $STAGE -le 8 ] ; then
  msg "[$0] calling ivector extraction + nnet3 alignment scripts"
  am_tag="tdnn"
  mkdir -p $WORKDIR/{ctm,pts}/$am_tag
  steps/make_ivectors.sh $DUMMY_EGS_DIR || exit 1
  steps/align.sh      $DUMMY_EGS_DIR $am_tag || exit 1
  steps/create_ctm.sh $DUMMY_EGS_DIR $am_tag $WORKDIR/ctm/$am_tag
  steps/ctm2pts.py    $DUMMY_EGS_DIR $WORKDIR/ctm/$am_tag $WORKDIR/pts/$am_tag || exit 1
fi

################################
### align routines stop here
################################

msg "[$0] success!"
