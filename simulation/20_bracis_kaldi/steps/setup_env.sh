#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 2 ; then
  echo "usage: $0 <kaldi-egs-dir> <ufpalign-plugin-dir>"
  exit 1
fi

proj_dir=$1
plug_dir=$2

[ -d $proj_dir ] && echo "[$0] dir '$proj_dir' exists and will be overwritten"
rm -rf $proj_dir
mkdir -p $proj_dir/data/local || exit 1

# TODO copy models from $plug_dir into $proj_dir/exp

cd $proj_dir

ln -s ../../wsj/s5/path.sh .
ln -s ../../wsj/s5/steps .
ln -s ../../wsj/s5/utils .
ln -s ../../wsj/s5/conf .

cd - > /dev/null
