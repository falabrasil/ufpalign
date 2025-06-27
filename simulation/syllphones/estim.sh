#!/usr/bin/env bash
#
# create m2m aligner model that can align phonetic and syllabic tokens to 
# create the syllphones file at inference time.
#
# author: feb 2025
# Cassio T Batista - https://cassiotbatista@github.io


export LC_ALL=pt_BR.UTF-8

UFPALIGN_DIR=/opt/UFPAlign
M2M_DIR=$HOME/work/tools/letter-to-phoneme/m2m-aligner

seed=42  # random seed
n_train=100000  # 100k
exp_dir=exp5

mkdir -p $exp_dir || exit 1

echo "[$(date)] $0: creating news file ..." | lolcat
python3 local/dict2news.py \
  --m2m_lut_file $exp_dir/m2m.lut \
  $UFPALIGN_DIR/data/dict/lexicon.txt \
  $UFPALIGN_DIR/data/dict/syllables.txt > $exp_dir/m2m.news 2> $exp_dir/m2m.log

# extract a subset of the whole data to train the aligner model
shuf -n $n_train --random-source=<(yes $seed) \
  $exp_dir/m2m.news > $exp_dir/train.news

echo "[$(date)] $0: estimating model from subset ..." | lolcat
/usr/bin/time -f "%U user %e real %M KB" \
$M2M_DIR/m2m-aligner \
  --cutoff 0.01 \
  --maxFn conXY \
  --maxX 4 \
  --maxY 1 \
  --inputFile $exp_dir/train.news \
  --outputFile $exp_dir/train.ali \
  --alignerOut $exp_dir/m2m.model

# kinda stupid to run on all data again since i've already executed it 
# on half of the data but who cares it's only 15secs for 200k utts anyway...
echo "[$(date)] $0: applying model to all data ..." | lolcat
/usr/bin/time -f "%U user %e real %M KB" \
$M2M_DIR/m2m-aligner \
  --maxFn conXY \
  --maxX 4 \
  --maxY 1 \
  --inputFile $exp_dir/m2m.news \
  --outputFile $exp_dir/m2m.ali \
  --alignerIn $exp_dir/m2m.model

# train another aligner model on the instances that could not be aligned by 
# the previous model. a subset of the training data (10%) is used to help 
# dealing with the lack of data in the residual dataset (err).
# https://stackoverflow.com/questions/1037365/how-to-sort-a-tab-delimited-file-with-sort-command
(
  shuf -n $((n_train / 10)) --random-source=<(yes $seed) $exp_dir/train.news
  cat $exp_dir/m2m.ali.err
) | sort -t $'\t' -k 2 > $exp_dir/res.news

echo "[$(date)] $0: estimating residual model for error mitigation ..." | lolcat
/usr/bin/time -f "%U user %e real %M KB" \
$M2M_DIR/m2m-aligner \
  --cutoff 0.01 \
  --maxFn conXY \
  --maxX 4 \
  --maxY 1 \
  --inputFile $exp_dir/res.news \
  --outputFile $exp_dir/res.ali \
  --alignerOut $exp_dir/res.model

# https://stackoverflow.com/questions/1037365/how-to-sort-a-tab-delimited-file-with-sort-command
echo "[$(date)] $0: creating syllphones file ..." | lolcat
(
  echo -e "<eps>\tsil"
  (
    python3 local/ali2syllphones.py < $exp_dir/m2m.ali
    python3 local/ali2syllphones.py --only_from $exp_dir/m2m.ali.err < $exp_dir/res.ali
    #python3 local/err2syllphones.py < $exp_dir/res.ali.err
    cat $exp_dir/m2m.lut
  ) | sort -u
) > $exp_dir/syllphones.txt

echo "[$(date)] $0: success!" | lolcat
