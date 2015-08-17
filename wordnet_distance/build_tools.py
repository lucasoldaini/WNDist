#!/usr/bin/python

# author:       Luca Soldaini
# email:        luca@soldaini.net
# description:  wordnet tools


# future statements
# no modules


# default modules
import os
import re
from itertools import chain


# installed modules
import networkx as nx


# project modules
from wordnet_distance.consts import SYMBOLS, TYPES


def read_index(path):
    with file(path) as f:
        rawlines = [
            ln.strip() for ln in f.readlines()
            if not ln.startswith(' ')
        ]

    index = {}

    for ln in rawlines:
        rawdata = ln.split()
        lemma, pos, cnt = rawdata[:3]

        for id_ in (rawdata[-i] for i in xrange(int(cnt), 0, -1)):
            index.setdefault(lemma, []).append('{}{}'.format(pos, id_))

    return index


def read_data(path, index, typ):

    split_senses = re.compile(r'\s[a-f0-9]{3}\s').split
    split_rels = re.compile(r'\s[a-f0-9]{4}(\s|$)').split
    sub_par_senses = re.compile(r'\([a-zA-Z0-9]\)$').sub

    with file(path) as f:
        rawlines = [
            ln.strip() for ln in f.readlines()
            if not ln.startswith(' ')
        ]

    data = {}

    for n, ln in enumerate(rawlines):
        rawline, gloss = map(str.strip, ln.split('|'))
        id_, _ignore, pos, sense, rawline = rawline.split(' ', 4)
        id_ = '{}{}'.format(typ, id_)

        extracted_rels = {}

        try:
            # because regex have no rsplit method
            rels, senses = (
                part[::-1] for part in split_senses(rawline[::-1], 1)
            )
            rels = [rel for rel in split_rels(rels) if rel.strip()]
        except ValueError:
            # no rels!
            rels = []
            senses = rawline[:-4]

        for i, rel in enumerate(rels):

            skiprel = False
            try:
                target_typ, target_id, target_pos = map(str.strip, rel.split())
            except ValueError:
                # this is not a relation
                skiprel = True

            if not skiprel:
                target_typ = SYMBOLS[target_typ[0]]
                target_id = '{}{}'.format(target_pos, target_id)
                extracted_rels.setdefault(target_typ, []).append(target_id)

        senses = senses.split()[::2]

        for sense in senses:
            sense = sub_par_senses('', sense)
            index.setdefault(sense, []).append(id_)

        data[id_] = {'rels': extracted_rels}

    return data


def make_wordnet(path):

    index_fns = [
        os.path.join(path, fn) for fn in os.listdir(path)
        if fn.startswith('index')
    ]

    index = {}

    for fn in index_fns:
        typ = os.path.split(fn)[1].split('.')[1]
        if typ not in TYPES:
            continue
        else:
            typ = TYPES[typ]
        typ_index = read_index(fn)
        for lemma, senses in typ_index.iteritems():
            index.setdefault(lemma, []).extend(senses)


    data_fns = [
        os.path.join(path, fn) for fn in os.listdir(path)
        if fn.startswith('data')
    ]

    data = {}

    for fn in data_fns:
        typ = os.path.split(fn)[1].split('.')[1]
        if typ not in TYPES:
            continue
        else:
            typ = TYPES[typ]
        typ_data = read_data(fn, index, typ)
        data.update(typ_data)

    wordnet = {'index': index, 'data': data}
    return wordnet


def instantiate_graph(wordnet, accepted_rels=None):
    def rels_it(rels):
        for grname, rel in rels.iteritems():
            for target in rel:
                yield (rel, target)

    graph = nx.DiGraph()
    graph.add_nodes_from(e for e in set(chain(*wordnet['index'].values())))

    for cid, data in wordnet['data'].iteritems():
        graph.add_edges_from(
            (cid, target) for rel, target in rels_it(data['rels'])
            if (accepted_rels is None) or (rel in accepted_rels)
        )

    return graph
