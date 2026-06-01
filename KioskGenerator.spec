# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['factory.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('favicon.ico', '.'),
        ('agerit_logo.png', '.'),
        ('emistr_logo.png', '.'),
        ('dist/browser_engine.exe', '.')
    ],
    hiddenimports=['tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KioskGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['favicon.ico'],
)
