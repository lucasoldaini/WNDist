from __future__ import print_function

import shutil
import time
import os

load_nltk = time.time()
from nltk.corpus import wordnet as wnnltk
load_nltk = time.time() - load_nltk
print('nltk : {:.2f} seconds'.format(load_nltk))

from wordnet_distance.wndist import WNDist

try:
    shutil.rmtree('cache')
except OSError:
    pass
os.mkdir('cache')

load_custom_cold = time.time()
wncstm = WNDist('cache', 'dict', printer=lambda m: print('\t{}'.format(m)))
load_custom_cold = time.time() - load_custom_cold
print('WNDist from cold: {:.2f} seconds'.format(load_custom_cold))

load_custom_hot = time.time()
wncstm = WNDist('cache', 'dict', printer=lambda m: print('\t{}'.format(m)))
load_custom_hot = time.time() - load_custom_hot
print('WNDist from hot: {:.2f} seconds'.format(load_custom_hot))

from itertools import product
w0, w1 = 'war', 'peace'

nltk_exec_time = time.time()
dists = []
for s1, s2 in product(wnnltk.synsets(w0), wnnltk.synsets(w1)):
    dists.append(s1.shortest_path_distance(s2))
nltk_exec_time = time.time() - nltk_exec_time
print('execution time for nltk : {:.4f}'.format(nltk_exec_time))


custom_exec_time = time.time()
wncstm.lemmasdist(w0, w1)
custom_exec_time = time.time() - custom_exec_time
print('execution time for WNDist : {:.4f}'.format(custom_exec_time))
