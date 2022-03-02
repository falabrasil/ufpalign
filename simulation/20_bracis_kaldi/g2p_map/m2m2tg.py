#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
#
# Grupo FalaBrasil (2020)
# Universidade Federal do Pará
#
# author: mar 2020
# cassio batista - https://cassota.gitlab.io/
# last edited: jul 2020

import sys
import os

from queue import Queue
from termcolor import colored
import config

from fb_textgrid import TextGrid, TextGridIO

TAG = sys.argv[0]
PADD = list('###')
DEGUB = False

def is_vowel(ch):
    """ check if a char is a vowel """

    if ch.lower() in list('aeiou'):
        return True
    return False


def m2m_bi2uni(m2m_list):
    """ Splits a bigram word model into a unique unigram word model

        i=11, j=3           i=10, j=3          i=9,10,11,12, j=3,4,5,6
        ###leilatem###      ###leilatem###     ###leilatem###
               ###temum###        ###temum###       ###temum###
                  ^                  ^                 ^^^^       m: mismatch
                  m                  m                 MMMm       M: match
    """

    q = Queue(maxsize=2)
    phonemes_list = []
    while len(m2m_list):  # NOTE can be optmised removing this while
        while not q.full():
            bigram = m2m_list.pop(0)
            q.put(PADD + bigram + PADD)
        curr_word = q.get()
        next_word = q.get()
        i = len(curr_word) - 1 - len(PADD) # to decrease backwards
        j = len(PADD)                      # to increase forward
        unmatch_count = 0
        match = False
        #print(curr_word, '***********************************')
        #print(next_word, '***********************************')
        while not match:
            # scan the first section: mismatch (m)
            while curr_word[i] != next_word[j]:
                #print('%-6s %-6s %02d %02d  <- bi2uni' % (curr_word[i], 
                #                                          next_word[j], i, j))
                i -= 1
                unmatch_count += 1
            #print('%-6s %-6s' % (curr_word[i], next_word[j]))
            # gambiarra master to avoid mismatches like in 's e j s'
            if unmatch_count == 0 and not is_vowel(curr_word[i][0]):
                i -= 1
                unmatch_count += 1
                continue
            #print('possible match')
            for k in range(unmatch_count + len(PADD)):
                # scan the second section: a match (M)
                if curr_word[i + k] == next_word[j + k]:
                    continue
                else:  
                    # found third section: right mismatch with PADD (m)
                    if curr_word[i + k] == '#':  # check immediate mismatch
                        match = True
                        #print('match! ->', end=' ')
                        #print(curr_word[len(PADD):i])
                    else:
                        #print('houston we have a problem: (%s, %s)' %
                        #      (curr_word[i + k], next_word[j + k]))
                        i -= 1
                        unmatch_count += 1
                    break
        phonemes_list.append(curr_word[len(PADD):i])
        q.put(next_word)
    phonemes_list.append(next_word[len(PADD):j + k])
    phonemes_list.append(next_word[j + k:-len(PADD)])
    return phonemes_list


