from typing import Dict, TypedDict, Tuple
from os import environ, path
from base64 import b64decode, b64encode

import boto3
from requests import Session, Response, codes
from requests.auth import HTTPBasicAuth

ARN = environ.get("arn")

# From the hub
HUE_APPLICATION_KEY = environ.get("hue_application_key")

# For OAuth
CLIENT_ID = environ.get("client_id")
CLIENT_SECRET = environ.get("client_secret")

BASE_URL = "https://api.meethue.com"

DESK = "abb4dce9-a33a-4a7f-bf69-a491f8d61c22"
BOWL = "15d8cf20-62db-471e-bbe4-d6835f80cfe4"
LAMP = "f6f1012b-04b1-4970-9d67-81e60ca7cd92"


class Tags(TypedDict):
    hueTokens: str


class TagAuth:
    client = None

    def get_client(self):
        if not self.client:
            self.client = boto3.client("lambda", region_name="eu-west-2")
        return self.client

    def get_tags(self) -> Tags:
        tags = self.get_client().list_tags(Resource=ARN)
        return tags["Tags"]

    def set_tags(self, value: str) -> None:
        self.get_client().tag_resource(
            Resource=ARN,
            Tags={"hueTokens": value},
        )

    def parse_tags(self, tags: Tags) -> Tuple[str, str]:
        data = tags["hueTokens"]
        value = b64decode(data).decode("utf-8")
        values = value.split(":")
        access_token, refresh_token = values
        return access_token, refresh_token

    def retrieve(self) -> Tuple[str, str]:
        tags = self.get_tags()
        return self.parse_tags(tags)

    def save(self, access_token: str, refresh_token: str) -> None:
        data = bytes(f"{access_token}:f{refresh_token}", encoding="utf-8")
        value = b64encode(data).decode("utf-8")
        self.set_tags(value)


class Hue:
    client: Session
    refresh_token: str

    def __init__(self):
        self.client = Session()
        self.auth = TagAuth()
        self.get_tokens()

    def get_tokens(self):
        access_token, refresh_token = self.auth.retrieve()
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.client.headers.update(
            {
                "Authorization": f"Bearer {self.access_token}",
                "hue-application-key": HUE_APPLICATION_KEY,
                "Allow": "*",
            }
        )

    def url(self, pathname: str) -> str:
        return path.join(BASE_URL, pathname)

    def on(self, light_id: str, state: bool) -> Response:
        payload = {"on": {"on": state}}
        res = self.client.put(
            self.url(f"route/clip/v2/resource/light/{light_id}"), json=payload
        )
        if res.status_code == codes.UNAUTHORIZED:
            self.refresh()
        return res

    def refresh(self):
        client = Session()
        client.auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        res = client.post(self.url("v2/oauth2/token"), data=data)
        data = res.json()
        print("Updating access token")
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.auth.save(self.access_token, self.refresh_token)


def all_on(state: bool):
    h = Hue()
    for light_id in [DESK, BOWL, LAMP]:
        h.on(light_id, state)


def main(__event: Dict, __context: Dict):
    all_on(False)


if __name__ == "__main__":
    all_on(True)
