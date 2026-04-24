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
import time
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
    """Scan for VST3 and CLAP plugins on the system. Pedalboard loads both."""
    import glob
    search_roots = [
        # VST3
        ("VST3", "C:/Program Files/Common Files/VST3"),
        ("VST3", "C:/Program Files (x86)/Common Files/VST3"),
        ("VST3", str(Path.home() / ".vst3")),
        # CLAP
        ("CLAP", "C:/Program Files/Common Files/CLAP"),
        ("CLAP", "C:/Program Files (x86)/Common Files/CLAP"),
        ("CLAP", str(Path.home() / ".clap")),
    ]
    exts = {"VST3": "*.vst3", "CLAP": "*.clap"}

    plugins = []
    paths_searched = []
    for kind, search_path in search_roots:
        paths_searched.append(search_path)
        if not Path(search_path).exists():
            continue
        for plug_file in glob.glob(f"{search_path}/**/{exts[kind]}", recursive=True):
            name = Path(plug_file).stem
            plugins.append({
                "name": name,
                "path": plug_file,
                "type": kind,
                "loaded": False,
            })

    return JSONResponse({
        "plugins": plugins,
        "count": len(plugins),
        "scan_paths": paths_searched,
        "note": "Plugins can be inserted on a selected track via the Plugins panel. CLAP and VST3 both supported."
    })

@api.post("/api/sheet/export-musicxml")
async def export_score_musicxml(request: Request):
    """Export current score to a MusicXML (.musicxml) file, compatible with
    MuseScore, Finale, Sibelius, Dorico, Flat.io, and every notation editor
    on the market."""
    from music21 import stream, note as m21note, chord as m21chord, meter, key as m21key, tempo
    data = await request.json()
    events = data.get("events", [])
    key_name = data.get("key", "C")
    time_sig = data.get("time_sig", "4/4")
    bpm = data.get("bpm", 120)

    s = stream.Stream()
    try:
        s.insert(0, m21key.Key(key_name))
    except Exception:
        pass
    try:
        num, den = time_sig.split("/")
        s.insert(0, meter.TimeSignature(f"{num}/{den}"))
    except Exception:
        pass
    s.insert(0, tempo.MetronomeMark(number=bpm))

    for ev in events:
        pitches = ev.get("pitches") or [ev.get("pitch", 60)]
        beat = float(ev.get("beat", 0))
        dur = float(ev.get("duration", 1))  # in quarter notes
        vel = int(ev.get("velocity", 80))

        if len(pitches) == 1:
            n = m21note.Note(int(pitches[0]), quarterLength=dur)
        else:
            n = m21chord.Chord([int(p) for p in pitches], quarterLength=dur)
        n.volume.velocity = vel
        n.offset = beat
        s.insert(beat, n)

    out_path = str(BASE_DIR / "temp" / "score_export.musicxml")
    Path(out_path).parent.mkdir(exist_ok=True)
    s.write("musicxml", fp=out_path)
    return JSONResponse({"ok": True, "path": out_path})


@api.post("/api/sheet/import-musicxml")
async def import_score_musicxml(request: Request):
    """Import a MusicXML file. Returns Sozawen-compatible events list."""
    from music21 import converter, chord as m21chord, note as m21note
    data = await request.json()
    path = data.get("path", "")
    if not path or not Path(path).exists():
        return JSONResponse({"error": "File not found"}, status_code=400)
    try:
        s = converter.parse(path)
    except Exception as e:
        return JSONResponse({"error": f"Parse failed: {e}"}, status_code=500)
    events = []
    for n in s.flatten().notes:
        offset = float(n.offset)
        dur = float(n.quarterLength)
        vel = getattr(getattr(n, "volume", None), "velocity", None) or 80
        if isinstance(n, m21chord.Chord):
            pitches = [int(p.midi) for p in n.pitches]
        elif isinstance(n, m21note.Note):
            pitches = [int(n.pitch.midi)]
        else:
            continue
        events.append({
            "beat": offset,
            "duration": dur,
            "pitches": pitches,
            "velocity": vel,
        })
    # Grab metadata
    try:
        key_name = s.analyze("key").tonic.name
    except Exception:
        key_name = "C"
    try:
        ts = next(s.flatten().getElementsByClass("TimeSignature"))
        time_sig = f"{ts.numerator}/{ts.denominator}"
    except Exception:
        time_sig = "4/4"
    try:
        mm = next(s.flatten().getElementsByClass("MetronomeMark"))
        bpm = float(mm.number) if mm.number else 120.0
    except Exception:
        bpm = 120.0

    return JSONResponse({"ok": True, "events": events,
                         "key": key_name, "time_sig": time_sig, "bpm": bpm,
                         "count": len(events)})


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
    the groove of the source audio. If replace_source is set, the
    detected pattern is rendered back to audio and replaces the track.
    """
    import asyncio
    data = await request.json()
    track_id = data.get("track_id")
    sensitivity = float(data.get("sensitivity", 5))  # 1..10 — higher detects more
    replace_source = bool(data.get("replace_source", False))

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

            # Peak picking — find onset times. Sensitivity lowers threshold.
            threshold = max(0.05, 0.5 - 0.04 * sensitivity)
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

        # Convert to a 16-step grid for the drum machine
        grid_pattern = {"kick": [0]*16, "snare": [0]*16, "hihat_closed": [0]*16}
        for hit in pattern:
            step = int(round(hit["beat"] * 4)) % 16
            key_name = {"kick": "kick", "snare": "snare",
                        "hihat": "hihat_closed"}.get(hit["sound"], "snare")
            grid_pattern[key_name][step] = 1

        response = {"ok": True, "pattern": pattern, "grid_pattern": grid_pattern,
                    "hits": len(pattern), "steps": 16,
                    "notes": int(sum(sum(v) for v in grid_pattern.values())),
                    "message": f"Detected {len(pattern)} hits"}

        if replace_source:
            try:
                from sozawen.instruments import render_drum_pattern
                import numpy as _np
                region = track.regions[0]
                region._ensure_cached()
                sr = region.sample_rate or 44100
                bpm = _engine.bpm or 120
                rendered = render_drum_pattern(grid_pattern, sr=sr, bpm=bpm)
                output_path = str(BASE_DIR / "temp" / f"a2d_{track_id}.wav")
                Path(output_path).parent.mkdir(exist_ok=True)
                if rendered.ndim == 1:
                    rendered = _np.column_stack([rendered, rendered])
                sf.write(output_path, rendered, int(sr))
                track.regions.clear()
                track.add_region(output_path, source_type="generated")
                response["replaced"] = True
            except Exception as e:
                response["warn"] = f"Detected but could not render replacement: {e}"

        return JSONResponse(response)
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
    # Session reset also clears undo history — there's no coherent pre-state to go back to
    _cmds.history().clear()
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
    tool_id = data.get("tool_id")  # set when action == "select_tool"
    engine_state = _engine.get_state()
    # Track tool usage timestamp so suggestions rotate — recently-used tools
    # fall in weight, unused tools bubble up over time.
    if tool_id:
        import time as _t
        _context.state.tool_last_used[tool_id] = _t.time()
    return JSONResponse(_context.update(engine_state, action=action))

@api.post("/api/track/add")
async def api_add_track(request: Request):
    data = await request.json()
    name = data.get("name", "")
    file_path = data.get("file_path", "")
    track_type = data.get("type", "audio")
    color = data.get("color")
    if track_type not in ("audio", "bus", "master", "folder", "vca"):
        track_type = "audio"
    _cmds.record_before(_engine, f"Add {track_type} track")
    track = _engine.add_track(name=name, track_type=track_type, color=color)
    if file_path and Path(file_path).exists() and track_type == "audio":
        track.add_region(file_path, source_type="imported")
    return JSONResponse({"ok": True, "track_id": track.id, "name": track.name, "type": track_type})

@api.post("/api/track/{track_id}/automation")
async def set_track_automation(track_id: int, request: Request):
    """Push an automation curve from the frontend to a track.

    Body: {param: "volume" | "pan", points: [{time: samples, value: float}, ...]}
    The engine's Track.read_at interpolates this curve during playback/mixdown.
    """
    data = await request.json()
    param = data.get("param", "volume")
    points = data.get("points", [])
    track = _engine.tracks.get(track_id)
    if not track:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    if not hasattr(track, "automation") or track.automation is None:
        track.automation = {}
    # Validate + sort
    clean_points = []
    for p in points:
        try:
            clean_points.append({"time": int(p.get("time", 0)), "value": float(p.get("value", 0))})
        except Exception:
            continue
    clean_points.sort(key=lambda p: p["time"])
    if param in ("volume", "pan"):
        track.automation[param] = clean_points
    else:
        # allow any param name — we only read volume and pan but the shape is open
        track.automation[param] = clean_points
    return JSONResponse({"ok": True, "param": param, "count": len(clean_points)})


@api.get("/api/track/{track_id}/automation")
async def get_track_automation(track_id: int, param: str = "volume"):
    track = _engine.tracks.get(track_id)
    if not track:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    auto = getattr(track, "automation", None) or {}
    return JSONResponse({"ok": True, "param": param, "points": auto.get(param, [])})


@api.post("/api/track/{track_id}/clip/{region_index}/gain")
async def set_clip_gain(track_id: int, region_index: int, request: Request):
    """Per-clip gain. gain_db is applied as a linear multiplier to every
    sample this region produces — independent of the track fader."""
    data = await request.json()
    gain_db = float(data.get("gain_db", 0.0))
    track = _engine.tracks.get(track_id)
    if not track:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    if region_index < 0 or region_index >= len(track.regions):
        return JSONResponse({"error": "Region index out of range"}, status_code=404)
    import math as _math
    _cmds.record_before(_engine, f"Clip gain on {track.name}")
    track.regions[region_index].gain = float(10 ** (gain_db / 20.0))
    return JSONResponse({"ok": True, "gain_db": gain_db, "gain_linear": track.regions[region_index].gain})


@api.get("/api/track/{track_id}/clips")
async def list_track_clips(track_id: int):
    """List every region on a track with its current gain (in dB)."""
    track = _engine.tracks.get(track_id)
    if not track:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    import math as _math
    clips = []
    for i, r in enumerate(track.regions):
        try:
            g_lin = float(getattr(r, "gain", 1.0))
            g_db = 20.0 * _math.log10(max(g_lin, 1e-6))
        except Exception:
            g_db = 0.0
        clips.append({
            "index": i,
            "name": getattr(r, "name", ""),
            "source_path": getattr(r, "source_path", ""),
            "gain_db": round(g_db, 2),
            "start_sample": getattr(r, "start_sample", 0),
            "track_offset": getattr(r, "track_offset", 0),
            "length": getattr(r, "length", 0),
            "muted": getattr(r, "muted", False),
        })
    return JSONResponse({"ok": True, "clips": clips})


@api.post("/api/track/{track_id}/vca-parent")
async def set_track_vca_parent(track_id: int, request: Request):
    """Assign (or clear, with null) a VCA parent track. The VCA's fader will
    proportionally scale this track's volume during mixdown/export."""
    data = await request.json()
    parent_id = data.get("parent_id")  # int or None
    track = _engine.tracks.get(track_id)
    if not track:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    if parent_id is not None:
        parent_id = int(parent_id)
        if parent_id == track_id:
            return JSONResponse({"error": "Cannot assign a track as its own VCA parent"}, status_code=400)
        if parent_id not in _engine.tracks:
            return JSONResponse({"error": "VCA parent track not found"}, status_code=404)
        if _engine.tracks[parent_id].track_type != "vca":
            return JSONResponse({"error": "Target is not a VCA track"}, status_code=400)
    _cmds.record_before(_engine, f"VCA assign {track.name}")
    track.vca_parent_id = parent_id
    return JSONResponse({"ok": True, "vca_parent_id": parent_id})


