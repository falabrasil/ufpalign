#!/usr/bin/env python3
#
# convert lexicon.txt and syllable.txt files into a file in the news format
# required by the m2m aligner. Could be easily done with awk if locale issues
# were not messing up with the order ot the `sort` command: graphemes had to
# match in a line by line fashion across both files, but they were not.
#
# author: feb 2025
# Cassio T Batista - https://cassiotbatista@github.io

import argparse
import logging
import re
from collections import OrderedDict

import icu


logging.basicConfig(
    format="%(filename)s %(levelname)8s %(message)s", level=logging.INFO
)


def main(args):
    lex = OrderedDict()
    with open(args.lex_file) as f:
        lines = [ line.strip() for line in f if line.strip() != '' ]
    for line in lines:
        g, _, p = line.partition('\t')
        if g in ("!SIL", "<UNK>"):
            continue
        lex[g.strip()] = re.sub(r"\s+", " ", p).strip()

    syll = OrderedDict()
    with open(args.syll_file) as f:
        lines = [ line.strip() for line in f if line.strip() != '' ]
    for line in lines:
        g, _, s = line.partition('\t')
        syll[g.strip()] = re.sub(r"\s+", " ", s.replace('-', ' ')).strip()

    # sanity check: dict sizes should match
    assert len(lex) == len(syll), f"{len(lex)} {len(syll)}"

    # fix bad syllabification
    lut = OrderedDict()
    deny_list = set()
    for g, s in syll.items():
        if s.replace(' ', '') != g or s.count(' ') == 0:
            keep = True
            deny_list.add(g)
            if s.replace(' ', '') == g[:-1]:
                logging.warning(f"fixing bad trimmed syll: {g=} {s=}")
                syll[g] = s + g[-1]
            elif s.replace(' ', '') == g[:-2]:
                logging.warning(f"fixing bad trimmed syll: {g=} {s=}")
                syll[g] = s + g[-2:]
            elif len(s.replace(' ', '')) < 3:  # 3 syllables at most
                logging.warning(f"fixing bad syll: {g=} {s=}")
                syll[g] = g  # bypass syll and make its value same as grapheme
            elif s.count(' ') == 0:
                logging.warning(f"lut'ing monossyl: {g=} {s=}")
                syll[g] = s  # monossylables
            else:
                logging.warning(f"discarding bad syll: {g=} {s=}")
                keep = False
            if keep:
                lut[g] = syll[g]
    for g in deny_list:
        del syll[g]

    # https://stackoverflow.com/questions/1653970/does-python-have-an-ordered-set
    #keys = set(lex.keys()).union(set(syll.keys()))
    collator = icu.Collator.createInstance(icu.Locale('pt_BR.UTF-8'))
    keys = set(lex.keys()).intersection(set(syll.keys()))
    keys = dict.fromkeys(sorted(list(keys), key=collator.getSortKey))
    for g in keys:
        if g in lex.keys() and g in syll.keys():
            p = lex[g]
            s = syll[g]
            if p == '' or s == '':
                logging.error(f" ** problem in {g=}: {p=} {s=}")
                continue
            print(f"{p}\t{s}")
        else:
            # should never reach here if the intersection operator is used
            logging.critical(f" ** missing grapheme {g}")

    with open(args.m2m_lut_file, "w") as f:
        for g, s in lut.items():
            p = lex[g]
            # TODO fix manually the syllphones by stitching s and p.
            # so far phonemes are copied as is.
            f.write(f"{g}\t{p}\n")  # FIXME


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--m2m_lut_file", type=str, required=True)
    parser.add_argument("lex_file")
    parser.add_argument("syll_file")
    args = parser.parse_args()

    logging.info(args)
    main(args)
