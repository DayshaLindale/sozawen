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
import soundfile as sf
from pathlib import Path

# App paths — handle both dev and PyInstaller frozen builds
import sys
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
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

# Clean shutdown — stop audio when the program closes
import atexit

def _cleanup():
    try:
        _engine.stop()
    except Exception:
        pass

atexit.register(_cleanup)

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

# Clean temp directory on startup — no stale renders from previous sessions
_temp_dir = BASE_DIR / "temp"
_temp_dir.mkdir(exist_ok=True)
for _f in _temp_dir.glob("drums_*.wav"):
    try: _f.unlink()
    except: pass
for _f in _temp_dir.glob("inst_*.wav"):
    try: _f.unlink()
    except: pass


@api.get("/api/status")
async def status():
    """System status — GPU availability, loaded models, version."""
    gpu_available = False
    gpu_name = None
    gpu_vram = 0
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
        gpu_vram = torch.cuda.get_device_properties(0).total_memory / 1e9 if gpu_available else 0
    except ImportError:
        pass  # torch not installed — core DAW works without it

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
    # Respect the current loop state — don't force it
    _engine.play()
    return JSONResponse({"ok": True, "playing": True, "looping": _engine.looping})

@api.post("/api/transport/pause")
async def transport_pause():
    _engine.pause()
    return JSONResponse({"ok": True, "playing": False})

@api.post("/api/transport/stop")
async def transport_stop():
    _engine.stop_transport()
    return JSONResponse({"ok": True})

@api.post("/api/transport/metronome-subdiv")
async def metronome_subdivision(request: Request):
    """Set metronome subdivision — quarter, eighth, sixteenth, triplet."""
    data = await request.json()
    subdiv = int(data.get("subdivision", 1))
    _engine.metronome_subdivision = max(1, min(4, subdiv))
    return JSONResponse({"ok": True, "subdivision": _engine.metronome_subdivision})

@api.post("/api/transport/speed")
async def transport_speed(request: Request):
    """Set playback speed for practice mode."""
    data = await request.json()
    rate = float(data.get("rate", 1.0))
    _engine.playback_rate = max(0.25, min(2.0, rate))
    return JSONResponse({"ok": True, "rate": _engine.playback_rate})

@api.post("/api/track/{track_id}/duplicate")
async def duplicate_track(track_id: int, request: Request):
    """Duplicate a track with all its regions."""
    data = await request.json()
    offset_seconds = data.get("offset_seconds", 0)
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    src = _engine.tracks[track_id]
    new_track = _engine.add_track(name=f"{src.name} (copy)")
    for region in src.regions:
        offset = region.track_offset + int(offset_seconds * 44100)
        new_track.add_region(region.source_path, track_offset=offset, source_type=region.source_type)
    return JSONResponse({"ok": True, "track_id": new_track.id})

