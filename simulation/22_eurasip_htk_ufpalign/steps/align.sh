#!/usr/bin/env bash
# convert wav + txt to TextGrid
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

. env.sh || exit 1

FMT='%H:%M:%S'


if test $# -ne 4 ; then
  echo "usage: $0 <corpora-in-dir> <dict-in-file> <rec-out-dir> <nj>"
  echo "  <corpora-in-dir> is a folder containing both wav and txt files"
  echo "  <dict-in-file> is the phonetic dictionary input file"
  echo "  <rec-out-dir> is a dir to store the aligner's .rec output file"
  echo "  <nj> is the number of parallel jobs"
  exit 1
fi

data_dir=$1
dict=$(mktemp --suffix='_dict')  # $2
rec_dir=$3
nj=$4

echo -e "<s>\tsil"     > $dict
echo -e "</s>\tsil"   >> $dict
echo -e "<unk>\tsil"  >> $dict
cat $2 >> $dict
echo -e "sil\tsil"    >> $dict

for wav in $data_dir/*.wav ; do
  wav=$(readlink -f $wav)
  txt=$(echo $wav | sed 's/\.wav/\.txt/g')
  lab=$(echo $wav | sed 's/\.wav/\.lab/g')  # aux input
  rec=$(echo $wav | sed 's/\.wav/\.rec/g')  # proper output

  rm -f $lab
  for word in $(cat $txt) ; do
      echo $word >> $lab
  done

  echo -ne "\r[$0 $(date +"$FMT")] $(basename $wav) + $(basename $txt)"
  ( $HVITE_BIN \
      -t 1 \
      -b sil \
      -a \
      -m \
      -C $UFPALIGN_DIR/confs/comp.cfg \
      -H $UFPALIGN_DIR/model/hmmdefs \
      -t 250.0 \
      $dict \
      $UFPALIGN_DIR/util/phones.list \
      $wav;
    mv $rec $rec_dir 2>/dev/null || echo "[$0 $(date "$FMT")] **$wav fail";
    rm -f $lab;
  ) &
  # ensure we don't supperpass the specified amount of parallel jobs
  while [ $(wc -w <<< $(jobs -p)) -eq $nj ] ; do
    sleep 1
  done
done
wait
echo
rm -f $dict
