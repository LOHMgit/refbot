import os
import logging
from flask import abort, Flask, jsonify, request
import slack_response

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
app.logger.setLevel(logging.DEBUG)
def is_request_valid(request):
    app.logger.debug(request.form['token'])
    app.logger.debug(os.environ['SLACK_VERIFICATION_TOKEN'])
    return request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']

@app.route('/')
def index():
    return '<h1>Refbot server</h1>'

@app.route('/getquran', methods=["POST"])
@app.route('/getscripture', methods=["POST"])
def get_refs():
    if not is_request_valid(request):
        abort(400)
    ref = request.form.get('text')
    slash_command = request.form.get('command')
    response_text, __, ___ = slack_response.SlackResponseBuilder(ref, slash_command).check_command()
    resp = jsonify(
        response_type='in_channel',
        text= response_text
    )
    resp.status_code = 200
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=port)
