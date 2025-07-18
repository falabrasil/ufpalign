#!/usr/bin/env python3
#
# m2m_aligner: aligns a phonetic sequence to a syllabic sequence based on
# pre-estimated m2m aligner token-pair probs
#
# Old command:
# $M2M_ROOT/m2m-aligner \
#  --maxFn conXY \
#  --maxX 4 \
#  --maxY 1 \
#  --inputFile sp.news.tmp \
#  --outputFile sp.ali.tmp \
#  --alignerIn $UFPALIGN_DIR/m2m.model
#
# Grupo FalaBrasil (2025)
# Universidade Federal do Pará
#
# author: jul 2025
# Cassio T Batista - https://cassiotbatista.github.io
# last update: jul 2025

import argparse
import logging
from typing import Dict, Tuple, List
from dataclasses import dataclass

import numpy as np


@dataclass
class Table:
    score: float
    back_x: int
    back_y: int
    back_r: int


def read_news(filename: str) -> Tuple[List[Tuple[str]], List[Tuple[str]]]:
    phones, syllables = [], []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            p, s = line.split("\t")
            phones.append(tuple(p.strip().split()))
            syllables.append(tuple(s.strip().split()))
    return phones, syllables


def viterbi_align(
    x: Tuple[str],
    y: Tuple[str],
    probs: Dict[Tuple[str, str], float],
    args
) -> Tuple[List[str], List[str]]:
    align_x, align_y = [], []
    q_tmp = Table(score=0, back_x=-1, back_y=-1, back_r=-1)
    Q = [
        [ [] for _ in range(len(y) + 1) ]  # Inner vector_2qtable
        for _ in range(len(x) + 1)         # Outer vector_3qtable
    ]
    Q[0][0].append(q_tmp)
    for xl in range(len(x) + 1):
        for yl in range(len(y) + 1):
            if xl > 0 and yl > 0:
                for i in range(1, args.max_x + 1):
                    if xl - i < 0:
                        break
                    for j in range(1, args.max_y + 1):
                        if yl - j < 0:
                            break
                        if not args.eq_map:
                            if i == j and i > 1:
                                continue
                        ss_x = "".join(x[xl-i:xl-i+i])
                        ss_y = "".join(y[yl-j:yl-j+j])
                        prob = probs[(ss_x, ss_y)] if (ss_x, ss_y) in probs else 0
                        score = np.log(prob) * max(i, j) if prob > 0 else float("-inf")
                        logging.debug(f"{ss_x} {ss_y} {prob} {score}")
                        for rindex in range(len(Q[xl-i][yl-j])):
                            logging.debug(
                                f"{xl-i} {yl-j} <- {xl} {yl} | {rindex}"
                                f"{Q[xl-i][yl-j][rindex].score}"
                            )
                            q_tmp = Table(
                                score=score + Q[xl-i][yl-j][rindex].score,
                                back_x=i,
                                back_y=j,
                                back_r=rindex
                            )
                            Q[xl][yl].append(q_tmp)
            # reduce size of n-best
            if len(Q[xl][yl]) > 1:
                Q[xl][yl] = sorted(
                    Q[xl][yl], key=lambda item: item.score, reverse=True
                )[:1]

    # sorting
    Q[len(x)][len(y)] = sorted(
        Q[len(x)][len(y)], key=lambda item: item.score, reverse=True
    )

    # backtracking
    #if len(Q[len(x)][len(y)]) <= 0:
    #    break
    score = Q[len(x)][len(y)][0].score
    logging.debug(f"{score=} !! ")
    # if score indicates a proper alignment
    if score > -1e12:
        xxl, yyl = len(x), len(y)
        back_r = 0
        align_x_tmp, align_y_tmp = [], []
        while xxl > 0 or yyl > 0:
            move_x = Q[xxl][yyl][back_r].back_x
            move_y = Q[xxl][yyl][back_r].back_y
            back_r = Q[xxl][yyl][back_r].back_r
            logging.debug(f"{xxl} {yyl} {move_x} {move_y}")
            align_x_tmp.append(
                args.sep_in_char.join(x[xxl-move_x:xxl-move_x+move_x])
                if move_x > 0 else args.null_char
            )
            align_y_tmp.append(
                args.sep_in_char.join(y[yyl-move_y:yyl-move_y+move_y])
                if move_y > 0 else args.null_char
            )
            xxl -= move_x
            yyl -= move_y
        align_x.append(list(reversed(align_x_tmp)))
        align_y.append(list(reversed(align_y_tmp)))
    # delete top guy
    del Q[len(x)][len(y)]

    return align_x, align_y, score


def read_aligner_from_file(filename: str) -> Dict[Tuple[str, str], float]:
    with open(filename) as f:
        model = f.readlines()
    probs = {}
    for line in model:
        line = line.strip()
        if line == "":
            continue
        p, s, prob = line.split("\t")
        pair = (p.strip(), s.strip())
        assert pair not in probs, pair
        probs[(pair)] = float(prob)
    return probs


def main(args):

    word_x, word_y = read_news(args.input_file)
    probs = read_aligner_from_file(args.aligner_in)
    assert len(word_x) == len(word_x)

    align_count = 0
    no_align_count = 0
    num_words = len(word_x)
    with open(args.output_file, "w") as fout, open(args.output_file + ".err", "w") as ferr:
        for i in range(num_words):
            align_x, align_y, score = viterbi_align(word_x[i], word_y[i], probs, args)
            if len(align_x) > 0 and len(align_y) > 0:
                x = args.sep_char.join(align_x[0]).strip() + args.sep_char
                y = args.sep_char.join(align_y[0]).strip() + args.sep_char
                fout.write(f"{x}\t{y}\n")
                align_count += 1
            else:
                x = " ".join(word_x[i])
                y = " ".join(word_y[i])
                ferr.write(f"{x}\t{y}\n")
                no_align_count += 1

    logging.info(f"Aligned {align_count} pairs")
    if (no_align_count > 0):
        logging.info(f"No aligned {no_align_count} pairs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="m2m-aligner")
    # https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    parser.add_argument(
        "-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO,
        help="log more"
    )
    parser.add_argument("--max_x", type=int, default=2)
    parser.add_argument("--max_y", type=int, default=2)
    parser.add_argument("--eq_map", action="store_true")
    parser.add_argument("--null_char", type=str, default="_")
    parser.add_argument("--sep_char", type=str, default="|")
    parser.add_argument("--sep_in_char", type=str, default=":")
    parser.add_argument("--output_file", type=str, required=True, help="ali")
    parser.add_argument("--input_file", type=str, required=True, help="news")
    parser.add_argument("--aligner_in", type=str, required=True, help="model probs")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(filename)s %(levelname)s %(message)s",
        level=args.loglevel
    )

    for k, v in vars(args).items():
        logging.debug(f"{k} {v}")

    main(args)