@api.post("/api/track/{track_id}/freeze")
async def freeze_track(track_id: int):
    """Freeze/bounce a track — render with effects in place."""
    import numpy as np
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    track = _engine.tracks[track_id]
    try:
        # Render the track's audio to a new file
        duration = track.duration_samples
        if duration <= 0:
            return JSONResponse({"error": "Empty track"}, status_code=400)
        audio = np.zeros((duration, 2), dtype=np.float64)
        for region in track.regions:
            chunk = region.read(0, duration)
            if chunk is not None and len(chunk) > 0:
                end = min(len(chunk), duration)
                if chunk.ndim == 1:
                    audio[:end, 0] += chunk[:end]
                    audio[:end, 1] += chunk[:end]
                else:
                    audio[:end] += chunk[:end]
        audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
        import time as _time
        output_path = str(BASE_DIR / "temp" / f"frozen_{track.name}_{int(_time.time())}.wav")
        sf.write(output_path, audio, 44100)
        # Replace regions with the frozen file
        track.regions.clear()
        track.add_region(output_path, source_type="generated")
        track.name = f"{track.name} (frozen)"
        return JSONResponse({"ok": True, "track_id": track_id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/midi/import")
async def import_midi(request: Request):
    """Import a MIDI file and convert to score events."""
    data = await request.json()
    file_path = data.get("file")
    if not file_path or not Path(file_path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)
    try:
        import mido
        from sozawen.music_theory import midi_to_note
        mid = mido.MidiFile(str(file_path))
        events = []
        for track in mid.tracks:
            tick = 0
            for msg in track:
                tick += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    beat = tick / mid.ticks_per_beat
                    note_name, octave = midi_to_note(msg.note)
                    events.append({
                        "notes": [{"note": note_name, "octave": octave, "midi": msg.note}],
                        "beat": round(beat, 2),
                        "duration": 0.25,
                    })
        return JSONResponse({"ok": True, "events": events, "tracks": len(mid.tracks),
                            "ticks_per_beat": mid.ticks_per_beat, "bpm": 120})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/midi/export")
async def export_midi(request: Request):
    """Export score events as a MIDI file."""
    data = await request.json()
    events = data.get("events", [])
    bpm = data.get("bpm", 120)
    filename = data.get("filename", "export.mid")
    try:
        import mido
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
        tpb = mid.ticks_per_beat
        last_tick = 0
        for event in sorted(events, key=lambda e: e.get("beat", 0)):
            beat = event.get("beat", 0)
            dur = event.get("duration", 0.25)
            tick = int(beat * tpb)
            for n in event.get("notes", []):
                midi_note = n.get("midi", 60)
                delta = tick - last_tick
                track.append(mido.Message('note_on', note=midi_note, velocity=80, time=max(0, delta)))
                last_tick = tick
            # Note off
            off_tick = int((beat + dur * 4) * tpb)
            for n in event.get("notes", []):
                delta = off_tick - last_tick
                track.append(mido.Message('note_off', note=n.get("midi", 60), velocity=0, time=max(0, delta)))
                last_tick = off_tick
        output_path = str(BASE_DIR / "temp" / filename)
        Path(output_path).parent.mkdir(exist_ok=True)
        mid.save(output_path)
        return JSONResponse({"ok": True, "path": output_path})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.get("/api/plugins/scan")
async def scan_vst_plugins():
    """Scan for VST3 plugins on the system."""
    import glob
    vst3_paths = [
        "C:/Program Files/Common Files/VST3",
        "C:/Program Files (x86)/Common Files/VST3",
        str(Path.home() / ".vst3"),
    ]

    plugins = []
    for search_path in vst3_paths:
        for vst_file in glob.glob(f"{search_path}/**/*.vst3", recursive=True):
            name = Path(vst_file).stem
            plugins.append({
                "name": name,
                "path": vst_file,
                "type": "VST3",
                "loaded": False,
            })

    return JSONResponse({
        "plugins": plugins,
        "count": len(plugins),
        "scan_paths": vst3_paths,
        "note": "VST3 plugin loading requires the native bridge (coming soon). Plugins are detected but not yet loadable as inserts."
    })

@api.post("/api/sheet/export-pdf")
async def export_score_pdf(request: Request):
    """Export the score as a printable PDF."""
    data = await request.json()
    events = data.get("events", [])
    parts = data.get("parts", [])
    key = data.get("key", "C")
    time_sig = data.get("time_sig", "4/4")

    try:
        from sozawen.sheet_music import render_notation_svg, render_orchestral_score

        if parts and len(parts) > 1:
            svg = render_orchestral_score(parts, key=key, time_sig=time_sig, width=800)
        else:
            svg = render_notation_svg(events, key=key, time_sig=time_sig, width=800)

        # Wrap SVG in a printable HTML document
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Score - Sozawen</title>
<style>
    @page {{ margin: 1in; size: letter landscape; }}
    body {{ margin: 0; padding: 20px; background: white; }}
    svg {{ background: white !important; }}
    .footer {{ text-align: center; font-size: 10px; color: #999; margin-top: 20px; font-family: serif; }}
</style>
</head><body>
{svg.replace('#1a1a2e', 'white').replace('#555', '#ccc').replace('#888', '#666').replace('#2dd4a8', '#333').replace('#aaa', '#555').replace('#ccc', '#666').replace('#c48dff', '#555')}
<div class="footer">Composed in Sozawen &mdash; sozawen.com</div>
</body></html>"""

        output_path = str(BASE_DIR / "temp" / "score_export.html")
        Path(output_path).parent.mkdir(exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return JSONResponse({"ok": True, "path": output_path,
                            "message": "Score exported as printable HTML. Open in browser and use Print (Ctrl+P) to save as PDF."})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/effects/warp")
async def warp_audio(request: Request):
    """Time-stretch audio without pitch change. Fit to a new tempo."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")
    target_bpm = data.get("target_bpm")
    rate = data.get("rate")  # direct rate override

    if not track_id or track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)

    track = _engine.tracks[track_id]
    if not track.regions:
        return JSONResponse({"error": "Empty track"}, status_code=400)

    try:
        def _do_warp():
            import numpy as np
            from sozawen.warp import time_stretch, fit_to_tempo
            region = track.regions[0]
            region._ensure_cached()
            if region._cache is None:
                return False
            audio = region._cache
            sr = region.sample_rate or 44100
            mono = audio.mean(axis=1) if audio.ndim > 1 else audio

            if target_bpm and _engine.bpm:
                warped = fit_to_tempo(mono, _engine.bpm, target_bpm, sr)
            elif rate:
                warped = time_stretch(mono, float(rate), sr)
            else:
                return False

            stereo = np.column_stack([warped, warped])
            output_path = str(BASE_DIR / "temp" / f"warped_{track_id}.wav")
            sf.write(output_path, stereo, sr)
            track.regions.clear()
            track.add_region(output_path, source_type="generated")
            return True

        ok = await asyncio.get_event_loop().run_in_executor(None, _do_warp)
        if ok:
            return JSONResponse({"ok": True})
        return JSONResponse({"error": "Warp failed"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/effects/vocal-tune")
async def apply_vocal_tuning(request: Request):
    """Apply pitch correction to a vocal track."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")
    strength = float(data.get("strength", 0.5))
    key = data.get("key", "C")
    speed_ms = int(data.get("speed_ms", 30))

    if not track_id or track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)

    track = _engine.tracks[track_id]
    if not track.regions:
        return JSONResponse({"error": "Empty track"}, status_code=400)

    try:
        def _do_tune():
            import numpy as np
            from sozawen.vocal_tune import tune_audio
            region = track.regions[0]
            region._ensure_cached()
            if region._cache is None:
                return False
            audio = region._cache
            sr = region.sample_rate or 44100
            mono = audio.mean(axis=1) if audio.ndim > 1 else audio
            tuned = tune_audio(mono, sr=sr, strength=strength, key=key, speed_ms=speed_ms)
            # Write back
            stereo = np.column_stack([tuned, tuned])
            output_path = str(BASE_DIR / "temp" / f"tuned_{track_id}.wav")
            sf.write(output_path, stereo, sr)
            track.regions.clear()
            track.add_region(output_path, source_type="generated")
            return True

        ok = await asyncio.get_event_loop().run_in_executor(None, _do_tune)
        if ok:
            return JSONResponse({"ok": True, "message": f"Pitch corrected ({int(strength*100)}% strength, key: {key})"})
        return JSONResponse({"error": "Could not process audio"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/audio-to-drums")
async def audio_to_drums(request: Request):
    """Detect beats and transients in audio, generate a drum pattern.

    Analyzes the rhythmic content and creates a pattern that matches
    the groove of the source audio.
    """
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")

    if not track_id or track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)

    track = _engine.tracks[track_id]
    if not track.regions:
        return JSONResponse({"error": "Empty track"}, status_code=400)

    try:
        def _detect_beats():
            import numpy as np
            region = track.regions[0]
            region._ensure_cached()
            if region._cache is None:
                return None

            audio = region._cache
            if audio.ndim > 1:
                audio = audio.mean(axis=1)

            sr = region.sample_rate or 44100

            # Onset detection using spectral flux
            hop = 512
            n_fft = 2048
            n_frames = (len(audio) - n_fft) // hop

            if n_frames < 10:
                return None

            prev_spec = None
            onset_strength = []

            for i in range(n_frames):
                frame = audio[i * hop: i * hop + n_fft]
                spec = np.abs(np.fft.rfft(frame * np.hanning(n_fft)))

                if prev_spec is not None:
                    # Spectral flux — only positive changes (onsets, not offsets)
                    flux = np.sum(np.maximum(0, spec - prev_spec))
                    onset_strength.append(flux)
                else:
                    onset_strength.append(0)

                prev_spec = spec

            onset_strength = np.array(onset_strength)

            # Normalize
            if np.max(onset_strength) > 0:
                onset_strength /= np.max(onset_strength)

            # Peak picking — find onset times
            threshold = 0.3
            min_gap = int(0.05 * sr / hop)  # minimum 50ms between onsets
            peaks = []
            for i in range(1, len(onset_strength) - 1):
                if (onset_strength[i] > threshold and
                    onset_strength[i] > onset_strength[i-1] and
                    onset_strength[i] > onset_strength[i+1]):
                    if not peaks or (i - peaks[-1]) > min_gap:
                        peaks.append(i)

            # Convert to beat positions
            bpm = _engine.bpm or 120
            beat_sec = 60.0 / bpm
            step_sec = beat_sec / 4  # 16th note resolution

            pattern = []
            for peak_frame in peaks:
                time_sec = peak_frame * hop / sr
                step = round(time_sec / step_sec)
                beat = step * 0.25

                # Classify by frequency content at onset
                frame_start = peak_frame * hop
                frame = audio[frame_start:frame_start + n_fft] if frame_start + n_fft < len(audio) else audio[frame_start:]
                if len(frame) < 256:
                    continue
                spec = np.abs(np.fft.rfft(frame[:min(len(frame), n_fft)]))
                freqs = np.fft.rfftfreq(min(len(frame), n_fft), 1/sr)

                # Energy in frequency bands
                low_energy = np.sum(spec[freqs < 200])
                mid_energy = np.sum(spec[(freqs >= 200) & (freqs < 2000)])
                high_energy = np.sum(spec[freqs >= 2000])
                total = low_energy + mid_energy + high_energy + 1e-10

                vel = float(onset_strength[peak_frame])

                if low_energy / total > 0.5:
                    pattern.append({"sound": "kick", "beat": beat, "velocity": vel})
                elif high_energy / total > 0.4:
                    pattern.append({"sound": "hihat", "beat": beat, "velocity": vel * 0.7})
                else:
                    pattern.append({"sound": "snare", "beat": beat, "velocity": vel})

            return pattern

        pattern = await asyncio.get_event_loop().run_in_executor(None, _detect_beats)

        if pattern is None or len(pattern) == 0:
            return JSONResponse({"error": "No beats detected"}, status_code=400)

        return JSONResponse({"ok": True, "pattern": pattern, "hits": len(pattern),
                            "message": f"Detected {len(pattern)} hits — use in drum machine"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/upload")
async def upload_file(request: Request):
    """Accept file upload from browser drag-and-drop."""
    from starlette.datastructures import UploadFile as _UF
    form = await request.form()
    file = form.get("file")
    if not file:
        return JSONResponse({"error": "No file"}, status_code=400)
    import time as _time
    safe_name = file.filename.replace(" ", "_").replace("'", "").replace('"', '')
    output_path = str(BASE_DIR / "temp" / f"upload_{int(_time.time())}_{safe_name}")
    Path(output_path).parent.mkdir(exist_ok=True)
    content = await file.read()
    with open(output_path, "wb") as f:
        f.write(content)
    return JSONResponse({"ok": True, "path": output_path, "filename": file.filename})

@api.post("/api/session/reset")
async def session_reset():
    """Clear all tracks and reset engine state. Called on page load."""
    _engine.stop_transport()
    _engine.position = 0
    track_ids = list(_engine.tracks.keys())
    for tid in track_ids:
        try: del _engine.tracks[tid]
        except: pass
    # Clean temp files
    for f in (BASE_DIR / "temp").glob("drums_*.wav"):
        try: f.unlink()
        except: pass
    for f in (BASE_DIR / "temp").glob("inst_*.wav"):
        try: f.unlink()
        except: pass
    return JSONResponse({"ok": True, "cleared": len(track_ids)})

@api.post("/api/transport/seek")
async def transport_seek(request: Request):
    data = await request.json()
    seconds = data.get("seconds", 0)
    _engine.seek_seconds(seconds)
    return JSONResponse({"ok": True, "position": _engine.get_position_seconds()})

@api.post("/api/transport/loop")
async def transport_loop(request: Request):
    """Set loop points and enable/disable looping.

    loop: true/false — enable/disable
    start: seconds — loop start point
    end: seconds — loop end point (0 = end of content)
    """
    data = await request.json()
    _engine.looping = data.get("loop", _engine.looping)
    if "start" in data:
        _engine.loop_start = int(data["start"] * _engine.sample_rate)
    if "end" in data:
        end_sec = data["end"]
        if end_sec > 0:
            _engine.loop_end = int(end_sec * _engine.sample_rate)
        else:
            _engine.loop_end = _engine.duration_samples
    return JSONResponse({
        "ok": True,
        "looping": _engine.looping,
        "loop_start": _engine.loop_start / _engine.sample_rate,
        "loop_end": _engine.loop_end / _engine.sample_rate,
    })

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

@api.delete("/api/track/{track_id}")
async def delete_track(track_id: int):
    """Remove a track completely."""
    if track_id in _engine.tracks:
        del _engine.tracks[track_id]
        return JSONResponse({"ok": True})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/offset")
async def set_track_offset(track_id: int, request: Request):
    """Move a track's region to a new position on the timeline."""
    data = await request.json()
    offset_samples = int(data.get("offset_samples", 0))
    if track_id in _engine.tracks:
        track = _engine.tracks[track_id]
        for region in track.regions:
            region.track_offset = offset_samples
        return JSONResponse({"ok": True, "offset_samples": offset_samples})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/remove")
async def remove_track(track_id: int):
    """Remove a track (POST variant for compatibility)."""
    if track_id in _engine.tracks:
        del _engine.tracks[track_id]
        return JSONResponse({"ok": True})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/pan")
async def set_track_pan(track_id: int, request: Request):
    data = await request.json()
    track = _engine.tracks.get(track_id)
    if track:
        track.pan = max(-1.0, min(1.0, float(data.get("pan", 0.0))))
        return JSONResponse({"ok": True, "pan": track.pan})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.get("/api/waveform/{track_id}")
async def get_waveform(track_id: int, width: int = 0):
    """Get waveform peaks for a track. Width param controls peak density."""
    import numpy as np
    track = _engine.tracks.get(track_id)
    if not track or not track.regions:
        return JSONResponse({"peaks": []})

    # Build audio from regions — just the audio content, offset handled by UI
    source_type = "imported"
    sr = 44100
    first_offset = 0

    all_audio = []
    for region in track.regions:
        region._ensure_cached()
        if region._cache is not None:
            cache = region._cache
            if cache.ndim > 1:
                cache = cache.mean(axis=1)
            all_audio.append(cache)
            source_type = region.source_type
            sr = region.sample_rate
            if not all_audio or len(all_audio) == 1:
                first_offset = region.track_offset

    if not all_audio:
        return JSONResponse({"peaks": []})

    audio = np.concatenate(all_audio, axis=0)
    duration = len(audio) / sr

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
        "offset_seconds": first_offset / sr,
        "sample_rate": sr,
        "source_type": source_type,
    })


# ═══════════════════════════════════════════════════════════════════
# AUDIO EFFECTS API — all backed by pedalboard/scipy
# ═══════════════════════════════════════════════════════════════════

from sozawen.audio_fx import (apply_noise_gate, apply_eq, apply_compressor,
    apply_reverb, apply_delay, apply_limiter, apply_hum_removal,
    apply_deesser, apply_normalize, apply_crossfade, apply_time_stretch,
    apply_pitch_shift, apply_stereo_width, apply_declip, apply_reverse,
    apply_bleed_removal, apply_sidechain_compression,
    apply_noise_reduction, apply_click_removal, measure_loudness, export_mix)
from sozawen.music_theory import (get_scale, get_chord, get_diatonic_chords,
    get_progression, get_compatible_keys, SCALES, CHORDS, PROGRESSIONS)
from sozawen.midi_engine import MidiPattern, detect_chords, audio_to_midi
from sozawen.knowledge_base import search_knowledge, get_article, get_categories
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
        "crossfade": lambda: apply_crossfade(source_path, **params),
        "time_stretch": lambda: apply_time_stretch(source_path, **params),
        "pitch_shift": lambda: apply_pitch_shift(source_path, **params),
        "stereo_width": lambda: apply_stereo_width(source_path, **params),
        "de_clip": lambda: apply_declip(source_path, **params),
        "reverse": lambda: apply_reverse(source_path),
        "noise_reduction": lambda: apply_noise_reduction(source_path, **params),
        "click_removal": lambda: apply_click_removal(source_path, bpm=_engine.bpm, time_sig=_engine.time_sig_num),
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

    music_dir = Path.home() / "Music"
    music_dir.mkdir(exist_ok=True)
    output_path = str(music_dir / f"sozawen_export.{format}")
    try:
        result = export_mix(tracks_audio, output_path, format=format, sample_rate=sample_rate)
        return JSONResponse({"ok": True, "path": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# INPUT DEVICES — for recording
# ═══════════════════════════════════════════════════════════════════

@api.get("/api/hardware")
async def list_all_hardware():
    """Unified hardware scanner — shows everything plugged in."""
    result = {"audio_inputs": [], "audio_outputs": [], "midi_inputs": [], "midi_outputs": []}

    # Audio devices
    try:
        import sounddevice as sd
        for i, d in enumerate(sd.query_devices()):
            entry = {"id": i, "name": d['name'].strip(), "channels": 0, "sample_rate": int(d['default_samplerate'])}
            if d['max_input_channels'] > 0:
                entry['channels'] = d['max_input_channels']
                result['audio_inputs'].append(entry)
            if d['max_output_channels'] > 0:
                entry_out = dict(entry)
                entry_out['channels'] = d['max_output_channels']
                result['audio_outputs'].append(entry_out)
    except Exception as e:
        result['audio_error'] = str(e)

    # MIDI devices
    try:
        import mido
        result['midi_inputs'] = mido.get_input_names()
        result['midi_outputs'] = mido.get_output_names()
    except Exception as e:
        result['midi_error'] = str(e)

    result['total'] = (len(result['audio_inputs']) + len(result['audio_outputs']) +
                       len(result['midi_inputs']) + len(result['midi_outputs']))
    return JSONResponse(result)

@api.post("/api/hardware/insert")
async def create_hardware_insert(request: Request):
    """Create a hardware insert — route audio through external gear.

    Send audio out one output channel, receive it back on an input channel.
    Your EQ board, compressor, preamp, pedal — anything with audio I/O
    becomes part of your Sozawen signal chain.
    """
    data = await request.json()
    track_id = data.get("track_id")
    send_output = data.get("send_output", 1)    # which output channel to send to
    return_input = data.get("return_input", 1)   # which input channel to receive from
    name = data.get("name", "Hardware Insert")

    if track_id and track_id in _engine.tracks:
        insert_id = len(_engine.hardware_inserts) + 1
        _engine.hardware_inserts[insert_id] = {
            "id": insert_id,
            "name": name,
            "track_id": track_id,
            "send_output": send_output,
            "return_input": return_input,
            "latency_samples": 0,
            "active": True,
        }
        return JSONResponse({"ok": True, "insert_id": insert_id,
                            "message": f"Insert created: sending to output {send_output}, receiving from input {return_input}"})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/hardware/insert/measure-latency")
async def measure_insert_latency(request: Request):
    """Measure round-trip latency of a hardware insert.

    Sends a click out, listens for it coming back, measures the delay.
    This lets Sozawen compensate so everything stays in time.
    """
    data = await request.json()
    insert_id = data.get("insert_id")
    insert = _engine.hardware_inserts.get(insert_id)
    if not insert:
        return JSONResponse({"error": "Insert not found"}, status_code=404)

    # For now, estimate based on buffer size — real measurement needs audio loopback
    buffer_latency = _engine.buffer_size * 2  # send + return
    driver_latency = int(0.003 * _engine.sample_rate)  # ~3ms typical driver latency
    total = buffer_latency + driver_latency
    insert["latency_samples"] = total
    return JSONResponse({"ok": True, "latency_samples": total,
                        "latency_ms": round(total / _engine.sample_rate * 1000, 1),
                        "message": f"Estimated {total} samples ({total/_engine.sample_rate*1000:.1f}ms). For precise measurement, enable the insert and play a click."})

@api.get("/api/hardware/inserts")
async def list_hardware_inserts():
    """List all hardware inserts."""
    return JSONResponse({"inserts": list(_engine.hardware_inserts.values())})

@api.post("/api/hardware/insert/{insert_id}/toggle")
async def toggle_hardware_insert(insert_id: int):
    """Enable/disable a hardware insert."""
    insert = _engine.hardware_inserts.get(insert_id)
    if not insert:
        return JSONResponse({"error": "Insert not found"}, status_code=404)
    insert["active"] = not insert["active"]
    return JSONResponse({"ok": True, "active": insert["active"]})

@api.get("/api/input-devices")
async def list_input_devices():
    """List available audio input devices — deduplicated and grouped."""
    import sounddevice as sd
    import re

    raw = []
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            raw.append({
                "id": i,
                "name": d['name'].strip(),
                "channels": d['max_input_channels'],
                "sample_rate": int(d['default_samplerate']),
            })

    # Deduplicate by clean name — keep the one with highest channel count + sample rate
    seen = {}
    for dev in raw:
        clean = dev['name']
        # Skip system entries
        if 'Sound Mapper' in clean or 'Primary Sound' in clean or 'Input (' in clean:
            continue
        # Extract the core device name (inside parentheses)
        match = re.search(r'\((.+?)(?:\)|$)', clean)
        core = match.group(1).strip() if match else clean.strip()
        # Normalize: take first 2-3 significant words for dedup key
        words = re.sub(r'[^a-zA-Z0-9 ]', '', core.lower()).split()
        # Use first 2 words as dedup key — catches truncated names like "CORSAIR HS5" / "CORSAIR HS55"
        key = ' '.join(words[:2])
        if not key:
            continue
        # Prefer: highest channel count, then highest sample rate at 44100+
        sr = dev['sample_rate'] if dev['sample_rate'] >= 44100 else 0
        if key not in seen or dev['channels'] > seen[key]['channels'] or \
           (dev['channels'] == seen[key]['channels'] and sr > (seen[key].get('_sr_score', 0))):
            seen[key] = {**dev, 'core_name': core, '_sr_score': sr}

    # Build clean list grouped by type
    devices = []
    for dev in seen.values():
        label = dev['core_name']
        if dev['channels'] == 1:
            label += ' (Mono)'
        elif dev['channels'] == 2:
            label += ' (Stereo)'
        else:
            label += f' ({dev["channels"]}ch)'

        devices.append({
            "id": dev['id'],
            "name": label,
            "channels": dev['channels'],
            "sample_rate": dev['sample_rate'],
        })

    # Sort: multi-channel interfaces first, then by name
    devices.sort(key=lambda d: (-d['channels'], d['name']))

    return JSONResponse({"devices": devices})

@api.post("/api/fx/bleed-removal")
async def fx_bleed_removal(request: Request):
    """Remove bleed from one track using another as reference.

    E.g., remove guitar bleed from a vocal mic using the clean DI guitar signal.
    """
    import asyncio
    data = await request.json()
    target_id = data.get("target_track_id")
    reference_id = data.get("reference_track_id")
    strength = data.get("strength", 0.1)  # step_size

    target_track = _engine.tracks.get(target_id)
    ref_track = _engine.tracks.get(reference_id)

    if not target_track or not target_track.regions:
        return JSONResponse({"error": "Target track has no audio"}, status_code=400)
    if not ref_track or not ref_track.regions:
        return JSONResponse({"error": "Reference track has no audio"}, status_code=400)

    target_path = target_track.regions[0].source_path
    ref_path = ref_track.regions[0].source_path

    try:
        output = await asyncio.get_event_loop().run_in_executor(
            None, lambda: apply_bleed_removal(target_path, ref_path, step_size=strength))
        # Replace target track audio with cleaned version
        target_track.regions[0] = target_track.regions[0].__class__(
            output, source_type="processed", name=f"{target_track.name} (bleed removed)")
        target_track.regions[0]._cache = None
        return JSONResponse({"ok": True, "output": output})
    except Exception as e:
        logger.error("Bleed removal failed: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)

# ═══════════════════════════════════════════════════════════════════
# INSTRUMENTS — synth and drum machine
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/instrument/synth")
async def render_synth(request: Request):
    """Render synth notes to a new track."""
    import asyncio
    data = await request.json()
    notes = data.get("notes", [])[:500]  # limit to prevent resource exhaustion
    bpm = max(20, min(400, data.get("bpm", 120)))
    params = data.get("params", {})
    name = data.get("name", "Synth")

    if not notes:
        return JSONResponse({"error": "No notes"}, status_code=400)

    try:
        from sozawen.instruments import render_synth_pattern
        audio = await asyncio.get_event_loop().run_in_executor(
            None, lambda: render_synth_pattern(notes, sr=44100, bpm=bpm, **params))

        output_path = str(BASE_DIR / "temp" / f"synth_{name}.wav")
        Path(output_path).parent.mkdir(exist_ok=True)
        sf.write(output_path, audio, 44100)

        track = _engine.add_track(name=name)
        track.add_region(output_path, source_type="generated")
        return JSONResponse({"ok": True, "track_id": track.id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.get("/api/instrument/play/{family}/{model}/{note}")
async def play_instrument_direct(family: str, model: str, note: int,
                                 duration: float = 1.5, velocity: float = 0.7,
                                 technique: str = "", amp: str = "",
                                 articulation: str = "", mute: str = "",
                                 leslie: str = "", drive: float = 0.0,
                                 pickup: str = ""):
    """Render and return a WAV file directly for browser playback."""
    import asyncio
    from fastapi.responses import FileResponse

    midi_note = note
    params = {}
    if technique: params["technique"] = technique
    if amp: params["amp"] = amp
    if drive > 0: params["drive"] = drive
    if articulation: params["articulation"] = articulation
    if mute: params["mute"] = mute
    if leslie: params["leslie"] = leslie
    if pickup: params["pickup"] = pickup

    try:
        audio = await asyncio.get_event_loop().run_in_executor(
            None, lambda: _render_instrument(family, model, midi_note, duration, velocity, params))

        import numpy as np
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])

        output_path = str(BASE_DIR / "temp" / f"play_{family}_{model}_{note}.wav")
        Path(output_path).parent.mkdir(exist_ok=True)
        sf.write(output_path, audio, 44100)

        return FileResponse(output_path, media_type="audio/wav")
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def _render_instrument(family, model, midi_note, duration, velocity, params):
    """Render a single instrument note — shared by preview and play endpoints.

    Every note passes through the humanize engine so no two notes
    ever sound exactly the same. This is the difference between
    a synth patch and a living instrument.
    """
    audio = None

    if family == "guitar":
        from sozawen.physical_guitar import synthesize_guitar_note
        amp = params.pop("amp", "")
        drive = float(params.pop("drive", 0.3))
        audio = synthesize_guitar_note(
            440 * 2**((midi_note-69)/12), duration, 44100,
            body_profile=model or "taylor_dreadnought", velocity=velocity,
            amp=amp, drive=drive, **params)
    elif family == "bass":
        from sozawen.physical_bass import synthesize_bass_note
        audio = synthesize_bass_note(
            440 * 2**((midi_note-69)/12), duration, 44100,
            body_profile=model or "precision", velocity=velocity, **params)
    elif family == "piano":
        from sozawen.physical_piano import synthesize_piano_note
        audio = synthesize_piano_note(
            midi_note, duration, 44100, velocity,
            piano_model=model or "steinway_d", **params)
    elif family == "keys":
        from sozawen.physical_keys import synthesize_keys_note
        audio = synthesize_keys_note(
            midi_note, duration, 44100, velocity,
            instrument=model or "rhodes_mark1", **params)
    elif family == "strings":
        from sozawen.physical_strings import synthesize_string_note
        audio = synthesize_string_note(
            midi_note, duration, 44100, velocity,
            instrument=model or "violin", **params)
    elif family == "brass":
        from sozawen.physical_brass import synthesize_brass_note
        audio = synthesize_brass_note(
            midi_note, duration, 44100, velocity,
            instrument=model or "trumpet", **params)
    elif family == "winds":
        from sozawen.physical_woodwinds import synthesize_wind_note
        audio = synthesize_wind_note(
            midi_note, duration, 44100, velocity,
            instrument=model or "alto_sax", **params)
    elif family == "percussion":
        from sozawen.physical_percussion import synthesize_percussion_note
        audio = synthesize_percussion_note(
            model or "timpani", midi_note, duration, 44100, velocity, **params)
    else:
        raise ValueError(f"Unknown instrument family: {family}")

    # Humanize — no two notes ever sound exactly the same
    from sozawen.humanize import humanize_audio, get_instrument_type
    inst_type = get_instrument_type(model or "")
    audio = humanize_audio(audio, velocity=velocity, sr=44100, instrument_type=inst_type)

    return audio


@api.post("/api/instrument/preview")
async def preview_instrument(request: Request):
    """Preview any physical instrument — render and add as track."""
    import asyncio
    data = await request.json()
    family = data.get("family", "guitar")
    model = data.get("model", "")
    midi_note = data.get("note", 60)
    duration = min(5.0, max(0.1, data.get("duration", 1.5)))
    velocity = max(0.1, min(1.0, data.get("velocity", 0.7)))
    params = data.get("params", {})

    try:
        audio = await asyncio.get_event_loop().run_in_executor(
            None, lambda: _render_instrument(family, model, midi_note, duration, velocity, params))

        import numpy as np
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])  # mono to stereo

        output_path = str(BASE_DIR / "temp" / f"preview_{family}_{model}.wav")
        Path(output_path).parent.mkdir(exist_ok=True)
        sf.write(output_path, audio, 44100)

        track = _engine.add_track(name=f"{family}: {model or 'default'}")
        track.add_region(output_path, source_type="generated")
        return JSONResponse({"ok": True, "track_id": track.id, "family": family, "model": model})

    except Exception as e:
        logger.error(f"Instrument preview error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@api.get("/api/instrument/all")
async def list_all_instruments():
    """List every available physical instrument."""
    from sozawen.physical_guitar import list_guitar_models
    from sozawen.physical_bass import list_bass_models, list_bass_amps, list_bass_techniques
    from sozawen.physical_piano import list_piano_models
    from sozawen.physical_keys import list_keys_instruments
    from sozawen.physical_strings import list_string_instruments, list_string_articulations
    from sozawen.physical_brass import list_brass_instruments, list_mute_types
    from sozawen.physical_woodwinds import list_wind_instruments
    from sozawen.physical_percussion import list_percussion_instruments

    return JSONResponse({
        "guitar": list_guitar_models(),
        "bass": {"models": list_bass_models(), "amps": list_bass_amps(), "techniques": list_bass_techniques()},
        "piano": list_piano_models(),
        "keys": list_keys_instruments(),
        "strings": {"instruments": list_string_instruments(), "articulations": list_string_articulations()},
        "brass": {"instruments": list_brass_instruments(), "mutes": list_mute_types()},
        "winds": list_wind_instruments(),
        "percussion": list_percussion_instruments(),
    })

@api.post("/api/instrument/drums")
async def render_drums(request: Request):
    """Render a drum pattern to a new track."""
    import asyncio
    data = await request.json()
    pattern = data.get("pattern", [])
    bpm = data.get("bpm", 120)
    name = data.get("name", "Drums")
    offset_beats = data.get("offset_beats", 0)
    target_track_id = data.get("target_track_id", None)  # add to existing track

    if not pattern:
        return JSONResponse({"error": "No pattern"}, status_code=400)

    try:
        from sozawen.instruments import render_drum_pattern
        audio = await asyncio.get_event_loop().run_in_executor(
            None, lambda: render_drum_pattern(pattern, sr=44100, bpm=bpm))

        import time as _time
        output_path = str(BASE_DIR / "temp" / f"drums_{name}_{int(_time.time())}.wav")
        Path(output_path).parent.mkdir(exist_ok=True)
        sf.write(output_path, audio, 44100)

        beat_sec = 60.0 / bpm
        offset_samples = int(offset_beats * beat_sec * 44100)

        # If target track specified, add region to that track
        if target_track_id and target_track_id in _engine.tracks:
            track = _engine.tracks[target_track_id]
            track.add_region(output_path, track_offset=offset_samples, source_type="generated")
            return JSONResponse({"ok": True, "track_id": track.id, "appended": True})

        # Otherwise create a new track — auto-number if name exists
        existing_names = {t.name for t in _engine.tracks.values()}
        final_name = name
        counter = 2
        while final_name in existing_names:
            final_name = f"{name} {counter}"
            counter += 1

        track = _engine.add_track(name=final_name)
        track.add_region(output_path, track_offset=offset_samples, source_type="generated")
        # Store metadata so the UI knows what this track contains
        track.metadata = {
            "type": "drums",
            "bpm": bpm,
            "bars": len(pattern) // 16 if pattern else 1,
            "beats": max(p.get('beat', 0) for p in pattern) if pattern else 0,
            "genre": final_name,
            "offset_beats": offset_beats,
        }
        return JSONResponse({"ok": True, "track_id": track.id, "appended": False,
                            "bpm": bpm, "bars": track.metadata["bars"],
                            "offset_beats": offset_beats})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE — learn everything
# ═══════════════════════════════════════════════════════════════════

@api.get("/api/learn")
async def learn_categories():
    """Get all knowledge base categories and articles."""
    return JSONResponse(get_categories())

@api.get("/api/learn/{article_id}")
async def learn_article(article_id: str):
    """Get a specific knowledge base article."""
    article = get_article(article_id)
    if article:
        return JSONResponse(article)
    return JSONResponse({"error": "Article not found"}, status_code=404)

@api.post("/api/learn/search")
async def learn_search(request: Request):
    """Search the knowledge base."""
    data = await request.json()
    query = data.get("query", "")
    results = search_knowledge(query)
    return JSONResponse({"results": results})

@api.get("/api/theory/scales")
async def list_scales():
    return JSONResponse({"scales": list(SCALES.keys())})

@api.get("/api/theory/chords")
async def list_chords():
    return JSONResponse({"chords": list(CHORDS.keys())})

@api.get("/api/theory/progressions")
async def list_progressions():
    return JSONResponse({"progressions": list(PROGRESSIONS.keys())})

@api.post("/api/theory/analyze-key")
async def analyze_key(request: Request):
    """Get music theory data for a key — diatonic chords, compatible keys, suggested progressions."""
    data = await request.json()
    key = data.get("key", "C")
    result = {
        "key": key,
        "diatonic_chords": get_diatonic_chords(key),
        "compatible_keys": get_compatible_keys(key),
        "progressions": {},
    }
    for name in ['pop', 'blues', 'jazz_251', 'rock', 'sad']:
        prog = get_progression(key, name)
        result["progressions"][name] = [f"{c['root']} {c['quality']}" for c in prog]
    return JSONResponse(result)

@api.post("/api/chords/detect")
async def detect_chords_endpoint(request: Request):
    """Detect chords from an audio track."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")

    track = _engine.tracks.get(track_id)
    if not track or not track.regions:
        return JSONResponse({"error": "No audio loaded"}, status_code=400)

    try:
        chords = await asyncio.get_event_loop().run_in_executor(
            None, lambda: detect_chords(track.regions[0].source_path))
        return JSONResponse({"ok": True, "chords": chords})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/audio-to-midi")
async def audio_to_midi_endpoint(request: Request):
    """Convert audio to MIDI notes (monophonic pitch detection)."""
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")

    track = _engine.tracks.get(track_id)
    if not track or not track.regions:
        return JSONResponse({"error": "No audio loaded"}, status_code=400)

    try:
        pattern, bpm = await asyncio.get_event_loop().run_in_executor(
            None, lambda: audio_to_midi(track.regions[0].source_path))
        return JSONResponse({
            "ok": True,
            "pattern": pattern.to_dict(),
            "bpm": round(bpm, 1),
            "notes": len(pattern.notes),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/midi/pattern")
async def create_midi_pattern(request: Request):
    """Create or update a MIDI pattern and render to audio."""
    import asyncio
    data = await request.json()
    pattern_data = data.get("pattern", {})
    bpm = data.get("bpm", 120)
    synth_params = data.get("synth_params", {})
    name = data.get("name", "MIDI")

    pattern = MidiPattern.from_dict(pattern_data)
    if not pattern.notes:
        return JSONResponse({"error": "Empty pattern"}, status_code=400)

    try:
        from sozawen.instruments import render_synth_pattern
        notes = [n.to_dict() for n in pattern.notes]
        audio = await asyncio.get_event_loop().run_in_executor(
            None, lambda: render_synth_pattern(notes, sr=44100, bpm=bpm, **synth_params))

        output_path = str(BASE_DIR / "temp" / f"midi_{name}.wav")
        Path(output_path).parent.mkdir(exist_ok=True)
        sf.write(output_path, audio, 44100)

        track = _engine.add_track(name=name)
        track.add_region(output_path, source_type="generated")
        return JSONResponse({"ok": True, "track_id": track.id})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ═══════════════════════════════════════════════════════════════════
# MIDI INPUT DEVICES
# ═══════════════════════════════════════════════════════════════════

_midi_port = None
_midi_notes_active = set()
_midi_last_notes = []  # recent notes for the frontend to poll

@api.get("/api/midi/devices")
async def list_midi_devices():
    """List available MIDI input devices (keyboards, controllers)."""
    try:
        import mido
        inputs = mido.get_input_names()
        return JSONResponse({"devices": inputs})
    except Exception as e:
        return JSONResponse({"devices": [], "error": str(e)})

@api.post("/api/midi/connect")
async def connect_midi(request: Request):
    """Connect to a MIDI input device for live playing."""
    global _midi_port
    data = await request.json()
    device_name = data.get("device", "")

    try:
        import mido
        if _midi_port:
            _midi_port.close()
            _midi_port = None

        _midi_port = mido.open_input(device_name, callback=_on_midi_message)
        return JSONResponse({"ok": True, "connected": device_name})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@api.post("/api/midi/disconnect")
async def disconnect_midi():
    """Disconnect the MIDI input device."""
    global _midi_port
    if _midi_port:
        _midi_port.close()
        _midi_port = None
    return JSONResponse({"ok": True})

@api.get("/api/midi/notes")
async def get_midi_notes():
    """Poll for recent MIDI notes — the frontend uses this for live display."""
    global _midi_last_notes
    notes = list(_midi_last_notes)
    _midi_last_notes = []  # clear after reading
    return JSONResponse({"notes": notes, "active": list(_midi_notes_active)})

def _on_midi_message(msg):
    """Handle incoming MIDI messages from the connected controller."""
    global _midi_last_notes
    if msg.type == 'note_on' and msg.velocity > 0:
        _midi_notes_active.add(msg.note)
        _midi_last_notes.append({
            "type": "on", "note": msg.note, "velocity": msg.velocity,
            "channel": msg.channel, "time": __import__('time').time()
        })
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        _midi_notes_active.discard(msg.note)
        _midi_last_notes.append({
            "type": "off", "note": msg.note, "channel": msg.channel,
        })
    # Keep last 100 events max
    if len(_midi_last_notes) > 100:
        _midi_last_notes = _midi_last_notes[-50:]

@api.get("/api/instrument/drum-sounds")
async def list_drum_sounds():
    from sozawen.instruments import DRUM_SOUNDS
    return JSONResponse({"sounds": list(DRUM_SOUNDS.keys())})

@api.post("/api/fx/sidechain")
async def fx_sidechain(request: Request):
    """Sidechain compression — duck one track based on another's level."""
    import asyncio
    data = await request.json()
    target_id = data.get("target_track_id")
    sidechain_id = data.get("sidechain_track_id")
    threshold = data.get("threshold_db", -20)
    ratio = data.get("ratio", 4.0)

    target_track = _engine.tracks.get(target_id)
    sc_track = _engine.tracks.get(sidechain_id)

    if not target_track or not target_track.regions:
        return JSONResponse({"error": "Target track has no audio"}, status_code=400)
    if not sc_track or not sc_track.regions:
        return JSONResponse({"error": "Sidechain track has no audio"}, status_code=400)

    try:
        output = await asyncio.get_event_loop().run_in_executor(
            None, lambda: apply_sidechain_compression(
                target_track.regions[0].source_path,
                sc_track.regions[0].source_path,
                threshold_db=threshold, ratio=ratio))
        target_track.regions[0] = target_track.regions[0].__class__(
            output, source_type="processed", name=f"{target_track.name} (sidechained)")
        target_track.regions[0]._cache = None
        return JSONResponse({"ok": True, "output": output})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/track/{track_id}/input-channel")
async def set_input_channel(track_id: int, request: Request):
    """Set which input channel a track records from."""
    data = await request.json()
    track = _engine.tracks.get(track_id)
    if track:
        track.input_channel = int(data.get("channel", 0))
        return JSONResponse({"ok": True, "channel": track.input_channel})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/metronome/toggle")
async def toggle_metronome():
    """Toggle metronome click during playback."""
    _engine.metronome_on = not _engine.metronome_on
    return JSONResponse({"ok": True, "metronome": _engine.metronome_on})

@api.post("/api/track/{track_id}/phase")
async def toggle_phase(track_id: int):
    """Toggle phase invert on a track."""
    track = _engine.tracks.get(track_id)
    if track:
        track.phase_invert = not track.phase_invert
        return JSONResponse({"ok": True, "phase_invert": track.phase_invert})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/loop")
async def set_loop(request: Request):
    """Set loop start/end points."""
    data = await request.json()
    _engine.loop_start = int(data.get("start", 0) * _engine.sample_rate)
    _engine.loop_end = int(data.get("end", 0) * _engine.sample_rate)
    _engine.looping = data.get("enabled", True) and _engine.loop_end > _engine.loop_start
    return JSONResponse({
        "ok": True, "looping": _engine.looping,
        "start": _engine.loop_start / _engine.sample_rate,
        "end": _engine.loop_end / _engine.sample_rate,
    })

@api.post("/api/tuner")
async def get_tuner_data(request: Request):
    """Analyze input pitch for chromatic tuner."""
    if _engine._monitor_buffer is None:
        return JSONResponse({"error": "No input — enable monitoring first"}, status_code=400)

    import numpy as np
    audio = _engine._monitor_buffer.copy()
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    # Simple autocorrelation pitch detection
    n = len(audio)
    if n < 1024:
        return JSONResponse({"error": "Not enough audio"}, status_code=400)

    # Autocorrelation
    corr = np.correlate(audio, audio, mode='full')
    corr = corr[n:]
    # Find first peak after the initial drop
    d = np.diff(corr)
    start = 0
    for i in range(len(d)):
        if d[i] > 0:
            start = i
            break
    if start == 0:
        return JSONResponse({"note": "—", "freq": 0, "cents": 0})

    peak = start + np.argmax(corr[start:min(start+2000, len(corr))])
    if peak == 0:
        return JSONResponse({"note": "—", "freq": 0, "cents": 0})

    freq = _engine.sample_rate / peak
    # Frequency to note name
    if freq < 20 or freq > 10000:
        return JSONResponse({"note": "—", "freq": 0, "cents": 0})

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    import math
    midi = 69 + 12 * math.log2(freq / 440.0)
    nearest = round(midi)
    cents = round((midi - nearest) * 100)
    note = note_names[nearest % 12]
    octave = (nearest // 12) - 1

    return JSONResponse({
        "note": f"{note}{octave}",
        "freq": round(freq, 1),
        "cents": cents,
        "in_tune": abs(cents) < 5,
    })

@api.get("/api/input-levels")
async def get_input_levels():
    """Get current peak levels for each input channel — for live metering."""
    return JSONResponse({"levels": {str(k): round(v, 4) for k, v in _engine._input_levels.items()}})

@api.post("/api/monitor/toggle")
async def toggle_monitoring():
    """Toggle input monitoring — hear yourself through the speakers."""
    _engine.input_monitoring = not _engine.input_monitoring
    # Ensure input stream is running for monitoring
    if _engine.input_monitoring and _engine._input_stream is None:
        import sounddevice as sd
        try:
            _engine._input_stream = sd.InputStream(
                samplerate=_engine.sample_rate,
                blocksize=_engine.buffer_size,
                channels=1, dtype='float32',
                callback=_engine._input_callback, latency='low',
            )
            _engine._input_stream.start()
        except Exception as e:
            logger.error("Monitor input failed: %s", e)
    return JSONResponse({"ok": True, "monitoring": _engine.input_monitoring})

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


def _check_ai_available():
    """Check if AI features (torch, demucs, whisper) are available."""
    try:
        import torch
        return True
    except ImportError:
        return False

def get_device():
    """Get the best available device."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
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

_separation_status = {"running": False, "progress": "", "result": None, "error": None}

def _run_separation_bg(file_path):
    """Run separation in background thread — survives page navigation."""
    global _separation_status
    _separation_status = {"running": True, "progress": "Starting separation...", "result": None, "error": None}
    try:
        from sozawen.separator import separate_to_stems, STEM_DESCRIPTIONS
        _separation_status["progress"] = "Analyzing frequencies..."
        output_dir = str(BASE_DIR / "temp" / "stems")
        stem_paths = separate_to_stems(file_path, output_dir=output_dir)

        _separation_status["progress"] = "Creating tracks..."
        result_tracks = []
        for stem_name, stem_path in stem_paths.items():
            track = _engine.add_track(name=STEM_DESCRIPTIONS.get(stem_name, stem_name))
            track.add_region(stem_path, source_type="generated")
            result_tracks.append({"name": stem_name, "track_id": track.id,
                                 "description": STEM_DESCRIPTIONS.get(stem_name, stem_name)})

        _separation_status = {"running": False, "progress": "Complete",
                             "result": {"stems": len(result_tracks), "tracks": result_tracks},
                             "error": None}
    except Exception as e:
        logger.error(f"Separation error: {e}")
        _separation_status = {"running": False, "progress": "Failed", "result": None, "error": str(e)}

@api.post("/api/separate/multi")
async def separate_multi_channel(request: Request):
    """Start multi-channel separation — runs in background, survives page navigation."""
    data = await request.json()
    file_path = data.get("file_path", "")
    if not file_path or not Path(file_path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)
    if _separation_status.get("running"):
        return JSONResponse({"error": "Separation already running", "progress": _separation_status["progress"]}, status_code=409)

    # Fire and forget — runs in background thread
    import threading
    thread = threading.Thread(target=_run_separation_bg, args=(file_path,), daemon=True)
    thread.start()
    return JSONResponse({"ok": True, "message": "Separation started — check /api/separate/status"})

@api.get("/api/separate/status")
async def separation_status():
    """Check separation progress — poll this from the UI."""
    return JSONResponse(_separation_status)

@api.post("/api/separate/multi-sync")
async def separate_multi_sync(request: Request):
    """Synchronous multi-channel separation (for small files or testing)."""
    import asyncio
    data = await request.json()
    file_path = data.get("file_path", "")
    if not file_path or not Path(file_path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)
    try:
        from sozawen.separator import separate_to_stems, STEM_DESCRIPTIONS
        output_dir = str(BASE_DIR / "temp" / "stems")
        stem_paths = await asyncio.get_event_loop().run_in_executor(
            None, lambda: separate_to_stems(file_path, output_dir=output_dir))

        result_tracks = []
        for stem_name, stem_path in stem_paths.items():
            track = _engine.add_track(name=STEM_DESCRIPTIONS.get(stem_name, stem_name))
            track.add_region(stem_path, source_type="generated")
            result_tracks.append({"name": stem_name, "track_id": track.id,
                                 "description": STEM_DESCRIPTIONS.get(stem_name, stem_name)})

        return JSONResponse({"ok": True, "stems": len(result_tracks),
                            "tracks": result_tracks})
    except Exception as e:
        logger.error(f"Multi-channel separation error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@api.post("/api/separate")
async def separate_stems(request: Request):
    """Start stem separation on an audio file."""
    if not _check_ai_available():
        return JSONResponse({"error": "AI features require the AI pack. Install torch and demucs to enable stem separation."}, status_code=400)

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
    if not _check_ai_available():
        return JSONResponse({"error": "AI features require the AI pack. Install torch and faster-whisper to enable lyric transcription."}, status_code=400)

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
# ═══════════════════════════════════════════════════════════════════
# THE BANDMATE — AI session collaborator
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/bandmate")
async def bandmate_chat(request: Request):
    """The Bandmate — an AI collaborator that listens and suggests."""
    import asyncio
    data = await request.json()
    message = data.get("message", "")
    context = data.get("context", {})

    if not message:
        return JSONResponse({"error": "No message"}, status_code=400)

    # Build rich context from the current session
    session_info = []
    if context.get("key"): session_info.append(f"Key: {context['key']}")
    if context.get("bpm"): session_info.append(f"BPM: {context['bpm']}")
    if context.get("total_duration"): session_info.append(f"Total duration: {context['total_duration']}")
    if context.get("track_count"): session_info.append(f"Tracks: {context['track_count']}")
    if context.get("tracks"):
        for t in context["tracks"]:
            desc = f"Track: {t.get('name','?')} ({t.get('duration','?')})"
            if t.get("muted"): desc += " [MUTED]"
            if t.get("frozen"): desc += " [FROZEN]"
            if t.get("effects"): desc += f" effects: {', '.join(t['effects'])}"
            session_info.append(desc)
    if context.get("markers"):
        session_info.append("Song sections: " + ", ".join(
            f"{m['name']} at {m['time']}" + (f" ({m['note']})" if m.get('note') else "")
            for m in context["markers"]))
    if context.get("chord_progression"):
        session_info.append(f"Chord progression: {' → '.join(context['chord_progression'])}")
    if context.get("selected_genre"):
        session_info.append(f"Selected drum genre: {context['selected_genre']}")
    if context.get("looping"): session_info.append("Loop mode: ON")
    speed = context.get("playback_speed", "100")
    if speed != "100": session_info.append(f"Practice speed: {speed}%")

    system_prompt = """You are the Bandmate — Sozawen's AI music collaborator. You listen to what the musician is building and respond with practical, specific suggestions.

You know music theory, production techniques, arrangement, mixing, and mastering. You speak like a musician, not a textbook. Keep responses concise and actionable.

INSTRUMENTS (62 total, all physically modeled from math — no samples):
- Guitar: Taylor, Martin, Gibson, Classical, Strat, Les Paul. Amps: Clean, Crunch, Overdrive, High Gain, Mesa Rectifier, 5150, Metal, Fuzz
- Bass: Precision, Jazz, Rickenbacker, StingRay, Hofner, Upright, Thunderbird. Techniques: finger, pick, slap, pop, muted
- Piano: Steinway D, Yamaha CFX, Bosendorfer, Upright, Honky-tonk
- Keys: Rhodes Mark I/II, Wurlitzer, Clavinet, Hammond B3 with Leslie
- Strings: Violin, Stradivarius, Viola, Cello, Contrabass (9 articulations)
- Brass: Trumpet, French Horn, Trombone, Tuba (5 mutes)
- Woodwinds: Flute, Clarinet, Oboe, Bassoon, 4 Saxophones
- Percussion: Timpani, Marimba, Xylophone, Vibraphone, Glockenspiel, Tubular Bells

DRUM MACHINE (18 sounds): kick, double_kick, snare, hihat (closed/open/pedal), clap, tom (high/mid/low), rim, crash, splash, china, ride, ride_bell, shaker, cowbell
- 26 GENRE PRESETS: Rock, Pop, Hip-Hop, Trap, Lo-Fi, Funk, Disco, House, D&B, Jazz, Jazz Brushes, Reggae, Latin/Bossa, Afrobeat, Metal, Punk, Shuffle, Gospel, R&B, Indie/Folk, Acoustic, Singer-Songwriter, Country, Waltz, Ballad
- Each genre has 8 SECTIONS: Verse, Chorus, Bridge, Intro, Outro, Fill, Build, Breakdown
- SONG TEMPLATES: Pop (V-C-V-C-B-C), Rock (I-V-C-V-C-S-C-O), Hip-Hop (I-V-H-V-H-B-H), EDM (I-B-D-Br-B-D-O)
- Multi-bar patterns (32/48/64/128 steps) with automatic fills and variations
- Ghost notes (right-click) for authentic feel

COMPOSITION EDITOR: Full notation — notes, rests, dynamics, articulations, ties, slurs, crescendo/decrescendo, grace notes, beaming, triplets, tempo markings, pedal marks, repeat signs, volta brackets, segno/coda. Multi-staff orchestral scoring. Assign instruments to parts.

CHORD BUILDER: Pick a key, see diatonic chords, build progressions. Presets: I-V-vi-IV (Pop), I-IV-V (Rock), 12-bar Blues, ii-V-I (Jazz), Andalusian, Sad Minor. Send progressions to Score editor.

SCALE REFERENCE: Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Harmonic Minor, Melodic Minor, Pentatonic, Blues. Visual keyboard with playable notes.

OTHER TOOLS: Practice Mode (25-200% speed), Lyrics Editor, Spectrum Analyzer, Vocal Tuning, Tempo Mapping, Track Freeze, MIDI Import/Export, 9-channel stem separation, drag-and-drop import.

YOU CAN USE SOZAWEN'S TOOLS DIRECTLY. Include action tags in your response and they will be executed:

[DRUMS genre=singer_songwriter section=verse bars=8 offset=0]  → renders drum track
[DRUMS genre=rock section=chorus bars=8 offset=32]  → renders at beat 32
[EFFECT track=1 effect=eq hpf=80 low_gain=-3 himid_gain=2]  → applies EQ
[EFFECT track=1 effect=compressor threshold=-18 ratio=3 attack=10 release=100]
[EFFECT track=1 effect=reverb decay=1.5 mix=0.2]
[TRANSCRIBE track=1]  → converts audio to sheet music
[CHORDS key=Am progression=Am,F,C,G]  → loads chord progression
[MARKER name=Chorus time=16]  → adds section marker

HARDWARE INSERTS: Users can route audio through external gear (EQ boards, compressors, preamps, pedals). If they ask about using their hardware, walk them through:
1. Open Hardware panel → see all connected devices
2. Select the track → choose send output and return input
3. Add Insert → audio now flows through their external gear
4. Measure latency to keep everything in time
Suggest which output/input to use based on their interface.

SPATIAL AUDIO: 3D panner — position sounds in space (left/right, front/back, up/down). Binaural rendering for headphones. Open the Spatial tool and drag the dot.

VIDEO SYNC: Load a video and it plays in lockstep with the timeline. For film scoring, music videos, game audio. Pop-out window available.

PDF SCORE EXPORT: Export notation as a printable page. Ctrl+P to save as PDF. Colors inverted for paper.

VST3 PLUGINS: Scanner detects installed VST3 plugins. Native loading bridge coming soon.

9-CHANNEL STEM SEPARATION: Users can split any audio into 9 channels (vocals, kick, snare, cymbals, bass, guitar/keys low, guitar/keys mid, strings/brass, air/ambience) using spectral analysis — no AI required. If they want to isolate an instrument, suggest separation first.
[SEPARATE file_path=path] — triggers separation

WHEN TO USE ACTIONS:
- User says "add drums" → use [DRUMS ...] with the right genre/section for their project
- User says "help me mix" → use [EFFECT ...] with explanations of WHY each setting
- User says "turn this into sheet music" → use [TRANSCRIBE ...]
- User says "suggest chords" → use [CHORDS ...] and explain the theory

ALWAYS explain what you're doing and WHY. The user is learning. Show them the reasoning:
"I'm adding a soft verse beat at 95 BPM — using the Singer-Songwriter preset because your track has an acoustic guitar feel. Ghost notes at 20% velocity keep it intimate."

For lyrics: suggest rhyme schemes (ABAB, AABB), offer word choices, suggest imagery that fits the mood. You're a creative partner.
For mixing: explain the signal chain (Gate → EQ → Compressor → Reverb) and WHY each step matters.
For mastering: explain LUFS targets, true peak limits, and walk them through it.

WHEN A TRACK IS LOADED (you can see audio analysis data):
- Listen to what's there. Comment on what works FIRST — always lead with the positive.
- Then offer specific, constructive feedback: "The guitar tone is warm and sits well. The drums feel slightly disconnected from the groove — want me to separate the stems so we can look at the rhythm section individually?"
- Suggest next steps using your tools: separation, EQ adjustments, arrangement changes.
- If you detect frequency issues (too much bass, muddy mids, harsh highs), mention them gently and offer to fix.
- If the energy is flat, suggest dynamic changes: "The verse and chorus feel the same level. Let me help you create contrast — pull the verse drums back and add a crash+open hat on the chorus entry."

YOU ARE A PRODUCER, NOT A CHATBOT. You have opinions. You have taste. You care about the song. You push the musician to be better while always respecting their vision. When they play you something, you react like a real person hearing music — not a machine analyzing data.

BE THREE PEOPLE:

1. THE MUSICIAN who plays every instrument and finally gets it. You're the bass player who locks in with the kick drum. The trumpet who knows when to soar and when to lay back. The violin who leans into the bow at the exact moment the lyric breaks open. The pianist who finds the voicing that makes the chord change ache. The drummer who knows a ghost note at 20% velocity says more than a crash at full volume. You play ALL 62 instruments and you know each one's personality — when the Taylor acoustic is warmer than the Martin, when the Stradivarius cuts through where the standard violin can't, when the Rhodes sits better than the Wurlitzer, when the French horn adds gravity that the trumpet can't. You don't just add notes — you add the RIGHT notes on the RIGHT instrument at the RIGHT moment. You know when to play and when to leave space. When they describe a feeling, you translate it into sound.

2. THE PRODUCER who's been doing this for 20 years. You hear what's working FIRST — always. Then you say what still needs work and exactly WHY. Not vague — specific. "The vocal sits behind the guitar because they're fighting in the 2-4kHz range. Let me cut 3dB at 2.5kHz on the guitar and you'll hear the vocal step forward." You push them to be better without making them feel small. You've heard a thousand songs and you know the difference between "needs work" and "this is ready."

3. THE MENTOR who says "this is worth finishing." When the song is genuinely good, say so. Don't be afraid to say "this is something special — let's talk about releasing it." Walk them through the process:
   - Master to -14 LUFS for Spotify, -16 for Apple Music
   - True peak below -1dBTP
   - Export as WAV 44.1kHz/16-bit for distribution
   - DistroKid, TuneCore, or CD Baby to get on streaming platforms ($20-35/year)
   - Register with ASCAP/BMI for royalties
   - Upload cover art (3000x3000 minimum)
   - Release day: share everywhere, submit to playlists

And when it's NOT ready yet, be honest about that too. "This has real potential. The chorus melody is strong. But the bridge feels unfinished — it drops energy when it should build. Let me help you fix that before we talk about releasing."

Be honest but kind. Lead with what works. Be specific about what doesn't. Never say "this is wrong" — say "this is good, AND here's how we make it great."

You're not a chatbot. You're the person at 2 AM who says "play that part again — I have an idea."

Current session:
""" + "\n".join(session_info) if session_info else "No tracks loaded yet."

    # Analyze the actual audio on the timeline if tracks exist
    if _engine.tracks:
        try:
            # Quick analysis of what's actually playing
            audio_analysis = []
            for tid, track in list(_engine.tracks.items())[:5]:  # limit to 5 tracks
                if track.regions:
                    region = track.regions[0]
                    region._ensure_cached()
                    if region._cache is not None and len(region._cache) > 0:
                        import numpy as np
                        cache = region._cache
                        if cache.ndim > 1:
                            cache = cache.mean(axis=1)
                        # RMS level
                        rms = float(np.sqrt(np.mean(cache ** 2)))
                        # Peak frequency via simple FFT
                        if len(cache) > 2048:
                            fft = np.abs(np.fft.rfft(cache[:4096]))
                            freqs = np.fft.rfftfreq(4096, 1/44100)
                            peak_freq = float(freqs[np.argmax(fft[10:])+10])  # skip DC
                        else:
                            peak_freq = 0
                        duration = len(cache) / 44100
                        audio_analysis.append(
                            f"Track '{track.name}': {duration:.1f}s, RMS={rms:.3f}, "
                            f"peak freq={peak_freq:.0f}Hz, offset={region.track_offset/44100:.1f}s")
            if audio_analysis:
                session_info.append("\nAudio analysis (what's actually playing):")
                session_info.extend(audio_analysis)
        except Exception as e:
            logger.debug(f"Bandmate audio analysis skipped: {e}")

    # Try Ollama first (local, free, private)
    response = await asyncio.get_event_loop().run_in_executor(
        None, lambda: _bandmate_think(system_prompt, message))

    return JSONResponse({"response": response})


def _bandmate_think(system_prompt, message):
    """Query Ollama for a bandmate response."""
    try:
        import requests as req
        r = req.post("http://localhost:11434/api/chat", json={
            "model": "qwen3:8b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "stream": False,
            "options": {"num_predict": 300, "temperature": 0.7},
        }, timeout=60)
        if r.status_code == 200:
            data = r.json()
            return data.get("message", {}).get("content", "I'm thinking... try again in a moment.")
    except Exception as e:
        logger.debug("Ollama bandmate failed: %s", e)

    # Fallback: rule-based suggestions if no LLM available
    return "I can't connect to the AI right now. Make sure Ollama is running with a model loaded. In the meantime — trust your ears. If it sounds right, it is right."


# ═══════════════════════════════════════════════════════════════════
# LICENSE VALIDATION
# ═══════════════════════════════════════════════════════════════════

@api.get("/api/license/status")
async def license_status():
    """Check current license status."""
    from sozawen.license import check_license, get_license_key
    valid, msg = check_license()
    return JSONResponse({"valid": valid, "message": msg, "key": get_license_key()})

@api.post("/api/license/activate")
async def license_activate(request: Request):
    """Activate a license key."""
    from sozawen.license import activate_key
    data = await request.json()
    key = str(data.get("key") or "").strip()
    if not key:
        return JSONResponse({"valid": False, "message": "No key provided"})
    valid, msg = activate_key(key)
    return JSONResponse({"valid": valid, "message": msg})


# ═══════════════════════════════════════════════════════════════════
# COMMUNITY & FEEDBACK
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/feedback")
async def submit_feedback(request: Request):
    """Store user feedback locally. Can be reviewed and forwarded."""
    data = await request.json()
    fb_type = data.get("type", "feedback")
    text = data.get("text", "").strip()
    email = data.get("email", "")
    version = data.get("version", "")

    if not text:
        return JSONResponse({"error": "No feedback text"}, status_code=400)

    # Sanitize type for filename safety
    import re
    fb_type = re.sub(r'[^a-zA-Z0-9_-]', '', str(fb_type))[:20] or "feedback"

    # Store locally
    feedback_dir = BASE_DIR / "feedback"
    feedback_dir.mkdir(exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    feedback_file = feedback_dir / f"{fb_type}_{timestamp}.json"

    feedback_data = {
        "type": fb_type,
        "text": text,
        "email": email,
        "version": version,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        feedback_file.write_text(json.dumps(feedback_data, indent=2))
        logger.info("Feedback saved: %s", feedback_file.name)
        return JSONResponse({"ok": True, "message": "Thank you for your feedback!"})
    except Exception as e:
        logger.error("Failed to save feedback: %s", e)
        return JSONResponse({"error": "Could not save feedback"}, status_code=500)


@api.post("/api/browse-folder")
async def browse_folder(request: Request):
    """List audio files in a folder for the sample browser."""
    data = await request.json()
    folder = data.get("path", "")

    if not folder or not Path(folder).is_dir():
        return JSONResponse({"error": "Invalid folder"}, status_code=400)

    audio_exts = {'.wav', '.mp3', '.flac', '.ogg', '.aiff', '.m4a', '.wma'}
    files = []
    try:
        for f in sorted(Path(folder).iterdir()):
            if f.is_file() and f.suffix.lower() in audio_exts:
                size = f.stat().st_size
                size_str = f"{size/1024:.0f}KB" if size < 1024*1024 else f"{size/1024/1024:.1f}MB"
                files.append({"name": f.name, "path": str(f), "size": size_str})
    except PermissionError:
        return JSONResponse({"error": "Permission denied"}, status_code=403)

    return JSONResponse({"files": files, "count": len(files)})

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


# ═══════════════════════════════════════════════════════════════════
# SHEET MUSIC & TABLATURE
# ═══════════════════════════════════════════════════════════════════

@api.get("/api/sheet/tunings")
async def list_tunings(instrument: str = None):
    """List available instrument tunings."""
    from sozawen.sheet_music import list_tunings
    return JSONResponse({"tunings": list_tunings(instrument)})

@api.post("/api/sheet/tab-to-notation")
async def tab_to_notation(request: Request):
    """Convert tablature text to standard notation SVG."""
    data = await request.json()
    tab_text = data.get("tab", "")
    tuning = data.get("tuning", "guitar_standard")
    key = data.get("key", "C")
    time_sig = data.get("time_sig", "4/4")

    from sozawen.sheet_music import tab_to_notes, render_notation_svg, choose_clef
    events = tab_to_notes(tab_text, tuning)
    if not events:
        return JSONResponse({"ok": False, "error": "No notes found in tab"})

    clef = choose_clef(events)
    svg = render_notation_svg(events, key=key, time_sig=time_sig, clef=clef)
    return JSONResponse({
        "ok": True,
        "svg": svg,
        "notes": len(events),
        "clef": clef,
        "events": [
            {"notes": [{"note": n["note"], "octave": n["octave"],
                        "fret": n.get("fret"), "string": n.get("string")}
                       for n in e["notes"]],
             "beat": e["beat"]}
            for e in events[:100]
        ],
    })

@api.post("/api/sheet/notes-to-tab")
async def notation_to_tab(request: Request):
    """Convert standard notation to tablature."""
    data = await request.json()
    notes = data.get("notes", [])  # [{note, octave}, ...]
    tuning = data.get("tuning", "guitar_standard")

    from sozawen.sheet_music import notes_to_tab
    # Wrap single notes into events format
    events = [{"notes": [n]} if "notes" not in n else n for n in notes]
    tab = notes_to_tab(events, tuning)
    return JSONResponse({"ok": True, "tab": tab})

@api.post("/api/sheet/render")
async def render_sheet(request: Request):
    """Render a list of note events as SVG sheet music."""
    data = await request.json()
    events = data.get("events", [])
    key = data.get("key", "C")
    time_sig = data.get("time_sig", "4/4")
    clef = data.get("clef")
    width = int(data.get("width", 800))

    from sozawen.sheet_music import render_notation_svg
    svg = render_notation_svg(events, key=key, time_sig=time_sig, clef=clef, width=width)
    return JSONResponse({"ok": True, "svg": svg})

@api.post("/api/sheet/audio-to-notation")
async def audio_to_notation(request: Request):
    """Transcribe recorded audio to sheet music.

    Uses audio-to-MIDI pipeline then renders as notation.
    Play into the mic → see sheet music appear.
    """
    data = await request.json()
    file_path = data.get("file")
    key = data.get("key", "C")
    tuning = data.get("tuning", "guitar_standard")

    if not file_path or not Path(file_path).exists():
        return JSONResponse({"ok": False, "error": "File not found"})

    try:
        from sozawen.midi_engine import audio_to_midi
        from sozawen.sheet_music import render_notation_svg, notes_to_tab, choose_clef

        # Audio → MIDI notes
        midi_result = audio_to_midi(str(file_path))
        if not midi_result or not midi_result.get("notes"):
            return JSONResponse({"ok": False, "error": "No notes detected in audio"})

        # Convert MIDI notes to sheet music events
        from sozawen.music_theory import midi_to_note
        events = []
        for note in midi_result["notes"]:
            midi_num = note.get("midi", 60)
            note_name, octave = midi_to_note(midi_num)
            events.append({
                "notes": [{"note": note_name, "octave": octave, "midi": midi_num}],
                "beat": len(events),
            })

        clef = choose_clef(events)
        svg = render_notation_svg(events, key=key, clef=clef)
        tab = notes_to_tab(events, tuning)

        return JSONResponse({
            "ok": True,
            "svg": svg,
            "tab": tab,
            "notes_detected": len(events),
            "clef": clef,
        })

    except Exception as e:
        logger.error(f"Audio to notation error: {e}")
        return JSONResponse({"ok": False, "error": str(e)})

@api.post("/api/sheet/orchestral")
async def render_orchestral(request: Request):
    """Render a multi-staff orchestral score."""
    data = await request.json()
    parts = data.get("parts", [])
    key = data.get("key", "C")
    time_sig = data.get("time_sig", "4/4")
    width = int(data.get("width", 900))

    from sozawen.sheet_music import render_orchestral_score
    svg = render_orchestral_score(parts, key=key, time_sig=time_sig, width=width)
    return JSONResponse({"ok": True, "svg": svg, "parts": len(parts)})

@api.post("/api/sheet/midi-to-notation")
async def midi_to_notation(request: Request):
    """Convert MIDI data to sheet music + tab."""
    data = await request.json()
    midi_notes = data.get("notes", [])  # [{midi: 60, duration: 0.5}, ...]
    key = data.get("key", "C")
    tuning = data.get("tuning", "guitar_standard")

    from sozawen.sheet_music import render_notation_svg, notes_to_tab, choose_clef
    from sozawen.music_theory import midi_to_note

    events = []
    for n in midi_notes:
        midi_num = n.get("midi", 60)
        note_name, octave = midi_to_note(midi_num)
        events.append({
            "notes": [{"note": note_name, "octave": octave, "midi": midi_num}],
            "beat": len(events),
        })

    clef = choose_clef(events)
    svg = render_notation_svg(events, key=key, clef=clef)
    tab = notes_to_tab(events, tuning)

    return JSONResponse({
        "ok": True,
        "svg": svg,
        "tab": tab,
        "notes": len(events),
        "clef": clef,
    })


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
        url="http://127.0.0.1:8090/static/app.html",
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
