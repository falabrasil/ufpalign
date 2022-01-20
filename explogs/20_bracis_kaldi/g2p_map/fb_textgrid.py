#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Grupo FalaBrasil (2020)
# Universidade Federal do Pará
#
# author: apr 2020
# cassio batista - https://cassota.gitlab.io/
# last edited: jul 2020

import sys
import os
import re
import random

import config
from FalaBrasilNLP import FalaBrasilNLP


__author__ = 'Cassio Batista'
__email__ = 'cassio.batista.13@gmail.com'

class LLTextGrid:
    """ Low-level data structure for Praat's TextGrid file format """

    def __init__(self, filetype="ooTextFile", objectclass="TextGrid", 
                 xmin=None, xmax=None, tiers="<exists>", size=None,
                 filename=None):
        super(LLTextGrid, self).__init__()
        self._filetype = filetype
        self._objectclass = objectclass
        self._xmin = xmin
        self._xmax = xmax
        self._tiers = tiers
        self._size = size
        self._filename = filename
        self._items = []

    def get_filetype(self):
        return self._filetype

    def set_filetype(self, filetype):
        self._filetype = str(filetype)

    def get_objectclass(self):
        return self._objectclass

    def set_objectclass(self, objectclass):
        self._objectclass = str(objectclass)

    def get_tiers(self):
        return self._tiers

    def set_tiers(self, tiers):
        self._tiers = str(tiers)

    def get_xmin(self):
        return self._xmin

    def set_xmin(self, xmin):
        self._xmin = float(xmin)

    def get_xmax(self):
        return self._xmax

    def set_xmax(self, xmax):
        self._xmax = float(xmax)

    def get_size(self):
        return self._size

    def set_size(self, size):
        self._size = int(size)

    def get_items(self):
        return self._items

    # TODO no set_item()?

    def add_item(self, item):
        self._items.append(item)

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        self._filename = str(filename)

    def get_item_by_id(self, index):
        for item in self.get_items():
            if item.get_index() == index:
                return item
        return None  # TODO raise exception?

    def get_item_by_name(self, name):
        for item in self.get_items():
            if item.get_name() == name:
                return item
        return None  # TODO raise exception?

    def __str__(self):
        textgrid = 'File type = "%s"\n' % self.get_filetype() + \
                   'Object class = "%s"\n' % self.get_objectclass() + \
                   'xmin = %.18f\n' % self.get_xmin() + \
                   'xmax = %.18f\n' % self.get_xmax() + \
                   'tiers? %s\n' % self.get_tiers() + \
                   'size = %d\n' % self.get_size() + \
                   'item []:\n'
        for itm in self.get_items():
            for line in str(itm).splitlines():
                textgrid += '\t' + line + '\n'
        return textgrid.rstrip().expandtabs(4)


class LLItem:
    """ Low-level TextGrid item, possibly a collections of intervals """

    def __init__(self, index=None, _class="IntervalTier", name=None,
            xmin=None, xmax=None, size=None):
        super(LLItem, self).__init__()
        self._index = index
        self._class = _class
        self._name = name
        self._xmin = xmin
        self._xmax = xmax
        self._size = size
        self._intervals = []

    def get_index(self):
        return self._index

    def set_index(self, index):
        self._index = int(index)

    def get_class(self):
        return self._class

    def set_class(self, _class):
        self._class = str(_class)

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = str(name)

    def get_xmin(self):
        return self._xmin

    def set_xmin(self, xmin):
        self._xmin = float(xmin)

    def get_xmax(self):
        return self._xmax

    def set_xmax(self, xmax):
        self._xmax = float(xmax)

    def get_size(self):
        return self._size

    def set_size(self, size):
        self._size = int(size)

    def get_intervals(self):
        return self._intervals

    # TODO no set_interval()?

    def add_interval(self, interval):
        if isinstance(interval, Interval):
            self._intervals.append(interval)
    
    def get_interval_by_id(self, index):
        for interval in self.get_intervals():
            if interval.get_index() == index:
                return interval
        return None

    def __str__(self):
        item = 'item [%d]:\n' % self.get_index() + \
               '\tclass = "%s"\n' % self.get_class() + \
               '\tname  = "%s"\n' % self.get_name() + \
               '\txmin  = %.18f\n' % self.get_xmin() + \
               '\txmax  = %.18f\n' % self.get_xmax() + \
               '\tintervals: size = %d\n' % self.get_size()
        for itv in self.get_intervals():
            for line in str(itv).splitlines():
                item += '\t' + line + '\n'
        return item