@api.get("/api/mixer/snapshot")
async def mixer_snapshot():
    """Return a compact mixer view of every track — used by the Mixer panel."""
    tracks = []
    for t in _engine.tracks.values():
        tracks.append({
            "id": t.id,
            "name": t.name,
            "type": getattr(t, "track_type", "audio"),
            "color": getattr(t, "color", "#9b59b6"),
            "volume": float(t.volume),
            "pan": float(t.pan),
            "muted": bool(t.muted),
            "solo": bool(t.solo),
            "vca_parent_id": getattr(t, "vca_parent_id", None),
            "fx_count": len(getattr(t, "fx_chain", []) or []),
        })
    return JSONResponse({"ok": True, "tracks": tracks})


@api.post("/api/track/{track_id}/color")
async def set_track_color(track_id: int, request: Request):
    data = await request.json()
    color = data.get("color")
    track = _engine.tracks.get(track_id)
    if not track or not color:
        return JSONResponse({"error": "Track or color missing"}, status_code=400)
    _cmds.record_before(_engine, f"Color {track.name}")
    track.color = color
    return JSONResponse({"ok": True, "color": color})


@api.post("/api/track/{track_id}/volume")
async def set_track_volume(track_id: int, request: Request):
    data = await request.json()
    track = _engine.tracks.get(track_id)
    if track:
        _cmds.record_before(_engine, f"Volume {track.name}")
        track.volume = data.get("volume", 1.0)
        return JSONResponse({"ok": True})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/mute")
async def toggle_track_mute(track_id: int):
    track = _engine.tracks.get(track_id)
    if track:
        _cmds.record_before(_engine, f"{'Unmute' if track.muted else 'Mute'} {track.name}")
        track.muted = not track.muted
        return JSONResponse({"ok": True, "muted": track.muted})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/solo")
async def toggle_track_solo(track_id: int):
    track = _engine.tracks.get(track_id)
    if track:
        _cmds.record_before(_engine, f"{'Unsolo' if track.solo else 'Solo'} {track.name}")
        track.solo = not track.solo
        return JSONResponse({"ok": True, "solo": track.solo})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.delete("/api/track/{track_id}")
async def delete_track(track_id: int):
    """Remove a track completely."""
    if track_id in _engine.tracks:
        name = _engine.tracks[track_id].name
        _cmds.record_before(_engine, f"Delete {name}")
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
        _cmds.record_before(_engine, f"Move {track.name}")
        for region in track.regions:
            region.track_offset = offset_samples
        return JSONResponse({"ok": True, "offset_samples": offset_samples})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/remove")
async def remove_track(track_id: int):
    """Remove a track (POST variant for compatibility)."""
    if track_id in _engine.tracks:
        name = _engine.tracks[track_id].name
        _cmds.record_before(_engine, f"Remove {name}")
        del _engine.tracks[track_id]
        return JSONResponse({"ok": True})
    return JSONResponse({"error": "Track not found"}, status_code=404)

@api.post("/api/track/{track_id}/pan")
async def set_track_pan(track_id: int, request: Request):
    data = await request.json()
    track = _engine.tracks.get(track_id)
    if track:
        _cmds.record_before(_engine, f"Pan {track.name}")
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
    apply_noise_reduction, apply_click_removal, measure_loudness, export_mix,
    apply_distortion, apply_parallel_compression,
    apply_chorus, apply_flanger, apply_phaser, apply_tremolo,
    apply_multiband_eq, apply_multiband_compressor)
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
        "distortion": lambda: apply_distortion(source_path, **params),
        "parallel_compression": lambda: apply_parallel_compression(source_path, **params),
        "chorus": lambda: apply_chorus(source_path, **params),
        "flanger": lambda: apply_flanger(source_path, **params),
        "phaser": lambda: apply_phaser(source_path, **params),
        "tremolo": lambda: apply_tremolo(source_path, **params),
        "multiband_eq": lambda: apply_multiband_eq(source_path, **params),
        "multiband_compressor": lambda: apply_multiband_compressor(source_path, **params),
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

# Platform presets — target LUFS + format + sample rate per service. Source:
# Spotify/Apple Music/YouTube public loudness guidelines; CD is Red Book.
PLATFORM_PRESETS = {
    "spotify":     {"format": "mp3",  "sample_rate": 44100, "lufs": -14.0, "dither": "tpdf",
                    "bit_depth": 16, "note": "Spotify normalizes to -14 LUFS integrated."},
    "apple_music": {"format": "aac",  "sample_rate": 44100, "lufs": -16.0, "dither": "tpdf",
                    "bit_depth": 16, "note": "Apple Music uses Sound Check -16 LUFS by default."},
    "youtube":     {"format": "wav",  "sample_rate": 48000, "lufs": -14.0, "dither": "tpdf",
                    "bit_depth": 24, "note": "YouTube normalizes -14 LUFS. 48kHz/24-bit is the sweet spot."},
    "soundcloud":  {"format": "mp3",  "sample_rate": 44100, "lufs": -14.0, "dither": "tpdf",
                    "bit_depth": 16, "note": "SoundCloud transcodes to 128 kbps MP3 internally."},
    "cd":          {"format": "wav",  "sample_rate": 44100, "lufs": -9.0,  "dither": "tpdf",
                    "bit_depth": 16, "note": "Red Book CD: 44.1 kHz / 16-bit. Loudness typically -9 to -11 LUFS."},
    "mastering":   {"format": "wav",  "sample_rate": 48000, "lufs": None,  "dither": "none",
                    "bit_depth": 24, "note": "No loudness normalization, no dither — ready for a mastering engineer."},
}


@api.get("/api/export/platforms")
async def get_export_platforms():
    """Return available platform presets for the export UI."""
    return JSONResponse({"ok": True, "presets": PLATFORM_PRESETS})


def _apply_dither(audio, method="tpdf", bit_depth=16):
    """Apply dither before bit-depth reduction. Reduces quantization distortion.

    - tpdf: Triangular PDF dither (standard, widest applicability)
    - rectangular: Simple rectangular PDF (older / lighter noise floor)
    - highpass: TPDF followed by a gentle high-pass so dither noise is less audible
    - none: no dither (use for intermediate files that will be processed further)
    """
    import numpy as _np
    if method in (None, "", "none"):
        return audio
    scale = float(2 ** (bit_depth - 1))
    noise_amp = 1.0 / scale
    if method == "rectangular":
        noise = _np.random.uniform(-noise_amp, noise_amp, audio.shape).astype(audio.dtype)
    elif method == "highpass":
        # TPDF then first-order difference (trivial HPF of white noise)
        n1 = _np.random.uniform(-noise_amp, noise_amp, audio.shape).astype(audio.dtype)
        n2 = _np.random.uniform(-noise_amp, noise_amp, audio.shape).astype(audio.dtype)
        tpdf = n1 + n2
        noise = _np.diff(tpdf, axis=0, prepend=0).astype(audio.dtype)
    else:  # tpdf default
        n1 = _np.random.uniform(-noise_amp, noise_amp, audio.shape).astype(audio.dtype)
        n2 = _np.random.uniform(-noise_amp, noise_amp, audio.shape).astype(audio.dtype)
        noise = n1 + n2
    return audio + noise


def _apply_lufs_target(audio, target_lufs, sample_rate):
    """Gain-adjust audio so integrated LUFS matches target. Skips if target None."""
    if target_lufs is None:
        return audio
    try:
        import pyloudnorm as pyln
        import numpy as _np
        meter = pyln.Meter(sample_rate)
        # pyloudnorm expects stereo as (n, 2) or mono as (n,)
        measured = meter.integrated_loudness(audio)
        if measured == float("-inf"):
            return audio
        gain_db = target_lufs - measured
        gain = 10.0 ** (gain_db / 20.0)
        return _np.clip(audio * gain, -1.0, 1.0).astype(audio.dtype)
    except Exception as e:
        logger.warning("LUFS targeting failed: %s", e)
        return audio


