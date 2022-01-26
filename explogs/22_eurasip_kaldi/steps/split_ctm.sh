#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 3 ; then
  echo "usage: $0 <dataset-dir> <phones.txt> <ctm-split-out-dir>"
  exit 1
fi

data_dir=$1
phones_file=$2
out_dir=$3

[ ! -d $data_dir ] && echo "[$0] dir '$data_dir' does not exist" && exit 1

for ctm in $(find $data_dir -name "*.phoneids.ctm") ; do
  am_tag=$(basename $ctm | cut -d '.' -f 1)
  mkdir -p $out_dir/$am_tag || exit 1
  while read line ; do
    utt_id=$(echo $line | awk '{print $1}')
    out_file=$(echo $utt_id | cut -d '_' -f 2).ctm
    echo -ne "\r[$0] extracting $out_file from phoneids.ctm"
    grep $utt_id $ctm > $out_dir/$am_tag/$out_file
  done < $ctm
done
