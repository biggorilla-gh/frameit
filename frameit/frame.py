import json

from frameit.models import Model
from frameit.utterance import Utterance
from frameit.frameattr import FrameAttribute


class Frame(object):
    def __init__(self, name, lang='en'):
        self.name = name
        self.utterances = set()
        self.models = []
        self.weights = []
        self.sum_weights = 0.0
        self.num_models = 0
        self.attributes = set()
        self.lang = lang

    def addExample(self, utterance):
        assert isinstance(utterance, Utterance)
        self.utterances.add(utterance)

    def addExamples(self, utterances):
        for utterance in utterances:
            self.addExample(utterance)

    def addAttribute(self, attrib):
        self.attributes.add(attrib)

    def getAttribute(self, name):
        for att in self.attributes:
            if att.name == name:
                return att
        return None

    @property
    def model(self):
        if self.num_models == 0:
            self.addModel(Model(lang=self.lang))
        return self.models[0]

    def addModel(self, model, weight=1.0):
        self.models.append(model)
        self.weights.append(weight)
        self.num_models += 1
        self.sum_weights += weight
        
    def predict(self, data):
        for x in data:
            assert isinstance(x, Utterance)

        labels = []
        for x in data:
            score = 0.0
            for i in range(self.num_models):
                score += self.weighs[i] * model.predict([x])[0][1]
            score /= self.sum_weights
            labels.append([1-score, score])
        return labels
                

    def trainModel(self, corpus, neg_set=None, reg_param=None,
                   batch_size=128, epochs=4, scale_to=4000, index=0):
        while(self.num_models <= index):
            self.addModel(Model(lang=self.lang))
        history = self.models[index].train(self.utterances, set(corpus.utterances),
                                   neg_set, reg_param=reg_param,
                                   batch_size=batch_size, epochs=epochs,
                                   scale_to=scale_to)
        return history

    def trainAll(self, corpus):
        self.trainModel()
        for attrib in self.attributes:
            attrib.trainModel(corpus)

    # ------------------------------------------
    def __str__(self):
        s = "Frame: " + self.name + "\n"
        for attr in self.attributes:
            s += "\t" + str(attr)
        return s

    def save(self, filename):
        with open(filename, "w") as handle:
            json.dump(self.get_state(), handle, indent=2)

    @classmethod
    def load(cls, filename):
        with open(filename, "r") as handle:
            state = json.load(handle)
        frame = cls(None)
        frame.set_state(state)
        return frame

    def get_state(self):
        state = {'name': self.name,
                 'lang': self.lang,
                 'models': [model.get_state() for model in self.models],
                 'weights': self.weights,
                 'attributes': [attr.get_state() for attr in self.attributes]}
        return state

    def set_state(self, state):
        self.name = state['name']
        self.lang = state.get('lang', 'en')
        self.attributes = []
        for attr_state in state['attributes']:
            attribute = FrameAttribute(None, None)
            attribute.set_state(attr_state)
            self.attributes.append(attribute)

        model_states =  state['models'] if 'models' in state else [state['model']]
        model_weights = state['weights'] if 'weights' in state else [1.0] 
        
        for i in range(len(model_states)):
            model = Model(lang=self.lang)
            model.set_state(model_states[i])
            self.addModel(model, model_weights[i])

