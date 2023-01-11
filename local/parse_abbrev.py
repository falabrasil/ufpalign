#!/usr/bin/env python3
#
# Grupo FalaBrasil (2021)
# Universidade Federal do Pará (UFPA)
# License: MIT
#
# corrige transcrição fonética de siglas.
# assume como "sigla" apenas palavras que 
# não contêm nenhuma vogal.
# NOTE: this only handles non-ASCII phoneset!
# this should be temporary until somebody
# integrates it into our G2P source code.
#
# author: jun 2021
# cassio batista - https://cassota.gitlab.io

import sys
import os
import logging
from collections import OrderedDict

import unidecode

logging.basicConfig(
    format="%(filename)s %(levelname)8s %(message)s",
    level=logging.INFO
)

# letter to phoneme mapping
L2P = {
    "-": " ",
    "a": "a",
    "b": "b e",
    "c": "s e",
    "ç": "s e",
    "d": "d e",
    "e": "E",
    "f": "E f i",
    "g": "g e",
    "h": "a g a",
    "i": "i",
    "j": "Z O t a",
    "k": "k a",
    "l": "E l i",
    "m": "e~ m i",
    "n": "e~ n i",
    "o": "O",
    "p": "p e",
    "q": "k e",
    "r": "E R i",
    "s": "E s i",
    "t": "t e",
    "u": "u",
    "v": "v e",
    "w": "d a b l i w",
    "x": "S i j s",
    "y": "i p s i l o~",
    "z": "z e"
}


if __name__ == "__main__":

    # scan lexicon for abbrevs: if it has at least one vowel, it isn't
    # NOTE: partition() doesn't raise if phonemes are null; split() does
    new_dict = OrderedDict()
    for line in sys.stdin:
        graph, _, phones = line.strip().partition("\t")
        graph, phones = graph.strip(), phones.strip()
        if graph in ("!SIL", "<UNK>"):
            logging.info(f"skipping special symbol {graph}")
            new_dict[graph] = phones
            continue
        if phones == "":
            logging.warning(f"empty phones for {graph}. fixing...")
            phones = " ".join(L2P[unidecode.unidecode(c)] for c in list(graph))
        is_abbrev = True
        for char in list(graph):
            # this script only handles consonants.
            # make sure none of the letters is or sounds like a vowel.
            if char in "aeiouáéíóúàèìòùâêîôûãõy":
                new_dict[graph] = phones
                is_abbrev = False
                break
        if is_abbrev:
            logging.warning(f"potential abbrev: {graph}")
            try:
                new_dict[graph] = " ".join(L2P[c] for c in list(graph))
            except KeyError:  # e.g.: "pç", "abç"
                logging.error(f"unfixable phones in {graph}")
                raise

    # write new lexicon
    for key, value in new_dict.items():
        print("%s\t%s" % (key, value))
