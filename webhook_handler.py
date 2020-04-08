import hmac
from flask import request, Blueprint, jsonify, current_app
import github

webhook = Blueprint('webhook', __name__, url_prefix='')


@webhook.route('/github', methods=['POST'])
def handle_github_hook():
    """ Entry point for GitHub webhook"""
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')

    secret = str.encode(current_app.config.get('GITHUB_SECRET'))
    hashhex = hmac.new(secret, request.data, digestmod='sha1').hexdigest()

    if hmac.compare_digest(hashhex, signature):
        print("request data matches")
        if request.json["action"] != "opened":
            print("Action is not opened")
            return jsonify({}), 200
        gitreview_file_url = request.json['pull_request']['repo']['contents_url'].replace('{+path}', '.gitreview')
    return jsonify({}), 200
