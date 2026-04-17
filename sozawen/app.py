"""Sozawen — The Burn That Flows

A bandmate who listens. Built by a musician, for musicians.
One-time purchase. No subscription. No cloud. No tracking.

Entry point: starts the pywebview desktop window with the Sozawen UI.
"""

import sys
import os
import json
import logging
import threading
from pathlib import Path

# App paths
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
ASSETS_DIR = BASE_DIR / "assets"
SETTINGS_PATH = BASE_DIR / "settings.json"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("sozawen")

# Settings
SETTINGS = {}
if SETTINGS_PATH.exists():
    try:
        SETTINGS = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
    except:
        pass

def save_settings():
    SETTINGS_PATH.write_text(json.dumps(SETTINGS, indent=2), encoding='utf-8')


# ═══════════════════════════════════════════════════════════════════
# API — FastAPI backend for the UI
# ═══════════════════════════════════════════════════════════════════

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

api = FastAPI(title="Sozawen", docs_url=None, redoc_url=None)
api.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ═══════════════════════════════════════════════════════════════════
# AUDIO ENGINE — singleton, persists across requests
# ═══════════════════════════════════════════════════════════════════
from sozawen.audio_engine import AudioEngine
from sozawen.context import ContextEngine

_engine = AudioEngine(sample_rate=44100, buffer_size=1024)
_engine.start()
_context = ContextEngine()


@api.get("/api/status")
async def status():
    """System status — GPU availability, loaded models, version."""
    import torch
    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    gpu_vram = torch.cuda.get_device_properties(0).total_memory / 1e9 if gpu_available else 0

    return JSONResponse({
        "version": SETTINGS.get("version", "0.1.0"),
        "gpu": gpu_available,
        "gpu_name": gpu_name,
        "gpu_vram_gb": round(gpu_vram, 1),
        "models_loaded": list(_loaded_models.keys()),
        "engine": _engine.get_state(),
    })


# ═══════════════════════════════════════════════════════════════════
# TRANSPORT + TRACK API — connects UI to audio engine
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/transport/play")
async def transport_play():
    _engine.play()
    return JSONResponse({"ok": True, "playing": True})

@api.post("/api/transport/pause")
async def transport_pause():
    _engine.pause()
    return JSONResponse({"ok": True, "playing": False})

@api.post("/api/transport/stop")
async def transport_stop():
    _engine.stop_transport()
    return JSONResponse({"ok": True})

@api.post("/api/transport/seek")
async def transport_seek(request: Request):
    data = await request.json()
    seconds = data.get("seconds", 0)
    _engine.seek_seconds(seconds)
    return JSONResponse({"ok": True, "position": _engine.get_position_seconds()})

@api.get("/api/transport/state")
async def transport_state():
    return JSONResponse(_engine.get_state())

@api.get("/api/context")
async def get_context():
    """Get the adaptive context — what tools should be visible right now."""
    engine_state = _engine.get_state()
    return JSONResponse(_context.update(engine_state))

@api.post("/api/context/action")
async def report_action(request: Request):
    """Tell the context engine what the user just did."""
    data = await request.json()
    action = data.get("action", "none")
    engine_state = _engine.get_state()
    return JSONResponse(_context.update(engine_state, action=action))

@api.post("/api/track/add")
async def api_add_track(request: Request):
    data = await request.json()
    name = data.get("name", "")
    file_path = data.get("file_path", "")
    track = _engine.add_track(name=name)
    if file_path and Path(file_path).exists():
        track.add_region(file_path, source_type="imported")
    return JSONResponse({"ok": True, "track_id": track.id, "name": track.name})

@api.post("/api/track/{track_id}/volume")
async def set_track_volume(track_id: int, request: Request):
    data = await request.json()
    track = _engine.tracks.get(track_id)
    if track:
        track.volume = data.get("volume", 1.0)
        return JSONResponse({"ok": True})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/mute")
async def toggle_track_mute(track_id: int):
    track = _engine.tracks.get(track_id)
    if track:
        track.muted = not track.muted
        return JSONResponse({"ok": True, "muted": track.muted})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/solo")
async def toggle_track_solo(track_id: int):
    track = _engine.tracks.get(track_id)
    if track:
        track.solo = not track.solo
        return JSONResponse({"ok": True, "solo": track.solo})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.get("/api/waveform/{track_id}")