@api.post("/api/export")
async def export_audio(request: Request):
    """Export the mix to a file.

    Supports:
    - format: wav, mp3, flac, aac, ogg
    - sample_rate: 44100, 48000, 88200, 96000, 192000
    - bit_depth: 16, 24, 32 (WAV/FLAC only)
    - dither: none, tpdf (default), rectangular, highpass
    - platform_preset: spotify, apple_music, youtube, soundcloud, cd, mastering
      (overrides format/sample_rate/bit_depth/dither/lufs to service standards)
    - target_lufs: explicit loudness target in LUFS (applied before dither)
    """
    import numpy as _np
    data = await request.json()

    preset_name = data.get("platform_preset")
    preset = PLATFORM_PRESETS.get(preset_name, {}) if preset_name else {}

    format = preset.get("format") or data.get("format", "wav")
    sample_rate = int(preset.get("sample_rate") or data.get("sample_rate", 44100))
    bit_depth = int(preset.get("bit_depth") or data.get("bit_depth", 24))
    dither = preset.get("dither", data.get("dither", "tpdf" if bit_depth < 32 else "none"))
    target_lufs = preset.get("lufs") if preset_name else data.get("target_lufs")

    # Collect all track audio — including VCA parent scaling
    tracks_audio = []
    for track in _engine.tracks.values():
        if track.muted or track.track_type in ("bus", "master", "vca"):
            continue
        scale = _vca_scale(track)
        for region in track.regions:
            region._ensure_cached()
            if region._cache is not None:
                audio = region._cache * track.volume * scale
                tracks_audio.append(audio)

    if not tracks_audio:
        return JSONResponse({"error": "No audio to export"}, status_code=400)

    # Mix down to single stereo array
    max_len = max(a.shape[0] for a in tracks_audio)
    mixed = _np.zeros((max_len, 2), dtype=_np.float32)
    for a in tracks_audio:
        if a.ndim == 1:
            a = _np.column_stack([a, a])
        elif a.shape[1] == 1:
            a = _np.column_stack([a, a])
        mixed[: a.shape[0]] += a[:, :2]

    # LUFS targeting first, then dither before bit-depth reduction
    mixed = _apply_lufs_target(mixed, target_lufs, sample_rate)
    if bit_depth < 32 and format in ("wav", "flac"):
        mixed = _apply_dither(mixed, method=dither, bit_depth=bit_depth)

    music_dir = Path.home() / "Music"
    music_dir.mkdir(exist_ok=True)
    output_path = str(music_dir / f"sozawen_export.{format}")

    try:
        # WAV / FLAC via soundfile for direct bit-depth control
        if format in ("wav", "flac"):
            subtype = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}.get(bit_depth, "PCM_24")
            sf.write(output_path, mixed, sample_rate, subtype=subtype, format=format.upper())
        elif format in ("mp3", "aac", "ogg", "m4a"):
            # Compressed formats via pydub + ffmpeg
            import pydub
            import io
            # Convert to 16-bit PCM first (pydub baseline)
            pcm16 = (_np.clip(mixed, -1.0, 1.0) * 32767).astype(_np.int16)
            seg = pydub.AudioSegment(
                pcm16.tobytes(), frame_rate=sample_rate, sample_width=2,
                channels=2,
            )
            # Output format mapping
            pydub_format = {"mp3": "mp3", "aac": "mp4", "m4a": "mp4", "ogg": "ogg"}.get(format, format)
            export_kwargs = {"format": pydub_format}
            if format == "mp3":
                export_kwargs["bitrate"] = data.get("mp3_bitrate", "320k")
            elif format in ("aac", "m4a"):
                export_kwargs["bitrate"] = data.get("aac_bitrate", "256k")
                export_kwargs["codec"] = "aac"
            elif format == "ogg":
                export_kwargs["bitrate"] = data.get("ogg_bitrate", "192k")
                export_kwargs["codec"] = "libvorbis"
            seg.export(output_path, **export_kwargs)
        else:
            return JSONResponse({"error": f"Unsupported format: {format}"}, status_code=400)

        return JSONResponse({
            "ok": True, "path": output_path, "format": format,
            "sample_rate": sample_rate, "bit_depth": bit_depth,
            "dither": dither, "target_lufs": target_lufs,
            "preset": preset_name, "preset_note": preset.get("note"),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# INPUT DEVICES — for recording
# ═══════════════════════════════════════════════════════════════════

APP_VERSION = "1.0.0"

@api.get("/api/version")
async def get_version():
    """Current app version."""
    return JSONResponse({"version": APP_VERSION})

@api.get("/api/update/check")
async def check_for_updates():
    """Check GitHub for the latest release version."""
    try:
        import requests as req
        r = req.get("https://api.github.com/repos/DayshaLindale/sozawen/releases/latest",
                     timeout=5, headers={"Accept": "application/vnd.github.v3+json"})
        if r.status_code == 200:
            data = r.json()
            latest = data.get("tag_name", "").lstrip("v")
            download_url = ""
            for asset in data.get("assets", []):
                if asset["name"].endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    break
            is_current = latest == APP_VERSION
            return JSONResponse({
                "current": APP_VERSION,
                "latest": latest,
                "up_to_date": is_current,
                "download_url": download_url,
                "release_notes": data.get("body", ""),
                "release_name": data.get("name", ""),
            })
        return JSONResponse({"current": APP_VERSION, "up_to_date": True, "error": "Could not check"})
    except Exception as e:
        return JSONResponse({"current": APP_VERSION, "up_to_date": True, "error": str(e)})

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

        # If target track specified, add region to that track.
        # "replace" mode clears the track's existing regions first so the
        # user can iterate on a drum part without stacking duplicates.
        if target_track_id and target_track_id in _engine.tracks:
            track = _engine.tracks[target_track_id]
            if data.get("replace"):
                track.regions = []
            track.add_region(output_path, track_offset=offset_samples, source_type="generated")
            return JSONResponse({"ok": True, "track_id": track.id,
                                 "appended": not bool(data.get("replace")),
                                 "replaced": bool(data.get("replace"))})

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
# MIDI Learn state ---------------------------------------------------------
# _midi_cc_mappings: {cc_number: {"target": "master_volume" | "track/<id>/volume" | ...,
#                                  "min": 0.0, "max": 1.0}}
_midi_cc_mappings = {}
_midi_learn_target = None  # if set, the next CC received gets mapped to this target
_midi_last_cc = None       # last CC observed (for display)

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
    """Handle incoming MIDI messages from the connected controller.

    Supports MPE (MIDI Polyphonic Expression):
    - pitchwheel per channel = per-note pitch bend (MPE uses ch 2-16 for notes)
    - aftertouch (channel pressure) = per-note pressure
    - polytouch (polyphonic aftertouch) = per-note pressure in non-MPE
    All events are appended to _midi_last_notes so the Piano Roll and recording
    can reconstruct the full expression stream."""
    global _midi_last_notes, _midi_learn_target, _midi_last_cc
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
    elif msg.type == 'pitchwheel':
        # MPE per-note pitch bend. msg.pitch is -8192..+8191
        _midi_last_notes.append({
            "type": "pitchbend",
            "channel": msg.channel,
            "value": msg.pitch / 8192.0,   # normalized -1..1
        })
    elif msg.type == 'aftertouch':
        # MPE per-note pressure (channel-level). msg.value is 0..127
        _midi_last_notes.append({
            "type": "pressure",
            "channel": msg.channel,
            "value": msg.value / 127.0,
        })
    elif msg.type == 'polytouch':
        # Polyphonic aftertouch (pre-MPE approach). msg.note + msg.value
        _midi_last_notes.append({
            "type": "pressure",
            "note": msg.note,
            "value": msg.value / 127.0,
        })
    elif msg.type == 'control_change':
        # Capture CC for learn-mode; otherwise apply any existing mapping
        cc = msg.control
        val = msg.value / 127.0  # normalize 0..1
        _midi_last_cc = {"cc": cc, "value": msg.value, "channel": msg.channel}
        if _midi_learn_target is not None:
            _midi_cc_mappings[cc] = {
                "target": _midi_learn_target,
                "min": 0.0, "max": 1.0,
            }
            _midi_learn_target = None
        elif cc in _midi_cc_mappings:
            _apply_midi_cc(_midi_cc_mappings[cc], val)
    # Keep last 100 events max
    if len(_midi_last_notes) > 100:
        _midi_last_notes = _midi_last_notes[-50:]


def _apply_midi_cc(mapping, norm_value):
    """Apply a CC value (0..1 normalized) to its mapped target."""
    target = mapping.get("target", "")
    mn = float(mapping.get("min", 0.0))
    mx = float(mapping.get("max", 1.0))
    v = mn + (mx - mn) * norm_value
    try:
        if target == "master_volume":
            if hasattr(_engine, "master_volume"):
                _engine.master_volume = v
        elif target == "tempo_bpm":
            _engine.bpm = max(20.0, min(300.0, 20.0 + norm_value * 280.0))
        elif target.startswith("track/") and target.endswith("/volume"):
            tid = int(target.split("/")[1])
            tr = _engine.tracks.get(tid)
            if tr:
                tr.volume = v * 2.0  # 0..2.0 range
        elif target.startswith("track/") and target.endswith("/pan"):
            tid = int(target.split("/")[1])
            tr = _engine.tracks.get(tid)
            if tr:
                tr.pan = (norm_value - 0.5) * 2.0  # -1..1
        elif target.startswith("track/") and target.endswith("/mute"):
            tid = int(target.split("/")[1])
            tr = _engine.tracks.get(tid)
            if tr:
                tr.muted = (norm_value > 0.5)
    except Exception as e:
        logger.warning("MIDI CC apply failed: %s", e)


@api.post("/api/midi/learn/start")
async def midi_learn_start(request: Request):
    """Arm learn-mode: the next incoming CC will be bound to `target`."""
    global _midi_learn_target
    data = await request.json()
    _midi_learn_target = data.get("target", "")
    return JSONResponse({"ok": True, "target": _midi_learn_target,
                         "hint": "Move the knob/fader on your controller now"})


@api.post("/api/midi/learn/cancel")
async def midi_learn_cancel():
    global _midi_learn_target
    _midi_learn_target = None
    return JSONResponse({"ok": True})


@api.get("/api/midi/learn/mappings")
async def midi_learn_mappings():
    return JSONResponse({
        "ok": True,
        "mappings": [{"cc": k, **v} for k, v in _midi_cc_mappings.items()],
        "learning": _midi_learn_target,
        "last_cc": _midi_last_cc,
    })


@api.post("/api/midi/learn/delete")
async def midi_learn_delete(request: Request):
    data = await request.json()
    cc = int(data.get("cc", -1))
    if cc in _midi_cc_mappings:
        del _midi_cc_mappings[cc]
    return JSONResponse({"ok": True})

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

YOU CAN USE SOZAWEN'S TOOLS DIRECTLY. Include action tags in your response and they will be executed. Use them freely — you have access to EVERY instrument, EVERY effect, and EVERY panel.

─── DRUMS ─────────────────────────────────────────────────────────────
[DRUMS genre=rock section=chorus bars=8 offset=0]  — render drum track
  genres: rock, pop, hiphop, trap, lofi, funk, disco, edm, dnb, jazz, jazz_brushes,
          reggae, latin, afrobeat, metal, punk, shuffle, gospel, rnb, indie,
          acoustic, singer_songwriter, country, waltz, ballad
  sections: verse, chorus, bridge, intro, outro, fill, build, breakdown

─── INSTRUMENT PLAYBACK — any of 62 physically-modeled instruments ────
[INSTRUMENT family=guitar model=taylor_dreadnought notes="C4 E4 G4 C5" duration=0.5 bpm=120]
[INSTRUMENT family=bass model=precision notes="E2 G2 A2 C3" technique=finger]
[INSTRUMENT family=piano model=steinway_d notes="C4,E4,G4|F4,A4,C5|G4,B4,D5" duration=1]
  notes: space-separated sequence, comma-separated for simultaneous chords,
         pipe-separated for chord progressions
  families + models:
    guitar: taylor_dreadnought, martin_dreadnought, gibson_j45, classical_nylon,
            electric_strat, electric_les_paul, acoustic_bass
    guitar amps (param amp=): clean_di, fender, marshall, vox, mesa, mesa_boogie, orange
    bass: precision, jazz, rickenbacker, stingray
    bass amps: ampeg_svt, darkglass, orange, fender, mesa, clean_di
    bass techniques (param technique=): finger, pick, slap, pop, muted
    piano: steinway_d, yamaha_cfx, bosendorfer
    keys: rhodes_mark1, rhodes_mark2, wurlitzer_200a, clavinet_d6, hammond_b3
    strings: violin, viola, cello, contrabass
    brass: trumpet, french_horn, trombone, tuba
    winds: flute, clarinet, oboe, bassoon, alto_sax, tenor_sax
    percussion: marimba, vibraphone

─── EFFECTS — apply to any track ──────────────────────────────────────
[EFFECT track=1 effect=eq hpf=80 low_gain=-3 himid_gain=2]
[EFFECT track=1 effect=compressor threshold=-18 ratio=3 attack=10 release=100]
[EFFECT track=1 effect=reverb decay=1.5 mix=0.2]
[EFFECT track=1 effect=delay time_ms=400 feedback=0.35 mix=0.25]
[EFFECT track=1 effect=distortion mode=tube drive=0.3]
[EFFECT track=1 effect=parallel_compression blend=0.3]
[EFFECT track=1 effect=chorus rate=1.5 depth=0.4]
[EFFECT track=1 effect=multiband_eq low_gain=2 lowmid_gain=-1 himid_gain=1 high_gain=0]
[EFFECT track=1 effect=multiband_compressor]
[EFFECT track=1 effect=sidechain trigger_track=2 amount=0.5]
[EFFECT track=1 effect=limiter ceiling=-1 release=100]

─── COMPOSITION & THEORY ──────────────────────────────────────────────
[CHORDS key=Am progression=Am,F,C,G]
[CHORD_SYMBOL beat=4 symbol=Cmaj7]
[TRANSPOSE track=1 semitones=5]
[QUANTIZE track=1 grid=0.25 strength=0.8]

─── TIMELINE & STRUCTURE ──────────────────────────────────────────────
[MARKER name=Chorus time=16]
[TIME_SIG bar=9 numerator=6 denominator=8]
[TEMPO beat=0 bpm=128]
[PUNCH in=8 out=12 enabled=true]

─── TRACK OPS ─────────────────────────────────────────────────────────
[TRACK action=add name="Lead Vocal" type=audio]
[TRACK action=mute id=2]
[TRACK action=volume id=1 db=-3]
[TRACK action=pan id=3 value=-0.3]
[TRACK action=position_3d id=1 x=0.5 y=0.3 z=0.6]
[TRACK action=freeze id=1]

─── MIX & MASTER ──────────────────────────────────────────────────────
[MIXER snapshot]  — save current mixer state
[VCA parent=1 child=2]
[LUFS target=-14 platform=spotify]
[SPATIAL_RENDER layout=7.1.4]

─── AUDIO TOOLS ───────────────────────────────────────────────────────
[TRANSCRIBE track=1]
[SEPARATE file_path=path channels=9]
[STRETCH track=1 rate=0.8]
[PITCH track=1 semitones=2]
[ANALYZE track=1]

─── NAVIGATION — open any tool panel for the user ─────────────────────
[OPEN tool=drums]
[OPEN tool=piano_roll]
[OPEN tool=bandmate]
  any tool_id from: drums, synth, pad, piano_roll, score, eq, compressor,
  reverb, delay, limiter, lufs, reference, export, spatial, plugins,
  sampler, melodic_seq, mixer, vca, punch, time_sig, tempo_map,
  lyrics_editor, chords, scale_ref, spectrum, metronome, tuner, tutorials,
  learn, hardware, midi_learn, midi_input — and every other tool in the app

─── LYRICS ────────────────────────────────────────────────────────────
[LYRICS title="Song Title" text="First line\nSecond line"]
[LYRIC_LINE beat=0 text="verse 1 opens here"]

HARDWARE INSERTS: Users can route audio through external gear (EQ boards, compressors, preamps, pedals). If they ask about using their hardware, walk them through:
1. Open Hardware panel → see all connected devices
2. Select the track → choose send output and return input
3. Add Insert → audio now flows through their external gear
4. Measure latency to keep everything in time
Suggest which output/input to use based on their interface.

SPATIAL AUDIO: 3D panner — position sounds in space (left/right, front/back, up/down). Binaural rendering for headphones. Open the Spatial tool and drag the dot.

VIDEO SYNC: Load a video and it plays in lockstep with the timeline. For film scoring, music videos, game audio. Pop-out window available.

PDF SCORE EXPORT: Export notation as a printable page. Ctrl+P to save as PDF. Colors inverted for paper.

VST3 PLUGINS: Scanner detects installed VST3 plugins. Once inserted on a track they process audio live during playback — their parameters expose as sliders in the Plugins panel. Bypass/remove per plugin. Save current plugin state as a preset and reload it on any track. Pedalboard is the host — any VST3 or CLAP plugin that pedalboard can load will work.

IMMERSIVE AUDIO: Full 7.1.4 (12-channel) and 5.1.2 (8-channel) rendering. Drag the dot in the Spatial Audio panel to place a track in 3D space. Render to multichannel WAV with ADM metadata sidecar (compatible with Dolby Atmos Renderer and Logic). Binaural downmix for headphones.
Channel layouts: 7.1.4 = L/R/C/LFE + Ls/Rs/Lrs/Rrs surrounds + Ltf/Rtf/Ltr/Rtr tops. 5.1.2 drops the rear surrounds and top rears. VBAP-style power-preserving panner places each source; LFE send is its own dial. NOT "Dolby Atmos" — that's a licensed trademark, we output compatible channel beds.

CYMBAL STATE MEMORY: Hi-hats, crashes, rides, chinas, and splashes remember they are still vibrating. Each mode (frequency + amplitude + phase) persists across strikes. New excitation sums with saturating nonlinearity — when the plate is already ringing at its max capacity, an additional strike adds almost nothing (physically correct — a real cymbal can't exceed steady-state vibration). Phase is preserved, so a well-timed second hit can reinforce or partially cancel existing vibration. Applies to crash/ride/ride_bell/hihat_open/china/splash in all pattern renders. Hi-hat closed/pedal stay stateless because they're percussive shorts.

9-CHANNEL STEM SEPARATION: Users can split any audio into 9 channels (vocals, kick, snare, cymbals, bass, guitar/keys low, guitar/keys mid, strings/brass, air/ambience) using spectral analysis — no AI required. If they want to isolate an instrument, suggest separation first.
[SEPARATE file_path=path] — triggers separation

═══ DEEP KNOWLEDGE — the physics and character behind each instrument ═══

GUITAR BODY PROFILES (physically modeled from modal resonance):
- Taylor Dreadnought: bright, clear, modern. Spruce top over rosewood gives a piano-like top end. Records easy, cuts in a mix. Best for pop rhythm, indie, acoustic production work.
- Martin D-28: warm, thick, piano-sustain low end. Rosewood back/sides with Sitka spruce. The bluegrass and singer-songwriter standard — Hank Williams, Johnny Cash, Dylan. Thick mids that sit under a vocal.
- Gibson J-45: punchy, midrange-forward, woody. Mahogany back/sides give grunt rather than sustain. The singer-songwriter's guitar — Dylan, Noel Gallagher, Sheryl Crow.
- Classical Nylon: wide neck, warm, rounded. No steel-string brightness. Flamenco, bossa, classical.
- Fender Stratocaster: bright, glassy, single-coil "quack" in positions 2/4. Clean cleans, articulate dirt. SRV, Gilmour, Mayer.
- Gibson Les Paul: warm, thick, sustained. Humbuckers cancel noise and push double the signal of single-coils. Shorter 24.75" scale = slinkier feel.

BASS BODY PROFILES:
- Precision: split-coil, fat and thumpy. 60% of records ever made. Motown, rock, punk. McCartney, JPJ, Dee Dee Ramone.
- Jazz: two single-coils, scooped mids, growly. Jaco, Marcus Miller, modern fingerstyle.
- StingRay: big humbucker + active 3-band EQ, aggressive. Flea, Louis Johnson slap territory.
- Rickenbacker 4003: trebly bite, piano-like clarity. Chris Squire, Geddy Lee, post-Hofner McCartney.

AMP MODELS (what breakup sounds like on each):
- fender: clean American, scooped mids, spring reverb, EL84/6V6 sweet low-volume breakup. Twin/Deluxe/Princeton.
- marshall: British crunch, pushed mids, EL34 aggression. Plexi, JCM800. Classic rock template.
- vox: British chime, EL84 compressed, treble-forward. AC30. Beatles, The Edge, Brian May.
- mesa / mesa_boogie: high-gain American, four gain stages, scooped for metal. Dual Rectifier, Mark IV.
- orange: midrangey British, chunky and woody. Stoner, doom, modern rock.
- clean_di: no amp coloration, useful for re-amping and pedal testing.

DRUM BRAND CHARACTER (modeled at shell and bearing-edge level):
- Ludwig: open, warm, resonant (Bonham, Ringo). Supraphonic 400 chrome snare, Black Beauty brass snare.
- DW: articulate, pristine, modern pop/session. Maple VLT construction.
- Gretsch: broken-in, round, vintage-voiced. Jazz standard.
- Yamaha: studio-consistent, tunes easily. Session favorite.
- Tama: dark, cutting, metal-friendly. Birch shells brighter than maple.

CYMBAL BRAND CHARACTER:
- Zildjian A: bright, cutting. Classic rock + pop default.
- Zildjian K: darker, drier, more complex. Jazz + studio.
- Paiste 2002: clear, shimmering, classic rock (Bonham, Nicko).
- Meinl Byzance: complex, dry, modern jazz + studio.
Cymbal sound is B20 alloy (80% copper, 20% tin) vs B8 (92/8 — cheaper, brighter-but-harsher). Modal frequencies + nonlinear amplitude-dependent pitch shift.

EFFECTS DEPTH:
- EQ: cut to remove problems, boost to add character. Classic carves: HPF below 80Hz on everything except kick/bass, notch 200-400Hz for mud, lift 2-4kHz for vocal presence, high shelf above 10kHz for air. Parametric bands with Q are for surgical cuts; shelves are for broad character.
- Compressor: threshold sets where it grabs, ratio sets how hard, attack controls transient preservation (fast kills snap, slow keeps it), release sets recovery. Typical vocal: -18dB threshold, 3:1 ratio, 10ms attack, 100ms release. Bus compression (2:1, slow attack) for glue.
- Reverb: decay (tail length), mix (wet/dry), pre-delay (distance from source). Short plate for vocals. Hall for orchestral. Room for drums.
- Parallel compression: duplicate a track, smash the copy with heavy compression (10:1, fast attack), blend underneath the original. Adds density without killing transients.
- Sidechain: kick triggers compressor on bass — classic EDM pump. Also used to duck pads under vocals.
- Distortion modes: tube (asymmetric soft clip, adds warmth), tape (gentle saturation + high rolloff), diode (harder clip), fuzz (heavy asymmetric saturation).
- Chorus/flanger/phaser: all LFO-modulated delay lines. Chorus is ~20ms delay, small detune. Flanger is ~1-5ms with feedback. Phaser uses allpass filters for comb-filter sweep.
- Multiband EQ/comp: splits signal at Linkwitz-Riley crossovers (phase-coherent), processes each band independently, sums.

LOUDNESS TARGETS (platform presets):
- Spotify: -14 LUFS integrated, -1 dBTP peak
- Apple Music: -16 LUFS (Sound Check), -1 dBTP
- YouTube Music: -14 LUFS, -1 dBTP
- SoundCloud: -8 to -13 LUFS tolerated, -1 dBTP
- CD mastering: -9 to -11 LUFS (no platform normalization), -0.1 dBTP
- Bandcamp: no normalization — quality matters, don't over-squash
Master panel auto-calibrates encoder settings when user picks a target.

KNOWLEDGE BASE (50 articles, all accessible via the Learn panel):
Music Theory: notes, intervals, scales, chords, circle_of_fifths, song_structure, rhythm, modulation, transposition
Recording: signal_chain, mic_placement, gain_staging, vocal_recording, drum_recording
Mixing: eq_guide, compression_guide, reverb_guide, panning_guide, mixing_order, frequency_chart, common_mistakes
Mastering: mastering_basics, loudness_standards, export_formats, reference_mixing
Instruments: guitar_types, tuning_reference, bass_guitar, drums_detailed, keyboards_piano, vocals_instrument, strings_brass_woodwinds, electronic_production, world_instruments, microphone_guide, acoustic_guitar_tones, electric_guitar_tones, amp_tones, bass_amp_tones, drum_brands
Hardware: audio_interfaces, monitors_headphones, cables_connections, acoustic_treatment, studio_budget_guide
Releasing: release_guide, copyright, export_platforms, collaboration, lyrics_protection
When a user asks a deep question ("how does compression work?", "why does Taylor sound different from Martin?"), reference the relevant article: "I can walk you through this — pull up the eq_guide article for the full story." Be concrete — quote specific values and examples.

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

    # If the user referenced a file path that isn't loaded, auto-import it
    # so the bandmate has session context to reason about. Matches Windows
    # paths (F:\..., F:/...), Git-Bash style (/f/...), and quoted paths.
    import re as _re
    file_ref = None
    msg = message or ""
    # Normalize quotes
    msg_clean = msg.replace("'", " ").replace('"', ' ')
    # Patterns: Windows drive, Git-Bash drive, UNC
    path_patterns = [
        r"([A-Za-z]):[\\/][^\s]+\.(?:mp3|wav|flac|ogg|aiff|m4a)",
        r"/([a-z])/[^\s]+\.(?:mp3|wav|flac|ogg|aiff|m4a)",
    ]
    for pat in path_patterns:
        m = _re.search(pat, msg_clean, _re.IGNORECASE)
        if m:
            raw = m.group(0)
            # Git-Bash to Windows: /f/foo -> F:/foo
            if raw.startswith('/') and len(raw) > 2 and raw[2] == '/':
                raw = f"{raw[1].upper()}:/{raw[3:]}"
            raw = raw.replace('\\', '/')
            if Path(raw).exists():
                file_ref = raw
            break
    imported_track_name = None
    if file_ref:
        # Check if this file is already a region on some track
        already = False
        for tid, tr in _engine.tracks.items():
            for r in getattr(tr, "regions", []) or []:
                if getattr(r, "source_path", None) and str(r.source_path).replace('\\','/').lower() == file_ref.lower():
                    already = True
                    break
            if already:
                break
        if not already:
            try:
                name = Path(file_ref).stem
                track = _engine.add_track(name=name, track_type="audio")
                track.add_region(file_ref, track_offset=0, source_type="file")
                imported_track_name = name
                # Refresh session context after import
                session_info.append(f"Just imported: {name} ({Path(file_ref).name})")
            except Exception as e:
                logger.debug("bandmate auto-import failed: %s", e)

    # Try Ollama first (local, free, private)
    response = await asyncio.get_event_loop().run_in_executor(
        None, lambda: _bandmate_think(system_prompt, message))

    # Parse action tags from the response so the frontend can execute them.
    # [DRUMS genre=X section=Y bars=Z offset=W] — render a drum track
    # [EFFECT track=N effect=X ...] — apply an effect
    # [CHORDS key=X progression=a,b,c] — load a chord progression
    # [MARKER name=X time=T] — add a section marker
    # [SEPARATE file_path=...] — run stem separation
    actions = []
    def _parse_kv(s):
        out = {}
        # Handles key=value and key="with spaces"
        for m_ in _re.finditer(r'(\w+)=(?:"([^"]*)"|(\S+))', s):
            out[m_.group(1)] = m_.group(2) if m_.group(2) is not None else m_.group(3)
        return out
    tag_rx = _re.compile(r'\[(DRUMS|INSTRUMENT|EFFECT|CHORDS|CHORD_SYMBOL|TRANSPOSE|QUANTIZE|'
                         r'MARKER|TIME_SIG|TEMPO|PUNCH|TRACK|MIXER|VCA|LUFS|'
                         r'SPATIAL_RENDER|TRANSCRIBE|SEPARATE|STRETCH|PITCH|'
                         r'ANALYZE|OPEN|LYRICS|LYRIC_LINE)\s+([^\]]+)\]')
    for m in tag_rx.finditer(response):
        actions.append({"type": m.group(1).lower(), "params": _parse_kv(m.group(2))})

    # ─── Backend-side execution of simple actions ─────────────────────────
    # The bandmate is a band member — it acts, not just suggests. For each
    # action we recognize, run it and attach the result. The raw response
    # still includes the tags so the frontend can ALSO render Apply buttons.
    executed = []
    for act in actions:
        t = act["type"]
        p = act["params"]
        result = {"type": t, "ok": False}
        try:
            if t == "instrument":
                # Render a sequence of notes through a physical instrument
                family = p.get("family", "piano")
                model = p.get("model", "")
                notes_spec = p.get("notes", "")
                bpm = float(p.get("bpm", "120"))
                dur = float(p.get("duration", "0.5"))
                vel = float(p.get("velocity", "0.7"))
                amp = p.get("amp", "")
                technique = p.get("technique", "")
                # Parse notes: "C4 E4 G4" (sequence) or "C4,E4,G4|F4,A4,C5" (chord progression)
                import numpy as _np
                NOTE_PC = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,
                           'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
                def _name_to_midi(n):
                    n = n.strip()
                    mm = _re.match(r'([A-G][#b]?)(-?\d+)', n)
                    if not mm: return None
                    return (int(mm.group(2)) + 1) * 12 + NOTE_PC[mm.group(1)]
                groups = notes_spec.split('|') if '|' in notes_spec else [notes_spec]
                seq = []
                for grp in groups:
                    if ',' in grp:
                        chord = [m_ for m_ in (_name_to_midi(n) for n in grp.split(',')) if m_ is not None]
                        if chord:
                            seq.append(chord)
                    else:
                        for n in grp.split():
                            mm = _name_to_midi(n)
                            if mm is not None:
                                seq.append([mm])
                if seq:
                    beat_sec = 60.0 / max(20, bpm)
                    total_dur = len(seq) * dur + 0.5
                    sr = 44100
                    out = _np.zeros(int(total_dur * sr * 2), dtype=_np.float32).reshape(-1, 2)
                    params_extra = {}
                    if amp: params_extra["amp"] = amp
                    if technique: params_extra["technique"] = technique
                    for i, chord in enumerate(seq):
                        start_sample = int(i * dur * sr)
                        for midi in chord:
                            audio = _render_instrument(family, model, midi, dur, vel, params_extra)
                            if audio is None: continue
                            if audio.ndim == 1:
                                audio = _np.column_stack([audio, audio])
                            end = min(start_sample + audio.shape[0], out.shape[0])
                            out[start_sample:end, :] += audio[:end - start_sample, :]
                    peak = float(_np.max(_np.abs(out))) or 1.0
                    if peak > 1.0:
                        out = out / peak * 0.95
                    import time as _t
                    output_path = str(BASE_DIR / "temp" / f"bandmate_inst_{int(_t.time())}.wav")
                    Path(output_path).parent.mkdir(exist_ok=True)
                    sf.write(output_path, out, sr)
                    track = _engine.add_track(name=f"{family.title()} (bandmate)")
                    track.add_region(output_path, track_offset=0, source_type="generated")
                    result["ok"] = True
                    result["track_id"] = track.id
                    result["notes_played"] = len(seq)

            elif t == "marker":
                name = p.get("name", "Marker")
                beat = float(p.get("time", p.get("beat", "0")))
                if not hasattr(_engine, "markers"):
                    _engine.markers = []
                _engine.markers.append({"name": name, "time": beat, "note": ""})
                result["ok"] = True

            elif t == "track":
                action_kind = p.get("action", "").lower()
                if action_kind == "add":
                    name = p.get("name", "Track")
                    tt = p.get("type", "audio")
                    track = _engine.add_track(name=name, track_type=tt)
                    result["ok"] = True
                    result["track_id"] = track.id
                elif action_kind in ("mute", "solo", "volume", "pan") and p.get("id"):
                    tid = int(p["id"])
                    if tid in _engine.tracks:
                        tr = _engine.tracks[tid]
                        if action_kind == "mute":
                            tr.muted = not tr.muted
                        elif action_kind == "solo":
                            tr.soloed = not getattr(tr, "soloed", False)
                        elif action_kind == "volume":
                            db = float(p.get("db", "0"))
                            tr.volume = 10 ** (db / 20.0)
                        elif action_kind == "pan":
                            tr.pan = float(p.get("value", "0"))
                        result["ok"] = True
                        result["track_id"] = tid

            elif t == "tempo":
                bpm = float(p.get("bpm", "120"))
                _engine.bpm = bpm
                result["ok"] = True
                result["bpm"] = bpm

            elif t == "time_sig":
                bar = int(p.get("bar", "0"))
                num = int(p.get("numerator", "4"))
                den = int(p.get("denominator", "4"))
                if bar == 0:
                    _engine.time_sig_num = num
                    _engine.time_sig_den = den
                else:
                    if not hasattr(_engine, "time_sig_changes"):
                        _engine.time_sig_changes = []
                    _engine.time_sig_changes.append({"bar": bar, "numerator": num, "denominator": den})
                result["ok"] = True
        except Exception as e:
            result["error"] = str(e)
            logger.debug("bandmate action %s failed: %s", t, e)
        executed.append(result)

    return JSONResponse({
        "response": response,
        "actions": actions,
        "executed": executed,
        "imported_track": imported_track_name,
    })


def _bandmate_think(system_prompt, message):
    """Query the bundled bandmate (with Ollama opt-in fallback)."""
    try:
        from sozawen import bandmate_engine
        # prefer_ollama=False: always try bundled first. This keeps the app
        # self-contained and ignores Ollama unless the user explicitly enabled it.
        return bandmate_engine.ask(system_prompt, message, prefer_ollama=False)
    except Exception as e:
        logger.debug("Bandmate engine failed: %s", e)
    return ("Bandmate unavailable. If the model hasn't been downloaded yet, "
            "open the Bandmate panel and click Download Brain (900 MB, one time).")


@api.get("/api/bandmate/status")
async def bandmate_status():
    """Report whether the bandmate model is installed and/or downloading."""
    from sozawen import bandmate_engine
    state = bandmate_engine.download_state()
    installed = bandmate_engine.model_exists()
    return JSONResponse({
        "installed": installed,
        "downloading": state.get("running", False),
        "done": state.get("done", False) or installed,
        "error": state.get("error"),
        "bytes": state.get("bytes", 0),
        "total": state.get("total", 0),
        "percent": (100.0 * state["bytes"] / max(1, state["total"])) if state.get("total") else 0.0,
        "model_path": str(bandmate_engine._active_model_path() or bandmate_engine.MODEL_PATH_USER),
        "bundled": bandmate_engine._find_bundled_model() is not None,
    })


@api.post("/api/bandmate/download")
async def bandmate_download():
    """Trigger a background download of the bandmate model."""
    from sozawen import bandmate_engine
    if bandmate_engine.model_exists():
        return JSONResponse({"ok": True, "already_installed": True})
    started = bandmate_engine.start_download_thread()
    return JSONResponse({"ok": True, "running": started})


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


# ═══════════════════════════════════════════════════════════════════
# TIME SIGNATURE CHANGES — mid-song meter shifts
# ═══════════════════════════════════════════════════════════════════

@api.get("/api/time-sig")
async def get_time_signature():
    return JSONResponse({
        "ok": True,
        "default": {"numerator": _engine.time_sig_num, "denominator": _engine.time_sig_den},
        "changes": list(getattr(_engine, "time_sig_changes", [])),
    })


@api.post("/api/time-sig/set-default")
async def set_default_time_sig(request: Request):
    """Set the project's base time signature (applies from bar 0)."""
    data = await request.json()
    num = int(data.get("numerator", 4))
    den = int(data.get("denominator", 4))
    if num < 1 or num > 32 or den not in (1, 2, 4, 8, 16, 32):
        return JSONResponse({"error": "Invalid time signature"}, status_code=400)
    _engine.time_sig_num = num
    _engine.time_sig_den = den
    return JSONResponse({"ok": True, "numerator": num, "denominator": den})


@api.post("/api/time-sig/add")
async def add_time_sig_change(request: Request):
    """Add a mid-song time signature change at a given bar."""
    data = await request.json()
    bar = int(data.get("bar", 0))
    num = int(data.get("numerator", 4))
    den = int(data.get("denominator", 4))
    if bar < 0 or num < 1 or num > 32 or den not in (1, 2, 4, 8, 16, 32):
        return JSONResponse({"error": "Invalid"}, status_code=400)
    changes = getattr(_engine, "time_sig_changes", [])
    # Replace existing change at same bar if any
    changes = [c for c in changes if c["bar"] != bar]
    changes.append({"bar": bar, "numerator": num, "denominator": den})
    changes.sort(key=lambda c: c["bar"])
    _engine.time_sig_changes = changes
    return JSONResponse({"ok": True, "changes": changes})


@api.post("/api/time-sig/delete")
async def delete_time_sig_change(request: Request):
    data = await request.json()
    bar = int(data.get("bar", -1))
    changes = [c for c in getattr(_engine, "time_sig_changes", []) if c["bar"] != bar]
    _engine.time_sig_changes = changes
    return JSONResponse({"ok": True, "changes": changes})


# ═══════════════════════════════════════════════════════════════════
# MARKERS — named cue points on the timeline
# ═══════════════════════════════════════════════════════════════════

_markers = []  # list of {id, name, time, note, color}
_marker_id_counter = 0


@api.get("/api/markers")
async def get_markers():
    return JSONResponse({"ok": True, "markers": list(_markers)})


@api.post("/api/markers/add")
async def add_marker(request: Request):
    global _marker_id_counter
    data = await request.json()
    _marker_id_counter += 1
    marker = {
        "id": _marker_id_counter,
        "name": data.get("name", f"Marker {_marker_id_counter}"),
        "time": float(data.get("time", 0.0)),
        "note": data.get("note", ""),
        "color": data.get("color", "#d4a84d"),
    }
    _markers.append(marker)
    _markers.sort(key=lambda m: m["time"])
    return JSONResponse({"ok": True, "marker": marker, "count": len(_markers)})


@api.post("/api/markers/update")
async def update_marker(request: Request):
    data = await request.json()
    mid = data.get("id")
    for m in _markers:
        if m["id"] == mid:
            for key in ("name", "time", "note", "color"):
                if key in data:
                    m[key] = data[key] if key != "time" else float(data[key])
            _markers.sort(key=lambda mm: mm["time"])
            return JSONResponse({"ok": True, "marker": m})
    return JSONResponse({"error": "Marker not found"}, status_code=404)


@api.post("/api/markers/delete")
async def delete_marker(request: Request):
    global _markers
    data = await request.json()
    mid = data.get("id")
    before = len(_markers)
    _markers = [m for m in _markers if m["id"] != mid]
    return JSONResponse({"ok": True, "removed": before - len(_markers)})


@api.post("/api/markers/clear")
async def clear_markers():
    global _markers
    _markers = []
    return JSONResponse({"ok": True})


# ═══════════════════════════════════════════════════════════════════
# UNDO / REDO
# ═══════════════════════════════════════════════════════════════════

from sozawen import commands as _cmds


@api.post("/api/undo")
async def api_undo():
    """Revert the last mutating action. Returns the label of what was undone."""
    h = _cmds.history()
    if not h.can_undo():
        return JSONResponse({"ok": False, "error": "Nothing to undo"})
    current = _cmds.snapshot_engine(_engine)
    prev = h.undo(current)
    if prev is None:
        return JSONResponse({"ok": False, "error": "Nothing to undo"})
    ok = _cmds.restore_engine(_engine, prev["snapshot"])
    return JSONResponse({"ok": ok, "label": prev["label"]})


@api.post("/api/redo")
async def api_redo():
    """Re-apply the last undone action."""
    h = _cmds.history()
    if not h.can_redo():
        return JSONResponse({"ok": False, "error": "Nothing to redo"})
    current = _cmds.snapshot_engine(_engine)
    nxt = h.redo(current)
    if nxt is None:
        return JSONResponse({"ok": False, "error": "Nothing to redo"})
    ok = _cmds.restore_engine(_engine, nxt["snapshot"])
    return JSONResponse({"ok": ok, "label": nxt["label"]})


@api.get("/api/undo/history")
async def api_undo_history():
    """Return labels for undo + redo stacks (for the history panel)."""
    h = _cmds.history()
    return JSONResponse({"ok": True, **h.labels()})


# ═══════════════════════════════════════════════════════════════════
# LYRICS SOURCE BANK — managed directory for written lyrics
# ═══════════════════════════════════════════════════════════════════

def _lyrics_dir():
    """Return the user's lyrics bank dir, creating it if needed."""
    d = Path.home() / "Documents" / "Sozawen" / "Lyrics"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sanitize_title(title):
    """Make a filesystem-safe filename stem from a title."""
    import re as _re
    safe = _re.sub(r'[^\w\s\-]', '', title).strip()
    safe = _re.sub(r'[\s]+', '_', safe)
    return safe[:80] or "untitled"


@api.get("/api/lyrics/list")
async def lyrics_list():
    """List all saved lyrics with title, modified date, and a short preview."""
    import time as _time
    d = _lyrics_dir()
    items = []
    for f in sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
            # First line is the title header "# Title"; rest is content
            title = f.stem.replace("_", " ")
            content = raw
            if raw.startswith("# "):
                first_nl = raw.find("\n")
                if first_nl > 0:
                    title = raw[2:first_nl].strip() or title
                    content = raw[first_nl + 1:].lstrip("\n")
            preview = content[:120].replace("\n", " ").strip()
            items.append({
                "id": f.stem,
                "title": title,
                "modified": int(f.stat().st_mtime),
                "modified_pretty": _time.strftime("%Y-%m-%d %H:%M",
                                                  _time.localtime(f.stat().st_mtime)),
                "preview": preview,
                "word_count": len(content.split()),
            })
        except Exception:
            continue
    return JSONResponse({"ok": True, "items": items, "dir": str(d)})


@api.get("/api/lyrics/load")
async def lyrics_load(id: str):
    """Load a saved lyric by id."""
    d = _lyrics_dir()
    f = d / f"{id}.md"
    if not f.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)
    raw = f.read_text(encoding="utf-8", errors="replace")
    title = id.replace("_", " ")
    content = raw
    if raw.startswith("# "):
        first_nl = raw.find("\n")
        if first_nl > 0:
            title = raw[2:first_nl].strip() or title
            content = raw[first_nl + 1:].lstrip("\n")
    return JSONResponse({"ok": True, "id": id, "title": title, "content": content})


@api.post("/api/lyrics/save")
async def lyrics_save(request: Request):
    """Save a lyric. If id given, overwrite that file (and rename if title changed).
    Otherwise create a new file from the title."""
    data = await request.json()
    title = (data.get("title") or "").strip() or "Untitled"
    content = data.get("content", "")
    old_id = data.get("id")

    new_id = _sanitize_title(title)
    d = _lyrics_dir()
    new_path = d / f"{new_id}.md"

    # Uniqueness: if we're creating new OR renaming and the target exists, suffix a counter
    if not old_id or new_id != old_id:
        n = 1
        base = new_id
        while new_path.exists():
            n += 1
            new_id = f"{base}_{n}"
            new_path = d / f"{new_id}.md"

    body = f"# {title}\n\n{content}"
    tmp = new_path.with_suffix(".md.tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(new_path)

    # If renaming, remove old file
    if old_id and old_id != new_id:
        old_path = d / f"{old_id}.md"
        if old_path.exists():
            try:
                old_path.unlink()
            except Exception:
                pass

    return JSONResponse({"ok": True, "id": new_id, "title": title,
                         "path": str(new_path)})


@api.post("/api/lyrics/delete")
async def lyrics_delete(request: Request):
    """Delete a saved lyric."""
    data = await request.json()
    id = data.get("id")
    if not id:
        return JSONResponse({"error": "Missing id"}, status_code=400)
    f = _lyrics_dir() / f"{id}.md"
    if f.exists():
        try:
            f.unlink()
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})


@api.post("/api/lyrics/reveal")
async def lyrics_reveal():
    """Open the lyrics directory in the OS file explorer."""
    import os as _os, subprocess as _sp, sys as _sys
    d = _lyrics_dir()
    try:
        if _sys.platform.startswith("win"):
            _os.startfile(str(d))
        elif _sys.platform == "darwin":
            _sp.Popen(["open", str(d)])
        else:
            _sp.Popen(["xdg-open", str(d)])
        return JSONResponse({"ok": True, "dir": str(d)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════════════════════════════════
# NEW ENDPOINTS — store-ready surface
# ═══════════════════════════════════════════════════════════════════

@api.post("/api/open-file")
async def api_open_file(request: Request):
    """Open a local file with the OS default handler (used by PDF export preview)."""
    data = await request.json()
    path = data.get("path", "")
    if not path or not Path(path).exists():
        return JSONResponse({"error": "Path missing"}, status_code=400)
    try:
        import os as _os, subprocess as _sp, sys as _sys
        if _sys.platform.startswith("win"):
            _os.startfile(path)
        elif _sys.platform == "darwin":
            _sp.Popen(["open", path])
        else:
            _sp.Popen(["xdg-open", path])
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def _track_plugin_latency_samples(track, sample_rate=44100):
    """Sum the plugin latencies on a track's fx_chain (in samples).
    Uses pedalboard's `plugin.latency_samples` when available.
    """
    total = 0
    for fx in getattr(track, "fx_chain", []) or []:
        if isinstance(fx, dict) and fx.get("type") == "vst3":
            plugin = fx.get("plugin")
            if plugin is None:
                continue
            try:
                latency = int(getattr(plugin, "latency_samples", 0))
            except Exception:
                latency = 0
            total += max(0, latency)
    return total


def _apply_pdc(tracks_audio_pairs, sample_rate=44100):
    """Given [(track, audio_array), ...], find the max plugin latency across
    tracks, and prepend silence to the shorter-latency tracks so they align.
    Returns the same list with audio arrays adjusted.

    tracks_audio_pairs: list of (track_object, audio_ndarray)
    """
    import numpy as _np
    if not tracks_audio_pairs:
        return tracks_audio_pairs
    latencies = [(_track_plugin_latency_samples(t, sample_rate), t, a) for (t, a) in tracks_audio_pairs]
    max_lat = max(l for l, _, _ in latencies)
    if max_lat <= 0:
        return [(t, a) for _, t, a in latencies]
    aligned = []
    for latency, t, audio in latencies:
        delay_samples = max_lat - latency
        if delay_samples > 0 and audio is not None:
            pad_shape = list(audio.shape)
            pad_shape[0] = delay_samples
            pad = _np.zeros(tuple(pad_shape), dtype=audio.dtype)
            aligned.append((t, _np.concatenate([pad, audio], axis=0)))
        else:
            aligned.append((t, audio))
    return aligned


@api.get("/api/mixer/pdc-status")
async def pdc_status():
    """Report per-track plugin latency so the user can see what PDC is doing."""
    out = []
    max_lat = 0
    for t in _engine.tracks.values():
        lat = _track_plugin_latency_samples(t)
        max_lat = max(max_lat, lat)
        out.append({
            "track_id": t.id, "name": t.name,
            "latency_samples": lat,
            "latency_ms": round(lat / 44.1, 2),
        })
    return JSONResponse({"ok": True, "max_latency_samples": max_lat,
                         "max_latency_ms": round(max_lat / 44.1, 2),
                         "tracks": out})


def _vca_scale(track):
    """Walk the VCA parent chain, return the product of parent volumes.

    If track has no VCA parent, returns 1.0. If there's a cycle (shouldn't happen),
    we stop at visited ids to avoid infinite loops.
    """
    mult = 1.0
    visited = set()
    cur = track
    while getattr(cur, "vca_parent_id", None) is not None and cur.vca_parent_id not in visited:
        visited.add(cur.vca_parent_id)
        parent = _engine.tracks.get(cur.vca_parent_id)
        if not parent:
            break
        mult *= float(getattr(parent, "volume", 1.0))
        cur = parent
    return mult


def _render_mix_mono(sample_rate=44100):
    """Render the whole session to a mono numpy array (for measurement)."""
    import numpy as _np
    tracks_audio = []
    for track in _engine.tracks.values():
        if track.muted or track.track_type in ("bus", "master"):
            continue
        scale = _vca_scale(track)
        for region in track.regions:
            region._ensure_cached()
            if region._cache is not None:
                audio = region._cache * track.volume * scale
                tracks_audio.append(audio)
    if not tracks_audio:
        return None
    max_len = max(a.shape[0] for a in tracks_audio)
    mix = _np.zeros(max_len, dtype=_np.float64)
    for a in tracks_audio:
        mono = a.mean(axis=1) if a.ndim > 1 else a
        mix[:mono.shape[0]] += mono
    return mix


@api.post("/api/mix/true-peak")
async def api_true_peak():
    """Measure true peak (inter-sample peak) via 4x oversampling."""
    import numpy as _np
    mix = _render_mix_mono()
    if mix is None:
        return JSONResponse({"error": "No audio in mix"}, status_code=400)
    try:
        from scipy.signal import resample_poly
        over = resample_poly(mix, up=4, down=1)
        peak = float(_np.max(_np.abs(over)))
        if peak < 1e-9:
            dbtp = -100.0
        else:
            dbtp = 20.0 * _np.log10(peak)
        return JSONResponse({"ok": True, "true_peak_dbtp": round(dbtp, 3),
                             "sample_peak": float(_np.max(_np.abs(mix)))})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Engine-level punch state (in-memory)
_punch_state = {"enabled": False, "punch_in": None, "punch_out": None}

@api.post("/api/transport/punch")
async def api_transport_punch(request: Request):
    """Set punch in/out points and enable/disable punch recording."""
    data = await request.json()
    _punch_state["punch_in"] = data.get("punch_in")
    _punch_state["punch_out"] = data.get("punch_out")
    _punch_state["enabled"] = bool(data.get("enabled", False))
    if hasattr(_engine, "punch_state"):
        _engine.punch_state = dict(_punch_state)
    else:
        setattr(_engine, "punch_state", dict(_punch_state))
    return JSONResponse({"ok": True, **_punch_state})

@api.get("/api/transport/punch")
async def api_transport_punch_get():
    return JSONResponse({"ok": True, **_punch_state})


@api.post("/api/sampler/render")
async def api_sampler_render(request: Request):
    """Render a list of MIDI notes through a sample-based instrument and add as a new track."""
    import asyncio
    data = await request.json()
    sample_path = data.get("sample_path", "")
    if not sample_path or not Path(sample_path).exists():
        return JSONResponse({"error": "Sample file not found"}, status_code=400)
    notes = data.get("notes", [])
    if not notes:
        return JSONResponse({"error": "No notes provided"}, status_code=400)
    root_midi = int(data.get("root_midi", 60))
    bpm = float(data.get("bpm", _engine.bpm or 120))
    attack_ms = int(data.get("attack_ms", 5))
    decay_ms = int(data.get("decay_ms", 50))
    sustain = float(data.get("sustain", 0.8))
    release_ms = int(data.get("release_ms", 150))
    loop = bool(data.get("loop", False))
    name = data.get("name", "Sampler")

    try:
        from sozawen.instruments import render_sampler_pattern
        def _do_render():
            audio = render_sampler_pattern(sample_path, notes,
                                           root_midi=root_midi, bpm=bpm,
                                           attack_ms=attack_ms, decay_ms=decay_ms,
                                           sustain=sustain, release_ms=release_ms,
                                           loop=loop, sr=44100)
            import numpy as _np, soundfile as _sf
            stereo = _np.column_stack([audio, audio])
            out_path = str(BASE_DIR / "temp" / f"sampler_{int(__import__('time').time())}.wav")
            Path(out_path).parent.mkdir(exist_ok=True)
            _sf.write(out_path, stereo, 44100)
            return out_path

        out_path = await asyncio.get_event_loop().run_in_executor(None, _do_render)
        track = _engine.add_track(name=name)
        track.add_region(out_path, source_type="generated")
        return JSONResponse({"ok": True, "track_id": track.id, "path": out_path})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@api.post("/api/midi/arpeggiate")
async def api_midi_arpeggiate(request: Request):
    """Transform chord notes into an arpeggio. Input: {notes, mode, rate_beats, octaves, gate}.
    Returns: {notes} — each {pitch, start_beat, duration_beats, velocity}."""
    from sozawen.midi_engine import MidiPattern, arpeggiate_pattern
    data = await request.json()
    notes_in = data.get("notes", [])
    pat = MidiPattern("arp-input", length_beats=data.get("length_beats", 16))
    for n in notes_in:
        pat.add_note(int(n.get("pitch", 60)), float(n.get("start_beat", 0)),
                     float(n.get("duration_beats", 0.25)), int(n.get("velocity", 100)))
    out = arpeggiate_pattern(pat,
                             mode=data.get("mode", "up"),
                             rate_beats=float(data.get("rate_beats", 0.25)),
                             octaves=int(data.get("octaves", 1)),
                             gate=float(data.get("gate", 0.9)))
    return JSONResponse({"ok": True, "notes": [
        {"pitch": n.pitch, "start_beat": n.start_beat,
         "duration_beats": n.duration_beats, "velocity": n.velocity}
        for n in out.notes]})


@api.post("/api/midi/chords")
async def api_midi_chords(request: Request):
    """Generate harmonizing chords for each melody note."""
    from sozawen.midi_engine import MidiPattern, generate_chords_from_melody
    data = await request.json()
    pat = MidiPattern("melody", length_beats=data.get("length_beats", 16))
    for n in data.get("notes", []):
        pat.add_note(int(n.get("pitch", 60)), float(n.get("start_beat", 0)),
                     float(n.get("duration_beats", 0.5)), int(n.get("velocity", 100)))
    out = generate_chords_from_melody(
        pat,
        chord_type=data.get("chord_type", "triad"),
        key=data.get("key", "C"),
        scale=data.get("scale", "major"),
        inversion=int(data.get("inversion", 0)),
        octave_offset=int(data.get("octave_offset", -1)),
    )
    return JSONResponse({"ok": True, "notes": [
        {"pitch": n.pitch, "start_beat": n.start_beat,
         "duration_beats": n.duration_beats, "velocity": n.velocity}
        for n in out.notes]})


@api.post("/api/midi/scale-force")
async def api_midi_scale_force(request: Request):
    """Snap every note to the nearest in-scale pitch."""
    from sozawen.midi_engine import MidiPattern, force_to_scale
    data = await request.json()
    pat = MidiPattern("input", length_beats=data.get("length_beats", 16))
    for n in data.get("notes", []):
        pat.add_note(int(n.get("pitch", 60)), float(n.get("start_beat", 0)),
                     float(n.get("duration_beats", 0.25)), int(n.get("velocity", 100)))
    out = force_to_scale(pat, key=data.get("key", "C"), scale=data.get("scale", "major"))
    return JSONResponse({"ok": True, "notes": [
        {"pitch": n.pitch, "start_beat": n.start_beat,
         "duration_beats": n.duration_beats, "velocity": n.velocity}
        for n in out.notes]})


@api.post("/api/midi/quantize")
async def api_midi_quantize(request: Request):
    """Quantize MIDI notes on a track to a grid. Strength 0..1, swing 0..1 (shifts offbeats)."""
    import numpy as _np
    data = await request.json()
    track_id = data.get("track_id")
    grid = float(data.get("grid", 0.25))       # beats (0.25 = 16th)
    strength = float(data.get("strength", 1.0))
    swing = float(data.get("swing", 0.0))
    if track_id is None or track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    track = _engine.tracks[track_id]
    bpm = getattr(_engine, "bpm", 120) or 120
    sec_per_beat = 60.0 / bpm
    grid_sec = grid * sec_per_beat
    # Collect midi notes across any midi regions on this track
    notes_moved = 0
    for region in getattr(track, "regions", []):
        midi_notes = getattr(region, "midi_notes", None)
        if not midi_notes:
            continue
        for n in midi_notes:
            t = float(n.get("start", n.get("time", 0.0)))
            snapped = round(t / grid_sec) * grid_sec
            # Swing: shift every other grid slot later by swing * grid_sec/2
            slot_index = int(round(snapped / grid_sec))
            if swing > 0 and slot_index % 2 == 1:
                snapped += swing * (grid_sec / 2.0)
            new_t = t + (snapped - t) * strength
            if abs(new_t - t) > 1e-6:
                notes_moved += 1
                if "start" in n:
                    n["start"] = new_t
                if "time" in n:
                    n["time"] = new_t
    return JSONResponse({"ok": True, "notes_moved": notes_moved,
                         "grid_seconds": round(grid_sec, 4)})


# Plugin loading — pedalboard bridge
_loaded_plugins = {}   # track_id -> list of (name, path, plugin)

@api.post("/api/plugins/load")
async def api_plugins_load(request: Request):
    """Insert a VST3 plugin on a track using pedalboard."""
    data = await request.json()
    track_id = data.get("track_id")
    path = data.get("path")
    name = data.get("name") or (Path(path).stem if path else "Plugin")
    if track_id is None or track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    if not path or not Path(path).exists():
        return JSONResponse({"error": "Plugin path missing"}, status_code=400)
    try:
        import pedalboard
        plugin = pedalboard.load_plugin(path)
        _loaded_plugins.setdefault(track_id, []).append(
            {"name": name, "path": path, "plugin": plugin}
        )
        # Attach to track fx_chain so the engine can process it
        track = _engine.tracks[track_id]
        if not hasattr(track, "fx_chain") or track.fx_chain is None:
            track.fx_chain = []
        track.fx_chain.append({"type": "vst3", "name": name, "path": path,
                               "plugin": plugin, "enabled": True})
        params = []
        try:
            for p_name in list(plugin.parameters.keys())[:20]:
                p = plugin.parameters[p_name]
                params.append({"name": p_name, "value": float(getattr(p, "raw_value", 0))})
        except Exception:
            pass
        return JSONResponse({"ok": True, "name": name, "parameters": params})
    except Exception as e:
        return JSONResponse({"error": f"Could not load plugin: {e}"}, status_code=500)


@api.post("/api/plugins/remove")
async def api_plugins_remove(request: Request):
    """Remove a loaded plugin from a track."""
    data = await request.json()
    track_id = data.get("track_id")
    name = data.get("name")
    if track_id is None or track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    track = _engine.tracks[track_id]
    track.fx_chain = [fx for fx in getattr(track, "fx_chain", [])
                      if not (isinstance(fx, dict) and fx.get("type") == "vst3" and fx.get("name") == name)]
    if track_id in _loaded_plugins:
        _loaded_plugins[track_id] = [p for p in _loaded_plugins[track_id] if p["name"] != name]
    return JSONResponse({"ok": True})


# Tray dock queue — popped-out tools POST here to ask the main window to re-add them
_dock_queue = []
_dock_lock = threading.Lock()

@api.post("/api/tray/dock")
async def api_tray_dock(request: Request):
    data = await request.json()
    name = data.get("name")
    if not name:
        return JSONResponse({"error": "missing name"}, status_code=400)
    with _dock_lock:
        _dock_queue.append(name)
    # Close the popout window whose title matches this tool — pywebview
    # windows are identified by title string. The main window's title
    # starts with "Sozawen — Born from the burn" so we skip it.
    try:
        import webview as _wv
        suffix = name.replace("_", " ")
        for w in list(_wv.windows):
            title = (w.title or "")
            if "Born from the burn" in title:
                continue
            if title.endswith(suffix) or f"Sozawen — {suffix}" == title:
                try:
                    w.destroy()
                except Exception:
                    pass
    except Exception as e:
        logger.debug("popout destroy skipped: %s", e)
    return JSONResponse({"ok": True})

@api.get("/api/tray/dock-pending")
async def api_tray_dock_pending():
    with _dock_lock:
        names = list(_dock_queue)
        _dock_queue.clear()
    return JSONResponse({"ok": True, "pending": names})


@api.post("/api/track/{track_id}/position-3d")
async def api_track_position_3d(track_id: int, request: Request):
    """Set a track's 3D position for immersive rendering.
    Body: {x, y, z, lfe_send}  — x=left/right, y=back/front, z=down/up, each -1..1.
    """
    data = await request.json()
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    track = _engine.tracks[track_id]
    track.position_3d = (
        float(data.get("x", 0.0)),
        float(data.get("y", 1.0)),
        float(data.get("z", 0.0)),
    )
    track.lfe_send = float(data.get("lfe_send", 0.0))
    return JSONResponse({"ok": True, "position": list(track.position_3d),
                         "lfe_send": track.lfe_send})


@api.get("/api/track/{track_id}/position-3d")
async def api_track_position_3d_get(track_id: int):
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=404)
    track = _engine.tracks[track_id]
    return JSONResponse({
        "position": list(track.position_3d) if track.position_3d else [0.0, 1.0, 0.0],
        "lfe_send": float(getattr(track, "lfe_send", 0.0)),
    })


@api.post("/api/spatial/render")
async def api_spatial_render(request: Request):
    """Render the project to an immersive multichannel WAV.

    Body: {layout: "7.1.4" | "5.1.2" | "binaural",
           output_path: optional — defaults to Documents/Sozawen/Exports/,
           include_adm: bool — also write an ADM-compatible JSON sidecar}
    """
    from sozawen.spatial_renderer import (
        render_immersive, render_binaural_downmix,
        write_multichannel_wav, write_adm_metadata, LAYOUT_7_1_4, LAYOUT_5_1_2,
    )
    data = await request.json()
    layout = data.get("layout", "7.1.4")
    include_adm = bool(data.get("include_adm", True))

    if layout not in ("7.1.4", "5.1.2", "binaural"):
        return JSONResponse({"error": "layout must be 7.1.4, 5.1.2, or binaural"}, status_code=400)

    # Figure out duration: longest track
    total_samples = 0
    for tid, track in _engine.tracks.items():
        if track.track_type == "master":
            continue
        for region in getattr(track, "regions", []) or []:
            end = getattr(region, "end_sample", 0)
            if end > total_samples:
                total_samples = end
    if total_samples <= 0:
        return JSONResponse({"error": "Project is empty"}, status_code=400)

    # Render each track to stereo with its fx_chain applied, collect for spatial render
    import numpy as _np
    tracks_with_audio = []
    for tid, track in _engine.tracks.items():
        if track.track_type in ("master", "vca"):
            continue
        buffer = _np.zeros((total_samples, 2), dtype=_np.float32)
        # Pull audio from read_at in chunks so automation + fx_chain apply
        CHUNK = 4096
        for pos in range(0, total_samples, CHUNK):
            n = min(CHUNK, total_samples - pos)
            buf = track.read_at(pos, n)
            buffer[pos:pos + n, :] = buf.astype(_np.float32)
        if _np.max(_np.abs(buffer)) < 1e-5:
            continue  # skip silent tracks
        tracks_with_audio.append({
            "name": track.name,
            "audio": buffer,
            "position": track.position_3d,
            "lfe_send": float(getattr(track, "lfe_send", 0.0)),
        })

    if not tracks_with_audio:
        return JSONResponse({"error": "All tracks are silent"}, status_code=400)

    # Decide output path
    out_dir = Path.home() / "Documents" / "Sozawen" / "Exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    default_stem = f"sozawen_immersive_{int(time.time())}"
    out_path = Path(data.get("output_path") or (out_dir / f"{default_stem}.wav"))

    if layout == "binaural":
        # Render to 7.1.4 first, then downmix
        multi = render_immersive(tracks_with_audio, 44100, "7.1.4", total_samples)
        stereo = render_binaural_downmix(multi, "7.1.4")
        write_multichannel_wav(out_path, stereo, 44100)
        result = {"path": str(out_path), "channels": 2, "layout": "binaural",
                  "samples": int(stereo.shape[0])}
    else:
        multi = render_immersive(tracks_with_audio, 44100, layout, total_samples)
        write_multichannel_wav(out_path, multi, 44100)
        result = {"path": str(out_path), "channels": multi.shape[1],
                  "layout": layout, "samples": int(multi.shape[0])}

    if include_adm and layout in ("7.1.4", "5.1.2"):
        adm_path = out_path.with_suffix(".adm.json")
        write_adm_metadata(adm_path, tracks_with_audio, layout, 44100, total_samples)
        result["adm_metadata"] = str(adm_path)

    return JSONResponse({"ok": True, **result})


@api.get("/api/plugins/list")
async def api_plugins_list(track_id: int):
    """List all VST3/CLAP plugins loaded on a track with their full parameters."""
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    track = _engine.tracks[track_id]
    out = []
    for idx, fx in enumerate(getattr(track, "fx_chain", []) or []):
        if not (isinstance(fx, dict) and fx.get("type") == "vst3"):
            continue
        plug = fx.get("plugin")
        params = []
        if plug is not None:
            try:
                for p_name in list(plug.parameters.keys()):
                    p = plug.parameters[p_name]
                    info = {"name": p_name,
                            "value": float(getattr(p, "raw_value", 0.0))}
                    # Optional metadata if pedalboard exposes it
                    for attr in ("min_value", "max_value", "units", "label"):
                        val = getattr(p, attr, None)
                        if val is not None:
                            info[attr] = val if isinstance(val, (int, float, str)) else str(val)
                    params.append(info)
            except Exception:
                pass
        out.append({
            "index": idx,
            "name": fx.get("name"),
            "path": fx.get("path"),
            "enabled": fx.get("enabled", True),
            "parameters": params,
        })
    return JSONResponse({"ok": True, "plugins": out})


@api.post("/api/plugins/set-param")
async def api_plugins_set_param(request: Request):
    """Set a single parameter on a loaded plugin.
    Body: {track_id, plugin_name, param_name, value (float 0..1 or native)}
    """
    data = await request.json()
    track_id = data.get("track_id")
    plugin_name = data.get("plugin_name")
    param_name = data.get("param_name")
    value = data.get("value")
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    track = _engine.tracks[track_id]
    for fx in getattr(track, "fx_chain", []) or []:
        if (isinstance(fx, dict) and fx.get("type") == "vst3"
                and fx.get("name") == plugin_name):
            plug = fx.get("plugin")
            if plug is None:
                return JSONResponse({"error": "Plugin instance missing"}, status_code=500)
            try:
                p = plug.parameters[param_name]
                p.raw_value = float(value)
                return JSONResponse({"ok": True,
                                     "value": float(p.raw_value)})
            except Exception as e:
                return JSONResponse({"error": f"Could not set parameter: {e}"}, status_code=500)
    return JSONResponse({"error": "Plugin not found on track"}, status_code=404)


@api.post("/api/plugins/toggle")
async def api_plugins_toggle(request: Request):
    """Enable or bypass a loaded plugin without unloading it.
    Body: {track_id, plugin_name, enabled: bool}
    """
    data = await request.json()
    track_id = data.get("track_id")
    plugin_name = data.get("plugin_name")
    enabled = bool(data.get("enabled", True))
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    track = _engine.tracks[track_id]
    for fx in getattr(track, "fx_chain", []) or []:
        if (isinstance(fx, dict) and fx.get("type") == "vst3"
                and fx.get("name") == plugin_name):
            fx["enabled"] = enabled
            return JSONResponse({"ok": True, "enabled": enabled})
    return JSONResponse({"error": "Plugin not found on track"}, status_code=404)


def _plugin_presets_dir():
    d = Path.home() / "Documents" / "Sozawen" / "PluginPresets"
    d.mkdir(parents=True, exist_ok=True)
    return d


@api.post("/api/plugins/save-preset")
async def api_plugins_save_preset(request: Request):
    """Save the current state of a loaded plugin as a preset file.

    Body: {track_id, plugin_name, preset_name}
    Returns path to saved preset.
    """
    data = await request.json()
    track_id = data.get("track_id")
    plugin_name = data.get("plugin_name")
    preset_name = (data.get("preset_name") or "preset").strip() or "preset"
    if track_id is None or track_id not in _loaded_plugins:
        return JSONResponse({"error": "No plugins loaded on that track"}, status_code=400)
    loaded = [p for p in _loaded_plugins[track_id] if p["name"] == plugin_name]
    if not loaded:
        return JSONResponse({"error": "Plugin not loaded on that track"}, status_code=404)
    plugin = loaded[0]["plugin"]
    # Sanitize filename
    import re as _re
    safe = _re.sub(r'[^\w\-]', '_', preset_name)[:80] or "preset"
    out_dir = _plugin_presets_dir() / _re.sub(r'[^\w\-]', '_', plugin_name)[:80]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{safe}.fxp"
    try:
        # pedalboard supports raw state via plugin.get_plugin_state() if exposed; else
        # fall back to snapshotting parameter values as JSON
        try:
            raw = plugin.raw_state  # pedalboard exposes this for VST3 on most hosts
            out_path.write_bytes(bytes(raw))
        except Exception:
            import json as _json
            params = {}
            try:
                for p_name in list(plugin.parameters.keys()):
                    p = plugin.parameters[p_name]
                    params[p_name] = float(getattr(p, "raw_value", 0))
            except Exception:
                pass
            out_path.write_text(_json.dumps({"type": "params", "plugin": plugin_name,
                                             "parameters": params}), encoding="utf-8")
        return JSONResponse({"ok": True, "path": str(out_path), "name": preset_name})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@api.post("/api/plugins/load-preset")
async def api_plugins_load_preset(request: Request):
    """Load a preset file into a currently-loaded plugin."""
    data = await request.json()
    track_id = data.get("track_id")
    plugin_name = data.get("plugin_name")
    preset_path = data.get("preset_path")
    if track_id is None or track_id not in _loaded_plugins:
        return JSONResponse({"error": "No plugins loaded on that track"}, status_code=400)
    if not preset_path or not Path(preset_path).exists():
        return JSONResponse({"error": "Preset file not found"}, status_code=404)
    loaded = [p for p in _loaded_plugins[track_id] if p["name"] == plugin_name]
    if not loaded:
        return JSONResponse({"error": "Plugin not loaded on that track"}, status_code=404)
    plugin = loaded[0]["plugin"]
    try:
        preset_bytes = Path(preset_path).read_bytes()
        # Try raw state first (VST3 native); fall back to param-set from JSON
        try:
            plugin.raw_state = preset_bytes
            return JSONResponse({"ok": True, "mode": "raw_state"})
        except Exception:
            import json as _json
            data_j = _json.loads(preset_bytes.decode("utf-8"))
            params = data_j.get("parameters", {})
            applied = 0
            for pname, pval in params.items():
                try:
                    p = plugin.parameters[pname]
                    p.raw_value = float(pval)
                    applied += 1
                except Exception:
                    pass
            return JSONResponse({"ok": True, "mode": "params", "applied": applied})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@api.get("/api/plugins/list-presets")
async def api_plugins_list_presets(plugin_name: str = ""):
    """List all presets saved for a given plugin."""
    import re as _re
    safe = _re.sub(r'[^\w\-]', '_', plugin_name)[:80] if plugin_name else ""
    base = _plugin_presets_dir()
    if safe:
        search_dir = base / safe
    else:
        search_dir = base
    if not search_dir.exists():
        return JSONResponse({"ok": True, "presets": []})
    presets = []
    for f in sorted(search_dir.glob("**/*.fxp"), key=lambda p: p.stat().st_mtime, reverse=True):
        presets.append({
            "name": f.stem,
            "path": str(f),
            "plugin": f.parent.name if f.parent != base else "(root)",
            "size": f.stat().st_size,
        })
    return JSONResponse({"ok": True, "presets": presets})


def _magnitude_to_rgb(mag_db, vmin=-80.0, vmax=0.0):
    """Apply a perceptual colormap (approximation of viridis) without matplotlib."""
    import numpy as _np
    norm = _np.clip((mag_db - vmin) / (vmax - vmin), 0.0, 1.0)
    # Viridis-ish polynomial approximation
    r = _np.clip(0.267 + 0.105*norm - 0.330*norm**2 + 2.300*norm**3 - 1.450*norm**4, 0, 1)
    g = _np.clip(0.005 + 1.405*norm - 0.370*norm**2 + 0.010*norm**3, 0, 1)
    b = _np.clip(0.329 + 1.395*norm - 3.250*norm**2 + 2.520*norm**3, 0, 1)
    rgb = _np.stack([r, g, b], axis=-1)
    return (rgb * 255).astype(_np.uint8)


@api.get("/api/mix/spectrogram")
async def api_spectrogram(track_id: int):
    """Return a base64-encoded PNG spectrogram of the given track."""
    import numpy as _np, base64, io
    if track_id not in _engine.tracks:
        return JSONResponse({"error": "Track not found"}, status_code=400)
    track = _engine.tracks[track_id]
    if not track.regions:
        return JSONResponse({"error": "Empty track"}, status_code=400)
    try:
        import librosa as _lr
        from PIL import Image
        region = track.regions[0]
        region._ensure_cached()
        if region._cache is None:
            return JSONResponse({"error": "Track has no cached audio"}, status_code=500)
        audio = region._cache
        sr = region.sample_rate or 44100
        mono = audio.mean(axis=1) if audio.ndim > 1 else audio
        # Limit to first 30s so the endpoint stays fast on long tracks
        mono = mono[: sr * 30]
        S = _np.abs(_lr.stft(mono, n_fft=2048, hop_length=512))
        S_db = _lr.amplitude_to_db(S, ref=_np.max)
        # Flip so high freqs are on top
        S_db = _np.flipud(S_db)
        rgb = _magnitude_to_rgb(S_db, vmin=-80, vmax=0)
        img = Image.fromarray(rgb, mode="RGB")
        # Upscale modestly for readability
        target_w = min(1400, max(800, S_db.shape[1]))
        target_h = 320
        img = img.resize((target_w, target_h), Image.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return JSONResponse({"ok": True, "image": b64,
                             "width": target_w, "height": target_h,
                             "name": track.name})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


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

    # JS API for pop-out windows — pywebview blocks window.open() by default,
    # so the frontend calls window.pywebview.api.popout(html, title, w, h)
    # and Python spawns a real native window. Using html= gives each pop-out
    # its own data-URL origin. Pop-outs that need main-session sync do it
    # via backend API calls (/api/lyrics/save, /api/bandmate, etc.) rather
    # than window.opener — which doesn't work across pywebview windows.
    class _PopoutApi:
        def popout(self, html, title="Sozawen", width=680, height=820):
            try:
                webview.create_window(
                    title,
                    html=html,
                    width=int(width) if width else 680,
                    height=int(height) if height else 820,
                    background_color="#0d0d1a",
                    text_select=True,
                )
                return True
            except Exception as e:
                logger.error("popout failed: %s", e)
                return False

        def popout_url(self, url, title="Sozawen", width=680, height=820):
            """Create a popout pointing at a same-origin URL.
            Same-origin means the popup inherits the full JS context of
            app.html and can fetch /api/* without CORS restrictions."""
            try:
                webview.create_window(
                    title,
                    url=url,
                    width=int(width) if width else 680,
                    height=int(height) if height else 820,
                    background_color="#0d0d1a",
                    text_select=True,
                )
                return True
            except Exception as e:
                logger.error("popout_url failed: %s", e)
                return False

        def close_popout(self):
            """Close the calling popout window. The main window keeps running."""
            try:
                # Destroy the active webview window — which one is active
                # is context-dependent; pywebview's webview.windows list holds
                # all windows, and the caller is the most recently active.
                for w in list(webview.windows):
                    if w.title and "Sozawen —" in (w.title or ""):
                        # popouts have "Sozawen — <toolname>" titles, main
                        # has "Sozawen — Born from the burn...". Skip the
                        # main one.
                        if "Born from the burn" in w.title:
                            continue
                        try:
                            w.destroy()
                        except Exception:
                            pass
                return True
            except Exception as e:
                logger.error("close_popout failed: %s", e)
                return False

    _popout_api = _PopoutApi()

    # Create native window — text_select=True so users can copy bandmate
    # responses, lyric lines, KB article passages, etc. CSS handles making
    # UI chrome (buttons, sidebar, transport) non-selectable where needed.
    _window = webview.create_window(
        "Sozawen — Born from the burn. Built by feeling.",
        url="http://127.0.0.1:8090/static/app.html",
        width=1280,
        height=820,
        min_size=(960, 640),
        background_color="#0d0d1a",
        frameless=False,
        easy_drag=True,
        text_select=True,
        js_api=_popout_api,
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