# class Token
class Item(LLItem):
    """ High-level interface for dealing with Item objects """

    def __init__(self, index=None, name=None, xmin=None, xmax=None, size=None):
        super(Item, self).__init__(index=index, name=name,
                                   xmin=xmin, xmax=xmax, size=size)
        self._tokenlists = []  # [['o'], ['g','a','l','u'], ['a','z','u','w']]
        self._timestamps = []

    def get_tokenlists(self):
        return self._tokenlists

    def set_tokenlists(self, tokenlists):
        # TODO check if nested list
        self._tokenlists = tokenlists

    def add_tokenlist(self, tokenlist):
        self._tokenlists.append(tokenlist)

    def get_timestamps(self, precision=None):
        if isinstance(precision, int):
            return [float('%.{}f'.format(precision) % t) for t in self._timestamps]
        return self._timestamps

    def get_timestamp_at(self, position):
        return self._timestamps[position]

    def set_timestamps(self, timestamps):
        # TODO check if list
        self._timestamps = timestamps

    def add_timestamp(self, timestamp):
        self._timestamps.append(timestamp)

    def __str__(self):
        return super().__str__()


class Interval:
    """ TextGrid interval """

    def __init__(self, index=None, xmin=None, xmax=None, text=None):
        super(Interval, self).__init__()
        self._index = index
        self._xmin = xmin
        self._xmax = xmax
        self._text = text

    def get_index(self):
        return self._index

    def set_index(self, index):
        self._index = int(index)

    def get_xmin(self):
        return self._xmin

    def set_xmin(self, xmin):
        self._xmin = float(xmin)

    def get_xmax(self):
        return self._xmax

    def set_xmax(self, xmax):
        self._xmax = float(xmax)

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = str(text)

    def __str__(self):
        return 'intervals [%d]:\n' % self.get_index() + \
               '\txmin = %.18f\n' % self.get_xmin() + \
               '\txmax = %.18f\n' % self.get_xmax() + \
               '\ttext = "%s"\n' % self.get_text()



