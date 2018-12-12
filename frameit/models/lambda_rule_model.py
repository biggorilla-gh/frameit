import json
import inspect

from frameit.models import CoreModel


class LambdaRuleModel(CoreModel):

    def __init__(self, name='', func=None, func_name=None, lang='en'):
        super(self.__class__, self).__init__(name + "_lambda_attr")
        self.lang = lang
        if type(func) is str:
            self.model_text = func
            self.func_name = func_name
            namespace = {}
            exec(self.model_text, namespace)
            self.model = namespace[self.func_name]
        else:
            self.model = func
            self.func_name = '' if func is None else func.__name__
            self.model_text = '' if func is None else inspect.getsource(func)

    def train(self, pos_set, neg_set):
        # This simply does nothing except report how good your rule is
        assert isinstance(pos_set, set)
        assert isinstance(neg_set, set)

        # Running the rules on all sentences
        extracted_tokens = set()
        for candid_token in pos_set.union(neg_set):
            curr_doc = candid_token.doc
            results = self.model(curr_doc)
            for token in results:
                extracted_tokens.add(token)

        # Evaluating how good the results are
        tp, fp = 0, 0
        for token in extracted_tokens:
            if token in pos_set:
                tp += 1
            elif token in neg_set:
                fp += 1
            else:
                # TODO: This is a weird case we need to decide about.
                pass
        if tp + fp == 0:
            return (0, 0)
        fn = len(pos_set) - tp
        precision = float(tp) / (tp + fp)
        recall = float(tp) / (tp + fn)
        return (precision, recall)

    def predict(self, data):
        labels = []
        for candid_token in data:
            curr_doc = candid_token.doc
            if curr_doc == None:
                print("Error: .doc field of candidate token {0} was None".format(str(candid_token)))
            namespace = {}
            results = self.model(curr_doc)
            if candid_token in results:
                labels.append((candid_token, 1.0))
            else:
                labels.append((candid_token, 0.0))
        return labels

    # ---------------------------------------------
    def save(self, filename):
        with open(filename, "w") as handle:
            json.dump(self.get_state(), handle)

    @classmethod
    def load(cls, filename):
        with open(filename, "r") as handle:
            state = json.load(handle)
        model = cls()
        model.set_state(state)
        return model

    def get_state(self):
        state = {'name': self.name,
                 'lang': self.lang,
                 'model_text': self.model_text,
                 'func_name': self.func_name}
        return state

    def set_state(self, state):
        self.name = state['name']
        #accommodating pre-internationalization code
        self.lang = state.get('lang', 'en')
        self.model_text = state['model_text']
        self.func_name = state['func_name']
        namespace = {}
        exec(self.model_text, namespace)
        self.model = namespace[self.func_name]
