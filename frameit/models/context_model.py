import json
import numpy as np
from random import shuffle

from frameit.models import CoreModel
from frameit.models.model_utils import to_categorical
from frameit.models.model_utils import build_attr_cnn_model, EMBEDDING_DIM
from frameit.models.model_utils import dict_to_keras_model
from frameit.models.model_utils import keras_model_to_dict


class ContextModel(CoreModel):

    def __init__(self, name="", max_length=50, lang='en'):
        super(self.__class__, self).__init__(name+"_deep_attr")
        self.max_length = 50
        self.lang = lang
        self.model = None

    def train(self, pos_set, neg_set, reg_param=None,
              batch_size=128, epochs=4, scale_to=4000):
        # TODO: add assert for neg_set to have at least 10% of the pos set
        assert isinstance(pos_set, set)
        assert isinstance(neg_set, set)

        # Create train and dev sets
        holdout_size = len(pos_set) // 10
        dev_data = list(pos_set)[:holdout_size]
        pos_set = list(pos_set)[holdout_size:]

        min_size = scale_to if len(pos_set) < scale_to else len(pos_set)
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

        # Create Keras model
        if reg_param:
            model = build_attr_cnn_model(self.max_length, reg_param)
        else:
            model = build_attr_cnn_model(self.max_length)

        # Convert text data to matrix
        x_train = np.zeros((min_size*2, self.max_length, EMBEDDING_DIM[self.lang]))
        x_words = np.zeros((min_size*2, EMBEDDING_DIM[self.lang]))
        for i, token in enumerate(train_data):
            x_words[i] = token.vector
            for j, t in enumerate(token.doc):
                if j == self.max_length:
                    break
                x_train[i][j] = t.vector

        x_val = np.zeros((holdout_size*2, self.max_length, EMBEDDING_DIM[self.lang]))
        words_val = np.zeros((holdout_size*2, EMBEDDING_DIM[self.lang]))
        for i, token in enumerate(dev_data):
            words_val[i] = token.vector
            for j, t in enumerate(token.doc):
                if j == self.max_length:
                    break
                x_val[i][j] = t.vector
        # Train model
        cat_labels = to_categorical(np.asarray(labels))
        cat_dev_labels = to_categorical(np.asarray(dev_labels))
        history = model.fit([x_words, x_train], cat_labels,
                            validation_data=([words_val, x_val],
                                             cat_dev_labels),
                            epochs=epochs, batch_size=batch_size)
        self.model = model
        return history

    def predict(self, data):
        x_pred = np.zeros((len(data), self.max_length, EMBEDDING_DIM[self.lang]))
        x_word = np.zeros((len(data), EMBEDDING_DIM[self.lang]))
        for i, token in enumerate(data):
            x_word[i] = token.vector
            for j, t in enumerate(token.doc):
                if j == self.max_length:
                    break
                x_pred[i][j] = t.vector
        labels = self.model.predict([x_word, x_pred])
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
                 'model': keras_model_to_dict(self.model)}
        return state

    def set_state(self, state):
        self.name = state['name']
        if 'lang' in state.keys():
            self.lang = state['lang']
        else:
            self.lang = 'en'
        self.model = dict_to_keras_model(state['model'])
