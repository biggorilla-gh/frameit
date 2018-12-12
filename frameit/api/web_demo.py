import requests
import os
from flask import Flask,render_template,request,url_for
import json

app = Flask(__name__)

url = os.environ.get("API_SERVER", "http://localhost:5555/")

color_names = ['White', 'LightPink', 'NavajoWhite' ,'PeachPuff', 'LightGreen', 'LightBlue' ]

def annotate(text, frame, slots):
    html = ''
    n = len(text)
    char_color = [0] * n
    attr_index = 1
    attr_names = []
    for attr, spans in slots.items():
        for span in spans:
            token_start = span["index"]
            token_len = len(span["token"])
            for i in range(token_len):
                char_color[token_start + i] = attr_index
        attr_names.append(attr)
        attr_index += 1
    prev_color = 0
    for i in range(n):
        color = char_color[i]
        if color != prev_color:
            if prev_color:
                html += '</span>'
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
        
        

def html_form(text, annotated_text="", debug_msg=""):
    return '''
<!doctype html>
<html>
  <head>
         <title>SRL API Server Demo</title>
  </head>
  <body>
         <table>
                <tr>
                  <td>Utterance:</td>
                  <td><textarea form="submit-form" cols="80" rows="3" style="font-size:100%%;"
                                name="text" id="text">%s
                  </textarea></td>
                </tr>
         </table>

         <p style="font-size:150%%;">%s</p>
         <form id="submit-form" action="query" method="post"
                         enc-type="application/x-www-form-urlencoded">
                <input type="checkbox" name="debug" value="1" checked="1"> Debug<br>
                <input type="submit" value="Submit">
         </form>
         <pre>
                %s
         </pre> 
  </body>
</html>
        ''' % (text, annotated_text, debug_msg)


def create_analyze_request(text):
    api_request = {"endpoint": "analyze",
                   "payload": {"sent": text}}
    return api_request

def jsonstr(data):
    return json.dumps(data, sort_keys=True, indent=2)

def call_api_server(url, request):
    headers = {'Content-Type': 'application/json'}
    print("\n\nREQUEST = %s" % jsonstr(request))
    resp = requests.post(url, data=json.dumps(request), headers=headers)
    response = json.loads(resp.text)
    print("RESPONSE = %s" % jsonstr(response))
    return response


@app.route('/ping')
def ping():
    print("PING")
    return 'pong'


@app.route('/js')
def js():
    return '''
<!DOCTYPE html>
<html>
<body>

<h1>SRL Demo</h1>

<button type="button" onclick="loadDoc()">Request data</button>

<pre id="demo">Response comes here</pre>
 
<script>
function loadDoc() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    document.getElementById("demo").innerHTML = "Here status = "+this.status
    if (this.status == 200) {
      document.getElementById("demo").innerHTML = "the response is: "+this.responseText;
    }
  };
  xhttp.open("POST", "http://localhost:5555", true);
  xhttp.setRequestHeader("Content-type", "application/json");
  xhttp.send('{"endpoint": "analyze", "payload": {"sent": "How do I get to the hotel from the airport"}}');
}
</script>

</body>
</html>
'''

@app.route('/')
def root():
    text = "How do I get to the hotel from the airport?"
    api_request = create_analyze_request(text)
    
    json_request = jsonstr(api_request)
    return html_form(text)

@app.route('/query', methods=['POST', 'GET'])
def query():
    if request.method == 'POST':
        text = request.form['text'].strip()
        debug = request.form.get('debug', None)
        analyze_request = create_analyze_request(text)
        analyze_reply = call_api_server(url, analyze_request)
        frame = None
        summary = "No frame detected"
        frames = analyze_reply["payload"].get("frames", None)
        slots = None
        annotated_text = text
        if frames:
            first_frame = frames[0]
            frame = first_frame.get("frame", None)
            summary = frame
            slots = first_frame.get("slots", {})
            annotated_text = annotate(text, frame, slots)
        debug_msg = ""
        if debug:
            debug_msg += "\n"+jsonstr(analyze_reply).replace('"', '') +"\n"
        
        return html_form(text, annotated_text, debug_msg)
    else:
        root()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
