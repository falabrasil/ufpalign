#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
#
# Grupo FalaBrasil (2020)
# Universidade Federal do Pará
#
# author: may 2019
# cassio batista - https://cassota.gitlab.io/
# last edited: jul 2020

import sys
import os
from queue import Queue
import config
from fb_textgrid import TextGridIO
from FalaBrasilNLP import FalaBrasilNLP

TAG = sys.argv[0]

def write_news2(tg_dataset, fb_phonelist, news_file):
    """ writes a pair of words per news line """

    ds_pair_q = Queue(maxsize=2)
    fb_pair_q = Queue(maxsize=2)
    i = 0
    with open(news_file, 'a') as f:
        for dsphonlist in tg_dataset.get_phonemes():
            phonelist = []
            for dsp in dsphonlist:
                if dsp != '_':
                    phonelist.append(dsp)
            if len(phonelist):
                ds_pair_q.put(list(phonelist))
                phonelist = []
                fbphonlist = fb_phonelist[i]
                for fbp in fbphonlist:
                    if fbp != '_':
                        phonelist.append(fbp)
                fb_pair_q.put(list(phonelist))
                i += 1
            if ds_pair_q.full() and fb_pair_q.full():
                ds_seq = ''
                while not ds_pair_q.empty():
                    seq = ds_pair_q.get()
                    ds_seq += ' '.join(seq) + config.SEP_CROSS
                ds_pair_q.put(list(seq))
                f.write(ds_seq.strip(config.SEP_CROSS) + '\t')
                fb_seq = ''
                while not fb_pair_q.empty():
                    seq = fb_pair_q.get()
                    fb_seq += ' '.join(seq) + config.SEP_CROSS
                fb_pair_q.put(list(seq))
                f.write(fb_seq.strip(config.SEP_CROSS) + '\n')
        # NOTE: helps m2m2tg separate between sentences
        f.write('%s\t%s\n' % (config.DELIM_SENT, config.DELIM_SENT))


if __name__=='__main__':
    if len(sys.argv) != 3:
        print('usage: %s <file_list> <news_file>' % sys.argv[0])
        print('  <file_list> is the input list of .textgrid file paths.')
        print('  <news_file> is the output file in the .news format')
        sys.exit(1)
    if os.path.isfile(sys.argv[2]):
        print('[%s] warning: file \'%s\' will be removed' % (TAG, sys.argv[2]))
        os.remove(sys.argv[2])

    nlp = FalaBrasilNLP()
    io = TextGridIO(sys.argv[1])
    for filepath in io.get_tg_filelist():
        if filepath in config.TG_EXCEPT:
            print('\n[%s] skipping `%s`' % (TAG, filepath))
            continue
        else:
            sys.stdout.write('\r[%s] `%s` ok!' % (TAG, filepath))
            sys.stdout.flush()
        tg_dataset = io.parse_tg_from_file(filepath)
        falabrasil_phones = []
        for word in tg_dataset.get_phrasegraph(nested=False)[0].split():
            phones = nlp.get_g2p(word)
            falabrasil_phones.append(phones.split())

        write_news2(tg_dataset, falabrasil_phones, sys.argv[2])
    sys.stdout.write('\n')
    print('[%s] finished successfully!' % TAG)
