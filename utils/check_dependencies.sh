#!/usr/bin/env bash
#
# author: jan 2023
# Cassio T Batista - https://cassiotbatista.github.io
# last update: feb 2025

ok=true
for f in sudo tar java wget curl python3 gdown ; do
  ! type -f $f > /dev/null 2>&1 && ok=false && \
    echo "$0: $f not installed"
done
for p in icu pandas textgrid unidecode ; do
  ! python3 -c "import $p" 2>/dev/null && ok=false && \
    echo "$0: please install $p python package"
done
$ok || exit 1
echo "$0: success!"
