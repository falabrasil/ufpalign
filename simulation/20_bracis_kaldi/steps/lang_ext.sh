#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 3 ; then
  echo "usage: $0 <kaldi-egs-dir> <ufpalign-plugin-dir> <dict>"
  exit 1
fi

proj_dir=$1
plug_dir=$2
dict=$3

# extend lexicon
tmp_dict=$(mktemp --suffix='_dict')
cp -r "$plug_dir/data_original/local" "$proj_dir/data"
cat $dict $proj_dir/data/local/dict/lexicon.txt > $tmp_dict
head -n 2 $tmp_dict > $proj_dir/data/local/dict/lexicon.txt  # just sil and unk
tail -n +3 $tmp_dict | sort | uniq > $proj_dir/data/local/dict/lexicon.txt  # escape sil and unk
rm -f $tmp_dict

cd $proj_dir

. path.sh

# prepare lang
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang || exit 1

# recompile G.fst (lm)
arpa2fst --disambig-symbol=#0 --read-symbol-table=data/lang/words.txt \
  data/local/tmp/lm.arpa data/lang/G.fst || exit 1

cd - > /dev/null
