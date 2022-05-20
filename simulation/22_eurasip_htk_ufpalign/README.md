# UFPAlign v1.0: Iago's PROPOR 2016 w/ HTK's HVite

Source: https://gitlab.com/fb-align/hvite-align

The default output of FalaBrasi's HTK alinger is a TextGrid file, so we gotta
convert it to pts before combining it with the pts extracted from the original
male/female dataset in order to compute the phonetic boundary metric.

```mermaid
graph LR;
    wav(wav)   --> aligner[HTK];
    txt(txt)   --> aligner;
    aligner    --> rec(rec);
    rec        --> rec2pts[rec2pts];
    rec2pts    --> pts(pts);

    style aligner stroke-width:2px,stroke:#000,fill:#fff
    style rec2pts stroke-width:2px,stroke:#000,fill:#fff

    style wav fill:#ff9
    style txt fill:#ff9
    style rec fill:#ff9
    style pts fill:#ff9
```


:warning: `.lab` files required by HVite are just txt with spaces substituted 
by linebreaks, i.e., word lists.


[![FalaBrasil](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_fb_git_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](https://gitlab.com/falabrasil/avatars/-/raw/main/logo_ufpa_git_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2021)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
