#!/usr/bin/env bash
#
# author: jan 2021
# cassio batista - https://cassota.gitlab.io

EASYALIGN_PATH=$HOME/Downloads/plugin_easyalign

## easyalign's lang/lang.Table file
# lang     g2p  align   sp       tk
# fra      1    1       16000    MFCC_0_D_A
# en       1    0                MFCC_0_D_A
# spa      1    1       44100    MFCC_0_D_A
# hb       0    1                MFCC_0_D_A
# nl       0    1                MFCC_0_D_A
# porbra   1    1       16000    MFCC_0_D_N_Z   # <-- Here I am rocking like a-
# slk      1    1       22050    MFCC_0_D_A
# sw       1    0                MFCC_0_D_A
# nan      0    1       16000    MFCC_0_D_A

## easyalign's align_sound.praat file
# spfreqref   = Get value... 'langcol' sp   # L80
# targetkind$ = Get value... 'langcol' tk   # L81
# srcrateref=10000000/spfreqref             # L86

SP_FREQ_REF=16000
TARGET_KIND=MFCC_0_D_N_Z
SRC_RATE_REF=$(python -c "print(10000000/$SP_FREQ_REF)")

if test $# -ne 3 ; then
  echo "usage: $0 <corpora-in-dir> <dict-in-file> <rec-out-dir> <nj>"
  echo "  <corpora-in-dir> is a folder containing both wav and txt files"
  echo "  <dict-in-file> is the phonetic dictionary input file"
  echo "  <rec-out-dir> is a dir to store the aligner's .rec output file"
  exit 1
fi

if [ ! -d $EASYALIGN_PATH ] ; then
  echo "$0: please update path to EasyAlign plugin dir: '$EASYALIGN_PATH'"
  echo "  http://latlcui.unige.ch/phonetique/easyalign.php"
  exit 1
elif ! type -t HVite > /dev/null ; then
  echo "$0: please install HTK"
  exit 1
fi

data_dir=$1
dict=$(mktemp --suffix='.dict')  # $2
rec_dir=$3

# generate dict according to HTK format
# FIXME not sure all those 'sil's are really necessary, but...
echo -e "<s>\tsil"     > $dict
echo -e "</s>\tsil"   >> $dict
echo -e "<unk>\tsil"  >> $dict
cat $2 | \
  sed 's/ R/ hh/g'   | \
  sed 's/ X/ hh/g'   | \
  sed 's/ r/ n4/g'   | \
  sed 's/ tS/ t S/g' | \
  sed 's/ dZ/ d Z/g' >> $dict
echo -e "sil\tsil"   >> $dict

# gen HTK's 'analysis.cfg' config file according to align_sound.praat#L92
cfg=$(mktemp --suffix='.cfg')
cat <<EOF > $cfg
SOURCERATE = $SRC_RATE_REF
TARGETKIND = $TARGET_KIND
SOURCEFORMAT = WAV
USEHAMMING = T 
PREEMCOEF = 0.97
NUMCHANS = 26
CEPFILTER = 22
NUMCEPS = 12
TARGETRATE = 100000
WINDOWSIZE = 250000
EOF

for wav in $data_dir/*.wav ; do
  echo -ne "\r$0: processing file '$(basename $wav)' "

  wav=$(readlink -f $wav)
  txt=$(echo $wav | sed 's/\.wav/\.txt/g')
  lab=$(echo $wav | sed 's/\.wav/\.lab/g')  # aux input
  rec=$(echo $wav | sed 's/\.wav/\.rec/g')  # proper output

  rm -f $lab
  for word in $(cat $txt) ; do
      echo $word >> $lab
  done

  # easyalign's align_sound.praat#L363 file
  #-T 1        # only for slk language
  #-b sil      # only if precise_endpointing flag not set
  #-A          # just to print CLI arguments
  HVite         \
    -a          \
    -m          \
    -C $cfg     \
    -H $EASYALIGN_PATH/lang/porbra/porbra.hmm \
    -t 250      \
    $dict       \
    $EASYALIGN_PATH/lang/porbra/porbraphone1.list \
    $wav && mv $rec $rec_dir || echo "$0: **problem with file '$wav'"
  rm -f $lab
done
echo

rm -f $cfg $dict