class TextGrid(LLTextGrid):
    """ High-level interface for LLTextGrid for easy management

        phonemes:    [], 1  [['a'], ['g','a','l','i~','J,'a'], ['a','z','u','w']]
        syllphones:  [], 2  [['a'], ['ga','li~','Ja'],         ['a','zuw']]
        wordgraphs:  [], 3  [['a'], ['galinha'],               ['azul']]
        wordphones:  [], 4a [['a'], ['gali~Ja'],               ['azuw']]
        phrasephone: '', 4b 'a gali~Ja azuw'
        phrasegraph: '', 5  'a galinha azul'

    """

    PHONEMES_ID = 1
    SYLLPHONES_ID = 2
    WORDGRAPHS_ID = 3
    PHRASEPHONE_ID = 4  # NOTE: CB: 4b
    PHRASEGRAPH_ID = 5
    nlp = FalaBrasilNLP()

    def __init__(self, xmin=None, xmax=None, size=None,
                 filename=None, init_default_items=False):
        super(TextGrid, self).__init__(xmin=xmin, xmax=xmax, size=size,
                                       filename=filename)
        if init_default_items:
            names = ['phones', 'syllphones', 'wordgraphs',
                     'phrasephones', 'phrasegraphs']
            for i, name in enumerate(names):
                item = Item(index=i + 1, name=name)
                self.add_item(item)

    # _---------------------------------
    def get_phonemes(self, nested=True):                                 # 1
        item = self.get_item_by_id(self.PHONEMES_ID)
        if nested:
            return item.get_tokenlists()
        return [itv.get_text() for itv in item.get_intervals()]

    def add_phonemes(self, phonemes):
        self.get_item_by_id(self.PHONEMES_ID).add_tokenlist(phonemes)

    def set_phonemes(self, phonemes):
        self.get_item_by_id(self.PHONEMES_ID).set_tokenlists(phonemes)

    def get_phoneme_timestamps(self, precision=None):
        return self.get_item_by_id(self.PHONEMES_ID).get_timestamps(precision)

    def get_phoneme_timestamp_at(self, position):
        return self.get_item_by_id(self.PHONEMES_ID).get_timestamp_at(position)

    def add_phoneme_timestamp(self, timestamp):
        self.get_item_by_id(self.PHONEMES_ID).add_timestamp(timestamp)

    def set_phoneme_timestamps(self, timestamps):
        self.get_item_by_id(self.PHONEMES_ID).set_timestamps(timestamps)

    # ------------------------------------
    def get_syllphones(self, nested=True):                               # 2
        item = self.get_item_by_id(self.SYLLPHONES_ID)
        if nested:
            return item.get_tokenlists()
        return [itv.get_text() for itv in item.get_intervals()]

    def add_syllphones(self, syllphones):
        self.get_item_by_id(self.SYLLPHONES_ID).add_tokenlist(syllphones)

    def set_syllphones(self, syllphones):
        self.get_item_by_id(self.SYLLPHONES_ID).set_tokenlists(syllphones)

    def get_syllphone_timestamps(self, precision=None):
        return self.get_item_by_id(self.SYLLPHONES_ID).get_timestamps(precision)

    def get_syllphone_timestamp_at(self, position):
        return self.get_item_by_id(sef.SYLLPHONES_ID).get_timestamp_at(position)

    def add_syllphone_timestamp(self, timestamp):
        self.get_item_by_id(self.SYLLPHONES_ID).add_timestamp(timestamp)

    def set_syllphone_timestamps(self, timestamps):
        self.get_item_by_id(self.SYLLPHONES_ID).set_timestamps(timestamps)

    # ------------------------------------
    def get_wordgraphs(self, nested=True):                               # 3
        item = self.get_item_by_id(self.WORDGRAPHS_ID)
        if nested:
            return item.get_tokenlists()
        return self.get_phrasegraph()

    def add_wordgraphs(self, wordgraphs):
        self.get_item_by_id(self.WORDGRAPHS_ID).add_tokenlist(wordgraphs)

    def set_wordgraphs(self, wordgraphs):
        self.get_item_by_id(self.WORDGRAPHS_ID).set_tokenlists(wordgraphs)

    def get_wordgraph_timestamps(self, precision=None):
        return self.get_item_by_id(self.WORDGRAPHS_ID).get_timestamps(precision)

    def get_wordgraph_timestamp_at(self, position):
        return self.get_item_by_id(self.WORDGRAPHS_ID).get_timestamp_at(position)

    def add_wordgraph_timestamp(self, timestamp):
        self.get_item_by_id(self.WORDGRAPHS_ID).add_timestamp(timestamp)

    def set_wordgraph_timestamps(self, timestamps):
        self.get_item_by_id(self.WORDGRAPHS_ID).set_timestamps(timestamps)

    # -----------------------------------
    def get_wordphones(self, nested=True):                               # 4a
        item = self.get_item_by_id(self.PHRASEPHONE_ID)
        if nested:
            return item.get_tokenlists()
        return self.get_phrasephone()

    def add_wordphones(self, wordphones):
        self.get_item_by_id(self.PHRASEPHONE_ID).add_tokenlist(wordphones)

    def set_wordphones(self, wordphones):
        self.get_item_by_id(self.PHRASEPHONE_ID).set_tokenlists(wordphones)

    def get_wordphone_timestamps(self, precision=None):
        return self.get_item_by_id(self.PHRASEPHONE_ID).get_timestamps(precision)

    def get_wordphone_timestamp_at(self, position):
        return self.get_item_by_id(sef.PHRASEPHONE_ID).get_timestamp_at(position)

    def add_wordphones_timestamp(self, timestamp):
        self.get_item_by_id(self.PHRASEPHONE_ID).add_timestamp(timestamp)

    def set_wordphone_timestamps(self, timestamps):
        self.get_item_by_id(self.PHRASEPHONE_ID).set_timestamps(timestamps)

    # ------------------------------------
    def get_phrasephone(self, nested=True):                             # 4b
        item = self.get_item_by_id(self.PHRASEPHONE_ID)
        if nested:
            return item.get_tokenlists()
        return [itv.get_text() for itv in item.get_intervals()]

    def set_phrasephone(self, text):
        self.get_item_by_id(self.PHRASEPHONE_ID).set_tokenlists([text])

    def get_phrasephone_timestamps(self, precision=None):
        return self.get_item_by_id(self.PHRASEPHONE_ID).get_timestamps(precision)

    def set_phrasephone_timestamps(self, timestamps):
        self.get_item_by_id(self.PHRASEPHONE_ID).set_timestamps(timestamps)

    # ------------------------------------
    def get_phrasegraph(self, nested=True):                              # 5
        item = self.get_item_by_id(self.PHRASEGRAPH_ID)
        if nested:
            return item.get_tokenlists()
        return [itv.get_text() for itv in item.get_intervals()]

    def set_phrasegraph(self, text):
        self.get_item_by_id(self.PHRASEGRAPH_ID).set_tokenlists([text])

    def get_phrasegraph_timestamps(self, precision=None):
        return self.get_item_by_id(self.PHRASEGRAPH_ID).get_timestamps(precision)

    def set_phrasegraph_timestamps(self, timestamps):
        self.get_item_by_id(self.PHRASEGRAPH_ID).set_timestamps(timestamps)

    # ------------------------------------
    def inspect(self):
        print('size', self.get_size())
        print('xmin', self.get_xmin())
        print('xmax', self.get_xmax())
        for item in self.get_items():
            print('item index', item.get_index())
            print('item name', item.get_name())
            print('item xmin', item.get_xmin())
            print('item xmax', item.get_xmax())
            print('item size', item.get_size())
        print(self.get_phrasephone())

    def lower(self):
        """ Parses Item tokenlists to LLItem Tiers

            Converts a list of tokenlists and timestamps to Interval
        """

        for item in self.get_items():
            timestamp_list = []
            for tokenlist in item.get_tokenlists():
                for token in tokenlist:
                    interval = Interval()
                    interval.set_text(token)
                    item.add_interval(interval)
            for index, interval in enumerate(item.get_intervals()):
                interval.set_index(index + 1)
                interval.set_xmin(item.get_timestamp_at(index))
                interval.set_xmax(item.get_timestamp_at(index + 1))
            size = len(item.get_intervals())
            item.set_size(size)
            item.set_xmin(item.get_interval_by_id(1).get_xmin())
            item.set_xmax(item.get_interval_by_id(size).get_xmax())
        size = len(self.get_items())
        self.set_size(size)
        self.set_xmin(self.get_item_by_id(1).get_xmin())
        self.set_xmax(self.get_item_by_id(1).get_xmax())

        return self

    def upper(self):
        """ Parses LLItem Tiers to Item Tokenlists

            Converts a list of intervals to tokenlists and timestamps

            tokens: ['6', '_', 'k', 'e', 's', '_', 't', 'a~', 'w~', ...
                     'f', 'o', 'j', 'h/', 'e', '_', 't', 'o~', 'm', ...
                     'a', 'd', '6', 'n', 'u', '_', 'k', 'o~', 'n',  ...]
        """

        # wordphones: ['6', 'kesta~w~', 'foj', 'h/eto~mad6', 'nu', ...]
        wordphones = self.get_item_by_id(self.PHRASEPHONE_ID) \
                         .get_interval_by_id(1).get_text().split()
        for index in (self.PHONEMES_ID, self.SYLLPHONES_ID):
            item = self.get_item_by_id(index)
            tokens = [itv.get_text() for itv in item.get_intervals()]
            timestamps = [0.0] + [itv.get_xmax() for itv in item.get_intervals()]
            for w in wordphones:
                tokenlist = []
                i = 0
                while i < len(w):
                    p = tokens.pop(0)
                    if p == '_':
                        if i == 0:
                            item.add_tokenlist(list(p))  # sil in between ws
                        else:
                            tokenlist.append(p)  # sil in the middle of w
                        continue
                    else:
                        for j in range(1, 10):  # 10 is just a safe margin
                            if p == w[i:i + j]:
                                tokenlist.append(p)
                                i += j
                                break
                item.add_tokenlist(tokenlist)
            item.set_timestamps(timestamps)

        # wordgraphs: ['a', 'questão', 'foi', 'retomada', 'no', ...]
        wordgraphs = self.get_item_by_id(self.PHRASEGRAPH_ID) \
                         .get_interval_by_id(1).get_text().split()
        item = self.get_item_by_id(self.WORDGRAPHS_ID)
        tokenlists = [t.split() for t in wordgraphs]
        timestamps = [0.0] + [itv.get_xmax() for itv in item.get_intervals()]
        item.set_tokenlists(tokenlists)
        item.set_timestamps(timestamps)

        for index in (self.PHRASEPHONE_ID, self.PHRASEGRAPH_ID):
            item = self.get_item_by_id(index)
            tokenlists = [item.get_interval_by_id(1).get_text().split()]
            timestamps = [0.0] + [itv.get_xmax() for itv in item.get_intervals()]
            item.set_tokenlists(tokenlists)
            item.set_timestamps(timestamps)

        return self


    def __str__(self):
        return super().__str__()


