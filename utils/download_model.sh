#!/usr/bin/env bash
#
# downloads acoustic model files in tar.gz format from Google Drive
# 
# author: apr 2021
# cassio batista - https://cassota.gitlab.io
# last update: jan 2023

# https://stackoverflow.com/questions/1494178/how-to-define-hash-tables-in-bash
declare -A files=(
  ["data.tar.gz"]="1677Chb1JDCttzBwyRm5_P-3ELoj6VaYH"
  ["mono.tar.gz"]="1WlOMnb0P_VNVwHs1iII78aMNjND6finP"
  ["tri1b.tar.gz"]="1ie3NXKKfmk4bPHcnhIW4v0zelXmcjKIl"
  ["tri2b.tar.gz"]="11rR2UtJahj7KHbW0hRfm55HFNm6pvCcP"
  ["tri3b.tar.gz"]="1IlBnLNabDnEY3rVBdz9g3P4g1wyD1Cxl"
  ["tdnn.tar.gz"]="10ru1CW221TzZGUdcCXTaZlw7H8nszvwP"
  ["ie.tar.gz"]="19VyLt6GpPJQmPdEwbsGuwiufdEUS5E_f"
)

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

filename=$tag.tar.gz
filehash=${files[$filename]}

[ ! -f $dir/$filename ] && gdown -O $dir/$filename "$filehash" || \
  echo "$0: file '$dir/$filename' exists. skipping download"
tar xf $dir/$filename -C $dir || exit 1

if [ ! -f $dir/fb_nlplib.jar ] ; then
  echo "$0: downloading FalaBrasil annotator lib from GitHub"
  wget -q --show-progress \
    https://github.com/falabrasil/annotator/raw/master/fb_nlplib.jar \
    -P $dir || exit 1
fi
