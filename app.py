from flask import Flask, render_template
from webhook_handler import webhook

app = Flask(__name__)
app.register_blueprint(webhook)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
