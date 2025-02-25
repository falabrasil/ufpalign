#!/usr/bin/env bash
#
# author: jan 2023
# Cassio T Batista - https://cassiotbatista.github.io
# last update: feb 2025

ok=true

# env var dependencies
[[ -z "$KALDI_ROOT" || ! -d "$KALDI_ROOT/egs" ]] && ok=false && \
  echo "$0: error: please set KALDI_ROOT dir: '$KALDI_ROOT'"
[[ -z "$M2M_ROOT" || ! -d "$M2M_ROOT" ]] && ok=false && \
  echo "$0: error: please set M2M_ROOT dir: '$M2M_ROOT'"

# bash dependencies
for f in sudo tar java wget curl python3 gdown ; do
  ! type -f $f > /dev/null 2>&1 && ok=false && \
    echo "$0: error: $f not installed"
done

# python dependencies
for p in icu pandas textgrid unidecode ; do
  ! python3 -c "import $p" 2>/dev/null && ok=false && \
    echo "$0: error: please install $p python package"
done

$ok && echo "$0: info: success!" || exit 1
