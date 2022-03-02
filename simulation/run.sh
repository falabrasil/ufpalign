#!/usr/bin/env bash
#
# author: feb 2022
# cassio batista - https://cassota.gitlab.io

set -euo pipefail

# FIXME XXX TODO adjust all paths within this file TODO XXX FIXME
. env.sh || exit 1

# check requirements according to env vars defined in env.sh
ok=true
local/check_dependencies.sh || ok=false
[ ! -d $DATA_DIR ] && echo "$0: error: bad mf dataset dir" && ok=false
[ ! -f $M2M_BIN ] && echo "$0: error: m2m not compiled" && ok=false
[ ! -f $HVITE_BIN ] && echo "$0: error: hvite not compiled" && ok=false
[ ! -d $EASYALIGN_DIR ] && echo "$0: error: bad easyalign (htk) dir" && ok=false
[ ! -d $UFPALIGN_DIR ] && echo "$0: error: bad ufpalign (htk) dir" && ok=false
[ ! -f $MFA_AMFILE ] && echo "$0: error: bad mfa acoustic model" && ok=false
[ ! -d $KALDI_DIR ] && echo "$0: error: bad kaldi dir" && ok=false
$ok || { echo "** PLEASE READ THE README.md FILE!!!" && exit 1 ; }

for sim in ds2fb 22_eurasip_htk_{easyalign,ufpalign} 22_eurasip_mfa_{align_only,train_and_align} 22_eurasip_kaldi ; do
  ( cd $sim ; bash run.sh || touch .err )
  [ -f $sim/.err ] && rm $sim/.err && echo "$0: error at $sim" && exit 1
done

echo "$0: success!"
