# PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
FROM continuumio/miniconda3:latest

LABEL maintainer="Cassio Batista <cassiotb@ufpa.br>"

ADD HTK-3.4.1.tar.gz /

# apt-get clean && rm -rf /var/lib/apt/lists/* && \
RUN mkdir -p /opt/kaldi /opt/htk /opt/m2m /opt/easyalign /opt/ufpalign-v1 /opt/speech-datasets && \
  git clone --depth 1 https://github.com/letter-to-phoneme/m2m-aligner.git /opt/m2m && \
  git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi && \
  git clone --depth 1 https://gitlab.com/fb-align/hvite-align.git /opt/ufpalign-v1 && \
  git clone --depth 1 https://github.com/falabrasil/speech-datasets.git /opt/speech-datasets && \
  wget http://latlcui.unige.ch/phonetique/easyalign/plugin_easyalign.zip -P /opt/easyalign && \
  unzip -q /opt/easyalign/plugin_easyalign.zip -d /opt/easyalign && \
  apt-get update -q && apt-get install -y --no-install-recommends build-essential gcc-multilib vim \
  cd /opt/htk && \
  ./configure --disable-hslab --disable-hdecode --disable-hlmtools --disable-htkbook --prefix=/opt/htk && \
  make -j $(nproc) && make install && \
  cd /opt/m2m && make && \
  conda install -c conda-forge montreal-forced-aligner -y && \
  mfa download acoustic portuguese && \
  mfa download dictionary portuguese_brazil_ipa && \
  mfa download g2p portuguese_g2p && \
  pip3 install pip -U && pip3 install 'dvc[gdrive]' matplotlib numpy pandas seaborn termcolor
