import spacy
from spacy.lang.en.stop_words import STOP_WORDS
#STOP_WORDS need to be language specific
from frameit.text_processing import TextProcessing


class Utterance(object):

    # nlp = None
    class_nlp = TextProcessing().nlp
    # marking stop words
    # nlp.vocab.add_flag(lambda s: s.lower() in STOP_WORDS, spacy.attrs.IS_STOP)
    # counter for fake utterances
    fake_id = 0

    def __init__(self, text, _id, sent_num=-1, lang='en'):
        self.lang = lang
        self.text = self.clean(str(text))
        self._spacy = None
        self.extractions = set()
        if _id is None:
            Utterance.fake_id -= 1
            self.id = Utterance.fake_id
        else:
            self.id = _id
        self.sent_num = sent_num
        self.frames = None
        self.nlp = Utterance.class_nlp[lang]
        # if type(Utterance.nlp) is dict:
            # Utterance.nlp = Utterance.nlp[self.lang]
            # Utterance.nlp.vocab.add_flag(lambda s: s.lower() in STOP_WORDS, spacy.attrs.IS_STOP)
        # if Utterance.nlp == None:
            # Utterance.nlp = TextProcessing(lang=lang).nlp[lang]

    def clean(self, text):
        single_line = text.replace('\n', '.').replace('\r', '.')
        return ' '.join(single_line.split())

    def __hash__(self):
        # this is required to make results reproducible
        return hash((self.id, self.sent_num))

    def __eq__(self, other):
        if not isinstance(other, Utterance):
            return False
        return (self.id == other.id) and (self.sent_num == other.sent_num)

    @property
    def spacy(self):
        if self._spacy is None:
            self._spacy = self.nlp(str(self.text))
        return self._spacy
