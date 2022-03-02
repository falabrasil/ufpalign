#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# to be executed after pts2news.sh script

. env.sh || exit 1

if test $# -ne 3 ; then
    echo "usage: $0 <news-in-file> <mm-out-file> <mm-model-out-file>"
    exit 1
elif [ ! -f $1 ] ; then
    echo "error: news file must exist: $1"
    exit 1
fi

$M2M_BIN --delY --maxFn conXY --inputFile $1 --outputFile $2 --alignerOut $3
rm -f $2.err $3  # dummies
