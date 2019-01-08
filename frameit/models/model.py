import json
import numpy as np
from random import shuffle

from frameit import Utterance
from frameit.models.model_utils import to_categorical
from frameit.models.model_utils import build_cnn_model, EMBEDDING_DIM
from frameit.models.model_utils import dict_to_keras_model
from frameit.models.model_utils import keras_model_to_dict

REGULARIZATION_PARAM = 0.1


class CoreModel(object):
    def __init__(self, name=''):
        self.name = name
        self.model = None

    def _reload(self, state):
        self.__setstate__(state)
        return

    def get_state(self):
        state = {'name': self.name}
        return state

    def set_state(self, state):
        self.name = state['name']

class Model(CoreModel):
    def __init__(self, name='', max_length=50, lang='en'):
        super(self.__class__, self).__init__(name+"_sent")
        self.max_length = 50
        self.lang = lang
        self.model = None

    def train(self, pos_set, neg_set, mandatory_neg_set, reg_param=None,
              batch_size=128, epochs=4, scale_to=4000):
        assert isinstance(pos_set, set)
        assert isinstance(neg_set, set)
        assert (len(pos_set) <= len(neg_set))

        # creating a shuffled list of positive instances
        pos_list = list(pos_set)
        shuffle(pos_list)
        neg_list = list(set(neg_set) - set(pos_set))
        shuffle(neg_list)

        # Create train and dev sets
        holdout_size = len(pos_list)//10
        dev_p_list = pos_list[:holdout_size]
        dev_n_list = neg_list[:holdout_size]
        tr_p_list = pos_list[holdout_size:]
        tr_n_list = neg_list[holdout_size:]

        # scaling up the data if necessary
        min_size = scale_to if len(tr_p_list) < scale_to else len(tr_p_list)
        scaled_tr_p = (tr_p_list *
                       ((min_size // len(tr_p_list)) + 1))[:min_size]
        scaled_tr_n = (tr_n_list *
                       ((min_size // len(tr_n_list)) + 1))[:min_size]

        # creating the dev data
        dev_data = dev_p_list + dev_n_list
        dev_labels = [1]*holdout_size + [0]*holdout_size

        # adding mandatory negative set and creating the training data
        if mandatory_neg_set:
            scaled_tr_n[:len(mandatory_neg_set)] = list(mandatory_neg_set)
        train_data = scaled_tr_p + scaled_tr_n
        labels = [1]*min_size + [0]*min_size

        # more shuffling
        tmp_data = list(zip(train_data, labels))
        shuffle(tmp_data)
        train_data = [x[0] for x in tmp_data]
        labels = [x[1] for x in tmp_data]
        # Create Keras model
        if reg_param:
            model = build_cnn_model(self.max_length, reg_param, lang=self.lang)
        else:
            model = build_cnn_model(self.max_length, lang=self.lang)

        # Convert text data to matrix
        x_train = np.zeros((min_size*2, self.max_length, EMBEDDING_DIM[self.lang]))
        for i, hm in enumerate(train_data):
            for j, t in enumerate(hm.spacy):
                if j == self.max_length:
                    break
                x_train[i][j] = t.vector

        x_val = np.zeros((holdout_size*2, self.max_length, EMBEDDING_DIM[self.lang]))
        for i, hm in enumerate(dev_data):
            for j, t in enumerate(hm.spacy):
                if j == self.max_length:
                    break
                x_val[i][j] = t.vector
        # Train model
        cat_labels = to_categorical(np.asarray(labels))
        dev_cat_labels = to_categorical(np.asarray(dev_labels))
        history = model.fit(x_train, cat_labels,
                            validation_data=(x_val, dev_cat_labels),
                            epochs=epochs, batch_size=batch_size)

        self.model = model

        return history

    def predict(self, data):
        for x in data:
            assert isinstance(x, Utterance)
        x_pred = np.zeros((len(data), self.max_length, EMBEDDING_DIM[self.lang]))
        for i, hm in enumerate(data):
            for j, t in enumerate(hm.spacy):
                if j == self.max_length:
                    break
                x_pred[i][j] = t.vector

        labels = self.model.predict(x_pred)
        return labels

    # --------------------------------------
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
                 'model': keras_model_to_dict(self.model)}
        return state

    def set_state(self, state):
        self.name = state['name']
        #accommodating pre-internationalization code
        lang = state.get('lang', None)
        if lang:
            self.lang = lang
        self.model = dict_to_keras_model(state['model'])
