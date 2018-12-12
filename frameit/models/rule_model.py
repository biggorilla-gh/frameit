import numpy as np
import re

from frameit.models.model import CoreModel
from frameit.text_processing import TextProcessing

class RuleModel(CoreModel):
    def __init__(self, name='', lang='en'):
        super(self.__class__, self).__init__(name+"_rule_attr")
        self.nlp = TextProcessing().nlp[lang]
        self.rules = []
        self.lang = lang
        self.patterns = []
        
    def add_rule(self, rule_text):
        self.rules.append(self.nlp(rule_text))

    def add_pattern(self, pattern_text):
        self.patterns.append(re.compile(pattern_text))

    def matches(self, start, doc, rule):
        n = len(doc)
        k = len(rule)
        if start + k > n:
            return None
        matching_tokens = []
        for i in range(k):
            if rule[i].text == '*':
                matching_tokens.append(doc[start+i])
            elif doc[start+i].lower != rule[i].lower:
                return None
        return matching_tokens

    def matches_patterns(self, tokens):
        if not tokens:
            return False
        first = tokens[0]
        last = tokens[-1]
        doc = first.doc
        span = doc[first.i : last.i + 1]
        for pattern in self.patterns:
            if pattern.match(span.text):
                return True
        return False
        
    def align(self, doc, rule):
        n = len(doc)
        k = len(rule)
        result = set()
        for start in range(n - k + 1):
            matching_tokens = self.matches(start, doc, rule)
            if self.matches_patterns(matching_tokens):
                result.update(matching_tokens)
        return result
        
    def extract(self, doc):
        result = set()
        for rule in self.rules:
            matching_tokens = self.align(doc, rule)
            if matching_tokens:
                result.update(matching_tokens)
        return result
        
    def predict(self, data):
        pred = np.zeros((len(data), 2))
        for i, token in enumerate(data):
            matching_tokens = self.extract(token.doc)
            if token in matching_tokens:
                 pred[i][1] = 1.0
        return pred

    def get_state(self):
        state = {'name': self.name,
                 'lang': self.lang,
                 'rules': [r.text for r in self.rules],
                 'patterns': [p.pattern for p in self.patterns]}
        return state

    def set_state(self, state):
        self.name = state['name']
        #accommodating pre-internationalization code
        self.lang = state.get('lang', 'en')
        self.rules = [self.nlp(r) for r in state['rules']]
        self.patterns = [re.compile(p) for p in state['patterns']]
        
        
