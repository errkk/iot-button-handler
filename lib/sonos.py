import webbrowser
from os import environ, path

from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from .tag_auth import TagAuth

# From the hub
HUE_APPLICATION_KEY = environ["hue_application_key"]

# For OAuth
REDIRECT_URI = "https://webhook.site/b1a702b9-4d5d-46f2-a70c-446683799f8c"
CLIENT_ID = environ["sonos_client_id"]
CLIENT_SECRET = environ["sonos_client_secret"]

BASE_URL = "https://api.ws.sonos.com/control/api/v1"
TOKEN_URL = "https://api.sonos.com/login/v3/oauth/access"
AUTH_URL = "https://api.sonos.com/login/v3/oauth"


class Sonos(TagAuth):
    tag_key = HUE_TOKEN_KEY

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

        token = client.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, code=code)
        self.save(token)

    def get_sonos_client(self) -> OAuth2Session:
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
        self.get_sonos_client().put(
            path.join(BASE_URL, "route/clip/v2/resource/light", light_id),
            json=payload,
        )
