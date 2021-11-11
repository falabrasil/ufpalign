#!/usr/bin/env bash
#
# downloads acoustic model files in tar.gz format from Google Drive
# 
# author: apr 2021
# cassio batista - https://cassota.gitlab.io
# last update: nov 2021

BASE_URL="https://drive.google.com/uc?export=download&"

# https://stackoverflow.com/questions/1494178/how-to-define-hash-tables-in-bash
declare -A files=(
  ["data.tar.gz"]="1YiZ9zzRHQNcQYFRwXzTKJ9RAZbdlyS7N"
  ["mono.tar.gz"]="1y9E1HATkxVn_MkGa4vsJyEvHa8X_rfgb"
  ["tri1.tar.gz"]="1gL_AmKvWFyqCdysk33X8V6-nJnqb1CiT"
  ["tri2.tar.gz"]="1LBz3_5VhQMMkWZZRuPKCyWpVl6t-xgfO"
  ["tri3.tar.gz"]="1qSrAZJ7Y8Mihgd9R9zSfdhsuaQBsX0fX"
  ["tdnn.tar.gz"]="11oWQfUxK8wMztyMypbcDBCRrxVZEKzPZ"
  ["ie.tar.gz"]="1K1BpN0yleASVQPPM8XTUORjg8LU-ykYp"
)

# https://stackoverflow.com/questions/48133080/how-to-download-a-google-drive-url-via-curl-or-wget/48133859
fetch() {
  filename="$1"
  filehash="$2"
  echo "$0: downloading '$filename' from Google Drive"
  curl -c  ./cookie -s -L "$BASE_URL&id=$filehash" > /dev/null
  curl -L --progress-bar -b ./cookie \
    "$BASE_URL&confirm=$(awk '/download/ {print $NF}' ./cookie)&id=$filehash" \
    -o $filename || exit 1
}

# main
if [ $# -ne 2 ] ; then
  echo "usage: $0 <tag> <model-dir>"
  echo "  <tag> is the resource tag"
  echo "  <model-dir> is the folder where models will be downloaded and extracted to"
  exit 1
fi

tag=$1
dir=$2
mkdir -p $dir || exit 1

trap 'rm -f cookie' SIGINT

filename=$tag.tar.gz
filehash=${files[$filename]}

[ -f $dir/$filename ] && \
  echo "$0: file '$dir/$filename' exists. skipping download" || \
  { fetch $filename $filehash && mv $filename $dir ; }
tar xf $dir/$filename -C $dir || exit 1

rm -f cookie

if [ ! -f $dir/fb_nlplib.jar ] ; then
  echo "$0: downloading FalaBrasil tagger lib from GitLab"
  wget -q --show-progress \
    https://gitlab.com/fb-nlp/nlp-generator/-/raw/master/fb_nlplib.jar \
    -P $dir || exit 1
fi
