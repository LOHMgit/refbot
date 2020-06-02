import os

from flask import abort, Flask, jsonify, request
#import slack_response

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))
app.logger.debug(port)

def is_request_valid(request):
    app.logger.debug(os.environ)
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    return is_token_valid

@app.route('/')
def index():
    return '<h1>Refbot server</h1>'

@app.route('/getquran', methods=['POST'])
@app.route('/getscripture', methods=['POST'])
def get_scripture():
    print(request.form)
    if not is_request_valid(request):
        abort(400)
    ref = request.form['text']
    slash_command = request.form['command']
    print(slash_command, ref)
    #response_text = slack_response.SlackResponseBuilder(command, slash_command).response
    resp = jsonify(
        response_type='in_channel',
        text='Scripture here'
    )
    resp.status_code = 200
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)

'''def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    slash_command = ["/getscripture", "/getquran"]
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(' or '.join(slash_command))

    #this is where you put the command logic
    response = slack_response.SlackResponseBuilder(command, slash_command).response
'''