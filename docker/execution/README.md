# Docker for executing of UFPAlign :whale:

This is an image to run UFPAlign in a Docker container. It's based on Kaldi
image for CPU execution which is in turn based on Debian 10 (Buster). 
JDK 8 package which is required by the FalaBrasil NLP lib, which performs
phonetic and syllabic conversion; and M2M aligner, which helps stitching phones
and syllables from the same utterance.


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
    falabrasil/ufpalign:execution-$(date +'%Y%m%d') bash
```

Or, if the container has already been created:

```bash
$ docker start ufpalign-execution
$ docker exec -it ufpalign-execution bash
```

Once inside the container, run the aligner:

```text
root@HASH # KALDI_ROOT=/opt/kaldi M2M_ROOt=/opt/m2m-aligner \
    bash ufpalign.sh demo/coxinha.wav demo/coxinha.txt mono
```


[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2025)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio T Batista - https://cassiotbatista.github.io     
