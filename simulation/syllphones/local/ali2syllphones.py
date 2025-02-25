#!/usr/bin/env python3
#
# author: feb 2025
# Cassio T Batista - https://cassiotbatista@github.io

import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--only_from", type=str, default=None)
args = parser.parse_args()

allow_list = None
if args.only_from:
    allow_list = set()
    with open(args.only_from) as f:
        for line in f:
            phonemes, syllables = line.split('\t')
            grapheme = syllables.replace(' ', '').strip()
            allow_list.add(grapheme)

j = 0
lines = [ line.strip() for line in sys.stdin if line.strip() != '' ]
for i, line in enumerate(lines):
    syllphones, syllables = line.split('\t')
    syllphones = syllphones.replace('|', ' - ').replace(':', ' ').strip()
    # NOTE recovering graphemes back like this would not work 100% of the
    # time because the syllabification is not perfect. For example, word `abl`
    # is mistankenly mapped to the char-only, single syllable `a`.
    # That would end up leading to multiple pronuncications in syllphones
    # dictionary. Fortunately, this has been fixed in `dict2news` script.
    grapheme = syllables.replace('|', '').strip()
    if allow_list is not None:
        if grapheme in allow_list:
            print(f"{grapheme}\t{syllphones.strip('-')}")
            j += 1
    else:
        print(f"{grapheme}\t{syllphones.strip('-')}")
        j += 1
print(f"done! retrieved {j} instances out of {i+1}", file=sys.stderr)
