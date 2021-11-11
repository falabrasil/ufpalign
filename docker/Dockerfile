FROM kaldiasr/kaldi:latest

RUN apt-get update && \
    apt-get -y install sudo curl openjdk-8-jdk locales && \
    mkdir -p /opt/UFPAlign && \
    sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

ENV LC_ALL pt_BR.UTF-8

COPY . /opt/UFPAlign/

WORKDIR /opt/UFPAlign
