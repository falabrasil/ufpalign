#!/usr/bin/env bash
#
# performs forced alignment on both GMM and TDNN-F 
# models using Kaldi scripts
# 
# author: jun 2021
# cassio batista - https://cassota.gitlab.io

../env.sh || exit 1

set -e
rm -rf alignme alignme_lores alignme_hires

stage=0

. path.sh
. utils/parse_options.sh

# NOTE: 'alignme' dir will be the new 'data' dir
mkdir -p alignme/local

# copy lexicon and lm files
cp -r data/local/dict alignme/local
cp -r data/local/lm   alignme/local

# TODO: Q: sort -u? A: will displace SIL & UNK
if [ $stage -le 0 ] ; then
  # extend lexicon
  msg "$0: extend lex"
  rm -fv alignme/local/dict/{lexiconp,lexiconp_silprob}.txt
  cat data/local/dict/lexicon.txt $DATA_DIR/dict_fb.dict > dict.tmp
  head -n +2 dict.tmp  > alignme/local/dict/lexicon.txt  # sil unk
  tail -n +3 dict.tmp >> alignme/local/dict/lexicon.txt  # remainder
  rm -f *.tmp

  # prep lang
  msg "$0: prep lang"
  utils/prepare_lang.sh \
    alignme/local/dict \
    "<UNK>" \
    alignme/local/lang_tmp \
    alignme/lang

  utils/validate_lang.pl --skip-determinization-check alignme/lang

  # prep data
  # FIXME this code is messy but que se foda-se
  msg "$0: prep data"
  find $DATA_DIR/{male,female} -name "*.wav" | xargs readlink -f | \
    sort | sed 's/\.wav//g' | while read line ; do
      spk_id=$(echo $line | sed 's/\// /g' | awk '{print $(NF-1)}') ;
      utt_id="${spk_id}_$(basename $line)" ;
      gender=${spk_id:0:1} ;
      echo "$utt_id $(cat $line.txt)" >> alignme/text ;
      echo "$utt_id $spk_id" >> alignme/utt2spk ;
      echo "$utt_id $line.wav" >> alignme/wav.scp ;
    done

  utils/utt2spk_to_spk2utt.pl alignme/utt2spk > alignme/spk2utt
  utils/fix_data_dir.sh alignme 
fi

# extract feats
if [ $stage -le 1 ] ; then
  utils/copy_data_dir.sh --validate-opts "--non-print" alignme alignme_lores
  utils/copy_data_dir.sh --validate-opts "--non-print" alignme alignme_hires

  msg "[$0] computing low resolution mfcc features"
  steps/make_mfcc.sh --nj 2 alignme_lores
  steps/compute_cmvn_stats.sh alignme_lores
  utils/fix_data_dir.sh alignme_lores

  msg "[$0] computing high resolution mfcc features"
  steps/make_mfcc.sh --nj 2 --mfcc-config conf/mfcc_hires.conf alignme_hires
  steps/compute_cmvn_stats.sh alignme_hires
  utils/fix_data_dir.sh alignme_hires

  msg "[$0] computing ivector features" 
  steps/online/nnet2/extract_ivectors_online.sh --nj 2 \
    alignme_hires exp/nnet3/extractor alignme/ivectors_hires
fi

echo "$0: #####################################"
echo "$0: ### align with GMM models routine ###"
echo "$0: #####################################"

if [ $stage -le 2 ] ; then
  msg "[$0] align mono"
  steps/align_si.sh --nj 2 alignme_lores alignme/lang \
    exp/mono alignme/results/mono_ali
  fblocal/ali2ctm2pts.sh mono

  msg "[$0] align tri-deltas"
  steps/align_si.sh --nj 2 alignme_lores alignme/lang \
    exp/tri1 alignme/results/tri1_ali
  fblocal/ali2ctm2pts.sh tri1

  msg "[$0] align tri-lda"
  steps/align_fmllr.sh --nj 2 alignme_lores alignme/lang \
    exp/tri2b alignme/results/tri2b_ali
  fblocal/ali2ctm2pts.sh tri2b

  msg "[$0] align tri-sat (1st)"
  steps/align_fmllr.sh --nj 2 alignme_lores alignme/lang \
    exp/tri3b alignme/results/tri3b_ali
  fblocal/ali2ctm2pts.sh tri3b

  msg "[$0] align tri-sat (2nd)"
  steps/align_fmllr.sh --nj 2 alignme_lores alignme/lang \
    exp/tri4b alignme/results/tri4b_ali
  fblocal/ali2ctm2pts.sh tri4b
fi

echo "$0: ########################################################"
echo "$0: ### align with mono-based TDNN-F mono models routine ###"
echo "$0: ########################################################"

if [ $stage -le 3 ] ; then
  # chain systems with ivector
  for am_tag in tdnn_mono_chain_delta_ivector_fs3_sp \
                tdnn_mono_chain_delta_ivector_nofs_sp \
                tdnn_mono_chain_lda_ivector_fs3_sp \
                tdnn_mono_chain_lda_ivector_nofs_sp ; do
    msg "$0: align $am_tag (mono chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false --online-ivector-dir alignme/ivectors_hires \
      --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
      alignme_hires \
      alignme/lang \
      exp/chain/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --chain true $am_tag
  done

  # chain systems with NO ivector
  for am_tag in tdnn_mono_chain_delta_noivector_fs3_sp \
                tdnn_mono_chain_delta_noivector_nofs_sp \
                tdnn_mono_chain_lda_noivector_fs3_sp \
                tdnn_mono_chain_lda_noivector_nofs_sp ; do
    msg "$0: align $am_tag (mono chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false \
      --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
      alignme_hires \
      alignme/lang \
      exp/chain/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --chain true $am_tag
  done

  # regular systems (no chain) with ivector
  for am_tag in tdnn_mono_nochain_delta_ivector_sp \
                tdnn_mono_nochain_lda_ivector_sp ; do
    msg "$0: align $am_tag (mono no chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false --online-ivector-dir alignme/ivectors_hires \
      alignme_hires \
      alignme/lang \
      exp/nnet3/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --nnet3 true $am_tag
  done

  # regular systems (no chain) with NO ivector
  for am_tag in tdnn_mono_nochain_delta_noivector_sp \
                tdnn_mono_nochain_lda_noivector_sp ; do
    msg "$0: align $am_tag (mono no chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false \
      alignme_hires \
      alignme/lang \
      exp/nnet3/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --nnet3 true $am_tag
  done
