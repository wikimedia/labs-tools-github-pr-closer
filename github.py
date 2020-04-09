import jwt
import time
import os
import requests
from flask import current_app


def get_jwt():
    path_to_private_key = os.path.join(os.getcwd(), "github-app-key.pem")
    pem_file = open(path_to_private_key, "rt").read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": current_app.config.get('GITHUB_APP_ID'),
    }
    encoded = jwt.encode(payload, pem_file, algorithm="RS256")
    bearer_token = encoded.decode("utf-8")
    return bearer_token


def get_access_token(repo_name, repo_id):
    jwt_token = get_jwt()
    install_data = requests.get('https://api.github.com/repos/' + repo_name + "/installation",
                                headers={
                                    "Authorization": "Bearer " + jwt_token,
                                    "Accept": "application/vnd.github.machine-man-preview+json"
                                })

    install_json = install_data.json()
    install_id = install_json["id"]

    token_data = requests.post('https://api.github.com/app/installations/' + str(install_id) + '/access_tokens',
                               json={
                                   "repository_ids": [repo_id],
                                   "permissions": {
                                       "metadata": "read",
                                       "pull_requests": "write",
                                       "single_file": "read",
                                   }
                               },
                               headers={
                                   "Authorization": "Bearer " + jwt_token,
                                   "Accept": "application/vnd.github.machine-man-preview+json"
                               })
    return token_data.json()['token']


def get_message_template():
    template_path = os.path.join(os.getcwd(), "message_template.md")
    return open(template_path, "rt").read()
