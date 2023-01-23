#!/usr/bin/env bash
#
# extend lexicon: call FalaBrasil G2P tool from NLP lib to create phonetic 
# transcriptions on the fly in case there are words missing in our lexicon
#
# author: apr 2021
# cassio batista - https://cassota.gitlab.io
# last update: jan 2023

update=false

if [ $# -ne 4 ] ; then
  echo "usage: $0 <jar-path> <trans-file> <lex-file> <syll-file>"
  echo "  <jar-path> is the path to FalaBrasil's tagger"
  echo "  <trans-file> is the text transcription file"
  echo "  <lex-file> is the phonetic dict file"
  echo "  <syll-file> is the syllabic dict file"
  exit 1
fi

jar_path=$1
txt_file=$2
lex_file=$3
syll_file=$4

# FIXME this is freaking odd since Kaldi encourages the use use LC_ALL=C for 
# compatibility with C++-sorting defaults, but this simply doesn't work for 
# diacritics. For example, using LC_ALL the last work would be "último" or 
# some other word starting with "ú" instead of a word beginning with "z". 
# Besides, all words starting with "á" would come after "z" as well.
# Gonna keep LC_ALL=pt_BR.utf8 here until someone complains - Cassio
export LC_ALL=pt_BR.utf8
#export LC_ALL=C

rm -f *.tmp
trap "rm -f *.tmp" SIGINT
for word in $(cat $txt_file) ; do
  echo $word
done > wlist.tmp

# FIXME this should be part of data.tar.gz
echo "$0: creating syllphones"
dir=$(dirname $lex_file)
java -jar $jar_path/fb_nlplib.jar -G -i wlist.tmp -o $dir/syllphones.tmp
local/parse_abbrev.py --syllphones < $dir/syllphones.tmp > $dir/syllphones.txt || exit 1

awk '{print $1}' $lex_file | python -c "
import sys
lex = []
for word in sys.stdin:
  lex.append(word.strip())
wlist = []
with open('wlist.tmp') as f:
  for word in f:
    wlist.append(word.strip())
for word in wlist:
  if word not in lex:
    print('** word \'%s\' not in lex. extending dict...' % word)
    sys.exit(1)
print('>> no words missing in dict. great!')
" && exit 0

# first lexicon
echo "$0: extending lexicon"
java -jar $jar_path/fb_nlplib.jar -g -i wlist.tmp -o dict.tmp
head -2 $lex_file > unk.tmp    # first get only unk tokens from lexicon
tail +3 $lex_file >> dict.tmp  # finally get phones from lexicon
sort -u dict.tmp -o dict.tmp
cat unk.tmp dict.tmp | local/parse_abbrev.py > $lex_file || exit 1

# then syll
echo "$0: extending syll"
java -jar $jar_path/fb_nlplib.jar -s -i wlist.tmp -o syll.tmp
cat $syll_file >> syll.tmp
sort -u syll.tmp | local/fix_syll.py > $syll_file || exit 1

rm -f *.tmp

echo "$0: creating syllphones"
utils/prepare_lang.sh data/dict "<UNK>" data/lang_tmp data/lang || exit 1
