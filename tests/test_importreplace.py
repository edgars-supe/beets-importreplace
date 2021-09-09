import unittest

import beets as beets
from beets.autotag.hooks import AlbumInfo
from beets.autotag.hooks import TrackInfo
from beetsplug.importreplace import ImportReplace


class ImportReplaceTest(unittest.TestCase):

    def _create_track_info(self, title: str = None, artist: str = None,
                           artist_sort: str = None, artist_credit: str = None):
        return TrackInfo(title=title, artist=artist, artist_sort=artist_sort,
                         artist_credit=artist_credit)

    def _create_album_info(self, tracks: [TrackInfo] = None, album: str = None,
                           artist: str = None, artist_sort: str = None,
                           artist_credit: str = None):
        return AlbumInfo(tracks=tracks or [], album=album, artist=artist,
                         artist_sort=artist_sort, artist_credit=artist_credit)

    def _set_config(self, item_fields: [str], album_fields: [str],
                    replace: {str: str}):
        beets.config['importreplace']['item_fields'] = item_fields
        beets.config['importreplace']['album_fields'] = album_fields
        beets.config['importreplace']['replace'] = replace

    def test_replaces_only_config_fields(self):
        """Check if plugin replaces text in only the specified fields"""
        self._set_config(item_fields=['title'], album_fields=['album'],
                         replace={'a': 'x'})
        tracks = [self._create_track_info(title='Fao', artist='Bar')]
        album_info = self._create_album_info(tracks=tracks, album='albumTest',
                                             artist='Bar')
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'xlbumTest')
        self.assertEqual(album_info.artist, 'Bar')
        self.assertEqual(album_info.tracks[0].title, 'Fxo')
        self.assertEqual(album_info.tracks[0].artist, 'Bar')

    def test_handles_empty_fields(self):
        """Verify that plugin works when field marked for replacement
         is absent"""
        self._set_config(item_fields=['title', 'artist'],
                         album_fields=['album', 'artist'],
                         replace={'a': 'x'})
        tracks = [self._create_track_info(title='Fao', artist=None)]
        album_info = self._create_album_info(tracks=tracks, album='albumTest',
                                             artist=None)
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'xlbumTest')
        self.assertEqual(album_info.artist, None)
        self.assertEqual(album_info.tracks[0].title, 'Fxo')
        self.assertEqual(album_info.tracks[0].artist, None)
