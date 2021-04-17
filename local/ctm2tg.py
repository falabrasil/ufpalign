#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
#
# fb_ctm2tg: a script to convert CTM files from Kaldi aligner to Praat's
# TextGrid format
#
# Grupo FalaBrasil (2019)
# Universidade Federal do Pará
#
# author: apr 2019
# cassio batista - cassio.batista.13@gmail.com

import sys

import os
os.environ['CLASSPATH'] = os.path.join(os.getenv('HOME'), 
			'fb-gitlab', 'fb-nlp', 'nlp-generator', # NOTE: call before jni
			'fb_nlplib.jar')

from jnius import autoclass

TG_NAMES = [
	'fonemeas', 'silabas-fonemas', 'palavras-grafemas',
	'frase-fonemas', 'frase-grafemas',
]

CTM_SIL_ID = '1' # TODO: keep an eye on sil id occurrences -- CB

class TimeMarkedConversation:
	def __init__(self):
		super(TimeMarkedConversation, self).__init__()

	# TODO: make it return an int > 0 for exiting, 0 for success
	def check_inputfile(self, filetype, filename):
		if filetype != 'graphemes' and filetype != 'phoneids':
			print('error: filetype %s is not acceptable' % filetype)
			sys.exit(2)
		if not os.path.isfile(filename):
			print('error: input file "%s" does not exist' % filename)
			sys.exit(2)
		elif not filename.endswith('%s.ctm' % filetype):
			print('error: input file "%s" does not have "%s.ctm" extension' % (filename, filetype))
			sys.exit(2)
		# https://stackoverflow.com/questions/2507808/how-to-check-whether-a-file-is-empty-or-not
		elif not os.stat(filename).st_size:
			print('error: input file "%s" appears to be empty' % filename)
			sys.exit(2)
	
class FalaBrasilNLP:
	def __init__(self):
		super(FalaBrasilNLP, self).__init__()
		self.jClass = autoclass('ufpa.util.PyUse')()

	def get_g2p(self, word):
		return self.jClass.useG2P(word)

	def get_syl(self, word):
		return self.jClass.useSyll(word)

	def get_stressindex(self, word):
		return self.jClass.useSVow(word)

	def get_g2psyl(self, word):
		return self.jClass.useSG2P(word)

	def print_asciilogo(self):
		print('\033[94m  ____                         \033[93m _____     _           \033[0m')
		print('\033[94m / ___| _ __ _   _ _ __   ___  \033[93m|  ___|_ _| | __ _     \033[0m')
		print('\033[94m| |  _ | \'__| | | | \'_ \ / _ \ \033[93m| |_ / _` | |/ _` |  \033[0m')
		print('\033[94m| |_| \| |  | |_| | |_) | (_) |\033[93m|  _| (_| | | (_| |    \033[0m')
		print('\033[94m \____||_|   \__,_| .__/ \___/ \033[93m|_|  \__,_|_|\__,_|    \033[0m')
		print('                  \033[94m|_|      \033[32m ____                _ _\033[91m  _   _ _____ ____    _            \033[0m')
		print('                           \033[32m| __ ) _ __ __ _ ___(_) |\033[91m| | | |  ___|  _ \  / \          \033[0m')
		print('                           \033[32m|  _ \| \'_ / _` / __| | |\033[91m| | | | |_  | |_) |/ ∆ \          \033[0m')
		print('                           \033[32m| |_) | | | (_| \__ \ | |\033[91m| |_| |  _| |  __// ___ \        \033[0m')
		print('                           \033[32m|____/|_|  \__,_|___/_|_|\033[91m \___/|_|   |_|  /_/   \_\       \033[0m')
		print('')

