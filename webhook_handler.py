import os
import hmac
from flask import request, Blueprint, jsonify
import github

webhook = Blueprint("webhook", __name__, url_prefix="")


@webhook.route("/github", methods=["POST"])
def handle_github_hook():
    """Entry point for GitHub webhook"""
    signature = request.headers.get("X-Hub-Signature")
    sha, signature = signature.split("=")

    secret = str.encode(os.environ.get("GITHUB_SECRET"))
    hashhex = hmac.new(secret, request.data, digestmod="sha1").hexdigest()

    if hmac.compare_digest(hashhex, signature):
        if request.json["action"] != "opened":
            return jsonify({}), 200

        repo = github.Repo(
            request.json["repository"]["full_name"], request.json["repository"]["id"]
        )

        if repo.should_close(request.json["pull_request"]["user"]["login"]):
            repo.comment_and_close(request.json["pull_request"])
            print(
                "Closed pr #"
                + str(request.json["pull_request"]["number"])
                + " on repository "
                + repo.repo_name,
                " made by ",
                request.json["pull_request"]["user"]["login"],
            )

    return jsonify({}), 200
