# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['AI-MOT-CPU-windows10-ver2.py'],
    pathex=[],
    binaries=[],
    datas=[('Z:\\anaconda3\\envs\\surv\\lib/site-packages\\ultralytics\\', 'ultralytics\\')],
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
    [],
    exclude_binaries=True,
    name='AI-MOT-GPU-windows10ver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Z:\\workspace\\AI-MOT\\asset\\kma.ico'
    )
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='육사-MOT',
)
