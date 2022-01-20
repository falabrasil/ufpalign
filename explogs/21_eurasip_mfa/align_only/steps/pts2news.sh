#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# to be executed after *_tg2pts.sh scripts

N=200

if test $# -ne 4 ; then
    echo "usage: $0 <mfa-pts-in-dir> <fb-pts-in-dir> <gender-tag> <news-out-file>"
    exit 1
fi

mfa_dir=$1
fb_dir=$2
gender_tag=$3
news_file=$4

# sanity check
if [ ! -d "$mfa_dir" ] ; then
    echo "error: mfa pts dir must exist: '$mfa_dir'"
    exit 1
elif [ ! -d "$fb_dir" ] ; then
    echo "error: fb pts dir must exist: '$fb_dir'"
    exit 1
elif [[ "$gender_tag" != "M" && "$gender_tag" != "F" ]]  ; then
    echo "$0: gender tag must be either 'M' or 'F': $gender_tag"
    exit 1
fi

rm -f $news_file
for i in $(seq -w $N) ; do
    basefile=$gender_tag-$i.pts
    mfa_pts=$mfa_dir/$basefile
    fb_pts=$fb_dir/$basefile
    if [[ -f "$mfa_pts" && -f "$fb_pts" ]] ; then
        echo -ne "\r[$0] $mfa_pts + $fb_pts -> $news_file"
        # parse falabrasil and mfa pts files into a single news file
        mfa_phones=$(awk '{print $1}' $mfa_pts | tr -d '"' | grep -Evw "sp|sil" | tr "\n" " ")
        fb_phones=$(awk '{print $1}' $fb_pts   | tr -d '"' | grep -v "_"        | tr "\n" " ")
        echo -e "$mfa_phones\t$fb_phones" >> $news_file
    #else
    #    echo
    #    echo "[$0] skipping $basefile"
    fi
done
echo
