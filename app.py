import subprocess
from flask import Flask, render_template
from webhook_handler import webhook


def get_revision():
    try:
        output = (
            subprocess.check_output(
                ["git", "describe", "--always"], stderr=subprocess.STDOUT
            )
            .strip()
            .decode()
        )
        assert "fatal" not in output
        return output
    except Exception:
        # if somehow git version retrieving command failed, just return
        return ""


app = Flask(__name__)
app.register_blueprint(webhook)


@app.context_processor
def inject_base_variables():
    return {
        "revision": get_revision(),
    }


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
