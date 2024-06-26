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

# sanity check acoustic model and dictionary
if [ ! -f $MFA_AMFILE ] ; then
  echo "$0: error: acoustic model not found: '$MFA_AMFILE'"
  exit 1
elif [ ! -f $dict_file ] ; then
  echo "$0: error: dict not found: '$dict_file'"
  exit 1
fi

# sanity check wav input and textgrid output dirs
if [ ! -d $corpus_dir ] ; then
  echo "$0: error: corpus dir not found: '$corpus_dir'"
  exit 1
elif [ ! -d $tg_out_dir ] ; then
  echo "$0: error: textgrid output dir not found: '$tg_out_dir'"
  exit 1
fi

echo "$0: aligning with model from '$MFA_AMFILE'"
logdir=$(mktemp -d)
mfa align -t $logdir -c $corpus_dir $dict_file $MFA_AMFILE $tg_out_dir || exit 1
echo "$0: done aligning '$corpus_dir'. output written to '$tg_out_dir'"
#rm -rf $logdir
