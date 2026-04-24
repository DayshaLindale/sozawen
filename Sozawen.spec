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
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# llama-cpp-python ships compiled DLLs in llama_cpp/lib/ that PyInstaller's
# hiddenimport alone doesn't pull. Collect them explicitly.
_llama_binaries = collect_dynamic_libs('llama_cpp')
_llama_datas = collect_data_files('llama_cpp')

a = Analysis(
    ['sozawen/__main__.py'],
    pathex=[str(BASE)],
    binaries=_llama_binaries,
    datas=[
        ('static', 'static'),
        # Bundle the Bandmate GGUF so users never have to download it.
        # ~1.1GB model — installer grows but there's zero "bully download"
        # after install.
        ('models', 'models'),
    ] + _llama_datas,
    hiddenimports=[
        'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
        'fastapi', 'fastapi.responses', 'fastapi.routing',
        'starlette', 'starlette.responses', 'starlette.routing',
        'starlette.middleware', 'starlette.staticfiles', 'starlette.requests',
        'anyio', 'anyio._backends', 'anyio._backends._asyncio',
        'sounddevice', 'soundfile', '_soundfile_data',
        'numpy', 'scipy', 'scipy.signal', 'scipy.interpolate', 'scipy.ndimage',
        'librosa', 'librosa.core', 'librosa.feature', 'librosa.beat',
        'librosa.effects', 'librosa.onset', 'librosa.util',
        'pyloudnorm',
        'pedalboard',
        'PIL', 'PIL.Image',
        'llama_cpp', 'llama_cpp.llama',
        'music21', 'music21.stream', 'music21.note', 'music21.chord',
        'music21.meter', 'music21.key', 'music21.tempo', 'music21.converter',
        'webview', 'webview.platforms', 'webview.platforms.edgechromium',
        'tkinter', 'tkinter.filedialog',
        'pydub',
        'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna',
        'soundfile',
        'json', 'hashlib', 'subprocess',
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
