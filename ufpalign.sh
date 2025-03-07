#!/usr/bin/env bash
#
# author: apr 2021
# Cassio T Batista - https://cassiotbatista.github.io
# last update: feb 2025


UFPALIGN_DIR=/opt/UFPAlign
beam=10
retry_beam=40

function log { echo -e "\e[$(shuf -i 91-96 -n 1)m[$(date +'%F %T')] $1\e[0m" ; }

. utils/parse_options.sh || exit 1

if [ $# -ne 3 ] ; then
  echo "usage: $0 [options] <wav-file> <txt-file> <am-tag>"
  echo "  <wav-file> is the audio input file"
  echo "  <txt-file> is the transcription input file"
  echo "  <am-tag> is the tag corresponding to the acoustic model"
  echo
  echo "  e.g.: KALDI_ROOT=$HOME/kaldi $0 demo/audio.wav demo/trans.txt tdnn"
  echo
  echo "  valid am tags: mono, tri1, tri2b, tri3b, tdnn"
  exit 1
fi

[ ! -d $UFPALIGN_DIR ] && \
  sudo mkdir -pv $UFPALIGN_DIR && \
  sudo chown -Rv $(whoami):$(whoami) $UFPALIGN_DIR

# check dependencies
KALDI_ROOT=$KALDI_ROOT \
M2M_ROOT=$M2M_ROOT \
  utils/check_dependencies.sh || exit 1

wav_file=$(readlink -f $1)
txt_file=$(readlink -f $2)
am_tag=$3

# sanity check
for f in $wav_file $txt_file ; do
  [ ! -f "$wav_file" ] && echo "$0: error: file '$f' does not exist" && exit 1
done
# https://stackoverflow.com/questions/12454731/meaning-of-operator-in-shell-script
[[ "$am_tag" =~ ("mono"|"tri1"|"tri"[2-3]"b"|"tdnn") ]] || \
  { echo "$0: error: bad acoustic model tag '$am_tag'" && exit 1 ; }

# fetch resources: models, taggers, and dicts
log "$0: downloading models"
utils/download_model.sh "data" $UFPALIGN_DIR || exit 1
utils/download_model.sh "m2m" $UFPALIGN_DIR || exit 1
utils/download_model.sh $am_tag $UFPALIGN_DIR || exit 1
[[ "$am_tag" == "tdnn" ]] && \
  { utils/download_model.sh "ie" $UFPALIGN_DIR || exit 1 ; }

egs_dir=$KALDI_ROOT/egs/UFPAlign/s5
rm -rf $egs_dir/data  # safety?
mkdir -p $egs_dir/data/local || exit 1

cp -r conf local $egs_dir
cp -rv $UFPALIGN_DIR/data $egs_dir
ln -rsf $KALDI_ROOT/egs/wsj/s5/{steps,utils,path.sh} $egs_dir

########################################
### kaldi-like scripting starts here ###
########################################
cd $egs_dir

. path.sh

# prepare data
log "$0: preparing data"
mkdir -p data/alignme || exit 1
utt_id=$(basename $wav_file | sed 's/\.wav//g')
echo "$utt_id $wav_file" > data/alignme/wav.scp
echo "$utt_id $(cat $txt_file)" > data/alignme/text
echo "$utt_id $utt_id" > data/alignme/utt2spk
utils/utt2spk_to_spk2utt.pl \
  data/alignme/utt2spk > data/alignme/spk2utt || exit 1

# extend lexicon & lang
log "$0: extending lexicon and lang"
UFPALIGN_DIR=$UFPALIGN_DIR \
M2M_ROOT=$M2M_ROOT \
  local/ext_dict.sh \
    $txt_file data/dict/{lexicon,syllables,syllphones}.txt || exit 1

# FIXME I should *NOT* be rebuilding the FSTs graphs here but Kaldi simply
# started complaining in 2025??? - Cassio
log "$0: rebuilding lang (I've been forced to, sorry)"
utils/prepare_lang.sh data/dict "<UNK>" data/lang_tmp data/lang || exit 1

# extract mfcc features: low resolution for gmm, high for tdnn
log "$0: extracting mfccs"
conf=conf/mfcc.conf 
[[ "$am_tag" == "tdnn" ]] && conf=conf/mfcc_hires.conf
steps/make_mfcc.sh --nj 1 --mfcc-config $conf data/alignme || exit 1
steps/compute_cmvn_stats.sh data/alignme || exit 1
utils/fix_data_dir.sh data/alignme || exit 1

# extract ivector features (for tdnn model only)
if [[ "$am_tag" == "tdnn" ]] ; then
  log "$0: extracting ivectors"
  steps/online/nnet2/extract_ivectors_online.sh --nj 1 \
    data/alignme $UFPALIGN_DIR/ie data/alignme/ivector_hires || exit 1
fi

# align
log "$0: aligning"
if [[ "$am_tag" =~ ("mono"|"tri1"|"tri"[2-3]"b") ]] ; then
  steps/align_si.sh --nj 1 --beam $beam --retry-beam $retry_beam \
    data/alignme data/lang $UFPALIGN_DIR/$am_tag data/alignme_ali || exit 1
elif [[ "$am_tag" == "tdnn" ]] ; then
  steps/nnet3/align.sh --nj 1 --use-gpu false \
    --beam $beam --retry-beam $retry_beam \
    --online-ivector-dir data/alignme/ivector_hires \
    --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
    data/alignme data/lang $UFPALIGN_DIR/$am_tag data/alignme_ali || exit 1
fi

# create ctm
log "$0: creating ctm"
frame_shift_opts=
[[ "$am_tag" == "tdnn" ]] && frame_shift_opts="--frame-shift='0.03'"
for ali in data/alignme_ali/ali.*.gz ; do
  # phonemes
  ali-to-phones $frame_shift_opts --ctm-output=true \
    $UFPALIGN_DIR/$am_tag/final.mdl \
    ark:"gunzip -c $ali |" \
    - | \
    tee ${ali%.gz}_p.ctm | \
    utils/int2sym.pl -f 5 data/lang/phones.txt | \
    local/strip.py > data/$am_tag.phonemes.ctm
  # graphemes
  linear-to-nbest \
    "ark:gunzip -c $ali |" \
    "ark:utils/sym2int.pl --map-oov 2 -f 2- data/lang/words.txt < data/alignme/text |" \
    '' \
    '' \
    ark:- | \
  lattice-align-words \
    data/lang/phones/word_boundary.int \
    $UFPALIGN_DIR/$am_tag/final.mdl \
    ark:- \
    ark:- | \
  nbest-to-ctm $frame_shift_opts --precision=3 --print-silence=true \
    ark:- \
    - | \
  tee ${ali%.gz}_w.ctm | \
  utils/int2sym.pl -f 5 data/lang/words.txt | \
  local/strip.py > data/$am_tag.graphemes.ctm
done

# create textgrid
log "$0: creating textgrid"
local/ctm2tg.py \
  --graphemes-ctm-file $PWD/data/$am_tag.graphemes.ctm \
  --phonemes-ctm-file $PWD/data/$am_tag.phonemes.ctm \
  --phonetic-dictionary $PWD/data/dict/lexicon.txt \
  --syllphones-dictionary $PWD/data/dict/syllphones.txt \
  --output-dir $PWD/data/tg || exit 1
  #--debug \

cd - > /dev/null

log "$0: success!"
