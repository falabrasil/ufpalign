#!/usr/bin/env python3
#
# ctm2tg: a script to convert CTM files from Kaldi aligner
# to Praat's TextGrid format
#
# Grupo FalaBrasil (2024)
# Universidade Federal do Pará
#
# author: apr 2024
# Cassio Batista - https://cassiotbatista.github.io

import argparse
import logging
import os
from collections import OrderedDict
from typing import Dict, List, Tuple, Optional, Union

import pandas as pd
from textgrid import TextGrid, IntervalTier


def get_args():
    parser = argparse.ArgumentParser()
    # https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    parser.add_argument(
        "-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO,
        help="log more"
    )
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
    parser.add_argument(
        "-s", "--syllphones-dictionary", type=str, required=True,
        help="something like 'syllphones.txt'"
    )
    #parser.add_argument(
    #    "-i", "--ignore-syllphones", action="store_true",
    #    help="whether to build the syllphones tier"
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
    if not filename.endswith(".ctm"):
        raise ValueError(f"{filename} doesn't have a *.ctm extension")
    if not os.stat(filename).st_size:
        raise ValueError(f"{filename} appears to be empty")
    logging.debug(f"{filename} is juicy good!")


# https://stackoverflow.com/questions/13479163/round-float-to-x-decimals (#16)
def floatify(val: Union[str, float]) -> float:
    """Convert a string or float to a special kind of float.

    The idea is having only two decimals, and some special rules are applied
    to strings based on observations on how Kaldi provides the float numbers
    in timestamps.

    See https://github.com/falabrasil/ufpalign/issues/16

    Args:
        val: string or float to be floatified
    Returns:
        float: two-decimal floating point timestamp
    """
    if isinstance(val, float):
        return round(float(val), 2)
    if val.endswith("0"):
        return float(val)
    if val.endswith("5"):
        return float(val) - 0.005
    return round(float(val), 2)


# ctm2tg.py    DEBUG phonemes i=7293 bos=754.24 eos=754.34 a_E
# ctm2tg.py    DEBUG phonemes i=7294 bos=754.34 eos=754.38 k_B
# ctm2tg.py    DEBUG phonemes i=7295 bos=754.37 eos=754.44 o_I
# Traceback (most recent call last):
def compute_eos_and_ensure_causality(
    bos: List[float],
    dur: List[float],
    tokens: List[str]
) -> Tuple[List[float], List[float]]:
    """Compute EOS values and fix BOS in order to ensure causality.

    Some tools apply sanity checks over Textgrid files like asserting
    whether the current phone's BOS is smaller than the previous phone's EOS.
    Due to numerical precision problems, Kaldi cannot always assert that, and
    apparently parameter tweaking is no help, which only leave us with the
    option of changing the C++ code and recompiling the binaries, which for
    now is infeasible.

    See https://github.com/falabrasil/ufpalign/issues/16

    Args:
        bos: list of beginning of speech floating point timestamps, from CTM
        dur: list of durations of each phone, from CTM
        tokens: phone symbols
    Returns:
        A tuple with fixed bos and new eos, which is the sum of bos and dur.
    """
    assert len(bos) == len(dur)
    eos = [floatify(b + d) for b, d in zip(bos, dur)]
    for i in range(1, len(bos)):
        prev_bos, curr_bos = bos[i-1], bos[i]
        prev_eos, curr_eos = eos[i-1], eos[i]
        prev_tok, curr_tok = tokens[i-1], tokens[i]
        if curr_bos < prev_eos:
            logging.warning(
                f"causality problem at frame {i=}: "
                f"{prev_bos=:.2f} {prev_eos=:.2f} {prev_tok:4s} | "
                f"{curr_bos=:.2f} {curr_eos=:.2f} {curr_tok:4s}"
            )
            bos[i] = prev_eos
    return bos, eos


def senone_to_monophone(senone: str) -> str:
    """Convert senone symbols to monophone symbols.

    Senones are basically the monophones with beginning, ending or intermediate
    markers. This function basically gets rid of the markers.

    Args:
        senone: a string representing the senone symbol
    Returns:
        a string representing the monophone symbol
    """
    return senone.split("_")[0]


# NOTE load bos as a string and force fit it as a float later when requested
def load_ctm(filename: str) -> pd.DataFrame:
    """Loads a CTM file from disk into a DataFrame in memory.

    """
    logging.info(f"loading {filename} ...")
    check_ctm(filename)
    ctm = pd.read_csv(
        filename, sep=" ", #engine="python",
        names=["uttid", "chid", "bos", "dur", "token"],
        dtype={"uttid": str, "chid": str, "bos": str, "dur": float, "token": str},
    )
    logging.debug(ctm.head(10))
    ctm["token"] = ctm["token"].apply(lambda x: senone_to_monophone(x))
    ctm["bos"] = ctm["bos"].apply(lambda x: floatify(x))
    ctm["dur"] = ctm["dur"].apply(lambda x: floatify(x))
    ctm["bos"], ctm["eos"] = compute_eos_and_ensure_causality(
        ctm["bos"].tolist(), ctm["dur"].tolist(), ctm["token"].tolist()
    )
    ctm = ctm.drop(["dur", "chid"], axis=1)
    ctm = ctm.reindex(["uttid", "bos", "eos", "token"], axis=1)
    logging.debug(ctm.head(10))
    return ctm


