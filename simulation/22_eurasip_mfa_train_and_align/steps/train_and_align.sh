#!/usr/bin/env bash
#
# author: feb 2021
# Cassio Batista - https://cassota.gitlab.io

if test $# -ne 3 ; then
  echo "usage: $0 <corpus-dir> <dict> <tg-out-dir>"
  exit 1
fi

corpus_dir=$1
dict_file=$2
tg_out_dir=$3

# sanity check
[ ! -d $corpus_dir ] && echo "$0: error: corpus dir not found: '$corpus_dir'" && exit 1
[ ! -f $dict_file ] && echo "$0: error: dict not found: '$dict_file'" && exit 1

mfa train -j 4 --clean --overwrite $corpus_dir $dict_file $tg_out_dir || exit 1
echo "$0: done training and aligning over $corpus_dir. output written to $tg_out_dir"
