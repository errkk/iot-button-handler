import json
from typing import TypedDict
from lib.hue import Hue
from lib.sonos import Sonos

DESK = "abb4dce9-a33a-4a7f-bf69-a491f8d61c22"
BOWL = "15d8cf20-62db-471e-bbe4-d6835f80cfe4"
LAMP = "f6f1012b-04b1-4970-9d67-81e60ca7cd92"


class APIResponse(TypedDict):
    statusCode: int
    body: str


def _make_response(data: dict, status=200) -> APIResponse:
    return {"body": json.dumps(data), "statusCode": status}


def main(_event, _context) -> None:
    h = Hue()
    for light_id in [DESK, BOWL, LAMP]:
        h.on(light_id, False)
    s = Sonos()
    s.all_off()


def set_vol(event, _context) -> APIResponse:
    try:
        vol = int(event["pathParameters"]["vol"])
    except (KeyError, ValueError):
        vol = 20

    s = Sonos()
    s.all_set_vol(vol)

    return _make_response({"message": f"Vol set: {vol}"})


if __name__ == "__main__":
    main({}, {})
