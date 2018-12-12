import json
from spacy.lexeme import Lexeme
from spacy.tokens import Token

from frameit import Corpus
from frameit.models.nocontext_model import NoContextModel
from frameit.models.context_model import ContextModel
from frameit.models.lambda_rule_model import LambdaRuleModel
from frameit.models.rule_model import RuleModel


class FrameAttribute(object):

    def __init__(self, name, constraints={}, unique=False, lang='en'):
        self.lang = lang
        self.name = name
        self.examples = set()
        self.model = set()
        self.constraints = constraints
        self.unique = unique

    def addExample(self, term):
        assert isinstance(term, Token) or isinstance(term, Lexeme)
        self.examples.add(term)

    def addExamples(self, examples):
        for term in examples:
            self.addExample(term)

    # Corpus is not really used, self.examples is used instead for
    # pos & neg examples
    def trainModel(self, corpus, type_='context', reg_param=None,
                   batch_size=128, epochs=4, scale_to=4000, func=None, func_name=None):
        if type_ == 'context':
            return self.train_context_model(reg_param,
                                            batch_size, epochs, scale_to)
        elif type_ == 'nocontext':
            return self.train_notcontext_model(corpus)
        elif type_ == 'rules':
            return self.train_rule_model()
        elif type_ == 'lambda_rules':
            return self.train_lambda_rule_model(corpus, func, func_name)

    def train_context_model(self, reg_param, batch_size,
                            epochs, scale_to):
        # error checking
        if not isinstance(next(iter(self.examples)), Token):
            raise ValueError('Malformed training data type for ' +
                             'the context dependent attribute model')
        self.model = ContextModel(self.name, self.name+"_TYPE", lang=self.lang)
        neg_set = set()
        for word in self.examples:
            for t in word.doc:
                # ignore if it's not matching the constraints
                if "POS" in self.constraints and \
                        t.pos_ not in self.constraints['POS']:
                    continue
                if t not in self.examples:
                    neg_set.add(t)
        return self.model.train(self.examples, neg_set, reg_param,
                                batch_size, epochs, scale_to)

    def train_notcontext_model(self, corpus):
        self.model = NoContextModel(self.name, self.name+"_TYPE", lang=self.lang)
        neg_set = set()
        neg_lemma = set()
        neg_list = []

        if isinstance(next(iter(self.examples)), Token):
            pos_lemma = set([t.lemma_.lower() for t in self.examples])
        else:
            pos_lemma = set([t.text.lower() for t in self.examples])

        pos_set = set()
        for token in self.examples:
            if isinstance(token, Token):
                if token.lemma_.lower() in pos_lemma:
                    pos_set.add(token)
            elif isinstance(token, Lexeme):
                if token.text.lower() in pos_lemma:
                    pos_set.add(token)

        pos_list = list(self.examples)

        sample_utterances = None
        if isinstance(corpus, Corpus):
            sample_utterances = corpus.utterances
        else:
            sample_utterances = corpus

        for utterance in sample_utterances:
            for t in utterance.spacy:
                if "POS" in self.constraints and \
                        t.pos_.upper() not in self.constraints['POS']:
                    continue
                if "DEP" in self.constraints and \
                        t.dep_.upper() not in self.constraints['DEP']:
                    continue

                if t.lemma_ not in pos_lemma:
                    if t.lemma_ not in neg_lemma:
                        neg_set.add(t)
                        neg_lemma.add(t.lemma_)
                    neg_list.append(t)

        return self.model.train(pos_list, neg_list)

    def train_lambda_rule_model(self, corpus, func, func_name):
        # error checking
        if not isinstance(next(iter(self.examples)), Token):
            raise ValueError('Malformed training data type for ' +
                             'the context dependent attribute model')
        self.model = LambdaRuleModel(self.name, func, func_name=func_name, lang=self.lang)
        neg_set = set()
        for word in self.examples:
            for t in word.doc:
                # ignore if it's not matching the constraints
                if "POS" in self.constraints and \
                        t.pos_ not in self.constraints['POS']:
                    continue
                if t not in self.examples:
                    neg_set.add(t)
        return self.model.train(self.examples, neg_set)

    def train_rule_model(self):
        pass

    # ------------------------------------------
    def __str__(self):
        return "Attribute: " + self.name + "\n"

    def save(self, filename):
        with open(filename, "w") as handle:
            json.dump(self.get_state(), handle)

    @classmethod
    def load(cls, filename):
        with open(filename, "r") as handle:
            state = json.load(handle)
        frameattr = cls(None)
        frameattr.set_state(state)
        return frameattr

    def get_state(self):
        state = {'name': self.name,
                 'lang': self.lang,
                 'model_type': self.model.__class__.__name__,
                 'constraints': self.constraints,
                 'unique': self.unique,
                 'attr_model': self.model.get_state()}
        return state

    def set_state(self, state):
        self.name = state['name']
        #backward compatibility
        self.lang = state.get('lang', 'en')
        self.unique = state['unique']
        self.constraints = state['constraints']
        model_type = state.get('model_type')
        self.model = eval(model_type)()
        self.model.set_state(state['attr_model'])
