from time import time
import webbrowser
from os import environ, path
from typing import List

from requests.auth import HTTPBasicAuth
from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from .tag_auth import TagAuth, Token

# For OAuth
REDIRECT_URI = "https://webhook.site/b1a702b9-4d5d-46f2-a70c-446683799f8c"
CLIENT_ID = environ["sonos_client_id"]
CLIENT_SECRET = environ["sonos_client_secret"]
TOKEN_KEY = environ["sonos_token_key"]

SONOS_HOUSEHOLD = environ["sonos_household"]

BASE_URL = "https://api.ws.sonos.com/control/api/v1"
TOKEN_URL = "https://api.sonos.com/login/v3/oauth/access"
AUTH_URL = "https://api.sonos.com/login/v3/oauth"

# Scope requested and in requests. Not saved in token dict
SCOPE = "playback-control-all"


class Sonos(TagAuth):
    tag_key = TOKEN_KEY

    def __init__(self) -> None:
        self._client = None
        self.manual_refresh = False

    @classmethod
    def get_auth_url(cls):
        client = OAuth2Session(
            client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE
        )
        url, _ = client.authorization_url(AUTH_URL)
        webbrowser.open_new_tab(url)

    def fetch_token(self, code: str) -> None:
        client = OAuth2Session(
            CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
        )

        token: Token = client.fetch_token(
            TOKEN_URL, client_secret=CLIENT_SECRET, code=code
        )
        self.token_updater(token)

    def get_sonos_client(self) -> OAuth2Session:
        if self._client:
            return self._client
        self.retrieve()
        if self.manual_refresh:
            self.token["expires_at"] = time() - 100
        self._client = OAuth2Session(
            client_id=CLIENT_ID,
            token=self.token,
        )
        return self._client

    def refresh_token(self) -> None:
        """
        Have to manually catch TokenExpiredError and refetch retry
        cos stoopid lib doesn't let us send the basic auth header in
        the refresh_token retquest, when it's done automatically
        """
        token = self.get_sonos_client().refresh_token(
            TOKEN_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        )
        self.token_updater(token)

    def request(self, *args, **kwargs) -> Response:
        try:
            return self.get_sonos_client().request(*args, **kwargs)
        except TokenExpiredError:
            self.refresh_token()
            return self.request(*args, **kwargs)

    def token_updater(self, token: Token) -> None:
        # Remove this so the token can be b64 encoded to < 256 bytes
        del token["scope"]
        self.save(token)

    def get_households(self) -> Response:
        return self.request("get", path.join(BASE_URL, "households"))

    def get_groups(self) -> Response:
        return self.request(
            "get", path.join(BASE_URL, "households", SONOS_HOUSEHOLD, "groups")
        )

    def stop(self, group_id: str) -> Response:
        return self.request(
            "post",
            path.join(BASE_URL, "groups", group_id, "playback", "pause"),
            json={},
        )

    def set_vol(self, group_id: str, vol: int) -> Response:
        volume = min(abs(vol), 100)
        return self.request(
            "post",
            path.join(BASE_URL, "groups", group_id, "groupVolume"),
            json={"volume": volume},
        )

    def get_group_ids(self) -> List[str]:
        res = self.get_groups()
        data = res.json()
        return [g["id"] for g in data["groups"]]

    def all_off(self):
        for group_id in self.get_group_ids():
            self.stop(group_id)

    def turn_down(self):
        for group_id in self.get_group_ids():
            self.set_vol(group_id, 5)

    def all_set_vol(self, vol: int):
        for group_id in self.get_group_ids():
            self.set_vol(group_id, vol)
