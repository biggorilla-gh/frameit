import unittest

from frameit import TextProcessing
from frameit.models.lambda_rule_model import LambdaRuleModel


def mylambda_v1(spacy_doc):
    # this is just a simple free-form function that
    # returns the word that follows "from"
    # the results should be a list of extracted tokens
    results = []
    for i, t in enumerate(spacy_doc):
        if t.text == 'from':
            results.append(spacy_doc[i + 1])
    return results


def mylambda_v2(spacy_doc):
    return [spacy_doc[0]]


class LambdaRuleModelTest(unittest.TestCase):

    def test_predict(self):
        # building a rule based on the function
        model = LambdaRuleModel('test', mylambda_v1)
        tp = TextProcessing()
        doc = tp.nlp['en']('I am coming from hotel.')
        pred = model.predict([doc[4]])
        self.assertEqual(pred[0][1], 1.0)
        pred = model.predict([doc[3]])
        self.assertEqual(pred[0][1], 0.0)

    def test_get_state(self):
        final_str = 'def mylambda_v2(spacy_doc):\n    return [spacy_doc[0]]\n'
        model = LambdaRuleModel('test', mylambda_v2)
        self.assertEqual(model.get_state(), {'name': 'test_lambda_attr',
                                             'lang': 'en',
                                             'func_name': 'mylambda_v2',
                                             'model_text': final_str})

    def test_set_state(self):
        model = LambdaRuleModel()
        final_str = 'def mylambda_v2(spacy_doc):\n    return [spacy_doc[0]]\n'
        model.set_state({'name': 'test_lambda_attr',
                         'func_name': 'mylambda_v2',
                         'model_text': final_str})
        tp = TextProcessing()
        doc = tp.nlp['en']('I am coming from hotel.')
        for i in range(len(doc)):
            pred = model.predict([doc[i]])
            self.assertEqual(pred[0][1], 1.0 if i == 0 else 0.0)
