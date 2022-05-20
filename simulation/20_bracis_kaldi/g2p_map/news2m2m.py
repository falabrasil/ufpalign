#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
#
# Grupo FalaBrasil (2020)
# Universidade Federal do Pará
#
# author: apr 2020
# cassio batista - https://cassota.gitlab.io/
# last edited: jul 2020

import sys
import os
import subprocess
import config
import tempfile
import shutil


TAG = sys.argv[0]
# [fb] |j:s -> :j|s # bring semivowel j close to the left vowel rather than
                    # close to the consonant s
MAPPINGS = {'~|m:': '~:m|', '~|n:': '~:n|', ':d|Z': '|d:Z', 'd|Z:': 'd:Z|'}


# https://note.nkmk.me/en/python-str-replace-translate-re-sub/
def fix_misaligns(m2mfile):
    tmp = os.path.join(tempfile.gettempdir(), 'm2m')
    with open(m2mfile, 'r') as fin:
        aligns = fin.readlines()
    with open(tmp, 'w') as fout:
        count = 0
        for seqpair in aligns:
            count += 1
            ds, fb = seqpair.strip().split('\t')
            for key, value in MAPPINGS.items():
                ds = ds.replace(key, value)
            if '~|_' in fb and ('~|m' in ds or '~|n' in ds or '~|j' in ds):
                if fb.count('~|_') < ds.count('~|m') + ds.count('~|n') + ds.count('~|j'):
                    #print(count, '##', ds, '##', fb, '##')
                    fbi = fb.split('|').index('_') # get index of deletion
                    dsl = ds.split('|')
                    dsl[fbi] = ':' + dsl[fbi] # add joint to the same index
                    ds = '|'.join(dsl).replace('|:', ':') # gambiarra
                else:
                    ds = ds.replace('~|m', '~:m')
                    ds = ds.replace('~|n', '~:n')
                    ds = ds.replace('~|j', '~:j')
                fb = fb.replace('~|_', '~')
            fout.write('%s\t%s\n' % (ds, fb))
    shutil.move(tmp, m2mfile)

def check_length(m2mfile):
    with open(m2mfile, 'r') as fin:
        aligns = fin.readlines()
    count = 0
    for seqpair in aligns:
        count += 1
        ds, fb = seqpair.strip().split('\t')
        if len(ds.split('|')) != len(fb.split('|')):
            print('misalign: %d: %s\t%s' % (count, ds, fb))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: %s <news_file> <m2m_file> <model_file>' % sys.argv[0])
        print('  <news_file> input file in .news format gen by \'tg2news.py\'')
        print('  <m2m_file> output file in .m2m format gen by M2M aligner')
        print('  <model_file> dummy file gen by M2M aligner you\'ll never need')
        sys.exit(1)
    news_file = sys.argv[1]
    m2m_file = sys.argv[2]
    model_file = sys.argv[3]
    err_file = m2m_file + '.err'
    subprocess.call(config.M2M_CMD.format(news_file, m2m_file, model_file),
                    shell=True)
    os.remove(model_file)
    os.remove(err_file)
    fix_misaligns(m2m_file)
    check_length(m2m_file)
    print('[%s] finished successfully!' % TAG)
