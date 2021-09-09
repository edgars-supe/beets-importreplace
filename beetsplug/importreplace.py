import re
from functools import reduce
from re import Pattern

from beets.autotag import TrackInfo, AlbumInfo
from beets.plugins import BeetsPlugin


class ImportReplace(BeetsPlugin):
    item_fields = set()
    album_fields = set()
    replacements = []

    def __init__(self):
        super(ImportReplace, self).__init__()
        self.item_fields = self.config['item_fields'].as_str_seq()
        self.album_fields = self.config['album_fields'].as_str_seq()
        for pattern, repl in self.config['replace'].get(dict).items():
            repl = repl or ''
            self.replacements.append((re.compile(pattern), repl))
        self.register_listener('trackinfo_received', self.trackinfo_received)
        self.register_listener('albuminfo_received', self.albuminfo_received)

    def trackinfo_received(self, info: TrackInfo):
        for field in self.item_fields:
            if field in info:
                replaced = self.replace_field(info.__getattr__(field))
                info.__setattr__(field, replaced)

    def albuminfo_received(self, info: AlbumInfo):
        for field in self.album_fields:
            if field in info:
                replaced = self.replace_field(info.__getattr__(field))
                info.__setattr__(field, replaced)
        for track in info.tracks:
            self.trackinfo_received(track)

    def replace_field(self, text: str) -> str:
        return reduce(self.replace, self.replacements, text)

    def replace(self, text: str, replacement: (Pattern, str)) -> str:
        return replacement[0].sub(repl=replacement[1], string=text)