class TextGrid:
	def __init__(self):
		super(TextGrid, self).__init__()

	def check_outputdir(self, dirname):
		if os.path.isdir(dirname):
			if len(os.listdir(dirname)):
				ans = input('warning: dir "%s" is not empty. overwrite? [y/N] ' % dirname)
				if ans == 'y':
					import shutil
					shutil.rmtree(dirname)
					os.mkdir(dirname)
				else:
					print('aborted.')
					sys.exit(1)
		else:
			print('info: textgrid files will be stored under "%s" dir' % dirname)
			os.mkdir(dirname)

	def get_mainheader(self, xmax):
		return u'File type = "ooTextFile"'              + '\n' + \
			u'Object class = "TextGrid"'                + '\n' + \
			u'xmin = 0.00'                              + '\n' + \
			u'xmax = %.2f'                  % xmax      + '\n' + \
			u'tiers? <exists>'                          + '\n' + \
			u'size = 5'                                 + '\n' + \
			u'item []:'                                 + '\n'
	
	def get_itemheader(self, itm_id, name, xmax, intv_size):
		return u'\titem[%d]:'               % itm_id    + '\n' + \
			u'\t\tclass = "IntervalTier"'               + '\n' + \
			u'\t\tname  = "%s"'             % name      + '\n' + \
			u'\t\txmin  = 0.00'                         + '\n' + \
			u'\t\txmax  = %.2f'             % xmax      + '\n' + \
			u'\t\tintervals: size = %d'     % intv_size + '\n'
	
	def get_intervalcontent(self, intv_id, begin, end, token):
		return u'\t\tintervals[%d]'         % intv_id   + '\n' + \
			u'\t\t\txmin = %.2f'            % begin     + '\n' + \
			u'\t\t\txmax = %.2f'            % end       + '\n' + \
			u'\t\t\ttext = "%s"'            % token     + '\n' 
	
	def get_intervalsize(self, itm_id, tokenlist):
		if itm_id == 0:
			return len(tokenlist['phnid'])
		elif itm_id == 1:
			return len(tokenlist['sylph']) + tokenlist['phnid'].count(CTM_SIL_ID) 
		elif itm_id == 2:
			return len(tokenlist['graph']) - \
						tokenlist['graph'].count('sil') + \
						tokenlist['phnid'].count(CTM_SIL_ID)
		else:
			return 1

	def get_itemcontent(self, itm_id, tokenlist, start, finish):
		interval_size = self.get_intervalsize(itm_id, tokenlist)
		item_header = self.get_itemheader(itm_id+1,
					TG_NAMES[item], finish['graph'][-1], interval_size)
		item_content     = ''
		interval_content = ''
		i = 0
		if item == 0: # fonemas
			p = 0
			while i < interval_size:
				if tokenlist['phnid'][i] == CTM_SIL_ID:
					token = 'sil'
				else:
					token = tokenlist['phone'][p]
					p += 1
				interval_content += self.get_intervalcontent(i+1,
							start['phnid'][i], finish['phnid'][i], token)
				i += 1
		elif item == 1: # silabas fonemas TODO
			interval_content = ''
			b = 0
			e = 0
			while len(tokenlist['phnid']):
				phoneid = tokenlist['phnid'].pop(0)
				if phoneid == CTM_SIL_ID:
					token = 'sil'
				else:
					token = tokenlist['sylph'].pop(0)
					phone = tokenlist['phone'].pop(0)
					while phone != token:
						phone += tokenlist['phone'].pop(0)
						tokenlist['phnid'].pop(0) # FIXME
						e += 1
				interval_content += self.get_intervalcontent(i+1,
							start['phnid'][b], finish['phnid'][e], token)
				i += 1
				b =  e+1
				e += 1
		elif item == 2: # palavras grafemas
			while i < interval_size:
				token = tokenlist['graph'][i]
				interval_content += self.get_intervalcontent(i+1,
							start['graph'][i], finish['graph'][i], token)
				i += 1
		elif item == 3: # frase fonemas
			token = ' '.join(phonesyl for phonesyl in tokenlist['phrph'])
			interval_content = self.get_intervalcontent(i+1,
						start['phnid'][0], finish['phnid'][-1], token)
		elif item == 4: # frase grafemas
			token = ' '.join(word for word in tokenlist['phrgr'])
			interval_content = self.get_intervalcontent(i+1,
						start['graph'][0], finish['graph'][-1], token)
		else:
			print('wait a minute... there is something really wrong here.')
		return item_header + interval_content

def get_file_numlines(fp):
	for linenumber, content in enumerate(fp):
		pass
	fp.seek(0)
	return linenumber+1

