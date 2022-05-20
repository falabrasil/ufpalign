#!/usr/bin/env bash
#
# author: feb 2021
# Cassio Batista - https://cassota.gitlab.io

. ../env.sh || exit 1

if test $# -ne 3 ; then
  echo "usage: $0 <corpus-dir> <dict> <tg-out-dir>"
  exit 1
fi

corpus_dir=$1
dict_file=$2
tg_out_dir=$3

# sanity check acoustic
[ ! -d $corpus_dir ] && echo "$0: error: corpus dir not found: '$corpus_dir'" && exit 1
[ ! -f $dict_file ] && echo "$0: error: dict not found: '$dict_file'" && exit 1

mfa align -j 10 --clean --overwrite $corpus_dir $dict_file $MFA_AMFILE $tg_out_dir || exit 1
echo "$0: done aligning '$corpus_dir'. output written to '$tg_out_dir'"
