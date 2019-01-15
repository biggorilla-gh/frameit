import os
import numpy
import random
import json
import inspect
import tensorflow as tf
import xml.etree.cElementTree as ET
from keras import backend
from spacy.tokens import Token
from tensorflow import set_random_seed
from frameit.utterance import Utterance
from frameit.utteraggr import UtteranceAggregator
from frameit.text_processing import TextProcessing
from frameit.frameattr import FrameAttribute
from frameit.frame import Frame




def set_seed(seed_num):
    random.seed(seed_num)
    numpy.random.seed(seed_num)
    set_random_seed(seed_num)
    os.environ['PYTHONHASHSEED'] = '0'
    session_conf = tf.ConfigProto(intra_op_parallelism_threads=1,
                                  inter_op_parallelism_threads=1)
    sess = tf.Session(graph=tf.get_default_graph(),
                      config=session_conf)
    backend.set_session(sess)

def swap_attributes(attr_examples, other_attr_examples):
    # building a doc to attribute dictionary
    doc2attrA = {}
    for attr in attr_examples:
        assert isinstance(attr, Token)
        doc2attrA[attr.doc] = attr
    doc2attrB = {}
    for attr in other_attr_examples:
        assert isinstance(attr, Token)
        doc2attrB[attr.doc] = attr
    # checking the keys that match
    docs_with_both_attr = \
        set(doc2attrA.keys()).intersection(set(doc2attrB.keys()))
    # swapping the attributes in each doc and building new utterances
    new_utterances = []
    new_attr_examples = []
    new_other_attr_examples = []
    attrA_index = None
    attrB_index = None 
    for doc in docs_with_both_attr:
        new_sequence = []
        for i, token in enumerate(doc):
            if token == doc2attrA[doc]:
                attrA_index = i
                new_sequence.append(doc2attrB[doc].text)
            elif token == doc2attrB[doc]:
                attrB_index = i
                new_sequence.append(doc2attrA[doc].text)
            else:
                new_sequence.append(token.text)
        new_string = ' '.join(new_sequence)
        new_utt = Utterance(new_string, None)
        new_utterances.append(new_utt)
        new_attr_examples.append(new_utt.spacy[attrA_index])
        new_other_attr_examples.append(new_utt.spacy[attrB_index])
    return new_utterances, new_attr_examples, new_other_attr_examples

def build_positive_set(corpus, string_list):
    ret = set()
    for string in string_list:
        ret.update(corpus.query(string))
    print('There are ' + str(len(ret)) + ' relevant messages in the corpus')
    return ret

def add_lemmas_to_set(corpus, string_list, existing_set=set()):
    ret = existing_set
    for string in string_list:
        ret.update(corpus.lemma_query(string))
    print('There are ' + str(len(ret)) + ' relevant messages in the corpus')
    return ret


def expand_with_hypernym(positive_utterances, positive_strings, corpus):
    corpus_aggr = UtteranceAggregator(positive_utterances)
    #Expand sets
    hypernyms = set()
    count = 0
    for c in positive_strings:
        try:
            hypernyms.update(corpus_aggr.hypernym_2_lemma[c])
        except KeyError as e:
            print(c)
            count += 1
    print("Number of strings for which no hypernyms were found ", str(count))

    for h in hypernyms:
        print(h)
        positive_utterances.update(corpus.query(h))
    print('There are ' + str(len(positive_utterances)) + ' relevant messages in the corpus')
    return positive_utterances

def trim_examples(positive_utterances, remove_list):
    new_positive_set = set()
    negative_set = set()
    for utterance in positive_utterances:
        for string in remove_list:
            match = False
            if string in utterance.text:
                match = True
                break
        if not match:
            new_positive_set.add(utterance)
        else:
            negative_set.add(utterance)
    print('There are ' + str(len(new_positive_set)) + ' relevant messages in the corpus')
    return new_positive_set, negative_set

def convert_data_to_xml(pos, neg, frame_name):
    root = ET.Element("root")
    doc = ET.SubElement(root, "doc")
    for e in pos:
        ET.SubElement(doc, "positive").text = e.text
    for e in neg:
        ET.SubElement(doc, "negative").text = e.text
    tree = ET.ElementTree(root)
    filename = frame_name + "_interim_data.xml"
    tree.write(filename)
    return filename

def save_frame_training_info_to_file(frame_name, corpus_file, positive_utterances, negative_set, 
                                    scale_to, epochs, batch_size, reg_param, filename, gold_filename):
    xml_filename = convert_data_to_xml(positive_utterances, negative_set, frame_name)
    # pos_list = list()
    # neg_list = list()
    # for utterance in positive_utterances:
    #     pos_list.append(utterance.text)
    # for utterance in negative_set:
    #     neg_list.append(utterance.text)
    save_data = {"frame_name": 'your_frame',
             "corpus_file": corpus_file,
             "positive_set": xml_filename,
             "negative_set": xml_filename,
             "scale_to": scale_to,
             "epochs": epochs,
             "batch_size": batch_size,
             "reg_param": reg_param,
             "gold_file": gold_filename
            }
    with open(filename, 'w') as outfile:
        json.dump(save_data, outfile)
    print("Saved info with filename %s." % filename)

