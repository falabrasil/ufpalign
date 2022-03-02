#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# to be executed after *_tg2pts.sh
if [ "$(basename $(pwd))" == "utils" ] ; then
    echo "[$0] Error: script should be called from the parent dir."
    echo "     e.g.: bash utils/$0"
    exit 1
fi

pts_dir="workspace/pts_in"
ds=$(for pts in $pts_dir/ds/*.pts ; do awk '{print $1}' $pts ; done | sort | uniq)
fb=$(for pts in $pts_dir/fb/*.pts ; do awk '{print $1}' $pts ; done | sort | uniq)

# https://unix.stackexchange.com/questions/114943/can-sed-replace-new-line-characters/169403#169403
echo "ds: $(echo $ds | sed ':a;N;s/\n/,/g;ba' | sed 's/\"//g')"
echo "fb: $(echo $fb | sed ':a;N;s/\n/,/g;ba' | sed 's/\"//g')"
