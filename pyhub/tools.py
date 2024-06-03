import os

SECRETS = {
    "PYHUB_USERNAME": "username",
    "PYHUB_PASSWORD": "password",
    "PYHUB_ORG": "org",
}


def get_credentials_from_env():
    res = {name: os.getenv(envvar) for envvar, name in SECRETS.items()}
    if not all(res.values()):
        raise ValueError("Missing credentials")
    return res
