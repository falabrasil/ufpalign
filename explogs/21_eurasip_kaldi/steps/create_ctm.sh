#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 3 ; then
  echo "usage: $0 <kaldi-egs-dir> <am-tag> <ctm-out-dir>"
  exit 1
fi

proj_dir=$1
am_tag=$2  # mono, tri1, tri2, tri3
out_dir=$(readlink -f $3)

cd $proj_dir

. path.sh

# creates phoneids.ctm
for i in results/${am_tag}_ali_alignme/ali.*.gz ; do
  if [ "$am_tag" == "tdnn" ] ; then
    ali-to-phones --frame-shift="0.03" --ctm-output exp/$am_tag/final.mdl \
      ark:"gunzip -c $i|" - > ${i%.gz}.ctm
  else
    ali-to-phones --ctm-output exp/$am_tag/final.mdl \
      ark:"gunzip -c $i|" - > ${i%.gz}.ctm
  fi
done
cat results/${am_tag}_ali_alignme/*.ctm > $out_dir/$am_tag.phoneids.CTM  # upper case on purpose

# separates phoneids by file
# TODO watch for slowness
while read line ; do
  utt_id=$(echo $line | awk '{print $1}')
  out_file=$(echo $utt_id | cut -d '_' -f 2).ctm
  echo -ne "\r[$0] extracting $out_file from phoneids.ctm"
  grep $utt_id $out_dir/$am_tag.phoneids.CTM > $out_dir/$out_file
done < data/alignme/utt2spk
echo

# creates grapheme.ctm
steps/get_train_ctm.sh data/alignme data/lang results/${am_tag}_ali_alignme exp/ctm_tmp
cat exp/ctm_tmp/ctm > $out_dir/$am_tag.graphemes.CTM
rm -rf exp/ctm_tmp

cd - > /dev/null
