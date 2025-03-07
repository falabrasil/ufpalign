#!/usr/bin/env bash
#
# downloads acoustic model files in tar.gz format from Google Drive
# 
# author: apr 2021
# Cassio T Batista - https://cassiotbatista.github.io
# last update: feb 2025

# https://stackoverflow.com/questions/1494178/how-to-define-hash-tables-in-bash
declare -A gdrive_dict=(
  #["data.tar.gz"]="1677Chb1JDCttzBwyRm5_P-3ELoj6VaYH"
  ["data.tar.gz"]="1LV079CNWO_rq8bPKUSOYXCeF-f1SheZS"
  ["mono.tar.gz"]="1WlOMnb0P_VNVwHs1iII78aMNjND6finP"
  ["tri1b.tar.gz"]="1ie3NXKKfmk4bPHcnhIW4v0zelXmcjKIl"
  ["tri2b.tar.gz"]="11rR2UtJahj7KHbW0hRfm55HFNm6pvCcP"
  ["tri3b.tar.gz"]="1IlBnLNabDnEY3rVBdz9g3P4g1wyD1Cxl"
  ["tdnn.tar.gz"]="10ru1CW221TzZGUdcCXTaZlw7H8nszvwP"
  ["ie.tar.gz"]="19VyLt6GpPJQmPdEwbsGuwiufdEUS5E_f"
  ["m2m.model.gz"]="16z7uSUeA6vdL2cXIDpto6kW9FelXYazM"
)

declare -A checksum_dict=(
  #["data.tar.gz"]="919984909fc449039a6890ead1b4e5f8"  # data_nosyllphones.tar.gz
  ["data.tar.gz"]="ded8d03f709867c098318d0cefdeecce"    
  ["mono.tar.gz"]="56ea26a427f50d0f09440d0456fbbff3"
  ["tri1b.tar.gz"]="4e8f7bb8a221d20cd7fee418e07be745"
  ["tri2b.tar.gz"]="a6e268cb457fc9e28d43fda58b13d021"
  ["tri3b.tar.gz"]="5424cec31cff7a7e05b95098ee7be11d"
  ["tdnn.tar.gz"]="27179684368faead0a558b714c94d49c"
  ["ie.tar.gz"]="20bce8f20d659603f9ec0655e0d62628"
  ["m2m.model.gz"]="692049ca0a2bee6c27b91997d5e1dc73"
)

if [ $# -ne 2 ] ; then
  echo "usage: $0 <tag> <model-dir>"
  echo "  <tag> is the resource tag"
  echo "  <model-dir> is the folder where models will be downloaded and extracted to"
  exit 1
fi

tag=$1
dir=$2
mkdir -p $dir || exit 1

[[ $tag == "m2m" ]] && filename=$tag.model.gz || filename=$tag.tar.gz
fileid=${gdrive_dict[$filename]}
filesum=${checksum_dict[$filename]}

# download models and pre-compiled dicts
if [ ! -f $dir/$filename ] ; then
  gdown -O $dir/$filename "$fileid"
else
  real_checksum=${checksum_dict[$filename]}
  curr_checksum=$(md5sum $dir/$filename | awk '{print $1}')
  if [[ $curr_checksum == $real_checksum  ]] ; then
    echo "$0: info: file '$dir/$filename' exists. skipping download."
  else
    echo -n "$0: warn: file '$dir/$filename' exists but seems out of date. "
    echo "consider erasing or changing your installation dir."
  fi
fi

# extract
if [[ $tag == "m2m" ]] ; then
  gunzip -kc $dir/$filename > $dir/${filename%.gz} || exit 1
else
  tar xf $dir/$filename -C $dir || exit 1
fi

# download tagger
if [ ! -f $dir/fb_nlplib.jar ] ; then
  echo "$0: downloading FalaBrasil annotator lib from GitHub"
  wget -q --show-progress \
    https://github.com/falabrasil/annotator/raw/master/fb_nlplib.jar \
    -P $dir || exit 1
fi
