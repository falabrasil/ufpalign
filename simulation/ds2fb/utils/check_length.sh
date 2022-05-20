#!/usr/bin/env bash
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

if [ "$(basename $(pwd))" == "utils" ] ; then
    echo "[$0] Error: script should be called from the parent dir."
    echo "     e.g.: bash utils/$0"
    exit 1
fi

for pts in M-001.pts M-002.pts M-003.pts M-004.pts M-005.pts M-006.pts M-007.pts M-008.pts M-009.pts M-010.pts F-001.pts F-002.pts F-003.pts F-004.pts F-005.pts F-006.pts F-007.pts F-008.pts F-009.pts F-010.pts ; do
    ds=$(wc -l < workspace/pts_in/ds/$pts)
    fb=$(wc -l < workspace/pts_in/fb/$pts)
    echo -n "$pts: $ds $fb (input pts) "
    ds=$(wc -l < workspace/pts_out/ds/$pts)
    fb=$(wc -l < workspace/pts_out/fb/$pts)
    echo "$ds $fb (output pts) "
done
