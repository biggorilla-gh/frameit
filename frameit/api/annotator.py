import os
import json

color_names = ['White', 'LightPink', 'PeachPuff', 'LightGreen', 'LightBlue' ]

def annotate_frame(text, frame, slots):
    html = ''
    if not slots:
        return html
    n = len(text)
    char_color = [0] * n
    char_confidence = [0.0] * n
    attr_index = 1
    attr_names = []
    num_highligthed_tokens = 0
    for attr, spans in slots.items():
        for span in spans:
            token_start = span["index"]
            token_len = len(span["token"])
            token_confidence = span["confidence"]
            for i in range(token_len):
                char_index = token_start + i
                if token_confidence > char_confidence[char_index]:
                    char_color[char_index] = attr_index
                    char_confidence[char_index] = token_confidence
                    num_highligthed_tokens += 1
        attr_names.append(attr)
        attr_index += 1
    if num_highligthed_tokens == 0:
        return html
    
    prev_color = 0
    html += '<p>'
    for i in range(n):
        color = char_color[i]
        if color != prev_color:
            if prev_color:
                html += '</span>'
            if color:
                html += '<span style="background-color:%s;">' % color_names[color]
        prev_color = color
        html += text[i]
    if prev_color:
        html += '</span>'
    html += '</p><p>'
    html += '<p><b>Frame Name:</b> %s</p>' % frame
    html += '<p><b>Frame Slots:</b> '
    for i in range(len(attr_names)):
        html += '<span style="background-color:%s;">%s</span> ' % (color_names[i+1], attr_names[i])
    return html
        


class Annotator:
    def __init__(self, srl):
        self.srl = srl
        pass
    
    def annotate(self, sent):
        resp = self.srl.analyze(sent)
        print("analyze response = ", json.dumps(resp, indent=2))
        frames = resp.get('frames', None)
        if not frames:
            return "<p>%s</p><p><b>No frames detected</b></p><hr>" % sent
        annotated_text = ""
        for frame_state in frames:
            name = frame_state['frame']
            slots = frame_state['slots']
            annotated_text += annotate_frame(sent, name, slots)
        annotated_text += resp.get('dep', '')
        annotated_text += '</p><hr>'
        return annotated_text
