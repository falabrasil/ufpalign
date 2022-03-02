msg() { echo -e "\e[93m$(date) $1\e[0m" ; }

# https://github.com/falabrasil/speech-datasets
DATA_DIR=/opt/speech-datasets/datasets/mf

# https://github.com/letter-to-phoneme/m2m-aligner
M2M_BIN=/opt/m2m/m2m-aligner

# https://htk.eng.cam.ac.uk/
HVITE_BIN=/opt/htk/bin/HVite

# http://latlcui.unige.ch/phonetique/easyalign.php
EASYALIGN_DIR=/opt/easyalign/plugin_easyalign

# https://gitlab.com/fb-align/hvite-align
UFPALIGN_DIR=/opt/ufpalign-v1/plugin_ufpalign-1.0

# https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner
MFA_AMFILE=$HOME/Documents/MFA/pretrained_models/acoustic/portuguese.zip

# https://github.com/kaldi-asr/kaldi
KALDI_DIR=/opt/kaldi
