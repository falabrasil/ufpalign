#!/usr/bin/env bash
#
# author: apr 2021
# cassio batista - https://cassota.gitlab.io
# last update: oct 2021

function log { echo -e "\e[$(shuf -i 91-96 -n 1)m[$(date +'%F %T')] $1\e[0m" ; }

if [ $# -ne 4 ] ; then
  echo "usage: $0 <kaldi-root> <wav-file> <txt-file> <am-tag>"
  echo "  <kaldi-root> is a dir where Kaldi has been previously installed"
  echo "  <wav-file> is the audio input file"
  echo "  <txt-file> is the transcription input file"
  echo "  <am-tag> is the tag corresponding to the acoustic model"
  echo
  echo "  e.g.: $0 $HOME/kaldi demo/audio.wav demo/trans.txt tdnn"
  echo
  echo "  valid am tags: mono, tri1, tri2, tri3, tdnn"
  exit 1
fi

local/check_deps.sh || exit 1

kaldi_root=$(readlink -f $1)
wav_file=$(readlink -f $2)
txt_file=$(readlink -f $3)
am_tag=$4

[ ! -d "$kaldi_root/egs" ] && \
  echo "$0: error: bad kaldi root dir: '$kaldi_root'" && exit 1
for f in $wav_file $txt_file ; do
  [ ! -f "$wav_file" ] && echo "$0: error: file '$f' does not exist" && exit 1
done
# https://stackoverflow.com/questions/12454731/meaning-of-operator-in-shell-script
[[ "$am_tag" =~ ("mono"|"tri"[1-3]|"tdnn") ]] || \
  { echo "$0: error: bad acoustic model tag '$am_tag'" && exit 1 ; }

egs_dir=$kaldi_root/egs/UFPAlign/s5
rm -rf $egs_dir/data $egs_dir/dict  # safety?
mkdir -p $egs_dir/data/local || exit 1

cp -r conf dict local $egs_dir
ln -rsf $kaldi_root/egs/wsj/s5/{steps,utils,path.sh} $egs_dir

########################################
### kaldi-like scripting starts here ###
########################################
cd $egs_dir

. path.sh

# download models
log "$0: downloading models"
local/download_models.sh exp || exit 1

# prepare data
log "$0: preparing data"
mkdir -p data/alignme || exit 1
utt_id=$(basename $wav_file | sed 's/\.wav//g')
echo "$utt_id $wav_file" > data/alignme/wav.scp
echo "$utt_id $(cat $txt_file)" > data/alignme/text
echo "$utt_id $utt_id" > data/alignme/utt2spk
utils/utt2spk_to_spk2utt.pl data/alignme/utt2spk > data/alignme/spk2utt || exit 1

# extend lexicon & lang
log "$0: extending lexicon and lang"
local/ext_lexsyl.sh $txt_file dict/{lexicon,syllables}.txt || exit 1
utils/prepare_lang.sh dict "<UNK>" data/local/lang data/lang || exit 1

# extract mfcc features
log "$0: extracting mfccs"
if [[ "$am_tag" =~ ("mono"|"tri"[1-3]) ]] ; then
  conf=conf/mfcc.conf  # low resolution features, 13 MFCCs
elif [[ "$am_tag" == "tdnn" ]] ; then
  conf=conf/mfcc_hires.conf # high resolution features, 40 MFCCs
fi
steps/make_mfcc.sh --nj 1 --mfcc-config $conf data/alignme || exit 1
steps/compute_cmvn_stats.sh data/alignme || exit 1
utils/fix_data_dir.sh data/alignme || exit 1

# extract ivector features (for tdnn model only)
if [[ "$am_tag" == "tdnn" ]] ; then
  log "$0: extracting ivectors"
  steps/online/nnet2/extract_ivectors_online.sh --nj 1 \
    data/alignme exp/nnet3_online_cmn/extractor/exp/model data/alignme/ivector_hires
fi

# align
log "$0: aligning"
if [[ "$am_tag" =~ ("mono"|"tri"[1-3]) ]] ; then
  steps/align_si.sh --nj 1 \
    data/alignme data/lang exp/$am_tag/exp/model data/alignme_ali
elif [[ "$am_tag" == "tdnn" ]] ; then
  steps/nnet3/align.sh --nj 1 --use-gpu false \
    --online-ivector-dir data/alignme/ivector_hires \
    --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
    data/alignme data/lang exp/chain_online_cmn/tdnn1k_sp/exp/model data/alignme_ali
fi

# create phoneids.ctm
log "$0: creating ctm"
for ali in data/alignme_ali/ali.*.gz ; do
  if [[ "$am_tag" =~ ("mono"|"tri"[1-3]) ]] ; then
    ali-to-phones --ctm-output exp/$am_tag/exp/model/final.mdl \
      ark:"gunzip -c $ali |" - > ${ali%.gz}.ctm
  elif [[ "$am_tag" == "tdnn" ]] ; then
    ali-to-phones --frame-shift="0.03" --ctm-output \
      exp/chain_online_cmn/tdnn1k_sp/exp/model/final.mdl \
      ark:"gunzip -c $ali |" - > ${ali%.gz}.ctm
  fi
done
cat data/alignme_ali/*.ctm > data/$am_tag.phoneids.ctm

# create graphemes.ctm
steps/get_train_ctm.sh data/alignme data/lang data/alignme_ali data/ctm_tmp || exit 1
cat data/ctm_tmp/ctm > data/$am_tag.graphemes.ctm || exit 1

# ctm 2 textgrid
log "$0: creating textgrid"
local/ctm2tg.py \
  data/$am_tag.{graphemes,phoneids}.ctm \
  dict/{lexicon,syllphones}.txt \
  data/tg || exit 1

cd - > /dev/null

log "$0: success!"
