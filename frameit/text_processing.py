import spacy
import os
from spacy.tokens import Doc, Span, Token
import spacy.util as util
from spacy.cli.info import info
from spacy.cli.download import download
import frameit.time_extraction as tp

class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class TextProcessing(metaclass=Singleton):

    def __init__(self, attr_dir=None):
        self.lang_dict = {
            'en': 'en_core_web_lg',
            'fr': 'fr_core_news_sm',
            'ja': 'ja_sudachipy_wikipedia'
        }
        self.nlp_dict = {}
        self.add_language('en')
        self.nlp = self.nlp_dict
        self.lemmatizer = spacy.lemmatizer.Lemmatizer()

    def add_language(self, lang):
        print('Loading the %s model' % lang)
        lang_model = self.lang_dict.get(lang, lang)
        if lang == "ja":
            import ja_sudachipy
            self.nlp_dict[lang] = ja_sudachipy.Japanese().load(lang_model)
            return
        if info():
             if lang_model not in info()['Models']:
                  download(lang_model)
        self.nlp_dict[lang] = spacy.load(lang_model)

    def lemmatize(self, utterance, pos):
        return self.lemmatizer(utterance, pos)

    def get_attributes(self, pos_set, func, parent_constraints, candidate_constraints):
        '''
        Keyword arguments:
            func -- the method to which we extract candidates. Can be: parent|child
            pos_set -- the positive set for the frame
            parent_constraints -- constraints for the parent of the candidate, all lowercase
            candidate_constraints -- constraints for the desired candidate, all lowercase

            example parent_constraints = [{"pos":["noun"], "dep":["pobj"], "lemma":["ate", "ran"]}, 
                                      {"pos":["num"], "dep":["adp"], "lemma":["hug"]}]
            candidate_constraints = same as above

        Return:
            all_candidates: a list of tuples [0] == candidates, [1] == candidate noun chunk, [2] == original utterance 
        '''
        all_candidates = set()
        if func.lower() == 'parent':
            for utterance in pos_set:
                candidates = self.extract_candidates_by_parent(utterance.spacy,
                                                     parent_constraints,
                                                     candidate_constraints)
                all_candidates.update(candidates)
        if func.lower() == 'child':
            for utterance in pos_set:
                candidates = self.extract_candidates_by_child(utterance.spacy,
                                                     parent_constraints,
                                                     candidate_constraints)
                all_candidates.update(candidates)
        '''
        if func.lower() == 'time':
            for utterance in pos_set:
                candidates = self.extract_time_candidates(utterance.spacy,
                                                     parent_constraints,
                                                     candidate_constraints)
                all_candidates.update(candidates)
        '''    

        return all_candidates

    def extract_candidates_by_parent(self, utterance, parent_constraints,
                           candidate_constraints):
        candidates = []
        for token in utterance:
            for obj in parent_constraints:
                if self.check_constraints(token, obj):
                    for child in token.children:
                        for cand in candidate_constraints:
                            if self.check_constraints(child, cand):
                                found_chunk = None
                                for chunk in utterance.noun_chunks:
                                    if child in chunk:
                                        found_chunk = chunk
                                        break
                                candidates.append((child, found_chunk, utterance))
        return candidates

    def extract_candidates_by_child(self, utterance, child_constraints,
                           candidate_constraints):
        candidates = []
        for token in utterance:
            for obj in candidate_constraints:
                if self.check_constraints(token, obj):
                    for child in token.children:
                        for cand in child_constraints:
                            if self.check_constraints(child, cand):
                                found_chunk = False
                                for chunk in utterance.noun_chunks:
                                    if token in chunk:
                                        found_chunk = chunk
                                        break
                                candidates.append((token, found_chunk, utterance))
        return candidates

    '''
    def extract_time_candidates(self, utterance, parent_constraints,
                           candidate_constraints):
        candidates = []
        for token in utterance:
            for obj in parent_constraints:
                if self.check_constraints(token, obj):
                    for child in token.children:
                        doc_child = self.get_doc(child, utterance)
                        for cand in candidate_constraints:
                            if self.check_constraints(doc_child, cand):
                                if child.lefts:
                                    for l in child.lefts:
                                        if self.check_constraints(l, cand):
                                            for chunk in utterance.noun_chunks:
                                                if l in chunk:
                                                    candidates.append((l, chunk, utterance))
                                                    break
                                    continue
                                else:
                                    for chunk in utterance.noun_chunks:
                                        if child in chunk:
                                            candidates.append((child, chunk, utterance))
        return candidates
    '''

    def get_doc(self, token, utterance):
        for tok in utterance:
            if tok.text == token.text:
                return tok

    def get_time(self, doc):
        from frameit.time_extraction import time_parser
        '''
        Return Args:
            This function uses spacy's time parser, and returns a list of candidate entities (Spans)
        '''
        times = []
        for ent in doc.ents:
            tokens = []
            if ent.label_ == "TIME":
                for token in ent:
                    tokens.append(token)
            times.extend(tokens)

        if not times:
            return(time_parser(doc))
        else:
            return times

    def get_date(self, doc):
        '''
        Return Args:
            This function uses spacy's date parser, and returns a list of candidate entities (Spans)
        '''
        times = []
        for ent in doc.ents:
            tokens = []
            if ent.label_ == "DATE":
                for token in ent:
                    tokens.append(token)
            times.extend(tokens)
        
        return times

    def check_constraints(self, token, obj):
        if "lemma" in obj and token.lemma_.lower() not in obj["lemma"]:
            return False
        if "pos" in obj and token.pos_.lower() not in obj["pos"]:
            return False
        if "dep" in obj and token.dep_.lower() not in obj["dep"]:
            return False
        return True

    def lemma_str(self, doc):
        lemmas = []
        for token in doc:
            lemmas.append(token.lemma_)
        return " ".join(lemmas)

    def get_root(self, doc):
        for token in doc:
            if token.dep_ == 'ROOT':
                return token
        return None

    def get_tree(self, root, tree_set):
        if len(list(root.children)) == 0:
            return "(" + root.dep_ + ")"
        s = "(" + root.dep_
        for child in root.children:
            s += self.get_tree(child, tree_set)
        s += ")"
        tree_set.add(s)
        return s

    def extract_dobj(self, utter, lemma_list, POS="VERB"):
        ret = []
        for token in utter.spacy:
            # print("token ", token)
            if token.lemma_ in lemma_list and token.pos_ == POS:
                # print("token rights ", token.rights)
                # print("token lefts ", token.lefts)
                for child in list(token.rights):
                    # print("child ", child)
                    if child.dep_ == 'dobj':
                        # print("child chunks ", utter.spacy.noun_chunks)
                        for chunk in utter.spacy.noun_chunks:
                            if child in chunk:
                                ret.append((child, chunk))
        return ret

    def extract_pobj(self, utter, lemma_list, POS="VERB"):
        ret = []
        for token in utter.spacy:
            if token.lemma_ in lemma_list and token.pos_ == POS:
                for child in list(token.rights):
                    if child.dep_ == 'pobj' or child.dep_ == 'dative':
                        chunks = []
                        for chunk in utter.spacy.noun_chunks:
                            if child in chunk:
                                chunks.append((child, chunk))
                        if chunks:
                            ret.extend(chunks)
                        else:
                            ret.append((child, child))
        return ret

    def extract_nsubj(self, utter, lemma_list, POS="VERB"):
        ret = []
        for token in utter.spacy:
            if token.lemma_ in lemma_list and token.pos_ == POS:
                for child in list(token.lefts):
                    if child.dep_ == 'nsubj':
                        for chunk in utter.spacy.noun_chunks:
                            if child in chunk:
                                ret.append((child, chunk))
        return ret

    def find_span_by_text(self, text, doc):
        words = text.split()
        span = None
        if len(words) == 1:
            for token in doc:
                if token.text.lower() == text:
                    return doc[token.i:token.i+1]
        else:
            first_word = words[0]
            last_word = words[-1]
            first_index = None
            last_index = None
            for token in doc:
                if token.text.lower() == first_word:
                    first_index = token.i
                    continue
                if token.text.lower() == last_word and first_index is not None:
                    last_index = token.i
                    break
            if first_index and last_index:
                span = doc[first_index:last_index+1]
        return span
