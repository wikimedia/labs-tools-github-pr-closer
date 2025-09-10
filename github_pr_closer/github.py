import os
import time
from pathlib import Path

import jwt
import requests

GITHUB_PRIVATE_KEY_ENVVAR = "GHPRC_JWT_SIGNING_KEY"
GITHUB_APP_ID_ENVVAR = "GHPRC_APP_ID"
GITHUB_APP_SECRET_ENVVAR = "GHPRC_APP_SECRET"


def get_jwt() -> str:
    signing_key = os.environ.get(GITHUB_PRIVATE_KEY_ENVVAR)
    app_id = os.environ.get(GITHUB_APP_ID_ENVVAR)

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id,
    }

    return jwt.encode(payload, signing_key, algorithm="RS256")


def get_message_template() -> str:
    return (Path(__file__).parent / "message_template.md").read_text()


def get_install_id(jwt_token, api_type, name):
    return requests.get(
        f"https://api.github.com/{api_type}/{name}/installation",
        headers={
            "Authorization": f"Bearer {jwt_token}",
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
            "Authorization": f"Bearer {jwt_token}",
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
                f"https://api.github.com/repos/{self.repo_name}/contents/{file_name}",
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
        comment_url = f"https://api.github.com/repos/{self.repo_name}/issues/{pull_request['number']}/comments"
        pr_edit_url = f"https://api.github.com/repos/{self.repo_name}/pulls/{pull_request['number']}"

        message = get_message_template().replace(
            "{{author}}", pull_request["user"]["login"]
        )

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.get_access_token()}",
        }

        requests.post(
            comment_url,
            json={
                "body": message,
            },
            headers=headers,
        )

        requests.patch(
            pr_edit_url,
            json={
                "state": "closed",
            },
            headers=headers,
        )
