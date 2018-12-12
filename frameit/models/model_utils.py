import json
import keras
import numpy as np
from io import TextIOWrapper
from keras import regularizers
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras.optimizers import Adam 
from keras.layers import concatenate
from keras.models import model_from_json
from keras.layers import Input, Flatten, Dense, Conv1D, MaxPooling1D


EMBEDDING_DIM = {
                    'en':300,
                    'fr':384,
                    'ja':200
            }


def keras_to_json(model, file_name=None):
    np_weights = model.get_weights()
    # converting weights to list since ndarrays can't be serialized to json
    weights = [w.tolist() for w in np_weights]
    model_desc = json.loads(model.to_json())
    full_desc = {'model': model_desc, 'weights': weights}
    if file_name is None:
        return json.dumps(full_desc)
    # else
    with open(file_name, 'w') as out_file:
        json.dump(full_desc, out_file, indent=4, sort_keys=True)


def json_to_keras(source):
    if isinstance(source, str):
        full_desc = json.loads(source)
    elif isinstance(source, TextIOWrapper):
        full_desc = json.load(source)
    else:
        # TODO: raise an exception
        return None
    weights = full_desc['weights']
    model_desc = full_desc['model']
    model = model_from_json(json.dumps(model_desc))
    np_weights = [np.array(w) for w in weights]
    model.set_weights(np_weights)
    return model


def keras_model_to_dict(model):
    np_weights = model.get_weights()
    # converting weights to list since ndarrays can't be serialized to json
    weights = [w.tolist() for w in np_weights]
    arch = json.loads(model.to_json())
    return {'arch': arch, 'weights': weights}


def dict_to_keras_model(d):
    arch = d['arch']
    model = model_from_json(json.dumps(arch))
    weights = d['weights']
    np_weights = [np.array(w) for w in weights]
    model.set_weights(np_weights)
    return model


def np_dict_to_dict(d):
    for k, v in d.items():
        if isinstance(v, np.ndarray):
            d[k] = v.tolist()
    return d


def dict_to_np_dict(d):
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = np.array(v)
    return d


def build_cnn_model(max_length, reg_param=0.01, lang='en'):
    new_model = Sequential()
    new_model.add(Conv1D(128, 2, activation='relu',
                         input_shape=((max_length, EMBEDDING_DIM[lang])),
                         kernel_regularizer=regularizers.l2(reg_param)))
    new_model.add(MaxPooling1D(2))
    new_model.add(Conv1D(128, 2, activation='relu',
                         kernel_regularizer=regularizers.l2(reg_param)))
    new_model.add(MaxPooling1D(2))
    new_model.add(Conv1D(128, 5, activation='relu',
                         kernel_regularizer=regularizers.l2(reg_param)))
    new_model.add(MaxPooling1D(2))
    new_model.add(Flatten())
    new_model.add(Dense(128, activation='relu',
                        kernel_regularizer=regularizers.l2(reg_param)))
    new_model.add(Dense(2, activation='softmax'))
    #rms = RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
    rms = Adam()
    new_model.compile(loss='categorical_crossentropy',
                      optimizer=rms, metrics=['acc'])
    return new_model


def build_attr_cnn_model(max_length, reg_param=0.01, lang='en'):
    word_input = Input(shape=(EMBEDDING_DIM[lang],))
    first_dense = \
        Dense(128, kernel_regularizer=regularizers.l2(reg_param))(word_input)

    sent_input = Input(shape=(max_length, EMBEDDING_DIM[lang]))
    conv_l = Conv1D(128, 2, activation='relu',
                    kernel_regularizer=regularizers.l2(reg_param))(sent_input)
    max_pool = MaxPooling1D(2)(conv_l)
    conv_l2 = Conv1D(128, 2, activation='relu',
                     kernel_regularizer=regularizers.l2(reg_param))(max_pool)
    max_pool2 = MaxPooling1D(2)(conv_l2)
    conv_l3 = Conv1D(128, 5, activation='relu',
                     kernel_regularizer=regularizers.l2(reg_param))(max_pool2)
    max_pool3 = MaxPooling1D(2)(conv_l3)
    flat = Flatten()(max_pool3)
    second_dense = Dense(128,  activation='relu',
                         kernel_regularizer=regularizers.l2(reg_param))(flat)
    merged = concatenate([first_dense, second_dense])

    out = Dense(2, activation='softmax')(merged)
    model = keras.models.Model(inputs=[word_input, sent_input], outputs=out)

    # rms = RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
    rms = Adam()
    model.compile(loss='categorical_crossentropy',
                  optimizer=rms, metrics=['acc'])
    return model


def to_categorical(y, num_classes=None):
    """
    Converts a class vector (integers) to binary class matrix.
    E.g. for use with categorical_crossentropy.
    # Arguments
        y: class vector to be converted into a matrix
            (integers from 0 to num_classes)
        num_classes: total number of classes.
    # Returns
        A binary matrix representation of the input.
    """
    y = np.array(y, dtype='int').ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes))
    categorical[np.arange(n), y] = 1
    return categorical
