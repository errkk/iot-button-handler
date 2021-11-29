from lib.hue import Hue
from lib.sonos import Sonos

DESK = "abb4dce9-a33a-4a7f-bf69-a491f8d61c22"
BOWL = "15d8cf20-62db-471e-bbe4-d6835f80cfe4"
LAMP = "f6f1012b-04b1-4970-9d67-81e60ca7cd92"


def main(_event, _context) -> None:
    h = Hue()
    for light_id in [DESK, BOWL, LAMP]:
        h.on(light_id, False)
    s = Sonos()
    s.all_off()


if __name__ == "__main__":
    main({}, {})
