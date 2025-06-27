#!/usr/bin/env bash
#
# extend lexicon: call FalaBrasil G2P tool from NLP lib to create phonetic 
# transcriptions on the fly in case there are words missing in our lexicon
#
# author: apr 2021
# Cassio T Batista - https://cassiotbatista.github.io
# last update: feb 2025

if [ $# -ne 4 ] ; then
  echo "usage: $0 <trans-file> <lex-file> <syll-file> <sp-file>"
  echo "  <trans-file> is the text transcription file"
  echo "  <lex-file> is the phonetic dict file"
  echo "  <syll-file> is the syllabic dict file"
  echo "  <sp-file> is the syllphones dict file"
  exit 1
fi

txt_file=$1
lex_file=$2
syll_file=$3
sp_file=$4

# FIXME this is freaking odd since Kaldi encourages the use use LC_ALL=C for 
# compatibility with C++-sorting defaults, but this simply doesn't work for 
# diacritics. For example, using LC_ALL the last work would be "último" or 
# some other word starting with "ú" instead of a word beginning with "z". 
# Besides, all words starting with "á" would come after "z" as well.
# Gonna keep LC_ALL=pt_BR.utf8 here until someone complains - Cassio
export LC_ALL=pt_BR.utf8
#export LC_ALL=C

rm -f *.tmp *.err
trap "rm -f *.tmp *.err" SIGINT
for word in $(cat $txt_file) ; do
  echo $word
done > wlist.tmp

# FIXME I think this routine should continue checking for *all* words not in 
# lexicon instead of aborting at the first one, because it'd cheaper to run 
# inference only over the diff (words missing in the lexicon) rather than at 
# the whole trans file
awk '{print $1}' $lex_file | python3 -c "
import sys
lex = set([ word.strip() for word in sys.stdin ])
with open('wlist.tmp') as f:
  wlist = set([ word.strip() for word in f ])
miss = set()
for word in wlist:
  if word not in lex:
    print(f'$0: warning: {word=} not in lex', file=sys.stderr)
    miss.add(word)
if len(miss) == 0:
  print('$0: info: no words missing in dict. great!', file=sys.stderr)
for m in miss:
  print(m)
" | sort > miss.tmp

echo "$0: info: extending lexicon"
java -jar $UFPALIGN_DIR/fb_nlplib.jar -g -i miss.tmp -o lex.tmp
(
  head -2 $lex_file
  (
    tail +3 $lex_file
    cat lex.tmp
  ) | sort -u | local/parse_abbrev.py
) > lex || exit 1
mv -v lex $lex_file

echo "$0: info: extending syllables"
java -jar $UFPALIGN_DIR/fb_nlplib.jar -s -i miss.tmp -o syll.tmp
sort -u $syll_file syll.tmp | local/fix_syll.py > syll || exit 1
mv -v syll $syll_file

# lastly, syllphones
echo "$0: info: extending syllphones"
local/dict2news.py \
  --m2m_lut_file sp.lut.tmp lex.tmp syll.tmp > sp.news.tmp || exit 1
$M2M_ROOT/m2m-aligner \
  --maxFn conXY \
  --maxX 4 \
  --maxY 1 \
  --inputFile sp.news.tmp \
  --outputFile sp.ali.tmp \
  --alignerIn $UFPALIGN_DIR/m2m.model
(
  head -n 1 $sp_file
  (
    tail -n +2 $sp_file
    python3 local/ali2syllphones.py < sp.ali.tmp
    cat sp.lut.tmp
  ) | sort -u | local/parse_abbrev.py
) > sp
mv sp $sp_file

# FIXME utts in \*.err are not being fixed
[ -s sp.ali.tmp.err ] && \
  echo "$0: warn: the syllables from the following words could not be " && \
  echo "properly aligned to their phonetic transcription, " && \
  echo "so they will NOT appear in the syllphones dict:" && \
  cat sp.ali.tmp.err

rm -f *.tmp *.err
echo "$0: info: success!"
