# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None


a = Analysis([
    'snip_tool.py',
],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='snip_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='snip_tool',
)

# Notes:
# - If your app includes non-Python files (images, data, configs), add them to `datas`.
# - If PyInstaller misses imports at runtime, list them in `hiddenimports`.
# - To build a windowed app (no console), set `console=False` in `EXE` above.
# Build with: `pyinstaller --clean --noconfirm snip_tool.spec`
