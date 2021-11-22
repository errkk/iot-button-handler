from typing import Dict
from os import environ, path
from requests import Session, Response

access_token = environ.get('access_token')
HUE_APPLICATION_KEY = environ.get('hue_application_key')

BASE_URL = "https://api.meethue.com/route/clip/v2"

DESK = "abb4dce9-a33a-4a7f-bf69-a491f8d61c22"
BOWL = "15d8cf20-62db-471e-bbe4-d6835f80cfe4"
LAMP = "f6f1012b-04b1-4970-9d67-81e60ca7cd92"

hue_client = Session()
hue_client.headers.update({
    'Authorization': f"Bearer {access_token}",
    'hue-application-key': HUE_APPLICATION_KEY,
    'Allow': "*"
})

def url(pathname: str) -> str:
    return path.join(BASE_URL, pathname)

def on(light_id: str, state: bool) -> Response:
    payload = {"on": {"on": state}}
    return hue_client.put(url(f"resource/light/{light_id}"), json=payload)


def all_on(state: bool):
    for light_id in [DESK, BOWL, LAMP]:
        on(light_id, state)

def main(__event: Dict, __context: Dict):
    all_on(False)

if __name__ == "__main__":
    all_on(True)
