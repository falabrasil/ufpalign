#!/usr/bin/env bash
#
# author: apr 2021
# cassio batista - https://cassota.gitlab.io

ok=true
for f in tar java wget curl python3 ; do
  type -f $f > /dev/null 2>&1 || { echo "$0: $f not installed" && ok=false ; }
done

$ok || exit 1
