#!/usr/bin/python

# author:       Luca Soldaini
# email:        luca@soldaini.net
# description:  wordnet tools


# future statements
from __future__ import print_function


# default modules
import os
import re
import json
import time
import shelve
import bisect
import cPickle as pickle
from copy import deepcopy
from argparse import ArgumentParser
from itertools import chain, product


# installed modules
import networkx as nx


# project modules
from wordnet_distance import build_tools


class WNDist(object):
    def __init__(self, cachedir=None, sourcedir=None,
                 accepted_rels=None, printer=None):
        self.cachedir = cachedir
        self.sourcedir = sourcedir
        self.printer = print if printer is None else printer

        if self.cachedir is None and self.sourcedir is None:
            raise ValueError('can\'t build a WordNet Graph with no cached '
                             'graph or no source')

        h = hash(json.dumps(accepted_rels))

        wordnet_cache_path = os.path.join(
            self.cachedir, 'wordne.cache_{}.json'.format(h)
        )

        if not os.path.exists(wordnet_cache_path):
            self.printer('building WordNet from source...')
            start = time.time()

            self.wordnet = build_tools.make_wordnet(sourcedir)
            with file(wordnet_cache_path, 'wb') as f:
                json.dump(self.wordnet, f)

            self.printer(
                'finished building WordNet in {:.2f} seconds'
                ''.format(time.time() - start)
            )
        else:
            self.printer('loading WordNet from cache...')
            start = time.time()

            with file(wordnet_cache_path) as f:
                self.wordnet = json.load(f)

            self.printer(
                'finished loading WordNet in {:.2f} seconds'
                ''.format(time.time() - start)
            )

        graph_cache_path = os.path.join(
            self.cachedir, 'wordnet-graph.cache_{}.gpickle'.format(h)
        )

        if not os.path.exists(graph_cache_path):
            self.printer('building networkx graph from wordnet...')
            start = time.time()

            self.graph = (
                build_tools.instantiate_graph(self.wordnet, accepted_rels)
            )
            nx.write_gpickle(self.graph, graph_cache_path)

            self.printer(
                'finished building graph in {:.2f} seconds'
                ''.format(time.time() - start)
            )
        else:
            self.printer('loading networkx graph from cache...')
            start = time.time()

            self.graph = nx.read_gpickle(graph_cache_path)

            self.printer(
                'finished loading graph in {:.2f} seconds'
                ''.format(time.time() - start)
            )


        dist_cache_path = os.path.join(
            self.cachedir, 'wordnet-graph.cache_{}.shelf'.format(h)
        )
        self.memoization = shelve.open(dist_cache_path)

    @property
    def index(self):
        return self.wordnet['index']

    def syndist(self, s1, s2):
        ck = '{}_{}'.format(s1, s2)
        if ck in self.memoization:
            return self.memoization[ck]
        else:
            try:
                dist = nx.shortest_path_length(self.graph, s1, s2)
            except nx.exception.NetworkXNoPath:
                dist = float('inf')
            self.memoization[ck] = dist
        return dist

    def lemmasdist(self, l1, l2):

        pos1 = pos2 = None

        if type(l1) == type(l2) == tuple:
            pos1, pos2 = l1[1][0].lower(), l2[1][0].lower()
            l1, l2 = l1[0], l2[0]

            print (pos1, pos2)

            if pos1 != pos2:
                # the PoS of the two lemmas are different, return inf
                return [float('inf')]

        if l1 not in self.index or l2 not in self.index:
            return [float('inf')]

        distances = []

        for w1, w2 in product(self.index[l1],
                              self.index[l2]):
            if w1[0] != w2[0]:
                continue

            print(w1[0], w2[0], pos1, pos2)

            not_matching_pos = (
                ((pos1 is not None) and (pos2 is not None)) and
                (w1[0] != pos1 or w2[0] != pos2)
            )
            if not_matching_pos:
                continue

            dist = self.syndist(w1, w2)

            if dist < float('inf'):
                distances.insert(bisect.bisect(distances, dist), dist)

        return distances if len(distances) > 0 else [float('inf')]
