import json
import numpy as np
from random import shuffle
from sklearn.linear_model import LogisticRegression

from frameit.models import CoreModel
from frameit.models.model_utils import EMBEDDING_DIM
from frameit.models.model_utils import np_dict_to_dict, dict_to_np_dict
from frameit.text_processing import TextProcessing


class NoContextModel(CoreModel):

    def __init__(self, name="", type_t=None, lang='en'):
        super(self.__class__, self).__init__(name+"_attr")
        self.type_t = type_t
        self.lang = lang
        self.model = None

    def train(self, pos_set, neg_set):
        assert isinstance(pos_set, set) or isinstance(pos_set, list)
        assert isinstance(neg_set, set) or isinstance(neg_set, list)
        
        self.model = LogisticRegression()
        # split into train and dev
        holdout_size = len(pos_set) // 10
        dev_data = list(pos_set)[:holdout_size]
        pos_set = list(pos_set)[holdout_size:]
        
        min_size = 4000 if len(pos_set) < 4000 else len(pos_set)
        train_data = (list(pos_set) *
                      ((min_size // len(pos_set)) + 1))[:min_size]
        
        neg_tmp = list(set(neg_set) - set(pos_set))
        # make a copy of neg_tmp since shuffle runs "in place"
        neg_tmp = list(neg_tmp)
        shuffle(neg_tmp)
        dev_data.extend(neg_tmp[:holdout_size])
        neg_train = (neg_tmp[holdout_size:] *
                     ((min_size // len(pos_set)) + 1))[:min_size]
        train_data.extend(neg_train)
        
        labels = [1]*min_size + [0]*min_size
        dev_labels = [1]*holdout_size + [0]*holdout_size
        
        # shuffle
        tmp_data = list(zip(train_data, labels))
        shuffle(tmp_data)
        train_data = [x[0] for x in tmp_data]
        labels = [x[1] for x in tmp_data]
        #
        # featurize
        tmp_train_data = np.zeros((len(train_data), EMBEDDING_DIM[self.lang]))
        # print("Debug line 54: ", self.lang)
        nlp = TextProcessing().nlp
        for i, d in enumerate(train_data):
            tmp_train_data[i] = nlp[self.lang](d.text).vector
        train_data = tmp_train_data
        tmp_dev_data = np.zeros((len(dev_data), EMBEDDING_DIM[self.lang]))
        for i, d in enumerate(dev_data):
            tmp_dev_data[i] = nlp[self.lang](d.text).vector
        dev_data = tmp_dev_data
        #
        # train
        self.model.fit(train_data, labels)
        #
        # return acc and dev acc
        return (self.model.score(train_data, labels),
                self.model.score(dev_data, dev_labels))

    def predict(self, words):
        # featurize
        data = np.zeros((len(words), EMBEDDING_DIM[self.lang]))
        for i, word in enumerate(words):
            data[i] = word.vector
        # return predictions
        return self.model.predict_proba(data)

    # -------------------------------------------
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
        copy_dict = self.model.__dict__.copy()
        state = {'name': self.name,
                 'lang': self.lang,
                 'type_t': self.type_t,
                 'linear_model': np_dict_to_dict(copy_dict)}
        return state

    def set_state(self, state):
        self.name = state['name']
        #accommodating pre-internationalization code
        self.lang = state.get('lang', 'en')
        self.type_t = state['type_t']
        self.model = LogisticRegression()
        self.model.__dict__ = dict_to_np_dict(state['linear_model'])
        