class TextGridIO:
    """ Handles TextGrid objects """

    def __init__(self, filename=None, shuffle=False):
        """ Constructor """

        if filename is not None:
            self._tg_filelist = self.load_tglist_from_file(filename, shuffle)
            if not self._tg_filelist:
                sys.stderr.write('problem reading file.\n')
                sys.exit(1)


    def load_tglist_from_file(self, filename, shuffle):
        """ Reads a file list and returns a Python list of file paths """

        if not os.path.isfile(filename):
            sys.stderr.write('[%s] error: `%s` is not a valid file.\n' %
                             (TAG, filename))
            return False
        with open(filename, 'r') as f:
            tg_filelist = f.read().split()
        for tgf in tg_filelist:
            if not os.path.isfile(tgf):
                sys.stderr.write('[%s] error: tg file `%s` does not exist.\n' %
                                 (TAG, tgf))
                return False
        if shuffle:
            random.shuffle(tg_filelist)
        else:
            tg_filelist.sort()
        return tg_filelist


    def get_tg_filelist(self):
        """ Returns a list of textgrid file paths. """

        return self._tg_filelist

#    def print_info(self, tg_ds, tg_fb, dtype='crossref'):
#        if dtype == 'crossref':
#            print(       '\033[41m[DS] phonemes   ', tg_ds.get_phonemes(),          '\033[0m')
#            print('\033[92m\033[7m[FB] phonemes   ', tg_fb.get_phonemes(),          '\033[0m')
#            print(       '\033[41m[DS] syllphones ', tg_ds.get_syllphones(),        '\033[0m')
#            print('\033[92m\033[7m[FB] syllphones ', tg_fb.get_syllphones(),        '\033[0m')
#            print(       '\033[44m[DS] wordgraphs ', tg_ds.get_wordgraphs(),        '\033[0m')
#            print('\033[36m\033[7m[FB] wordgraphs ', tg_fb.get_wordgraphs(),        '\033[0m')
#            print(       '\033[41m[DS] wordphones ', tg_ds.get_wordphones(),        '\033[0m')
#            print('\033[92m\033[7m[FB] wordphones ', tg_fb.get_wordphones(),        '\033[0m')
#            print(       '\033[41m[DS] phrasephone', tg_ds.get_phrasephone(),       '\033[0m')
#            print('\033[92m\033[7m[FB] phrasephone', tg_fb.get_phrasephone(),       '\033[0m')
#            print(       '\033[41m[DS] phrasegraph', tg_ds.get_phrasegraph(),       '\033[0m')
#            print('\033[92m\033[7m[FB] phrasegraph', tg_fb.get_phrasegraph(),       '\033[0m')
#            print()
#            print(       '\033[41m[DS] time graph', tg_ds.get_wordgraph_timestamp(),'\033[0m')
#            print(       '\033[41m[DS] time phons', tg_ds.get_phoneme_timestamp(),  '\033[0m')
#            print(       '\033[41m[DS] time sylls', tg_ds.get_syllphone_timestamp(),'\033[0m')
#            print(       '\033[41m[DS] time wphon', tg_ds.get_wordphone_timestamp(),'\033[0m')
#            print()
#            print('\033[92m\033[7m[FB] time graph', tg_fb.get_wordgraph_timestamp(),'\033[0m')
#            print('\033[92m\033[7m[FB] time phons', tg_fb.get_phoneme_timestamp(),  '\033[0m')
#            print('\033[92m\033[7m[FB] time sylls', tg_fb.get_syllphone_timestamp(),'\033[0m')
#            print('\033[92m\033[7m[FB] time wphon', tg_fb.get_wordphone_timestamp(),'\033[0m')
#            return
#        if dtype == 'all' or dtype == 'dataset':
#            print(       '\033[41m[DS] phonemes   ', tg_ds.get_phonemes(),          '\033[0m')
#            print(       '\033[41m[DS] syllphones ', tg_ds.get_syllphones(),        '\033[0m')
#            print(       '\033[44m[DS] wordgraphs ', tg_ds.get_wordgraphs(),        '\033[0m')
#            print(       '\033[41m[DS] wordphones ', tg_ds.get_wordphones(),        '\033[0m')
#            print(       '\033[41m[DS] phrasephone', tg_ds.get_phrasephone(),       '\033[0m')
#            print(       '\033[41m[DS] phrasegraph', tg_ds.get_phrasegraph(),       '\033[0m')
#            print()
#            print(       '\033[41m[DS] time graph', tg_ds.get_wordgraph_timestamp(),'\033[0m')
#            print(       '\033[41m[DS] time phons', tg_ds.get_phoneme_timestamp(),  '\033[0m')
#            print(       '\033[41m[DS] time sylls', tg_ds.get_syllphone_timestamp(),'\033[0m')
#            print(       '\033[41m[DS] time wphon', tg_ds.get_wordphone_timestamp(),'\033[0m')
#            if dtype == 'dataset':
#                return
#            print()
#        if dtype == 'all' or dtype == 'falabrasil':
#            print('\033[92m\033[7m[FB] phonemes   ', tg_fb.get_phonemes(),          '\033[0m')
#            print('\033[92m\033[7m[FB] syllphones ', tg_fb.get_syllphones(),        '\033[0m')
#            print('\033[36m\033[7m[FB] wordgraphs ', tg_fb.get_wordgraphs(),        '\033[0m')
#            print('\033[92m\033[7m[FB] wordphones ', tg_fb.get_wordphones(),        '\033[0m')
#            print('\033[92m\033[7m[FB] phrasephone', tg_fb.get_phrasephone(),       '\033[0m')
#            print('\033[92m\033[7m[FB] phrasegraph', tg_fb.get_phrasegraph(),       '\033[0m')
#            print()
#            print('\033[92m\033[7m[FB] time graph', tg_fb.get_wordgraph_timestamp(),'\033[0m')
#            print('\033[92m\033[7m[FB] time phons', tg_fb.get_phoneme_timestamp(),  '\033[0m')
#            print('\033[92m\033[7m[FB] time sylls', tg_fb.get_syllphone_timestamp(),'\033[0m')
#            print('\033[92m\033[7m[FB] time wphon', tg_fb.get_wordphone_timestamp(),'\033[0m')


    def parse_interval(self, index, contents):
        """ Parses attributes from file into an Interval object """

        interval = Interval(index=int(index))
        while len(contents):
            line = contents.pop(0)
            tokens = re.split('[=?:]', line)
            if len(tokens) == 2:
                key, val = re.sub(r'\s+', '', tokens[0].lower()), tokens[1].strip()
                match_item = re.search('^item\[(.*?)\]', key)
                match_interval = re.search('^intervals\[(.*?)\]', key)
                if match_interval is not None:
                    contents.insert(0, line)
                    break
                elif match_item is not None:
                    contents.insert(0, line)
                    break
                else:
                    setter = getattr(interval, 'set_%s' % key)
                    setter(val.replace('"', ''))
            else:
                #sys.stderr.write('a blank line of length %d?\n' % len(tokens))
                continue
        return interval


    def parse_item(self, index, contents):
        """ Parses attributes from file into an Item object """

        item = Item(index=int(index))
        while len(contents):
            line = contents.pop(0)
            tokens = re.split('[=?:]', line)
            if len(tokens) == 2:
                key, val = re.sub(r'\s+', '', tokens[0].lower()), tokens[1].strip()
            elif len(tokens) == 3:
                key, val = re.sub(r'\s+', '', tokens[1].lower()), tokens[2].strip()
            else:
                #sys.stderr.write('a blank line of length %d?\n' % len(tokens))
                continue
            match_interval = re.search('^intervals\[(.*?)\]', key)
            match_item = re.search('^item\[(.*?)\]', key)
            if match_interval is not None:
                index = match_interval.group(1)
                if index.isdigit():
                    interval = self.parse_interval(index, contents)
                    item.add_interval(interval)
            elif match_item is not None:
                contents.insert(0, line)
                break
            else:
                setter = getattr(item, 'set_%s' % key)
                setter(val.replace('"', ''))
        return item


    def parse_textgrid(self, contents):
        """ Parse attributes from file into a TextGrid object """

        tg = TextGrid()
        while len(contents):
            line = contents.pop(0)
            tokens = re.split('[=:?]+', line)
            if len(tokens) == 2:
                key, val = re.sub(r'\s+', '', tokens[0].lower()), tokens[1].strip()
                match_item = re.search('^item\[(.*?)\]', key)
                if match_item is not None:
                    index = match_item.group(1)
                    if index.isdigit():
                        item = self.parse_item(index, contents)
                        tg.add_item(item)
                else:
                    setter = getattr(tg, 'set_%s' % key)
                    setter(val.replace('"', ''))
            else:
                #sys.stderr.write('a blank line of length %d?\n' % len(tokens))
                continue
        return tg.upper()

    def parse_tg_from_file(self, filename):
        """ Parses a textgrid file into a LLTextGrid object """

        with open(filename, 'r') as f:
            contents = f.readlines()
        return self.parse_textgrid(contents)


    def write_tg_to_file(self, tg, filename):
        """ Writes a LLTextGrid object to a file """

        with open(filename, 'w') as f:
            f.write(str(tg))


