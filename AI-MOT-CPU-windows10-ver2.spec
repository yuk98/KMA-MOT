# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['AI-MOT-CPU-windows10-ver2.py'],
    pathex=[],
    binaries=[],
    datas=[('Z:/anaconda3/envs/surv/lib/site-packages/ultralytics/', 'ultralytics/')],
    hiddenimports=[],
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
    name='KMA-MOT',
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
    icon=['Z:\\workspace\\AI-MOT\\asset\\kma.ico'],
)
