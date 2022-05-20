#!/usr/bin/env bash
#
# author: feb 2022
# cassio batista - https://cassota.gitlab.io

ok=true
for f in git dvc python3 ; do
  ! type -f $f > /dev/null 2>&1 && \
    ok=false && echo "$0: error: please install $f"
done

for f in matplotlib numpy pandas seaborn termcolor ; do
  python3 -c "import $f" 2> /dev/null || \
    { ok=false && echo "$0: error: please install $f" ; }
done

$ok || exit 1

echo "$0: success!"
