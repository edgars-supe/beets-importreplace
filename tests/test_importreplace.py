from __future__ import annotations

import sys

if not sys.version_info < (3, 12):
    from typing import override  # pyright: ignore[reportUnreachable]
else:
    from typing_extensions import override
import unittest

import beets as beets
from beets.autotag.hooks import AlbumInfo, TrackInfo

from beetsplug.importreplace import ImportReplace

# multi-valued tags was added in beets v2.0.0 (#4743)


class ImportReplaceTest(unittest.TestCase):
    @override
    def setUp(self) -> None:
        beets.config["importreplace"] = {"replacements": []}

    @override
    def tearDown(self) -> None:
        beets.config["importreplace"] = {"replacements": []}

    def _create_track_info(
        self,
        title: str | None = None,
        artist: str | None = None,
        artist_sort: str | None = None,
        artist_credit: str | None = None,
        artists: list[str] | None = None,
        artists_sort: list[str] | None = None,
        artists_credit: list[str] | None = None,
        track_id: str | None = None,
    ) -> TrackInfo:
        return TrackInfo(
            title=title,
            track_id=track_id,
            artist=artist,
            artist_sort=artist_sort,
            artist_credit=artist_credit,
            artists=artists,
            artists_sort=artists_sort,
            artists_credit=artists_credit,
        )

    def _create_album_info(
        self,
        tracks: list[TrackInfo] | None = None,
        album: str | None = None,
        artist: str | None = None,
        artist_sort: str | None = None,
        artist_credit: str | None = None,
        artists: list[str] | None = None,
        artists_sort: list[str] | None = None,
        artists_credit: list[str] | None = None,
        album_id: str | None = None,
        artist_id: str | None = None,
    ) -> AlbumInfo:
        return AlbumInfo(
            album=album,
            album_id=album_id,
            artist=artist,
            artist_id=artist_id,
            tracks=tracks or [],
            artist_sort=artist_sort,
            artist_credit=artist_credit,
            artists=artists,
            artists_sort=artists_sort,
            artists_credit=artists_credit,
        )

    def _add_replacement(
        self,
        item_fields: list[str] | None = None,
        album_fields: list[str] | None = None,
        replace: dict[str, str] | None = None,
    ) -> None:
        replacement: dict[str, dict[str, str] | list[str]] = {}
        if item_fields:
            replacement["item_fields"] = item_fields
        if album_fields:
            replacement["album_fields"] = album_fields
        if replace:
            replacement["replace"] = replace

        beets.config["importreplace"]["replacements"].get(list).append(replacement)

    def test_replaces_only_config_fields(self) -> None:
        """Check if plugin replaces text in only the specified fields"""
        self._add_replacement(
            item_fields=["title"], album_fields=["album"], replace={"The": "A"}
        )
        tracks: list[TrackInfo] = [
            self._create_track_info(title="The Piece", artist="The Dude")
        ]
        album_info: AlbumInfo = self._create_album_info(
            tracks=tracks,
            album="The Album",
            artist="The Dude",
            artists=["The Dude", "This Artist"],
        )
        subject: ImportReplace = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, "A Album")
        self.assertEqual(album_info.artist, "The Dude")
        self.assertEqual(album_info.tracks[0].title, "A Piece")
        self.assertEqual(album_info.tracks[0].artist, "The Dude")
        self.assertEqual(album_info.artists[0], "The Dude")
        self.assertEqual(album_info.artists[1], "This Artist")

    def test_replaces_only_config_fields_multiple(self) -> None:
        """Check if plugin replaces text in only the specified fields when
        multiple replacements given."""
        self._add_replacement(
            item_fields=["title"], album_fields=["album"], replace={"The": "A"}
        )
        self._add_replacement(
            item_fields=["artist"],
            album_fields=["artist", "artists"],
            replace={"This": "That"},
        )
        tracks: list[TrackInfo] = [
            self._create_track_info(title="The Piece", artist="The This")
        ]
        album_info: AlbumInfo = self._create_album_info(
            tracks=tracks,
            album="The Album",
            artist="The This",
            artists=["The This", "This Artist"],
            artists_credit=["The This"],
        )
        subject: ImportReplace = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, "A Album")
        self.assertEqual(album_info.artist, "The That")
        self.assertEqual(album_info.tracks[0].title, "A Piece")
        self.assertEqual(album_info.tracks[0].artist, "The That")
        self.assertEqual(album_info.artists[0], "The That")
        self.assertEqual(album_info.artists[1], "That Artist")
        self.assertEqual(album_info.artists_credit[0], "The This")

    def test_handles_empty_fields(self) -> None:
        """Verify that plugin works when field marked for replacement
        is absent"""
        self._add_replacement(
            item_fields=["title", "artist"],
            album_fields=["album", "artist"],
            replace={"This": "That"},
        )
        tracks: list[TrackInfo] = [
            self._create_track_info(title="This Piece", artist=None)
        ]
        album_info: AlbumInfo = self._create_album_info(
            tracks=tracks, album="This Album", artist=None
        )
        subject: ImportReplace = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, "That Album")
        self.assertEqual(album_info.artist, None)
        self.assertEqual(album_info.tracks[0].title, "That Piece")
        self.assertEqual(album_info.tracks[0].artist, None)

    def test_replaces_in_order(self) -> None:
        """Verify that the plugin replaces fields in the order given in the
        config."""
        self._add_replacement(
            item_fields=["title"], album_fields=["album"], replace={"The": "This"}
        )
        self._add_replacement(
            item_fields=["title"], album_fields=["album"], replace={"This": "That"}
        )
        tracks: list[TrackInfo] = [
            self._create_track_info(title="The Piece", artist="The Dude")
        ]
        album_info: AlbumInfo = self._create_album_info(
            tracks=tracks, album="The Album", artist="The Dude"
        )
        subject: ImportReplace = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, "That Album")
        self.assertEqual(album_info.artist, "The Dude")
        self.assertEqual(album_info.tracks[0].title, "That Piece")
        self.assertEqual(album_info.tracks[0].artist, "The Dude")

    def test_incorrect_field(self) -> None:
        """Verify the plugin works when a non-existent field is specified."""
        self._add_replacement(
            item_fields=["asdf"], album_fields=["asdf"], replace={"This": "That"}
        )
        tracks: list[TrackInfo] = [
            self._create_track_info(title="The Piece", artist="The Dude")
        ]
        album_info: AlbumInfo = self._create_album_info(
            tracks=tracks, album="The Album", artist="The Dude"
        )
        subject: ImportReplace = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, "The Album")
        self.assertEqual(album_info.artist, "The Dude")
        self.assertEqual(album_info.tracks[0].title, "The Piece")
        self.assertEqual(album_info.tracks[0].artist, "The Dude")

    def test_no_fields(self) -> None:
        """Verify the plugin works when item_fields or album_fields not
        given."""
        self._add_replacement(item_fields=["title"], replace={"The": "A"})
        self._add_replacement(album_fields=["artist"], replace={"This": "That"})
        tracks: list[TrackInfo] = [
            self._create_track_info(title="The Piece", artist="The This")
        ]
        album_info: AlbumInfo = self._create_album_info(
            tracks=tracks,
            album="The Album",
            artist="The This",
            artists=["The Dude", "This Artist"],
        )
        subject: ImportReplace = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, "The Album")
        self.assertEqual(album_info.artist, "The That")
        self.assertEqual(album_info.tracks[0].title, "A Piece")
        self.assertEqual(album_info.tracks[0].artist, "The This")
        self.assertEqual(album_info.artists[0], "The Dude")
        self.assertEqual(album_info.artists[1], "This Artist")
