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

def url(pathname: str) -> str:
    return path.join(BASE_URL, pathname)


class TagAuth:
    client = None

    def get_client(self):
        if not self.client:
            self.client = boto3.client("lambda", region_name="eu-west-2")
        return self.client

    def retrieve(self) -> None:
        tags = self.get_client().list_tags(Resource=ARN)
        self.parse_tags(tags["Tags"])

    def save(self, access_token: str, refresh_token: str) -> None:
        data = bytes(f"{access_token}:f{refresh_token}", encoding="utf-8")
        value = b64encode(data).decode("utf-8")
        self.get_client().tag_resource(
            Resource=ARN,
            Tags={"hueTokens": value},
        )

    def parse_tags(self, tags: Tags) -> None:
        if "hueTokens" not in tags:
            print("No tokens found in tags")
        data = tags["hueTokens"]
        value = b64decode(data).decode("utf-8")
        values = value.split(":")
        access_token, refresh_token = values
        self.access_token = access_token
        self.refresh_token = refresh_token
        print(self.access_token, self.refresh_token)

    def get_from_auth_code(self,code: str) -> None:
        print(f"https://api.meethue.com/v2/oauth2/authorize?client_id={CLIENT_ID}&response_type=code")
        data = {"grant_type": "authorization_code", "code": code}
        return self.request_token(data)

    def refresh(self):
        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        return self.request_token(data)

    def request_token(self, data: Dict) -> None:
        client = Session()
        client.auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        res = client.post(url("v2/oauth2/token"), data=data)
        data = res.json()
        print("Updating access token", data)
        try:
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
        except KeyError:
            print(data)
            raise Exception("No access token returned")
        else:
            self.save(self.access_token, self.refresh_token)


class Hue:
    client: Session

    def __init__(self):
        self.client = Session()
        self.auth = TagAuth()
        self.auth.retrieve()

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.auth.access_token}",
            "hue-application-key": HUE_APPLICATION_KEY,
            "Allow": "*",
        }

    def on(self, light_id: str, state: bool) -> None:
        payload = {"on": {"on": state}}
        headers = self.get_headers()
        self.client.put(
            url(f"route/clip/v2/resource/light/{light_id}"), json=payload, headers=headers
        )


def all_on(state: bool):
    h = Hue()
    for light_id in [DESK, BOWL, LAMP]:
        h.on(light_id, state)


def main(__event: Dict, __context: Dict):
    all_on(False)


if __name__ == "__main__":
    # auth = TagAuth()
    # auth.get_from_auth_code("gWUvQjox")
    # auth.retrieve()
    all_on(True)