async def get_waveform(track_id: int, width: int = 0):
    """Get waveform peaks for a track. Width param controls peak density."""
    import numpy as np
    track = _engine.tracks.get(track_id)
    if not track or not track.regions:
        return JSONResponse({"peaks": []})

    # Merge all regions' audio
    all_audio = []
    source_type = "imported"
    for region in track.regions:
        region._ensure_cached()
        if region._cache is not None:
            all_audio.append(region._cache)
            source_type = region.source_type

    if not all_audio:
        return JSONResponse({"peaks": []})

    # Concatenate all regions
    audio = np.concatenate(all_audio, axis=0)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    duration = len(audio) / track.regions[0].sample_rate

    # Generate enough peaks to fill the requested width, or default to duration * 10
    target_peaks = width if width > 0 else max(2000, int(duration * 10))
    chunk_size = max(1, len(audio) // target_peaks)
    peaks = []
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        peaks.append({
            "min": float(np.min(chunk)),
            "max": float(np.max(chunk)),
        })

    return JSONResponse({
        "peaks": peaks,
        "duration": duration,
        "sample_rate": track.regions[0].sample_rate,
        "source_type": source_type,
    })


# ═══════════════════════════════════════════════════════════════════
# AUDIO EFFECTS API — all backed by pedalboard/scipy
# ═══════════════════════════════════════════════════════════════════

from sozawen.audio_fx import (apply_noise_gate, apply_eq, apply_compressor,
    apply_reverb, apply_delay, apply_limiter, apply_hum_removal,
    apply_deesser, apply_normalize, measure_loudness, export_mix)
@api.post("/api/project/save")
async def save_project(request: Request):
    """Save the current project state."""
    data = await request.json()
    project_dir = BASE_DIR / "projects"
    project_dir.mkdir(exist_ok=True)
    from datetime import datetime
    filename = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = project_dir / filename
    filepath.write_text(json.dumps(data, indent=2), encoding='utf-8')
    # Also save as "last_session.json" for crash recovery
    (project_dir / "last_session.json").write_text(json.dumps(data, indent=2), encoding='utf-8')
    return JSONResponse({"ok": True, "path": str(filepath)})

@api.get("/api/project/recover")
async def recover_project():
    """Check for a recoverable session from last crash."""
    project_dir = BASE_DIR / "projects"
    last = project_dir / "last_session.json"
    if last.exists():
        try:
            data = json.loads(last.read_text(encoding='utf-8'))
            return JSONResponse({"available": True, "project": data})
        except:
            pass
    return JSONResponse({"available": False})

from sozawen.editing import (detect_channels, split_channels, split_region_at_sample,
    generate_click_track, detect_silence, detect_transients)


# ═══════════════════════════════════════════════════════════════════
# EDITING API
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/edit/split")
async def split_at_position(request: Request):
    """Split a track's region at the current playhead position."""
    data = await request.json()
    track_id = data.get("track_id")
    position = data.get("position", _engine.position)  # sample position

    track = _engine.tracks.get(track_id)
    if not track:
        # Try first track
        track = next(iter(_engine.tracks.values()), None)
    if not track or not track.regions:
        return JSONResponse({"error": "No track to split"}, status_code=400)

    from sozawen.audio_engine import Region
    results = []
    new_regions = []
    for region in track.regions:
        split = split_region_at_sample(region, position)
        if split:
            left, right = split
            new_regions.append(Region(**left))
            new_regions.append(Region(**right))
            results.append({"split_at": position, "left": left["name"], "right": right["name"]})
        else:
            new_regions.append(region)

    track.regions = new_regions
    return JSONResponse({"ok": True, "splits": results})

@api.post("/api/edit/detect-channels")
async def api_detect_channels(request: Request):
    """Detect channel count and info for an audio file."""
    data = await request.json()
    file_path = data.get("file_path", "")
    track_id = data.get("track_id")

    if not file_path and track_id is not None:
        track = _engine.tracks.get(track_id)
        if track and track.regions:
            file_path = track.regions[0].source_path

    if not file_path:
        return JSONResponse({"error": "No file specified"}, status_code=400)

    info = detect_channels(file_path)
    return JSONResponse(info)

@api.post("/api/edit/split-channels")
async def api_split_channels(request: Request):
    """Split a multi-channel file into individual tracks."""
    import asyncio
    data = await request.json()
    file_path = data.get("file_path", "")
    track_id = data.get("track_id")

    if not file_path and track_id is not None:
        track = _engine.tracks.get(track_id)
        if track and track.regions:
            file_path = track.regions[0].source_path

    if not file_path:
        return JSONResponse({"error": "No file specified"}, status_code=400)

    # Detect first
    info = detect_channels(file_path)
    channels = info.get("channels", 1)

    if channels <= 1:
        return JSONResponse({"message": "File is mono — nothing to split", "channels": 1})

    # Split
    results = await asyncio.get_event_loop().run_in_executor(
        None, lambda: split_channels(file_path))

    # Create tracks for each channel
    for ch_info in results:
        track = _engine.add_track(name=ch_info["name"])
        track.add_region(ch_info["path"], source_type="imported")

    return JSONResponse({"ok": True, "channels": len(results), "tracks": [r["name"] for r in results]})

@api.post("/api/edit/detect-silence")
async def api_detect_silence(request: Request):
    """Find silent sections in audio."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")
    threshold = data.get("threshold_db", -40)

    track = _engine.tracks.get(track_id) if track_id is not None else next(iter(_engine.tracks.values()), None)
    if not track or not track.regions:
        return JSONResponse({"error": "No audio loaded"}, status_code=400)

    regions = await asyncio.get_event_loop().run_in_executor(
        None, lambda: detect_silence(track.regions[0].source_path, threshold_db=threshold))
    return JSONResponse({"silent_regions": regions, "count": len(regions)})

@api.post("/api/edit/detect-transients")
async def api_detect_transients(request: Request):
    """Find transient/attack points in audio."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")
    sensitivity = data.get("sensitivity", 0.5)

    track = _engine.tracks.get(track_id) if track_id is not None else next(iter(_engine.tracks.values()), None)
    if not track or not track.regions:
        return JSONResponse({"error": "No audio loaded"}, status_code=400)

    transients = await asyncio.get_event_loop().run_in_executor(
        None, lambda: detect_transients(track.regions[0].source_path, sensitivity))
    return JSONResponse({"transients": transients, "count": len(transients)})