def map_ds_m2m_to_tg(m2m, tg):
    """ Maps dataset's tg (including timestamps) to new tg using m2m aligns

        it also merges two or more phonemes into one, which affects
        timestamps
    """

    phonemes = list(tg.get_phonemes())
    timestamps = list(tg.get_phoneme_timestamps())
    #print(phonemes, '>>>>>>>>>>>>>>>>>>>>>>>>>')
    #print(timestamps, '>>>>>>>>>>>>>>>>>>>>>>>>>>')
    tg_ali = TextGrid(init_default_items=True)
    tg_ali.add_phoneme_timestamp(0.0)
    time_i = 1
    while len(phonemes):
        i = 0
        j = 0
        tg_word = phonemes.pop(0)
        if tg_word == ['_']:
            tg_ali.add_phonemes(list(tg_word))
            tg_ali.add_phoneme_timestamp(timestamps[time_i])
            time_i += 1
            continue
        m2m_word = m2m.pop(0)
        #print(i, j, tg_word, m2m_word)
        #print('###', tg_ali.get_phonemes())
        if tg_word == m2m_word:
            tg_ali.add_phonemes(list(tg_word))
            for phone in tg_word:
                tg_ali.add_phoneme_timestamp(timestamps[time_i])
                time_i += 1
            continue
        phones = []
        times = []
        while i < len(tg_word):
            #print('>>>>>>>>>>>', phones, i, j, tg_word[i], m2m_word[j])
            if tg_word[i] == '_':
                phones.append(tg_word[i])
                times.append(timestamps[time_i])
                i += 1
                time_i += 1
            elif tg_word[i] == m2m_word[j]:
                #print('eita jesus', phones, times, timestamps[time_i])
                phones.append(m2m_word[j])
                times.append(timestamps[time_i])
                i += 1
                j += 1
                time_i += 1
            elif tg_word[i].count(':') > 0:
                print('what the fuck this is weird')
            elif m2m_word[j].count(':') > 0:
                diphon = True
                for k, dp in enumerate(m2m_word[j].split(':')):
                    if dp != tg_word[i]:
                        print('what the hell is going on here')
                        diphon = False
                        break
                    i += 1
                if diphon:
                    phones.append(m2m_word[j])
                    #times.append(sum(timestamps[time_i:time_i + k + 1]))
                    times.append(timestamps[time_i + k])
                    time_i += k + 1
                j += 1
        tg_ali.add_phonemes(list(phones))
        for t in times:
            tg_ali.add_phoneme_timestamp(t)
    # FIXME CB: right now we only have interest in phonemes so every other
    #       tier will be copied *as it is* from the original TextGrid,
    #       which means phones will not be broken or split.
    tg_ali.set_syllphones(tg.get_syllphones())                           # 2
    tg_ali.set_syllphone_timestamps(tg.get_syllphone_timestamps())
    tg_ali.set_wordgraphs(tg.get_wordgraphs())                           # 3
    tg_ali.set_wordgraph_timestamps(tg.get_wordgraph_timestamps())
    tg_ali.set_phrasephone(tg.get_phrasephone(nested=False))             # 4b
    tg_ali.set_phrasephone_timestamps(tg.get_phrasephone_timestamps())
    tg_ali.set_phrasegraph(tg.get_phrasegraph(nested=False))             # 5
    tg_ali.set_phrasegraph_timestamps(tg.get_phrasegraph_timestamps())
    #print(tg_ali.get_phonemes(), '<<<<<<<<<<<<<<<<<<<<')
    #print(tg_ali.get_phoneme_timestamps(precision=2), '<<<<<<<<<<<<<<<<<<<<')
    return tg_ali.lower()


def map_fb_m2m_to_tg(m2m, tg):
    """ map dataset's new aligned tg to falabrasil's tg, using m2m phones

        it also splits a phoneme into two or more, which affects
        timestamps
    """

    phonemes = list(tg.get_phonemes())
    timestamps = list(tg.get_phoneme_timestamps())
    #print(tg.get_phoneme_timestamps(precision=2))
    tg_ali = TextGrid(init_default_items=True)
    tg_ali.add_phoneme_timestamp(0.0)
    time_i = 1
    while len(phonemes):
        i = 0
        j = 0
        tg_word = phonemes.pop(0)
        if tg_word == ['_']:
            tg_ali.add_phonemes(list(tg_word))
            tg_ali.add_phoneme_timestamp(timestamps[time_i])
            time_i += 1
            continue
        m2m_word = m2m.pop(0)
        #print(i, j, tg_word, m2m_word, '*********************')
        #print('%%%', tg_ali.get_phonemes())
        if tg_word == m2m_word:
            tg_ali.add_phonemes(list(tg_word))
            for phone in tg_word:
                tg_ali.add_phoneme_timestamp(timestamps[time_i])
                time_i += 1
            continue
        phones = []
        times = []
        #print(m2m_word, j, '########################')
        while i < len(tg_word):
            #print(phones, i, j, tg_word[i], m2m_word[j])
            if tg_word[i] == '_':
                phones.append(tg_word[i])
                times.append(timestamps[time_i])
                i += 1
                time_i += 1
            elif m2m_word[j].count(':') > 0:
                #print(m2m_word[j], '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                for k, dp in enumerate(m2m_word[j].split(':')):
                    phones.append(dp)
                i += 1
                #print(phones)
                #if time_i + 1 < len(timestamps):
                #    #time_off = timestamps[time_i + 1] - timestamps[time_i - 1]
                #    time_off = timestamps[time_i] - timestamps[time_i - 1]
                #    time_off = time_off / float(k + 2)
                #else:
                time_off = timestamps[time_i] - timestamps[time_i - 1]
                time_off = time_off / (k + 1)  # CB: FIXED
                for t in range(1, k + 2):
                    times.append(timestamps[time_i - 1] + float(t) * time_off)
                time_i += 1
                j += 1
            else: # one to one map, swift!
                #print('eita jesus', phones, times)
                phones.append(m2m_word[j])
                times.append(timestamps[time_i])
                i += 1
                j += 1
                time_i += 1
        tg_ali.add_phonemes(list(phones))
        for t in times:
            tg_ali.add_phoneme_timestamp(t)
    # FIXME CB: right now we only have interest in phonemes so every other
    #       tier will be copied *as it is* from the original TextGrid,
    #       which means phones will not be broken or split.
    tg_ali.set_syllphones(tg.get_syllphones())                           # 2
    tg_ali.set_syllphone_timestamps(tg.get_syllphone_timestamps())
    tg_ali.set_wordgraphs(tg.get_wordgraphs())                           # 3
    tg_ali.set_wordgraph_timestamps(tg.get_wordgraph_timestamps())
    #tg_ali.set_phrasephone(tg.get_phrasephone(nested=False))             # 4b
    phrasephone = ''
    for l in tg_ali.get_phonemes():
        for p in l:
            if p != '_':
                phrasephone += p
        phrasephone += ' '
    tg_ali.set_phrasephone([phrasephone.strip()])                        # 4b
    tg_ali.set_phrasephone_timestamps(tg.get_phrasephone_timestamps())
    tg_ali.set_phrasegraph(tg.get_phrasegraph(nested=False))             # 5
    tg_ali.set_phrasegraph_timestamps(tg.get_phrasegraph_timestamps())
    return tg_ali.lower()

