import json
from typing import TypedDict
from lib.hue import Hue
from lib.scheduler import SleepScheduler
from lib.sonos import Sonos
from lib.ad_killer import AdKiller

DESK = "abb4dce9-a33a-4a7f-bf69-a491f8d61c22"
BOWL = "15d8cf20-62db-471e-bbe4-d6835f80cfe4"
LAMP = "f6f1012b-04b1-4970-9d67-81e60ca7cd92"


class APIResponse(TypedDict):
    statusCode: int
    body: str


def _make_response(data: dict, status=200) -> APIResponse:
    return {"body": json.dumps(data), "statusCode": status}


def main(_event, _context) -> None:
    hue = Hue()
    for light_id in [DESK, BOWL, LAMP]:
        hue.on(light_id, False)
    sonos = Sonos()
    sonos.all_off()


def set_vol(event, _context) -> APIResponse:
    try:
        vol = int(event["pathParameters"]["vol"])
    except (KeyError, ValueError):
        vol = 20

    sonos = Sonos()
    sonos.all_set_vol(vol)

    return _make_response({"message": f"Vol set: {vol}"})


def fade(_event, _context) -> APIResponse:
    sonos = Sonos()
    sonos.fade()

    scheduler = SleepScheduler()
    scheduler.disable()

    hue = Hue()
    hue.on(BOWL, False)

    return _make_response({"message": "Faded"})


def set_sleep(event, _context) -> APIResponse:
    try:
        mins = int(event["pathParameters"]["mins"])
    except (KeyError, ValueError):
        mins = 15

    scheduler = SleepScheduler()
    dt = scheduler.enable(mins)

    hue = Hue()
    hue.on(DESK, False)
    hue.on(LAMP, False)
    hue.dim(BOWL)

    sonos = Sonos()
    sonos.all_set_vol(6)

    return _make_response({"message": f"Timer set for: {mins} off at: {dt.isoformat()}"})


def cancel_sleep(_event, _context) -> APIResponse:
    scheduler = SleepScheduler()
    scheduler.disable()

    return _make_response({"message": "Timer canceled"})


def turn_down_ads(_event, _context) -> None:
    ad_killer = AdKiller()
    ad_killer.turn_down_pb()


def on_ad_timeout(_event, _context) -> None:
    ad_killer = AdKiller()
    ad_killer.turn_back_up()


if __name__ == "__main__":
    sonos = Sonos()
    sonos.get_group_ids()
