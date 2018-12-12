from collections import Counter
from nltk.corpus import wordnet as wn


class UtteranceAggregator(object):
    def __init__(self, utter_set):
        self.utterances = utter_set
        self.frame_counter = agg_frame_counts(self.utterances)
        self.frame_field_counter = agg_frame_field_counts(self.utterances)
        self.word_counter = agg_word_counts(self.utterances)
        self.lemma_counter = agg_lemma_counts(self.utterances)
        self.lemma_2_hypernym = agg_hypernyms(self.utterances)
        self.hypernym_2_lemma = agg_hypernym_lemmas(self.utterances,
                                                    self.lemma_2_hypernym)


# ------------------------------------------------------------------------------
# The helper functions in the module
# ------------------------------------------------------------------------------
def agg_frame_counts(utterance):
    counter = Counter()
    for utterance in utterance:
        if utterance.frames is None:
            continue
        for frame_name in utterance.frames.keys():
            counter[frame_name] += 1
    return counter


def agg_frame_field_counts(utterances):
    aggr = {}
    for utterance in utterances:
        if utterance.frames is None:
            continue
        for f_name in utterance.frames.keys():
            if f_name not in aggr:
                aggr[f_name] = {}
                aggr[f_name]['__text__'] = Counter()
            aggr[f_name]['__text__'][utterance.frames[f_name]['text']] += 1
            for attr, text in utterance.frames[f_name]['annotations']:
                if attr not in aggr[f_name]:
                    aggr[f_name][attr] = Counter()
                aggr[f_name][attr][text] += 1
    return aggr


def agg_word_counts(utterances):
    counter = Counter()
    for utterance in utterances:
        for token in utterance.spacy:
            if not (token.is_stop or token.is_punct):
                counter[token.text] += 1
    return counter


def agg_lemma_counts(utterances):
    counter = Counter()
    for utterance in utterances:
        for token in utterance.spacy:
            if not (token.is_stop or token.is_punct):
                counter[token.lemma_] += 1
    return counter


def get_first_n_nouns(lemma, n=1):
    synsets = []
    ss = wn.synsets(lemma)
    for synset in ss:
        if synset.pos() == 'n':
            synsets.append(synset)
        if len(synsets) == n:
            break
    return synsets


def get_hypernyms(synset):
    hypernym_lemmas = set()
    if synset is None:
        return hypernym_lemmas
    path = synset.hypernym_paths()
    if len(path) > 0:
        for p in path:
            for s in p:
                hypernym_lemmas.update(s.lemma_names())
        return hypernym_lemmas
    return hypernym_lemmas


def agg_hypernyms(utterances):
    lemma_to_path = {}
    for utterance in utterances:
        doc = utterance.spacy
        for token in doc:
            lemma = token.lemma_
            if lemma not in lemma_to_path:
                lemma_to_path[lemma] = set()
                for synset in get_first_n_nouns(lemma):
                    lemma_to_path[lemma].update(get_hypernyms(synset))
    return lemma_to_path


def agg_hypernym_lemmas(utterances, lemma_2_hyp):
    hyp_2_lemma = {}
    for k, v in lemma_2_hyp.items():
        for item in v:
            hyp_2_lemma[item] = hyp_2_lemma.get(item, [])
            hyp_2_lemma[item].append(k)
    for k in hyp_2_lemma.keys():
        hyp_2_lemma[k] = set(hyp_2_lemma[k])
    return hyp_2_lemma
