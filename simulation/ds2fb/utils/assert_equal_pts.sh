#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

if [ "$(basename $(pwd))" == "utils" ] ; then
    echo "[$0] Error: script should be called from the parent dir."
    echo "     e.g.: bash utils/$0"
    exit 1
fi

pts_dir="workspace/pts_out/"
unmatch_count=0
for r in $pts_dir/fb/*.pts ; do
    pts=$(basename $r)
    echo -ne "\r[$0] Asserting file $pts\t"
    if [ $(wc -l < $pts_dir/fb/$pts) -ne $(wc -l < $pts_dir/ds/$pts) ] ; then
        echo "[$0] Warning: no match for file '$pts'."
        unmatch_count=$((unmatch_count+1))
    fi
done
echo
echo "[$0] Number of mismatches: $unmatch_count"
