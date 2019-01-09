import xml.etree.ElementTree as ET
from frameit import SRL, FrameLabel, Frame, Utterance


class EvalToken:
    def __init__(self, text, idx):
        self.text = text
        self.idx = idx

def evalFrame(frame_filename, gold_filename, verbose_frame=False, verbose_attribute=False, limit=5, skip=None, fuzzy=False, generous=False):
    '''
    frame_filename: file where trained frame is stored

    gold_filename: xml file of examples correctly labeled for a positive or negative match of the frame, as well as annotated for attributes

    verbose_frame: boolean, if True script prints debug information about Frame for each sentence. Default False

    verbose_attribte: boolean, if True script prints debug information about attribute matches for each sentence. Default False
    limit: int, sets cap on number of messages to print in verbose mode. Default 5.

    skip: specify names of attributes to ignore in evaluation. Default None

    fuzzy: bool, if True, attributes extracted which are substrings of the gold-data attribute are ignored when calculating accuracy (normally they would be considered incorrect answers). Default False.

    generous: bool, only used if fuzzy is also True. If True, fuzzy answers are instead counted as correct answers. Default False.

    '''
    frame = Frame.load(frame_filename)

    srl = SRL()
    srl.addFrame(frame)

    tree = ET.parse(gold_filename)
    root = tree.getroot()

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    attr_mismatches = 0

    attr_result_dict = {}

    individual_attr_true_pos_count = 0
    individual_attr_true_neg_count = 0
    individual_attr_false_pos_count = 0
    individual_attr_false_neg_count = 0

    print_count = 0
    for sent in root:
        # print('\niterate')
        text = ''.join(sent.itertext())
        srl_labels = srl.parse(text)

        label = None
        if sent.tag == 'negative':
            if srl_labels:
                false_positives += 1
                if verbose_frame and print_count < limit:
                    print('False positive: ', text)
                    print_count += 1
            else:
                true_negatives += 1
            continue

        label = FrameLabel(frame, Utterance(text, 1), 1.0)
        if sent.text == None:
            continue
        offset = len(sent.text)  # character offset in the sentence
        for a in sent:
            if frame.getAttribute(a.tag) is None:
                continue
            label.add_attr(frame.getAttribute(a.tag), EvalToken(a.text, offset), 1)
            offset += len(a.text)
            if a.tail:
                offset += len(a.tail)
        if not srl_labels:
            false_negatives += 1
            if verbose_frame and print_count < limit:
                print('False negative', text)
                print_count += 1
            continue
        srl_label = srl_labels[0]

        extracted_attributes = {}
        gold_attributes = {}
        for key in label.attrs.keys():
            if skip is not None:
                if key.name in skip:
                    continue
            if key.name not in attr_result_dict.keys():
                #true positive, false positive, missed positive
                attr_result_dict[key.name] = [0,0,0]
            if key.name not in gold_attributes.keys():
                gold_attributes[key.name] = set()
            if key.name not in extracted_attributes.keys():
                extracted_attributes[key.name] = set()
            for token in label.attrs[key]:
                gold_attributes[key.name].add(token[0].text)

        for srl_key in srl_label.attrs.keys():
            if skip is not None:
                if srl_key.name in skip:
                    continue
            if srl_key.name not in attr_result_dict.keys():
                attr_result_dict[srl_key.name] = [0,0,0]
            if srl_key.name not in gold_attributes.keys():
                gold_attributes[srl_key.name] = set()
            if srl_key.name not in extracted_attributes.keys():
                extracted_attributes[srl_key.name] = set()
            for item in srl_label.attrs[srl_key]:
                if item[0].text not in extracted_attributes[srl_key.name]:
                    extracted_attributes[srl_key.name].add(item[0].text)

        same = True
        for key in extracted_attributes.keys():
            if extracted_attributes[key] != gold_attributes[key]:
                same = False
                break
        if same:
            true_positives += 1
            for key in extracted_attributes.keys():
                attr_result_dict[key][0] += len(extracted_attributes[key])
                individual_attr_true_pos_count += len(extracted_attributes[key])
        else:
            attr_mismatches += 1
            for key2 in gold_attributes.keys():
                for gold_token in gold_attributes[key2]:
                    if gold_token in extracted_attributes[key2]:
                        individual_attr_true_pos_count += 1
                        attr_result_dict[key2][0] += 1
                    else:
                        if fuzzy:
                            ok = False
                            for substring in extracted_attributes[key2]:
                                if str(substring) in str(gold_token):
                                    ok = True
                                    break
                            if ok:
                                if generous:
                                    individual_attr_true_pos_count += 1
                                    attr_result_dict[key2][0] += 1
                                if verbose_attribute and print_count < limit:
                                    print('Excusing fuzzy missed attribute: ')
                                    print('Sentence: ', text)
                                    print('Got {0}, wanted {1}\n'.format(extracted_attributes[key2], gold_token))
                                continue
                        individual_attr_false_neg_count += 1
                        attr_result_dict[key2][2] += 1
                        if verbose_attribute and print_count < limit:
                            print('Missed attribute in ', key2)
                            print('Sentence: ', text)
                            print('Got {0}, wanted {1}\n'.format(extracted_attributes[key2], gold_token))
                            print_count += 1
            for key3 in extracted_attributes.keys():
                for extracted_token in extracted_attributes[key3]:
                    if extracted_token not in gold_attributes[key3]:
                        if fuzzy:
                            ok = False
                            for string in gold_attributes[key2]:
                                if str(extracted_token) in str(string):
                                    ok = True
                                    break
                            if ok:
                                if generous:
                                    individual_attr_true_pos_count += 1
                                    attr_result_dict[key3][0] += 1
                                if verbose_attribute and print_count < limit:
                                    print('Excusing fuzzy false positive: ')
                                    print('Sentence: ', text)
                                    print('Got {0}, wanted {1}\n'.format(extracted_token, gold_attributes[key2]))
                                continue
                        individual_attr_false_pos_count += 1
                        attr_result_dict[key3][1] += 1
                        if verbose_attribute and print_count < limit:
                            print('Current attribute is: ', key3)
                            print('False positive attribute')
                            print('Sentence: ', text)
                            print('Got {0}, wanted {1}\n'.format(extracted_token, gold_attributes[key3]))
                            print_count += 1

    print('true_positives = ', true_positives)
    print('true_negatives = ', true_negatives)
    print('false_positives = ', false_positives)
    print('false_negatives = ', false_negatives)
    print('mismatches = ', attr_mismatches)
    print('Raw true attributes = ', individual_attr_true_pos_count)
    print('Raw false positive attributes = ', individual_attr_false_pos_count)
    print('Raw missed attributes = ', individual_attr_false_neg_count)
    raw_attr_precision = individual_attr_true_pos_count / (individual_attr_true_pos_count + individual_attr_false_pos_count + 1e-20)
    raw_attr_recall = individual_attr_true_pos_count / (individual_attr_true_pos_count + individual_attr_false_neg_count +1e-20)
    raw_attr_f1 = (raw_attr_precision * 2 * raw_attr_recall)/(raw_attr_precision + raw_attr_recall + 1e-20)
    attr_precision = (true_positives) / (true_positives + attr_mismatches + false_positives + 1e-20)
    attr_recall = true_positives / (true_positives +  false_negatives + 1e-20)
    attr_f1 = (2 * attr_precision * attr_recall)/(attr_precision + attr_recall + 1e-20)
    frame_precision = (true_positives + attr_mismatches) / (true_positives + attr_mismatches + false_positives + 1e-20)
    frame_recall = (true_positives + attr_mismatches) / (true_positives + attr_mismatches + false_negatives + 1e-20)
    frame_f1 = (2 * frame_precision * frame_recall) / (frame_precision + frame_recall+1e-20)
    print('Frame detection precision = ', frame_precision)
    print('Frame detection recall = ', frame_recall)
    print('Frame F1 score = ', frame_f1)


    print('True Attribute detection precision = ', attr_precision)
    print('True Attribute detection recall = ', attr_recall)
    print('True Attribute F1 score = ', attr_f1)
    print('Raw Attribute precision = ', raw_attr_precision)
    print('Raw Attribute recall = ', raw_attr_recall)
    print('Raw attribute f1 = ', raw_attr_f1)

    print('Now calculating attribute detection only for successful frame identification cases')
    successful_attr_precision = true_positives / (true_positives + attr_mismatches + 1e-20)
    print('Successful frame attribute precision = ', successful_attr_precision)
    print('Attribute-specific stats:')
    for key in attr_result_dict.keys():
        print('{0}:\n\t correct-positive: {1}\n\t false-positive: {2}\n\t missed-positive: {3}'.format(key, attr_result_dict[key][0],attr_result_dict[key][1],attr_result_dict[key][2]))
        single_att_precision = attr_result_dict[key][0] / (attr_result_dict[key][1] + attr_result_dict[key][0] + 1e-20)
        single_att_recall = attr_result_dict[key][0] / (attr_result_dict[key][0] + attr_result_dict[key][2] + 1e-20)
        single_att_f1 = (2 * single_att_precision * single_att_recall ) / (single_att_recall + single_att_precision + 1e-20)
        print('Precision: {0}, Recall: {1}, F1: {2}'.format(single_att_precision, single_att_recall, single_att_f1))