# https://stackoverflow.com/questions/18695605/how-to-convert-a-dataframe-to-a-dictionary
def load_dictionary(filename: str) -> Dict[str, str]:
    """Load tab-sep phonetic or syllabic dictionaries

    """
    logging.info(f"loading {filename} ...")
    dictionary = pd.read_csv(
        filename, sep="\t", engine="python", names=["word", "tokens"],
    )
    return OrderedDict(zip(dictionary["word"], dictionary["tokens"]))


def join_tokens_as_a_sentence(
    tokens: List[str],
    lexicon: Optional[Dict[str, str]] = None,
) -> str:
    """Join tokens that belong to the same word, discarding silences.
    
    This is useful for some tiers that comprise the full sentence that has been
    aligned, either as graphemes or phonemes.
    """
    sent = []
    for t in tokens:
        if t in ("<eps>", "sil"):
            continue
        sent.append(lexicon[t].replace(" ", "") if lexicon else t)
    return " ".join(sent).strip()


def build_syllphones_ctm(
    p_ctm: pd.DataFrame,
    g_ctm: pd.DataFrame,
    sp_dict: Dict[str, str],
) -> pd.DataFrame:
    """Tech debt

    """
    df_list = []
    for uttid in g_ctm["uttid"].unique():
        w_df = g_ctm[g_ctm["uttid"] == uttid]
        p_df = p_ctm[p_ctm["uttid"] == uttid]
        ctm = []
        prev_bos = 0.0
        for word in w_df['token']:
            logging.debug(f"fetching syllphones for {word=}")
            syllphones = sp_dict[word]
            logging.debug(f"{syllphones=}")
            for syllable in [s.strip() for s in syllphones.split('-')]:
                last_phone = syllable.split()[-1]
                logging.debug(f"fetching times for {last_phone=}")
                # NOTE the bos condition looks brittle. keep an eye on that.
                eos = p_df[
                    (p_df['token'] == last_phone) & (p_df['bos'] >= prev_bos)
                ]['eos'].tolist()[0]
                ctm.append((uttid, prev_bos, eos, syllable))
                prev_bos = eos
        df = pd.DataFrame(ctm, columns=["uttid", "bos", "eos", "token"])
        df_list.append(df)
    return pd.concat(df_list)


def main(args):

    g_ctm = load_ctm(args.graphemes_ctm_file)
    p_ctm = load_ctm(args.phonemes_ctm_file)
    lexicon = load_dictionary(args.phonetic_dictionary)

    syllphones = load_dictionary(args.syllphones_dictionary)
    s_ctm = build_syllphones_ctm(p_ctm, g_ctm, syllphones)

    os.makedirs(args.output_dir, exist_ok=True)
    for uttid in g_ctm["uttid"].unique():
        w_df = g_ctm[g_ctm["uttid"] == uttid]
        p_df = p_ctm[p_ctm["uttid"] == uttid]
        s_df = s_ctm[s_ctm["uttid"] == uttid]
        # build phonemes tier
        logging.info(f"building 'fonemas' tier...")
        p_tier = IntervalTier(name="fonemas")
        for i, (t, bos, eos) in enumerate(
            zip(p_df["token"], p_df["bos"], p_df["eos"])
        ):
            logging.debug(f"phonemes {i=} {bos=} {eos=} {t}")
            p_tier.add(minTime=bos, maxTime=eos, mark=t)
        # build graphemes tier
        logging.info(f"building 'grafemas' tier...")
        w_tier = IntervalTier(name="grafemas")
        for t, bos, eos in zip(w_df["token"], w_df["bos"], w_df["eos"]):
            w_tier.add(minTime=bos, maxTime=eos, mark=t)
        # build syllphones tier
        logging.info(f"building 'silabas-fonemas' tier...")
        s_tier = IntervalTier(name="silabas-fonemas")
        for t, bos, eos in zip(s_df["token"], s_df["bos"], s_df["eos"]):
            s_tier.add(minTime=bos, maxTime=eos, mark=t)
        # build phoneme sentence tier
        logging.info(f"building 'frase-fonemas' tier...")
        ps_tier = IntervalTier(name="frase-fonemas")
        bos = sorted(p_df["bos"].tolist())[0]
        eos = sorted(p_df["eos"].tolist())[-1]
        t = join_tokens_as_a_sentence(w_df["token"].tolist(), lexicon=lexicon)
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
        for tier in (p_tier, w_tier, s_tier, ps_tier, gs_tier):
            tg.append(tier)
        # save texgrid to file
        fout = f"{uttid}.TextGrid"
        fout = os.path.join(os.path.realpath(args.output_dir), fout)
        logging.info(f"dumping textgrid to file {fout} ...")
        tg.write(f=fout)


if __name__ == "__main__":

    args = get_args()
    logging.basicConfig(
        format="%(filename)s %(levelname)8s %(message)s", level=args.loglevel
    )
    logging.info(args)
    main(args)
    logging.debug("Sucesso meu jovem!!")
