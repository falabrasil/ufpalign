#!/usr/bin/env python3
#
# same as `sed 's/^\s|\s$//g'`, which does not work.
# effectively removes leading and trailing white spaces from each line.
#
# author: jan 2024
# Cassio Batista - https://cassiotbatista.github.io

import sys

lines = [ line.strip() for line in sys.stdin if line.strip() != "" ]
for line in lines:
    sys.stdout.write(f"{line}\n")
sys.stdout.flush()
