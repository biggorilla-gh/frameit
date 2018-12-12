from collections import Counter


def get_boundry_examples(frame, corpus, k=20):
    res_set = Counter()
    utter_list = list(corpus)
    pred = frame.model.predict(utter_list)
    for i, msg in zip(xrange(pred.shape[0]), utter_list):
        res_set[msg] = abs(pred[i][1] - .5)
    return [key for key, val in res_set.most_common()[-k:]]


def get_confidence_examples(frame, corpus, k=20):
    res_set = Counter()
    utter_list = list(corpus)
    pred = frame.model.predict(utter_list)
    for i, msg in zip(xrange(pred.shape[0]), utter_list):
        res_set[msg] = pred[i][1]
    return [key for key, val in res_set.most_common()[:k]]


def get_neg_confidence_examples(frame, corpus, k=20):
    res_set = Counter()
    utter_list = list(corpus)
    pred = frame.model.predict(utter_list)
    for i, msg in zip(xrange(pred.shape[0]), utter_list):
        res_set[msg] = 1 - pred[i][1]
    return [key for key, val in res_set.most_common()[:k]]


def get_similar_examples(examples, corpus, subset, k=10):
    ret_list = []
    for e in examples:
        ret_list.append(corpus.find_nearest_n(e.text, k, subset))
    return [y for x in ret_list for y in x[0]]


def update_frame_examples(labels, bound_examples, frame,
                          neg_set=set(), debug_set=set()):
    for label, e in zip(labels, bound_examples):
        if label == 1:
            print "Adding ...", e.text[:20]
            frame.utterances.add(e)
        elif label == 0:
            if e in frame.utterances:
                print "Removing bad datapoint...", e.text[:20]
                frame.utterances.remove(e)
                debug_set.add(e)
            neg_set.add(e)
    return frame, neg_set, debug_set


def collect_labels(examples):
    labels = []
    for e in examples:
        print e.text
        i = None
        while(i != 'f' and i != 't'):
            i = raw_input("Please enter t if true and f if false" + '\n')
            if i == 'f':
                labels.append(0)
            elif i == 't':
                labels.append(1)
            else:
                print "Entry not recognized. Only t and f are recognized", '\n'
    return labels
