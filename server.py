# coding: utf-8

from flask import Flask, request, send_from_directory
from config import CONFIG
import messenger

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == CONFIG['VERIFY_TOKEN']:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()

    for event in messenger.messaging_events(payload):
        if 'optin' in event:
            messenger.received_authentication(event)
        elif 'message' in event:
            messenger.received_message(event)
        elif 'delivery' in event:
            messenger.received_delivery_confirmation(event)
        elif 'postback' in event:
            messenger.received_postback(event)
        elif 'read' in event:
            messenger.received_message_read(event)
        elif 'account_linking' in event:
            messenger.received_account_link(event)
        else:
            print("Webhook received unknown messagingEvent:", event)

    return "ok"


@app.route('/authorize', methods=['GET'])
def authorize():
    account_linking_token = request.args.get('account_linking_token', '')
    redirect_uri = request.args.get('redirect_uri', '')

    auth_code = '1234567890'

    redirect_uri_success = redirect_uri + "&authorization_code=" + auth_code

    return "ok"


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('assets', path)


if __name__ == '__main__':
    app.run(port=8080, debug=False)
