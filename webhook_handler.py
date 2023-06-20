import hmac
import os
from flask import request, Blueprint, jsonify
import github

webhook = Blueprint("webhook", __name__, url_prefix="")


@webhook.route("/github", methods=["POST"])
def handle_github_hook():
    """Entry point for GitHub webhook"""
    signature = request.headers.get("X-Hub-Signature")
    sha, signature = signature.split("=")

    secret = os.getenv("GITHUB_APP_SECRET_ENVVAR")
    hashhex = hmac.new(secret, request.data, digestmod="sha1").hexdigest()

    if not hmac.compare_digest(hashhex, signature):
        return jsonify({}), 200
    if request.json["action"] not in ("opened", "reopened"):
        return jsonify({}), 200

    repo = github.Repo(
        request.json["repository"]["full_name"], request.json["repository"]["id"]
    )

    if not repo.should_close(request.json["pull_request"]["user"]["login"]):
        return jsonify({}), 200

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
