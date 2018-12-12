from flask import Flask, json, request, Response
import sys, traceback, logging
from frameit import logger

# logname = 'frameit/api/logs/logs.txt'
# logging.basicConfig(filename=logname,
#                             filemode='a',
#                             format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                             datefmt='%H:%M:%S',
#                             level=logging.DEBUG)
logging.debug('Session start')

def create_app(api):
    app = Flask(__name__)

    @app.route('/ping', methods=['GET'])
    def ping():
        return Response('pong', status=200)

    @app.route('/', methods=['OPTIONS'])
    def options():
        resp = Response('OK', status=200)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = '*'
        print(resp.headers)
        return resp

    @app.route('/', methods=['GET', 'POST'])
    def root():
        if request.headers.get('Content-Type', 'text/plain') != 'application/json':
            return Response('Error', status=200)
        api_request = request.json
        print("REQUEST: ", json.dumps(api_request, indent=2))
        # logging.debug('hi')
        endpoint = api_request.get('endpoint', None)
        payload = api_request.get('payload', None)
        api_response = {'endpoint': endpoint}
        logging.debug(payload)
        func = getattr(api, endpoint, None)
        if func:
            try:
                api_response['payload'] = func(**payload)
                api_response['success'] = True
            except Exception as e:
                api_response['error'] = str(e)
                traceback.print_exc(file=sys.stdout)
        else:
            api_response['error'] =  'Unknown endpoint: %s' % endpoint
        print("RESPONSE = ", json.dumps(api_response, indent=2))
        # logging.debug(api_response['payload'])
        # logging.debug(func)
        resp = Response(json.dumps(api_response), status=200, mimetype='application/json')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = '*'
        return resp

    return app
