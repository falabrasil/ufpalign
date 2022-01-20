#!/usr/bin/env bash
#
# author: dec 2020
# cassio batista - https://cassota.gitlab.io

if test $# -ne 2 ; then
  echo "usage: $0 <kaldi-model-egs-dir> <kaldi-dummy-egs-dir>"
  exit 1
fi

model_dir=$1
dummy_dir=$2

[ -d $dummy_dir ] && echo "[$0] '$dummy_dir' exists and will be overwritten" 
rm -rf $dummy_dir

echo "[$0] setting up environment on '$dummy_dir'"

# copying models and data (exp and data/local)
# NOTE: assumes mini-librispeech dirnames as convention
mkdir -p $dummy_dir/{exp,results,data/local} || exit 1

cp -r $model_dir/data/local/{dict,lm} $dummy_dir/data/local
ln -rs $model_dir/exp/chain_online_cmn/tdnn1k_sp $dummy_dir/exp/tdnn
for gmm_am_tag in mono tri1 tri2b tri3b nnet3_online_cmn ; do
  ln -rs $model_dir/exp/$gmm_am_tag $dummy_dir/exp
done


ln -s $model_dir/cmd.sh  $dummy_dir
ln -s $model_dir/path.sh $dummy_dir
ln -s $model_dir/steps   $dummy_dir
ln -s $model_dir/utils   $dummy_dir
ln -s $model_dir/conf    $dummy_dir
