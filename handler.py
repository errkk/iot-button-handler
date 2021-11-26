import json
from base64 import b64decode, b64encode
from os import environ, path
from typing import Dict, Tuple, TypedDict

import boto3
from requests import Response, Session, codes
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

ARN = environ.get("arn")

# From the hub
HUE_APPLICATION_KEY = environ.get("hue_application_key")

# For OAuth
REDIRECT_URI = "https://webhook.site/b1a702b9-4d5d-46f2-a70c-446683799f8c"
CLIENT_ID = environ.get("client_id")
CLIENT_SECRET = environ.get("client_secret")

BASE_URL = "https://api.meethue.com"
TOKEN_URL = path.join(BASE_URL, "v2/oauth2/token")
AUTH_URL = path.join(BASE_URL, "v2/oauth2/authorize")

DESK = "abb4dce9-a33a-4a7f-bf69-a491f8d61c22"
BOWL = "15d8cf20-62db-471e-bbe4-d6835f80cfe4"
LAMP = "f6f1012b-04b1-4970-9d67-81e60ca7cd92"

HUE_TOKEN_KEY = "hueTokens"


class Tags(TypedDict):
    hueTokens: str


class Token(TypedDict):
    expires_in: int
    access_token: str
    refresh_token: str
    token_type: str


def url(pathname: str) -> str:
    return path.join(BASE_URL, pathname)


class TagAuth:
    client = None

    def __init__(self, tag_key: str) -> None:
        self.tag_key = tag_key

    def get_client(self):
        if not self.client:
            self.client = boto3.client("lambda", region_name="eu-west-2")
        return self.client

    def retrieve(self) -> None:
        tags = self.get_client().list_tags(Resource=ARN)
        if self.tag_key not in tags:
            print("No tokens found in tags")
        data = tags[self.tag_key]
        value = b64decode(data).decode("utf-8")
        self.token = json.loads(value)
        return self.token

    def save(self, token) -> None:
        self.token = token
        json_data = json.dumps(self.token)
        data = bytes(json_data, encoding="utf-8")
        value = b64encode(data).decode("utf-8")
        self.get_client().tag_resource(
            Resource=ARN,
            Tags={self.tag_key: value},
        )


# class Hue:
#     client: Session

#     def __init__(self):
#         self.auth = TagAuth()
#         self.auth.retrieve()

#     def get_headers(self):
#         # Always get latest header from auth instance, in case it updated
#         return {
#             "Authorization": f"Bearer {self.auth.access_token}",
#             "hue-application-key": HUE_APPLICATION_KEY,
#             "Allow": "*",
#         }

#     def on(self, light_id: str, state: bool) -> None:
#         payload = {"on": {"on": state}}
#         self.client.put(
#             url(f"route/clip/v2/resource/light/{light_id}"),
#             json=payload,
#         )


# def all_on(state: bool):
#     h = Hue()
#     for light_id in [DESK, BOWL, LAMP]:
#         h.on(light_id, state)


# def main(__event: Dict, __context: Dict):
#     all_on(False)


class Hue:
    client: OAuth2Session
    tag_auth: TagAuth

    def __init__(self) -> None:
        # self.tag_auth = TagAuth()
        self.tag_auth = TagAuth("testTokeKey")

    @classmethod
    def get_auth_url(cls):
        client = OAuth2Session(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI)
        url, state = client.authorization_url(AUTH_URL)
        return url, state

    def fetch_token(self, state: str, code: str) -> None:
        client = OAuth2Session(
            client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, state=state
        )
        headers = {
            "hue-application-key": HUE_APPLICATION_KEY,
            "Allow": "*",
        }
        token = client.fetch_token(
            TOKEN_URL,
            code=code,
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            headers=headers,
            include_client_id=True,
        )
        self.tag_auth.save(token)

    def token_updater(self, token) -> None:
        self.tag_auth.save(token)

    def get_hue_client(self) -> OAuth2Session:
        if self.client:
            return self.client
        self.tag_auth.retrieve()
        extra = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        client = OAuth2Session(
            client_id=CLIENT_ID,
            token=self.tag_auth.token,
            auto_refresh_kwargs=extra,
            auto_refresh_url=TOKEN_URL,
            # TODO make this an instance method so it can update the token that this uses
            token_updater=self.token_updater,
        )
        return client


if __name__ == "__main__":
    h = Hue()
    # print(h.get_auth_url())
    code = "4pJbxBnT"
    state = "KpZzbeJitsmBRAP549vTFFQfJ45Cka"
    h.fetch_token(state, code)
