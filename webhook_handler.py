import hmac
from flask import request, Blueprint, jsonify, current_app
import github
import requests

webhook = Blueprint('webhook', __name__, url_prefix='')


@webhook.route('/github', methods=['POST'])
def handle_github_hook():
    """ Entry point for GitHub webhook"""
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')

    secret = str.encode(current_app.config.get('GITHUB_SECRET'))
    hashhex = hmac.new(secret, request.data, digestmod='sha1').hexdigest()

    if hmac.compare_digest(hashhex, signature):
        if request.json["action"] != "opened":
            return jsonify({}), 200

        repo = request.json['repository']
        access_token = github.get_access_token(repo['full_name'], repo['id'])

        gitreview_file_url = repo['contents_url'].replace('{+path}', '.gitreview')
        gitreview_data = requests.get(gitreview_file_url,
                                      headers={
                                          "Accept": "application/vnd.github.v3+json",
                                          "Authorization": "token " + access_token,
                                      })

        if gitreview_data.status_code == 404:
            # gitreview not present; probably not mirrored from Gerrit so not commenting
            return

        comment_url = 'https://api.github.com/repos/' + repo['full_name'] + '/issues/' + str(request.json['pull_request']['number']) + '/comments'
        pr_edit_url = 'https://api.github.com/repos/' + repo['full_name'] + '/pulls/' + str(request.json['pull_request']['number'])
        message = github.get_message_template().replace("{{author}}", request.json['pull_request']['user']['login'])
        requests.post(comment_url,
                      json={
                          "body": message,
                      },
                      headers={
                          "Accept": "application/vnd.github.v3+json",
                          "Authorization": "token " + access_token,
                      })
        requests.patch(pr_edit_url,
                       json={
                           "state": "closed",
                       },
                       headers={
                           "Accept": "application/vnd.github.v3+json",
                           "Authorization": "token " + access_token,
                       })
        print("Closed pr #" + str(request.json['pull_request']['number']) + " on repository " + repo['full_name'])

    return jsonify({}), 200
