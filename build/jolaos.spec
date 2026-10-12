# -*- mode: python ; coding: utf-8 -*-
# Budowanie: python -m PyInstaller build/jolaos.spec --noconfirm

from pathlib import Path

ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / "run_jolaos.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "build" / "jolaos.ico"), "build"),
        (str(ROOT / "build" / "jolaos.png"), "build"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["unittest", "pydoc", "doctest", "xmlrpc", "test"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Jolaos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "build" / "jolaos.ico"),
    uac_admin=True,
    version=str(ROOT / "build" / "version_info.txt"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Jolaos",
)