if __name__=='__main__':
	fb  = FalaBrasilNLP()
	tg  = TextGrid()
	ctm = TimeMarkedConversation() # FIXME: dup var def
	if len(sys.argv) != 4:
		fb.print_asciilogo()
		print('usage: (python3) %s <file.graphemes.ctm> <file.phoneids.ctm> <out_dir>' % sys.argv[0])
		print('\t<file.graphemes.ctm>')
		print('\t<file.phoneids.ctm>')
		print('\t<out_dir>')
		sys.exit(1)

	# process grapheme input file
	ctm_graph_filename = sys.argv[1]
	ctm.check_inputfile('graphemes', ctm_graph_filename)

	# process phone ids input file
	ctm_phone_filename = sys.argv[2]
	ctm.check_inputfile('phoneids', ctm_phone_filename)

	# process textgrid output dir
	tg_output_dirname = sys.argv[3]
	tg.check_outputdir(tg_output_dirname)

	ctm = { # FIXME: dup var def
		'graph':open(ctm_graph_filename, 'r'),
		'phnid':open(ctm_phone_filename, 'r')
	}
	ctm_lines = {
		'graph':get_file_numlines(ctm['graph']),
		'phnid':get_file_numlines(ctm['phnid'])
	}
	fp_index = { 'graph': 0,  'phnid': 0  }
	start    = { 'graph': [], 'phnid': [], 'sylph': [] }
	finish   = { 'graph': [], 'phnid': [], 'sylph': [] }
	bt       = { 'graph': 0,  'phnid': 0  }
	dur      = { 'graph': 0,  'phnid': 0  }

	tokenlist = {
		'phnid':[], # 0 (1) phoneme ids as they appear in the CTM file
		'sylph':[], # 1 (2) phonemes separated by syllabification of graphemes
		'graph':[], # 2 (3) graphemes (words)
		'phrph':[], # 4 (5) phrase of phonemes separated by the space between graphemes
		'phrgr':[], # 3 (4) phrase of graphemes (words) 
		'phone':[], #       phonemes as they occur in the list of words
	}

	# treat .grapheme file
	filepath, chn, bt['graph'], dur['graph'], grapheme = ctm['graph'].readline().split()
	old_name = curr_name = filepath.split(sep='_', maxsplit=1).pop()
	start['graph'].append(float(bt['graph']))
	finish['graph'].append(float(bt['graph']) + float(dur['graph']))
	tokenlist['graph'].append(grapheme)
	fp_index['graph'] += 1
	while fp_index['phnid'] < ctm_lines['phnid']:
		while curr_name == old_name:
			if fp_index['graph'] >= ctm_lines['graph']:
				break
			filepath, chn, bt['graph'], dur['graph'], grapheme = ctm['graph'].readline().split()
			curr_name = filepath.split(sep='_', maxsplit=1).pop()
			start['graph'].append(float(bt['graph']))
			finish['graph'].append(float(bt['graph']) + float(dur['graph']))
			tokenlist['graph'].append(grapheme)
			fp_index['graph'] += 1

		# FIXME: dumb way to avoid the first word of the next sentence to be
		# appended to the end of the current one
		if fp_index['graph'] < ctm_lines['graph']:
			start['graph'].pop()
			finish['graph'].pop()
			tokenlist['graph'].pop()

		# treat .phoneids file
		filepath, chn, bt['phnid'], dur['phnid'], phoneme = ctm['phnid'].readline().split()
		curr_name = filepath.split(sep='_', maxsplit=1).pop()
		start['phnid'].append(float(bt['phnid']))
		finish['phnid'].append(float(bt['phnid']) + float(dur['phnid']))
		tokenlist['phnid'].append(phoneme)
		fp_index['phnid'] += 1
		while curr_name == old_name:
			if fp_index['phnid'] >= ctm_lines['phnid']:
				break
			filepath, chn, bt['phnid'], dur['phnid'], phoneme = ctm['phnid'].readline().split()
			curr_name = filepath.split(sep='_', maxsplit=1).pop()
			start['phnid'].append(float(bt['phnid']))
			finish['phnid'].append(float(bt['phnid']) + float(dur['phnid']))
			tokenlist['phnid'].append(phoneme)
			fp_index['phnid'] += 1

		# FIXME: dumb way to avoid the first phoneme of the next sentence to be
		# appended to the end of the current one
		if fp_index['phnid'] < ctm_lines['phnid']:
			start['phnid'].pop()
			finish['phnid'].pop()
			tokenlist['phnid'].pop()

		# prepare tg item's basic data structures
		tokenlist['phone'] = []
		for word in tokenlist['graph']:
			if word == '<UNK>':
				tokenlist['sylph'].append(word)
				tokenlist['phone'].append(word)
				tokenlist['phrph'].append(word)
				tokenlist['phrgr'].append(word)
				continue
			elif word == 'cinquenta':
				tokenlist['sylph'].append('si~')
				tokenlist['sylph'].append('kwe~')
				tokenlist['sylph'].append('ta')
			elif word == 'veloz':
				tokenlist['sylph'].append('ve')
				tokenlist['sylph'].append('lOjs')
			elif word == 'dez':
				tokenlist['sylph'].append('dEjs')
			else:
				for sylph in fb.get_g2psyl(word).split('-'):
					tokenlist['sylph'].append(sylph.replace('\'',''))
			phonemes = fb.get_g2p(word)
			for phone in phonemes.split():
				tokenlist['phone'].append(phone)
			tokenlist['phrph'].append(phonemes.replace(' ', ''))
			tokenlist['phrgr'].append(word)

		# write things to textgrid file
		with open('%s/%s.textgrid' % (tg_output_dirname, old_name), 'w') as f:
			sys.stdout.write('\r%s' % old_name)
			sys.stdout.flush()
			f.write(tg.get_mainheader(finish['graph'][-1]))
			for item in range(5):
				f.write(tg.get_itemcontent(item, tokenlist, start, finish))

		# flush vars
		start['graph']     = [float(bt['graph'])]
		finish['graph']    = [float(bt['graph']) + float(dur['graph'])]
		tokenlist['graph'] = [grapheme]
		old_name           = curr_name
		start['phnid']     = [float(bt['phnid'])]
		finish['phnid']    = [float(bt['phnid']) + float(dur['phnid'])]
		tokenlist['phnid'] = [phoneme]

		tokenlist['sylph'] = []
		tokenlist['phrph'] = []
		tokenlist['phrgr'] = []

	print('\tdone!')
	print('##', fp_index, '##', ctm_lines, '##')
	ctm['graph'].close()
	ctm['phnid'].close()
### EOF ###
