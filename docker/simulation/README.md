# Docker for simulation :whale:

In order to build this image, you gotta download HTK source from the website
first: https://htk.eng.cam.ac.uk/. Place the file `HTK-3.4.1.tar.gz` from the
last stable release in this very dir, then.

The image is based on 
[Continuum IO's image for Miniconda 3](https://hub.docker.com/r/continuumio/miniconda3),
which in turn is based on Debian 11 (Buster), but in theory one could use any 
Debian version (after Stretch, please.) Miniconda is necessary because of MFA.

:warning: this image won't go into docker hub due to HTK licensing and 
copyright issues.


## Build

```bash
$ git clone https://github.com/falabrasil/ufpalign
$ cd ufpalign/docker/simulation
# do not forget to download HTK source right now and put the .tar.gz file here
$ docker build -t falabrasil/ufpalign:simulation-$(date +'%Y%m%d') .
```

## Usage

```text
$ git clone https://github.com/falabrasil/ufpalign
$ docker run --name ufpalign-simulation -it -v $PWD/ufpalign:/opt/ufpalign \
    falabrasil/ufpalign-simulation:-$(date +'%Y%m%d') bash
(base) root@HASH # cd /opt/speech-datasets && dvc pull -r align 
(base) root@HASH # cd /opt/ufpalign/simulation && bash run.sh
```


[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2022)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
