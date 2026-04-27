# wavtag

A CLI tool for batch editing and normalizing metadata tags across audio file collections.

---

## Installation

```bash
pip install wavtag
```

Or install from source:

```bash
git clone https://github.com/yourusername/wavtag.git
cd wavtag && pip install .
```

---

## Usage

```bash
# View tags for all audio files in a directory
wavtag inspect ./music

# Batch set artist and album tags
wavtag set --artist "Unknown Artist" --album "My Album" ./music/*.mp3

# Normalize tags across a collection (trim whitespace, fix casing)
wavtag normalize ./music

# Copy tags from one file to another
wavtag copy source.flac target.wav
```

Run `wavtag --help` to see all available commands and options.

---

## Supported Formats

- MP3, FLAC, WAV, AIFF, OGG

---

## License

This project is licensed under the [MIT License](LICENSE).