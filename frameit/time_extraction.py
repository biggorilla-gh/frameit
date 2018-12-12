import random
import pandas as pd
import spacy
import re
from spacy.tokens import Doc, Token, Span
from spacy.lexeme import Lexeme

parent_constraint = [{"pos":["adp"], "dep":["prep"]}]
cand_constraint = [{"pos":["noun", "num"], "dep":['pobj','nummod', 'num', 'number']}]


non_numerical_dict = ["noon", "evening", "morning", "midday", "night"]
numerical_tags = ["num", "number", "nummod"]
time_meridiums = ["am", "pm"]
puncts = ["!", "?", ".", ","]
regex_patterns = ['half past ([^\s]+)(\s(am|pm))?(am|pm)?', 'half to ([^\s]+)(\s(am|pm))?(am|pm)?',
                  'quarter to ([^\s]+)(\s(am|pm))?(am|pm)?', 'quarter past ([^\s]+)(\s(am|pm))?(am|pm)?',
                  '\d+(\s)?(minutes|min|hrs|hours|hour)', '\d+(:?)(\d+)?(\s(am|pm))?(am|pm)?', ]

def check_constraints(token, obj):
    # if constraint obj is empty, that means there are no constraints
    if not obj:
        return True
    if "lemma" in obj and token.lemma_.lower() not in obj["lemma"]:
        return False
    if "pos" in obj and token.pos_.lower() not in obj["pos"]:
        return False
    if "dep" in obj and token.dep_.lower() not in obj["dep"]:
        return False
    return True

def get_doc(token, doc, index=False):
    for tok in doc:
        if tok.text == token.text:
            if index:
                return tok.i
            return tok

def child_is_num(child, child_index, doc):
    '''
    candidate might not have a "NUM" postag, 
    and must be checked using dictionaries and additional particles
    '''
    if child_index+1 != len(doc):
        if doc[child_index+1].text.lower() == ("am" or "pm"):
            span = doc[child_index:child_index+2]
            return (child, span, doc)

    found_chunk = None
    if child.text.lower() in non_numerical_dict:
        return (child, found_chunk, doc)
    for chunk in doc.noun_chunks:
        if child in chunk:
            found_chunk = chunk
            break
    return (child, found_chunk, doc)

def clean_result(result):
    '''
    Return either the token extracted, or if noun chunk exists, 
    first clean of punctuation and return span
    '''
    final_candidate = None
    if result[1] == None:
        return result[0]
    else:
        for token in result[1]:
            if token.pos_.lower() == "punct":
                return result[1][:token.i]
        return result[1]

def extract_substring(doc):
    '''
    Return extracted substring if one of regex patterns matched
    '''
    for reg in regex_patterns:
        r = re.compile(reg)
        found = [[m.start(),m.end()] for m in r.finditer(doc.text)]
        if found:
            spans = []
            for match in found:
                span_f = doc.char_span(match[0], match[1])
                if span_f:
                    spans.append(span_f)
            return spans
    return []

def merge_results(spacy_candidates, regx_parsings):
    '''
    Return a unified result using both regex and spacy dependency tree.
    We take the regex answer if a spacy candidate is a substring of it (regex might extract more),
    otherwise we take the spacy candidate
    '''
    final_parsings = []
    for sp_cand in spacy_candidates:
        remove_cand = False
        for regx in regx_parsings:
            if sp_cand.text in regx.text:
                if regx.text[-1] in puncts:
                    continue
                remove_cand =True
                final_parsings.append(regx)
        if remove_cand:
            continue
        else:
            final_parsings.append(sp_cand)
    return final_parsings

def resulting_tokens(final_parsings):
    '''
    Convert the resulting list of spans to a list of tokens
    '''
    print("parsings not caught by spacy: ")
    for res in final_parsings:
        print(res)
        print()
    result = []
    for cand in final_parsings:
        if isinstance(cand, Token) or isinstance(cand, Lexeme):
            result.append(cand)
        else:
            tokens = []
            for token in cand:
                tokens.append(token)
            result.extend(tokens)
    
    return result

def extract_time_candidates(doc, parent_constraints,
                           candidate_constraints):
    '''
    Time parser function that uses the spacy dependency parse tree, along with pos tags and dictionaries
    '''
    candidates = []
    for token in doc:
         for obj in parent_constraints:
            if check_constraints(token, obj):
                for child in token.children:
                     for cand in candidate_constraints:
                         if check_constraints(child, cand):
                            child_index = get_doc(child, doc, True)
                            if child.n_lefts != 0:
                                for l in child.lefts:
                                    if check_constraints(l, cand):
                                        for chunk in doc.noun_chunks:
                                            if l in chunk:
                                                candidates.append((l, chunk, doc))
                                                break
                                    if (child.pos_.lower() in numerical_tags) or (child.text.lower() in non_numerical_dict):
                                        candidates.append(child_is_num(child, child_index, doc))
                                        break

                                continue
                            else:
                                if (child.pos_.lower() in numerical_tags) or (child.text.lower() in non_numerical_dict) or \
                                (any(meridium in child.text.lower() for meridium in time_meridiums)):
                                    candidates.append(child_is_num(child, child_index, doc))

    return candidates

def time_parser(doc):
    '''
    Keyword arguments:
        doc -- An object of utterance.spacy type
    Return:
        final_parsings -- A list of matching 'Span' type or an empty list
    '''
    print("utterance ", doc.text)
    spacy_result = []
    res = extract_time_candidates(doc,parent_constraint, cand_constraint)
    if res:
        for r in res:
            spacy_result.append(clean_result(r))
    regx_result = extract_substring(doc)
    if regx_result and spacy_result:
        final_parsings = merge_results(spacy_result, regx_result)
        return resulting_tokens(final_parsings)
    else:
        return resulting_tokens(spacy_result) if spacy_result else resulting_tokens(regx_result)

'''

Uncomment to run file independently 

#Import text processing to make main work
if __name__ == "__main__":
    nlp = spacy.load("en")
    df = pd.read_csv("../notebooks/Building and Evaluating TrustYou Frames/frame_training_data/arrival_frame_training_002.csv")
    sample = df["text"].tolist()[:10]
    utterances = [Utterance(utter, i) for i, utter in enumerate(sample)]


    #Maybe chunk should be temp var, and break and onlythen add to candidates, so that you ge the token even without tokens
    sample = ["should be there in the evening", "I will be getting to the hotel around noon", "I will be getting to the hotel around four", "I will be getting to the hotel at half past four",
    "My flight arrives at 6:15am", "I will be arriving at 3pm!", "Hi! Thank you! We expect to arrive at 2:30 this afternoon...Best regards, Beth ..&gt;",
    "Delta flight #DL344 .Arrive in Cabo at 1:12pm.J[EMAIL]", "About 1pm I will arrive in Spokane. Even early parking would be great!",
    "Hello, my flight arrives at 11:10am.", "Ok thank you, so we don't need to meet you for the key, we ll arrive in about 2 hour",
    "Ok thank you, so we don't need to meet you for the key, we ll arrive in 2 hour", "Hi! I am arriving at DEN at 10, should be at the hotel by 11:15am. Thanks!",
    "My flight arrives at 6:15am", "We are now planning on arriving at approximately 8:00 pm on Friday the 6th of OCT"]
    utterances = [Utterance(utter, i) for i, utter in enumerate(sample)]
    utterances = [Utterance("I will be there 20 minutes past 2", 0).spacy]
    
    for utterance in utterances:
        results = time_parser(utterance)
        print(results)
        print()
'''

