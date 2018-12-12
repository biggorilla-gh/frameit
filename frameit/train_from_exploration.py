##For testing only, to be removed before release
import json
import inspect
import sys
from frameit import Frame, FrameAttribute, Utterance
from frameit.corpus import Corpus

def main(argv):
    directory = {}
    with open(argv, 'r') as infile:
        directory = json.load(infile)
    if directory:
        try:
            train_frame_wrapper(directory['outfile'],frame_file=directory['frame_file'], 
                ml_attr_files=directory['ml_attr_files'], lambda_attr_files=directory['lambda_attr_files'])
        except KeyError:
            print("Failed to access key in file directory, please check to make sure that %s is formatted properly", argv)
    else: print('Failed to load frame directory file, please check %s', argv)


def train_frame_wrapper(frame_outfile_name, 
    frame_file='frame_training_info.json', ml_attr_files=['attr1.json'], lambda_attr_files=['attr2.json']):
    attributes = []
    with open(frame_file, 'r') as infile:
        frame_schema = json.load(infile)
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
    for e in schema['positive_set']:
        pos_set.add(Utterance(e, None))
    neg_set = set()
    for e in schema['negative_set']:
        neg_set.add(Utterance(e, None))
    frame.addExamples(pos_set)
    frame.trainModel(corpus, scale_to=schema['scale_to'], epochs=schema['epochs'], batch_size=schema['batch_size'],
                     reg_param=schema['reg_param'], neg_set=neg_set)
    return frame

if __name__ == "__main__":
    main(sys.argv)