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

# set path to repo dir from https://gitlab.com/fb-nlp/nlp-genetator.git
FB_NLP_PATH = os.path.join(os.environ['HOME'], 'fb-gitlab/fb-nlp/nlp-generator')
sys.path.insert(0, FB_NLP_PATH)

SEP_CROSS  = ' '
DELIM_SENT = '@'
M2M_CMD    = (os.path.join(os.environ['HOME'],
                           'git-all/m2m-aligner/m2m-aligner') +
              ' --delX --inputFile {} --outputFile {} --alignerOut {}')

TG_EXCEPT = [
    '../../male/textgrid/M-028.TextGrid',
    '../../male/textgrid/M-055.TextGrid',
    '../../male/textgrid/M-059.TextGrid',
    '../../male/textgrid/M-070.TextGrid',
    '../../male/textgrid/M-088.TextGrid',
    '../../male/textgrid/M-096.TextGrid',
    '../../male/textgrid/M-113.TextGrid',
    '../../male/textgrid/M-128.TextGrid',
    '../../male/textgrid/M-148.TextGrid',
    '../../male/textgrid/M-154.TextGrid',
    '../../male/textgrid/M-164.TextGrid',
    '../../male/textgrid/M-178.TextGrid',
    '../../male/textgrid/M-181.TextGrid',
    '../../male/textgrid/M-195.TextGrid',
]

TG_HEAVY_CROSS = [
    '../../male/textgrid/M-026.TextGrid', # paira um              -> ['p', 'a', 'j', '4', 'u~:m']
    '../../male/textgrid/M-048.TextGrid', # hoje eu               -> ['o', 'Z', 'e', 'w']
    '../../male/textgrid/M-049.TextGrid', # sem ele               -> ['s', 'e~', 'j~:J', 'e', 'l', 'i'] (/J/ = nh)
    '../../male/textgrid/M-054.TextGrid', # marcado para as       -> ['m', 'a', 'h', 'k', 'a', 'd', 'u', 'p', 'a'], ['p', 'a', '4', '6', 'j', 'S']
    '../../male/textgrid/M-057.TextGrid', # era um                -> ['E', '4', 'u~:m']
    '../../male/textgrid/M-071.TextGrid', # esse empreendimento   -> ['e', 's', 'i~:m', 'p', '4', 'e~', 'e~:n', 'd:Z', 'i', 'm', 'e~:n', 't', 'u'
    '../../male/textgrid/M-076.TextGrid', # as aulas              -> ['6', 'z', 'a', 'w', 'l', '6', 'Z']
    '../../male/textgrid/M-080.TextGrid', # ainda é               -> ['a', 'i~:n', 'd', 'E']
    '../../male/textgrid/M-147.TextGrid', # * gambiarra didnt work "um(a a)rma"
    '../../male/textgrid/M-155.TextGrid', # uma empresa           -> ['u~', 'm', 'i~:m', 'p', '4', 'e', 'z', '6']
    '../../male/textgrid/M-160.TextGrid', # para ensaiar          -> ['p', 'a', '4', 'i~:n', 's', 'a', 'j', 'a', 'h']
    '../../male/textgrid/M-168.TextGrid', # hoje eu               -> ['o', 'Z', 'e', 'w']
    '../../male/textgrid/M-172.TextGrid', # planejo uma           -> ['p', 'l', 'a', 'n', 'e', 'Z', 'u~', 'm', '6']
    '../../male/textgrid/M-180.TextGrid', # fila aumentou         -> ['f', 'i', 'l', 'a', 'w', 'm', 'e~:n', 't', 'o', 'w']
    '../../male/textgrid/M-183.TextGrid', # mostra uma            -> ['m', 'O', 'S', 't', '4', 'u~', 'm', '6']
    '../../male/textgrid/M-189.TextGrid', # ele entende           -> ['e', 'l', 'i~:n', 't', 'e~:j~:n', 'd:Z', 'i']
    '../../male/textgrid/M-194.TextGrid', # joice esticou         -> ['Z', 'O', 'j', 's', 'i', 'S', 't:S', 'i', 'k', 'o', 'w']
]
