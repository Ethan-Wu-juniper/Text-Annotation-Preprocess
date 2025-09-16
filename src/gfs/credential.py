import os
import base64
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request


def get_crendential() -> str | None:
    encoded = os.getenv("GLAB_CREDENTIALS_JSON")
    if encoded:
        credentials_json = base64.b64decode(encoded).decode("utf-8")
        credentials_info = json.loads(credentials_json)
    else:
        return None

    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=scopes
    )
    request = Request()
    credentials.refresh(request)
    return credentials
