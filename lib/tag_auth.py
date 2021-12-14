from __future__ import annotations
import json
from os import environ
from base64 import b64decode, b64encode
from typing import TypedDict, List
from typing_extensions import NotRequired

import boto3


ARN = environ["arn"]


class Tags(TypedDict):
    hueTokens: str


class Token(TypedDict):
    expires_in: int
    expires_at: float
    access_token: str
    refresh_token: str
    token_type: str
    scope: NotRequired[List]


class TagBase:
    boto_client = None
    data = {}
    tag_key: str

    def get_boto_client(self):
        if not self.boto_client:
            self.boto_client = boto3.client("lambda", region_name="eu-west-2")
        return self.boto_client

    def retrieve(self) -> Dict:
        tags = self.get_boto_client().list_tags(Resource=ARN)
        if self.tag_key not in tags["Tags"]:
            print("No tokens found in tags")
        data = tags["Tags"][self.tag_key]
        value = b64decode(data).decode("utf-8")
        self.data = json.loads(value)
        return self.data

    def save(self, data: Dict) -> None:
        self.data = data
        json_data = json.dumps(self.data)
        data = bytes(json_data, encoding="utf-8")
        value = b64encode(data).decode("utf-8")
        self.get_boto_client().tag_resource(
            Resource=ARN,
            Tags={self.tag_key: value},
        )


class TagAuth(TagBase):
    token: Token
    tag_key: str

    def retrieve(self) -> Token:
        self.token = super().retrieve()
        return self.token

    def save(self, token: Token) -> None:
        self.token = token
        self.data = token
        super().save(token)
