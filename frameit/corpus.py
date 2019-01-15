import os
import json
import math
import time
import warnings
import numpy as np
import pandas as pd
import whoosh.analysis as analysis
from whoosh.fields import Schema, ID, TEXT, NGRAM
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from scipy.spatial.distance import cosine

from frameit.utterance import Utterance
from frameit.log_utils import log_progress
from frameit.text_processing import TextProcessing


class Corpus(object):

    def __init__(self, input_, limit=None, build_index=False, csv_path='', lang='en'):
        # checking the type of input
        print("init Corpus")
        self.lang = lang
        if isinstance(input_, pd.DataFrame):
            if limit is None:
                self.data = input_
            else:
                self.data = input_.head(limit)
            path = csv_path
        elif isinstance(input_, str):
            if limit is None:
                self.data = pd.read_csv(input_)
            else:
                self.data = pd.read_csv(input_, nrows=limit)
            if csv_path:
                path=csv_path
            else:
                path = input_
        else:
            raise ValueError("The input to the corpus should be either a \
                             file name or a DataFrame.")
        # Step 1) loading the sentences
        all_text = self.data['text'].tolist()

        # Step 2) Load semafor results
        print("Parsing the Semafor data... ")
        semafor_file = os.path.dirname(path) + "/semaforData.json"
        framenet = None
        if os.path.isfile(semafor_file):
            with open(semafor_file, "rb") as f:
                framenet = f.readlines()
        else:
            warnings.warn('No FrameNet data found for the corpus.')

        # Step 3) Load deepsrl results
        print("Parsing the DeepSRL data... ")
        deepsrl_file = os.path.dirname(path) + "/deepsrlData.json"
        deepsrl = None
        if os.path.isfile(deepsrl_file):
            with open(deepsrl_file, "rb") as f:
                deepsrl = f.readlines()
        else:
            warnings.warn('No ProbBank data found for the corpus.')

        # Creating utterances from the loaded data
        self.utterances = []
        print("Creating Utterances...")
        time.sleep(0.3)   # to avoid prints in the middle of the progress bar
        index = 0
        for sent in log_progress(all_text):
            self.utterances.append(Utterance(sent, _id=index, lang=self.lang))
            utterance = self.utterances[index]
            utterance.frames = getFrames(framenet, index)
            utterance.propbank = getPropBank(deepsrl, index)
            index += 1
        time.sleep(0.3)   # to avoid prints in the middle of the progress bar

        # Building or loading indices
        self.prepare_indices(build_index, path)

    def prepare_indices(self, build_index, path):
        if build_index:
            print("Indexing corpus...")
            schema = None
            if self.lang == "ja":
                schema = Schema(path=ID(stored=True), content=NGRAM(stored=True))
            else:
                ana = analysis.StandardAnalyzer(stoplist=None, minsize=0)
                schema = Schema(path=ID(stored=True), content=TEXT(analyzer=ana))
            index_directory = os.path.dirname(path) + "/tmp/indices/indexdir"
            if not os.path.exists(index_directory):
                os.makedirs(index_directory)
            self.ix = create_in(index_directory, schema)
            with self.ix.writer(limitmb=2048, multisegment=True) as writer:
                i = 0
                for utterance in log_progress(self.utterances):
                    writer.add_document(path=str(i),
                                        content=utterance.text)
                    i += 1

            print("Indexing corpus by lemma...")
            if self.lang == "ja":
                schema = Schema(path=ID(stored=True), content=NGRAM(stored=True))
            else:
                ana = analysis.StandardAnalyzer(stoplist=None, minsize=0)
                schema = Schema(path=ID(stored=True), content=TEXT(analyzer=ana))
            lemma_index_directory = os.path.dirname(path) + \
                "/tmp/indices/lemmaindexdir"
            if not os.path.exists(lemma_index_directory):
                os.makedirs(lemma_index_directory)
            self.ix_lemma = create_in(lemma_index_directory, schema)
            with self.ix_lemma.writer(limitmb=2048,
                                      multisegment=True) as writer:
                i = 0
                for utterance in log_progress(self.utterances):
                    lemmas = [token.lemma_ for token in utterance.spacy]
                    writer.add_document(path=str(i),
                                        content=" ".join(lemmas))
                    i += 1
        else:
            print("Loading indices...")
            index_directory = os.path.dirname(path) + "/tmp/indices/indexdir"
            if not os.path.exists(index_directory):
                raise IOError('No existing indices! You should build ' +
                              'indices before trying to load them.')
            self.ix = open_dir(index_directory)

            print("Loading lemma indices...")
            index_directory = os.path.dirname(path) + \
                "/tmp/indices/lemmaindexdir"
            if not os.path.exists(index_directory):
                raise IOError('No existing indices! You should build ' +
                              'indices before trying to load them.')
            self.ix_lemma = open_dir(index_directory)

    def find_nearest_n(self, query_str, n, subset=None):
        query = Utterance(query_str, 999999, lang=self.lang).spacy.vector
        utt_set = list(subset) if subset else self.utterances
        distances = np.zeros(len(utt_set))
        for i, utterance in enumerate(utt_set):
            tmp = cosine(query, utterance.spacy.vector)
            if math.isnan(tmp) or tmp > 1:
                distances[i] = 100
            else:
                distances[i] = tmp
        top_indexes = distances.argsort()
        nearest_utts = [utt_set[j] for j in top_indexes][:n]
        nearest_dists = distances[top_indexes][:n]
        return nearest_utts, nearest_dists

    def query(self, query, sent_level=False):
        with self.ix.searcher() as searcher:
            query_p = None
            if self.lang == "ja":
                query_p = QueryParser("content",
                                  self.ix.schema).parse('%s' % query)
            else:
                query_p = QueryParser("content",
                                  self.ix.schema).parse('"%s"' % query)
            results = searcher.search(query_p, limit=None)
            raw_res = [self.utterances[int(res['path'])] for res in results]
        if not sent_level:
            return raw_res
        else:
            # finding the sentence that contains the query
            new_res = []
            for utt in raw_res:
                for sent_num, sent in enumerate(utt.spacy.sents):
                    if query in sent.text:
                        new_res.append(Utterance(sent.text, utt.id, sent_num, lang=self.lang))
            return new_res

    def lemma_query(self, query, sent_level=False):
        spacy_string = TextProcessing().nlp[self.lang](query)
        lemma_list = [token.lemma_ for token in spacy_string]
        lemma_string = ' '.join(lemma_list)
        with self.ix_lemma.searcher() as searcher:
            query = None
            if self.lang == "ja":
                query = QueryParser("content",
                                self.ix_lemma.schema).parse('%s' %
                                                            lemma_string)
            else:
                query = QueryParser("content",
                                self.ix_lemma.schema).parse('"%s"' %
                                                            lemma_string)
            results = searcher.search(query, limit=None)
            raw_res = [self.utterances[int(res['path'])] for res in results]
        if not sent_level:
            return raw_res
        else:
            # finding the sentence that contains the query
            new_res = []
            for utt in raw_res:
                for sent_num, sent in enumerate(utt.spacy.sents):
                    # creating the lemma version of sentence
                    lemma_text = ' '.join([x.lemma_ for x in sent])
                    if lemma_string in lemma_text:
                        new_res.append(Utterance(sent.text, utt.id, sent_num, lang=self.lang))
            return new_res

    def pd_query(self, panda):
        '''Returns a list of Utterances corresponding to the input
        (list of DataFrame)'''
        if isinstance(panda, pd.DataFrame):
            indices = list(panda.index)
        else:
            indices = panda  # assuming panda is a list
        return [self.utterances[index] for index in indices]

# ------------------------------------------------------------------------------
# The helper functions in the module
# ------------------------------------------------------------------------------


def getFrames(framenet, index):
    # check if any frame exists
    if framenet is None:
        return None
    djson = json.loads(framenet[index])
    # check if the particular frame exist
    if djson[str(index)] is None:
        return None
    frames = {}
    for sent in djson[str(index)]['sentences']:
        for frame in sent['frames']:
            frame_name = frame['target']['name']
            frames[frame_name] = {}
            frames[frame_name]['text'] = frame['target']['text']
            frames[frame_name]['annotations'] = []
            # finding the frameElements
            # check for old version
            if 'annotationSets' in frame:
                elements = frame['annotationSets'][0]['frameElements']
            else:
                elements = frame['frameElements']
            for e in elements:
                frames[frame_name]['annotations'].append((e['name'], e['text']))
    return frames


def getPropBank(deepsrl, index):
    # check if any frame exists
    if deepsrl is None:
        return None
    djson = json.loads(deepsrl[index])
    # check if the particular frame exist
    if djson[str(index)] is None:
        return None
    return djson[str(index)]
