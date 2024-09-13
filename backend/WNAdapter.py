import nltk
from nltk.corpus import wordnet as wn

class WNAdapter:
    #POS = ['n', 'v', 'a', 's', 'r'] # 'a' and 's' are duplicates
    POS = ['n', 'v', 'a', 'r']

    NOUN_RELATIONS = ['hypernyms', 'hyponyms', 'antonyms', 'attributes'
                    'member holonyms', 'part holonyms', 'substance holonyms', 
                    'member meronyms', 'part meronyms', 'substance meronyms']
    VERB_RELATIONS = ['hypernyms', 'troponyms', 'entailment', 'cause', 'also see', 'derivationally related forms']
    ADJ_RELATIONS  = ['antonyms', 'similar to', 'relational adj', 'also see', 'value of'] 
    ADV_RELATIONS  = ['derived from']

    CYCLIC_RELATIONS = ['derivationally related forms', 'antonyms', 'similar to', 'also see', 'relational adj']

    # Utility function for calling relations in Lemma class (base of Synset class)
    # Usage: synsets = _call_lemma_relation(synset('night.n.01'), lambda lemma: lemma.antonyms())
    def _call_lemma_relation(synset, lemma_relation):
        antonym_lemmas = [lemma_relation(lem) for lem in synset.lemmas()]
        antonym_synsets = [lemma.synset() for sublist in antonym_lemmas for lemma in sublist] # flatten & convert to Synset
        return antonym_synsets

    NOUN_RELATIONS_FUNC = [lambda s: s.hypernyms(), lambda s: s.hyponyms(), lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.antonyms()), lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.attributes()),
                            lambda s: s.member_holonyms(), lambda s: s.part_holonyms(), lambda s: s.substance_holonyms(),
                            lambda s: s.member_meronyms(), lambda s: s.part_holonyms(), lambda s: s.substance_holonyms()]

    VERB_RELATIONS_FUNC = [lambda s: s.hypernyms(), lambda s: s.hyponyms(), lambda s: s.entailments(),
                        lambda s: s.causes(), lambda s: s.also_sees(), lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.derivationally_related_forms())]

    ADJ_RELATIONS_FUNC = [lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.antonyms()), lambda s: s.similar_tos(), lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.derivationally_related_forms()),
                        lambda s: s.also_sees(), lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.attributes())]

    ADV_RELATIONS_FUNC = [lambda s: WNAdapter._call_lemma_relation(s, lambda ss: ss.pertainyms())]

    RELATION_NAME_FUNC = {'n': dict(zip(NOUN_RELATIONS, NOUN_RELATIONS_FUNC)),
                          'v': dict(zip(VERB_RELATIONS, VERB_RELATIONS_FUNC)),
                          'a': dict(zip(ADJ_RELATIONS, ADJ_RELATIONS_FUNC)),
                          'r': dict(zip(ADV_RELATIONS, ADV_RELATIONS_FUNC))}
    
    def look_up(word):
        return {pos: wn.synsets(word, pos=pos) for pos in WNAdapter.POS}
    
    def synset(synset_name):
        return wn.synset(synset_name)

    def get_relations(synset, pos):
        if pos not in WNAdapter.POS:
            return {}
        
        relations = {r_name: r_func(synset) for r_name, r_func in WNAdapter.RELATION_NAME_FUNC[pos].items() if r_func(synset) != []}
        return relations
    
    def get_relation_recursive(synset, relation):
        if not synset:
            return None
        
        if relation in WNAdapter.CYCLIC_RELATIONS:
            return None
        
        tree = {}
        for ss in relation(synset):
            tree[ss.name()] = WNAdapter.get_relation_recursive(ss, relation)

        return tree

    def synset_words(synset):
        lemmas = [lemma.replace('_', ' ') for lemma in synset.lemma_names()]
        return ", ".join(lemmas)

    def synset_info(synset):
        return f'{WNAdapter.synset_words(synset)} -- {synset.definition()} -- ({synset.name()}, id={synset.offset()})'