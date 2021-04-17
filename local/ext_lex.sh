#!/usr/bin/env bash
#
# extend lexicon: call FalaBrasil G2P tool from NLP lib to create phonetic 
# transcriptions on the fly in case there are words missing in our lexicon
#
# author: apr 2021
# cassio batista - https://cassota.gitlab.io

if [ $# -ne 2 ] ; then
  echo "usage: $0 <trans-file> <lex-file>"
  echo "  <trans-file> is the text transcription file"
  echo "  <lex-file> is the phonetic dict file"
  exit 1
fi

txt_file=$1
lex_file=$2

rm -f *.tmp
trap "rm -f *.tmp" SIGINT
for word in $(cat $txt_file) ; do
  echo $word >> wlist.tmp
done

java -jar fb_nlplib.jar -g -i wlist.tmp -o dict.tmp
head -2 $lex_file > sil.tmp    # get unk tokens from lexicon
tail +3 $lex_file >> dict.tmp  # get phones from lexicon
sort -u dict.tmp -o dict.tmp || exit 1
cat sil.tmp dict.tmp > $lex_file || exit 1

rm -f *.tmp
