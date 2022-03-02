#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# NOTE: to be called first, no direct dependency
# pts: phonetic timestamp

if test $# -ne 2 ; then
    echo "usage: $0 <tg-in-dir> <pts-out-dir>"
    exit 1
elif [ ! -d "$1" ] ; then
    echo "error: textgrid dir must exist: '$1'"
    exit 1
fi

suffix=$(date +'%Y%m%d_%H%M%S')
for tg in $1/*.TextGrid ; do
    basefile=$(basename $tg)
    pts=$2/$(echo $basefile | sed 's/\.TextGrid/\.pts/g')
    echo -ne "\r[$0] processing file $basefile "

    # get pts from dataset textgrid
    # TextGrid files manully aligned on this dataset have 5 tiers and the
    # phonemes' happed to be in the first one, so we can't just grep around but
    # we can rather awk for two string to get the content in between them. As
    # we know the second tier stores phoneme syllabels under the name
    # "syll", awk will get everything from "phones" to "syll".
    # Ref.: https://unix.stackexchange.com/questions/21076/how-to-show-lines-after-each-grep-match-until-other-specific-match
    timestamps=$(awk '/name = "phones"/,/name = "syll"/' $tg |\
        grep 'xmax' | tail -n +2 | sed 's/xmax =//g' | tr -d '[ \t]')
    phonemes=$(awk '/name = "phones"/,/name = "syll"/' $tg |\
        grep 'text' | sed 's/text =//g' | tr -d '[ \t]')

    # FIXME iterate an index once would be smarter than looping a foreach twice
    rm -f /tmp/{p,ts}.$suffix
    for p in $(echo $phonemes) ; do
        echo $p >> /tmp/p.$suffix
    done

    for ts in $(echo $timestamps) ; do
        echo "${ts:0:6}" >> /tmp/ts.$suffix
    done

    ( paste /tmp/{p,ts}.$suffix | expand -t 8 ) > $pts || \
        { echo "$0: problem writing to file '$pts'" && exit 1; }
    rm -f /tmp/{p,ts}.$suffix
done
echo
