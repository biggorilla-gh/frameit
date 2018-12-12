import unittest

from frameit.models.rule_model import RuleModel


class RuleModelTest(unittest.TestCase):

    def test_extract(self):
        model = RuleModel('test')
        model.add_rule('around * today')
        model.add_pattern('\d{1,2}')
        doc = model.nlp('I will be arriving around 3 today')
        extracted = model.extract(doc)
        self.assertEqual(len(extracted), 1)
        pred = model.predict([doc[5]])
        self.assertEqual(pred[0][1], 1.0)
        
    def test_predict(self):
        model = RuleModel('test')
        model.add_rule('around * today')
        model.add_pattern('\d{1,2}')
        doc = model.nlp('I will be arriving around 3 today')
        pred = model.predict([doc[5]])
        self.assertEqual(pred[0][1], 1.0)

    def test_predict_multiple_tokens(self):
        model = RuleModel('test')
        model.add_rule('around * * today')
        model.add_pattern('\d{1,2} [ap]m')
        doc = model.nlp('I will be arriving around 3 pm today')
        for i in range(len(doc)):
            pred = model.predict([doc[i]])
            self.assertEqual(pred[0][1], 1.0 if i in [5, 6] else 0.0)

    def test_get_state(self):
        model = RuleModel('test')
        model.add_rule('around * * today')
        model.add_pattern('\d{1,2} [ap]m')
        self.assertEqual(model.get_state(), {'name': 'test_rule_attr',
                                             'lang': 'en',
                                             'rules': ['around * * today'],
                                             'patterns': ['\d{1,2} [ap]m']})
                         
    def test_set_state(self):
        model = RuleModel()
        model.set_state({'name': 'test_rule_attr',
                         'rules': ['around * * today'],
                         'patterns': ['\d{1,2} [ap]m']})
        doc = model.nlp('I will be arriving around 3 pm today')
        for i in range(len(doc)):
            pred = model.predict([doc[i]])
            self.assertEqual(pred[0][1], 1.0 if i in [5, 6] else 0.0)
        
