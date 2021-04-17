#!/usr/bin/env bash
#
# downloads acoustic model files in tar.gz format from Google Drive
# 
# author: apr 2021
# cassio batista - https://cassota.gitlab.io

# https://stackoverflow.com/questions/48133080/how-to-download-a-google-drive-url-via-curl-or-wget/48133859

files=(
  "mono.tar.gz" "tri_deltas.tar.gz" "tri_lda.tar.gz" "tri_sat.tar.gz"
  "ivector_extractor.tar.gz" "tdnnf.tar.gz"
)

ids=(
  "1Cj8cFkRZjJ5B4bVl5lzEhjAY6_FhyPKB" "1L7zbm-Y_Lf5kzrZHcxb7XDE_4LXg4LPi"
  "1pIV4RYAAjvh7ZJWFNGajIQjjTnQVv9Nr" "130INMFrOpbyVnRBJ5OIRlD1FZx7W0Tfr"
  "10QEojcAJ20CZiQ7fZLusPXrd1Sb7OO7L" "1_Yp35qa5xpubIFYcpJGcFwKGsYOaw5Ju"
)

function fetch {
  fileid="$1"
  filename=$2
  baseurl="https://drive.google.com/uc?export=download&"
  echo "$0: downloading '$filename' from Google Drive"
  curl -c  ./cookie -s -L "$baseurl&id=$fileid" > /dev/null
  curl -L --no-progress-meter -b ./cookie \
    "$baseurl&confirm=$(awk '/download/ {print $NF}' ./cookie)&id=$fileid" \
    -o $filename || exit 1
}

if [ $# -ne 1 ] ; then
  echo "usage: $0 <model-dir>"
  echo "  <model-dir> is the folder where models will be downloaded and extracted to"
  exit 1
fi

dir=$1
mkdir -p $dir || exit 1

trap 'rm -f cookie' SIGINT
for i in $(seq 0 5) ; do
  filename=${files[$i]}
  fileid=${ids[$i]}
  [ -f $dir/$filename ] && \
    echo "$0: file '$dir/$filename' exists. skipping download" && continue
  fetch $fileid $filename
  mv $filename $dir && tar xf $dir/$filename -C $dir || exit 1
done

rm -f cookie

if [ ! -f fb_nlplib.jar ] ; then
  echo "$0: downloading FalaBrasil NLP lib from GitLab"
  wget -q --show-progress \
    https://gitlab.com/fb-nlp/nlp-generator/-/raw/master/fb_nlplib.jar || exit 1
fi
