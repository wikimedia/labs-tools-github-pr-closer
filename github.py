import jwt
import time
import os
import requests


GITHUB_PRIVATE_KEY_FILE = "/data/project/github-pr-closer/data/github-app-key.pem"
GITHUB_APP_ID_FILE = "/data/project/github-pr-closer/data/github-app-id.txt"
GITHUB_APP_SECRET_FILE = "/data/project/github-pr-closer/data/github-app-secret.txt"


def get_jwt():
    with open(GITHUB_PRIVATE_KEY_FILE, "rt") as f:
        pem_file = f.read()
    with open(GITHUB_APP_ID_FILE, "rt") as f:
        app_id = f.read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id,
    }

    encoded = jwt.encode(payload, pem_file, algorithm="RS256")
    bearer_token = encoded.decode("utf-8")
    return bearer_token


def get_message_template():
    template_path = os.path.join(os.path.dirname(__file__), "message_template.md")
    with open(template_path, "rt") as f:
        return f.read()


def get_install_id(jwt_token, api_type, name):
    return requests.get(
        "https://api.github.com/" + api_type + "/" + name + "/installation",
        headers={
            "Authorization": "Bearer " + jwt_token,
            "Accept": "application/vnd.github.machine-man-preview+json",
        },
    ).json()["id"]


def get_access_token(jwt_token, install_id, additional_args=None):
    if additional_args is None:
        additional_args = {}

    params = {
        **additional_args,
        "permissions": {
            "metadata": "read",
            "pull_requests": "write",
            "single_file": "read",
        },
    }

    return requests.post(
        f"https://api.github.com/app/installations/{install_id}/access_tokens",
        json=params,
        headers={
            "Authorization": "Bearer " + jwt_token,
            "Accept": "application/vnd.github.machine-man-preview+json",
        },
    ).json()["token"]


class Repo:
    def __init__(self, repo_name, repo_id):
        self.repo_name = repo_name
        self.repo_id = repo_id
        self.access_token = None

    def set_access_token(self, token):
        self.access_token = token

    def fetch_access_token(self):
        jwt_token = get_jwt()

        install_id = get_install_id(jwt_token, "repos", self.repo_name)
        self.set_access_token(
            get_access_token(jwt_token, install_id, {"repository_ids": [self.repo_id]})
        )

    def get_access_token(self):
        if self.access_token is None:
            self.fetch_access_token()

        return self.access_token

    def does_file_exist(self, file_name):
        return (
            requests.get(
                "https://api.github.com/repos/"
                + self.repo_name
                + "/contents/"
                + file_name,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token {self.get_access_token()}",
                },
            ).status_code
            == 200
        )

    def should_close(self, author):
        if author == "dependabot[bot]" and self.does_file_exist(
            ".github/workflows/dependabot-gerrit.yml"
        ):
            return False

        return self.does_file_exist(".gitreview")

    def comment_and_close(self, pull_request):
        comment_url = (
            "https://api.github.com/repos/"
            + self.repo_name
            + "/issues/"
            + str(pull_request["number"])
            + "/comments"
        )
        pr_edit_url = (
            "https://api.github.com/repos/"
            + self.repo_name
            + "/pulls/"
            + str(pull_request["number"])
        )
        message = get_message_template().replace(
            "{{author}}", pull_request["user"]["login"]
        )
        requests.post(
            comment_url,
            json={
                "body": message,
            },
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.get_access_token()}",
            },
        )
        requests.patch(
            pr_edit_url,
            json={
                "state": "closed",
            },
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.get_access_token()}",
            },
        )
