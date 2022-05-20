#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

WORKDIR=workspace
KALDI_PROJ_DIR=/mnt/ext/git-all/kaldi/egs/bracis2020/s5
UFPALIGN_PLUGIN_DIR=/mnt/ext/Downloads/plugin_ufpalign-2.0/UFPAlign

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
  echo "[$0] calling setup env script" | lolcat
  steps/setup_env.sh $KALDI_PROJ_DIR $UFPALIGN_PLUGIN_DIR || exit 1
fi

if [ $STAGE -le 1 ] ; then
  echo "[$0] calling lang ext script" | lolcat
  steps/lang_ext.sh $KALDI_PROJ_DIR $UFPALIGN_PLUGIN_DIR ../../dict_fb.dict || exit 1
fi

if [ $STAGE -le 2 ] ; then
  echo "[$0] calling data preparation script" | lolcat
  find ../../{male,female} -name "*.wav" | \
    xargs readlink -f | sort | sed 's/\.wav//g' > filelist.tmp
  steps/data_prep.sh $KALDI_PROJ_DIR filelist.tmp || exit 1
  rm filelist.tmp
fi

if [ $STAGE -le 3 ] ; then
  echo "[$0] calling mfcc + cmvn script" | lolcat
  steps/make_mfcc.sh $KALDI_PROJ_DIR || exit 1
fi

exit 0
################################
### align routines start here
################################

if [ $STAGE -le 4 ] ; then
  echo "[$0] calling gmm mono alignment script" | lolcat
  mkdir -p $WORKDIR/ctm/mono
  steps/align_si.sh $KALDI_PROJ_DIR "mono" || exit 1
  steps/create_ctm.sh $KALDI_PROJ_DIR "mono" $WORKDIR/ctm/mono
fi

if [ $STAGE -le 5 ] ; then
  echo "[$0] calling gmm tri-Δ+ΔΔ alignment script" | lolcat
  mkdir -p $WORKDIR/ctm/tri1
  steps/align_si.sh $KALDI_PROJ_DIR "tri1" || exit 1
  steps/create_ctm.sh $KALDI_PROJ_DIR "tri1" $WORKDIR/ctm/tri1
fi

if [ $STAGE -le 6 ] ; then
  echo "[$0] calling gmm tri-lda-mllt alignment script" | lolcat
  mkdir -p $WORKDIR/ctm/tri2
  steps/align_fmllr.sh $KALDI_PROJ_DIR "tri2" || exit 1
  steps/create_ctm.sh $KALDI_PROJ_DIR "tri2" $WORKDIR/ctm/tri2
fi

if [ $STAGE -le 7 ] ; then
  echo "[$0] calling gmm tri-sat alignment script" | lolcat
  mkdir -p $WORKDIR/ctm/tri3
  steps/align_fmllr.sh $KALDI_PROJ_DIR "tri3" || exit 1
  steps/create_ctm.sh $KALDI_PROJ_DIR "tri3" $WORKDIR/ctm/tri3
fi

if [ $STAGE -le 8 ] ; then
  echo "[$0] calling nnet3 alignment script" | lolcat
  mkdir -p $WORKDIR/ctm/dnn
  steps/align_dnn.sh $KALDI_PROJ_DIR || exit 1
  steps/create_ctm.sh $KALDI_PROJ_DIR "dnn" $WORKDIR/ctm/dnn
fi

################################
### align routines stop here
################################

if [ $STAGE -le 9 ] ; then
  mkdir -p $WORKDIR/pts
  echo "[$0] calling ctm2pts script" | lolcat
  steps/ctm2pts.py $KALDI_PROJ_DIR $WORKDIR/ctm $WORKDIR/pts || exit 1
fi

echo "[$0] success!" | lolcat -ai -d 36
