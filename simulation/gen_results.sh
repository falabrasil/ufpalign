#!/usr/bin/env bash
#
# author: feb 2020
# Cassio Batista - https://cassota.gitlab.io

#######################################################################
### PROPOR 2016 & MFA
#######################################################################

rm -f /tmp/*.{pb,iou,png} .err

predicted=(
  "22_eurasip_htk_ufpalign/workspace/pts" 
  "22_eurasip_htk_easyalign/workspace/pts/fb" 
  "22_eurasip_mfa_align_only/workspace/pts_out/fb" 
  "22_eurasip_mfa_train_and_align/workspace/pts" 
)
filename=(
  "UFPAlign 1.0 - %s" 
  "EasyAlign - %s" 
  "MFA (align only) - %s" 
  "MFA (train and align) - %s" 
)

for i in $(seq 0 3) ; do
  for gender in M F ; do
    ( local/pts2pb.py \
        ds2fb/workspace/pts_out/fb \
        ${predicted[$i]} \
        $gender \
        "$(printf "/tmp/${filename[$i]}.pb" $gender)" || touch .err )&
    ( local/pts2iou.py \
        ds2fb/workspace/pts_out/fb \
        ${predicted[$i]} \
        $gender \
        "$(printf "/tmp/${filename[$i]}.iou" $gender)" || touch .err )&
  done
done
wait
[ -f .err ] && rm .err && echo "$0: error: htk or mfa error" && exit 1

########################################################################
#### BRACIS 2020: Resource Management
########################################################################
#
#predicted=(
#  "20_bracis_kaldi/workspace/pts/mono"
#  "20_bracis_kaldi/workspace/pts/tri1"
#  "20_bracis_kaldi/workspace/pts/tri2b"
#  "20_bracis_kaldi/workspace/pts/tri3b"
#  "20_bracis_kaldi/workspace/pts/dnn_2hidden"
#  "20_bracis_kaldi/workspace/pts/dnn_4hidden"
#)
#
#filename=(
#  "UFPAlign 2.0 (mono) - %s" 
#  "UFPAlign 2.0 (tri-Δ) - %s" 
#  "UFPAlign 2.0 (tri-LDA) - %s" 
#  "UFPAlign 2.0 (tri-SAT) - %s" 
#  "UFPAlign 2.0 (DNN 2) - %s" 
#  "UFPAlign 2.0 (DNN 4) - %s" 
#)
#
#rm -f /tmp/*.pb
#for i in $(seq 0 5) ; do
#  for gender in M F ; do
#    utils/pts2pb.py \
#      ds2fb/workspace/pts_out/fb \
#      ${predicted[$i]} \
#      $gender \
#      "$(printf "/tmp/${filename[$i]}.pb" $gender)" || exit 1
#  done
#done
#
## plot M and F in different mpl Figure objects to preserve space
#for gender in M F ; do
#  utils/pb2tol.py /tmp/UFPAlign*mono*$gender.pb \
#                   /tmp/UFPAlign*Δ*$gender.pb \
#                   /tmp/UFPAlign*LDA*$gender.pb \
#                   /tmp/UFPAlign*SAT*$gender.pb \
#                   /tmp/UFPAlign*DNN*$gender.pb
#done

#######################################################################
### EURASIP 2022: Mini-Librispeech
#######################################################################

predicted=(
  "21_eurasip_kaldi/workspace/pts/mono"
  "21_eurasip_kaldi/workspace/pts/tri1"
  "21_eurasip_kaldi/workspace/pts/tri2b"
  "21_eurasip_kaldi/workspace/pts/tri3b"
  "21_eurasip_kaldi/workspace/pts/tdnn"
)

filename=(
  "Kaldi (mono) - %s" 
  "Kaldi (tri-Δ) - %s" 
  "Kaldi (tri-LDA) - %s" 
  "Kaldi (tri-SAT) - %s" 
  "Kaldi (TDNN) - %s" 
)

for i in $(seq 0 4) ; do
  for gender in M F ; do
    ( local/pts2pb.py \
        ds2fb/workspace/pts_out/fb \
        ${predicted[$i]} \
        $gender \
        "$(printf "/tmp/${filename[$i]}.pb" $gender)" || touch .err )&
    ( local/pts2iou.py \
        ds2fb/workspace/pts_out/fb \
        ${predicted[$i]} \
        $gender \
        "$(printf "/tmp/${filename[$i]}.iou" $gender)" || touch .err )&
  done
done
wait
[ -f .err ] && rm .err && echo "$0: error: kaldi error" && exit 1

# iou: intersection over union actually request by reviewer 1 of eurasip
# plot M and F in different mpl Figure objects to preserve space
for gender in F M ; do
  ( local/iou2bp_trideltas.py /tmp/Kaldi*Δ*$gender.iou )&
  ( sleep 1 && \
    local/iou2bp.py /tmp/{U,E,M}*$gender.iou \
                     /tmp/Kaldi*mono*$gender.iou \
                     /tmp/Kaldi*Δ*$gender.iou \
                     /tmp/Kaldi*LDA*$gender.iou \
                     /tmp/Kaldi*SAT*$gender.iou \
                     /tmp/Kaldi*TDNN*$gender.iou )&
  local/pb2tol.py /tmp/{U,E,M}*$gender.pb \
                   /tmp/Kaldi*mono*$gender.pb \
                   /tmp/Kaldi*Δ*$gender.pb \
                   /tmp/Kaldi*LDA*$gender.pb \
                   /tmp/Kaldi*SAT*$gender.pb \
                   /tmp/Kaldi*TDNN*$gender.pb
wait
done
