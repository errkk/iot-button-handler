import questionary

from .hue import Hue
from .sonos import Sonos


def auth_hue():
    h = Hue()
    h.get_auth_url()

    code = questionary.text("Enter the code").ask()
    h.fetch_token(code)


def auth_sonos():
    s = Sonos()
    s.get_auth_url()

    code = questionary.text("Enter the code").ask()
    s.fetch_token(code)


if __name__ == "__main__":
    auth_hue()
    auth_sonos()
