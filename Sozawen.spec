# -*- mode: python ; coding: utf-8 -*-
"""Sozawen PyInstaller spec — Born from the burn. Built by feeling.

Core DAW ships lean (~300MB). AI features (stem separation, lyrics)
download their models on first use via the smart loader.
"""

import sys
from pathlib import Path

block_cipher = None
BASE = Path('.').resolve()

# Core dependencies only — no torch, no demucs, no whisper in the base install
# Those are loaded dynamically and download models on first use
a = Analysis(
    ['sozawen/__main__.py'],
    pathex=[str(BASE)],
    binaries=[],
    datas=[
        ('static', 'static'),
    ],
    hiddenimports=[
        'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
        'fastapi', 'starlette', 'anyio', 'anyio._backends', 'anyio._backends._asyncio',
        'sounddevice', 'soundfile',
        # pedalboard REMOVED — GPL-3.0, replaced with pure scipy/numpy DSP
        'numpy', 'scipy', 'scipy.signal',
        'librosa', 'librosa.core', 'librosa.feature', 'librosa.beat',
        'librosa.effects', 'librosa.onset',
        'pyloudnorm',
        'webview',
        'tkinter', 'tkinter.filedialog',
        'pydub',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchaudio', 'torchvision',  # AI pack, not base
        'demucs',  # AI pack
        'faster_whisper', 'ctranslate2',  # AI pack
        'matplotlib', 'IPython', 'jupyter',
        'pytest', 'setuptools', 'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Sozawen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # windowed app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/sozawen.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Sozawen',
)
