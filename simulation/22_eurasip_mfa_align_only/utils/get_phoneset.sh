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
echo "[$0] getting mfa phones..."
mfa=$(for pts in $pts_dir/mfa/*.pts ; do awk '{print $1}' $pts ; done | sort | uniq)
echo "[$0] getting fb phones..."
fb=$(for pts in $pts_dir/fb/*.pts   ; do awk '{print $1}' $pts ; done | sort | uniq)

# https://unix.stackexchange.com/questions/114943/can-sed-replace-new-line-characters/169403#169403
echo "mfa: $(echo $mfa | tr "\n" " " | sed 's/\"//g')"
echo "fb:  $(echo $fb  | tr "\n" " " | sed 's/\"//g')"
