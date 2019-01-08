from frameit.utterance import Utterance
from frameit.frame import Frame
from spacy import displacy
import logging
#from frameit import logger

# class FrameLabel(object):
    def __init__(self, frame, sentence, confidence):
        self.frame = frame
        self.sentence = sentence
        self.confidence = confidence
        self.attrs = {}
        for attr in self.frame.attributes:
            self.attrs[attr] = []

    def add_attr(self, attr, token, conf):
        self.attrs[attr].append((token, conf))

    def get_state(self):
        state = {'frame': self.frame.name}
        state['slots'] = {}
        for attr, tokens in self.attrs.items():
            if not attr.name in state['slots'].keys():
                state['slots'][attr.name] = []
            state['slots'][attr.name] += \
                [{'token': token.text, 'index': token.idx, 'confidence': conf} for (token, conf) in tokens]
        return state

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = "Sentence: " + self.sentence.text + "\n"
        s += "Frame: " + self.frame.name + "\n"
        s += "Confidence: " + str(self.confidence) + "\n"
        if len(self.frame.attributes) > 0:
            s += "Attributes: " + "\n"
        for attr, tokens in self.attrs.items():
            s += ("\t" + str(attr.name) + "=>" +
                  ",".join([token.text + ' (' + str(conf) + ')'
                            for (token, conf) in tokens]) + "\n")
        return s

    def __eq__(self, other):
        if self.frame.name != other.frame.name:
            return False
        for attr, tokens in self.attrs.items():
            other_tokens = other.attrs.get(attr, None)
            if not other_tokens:
                return False
            if len(tokens) != len(other_tokens):
                return False
            for i in range(len(tokens)):
                if tokens[i][0].text != other_tokens[i][0].text or \
                        tokens[i][0].idx != other_tokens[i][0].idx:
                    return False
        return True


class SRL(object):
    def __init__(self):
        self.frames = []

    def addFrame(self, frame):
        self.frames.append(frame)

    def loadFrame(self, filename):
        frame = Frame.load(filename)
        self.addFrame(frame)

    def parse(self, sent):
        if isinstance(sent, str):
            sent = Utterance(sent, -1)
        elif isinstance(sent, Utterance):
            pass
        else:
            print("Argument to parse must be a string or Sentence object")
            return None
        labels = []
        # Parse for each frame
        for frame in self.frames:
            pred = frame.model.predict([sent])
            if pred[0][1] > 0.5:
                flabel = FrameLabel(frame, sent, pred[0][1])
                for attr in frame.attributes:
                    self._parse_attr(attr, sent, flabel)
                labels.append(flabel)
#        logging.debug('Found labels {0}'.format(labels))
        return labels

    def analyze(self, sent):
        sent = Utterance(sent, -1)
        labels = self.parse(sent)
        return {'text': sent.text,
                'frames': [label.get_state() for label in labels],
                'dep': displacy.render(sent.spacy, style='dep', options={'offset_x': 5})}

    def _parse_attr(self, attr, sent, flabel):
        const = attr.constraints
        # variables for finding the max
        best_cand = None
        best_score = -1
        for token in sent.spacy:
            candidate = None
            if const and "POS" in const:
                if token.pos_ in const['POS']:
                    candidate = token
            else:
                candidate = token
            if candidate:
                pred = attr.model.predict([token])
                if pred[0][1] > 0.5:
                    if attr.unique:
                        if pred[0][1] > best_score:
                            best_score = pred[0][1]
                            best_cand = candidate
                    else:
                        flabel.add_attr(attr, candidate, pred[0][1])
        # assign the best candidate if it exist (and if the attribute is unique)
        if attr.unique and best_cand is not None:
            flabel.add_attr(attr, best_cand, best_score)
        return

    # ------------------------------------------
    def serialize(self, inputfile):
        pass

    @staticmethod
    def load_srl(inputfile):
        return None
