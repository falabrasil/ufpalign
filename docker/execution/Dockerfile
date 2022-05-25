FROM kaldiasr/kaldi:latest

LABEL maintainer="Cassio Batista <cassiotb@ufpa.br>"

RUN apt-get update && \
    apt-get -y install sudo curl openjdk-8-jdk locales python3-pip && \
    pip3 install pip -U && pip install gdown && \
    mkdir -p /opt/UFPAlign && \
    sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

ENV LC_ALL pt_BR.UTF-8

COPY . /opt/UFPAlign/

WORKDIR /opt/UFPAlign
