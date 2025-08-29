import hmac
import os

from flask import Flask, jsonify, render_template, request

from github_pr_closer.github import GITHUB_APP_ID_ENVVAR, GITHUB_APP_SECRET_ENVVAR, Repo

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", app_id=os.environ.get(GITHUB_APP_ID_ENVVAR))


@app.post("/github")
def handle_github_hook():
    """Entry point for GitHub webhook"""
    signature = request.headers.get("X-Hub-Signature")
    sha, signature = signature.split("=")

    secret = os.environ.get(GITHUB_APP_SECRET_ENVVAR).encode("utf-8")
    hashhex = hmac.new(secret, request.data, digestmod="sha1").hexdigest()

    if not hmac.compare_digest(hashhex, signature):
        app.logger.info("Bad signature.")
        return jsonify({}), 200

    action = request.json.get("action")
    if action not in ("opened", "reopened"):
        app.logger.info("Ignoring action %s.", action)
        return jsonify({}), 200

    repo = Repo(
        request.json["repository"]["full_name"],
        request.json["repository"]["id"],
    )

    author_name = request.json["pull_request"]["user"]["login"]

    if not repo.should_close(author_name):
        app.logger.info(
            "Ignoring PR #%s on repository %s made by %s",
            request.json["pull_request"]["number"],
            repo.repo_name,
            author_name,
        )

        return jsonify({}), 200

    repo.comment_and_close(request.json["pull_request"])

    app.logger.info(
        "Closed PR #%s on repository %s made by %s",
        request.json["pull_request"]["number"],
        repo.repo_name,
        author_name,
    )

    return jsonify({}), 200


if __name__ == "__main__":
    app.run()
