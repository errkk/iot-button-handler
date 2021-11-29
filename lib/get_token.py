import questionary

from .hue import Hue


def main():
    h = Hue()
    h.get_auth_url()

    code = questionary.text("Enter the code").ask()
    h.fetch_token(code)


if __name__ == "__main__":
    main()
