#!/usr/bin/env bash
#
# extend lexicon: call FalaBrasil G2P tool from NLP lib to create phonetic 
# transcriptions on the fly in case there are words missing in our lexicon
#
# author: apr 2021
# Cassio T Batista - https://cassiotbatista.github.io
# last update: feb 2025


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

# FIXME I think this routine should continue checking for *all* words not in 
# lexicon instead of aborting at the first one, because it'd cheaper to run 
# inference only over the diff (words missing in the lexicon) rather than at 
# the whole trans file
awk '{print $1}' $lex_file | python -c "
import sys
lex = [ word.strip() for word in sys.stdin ]
with open('wlist.tmp') as f:
  wlist = [ word.strip() for word in f ]
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

# lastly, syllphones
# TODO upload m2m.model to GDrive, fetch it and place it under `/opt/` dir 
# alongside the others at installation time.

rm -f *.tmp