@api.post("/api/edit/count-in")
async def api_generate_count_in(request: Request):
    """Generate a count-in click and play it before recording starts."""
    data = await request.json()
    bars = data.get("bars", 1)
    bpm = data.get("bpm", _engine.bpm)

    click_audio = generate_click_track(bpm, 0, _engine.sample_rate,
                                        count_in_bars=bars)
    # Save to temp and play
    import tempfile
    tmp = Path(tempfile.mktemp(suffix=".wav", prefix="countin_"))
    sf.write(str(tmp), click_audio, _engine.sample_rate)

    return JSONResponse({
        "ok": True,
        "path": str(tmp),
        "duration": len(click_audio) / _engine.sample_rate,
        "beats": bars * _engine.time_sig_num,
    })

@api.post("/api/fx/apply")
async def apply_effect(request: Request):
    """Apply an audio effect to a track. Non-destructive — creates a new file."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id", 0)
    effect = data.get("effect", "")
    params = data.get("params", {})

    track = _engine.tracks.get(track_id)
    if not track or not track.regions:
        return JSONResponse({"error": "No track or audio loaded"}, status_code=400)

    source_path = track.regions[0].source_path

    fx_map = {
        "noise_gate": lambda: apply_noise_gate(source_path, **params),
        "eq": lambda: apply_eq(source_path, **params),
        "compressor": lambda: apply_compressor(source_path, **params),
        "reverb": lambda: apply_reverb(source_path, **params),
        "delay": lambda: apply_delay(source_path, **params),
        "limiter": lambda: apply_limiter(source_path, **params),
        "hum_remove": lambda: apply_hum_removal(source_path, **params),
        "de_ess": lambda: apply_deesser(source_path, **params),
        "normalize": lambda: apply_normalize(source_path, **params),
    }

    if effect not in fx_map:
        return JSONResponse({"error": f"Unknown effect: {effect}"}, status_code=400)

    try:
        output_path = await asyncio.get_event_loop().run_in_executor(None, fx_map[effect])
        # Replace the track's audio with the processed version
        track.regions[0] = track.regions[0].__class__(
            output_path, source_type="processed", name=f"{track.name} ({effect})")
        track.regions[0]._cache = None  # force reload
        return JSONResponse({"ok": True, "output": output_path, "effect": effect})
    except Exception as e:
        logger.error("FX apply failed: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/fx/measure")
async def measure_audio(request: Request):
    """Measure loudness (LUFS, true peak, dynamic range)."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id", 0)

    track = _engine.tracks.get(track_id)
    if not track or not track.regions:
        return JSONResponse({"error": "No audio loaded"}, status_code=400)

    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: measure_loudness(track.regions[0].source_path))
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/export")
async def export_audio(request: Request):
    """Export the mix to a file."""
    data = await request.json()
    format = data.get("format", "wav")
    sample_rate = data.get("sample_rate", 44100)

    # Collect all track audio
    tracks_audio = []
    for track in _engine.tracks.values():
        if track.muted or track.track_type in ("bus", "master"):
            continue
        for region in track.regions:
            region._ensure_cached()
            if region._cache is not None:
                audio = region._cache * track.volume
                tracks_audio.append(audio)

    if not tracks_audio:
        return JSONResponse({"error": "No audio to export"}, status_code=400)

    output_path = str(Path.home() / "Music" / f"sozawen_export.{format}")
    try:
        result = export_mix(tracks_audio, output_path, format=format, sample_rate=sample_rate)
        return JSONResponse({"ok": True, "path": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# INPUT DEVICES — for recording
# ═══════════════════════════════════════════════════════════════════

@api.get("/api/input-devices")
async def list_input_devices():
    """List available audio input devices for recording."""
    import sounddevice as sd
    devices = []
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            devices.append({
                "id": i,
                "name": d['name'],
                "channels": d['max_input_channels'],
                "sample_rate": int(d['default_samplerate']),
            })
    return JSONResponse({"devices": devices})

@api.post("/api/record/start")
async def start_recording(request: Request):
    """Start recording on an armed track."""
    data = await request.json()
    device_id = data.get("device_id")
    track_id = data.get("track_id")

    if device_id is not None:
        import sounddevice as sd
        sd.default.device[0] = int(device_id)

    if track_id is not None:
        _engine.record(track_id)
    else:
        # Arm first track or create one
        if not _engine.tracks:
            track = _engine.add_track("Recording", track_type="audio")
            track.record_armed = True
        _engine.record()

    return JSONResponse({"ok": True, "recording": True})

@api.post("/api/record/stop")
async def stop_recording():
    """Stop recording and finalize the audio."""
    _engine.stop_recording()
    state = _engine.get_state()
    return JSONResponse({"ok": True, "state": state})


# ═══════════════════════════════════════════════════════════════════
# MODEL MANAGEMENT — lazy load, GPU/CPU auto
# ═══════════════════════════════════════════════════════════════════

_loaded_models = {}
_model_lock = threading.Lock()

# Pre-load heavy imports in background so first use doesn't hang
def _preload_libs():
    import time
    time.sleep(1)
    logger.info("Pre-loading audio libraries...")
    try:
        import librosa
        import numpy
        import soundfile
        logger.info("Audio libraries ready")
    except Exception as e:
        logger.warning("Pre-load: %s", e)
threading.Thread(target=_preload_libs, daemon=True, name="preload").start()


def get_device():
    """Get the best available device."""
    import torch
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def get_demucs_model(quality="high"):
    """Load or return cached Demucs stem separation model."""
    key = f"demucs_{quality}"
    if key in _loaded_models:
        return _loaded_models[key]

    with _model_lock:
        if key in _loaded_models:
            return _loaded_models[key]

        logger.info("Loading Demucs model (quality=%s)...", quality)
        try:
            from demucs.pretrained import get_model
            import torch

            model_names = {
                "high": "htdemucs_ft",    # 4-stem, best quality
                "fast": "htdemucs",        # 4-stem, faster
                "6stem": "htdemucs_6s",    # 6-stem (adds guitar + piano)
            }
            model_name = model_names.get(quality, "htdemucs_ft")
            model = get_model(model_name)

            # Try GPU, fall back to CPU if VRAM is full
            device = "cpu"
            if torch.cuda.is_available():
                free_vram = (torch.cuda.get_device_properties(0).total_memory
                           - torch.cuda.memory_allocated(0)) / 1e9
                if free_vram > 2.0:  # need at least 2GB for Demucs
                    device = "cuda"
                    model = model.to(device)
                    logger.info("Demucs on GPU (%.1fGB free)", free_vram)
                else:
                    logger.info("GPU busy (%.1fGB free) — Demucs on CPU (slower but works)", free_vram)

            _loaded_models[key] = (model, device)
            logger.info("Demucs loaded on %s", device)
            return model, device
        except Exception as e:
            logger.error("Failed to load Demucs: %s", e)
            return None, "cpu"

def get_whisper_model(size="base"):
    """Load or return cached Whisper model for lyric transcription."""
    key = f"whisper_{size}"
    if key in _loaded_models:
        return _loaded_models[key]

    with _model_lock:
        if key in _loaded_models:
            return _loaded_models[key]

        logger.info("Loading Whisper %s...", size)
        try:
            from faster_whisper import WhisperModel
            device = get_device()
            compute = "float16" if device == "cuda" else "int8"
            model = WhisperModel(size, device=device, compute_type=compute)
            _loaded_models[key] = model
            logger.info("Whisper %s loaded on %s", size, device)
            return model
        except Exception as e:
            logger.error("Failed to load Whisper: %s", e)
            return None


# ═══════════════════════════════════════════════════════════════════
# STEM SEPARATION
# ═══════════════════════════════════════════════════════════════════

_active_jobs = {}

@api.post("/api/separate")
async def separate_stems(request: Request):
    """Start stem separation on an audio file."""
    data = await request.json()
    file_path = data.get("file_path", "")
    quality = data.get("quality", "high")  # "high" or "fast"
    stems = data.get("stems", 4)  # 2 or 4

    if not file_path or not Path(file_path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)

    job_id = str(__import__('uuid').uuid4())[:8]
    _active_jobs[job_id] = {"status": "starting", "progress": 0, "file": file_path}

    def _run_separation():
        try:
            _active_jobs[job_id]["status"] = "loading_model"
            model, device = get_demucs_model(quality)
            if model is None:
                _active_jobs[job_id] = {"status": "error", "error": "Could not load model"}
                return

            _active_jobs[job_id]["status"] = "separating"
            _active_jobs[job_id]["progress"] = 10

            import torch
            import soundfile as _sf
            import numpy as np
            from demucs.apply import apply_model

            # Load audio with soundfile (avoids torchcodec issues)
            audio_np, sr = _sf.read(file_path, dtype='float32')
            if audio_np.ndim == 1:
                audio_np = np.column_stack([audio_np, audio_np])
            # Convert to torch: (channels, samples)
            wav = torch.from_numpy(audio_np.T).unsqueeze(0)  # (1, channels, samples)

            if device == "cuda":
                wav = wav.to(device)

            _active_jobs[job_id]["progress"] = 20

            # Separate
            with torch.no_grad():
                sources = apply_model(model, wav, device=device,
                                     progress=True, num_workers=0)

            _active_jobs[job_id]["progress"] = 80

            # Save stems with soundfile
            # Determine source names based on model
            if quality == "6stem":
                source_names = ["drums", "bass", "other", "vocals", "guitar", "piano"]
            else:
                source_names = ["drums", "bass", "other", "vocals"]

            output_dir = Path(file_path).parent / f"{Path(file_path).stem}_stems"
            output_dir.mkdir(exist_ok=True)

            stem_files = []
            n_sources = sources.shape[1]  # actual number of sources from model

            for i in range(min(n_sources, len(source_names))):
                name = source_names[i]
                if stems == 2 and name not in ("vocals",):
                    continue
                stem_path = output_dir / f"{name}.wav"
                stem_audio = sources[0, i].cpu().numpy().T
                _sf.write(str(stem_path), stem_audio, sr)
                stem_files.append({"name": name, "path": str(stem_path)})

            if stems == 2:
                # Combine everything except vocals as instrumental
                non_vocal = sum(sources[0, i] for i in range(n_sources) if source_names[i] != "vocals")
                inst_path = output_dir / "instrumental.wav"
                _sf.write(str(inst_path), non_vocal.cpu().numpy().T, sr)
                stem_files.append({"name": "instrumental", "path": str(inst_path)})

            _active_jobs[job_id] = {
                "status": "complete",
                "progress": 100,
                "stems": stem_files,
                "output_dir": str(output_dir),
            }
            logger.info("Separation complete: %s → %d stems", file_path, len(stem_files))

        except Exception as e:
            logger.error("Separation failed: %s", e)
            _active_jobs[job_id] = {"status": "error", "error": str(e)}

    threading.Thread(target=_run_separation, daemon=True, name=f"sep-{job_id}").start()
    return JSONResponse({"job_id": job_id, "status": "started"})


@api.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a processing job."""
    job = _active_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return JSONResponse(job)


# ═══════════════════════════════════════════════════════════════════
# LYRIC TRANSCRIPTION
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/transcribe-lyrics")
async def transcribe_lyrics(request: Request):
    """Transcribe lyrics from a vocal track."""
    data = await request.json()
    file_path = data.get("file_path", "")
    language = data.get("language", "en")

    if not file_path or not Path(file_path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)

    model = get_whisper_model("base")
    if model is None:
        return JSONResponse({"error": "Could not load Whisper"}, status_code=500)

    try:
        segments, info = model.transcribe(file_path, language=language,
                                           word_timestamps=True)
        lyrics = []
        for seg in segments:
            entry = {
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            }
            if seg.words:
                entry["words"] = [
                    {"word": w.word, "start": round(w.start, 2),
                     "end": round(w.end, 2), "confidence": round(w.probability, 3)}
                    for w in seg.words
                ]
            lyrics.append(entry)

        return JSONResponse({
            "lyrics": lyrics,
            "full_text": " ".join(l["text"] for l in lyrics),
            "language": info.language,
            "duration": round(info.duration, 2),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# AUDIO ANALYSIS
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/analyze")
async def analyze_audio(request: Request):
    """Analyze audio: key, BPM, loudness, spectrum. Runs in thread pool to avoid blocking."""
    data = await request.json()
    file_path = data.get("file_path", "")

    if not file_path or not Path(file_path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)

    import asyncio

    def _analyze():
        import librosa
        import numpy as np

        y, sr = librosa.load(file_path, sr=None, duration=300)  # cap at 5 min for speed
        duration = len(y) / sr

        # BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo) if not hasattr(tempo, '__len__') else float(tempo[0])

        # Key detection
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_strengths = chroma.mean(axis=1)
        detected_key = key_names[int(np.argmax(key_strengths))]

        # Loudness (RMS and peak)
        rms = float(np.sqrt(np.mean(y ** 2)))
        peak = float(np.max(np.abs(y)))
        rms_db = float(20 * np.log10(rms + 1e-10))
        peak_db = float(20 * np.log10(peak + 1e-10))

        return {
            "duration": round(duration, 2),
            "bpm": round(bpm, 1),
            "key": detected_key,
            "rms_db": round(rms_db, 1),
            "peak_db": round(peak_db, 1),
            "sample_rate": sr,
            "channels": 1 if y.ndim == 1 else y.shape[0],
        }

    try:
        result = await asyncio.get_event_loop().run_in_executor(None, _analyze)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# MAIN — Desktop window
# ═══════════════════════════════════════════════════════════════════

_window = None  # global reference for API access

# File picker endpoint — avoids pywebview JS API timing issues
@api.get("/api/pick-file")
async def pick_file_endpoint():
    """Open native file picker via tkinter (works without pywebview window)."""
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _open_file_dialog)
    if result:
        return JSONResponse({"path": result})
    return JSONResponse({"path": None})


def _open_file_dialog():
    """Run tkinter file dialog in a thread (must not block async loop)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askopenfilename(
            title="Open Audio File",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.flac *.ogg *.aiff *.m4a *.wma"),
                ("All Files", "*.*"),
            ]
        )
        root.destroy()
        return path if path else None
    except Exception as e:
        logger.error(f"File dialog error: {e}")
        return None


def main():
    global _window
    import webview
    import uvicorn

    # Start API server in background
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(api, host="127.0.0.1", port=8090, log_level="warning"),
        daemon=True
    )
    server_thread.start()

    import time
    time.sleep(1)

    # Create native window
    _window = webview.create_window(
        "Sozawen — Born from the burn. Built by feeling.",
        url="http://127.0.0.1:8090/static/index.html",
        width=1280,
        height=820,
        min_size=(960, 640),
        background_color="#0d0d1a",
        frameless=False,
        easy_drag=True,
        text_select=False,
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
