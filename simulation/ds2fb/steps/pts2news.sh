#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# to be executed after *_tg2pts.sh scripts

if test $# -ne 3 ; then
    echo "usage: $0 <fb-pts-in-dir> <news-out-file> <gender-tag>"
    echo "  <gender-tag> must be either 'M' or 'F'"
    exit 1
elif [ ! -d "$1" ] ; then
    echo "error: pts dir must exist: '$1'"
    exit 1
fi

rm -f $2
for fb_pts in $1/$3-*.pts ; do
    ds_pts=$(echo $fb_pts | sed 's/fb/ds/g')
    echo -ne "\r[$0] $fb_pts + $ds_pts -> $2 "

    # parse falabrasil and dataset pts files into a single news file
    fb_phones=$(awk '{print $1}' $fb_pts | tr -d '"'               | tr "\n" " ")
    ds_phones=$(awk '{print $1}' $ds_pts | tr -d '"' | grep -v "_" | tr "\n" " ")
    echo -e "$ds_phones\t$fb_phones" >> $2
done
echo
