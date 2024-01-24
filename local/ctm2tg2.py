#!/usr/bin/env python3
#
# author: jan 2024
# Cassio Batista - https://cassiotbatista.github.io

import argparse
import logging
import os
from collections import OrderedDict
from typing import Dict, List, Tuple, Optional

import pandas as pd
from textgrid import TextGrid, IntervalTier


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g", "--graphemes-ctm-file", type=str, required=True,
        help="something like 'mono.graphemes.ctm'"
    )
    parser.add_argument(
        "-p", "--phonemes-ctm-file", type=str, required=True,
        help="something like 'mono.phonemes.ctm'"
    )
    parser.add_argument(
        "-l", "--phonetic-dictionary", type=str, required=True,
        help="something like 'lexicon.txt'"
    )
    #parser.add_argument(
    #    "-s", "--syllabic-dictionary", type=str, required=True,
    #    help="something like 'syll.txt'"
    #)
    parser.add_argument(
        "-i", "--ignore-syllphones", action="store_true",
        help="whether to ignore the syllabe-phonemes tier"
    )
    ## TODO make it --keep-sil with "store_false". not sure if it applies
    #parser.add_argument(
    #    "-e", "--skip-sil", action="store_true",
    #    help="ignore silence phones in the output. only works for 'frases' tiers"
    #)
    parser.add_argument(
        "-o", "--output-dir", type=str, required=True,
        help="directory to dump TextGrid files"
    )
    return parser.parse_args()


# https://stackoverflow.com/questions/2507808/how-to-check-whether-a-file-is-empty-or-not
def check_ctm(filename: str) -> None:
    if not os.path.isfile(filename):
        raise ValueError(f"{filename} does not exist")
    elif not filename.endswith(".ctm"):
        raise ValueError(f"{filename} doesn't have a *.ctm extension")
    elif not os.stat(filename).st_size:
        raise ValueError(f"{filename} appears to be empty")
    logging.debug(f"{filename} is juicy good!")


# https://stackoverflow.com/questions/13479163/round-float-to-x-decimals
def floatify(val: str) -> float:
    if val.endswith("0"):
        return float(val)
    elif val.endswith("5"):
        return float(val) - 0.005
    return round(float(val), 2)


# NOTE load bos as a string and force fit it as a float later
def load_ctm(filename: str, round_bos: bool = False) -> pd.DataFrame:
    check_ctm(filename)
    ctm = pd.read_csv(
        filename, sep=" ", #engine="python",
        names=["uttid", "chid", "bos", "dur", "token"],
        dtype={"uttid": str, "chid": str, "bos": str, "dur": float, "token": str},
    )
    ctm["bos"] = ctm["bos"].apply(lambda x: floatify(x) if round_bos else float(x))
    ctm["eos"] = ctm["bos"] + ctm["dur"]
    ctm["bos"] = ctm["bos"].apply(lambda x: float(f"{x * 1000 / 1000.0:.2f}"))
    ctm["eos"] = ctm["eos"].apply(lambda x: float(f"{x * 1000 / 1000.0:.2f}"))
    ctm = ctm.drop(["dur"], axis=1)
    ctm = ctm.reindex(["uttid", "chid", "bos", "eos", "token"], axis=1)
    logging.debug(ctm.head())
    return ctm


# https://stackoverflow.com/questions/18695605/how-to-convert-a-dataframe-to-a-dictionary
def load_lexicon(filename: str) -> Dict[str, str]:
    """load tab-sep phonetic or syllabic dictionaries"""
    lex = pd.read_csv(
        filename, sep="\t", engine="python", names=["word", "tokens"],
    )
    return OrderedDict(zip(lex["word"], lex["tokens"]))


def join_tokens_as_a_sentence(
    tokens: List[str], lexicon: Optional[Dict[str, str]] = None,
) -> str:
    sent = []
    for t in tokens:
        if t == "<eps>" or t == "sil":
            continue
        sent.append(lexicon[t].replace(" ", "") if lexicon else t)
    return " ".join(sent).strip()


def main(args) -> None:

    g_ctm = load_ctm(args.graphemes_ctm_file)
    p_ctm = load_ctm(args.phonemes_ctm_file, round_bos=True)
    #syll = load_lexicon(args.syllabic_dictionary)
    lex = load_lexicon(args.phonetic_dictionary)

    os.makedirs(args.output_dir, exist_ok=True)
    for uttid in g_ctm["uttid"].unique():
        w_df = g_ctm[g_ctm["uttid"] == uttid]
        p_df = p_ctm[p_ctm["uttid"] == uttid]
        # build phonemes tier
        logging.info(f"building 'fonemas' tier...")
        p_tier = IntervalTier(name="fonemas")
        for t, bos, eos in zip(p_df["token"], p_df["bos"], p_df["eos"]):
            p_tier.add(minTime=bos, maxTime=eos, mark=t)
        # build graphemes tier
        logging.info(f"building 'grafemas' tier...")
        w_tier = IntervalTier(name="grafemas")
        for t, bos, eos in zip(w_df["token"], w_df["bos"], w_df["eos"]):
            w_tier.add(minTime=bos, maxTime=eos, mark=t)
        # build phoneme sentence tier
        logging.info(f"building 'frase-fonemas' tier...")
        ps_tier = IntervalTier(name="frase-fonemas")
        bos = sorted(p_df["bos"].tolist())[0]
        eos = sorted(p_df["eos"].tolist())[-1]
        t = join_tokens_as_a_sentence(w_df["token"].tolist(), lexicon=lex)
        ps_tier.add(minTime=bos, maxTime=eos, mark=t)
        # build grapheme sentence tier
        logging.info(f"building 'frase-grafemas' tier...")
        gs_tier = IntervalTier(name="frase-grafemas")
        bos = sorted(w_df["bos"].tolist())[0]
        eos = sorted(w_df["eos"].tolist())[-1]
        t = join_tokens_as_a_sentence(w_df["token"].tolist())
        gs_tier.add(minTime=bos, maxTime=eos, mark=t)
        # compose textgrid
        logging.info(f"composing textgrid by attaching tiers...")
        tg = TextGrid()
        for tier in (p_tier, w_tier, ps_tier, gs_tier):
            tg.append(tier)
        # save texgrid to file
        fout = f"{uttid}.TextGrid"
        fout = os.path.join(os.path.realpath(args.output_dir), fout)
        logging.info(f"dumping textgrid to file {fout} ...")
        tg.write(f=fout)


if __name__ == "__main__":

    logging.basicConfig(
        format="%(filename)s %(levelname)8s %(message)s",
        level=logging.INFO
    )

    args = get_args()
    main(args)
