import unittest

import beets as beets
from beets.autotag.hooks import AlbumInfo
from beets.autotag.hooks import TrackInfo
from beetsplug.importreplace import ImportReplace

# multi-valued tags was added in beets v2.0.0 (#4743)

class ImportReplaceTest(unittest.TestCase):

    def setUp(self):
        beets.config['importreplace'] = {'replacements': []}

    def tearDown(self):
        beets.config['importreplace'] = {'replacements': []}

    def _create_track_info(self, title: str = None, artist: str = None,
                           artist_sort: str = None, artist_credit: str = None,
                           artists: [str]= None, artists_sort: [str] = None,
                           artists_credit: [str] = None, track_id: str = None):
        try:
            return TrackInfo(title=title, track_id=track_id, artist=artist,
                             artist_sort=artist_sort,
                             artist_credit=artist_credit, artists=artists,
                             artists_sort=artists_sort,
                             artists_credit=artists_credit)
        except TypeError:
            # beets <1.5.0 uses positional arguments
            return TrackInfo(title, track_id, artist=artist,
                             artist_sort=artist_sort,
                             artist_credit=artist_credit)

    def _create_album_info(self, tracks: [TrackInfo] = None, album: str = None,
                           artist: str = None, artist_sort: str = None,
                           artist_credit: str = None, artists: [str] = None,
                           artists_sort: [str] = None,
                           artists_credit: [str] = None, album_id: str = None,
                           artist_id: str = None):
        album_info = None
        try:
            album_info = AlbumInfo(album=album, album_id=album_id, artist=artist,
                                   artist_id=artist_id, tracks=tracks or [],
                                   artist_sort=artist_sort,
                                   artist_credit=artist_credit,
                                   artists=artists, artists_sort=artists_sort,
                                   artists_credit=artists_credit)
        except TypeError as e:
            # beets <1.5.0 uses positional arguments
            album_info = AlbumInfo(album, album_id, artist, artist_id,
                                   tracks=tracks or [], artist_sort=artist_sort,
                                   artist_credit=artist_credit)
        finally:
            return album_info

    def _add_replacement(self, item_fields: [str] = None,
                         album_fields: [str] = None,
                         replace: {str: str} = None):
        replacement = {}
        if item_fields:
            replacement['item_fields'] = item_fields
        if album_fields:
            replacement['album_fields'] = album_fields
        if replace:
            replacement['replace'] = replace

        beets.config['importreplace']['replacements'] \
            .get(list) \
            .append(replacement)

    def test_replaces_only_config_fields(self):
        """Check if plugin replaces text in only the specified fields"""
        self._add_replacement(item_fields=['title'], album_fields=['album'],
                              replace={'The': 'A'})
        tracks = [self._create_track_info(title='The Piece', artist='The Dude')]
        album_info = self._create_album_info(tracks=tracks, album='The Album',
                                             artist='The Dude',
                                             artists=['The Dude', 'This Artist'])
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'A Album')
        self.assertEqual(album_info.artist, 'The Dude')
        self.assertEqual(album_info.tracks[0].title, 'A Piece')
        self.assertEqual(album_info.tracks[0].artist, 'The Dude')
        self.assertEqual(album_info.artists[0], 'The Dude')
        self.assertEqual(album_info.artists[1], 'This Artist')

    def test_replaces_only_config_fields_multiple(self):
        """Check if plugin replaces text in only the specified fields when
        multiple replacements given."""
        self._add_replacement(item_fields=['title'], album_fields=['album'],
                              replace={'The': 'A'})
        self._add_replacement(item_fields=['artist'],
                              album_fields=['artist', 'artists'],
                              replace={'This': 'That'})
        tracks = [self._create_track_info(title='The Piece', artist='The This')]
        album_info = self._create_album_info(tracks=tracks,
                                             album='The Album',
                                             artist='The This',
                                             artists=['The This', 'This Artist'],
                                             artists_credit=['The This'])
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'A Album')
        self.assertEqual(album_info.artist, 'The That')
        self.assertEqual(album_info.tracks[0].title, 'A Piece')
        self.assertEqual(album_info.tracks[0].artist, 'The That')
        self.assertEqual(album_info.artists[0], 'The That')
        self.assertEqual(album_info.artists[1], 'That Artist')
        self.assertEqual(album_info.artists_credit[0], 'The This')

    def test_handles_empty_fields(self):
        """Verify that plugin works when field marked for replacement
         is absent"""
        self._add_replacement(item_fields=['title', 'artist'],
                              album_fields=['album', 'artist'],
                              replace={'This': 'That'})
        tracks = [self._create_track_info(title='This Piece', artist=None)]
        album_info = self._create_album_info(tracks=tracks, album='This Album',
                                             artist=None)
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'That Album')
        self.assertEqual(album_info.artist, None)
        self.assertEqual(album_info.tracks[0].title, 'That Piece')
        self.assertEqual(album_info.tracks[0].artist, None)

    def test_replaces_in_order(self):
        """Verify that the plugin replaces fields in the order given in the
        config."""
        self._add_replacement(item_fields=['title'], album_fields=['album'],
                              replace={'The': 'This'})
        self._add_replacement(item_fields=['title'], album_fields=['album'],
                              replace={'This': 'That'})
        tracks = [self._create_track_info(title='The Piece', artist='The Dude')]
        album_info = self._create_album_info(tracks=tracks, album='The Album',
                                             artist='The Dude')
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'That Album')
        self.assertEqual(album_info.artist, 'The Dude')
        self.assertEqual(album_info.tracks[0].title, 'That Piece')
        self.assertEqual(album_info.tracks[0].artist, 'The Dude')

    def test_incorrect_field(self):
        """Verify the plugin works when a non-existent field is specified."""
        self._add_replacement(item_fields=['asdf'], album_fields=['asdf'],
                              replace={'This': 'That'})
        tracks = [self._create_track_info(title='The Piece', artist='The Dude')]
        album_info = self._create_album_info(tracks=tracks, album='The Album',
                                             artist='The Dude')
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'The Album')
        self.assertEqual(album_info.artist, 'The Dude')
        self.assertEqual(album_info.tracks[0].title, 'The Piece')
        self.assertEqual(album_info.tracks[0].artist, 'The Dude')

    def test_no_fields(self):
        """Verify the plugin works when item_fields or album_fields not
        given."""
        self._add_replacement(item_fields=['title'],
                              replace={'The': 'A'})
        self._add_replacement(album_fields=['artist'],
                              replace={'This': 'That'})
        tracks = [self._create_track_info(title='The Piece', artist='The This')]
        album_info = self._create_album_info(tracks=tracks,
                                             album='The Album',
                                             artist='The This',
                                             artists=['The Dude', 'This Artist'],
                                             )
        subject = ImportReplace()
        subject._albuminfo_received(album_info)
        self.assertEqual(album_info.album, 'The Album')
        self.assertEqual(album_info.artist, 'The That')
        self.assertEqual(album_info.tracks[0].title, 'A Piece')
        self.assertEqual(album_info.tracks[0].artist, 'The This')
        self.assertEqual(album_info.artists[0], 'The Dude')
        self.assertEqual(album_info.artists[1], 'This Artist')
