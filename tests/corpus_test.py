import unittest
import pandas as pd

from frameit import Corpus


class CorpusTest(unittest.TestCase):

    def test_corpus_from_pandas(self):
        dat = pd.DataFrame({'text': ['This is some text.',
                                     'This is more text.',
                                     'And this makes a corpus.']})
        corpus = Corpus(dat, build_index=True)
        self.assertEqual(len(corpus.utterances), 3)

    def test_corpus_from_csv(self):
        corpus = Corpus('./resources/cf_report_filtered_trustyou.csv',
                        limit=10, build_index=True)
        self.assertEqual(len(corpus.utterances), 10)
        self.assertEqual(corpus.utterances[0].text,
                         'We are doing well in our travels and we will ' +
                         'arrive today hopefully by')
