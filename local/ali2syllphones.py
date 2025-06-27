#!/usr/bin/env python3
#
# author: feb 2025
# Cassio T Batista - https://cassiotbatista@github.io

import sys


lines = [ line.strip() for line in sys.stdin if line.strip() != '' ]
for line in lines:
    syllphones, syllables = line.split('\t')
    syllphones = syllphones.replace('|', ' - ').replace(':', ' ').strip()
    grapheme = syllables.replace('|', '').strip()
    print(f"{grapheme}\t{syllphones.strip('-')}")
