import hmac
from flask import request, Blueprint, jsonify, current_app

webhook = Blueprint('webhook', __name__, url_prefix='')


@webhook.route('/github', methods=['POST'])
def handle_github_hook():
    """ Entry point for GitHub webhook"""
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')

    secret = str.encode(current_app.config.get('GITHUB_SECRET'))

    hashhex = hmac.new(secret, request.data, digestmod='sha1').hexdigest()
    if hmac.compare_digest(hashhex, signature):
        print(request.data)
    return jsonify({}), 200
