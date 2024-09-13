# **************************** Lowest Common Hyponym.py ****************************
import re
from nltk.corpus import wordnet as wn
import streamlit as st
import graphviz as g

def split_string(input_string, separators):
    # Create a regex pattern from the list of separators
    pattern = '|'.join(map(re.escape, separators))
    
    # Split the input string using the pattern
    words = re.split(pattern, input_string)
    
    # Remove empty strings from the result (if any)
    words = [word.strip() for word in words if word.strip()]
    
    return words

def is_wordnet_format(word):
    pattern = r'^[a-z]+(?:\.[a-z]+){2}\.\d+$'
    return re.match(pattern, word) is not None

def parse_input(inp: str):
    sep = [', ', ' ']
    words = split_string(inp, sep)
    return words

def get_synsets_by_pos(word):
    pos_categories = {
        'noun': wn.NOUN,
        'verb': wn.VERB,
        'adj': wn.ADJ,
        #'sat': wn.ADJ_SAT,
        'adv': wn.ADV
    }
    
    # Find all the synsets and store them in the coresponding key.
    synsets_by_pos = {pos: wn.synsets(word, pos_categories[pos]) for pos in pos_categories if wn.synsets(word, pos_categories[pos])}
    
    return synsets_by_pos

def find_most_similar_pair(ss_list1, ss_list2, dist_function):
    '''
    Find the most similar of ss1[] and ss2[] base of dist_function.
    ss1[] and ss2[] must have the same POS
    '''
    min_dist = 100
    min_pair = (None, None)
    for ssi in ss_list1:
        for ssj in ss_list2:
            dist = dist_function(ssi, ssj)
            print(f'{ssi} - {ssj}: {dist}')
            if dist is not None and dist < min_dist:
                min_dist = dist
                min_pair = (ssi, ssj)

    return min_pair

def lowest_common_hypernyms(words: list, dist_function):
    # for each word, find its synsets by pos: list of dicts
    ss_list_dict = [get_synsets_by_pos(w) for w in words]

    # Find the pos all the synsets have in common
    common_pos = set(ss_list_dict[0].keys())
    for dic in ss_list_dict[1:]:
        common_pos &= set(dic.keys())

    # For each pos, find the lowest_common_hypernyms.
    res = {}
    candidates = {}
    for pos in common_pos:

        # Find the nearest between 0 and 1
        ssi, ssj = find_most_similar_pair(ss_list_dict[0][pos], ss_list_dict[1][pos], dist_function)

        if str(ssi) == 'None' or str(ssj) == 'None':
            continue

        lowest_common_hyper = ssi.lowest_common_hypernyms(ssj)
        candidates[pos] = [ssi, ssj]

        # Find the nearets to the rest
        for dic in ss_list_dict[2:]:
            ssi, ssj = find_most_similar_pair(lowest_common_hyper, dic[pos], dist_function)

            lowest_common_hyper = lowest_common_hyper[0].lowest_common_hypernyms(ssj)
            candidates[pos].append(ssj)

        res[pos] = lowest_common_hyper

    return res, candidates


# Maintain a set of edges (remove duplicates)
class MyDigraph(g.Digraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._edges = set()
    
    def edge(self, tail_name, head_name, **attrs):
        super().edge(tail_name, head_name, **attrs)
        self._edges.add((tail_name, head_name))
    
    def edge_exists(self, tail_name, head_name):
        return (tail_name, head_name) in self._edges

def visualize_lch(lch, candidates):
    pos_paths = {}
    pos_graph = {}
    for pos in candidates.keys():
        lch_pos = lch[pos][0]
        pos_paths[pos] = [path[path.index(lch_pos):] for ss in candidates[pos] for path in ss.hypernym_paths() if lch_pos in path]

        pos_graph[pos] = MyDigraph()
        for path in pos_paths[pos]:
            # Add nodes for each synset
            for synset in path:
                pos_graph[pos].node(synset.name(), synset.name())

            # Add edges between each consecutive pair of synsets
            for i in range(len(path) - 1):
                if not pos_graph[pos].edge_exists(path[i].name(), path[i + 1].name()):
                    pos_graph[pos].edge(path[i].name(), path[i + 1].name())

    return pos_graph