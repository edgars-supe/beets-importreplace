import re
from functools import reduce
from re import Pattern

from beets.autotag import TrackInfo, AlbumInfo
from beets.plugins import BeetsPlugin


class ImportReplace(BeetsPlugin):
    def __init__(self):
        super(ImportReplace, self).__init__()
        self._item_replacements = {}
        self._album_replacements = {}
        self._read_config()
        self.register_listener('trackinfo_received', self._trackinfo_received)
        self.register_listener('albuminfo_received', self._albuminfo_received)

    def _read_config(self):
        replacements = self.config['replacements']
        for replacement in replacements:
            patterns = self._extract_patterns(replacement)
            if patterns:
                if 'item_fields' in replacement.keys():
                    self._extract_item_fields(
                        patterns,
                        replacement['item_fields'].as_str_seq())
                if 'album_fields' in replacement.keys():
                    self._extract_album_fields(
                        patterns,
                        replacement['album_fields'].as_str_seq())

    @staticmethod
    def _extract_patterns(replacement) -> [(Pattern, str)]:
        patterns = []
        for pattern, repl in replacement['replace'].get(dict).items():
            patterns.append((re.compile(pattern), repl))
        return patterns

    def _extract_item_fields(self, patterns, fields):
        for field in fields:
            if field in self._item_replacements.keys():
                self._item_replacements[field].extend(patterns)
            else:
                self._item_replacements[field] = patterns

    def _extract_album_fields(self, patterns, fields):
        for field in fields:
            if field in self._album_replacements.keys():
                self._album_replacements[field].extend(patterns)
            else:
                self._album_replacements[field] = patterns

    def _trackinfo_received(self, info: TrackInfo):
        for field, replacements in self._item_replacements.items():
            if field in info:
                value = info.__getattr__(field)
                if value:
                    replaced = self._replace_field(value, replacements)
                    info.__setattr__(field, replaced)

    def _albuminfo_received(self, info: AlbumInfo):
        for field, replacements in self._album_replacements.items():
            if field in info:
                value = info.__getattr__(field)
                if value:
                    replaced = self._replace_field(value, replacements)
                    info.__setattr__(field, replaced)
        for track in info.tracks:
            self._trackinfo_received(track)

    def _replace_field(self, text: str|list, replacements: [(Pattern, str)]) -> str|list:
        if isinstance(text, list):
            return list(map(lambda item: reduce(self._replace, replacements, item), text))
        else:
            return reduce(self._replace, replacements, text)

    def _replace(self, text: str, replacement: (Pattern, str)) -> str:
        return replacement[0].sub(repl=replacement[1], string=text)
