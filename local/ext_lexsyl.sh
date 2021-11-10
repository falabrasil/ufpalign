#!/usr/bin/env bash
#
# extend lexicon: call FalaBrasil G2P tool from NLP lib to create phonetic 
# transcriptions on the fly in case there are words missing in our lexicon
#
# author: apr 2021
# cassio batista - https://cassota.gitlab.io

if [ $# -ne 3 ] ; then
  echo "usage: $0 <trans-file> <lex-file> <syll-file>"
  echo "  <trans-file> is the text transcription file"
  echo "  <lex-file> is the phonetic dict file"
  echo "  <syll-file> is the syllabic dict file"
  exit 1
fi

txt_file=$1
lex_file=$2
syll_file=$3

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
  echo $word >> wlist.tmp
done

# first lexicon
echo "$0: extending lexicon"
java -jar fb_nlplib.jar -g -i wlist.tmp -o dict.tmp
head -2 $lex_file > unk.tmp    # first get only unk tokens from lexicon
tail +3 $lex_file >> dict.tmp  # finally get phones from lexicon
sort -u dict.tmp -o dict.tmp
cat unk.tmp dict.tmp > $lex_file || exit 1

# then syll
echo "$0: extending syll"
java -jar fb_nlplib.jar -s -i wlist.tmp -o syll.tmp
cat $syll_file >> syll.tmp
sort -u syll.tmp > $syll_file || exit 1

echo "$0: creating syllphones"
java -jar fb_nlplib.jar -G -i wlist.tmp -o $(dirname $lex_file)/syllphones.txt

rm -f *.tmp
