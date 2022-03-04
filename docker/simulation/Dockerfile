# PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
FROM continuumio/miniconda3:latest

LABEL maintainer="Cassio Batista <cassiotb@ufpa.br>"

RUN apt-get update -q && apt-get install -y --no-install-recommends \
  build-essential gcc-multilib vim unzip && \
  apt-get clean && rm -rf /var/lib/apt/lists/* && \
  mkdir -p /opt/kaldi /opt/m2m /opt/easyalign /opt/ufpalign-v1 /opt/speech-datasets

ADD HTK-3.4.1.tar.gz /opt

RUN git clone --depth 1 https://github.com/letter-to-phoneme/m2m-aligner.git /opt/m2m && \
  git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi && \
  git clone --depth 1 https://gitlab.com/fb-align/hvite-align.git /opt/ufpalign-v1 && \
  git clone --depth 1 https://github.com/falabrasil/speech-datasets.git /opt/speech-datasets && \
  wget -q http://latlcui.unige.ch/phonetique/easyalign/plugin_easyalign.zip -P /opt/easyalign && \
  unzip -q /opt/easyalign/plugin_easyalign.zip -d /opt/easyalign && \
  cd /opt/htk && \
  ./configure --disable-hslab --disable-hdecode --disable-hlmtools --disable-htkbook --prefix=/opt/htk && \
  make -j $(nproc) && make install && \
  cd /opt/m2m && make && \
  conda install -c conda-forge montreal-forced-aligner -y && \
  mfa model download acoustic portuguese && \
  mfa model download dictionary portuguese_brazil_ipa && \
  mfa model download g2p portuguese_g2p && \
  pip3 install pip -U && pip3 install 'dvc[gdrive]' matplotlib numpy pandas seaborn termcolor
