import re
from functools import reduce
from re import Pattern

from beets.autotag import TrackInfo, AlbumInfo
from beets.plugins import BeetsPlugin


class ImportReplace(BeetsPlugin):
    _item_fields = set()
    _album_fields = set()
    _replacements = []

    def __init__(self):
        super(ImportReplace, self).__init__()
        self._item_fields = self.config['item_fields'].as_str_seq()
        self._album_fields = self.config['album_fields'].as_str_seq()
        for pattern, repl in self.config['replace'].get(dict).items():
            repl = repl or ''
            self._replacements.append((re.compile(pattern), repl))
        self.register_listener('trackinfo_received', self._trackinfo_received)
        self.register_listener('albuminfo_received', self._albuminfo_received)

    def _trackinfo_received(self, info: TrackInfo):
        for field in self._item_fields:
            if field in info:
                value = info.__getattr__(field)
                if value:
                    replaced = self._replace_field(value)
                    info.__setattr__(field, replaced)

    def _albuminfo_received(self, info: AlbumInfo):
        for field in self._album_fields:
            if field in info:
                value = info.__getattr__(field)
                if value:
                    replaced = self._replace_field(value)
                    info.__setattr__(field, replaced)
        for track in info.tracks:
            self._trackinfo_received(track)

    def _replace_field(self, text: str) -> str:
        return reduce(self._replace, self._replacements, text)

    def _replace(self, text: str, replacement: (Pattern, str)) -> str:
        return replacement[0].sub(repl=replacement[1], string=text)