def transpose_m2m(m2m_list):
    """ converts single line single column to multi line double column """

    ds_list, fb_list = [], []
    for entry in m2m_list:
        if entry == '':
            continue
        ds, fb = entry.split('\t')
        ds_list.append(ds.strip('|').split('|'))
        fb_list.append(fb.strip('|').split('|'))
    return ds_list, fb_list

def divide():
    print('-----------------------------------------------------', end='')
    print('-----------------------------------------------------', end='')
    print('-----------------------------------------------------', end='')
    print('-----------------------------------------------------')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: %s <file_list> <m2m_file> <tg_outdir>')
        print('  <file_list> is a list of .textgrid file paths')
        print('  <m2m_file> is a list of .textgrid file paths')
        print('  <tg_outdir> is the dir to store the mapped tg files')
        sys.exit(1)

    if os.path.isdir(sys.argv[3]):
        print('warning: dir `%s` exists and will be overwritten' % sys.argv[3])
    else:
        os.mkdir(sys.argv[3])

    # TODO use arparse for file names
    with open(sys.argv[2], 'r') as f:
        m2m = f.read().split('%s|\t%s|\n' % (config.DELIM_SENT, config.DELIM_SENT))

    io = TextGridIO(sys.argv[1])  # TODO use argparse instead
    for index, filepath in enumerate(io.get_tg_filelist()):
        tg_dataset = io.parse_tg_from_file(filepath)
        if filepath in config.TG_EXCEPT:
            print(colored('[%s] `%s` skp' % (TAG, filepath), 'red'),
                  end=' ')
            print(tg_dataset.get_phrasegraph(), end=' -> ')
            print(tg_dataset.get_phrasephone())
            if DEGUB:
                divide()
            continue
        elif filepath in config.TG_HEAVY_CROSS:
            print(colored('[%s] `%s` skp' % (TAG, filepath), 'yellow'),
                  end=' ')
            print(tg_dataset.get_phrasegraph(), end=' -> ')
            print(tg_dataset.get_phrasephone())
            m2m.pop(0) # print this if you want
            if DEGUB:
                divide()
            continue
        else:
            print(colored('[%s] `%s` ok!' % (TAG, filepath), 'green'),
                  end=' ')
            print(tg_dataset.get_phrasegraph(), end=' -> ')
            print(tg_dataset.get_phrasephone())
        #print('inspect tg_datset:')
        #tg_dataset.inspect()
        # NOTE do I really need pop here? indexing list myabe?
        m2m_dataset, m2m_falabrasil = transpose_m2m(m2m.pop(0).split('\n'))
        if DEGUB:
            print('mds bi ', m2m_dataset)
            print('mfb bi ', m2m_falabrasil)
        # unfold bigram word representation into single word representation
        m2m_dataset = m2m_bi2uni(m2m_dataset)
        m2m_falabrasil = m2m_bi2uni(m2m_falabrasil)
        if DEGUB:
            print('mds uni', m2m_dataset)
            print('mfb uni', m2m_falabrasil)
        # map phones and timestamps from datasets
        tg_dataset_align    = map_ds_m2m_to_tg(m2m_dataset, tg_dataset)
        #print('inspect tg_datset_align:')
        #tg_dataset_align.inspect()
        tg_falabrasil_align = map_fb_m2m_to_tg(m2m_falabrasil, tg_dataset_align)
        #print('inspect tg_falabrasil_align:')
        #tg_falabrasil_align.inspect()
        if DEGUB:
            print('ds file', tg_dataset.get_phonemes())
            print('tg dsa ', tg_dataset_align.get_phonemes())
            print('tg fba ', tg_falabrasil_align.get_phonemes())
            divide()
        outfile = os.path.join(sys.argv[3], os.path.basename(filepath))
        io.write_tg_to_file(tg_falabrasil_align, outfile)

    sys.stderr.write('[%s] finished successfully!' % TAG)
    sys.stderr.write('                               \n')  # hehe
