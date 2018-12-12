import os
import json

color_names = ['White', 'LightPink', 'PeachPuff', 'LightGreen', 'LightBlue' ]

import csv

def get_value(slots, attr):
    spans = slots.get(attr, None)
    return " ".join([span["token"] for span in spans])


class Answerer:
    def __init__(self, srl):
        self.hotel_id = "/t/cbr"
        self.load_kg("hotel_kg.tsv")
        self.srl = srl
        pass

    def load_kg(self, filename):
        self.kg = []
        with open(filename, "rt") as tsv:
            for line in csv.reader(tsv, delimiter='\t'):
                self.kg.append(line)

    def lookup(self, facility):
        pred_id = None
        for fact in self.kg:
            if facility.lower() in fact[2].lower():
                pred_id = fact[0]
                break
        for fact in self.kg:
            if fact[0] == self.hotel_id and fact[1] == pred_id:
                return fact[2]
        return 'No'
    
    def answer(self, question):
        resp = self.srl.analyze(question)
        frames = resp.get('frames', None)
        if not frames:
            "<p>%s</p><p>I don't know how to answer this.</p><hr>" % question
        annotated_text = ""
        for frame_state in frames:
            name = frame_state['frame']
            slots = frame_state['slots']
            if name == "Hotel Facility":
                facility = get_value(slots, "Facility")
                return "<p>%s</p><p>%s</p><hr>" % (question, self.lookup(facility))
        return "<p>%s</p><p>I don't know how to answer this.</p><hr>" % question
