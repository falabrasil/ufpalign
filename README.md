# Forced Phonetic Alignment in Brazilian Portuguese :br:

This repo hopes to unify some of the open-source, Kaldi-based forced phonetic
alignment tools into a single resource point over which models for Brazilian
Portuguese are available.

- [MFA: Montreal Forced Aligner](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner)
- [Gentle: A robust yet lenient forced aligner built on Kaldi](https://github.com/lowerquality/gentle)


## Installation Instructions (from source)


### Create a virtual environment

We recommend the use of
[Anaconda :snake:](https://docs.anaconda.com/anaconda/install/linux/).

```bash
$ conda create --name br-ali python=3.7
$ conda activate br-ali
(br-ali) $  # <-- this is the sign that the environment is active
```


### Install GCC 8 suite (Arch Linux only)

:warning: Since I am running Arch Linux, which defaults to GCC 10.2.0 as of
Nov 2020, I had therefore to use version 8 of the C compiler suite, which is
the one which both C++11 standard and CUDA/NVIDIA drivers do not complain.
Debian-based distro might skip this part, as well as omit further `CC`,
`CXX`, and other Makefile implicit variables.

```text
# pacman -S gcc8-libs gcc8-fortran gcc8
```

```bash
$ gcc-8 --version       # returns `gcc-8 (GCC) 8.4.0`
$ g++-8 --version       # returns `g++-8 (GCC) 8.4.0`
$ gfortran-8 --version  # returns `GNU Fortran (GCC) 8.4.0`
```


### Install Kaldi with OpenBLAS as math library

First, clone Kaldi from GitHub under a directory I called `kaldi-ali`:

```bash
$ git clone https://github.com/kaldi-asr/kaldi kaldi-ali
```

Then install Kaldi `tools`, plus OpenBLAS, Phonetisaurus, and OpenGrm libs.
Sometimes OpenFST isn't compiled as well so we have to do it manually.

```bash
(br-ali) $ cd kaldi-ali/tools
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 extras/check_dependencies.sh
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 make -j 6
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 make openblas  # NOTE: uses all CPU cores
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 make openfst   # NOTE: uses all CPU cores
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 extras/install_phonetisaurus.sh  # MFA dependency
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 extras/install_opengnr.sh        # MFA dependency
```

Finally, install Kaldi `src`, linking OpenBLAS as math library. CUDA dir is
optional, I guess. Source extras should also be compiled.

```bash
(br-ali) $ cd kaldi-ali/src
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 ./configure --shared --mathlib=OPENBLAS --cudatk-dir=/opt/cuda/
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 make depend -j 6
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 make -j 6
(br-ali) $ CC=gcc-8 CXX=g++-8 FC=gfortran-8 make ext -j 6  # Gentle dependency
```

[![FalaBrasil](doc/logo_fb_github_footer.png)](https://ufpafalabrasil.gitlab.io/ "Visite o site do Grupo FalaBrasil") [![UFPA](doc/logo_ufpa_github_footer.png)](https://portal.ufpa.br/ "Visite o site da UFPA")

__Grupo FalaBrasil (2020)__ - https://ufpafalabrasil.gitlab.io/      
__Universidade Federal do Pará (UFPA)__ - https://portal.ufpa.br/     
Cassio Batista - https://cassota.gitlab.io/    
