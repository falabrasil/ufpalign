#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

if [ "$(basename $(pwd))" == "utils" ] ; then
    echo "[$0] Error: script should be called from the parent dir."
    echo "     e.g.: bash utils/$0"
    exit 1
fi

if test $# -ne 1 ; then
    echo "usage: $0 <phone-token>"
    exit 1
fi

for dir in male female ; do
    grep -n $1 workspace/ali_$dir.mm --color=always >&2
    indices=$(grep -n $1 workspace/ali_$dir.mm | cut -d ':' -f 1)
    if [ ! -z "$indices" ] ; then
        for i in $(echo $indices); do
            f=$(echo ${dir:0:1} | tr '[a-z]' '[A-Z]')-$(printf "%03d" $i)
            echo -n "$f: " && cat ../../$dir/$f.txt | lolcat
        done
    fi
done
