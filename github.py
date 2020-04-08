import jwt
import time
import os
import requests
from flask import current_app


def get_jwt():
    path_to_private_key = os.path.join(os.getcwd(), "github-app-key.pem")
    print("path_to_private_key", path_to_private_key)
    pem_file = open(path_to_private_key, "rt").read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": current_app.config.get('GITHUB_APP_ID'),
    }
    encoded = jwt.encode(payload, pem_file, algorithm="RS256")
    bearer_token = encoded.decode("utf-8")
    return bearer_token


def get_access_token():
    pass