fi

echo "$0: ###################################################################"
echo "$0: ### align with trideltas-based TDNN-F tri-deltas models routine ###"
echo "$0: ###################################################################"

if [ $stage -le 4 ] ; then
  # chain systems with ivector
  for am_tag in tdnn_trideltas_chain_delta_ivector_fs3_sp \
                tdnn_trideltas_chain_delta_ivector_nofs_sp \
                tdnn_trideltas_chain_lda_ivector_fs3_sp \
                tdnn_trideltas_chain_lda_ivector_nofs_sp ; do
    msg "$0: align $am_tag (tri-deltas chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false --online-ivector-dir alignme/ivectors_hires \
      --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
      alignme_hires \
      alignme/lang \
      exp/chain/$am_tag \
      alignme/results/${am_tag}_ali && \
    fblocal/ali2ctm2pts.sh --chain true $am_tag
  done

  # chain systems with NO ivector
  for am_tag in tdnn_trideltas_chain_delta_noivector_fs3_sp \
                tdnn_trideltas_chain_delta_noivector_nofs_sp \
                tdnn_trideltas_chain_lda_noivector_fs3_sp \
                tdnn_trideltas_chain_lda_noivector_nofs_sp ; do
    msg "$0: align $am_tag (tri-deltas chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false \
      --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
      alignme_hires \
      alignme/lang \
      exp/chain/$am_tag \
      alignme/results/${am_tag}_ali && \
    fblocal/ali2ctm2pts.sh --chain true $am_tag
  done

  # regular systems (no chain) with ivector
  for am_tag in tdnn_trideltas_nochain_delta_ivector_sp \
                tdnn_trideltas_nochain_lda_ivector_sp ; do
    msg "$0: align $am_tag (tri-deltas no chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false --online-ivector-dir alignme/ivectors_hires \
      alignme_hires \
      alignme/lang \
      exp/nnet3/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --nnet3 true $am_tag
  done

  # regular systems (no chain) with NO ivector
  for am_tag in tdnn_trideltas_nochain_delta_noivector_sp \
                tdnn_trideltas_nochain_lda_noivector_sp ; do
    msg "$0: align $am_tag (tri-deltas no chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false \
      alignme_hires \
      alignme/lang \
      exp/nnet3/$am_tag \
      alignme/results/${am_tag}_ali && \
    fblocal/ali2ctm2pts.sh --nnet3 true $am_tag
  done
fi

echo "$0: ################################################"
echo "$0: ### align with TDNN-F tri-sat models routine ###"
echo "$0: ################################################"

if [ $stage -le 5 ] ; then
  # chain systems with ivector
  for am_tag in tdnn_trisat_chain_delta_ivector_fs3_sp \
                tdnn_trisat_chain_delta_ivector_nofs_sp \
                tdnn_trisat_chain_lda_ivector_fs3_sp \
                tdnn_trisat_chain_lda_ivector_nofs_sp ; do
    msg "$0: align $am_tag (tri-sat chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false --online-ivector-dir alignme/ivectors_hires \
      --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
      alignme_hires \
      alignme/lang \
      exp/chain/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --chain true $am_tag
  done

  # chain systems with NO ivector
  for am_tag in tdnn_trisat_chain_delta_noivector_fs3_sp \
                tdnn_trisat_chain_delta_noivector_nofs_sp \
                tdnn_trisat_chain_lda_noivector_fs3_sp \
                tdnn_trisat_chain_lda_noivector_nofs_sp ; do
    msg "$0: align $am_tag (tri-sat chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false \
      --scale-opts '--transition-scale=1.0 --acoustic-scale=1.0 --self-loop-scale=1.0' \
      alignme_hires \
      alignme/lang \
      exp/chain/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --chain true $am_tag
  done

  # regular systems (no chain) with ivector
  for am_tag in tdnn_trisat_nochain_delta_ivector_sp \
                tdnn_trisat_nochain_lda_ivector_sp ; do
    msg "$0: align $am_tag (tri-sat no chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false --online-ivector-dir alignme/ivectors_hires \
      alignme_hires \
      alignme/lang \
      exp/nnet3/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --nnet3 true $am_tag
  done

  # regular systems (no chain) with no ivector
  for am_tag in tdnn_trisat_nochain_delta_noivector_sp \
                tdnn_trisat_nochain_lda_noivector_sp ; do
    msg "$0: align $am_tag (tri-sat no chain)"
    steps/nnet3/align.sh --nj 2 --use-gpu false \
      alignme_hires \
      alignme/lang \
      exp/nnet3/$am_tag \
      alignme/results/${am_tag}_ali
    fblocal/ali2ctm2pts.sh --nnet3 true $am_tag
  done
fi

msg "$0: success!"
