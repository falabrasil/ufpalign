#!/usr/bin/env bash
#
# This is the third version of this run script. The old ones are within
# `oldrun` dir. It had to be created after the second attempt to extract
# phoneid information from the file phones.txt didn't go well because it seems
# the mapping from phonemes to ids is not compatible across models, so it was
# yielding the wrong mappings (except for the sil, perhaps.)
#
# This script therefore assumes a 1:1 mapping between phoneids.ctm and the 
# trancription extracted directly from the phonetic dictionary. The G2P mapping
# is built from every .txt file within male/female datasets, so the phonemes 
# for all words of the sentence are considered when put against the excerpts 
# from the .ctm file.
#
#  $ head -n 27 ../../male/20_bracis_kaldi/00mono/ctm/mono.phoneids.ctm workspace/pts/mono/M-001.pts
#  ==> mono.phoneids.ctm <==            ==> workspace/pts/mono/M-001.pts <==
#  M-001 1 0.000 0.040 14               a       0.040
#  M-001 1 0.040 0.120 71               k       0.160
#  M-001 1 0.160 0.050 33               e       0.210
#  M-001 1 0.210 0.150 117              s       0.360
#  M-001 1 0.360 0.060 125              t       0.420
#  M-001 1 0.420 0.050 17               a~      0.470
#  M-001 1 0.470 0.050 148              w~      0.520
#  M-001 1 0.520 0.110 43               f       0.630
#  M-001 1 0.630 0.050 93               o       0.680
#  M-001 1 0.680 0.030 60               j       0.710
#  M-001 1 0.710 0.040 111              R       0.750
#  M-001 1 0.750 0.070 33               e       0.820
#  M-001 1 0.820 0.100 125              t       0.920
#  M-001 1 0.920 0.050 93               o       0.970
#  M-001 1 0.970 0.110 85               m       1.080
#  M-001 1 1.080 0.120 13               a       1.200
#  M-001 1 1.200 0.060 25               d       1.260
#  M-001 1 1.260 0.030 12               a       1.290
#  M-001 1 1.290 0.060 87               n       1.350
#  M-001 1 1.350 0.060 132              u       1.410
#  M-001 1 1.410 0.090 71               k       1.500
#  M-001 1 1.500 0.120 97               o~      1.620
#  M-001 1 1.620 0.050 49               g       1.670
#  M-001 1 1.670 0.060 109              r       1.730
#  M-001 1 1.730 0.120 41               E       1.850
#  M-001 1 1.850 0.200 117              s       2.050
#  M-001 1 2.050 0.030 132              u       2.080
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

WORKDIR=workspace

# https://stackoverflow.com/questions/402377/using-getopts-to-process-long-and-short-command-line-options
while true ; do
  case $1 in
    -r | --reset) echo "$0: removing $WORKDIR" && rm -rf $WORKDIR; shift ;;
    *) break ;;
  esac
done

find ../../{male,female} -name "*.txt" > txtlist.tmp
for ctm in $(find ../../{male,female}/20_bracis_kaldi -name "*.phoneids.ctm") ; do
  echo "[$0] processing $ctm" | lolcat
  out_dir=$WORKDIR/pts/$(basename $ctm | cut -d '.' -f 1)
  mkdir -p $out_dir
  steps/ctm2pts3.py \
    $ctm \
    txtlist.tmp \
    ../../dict_fb.dict \
    $out_dir || exit 1
done
rm txtlist.tmp

echo "[$0] success!" | lolcat -ai -d 36
