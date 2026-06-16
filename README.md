# snip_tool

Lightweight Python snipping tool — quickly capture and save screenshots.

## Description

`snip_tool` is a small, dependency-light Python utility for capturing screenshots and saving them to disk. It's designed for quick use on a developer workstation: run `snip_tool.py` to select and save a region with minimal fuss, or package the app into a single executable using the provided `snip_tool.spec`.

## Features

- Fast, minimal UI for selecting and saving screen regions
- Easy to package with PyInstaller
- Small, single-file script ideal for personal workflows

## Requirements

- Python 3.8 or newer
- (Optional) `pyinstaller` to build an executable: `pip install pyinstaller`

## Quick start

Run directly with Python:

```bash
python snip_tool.py
```

Build a distributable with PyInstaller (uses `snip_tool.spec`):

```bash
pyinstaller --clean --noconfirm snip_tool.spec
```

The built artifacts will appear in the `dist/` directory.

## Development

- Edit `snip_tool.py` to change behavior or add features.
- If PyInstaller misses an import at runtime, add it to the `hiddenimports` list in `snip_tool.spec`.

## Files

- `snip_tool.py` — main script
- `snip_tool.spec` — PyInstaller spec used to build the exe

## License

MIT — see LICENSE (or add a LICENSE file to the repo to make this explicit).
