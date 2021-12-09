import webbrowser
from os import environ, path

from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from .tag_auth import TagAuth, Token

# From the hub
HUE_APPLICATION_KEY = environ["hue_application_key"]

# For OAuth
REDIRECT_URI = "https://webhook.site/b1a702b9-4d5d-46f2-a70c-446683799f8c"
CLIENT_ID = environ["hue_client_id"]
CLIENT_SECRET = environ["hue_client_secret"]
TOKEN_KEY = environ["hue_token_key"]

BASE_URL = "https://api.meethue.com"
TOKEN_URL = path.join(BASE_URL, "v2/oauth2/token")
AUTH_URL = path.join(BASE_URL, "v2/oauth2/authorize")


class Hue(TagAuth):
    tag_key = TOKEN_KEY

    def __init__(self) -> None:
        self._client = None

    @classmethod
    def get_auth_url(cls):
        client = OAuth2Session(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI)
        url, _ = client.authorization_url(AUTH_URL)
        webbrowser.open_new_tab(url)

    def fetch_token(self, code: str) -> None:
        client = OAuth2Session(
            CLIENT_ID,
        )
        client.auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

        token: Token = client.fetch_token(
            TOKEN_URL, client_secret=CLIENT_SECRET, code=code
        )
        self.save(token)

    def get_hue_client(self) -> OAuth2Session:
        if self._client:
            return self._client
        self.retrieve()
        extra = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        self._client = OAuth2Session(
            client_id=CLIENT_ID,
            token=self.token,
            auto_refresh_kwargs=extra,
            auto_refresh_url=TOKEN_URL,
            token_updater=self.save,
        )
        self._client.headers.update(
            {
                "hue-application-key": HUE_APPLICATION_KEY,
            }
        )
        return self._client

    def on(self, light_id: str, state: bool) -> None:
        payload = {"on": {"on": state}}
        self.get_hue_client().put(
            path.join(BASE_URL, "route/clip/v2/resource/light", light_id),
            json=payload,
        )

    def dim(self, light_id: str) -> None:
        payload = {
            "on": {"on": True},
            "dimming": {"brightness": 30},
            "color_temperature": {"mirek": 500},  # 153 -1500
            "dynamics": {"duration": 10000},
        }

        self.get_hue_client().put(
            path.join(BASE_URL, "route/clip/v2/resource/light", light_id),
            json=payload,
        )
