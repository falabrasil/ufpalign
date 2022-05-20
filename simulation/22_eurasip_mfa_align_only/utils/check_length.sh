#!/usr/bin/env bash

for pts in M-001.pts M-002.pts M-003.pts M-004.pts M-005.pts M-006.pts M-007.pts M-008.pts M-009.pts M-010.pts ; do
    mfa=$(wc -l < workspace/pts_in/mfa/$pts)
    fb=$(wc -l  < workspace/pts_in/fb/$pts)
    echo -n "$pts: $mfa $fb (input pts) "
    mfa=$(wc -l < workspace/pts_out/mfa/$pts)
    fb=$(wc -l  < workspace/pts_out/fb/$pts)
    echo "$mfa $fb (output pts) "
done