if __name__ == '__main__':
    io = TextGridIO('res/filelist_male.txt', shuffle=True)
    for f in io.get_tg_filelist():
        tg = io.parse_tg_from_file(f)
        tg.set_filename(f)
        #print(tg)
        print('phonemes')
        print(tg.get_phonemes(nested=False))
        print(tg.get_phonemes(nested=True))
        print(tg.get_phoneme_timestamps())
        print(tg.get_phoneme_timestamps(precision=2))
        print('##########')
        print('syllphones')
        print(tg.get_syllphones(nested=False))
        print(tg.get_syllphones(nested=True))
        print(tg.get_syllphone_timestamps())
        print(tg.get_syllphone_timestamps(precision=2))
        print('##########')
        print('wordgraphs')
        print(tg.get_wordgraphs(nested=False))
        print(tg.get_wordgraphs(nested=True))
        print(tg.get_wordgraph_timestamps())
        print(tg.get_wordgraph_timestamps(precision=2))
        print('##########')
        print('wordphones')
        print(tg.get_wordphones(nested=False))
        print(tg.get_wordphones(nested=True))
        print(tg.get_wordphone_timestamps())
        print(tg.get_wordphone_timestamps(precision=2))
        print('##########')
        print(tg.get_phrasephone())
        print(tg.get_phrasephone_timestamps())
        print(tg.get_phrasephone_timestamps(precision=2))
        print('##########')
        print(tg.get_phrasegraph())
        print(tg.get_phrasegraph_timestamps())
        print(tg.get_phrasegraph_timestamps(precision=3))
        break
