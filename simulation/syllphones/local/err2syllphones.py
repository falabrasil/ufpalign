#!/usr/bin/env python3

import sys

j = 0
lines = [ line.strip() for line in sys.stdin if line.strip() != '' ]
for i, line in enumerate(lines):
    phonemes, syllables = line.split('\t')
    phonemes, syllables = phonemes.strip(), syllables.strip()
    # save only single-syllable words. screw the others
    if syllables.count(' ') == 0:
        syllphones = phonemes
        j += 1
    else:
        print(f" ** irrecovarable pair: {phonemes=} {syllables=}", file=sys.stderr)
        continue
    # NOTE recovering graphemes back like this does not work 100% of the
    # time because the syllabification is not perfect. For example, word `abl`
    # is mistankenly mapped a char-only, single syllable `a`.
    # That leads to multiple pronuncications in syllphones dictionary.
    # Fortunately, this has been fixed in `dict2news` script.
    grapheme = syllables.replace(' ', '').strip()
    print(f"{grapheme}\t{syllphones.strip('-')}")
print(f"done! saved {j} instances out of {i+1}", file=sys.stderr)
