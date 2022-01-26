#!/usr/bin/env bash

if [ "$(basename $(pwd))" == "utils" ] ; then
    echo "[$0] Error: script should be called from 'scripts/mfa2fb' dir."
    echo "     e.g.: bash utils/$0"
    exit 1
fi

if test $# -ne 1 ; then
  echo "usage: $0 <workspace-pts-out-dir>"
  exit 1
fi

pts_dir=$1
unmatch_count=0
for r in $pts_dir/fb/*.pts ; do
    pts=$(basename $r)
    echo -ne "\r[$0] Asserting file $pts\t"
    if [ $(wc -l < $pts_dir/fb/$pts) -ne $(wc -l < $pts_dir/mfa/$pts) ] ; then
        echo "[$0] Warning: no match for file '$pts'."
        unmatch_count=$((unmatch_count+1))
    fi
done
echo
echo "[$0] Number of mismatches: $unmatch_count"
