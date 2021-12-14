from os import environ

from lib.tag_auth import TagBase
from lib.sonos import Sonos


VOL_KEY = environ["prev_vol_key"]


class AdKiller(TagBase):
    tag_key = VOL_KEY
    turned_down = 4
    default_vol = 12

    def __init__(self) -> None:
        self.sonos = Sonos()
        self.group_id: str = self.sonos.get_group_ids()[0]

    def pb_check(self) -> bool:
        is_playing = self.sonos.is_playing(self.group_id)
        is_pb = self.sonos.is_pb(self.group_id)
        return is_playing and is_pb

    def turn_down_pb(self):
        if not self.pb_check():
            return
        # Save current vol for next time
        vol = self.sonos.get_vol(self.group_id)
        # Turn it the fuck down
        turned_down = False
        if vol > self.turned_down:
            self.sonos.set_vol(self.group_id, self.turned_down)
            turned_down = True

        self.save({"vol": vol, "turned_down": turned_down})

    def turn_back_up(self):
        if not self.pb_check():
            return
        current_vol = self.sonos.get_vol(self.group_id)
        if current_vol != self.turned_down:
            return
        self.retrieve()
        prev_vol = self.data.get("vol", self.default_vol)
        turned_down = self.data.get("turned_down", False)
        if turned_down:
            self.sonos.set_vol(self.group_id, prev_vol)
