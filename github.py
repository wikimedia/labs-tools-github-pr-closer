import jwt
import time
import os
import requests


def get_jwt():
    path_to_private_key = os.path.join(os.getcwd(), "github-app-key.pem")
    pem_file = open(path_to_private_key, "rt").read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": os.environ.get('GITHUB_APP_ID'),
    }
    encoded = jwt.encode(payload, pem_file, algorithm="RS256")
    bearer_token = encoded.decode("utf-8")
    return bearer_token


def get_message_template():
    template_path = os.path.join(os.getcwd(), "message_template.md")
    return open(template_path, "rt").read()


class Repo:
    def __init__(self, repo_name, repo_id):
        self.repo_name = repo_name
        self.repo_id = repo_id
        self.access_token = None

    def fetch_access_token(self):
        jwt_token = get_jwt()
        install_data = requests.get('https://api.github.com/repos/' + self.repo_name + "/installation",
                                    headers={
                                        "Authorization": "Bearer " + jwt_token,
                                        "Accept": "application/vnd.github.machine-man-preview+json"
                                    })

        install_json = install_data.json()
        install_id = install_json["id"]

        token_data = requests.post('https://api.github.com/app/installations/' + str(install_id) + '/access_tokens',
                                   json={
                                       "repository_ids": [self.repo_id],
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
        self.access_token = token_data.json()['token']

    def does_file_exist(self, file_name):
        return requests.get('https://api.github.com/repos/' + self.repo_name + '/contents/' + file_name,
                            headers={
                                "Accept": "application/vnd.github.v3+json",
                                "Authorization": "token " + self.access_token,
                            }).status_code == 200

    def should_close(self):
        return not self.does_file_exist('.gitreview')

    def comment_and_close(self, pull_request):
        comment_url = 'https://api.github.com/repos/' + self.repo_name + '/issues/' + str(pull_request['number']) + '/comments'
        pr_edit_url = 'https://api.github.com/repos/' + self.repo_name + '/pulls/' + str(pull_request['number'])
        message = get_message_template().replace("{{author}}", pull_request['user']['login'])
        requests.post(comment_url,
                      json={
                          "body": message,
                      },
                      headers={
                          "Accept": "application/vnd.github.v3+json",
                          "Authorization": "token " + self.access_token,
                      })
        requests.patch(pr_edit_url,
                       json={
                           "state": "closed",
                       },
                       headers={
                           "Accept": "application/vnd.github.v3+json",
                           "Authorization": "token " + self.access_token,
                       })
