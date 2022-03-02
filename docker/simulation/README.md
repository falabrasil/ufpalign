# HTK in Docker :whale:

In order to build this image, you gotta download HTK source from the website
first: https://htk.eng.cam.ac.uk/. Place the file `HTK-3.4.1.tar.gz` from the
last stable release in this very dir, then.

The image is based on Debian 11 (Buster),
but in theory one could use any Debian version (after Stretch, please.)

:warning: this image won't go into docker hub due to HTK licensing and 
copyright issues.


## Build

```bash
$ cd ufpalign/docker/simulation
# do not forget to download HTK source right now and put the .tar.gz file here
$ docker build -t ufpalign/simulation:$(date +'%Y%m%d') .
```


[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2022)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