def load_frame_pos_set(filename):
    with open(filename, 'r') as infile:
        loaded = json.load(infile)['positive_set']
        if type(loaded) is list:
            positive_list = loaded
        else:
            tree = ElementTree.parse(loaded)
            pos = tree.findall("positive")
            positive_list = [t.text for t in pos]
    print('There are ' + str(len(positive_list)) + ' relevant messages in the corpus')
    positive_utterances = set()
    for item in positive_list:
        positive_utterances.add(Utterance(item, None))
    return positive_utterances

def get_token_type(tokens):
    t = TextProcessing()
    candidate_set = set()
    for token in tokens:
        if token[1] is None:
            continue
        if len(token[1]) == 1:
            spacy_token = t.get_doc(token[1], token[2])
            candidate_set.add(spacy_token)
        else:
            cand = token[0]
            candidate_set.add(cand)

    return candidate_set

def get_attribute_candidates(pos_set, dep_type, dep, cand):
    t = TextProcessing()
    attr1_candidates = t.get_attributes(pos_set, "parent", dep, cand)
    return get_token_type(attr1_candidates)

def remove_attribute_examples(examples, del_list):
    ret = list(examples)
    for t in examples:
        if t.text in del_list:
            ret.remove(t)
        else:
            continue
    return ret

def save_ml_attr_data_to_file(attr, examples, filename):
    for e in examples:
        attr['examples'].append(tuple([e.doc.text, e.i]))
    with open(filename, 'w') as outfile:
        json.dump(attr, outfile)
    print('Saved attribute %s to file %s' % (attr['name'], filename))

def save_lambda_attr_data_to_file(attr, func, filename):
    attr['func'] = inspect.getsource(func)
    attr['func_name'] = func.__name__
    with open(filename, 'w') as outfile:
        json.dump(attr, outfile)
    print('Saved attribute %s to file %s' % (attr['name'], filename))

def train_frame_wrapper(frame_outfile_name, 
    frame_file='frame_training_info.json', ml_attr_files=['attr1.json'], lambda_attr_files=['attr2.json']):
    from frameit import Corpus
    attributes = []
    with open(frame_file, 'r') as infile:
        frame_schema = json.load(infile)
    gold_file = frame_schema["gold_file"]
    corp = Corpus(frame_schema["corpus_file"])
    print('Importing machine learning attributes')
    for ml_attribute_file in ml_attr_files:
        attributes.append(train_ml_attribute(corp, ml_attribute_file))
    print('Importing lambda_rule attributes')
    for lambda_attribute_file in lambda_attr_files:
        attributes.append(train_lambda_attribute(corp, lambda_attribute_file))
    print('Rebuilding frame')
    frame = reconstruct_frame(corp, frame_schema)
    for attr in attributes:
        frame.addAttribute(attr)
    print('Saving frame to file')
    frame.save(frame_outfile_name)
    print('Done!')
    print("Corresponding gold file is ", gold_file)
    return gold_file

def train_ml_attribute(corpus, file):
    with open(file, 'r') as infile:
        schema = json.load(infile)
    attribute = FrameAttribute(schema['name'], schema['linguistic_info'], schema['unique'])
    reconstructed_examples = set()
    for e in schema['examples']:
        doc = Utterance(e[0], None).spacy
        reconstructed_examples.add(doc[e[1]])
    attribute.addExamples(reconstructed_examples)
    print('Training ', schema['name'])
    attribute.trainModel(corpus, "nocontext")
    return attribute

def train_lambda_attribute(corpus, file):
    dummy = Utterance('silly legacy code that needs at least this many examples to run', None)
    with open(file, 'r') as infile:
        schema = json.load(infile)
    attribute = FrameAttribute(schema['name'], schema['linguistic_info'], schema['unique'])
    namespace = {}
    model_text = schema['func']
    name = schema['func_name']
    print('Training ', schema['name'])
    attribute.addExamples(dummy.spacy)
    attribute.trainModel(corpus, type_="lambda_rules", func=model_text, func_name=name)
    return attribute

def reconstruct_frame(corpus, schema):
    frame = Frame(schema['frame_name'])
    pos_set = set()
    neg_set = set()
    if type(schema['positive_set']) is list:
        positive_list = schema['positive_set']
        negative_list = schema['negative_set']
    else:
        tree = ElementTree.parse(schema['positive_set'])
        pos = tree.findall("positive")
        neg = tree.findall("negative")
        positive_list = [t.text for t in pos]
        negative_list = [t.text for t in neg]
        for e in positive_list:
            pos_set.add(Utterance(e, None))
        for e in negative_list:
            neg_set.add(Utterance(e, None))
    frame.addExamples(pos_set)
    frame.trainModel(corpus, scale_to=schema['scale_to'], epochs=schema['epochs'], batch_size=schema['batch_size'],
                     reg_param=schema['reg_param'], neg_set=neg_set)
    return frame


