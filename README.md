# ImportReplace

A plugin for [beets](https://github.com/beetbox/beets) to perform regex
replacements during import.

It works on metadata in `AlbumInfo` and `TrackInfo` objects as they come in.
Running many replacements (or on many fields) might negatively impact import
performance.

A good usecase for this plugin is replacing the Unicode apostrophes, quotation
marks and hyphens used by MusicBrainz with their ASCII counterparts. The
built-in [`replace`](https://beets.readthedocs.io/en/stable/reference/config.html#replace)
configuration won't work for this, because it only acts on filenames.

## Installation

Install the plugin using `pip`:

```shell
pip install git+https://github.com/edgars-supe/beets-importreplace.git
```

Then, [configure](#configuration) the plugin in your
[`config.yaml`](https://beets.readthedocs.io/en/latest/plugins/index.html) file.

## Configuration

First, add `importreplace` to your list of enabled plugins.

```yaml
plugins: importreplace
```

Then, add a `importreplace:` configuration block in your beets `config.yaml`
file. Add one or more replacement configurations under `replacements:` This
example configuration replaces Unicode apostrophes, quotes and hyphen used by
MusicBrainz with their ASCII counterparts.

```yaml
importreplace:
  replacements:
    - item_fields: title artist artist_sort artist_credit
      album_fields: album artist artist_sort artist_credit
      replace:
        '[\u2018-\u201B]': ''''
        '[\u201C-\u201F]': '"'
        '[\u2010-\u2015]': '-'
```

* `item_fields` is a set of fields to run replacements on for items
* `album_fields` is a set of fields to run replacements on for albums
* `replace` is a set of regex/replacement pairs

That's about it.

You can add more replacement configurations for different fields. For example,
to replace certain strings only for tracks, but different strings only for
albums.

```yaml
importreplace:
  replacements:
    - item_fields: title
      replace:
        'The': 'That'
    - item_fields: album
      album_fields: album
      replace:
        'Foo': 'Bar'
```

This config will convert

```
Artist - The Fighters of Foo/Artist - The Foo Song
```

into

```
Artist - The Fighters of Bar/Artist - That Foo Song
```
