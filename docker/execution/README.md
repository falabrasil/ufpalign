# Docker for executing of UFPAlign :whale:

This is an image to run UFPAlign in a Docker container. It's based on Kaldi
image for CPU execution which is in turn based on Debian 10 (Buster). The only
extra thing is the JDK 8 package which is required by the FalaBrasil NLP lib,
which performs G2P conversion.


## Build

```bash
$ git clone https://github.com/falabrasil/ufpalign
$ cd ufpalign
$ docker build -t falabrasil/ufpalign:execution-$(date +'%Y%m%d') -f docker/execution/Dockerfile .
```


## Usage

Create the container and run it at once:

```bash
$ docker run --name ufpalign-execution -it \
    falabrasil/ufpalign-execution:-$(date +'%Y%m%d') bash
root@HASH # bash ufpalign.sh /opt/kaldi demo/audio.wav demo/trans.txt tdnn
```

Or, if the container has already been created:

```bash
$ docker start falabrasil/ufpalign-execution:-$(date +'%Y%m%d') 
$ docker exec -it falabrasil/ufpalign-execution:-$(date +'%Y%m%d') bash
root@HASH # bash ufpalign.sh /opt/kaldi demo/audio.wav demo/trans.txt tdnn
```

Then, within the container, run the aligner:

```text
root@HASH # bash ufpalign.sh /opt/kaldi demo/audio.wav demo/trans.txt tdnn
```


[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2022)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
