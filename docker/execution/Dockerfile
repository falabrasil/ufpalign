FROM kaldiasr/kaldi:latest

LABEL maintainer="Cassio T Batista <cassiotbatista@gmail.com>"

RUN apt-get update && \
    apt-get -y install sudo curl git openjdk-8-jdk locales python3-pip && \
    git clone https://github.com/letter-to-phoneme/m2m-aligner.git /opt/m2m-aligner && \
    cd /opt/m2m-aligner && \
    make && \
    cd - \
    pip3 install pip -U && \
    pip3 install gdown==5.0.0 pandas==2.2.2 TextGrid==1.5 Unidecode==1.3.8 PyICU==2.14 && \
    mkdir -p /opt/UFPAlign && \
    sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

ENV LC_ALL pt_BR.UTF-8

COPY . /opt/UFPAlign/

WORKDIR /opt/UFPAlign
