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

## Configuration

To configure the plugin, add a `importreplace:` configuration block in your
beets `config.yaml` file. This example configuration replaces Unicode
apostrophes, quotes and hyphen used by MusicBrainz with their ASCII
counterparts.

```yaml
importreplace:
    item_fields: title artist artist_sort artist_credit
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

## Installation

Install the plugin using `pip`:
```shell
pip install git+git://github.com/edgars-supe/beets-importreplace.git
```
Then, [configure](#configuration) the plugin in your
[`config.yaml`](https://beets.readthedocs.io/en/latest/plugins/index.html) file.
