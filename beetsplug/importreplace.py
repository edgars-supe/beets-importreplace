from __future__ import annotations

import re
from functools import reduce
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from re import Pattern

    from beets.autotag import AlbumInfo, TrackInfo
    from confuse import Subview

from beets.plugins import BeetsPlugin


class ImportReplace(BeetsPlugin):
    def __init__(self) -> None:
        super().__init__()
        self._item_replacements: dict[str, list[tuple[Pattern[str], str]]] = {}
        self._album_replacements: dict[str, list[tuple[Pattern[str], str]]] = {}
        self._read_config()
        self.register_listener("trackinfo_received", self._trackinfo_received)
        self.register_listener("albuminfo_received", self._albuminfo_received)

    def _read_config(self) -> None:
        replacements: Subview = self.config["replacements"]
        for replacement in replacements:
            patterns: list[tuple[Pattern[str], str]] = self._extract_patterns(
                replacement
            )
            if patterns:
                if "item_fields" in replacement.keys():
                    self._extract_item_fields(
                        patterns, replacement["item_fields"].as_str_seq()
                    )
                if "album_fields" in replacement.keys():
                    self._extract_album_fields(
                        patterns, replacement["album_fields"].as_str_seq()
                    )

    @staticmethod
    def _extract_patterns(replacement: Subview) -> list[tuple[Pattern[str], str]]:
        patterns: list[tuple[Pattern[str], str]] = []
        for pattern, repl in replacement["replace"].get(dict).items():
            patterns.append((re.compile(pattern), repl))
        return patterns

    def _extract_item_fields(
        self, patterns: list[tuple[Pattern[str], str]], fields: list[str]
    ) -> None:
        for field in fields:
            if field in self._item_replacements.keys():
                self._item_replacements[field].extend(patterns)
            else:
                self._item_replacements[field] = patterns

    def _extract_album_fields(
        self, patterns: list[tuple[Pattern[str], str]], fields: list[str]
    ) -> None:
        for field in fields:
            if field in self._album_replacements.keys():
                self._album_replacements[field].extend(patterns)
            else:
                self._album_replacements[field] = patterns

    def _trackinfo_received(self, info: TrackInfo) -> None:
        for field, replacements in self._item_replacements.items():
            if field in info:
                value: str | list[str] = info.__getattr__(field)
                if value:
                    replaced: str | list[str] = self._replace_field(value, replacements)
                    info.__setattr__(field, replaced)

    def _albuminfo_received(self, info: AlbumInfo) -> None:
        for field, replacements in self._album_replacements.items():
            if field in info:
                value: str | list[str] = info.__getattr__(field)
                if value:
                    replaced: str | list[str] = self._replace_field(value, replacements)
                    info.__setattr__(field, replaced)
        for track in info.tracks:
            self._trackinfo_received(track)

    def _replace_field(
        self, text: str | list[str], replacements: list[tuple[Pattern[str], str]]
    ) -> str | list[str]:
        if isinstance(text, list):
            return list(
                map(lambda item: str(self._replace_field(item, replacements)), text)
            )
        else:
            return reduce(self._replace, replacements, text)

    def _replace(self, text: str, replacement: tuple[Pattern[str], str]) -> str:
        return replacement[0].sub(repl=replacement[1], string=text)
