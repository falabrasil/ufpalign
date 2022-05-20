#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 2 ; then
  echo "usage: $0 <kaldi-egs-dir> <dict>"
  exit 1
fi

proj_dir=$1
dict=$2

# extend lexicon
dict_dir=$proj_dir/data/local/dict
rm -f $dict_dir/lexiconp.txt
rm -f $dict_dir/lexiconp_silprob.txt

tmp_dict=$(mktemp --suffix='_dict')
cat $proj_dir/data/local/dict/lexicon.txt $dict > $tmp_dict || exit 1
head -n +2 $tmp_dict               >  $proj_dir/data/local/dict/lexicon.txt  # just sil and unk
tail -n +3 $tmp_dict | sort | uniq >> $proj_dir/data/local/dict/lexicon.txt  # escape sil and unk
rm -f $tmp_dict

cd $proj_dir

. path.sh

# prepare lang
utils/prepare_lang.sh \
    data/local/dict \
    "<UNK>" \
    data/local/lang_tmp \
    data/lang || exit 1

# recompile G.fst (lm)
gunzip -c data/local/lm/lm_tglarge.arpa.gz |
    arpa2fst --disambig-symbol=#0 \
             --read-symbol-table=data/lang/words.txt - data/lang/G.fst || exit 1

utils/validate_lang.pl --skip-determinization-check data/lang || exit 1

cd - > /dev/null
