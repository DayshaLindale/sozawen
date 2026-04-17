"""Sozawen Audio Effects — all processing tools backed by pedalboard.

Each function takes an input file, applies the effect, saves the result.
Non-destructive: original file is never modified. Output goes to a new file.
"""

import numpy as np
import soundfile as sf
import logging
from pathlib import Path

logger = logging.getLogger("sozawen.fx")


def _load(path):
    data, sr = sf.read(path, dtype='float32')
    if data.ndim == 1:
        data = np.column_stack([data, data])
    return data, sr


def _save(data, sr, original_path, suffix):
    out = Path(original_path)
    output_path = out.parent / f"{out.stem}_{suffix}{out.suffix}"
    sf.write(str(output_path), data, sr)
    return str(output_path)


def apply_noise_gate(path, threshold_db=-40, attack_ms=10, release_ms=100):
    from pedalboard import NoiseGate
    data, sr = _load(path)
    board = NoiseGate(threshold_db=threshold_db, attack_ms=attack_ms, release_ms=release_ms)
    result = board(data.T, sr).T
    return _save(result, sr, path, "gated")


def apply_eq(path, low_db=0, low_mid_db=0, mid_db=0, high_mid_db=0, high_db=0):
    from pedalboard import LowShelfFilter, HighShelfFilter, PeakFilter, Pedalboard
    board = Pedalboard([
        LowShelfFilter(cutoff_frequency_hz=80, gain_db=low_db),
        PeakFilter(cutoff_frequency_hz=250, gain_db=low_mid_db, q=1.0),
        PeakFilter(cutoff_frequency_hz=1000, gain_db=mid_db, q=1.0),
        PeakFilter(cutoff_frequency_hz=4000, gain_db=high_mid_db, q=1.0),
        HighShelfFilter(cutoff_frequency_hz=12000, gain_db=high_db),
    ])
    data, sr = _load(path)
    result = board(data.T, sr).T
    return _save(result, sr, path, "eq")


def apply_compressor(path, threshold_db=-20, ratio=3.0, attack_ms=10, release_ms=100, makeup_db=0):
    from pedalboard import Compressor, Gain, Pedalboard
    board = Pedalboard([
        Compressor(threshold_db=threshold_db, ratio=ratio,
                   attack_ms=attack_ms, release_ms=release_ms),
        Gain(gain_db=makeup_db),
    ])
    data, sr = _load(path)
    result = board(data.T, sr).T
    return _save(result, sr, path, "compressed")


def apply_reverb(path, room_size=0.4, decay=1.5, wet_dry=0.25):
    from pedalboard import Reverb
    board = Reverb(room_size=room_size, damping=0.5, wet_level=wet_dry, dry_level=1.0-wet_dry)
    data, sr = _load(path)
    result = board(data.T, sr).T
    return _save(result, sr, path, "reverb")


def apply_delay(path, delay_ms=375, feedback=0.3, mix=0.2):
    from pedalboard import Delay
    board = Delay(delay_seconds=delay_ms/1000, feedback=feedback, mix=mix)
    data, sr = _load(path)
    result = board(data.T, sr).T
    return _save(result, sr, path, "delay")


def apply_limiter(path, ceiling_db=-1.0, input_gain_db=0):
    from pedalboard import Limiter, Gain, Pedalboard
    board = Pedalboard([
        Gain(gain_db=input_gain_db),
        Limiter(threshold_db=ceiling_db),
    ])
    data, sr = _load(path)
    result = board(data.T, sr).T
    return _save(result, sr, path, "limited")


def apply_hum_removal(path, frequency=60, harmonics=4, strength=0.7):
    """Remove hum using notch filters at the fundamental and harmonics."""
    from scipy.signal import iirnotch, filtfilt
    data, sr = _load(path)
    result = data.copy()
    for h in range(1, harmonics + 1):
        freq = frequency * h
        if freq >= sr / 2:
            break
        Q = 30 * strength
        b, a = iirnotch(freq, Q, sr)
        for ch in range(result.shape[1]):
            result[:, ch] = filtfilt(b, a, result[:, ch]).astype(np.float32)
    return _save(result, sr, path, "dehum")


def apply_deesser(path, frequency=6000, reduction_db=6):
    """Simple de-esser using a dynamic high shelf."""
    from pedalboard import HighShelfFilter
    # Simplified: just apply a gentle high shelf cut
    # A real de-esser would be frequency-selective compression
    board = HighShelfFilter(cutoff_frequency_hz=frequency, gain_db=-reduction_db)
    data, sr = _load(path)
    result = board(data.T, sr).T
    return _save(result, sr, path, "deessed")


def apply_normalize(path, target_db=-1.0, mode="peak"):
    data, sr = _load(path)
    if mode == "peak":
        peak = np.max(np.abs(data))
        if peak > 0:
            gain = 10 ** (target_db / 20) / peak
            data = data * gain
    elif mode == "rms":
        rms = np.sqrt(np.mean(data ** 2))
        if rms > 0:
            gain = 10 ** (target_db / 20) / rms
            data = data * gain
    data = np.clip(data, -1.0, 1.0)
    return _save(data, sr, path, "normalized")


def measure_loudness(path):
    """Measure LUFS, true peak, and dynamic range."""
    import pyloudnorm as pyln
    data, sr = _load(path)
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(data)
    true_peak = 20 * np.log10(np.max(np.abs(data)) + 1e-10)
    # Dynamic range: difference between loudest and average
    rms = 20 * np.log10(np.sqrt(np.mean(data ** 2)) + 1e-10)
    dynamic_range = true_peak - rms
    return {
        "lufs": round(float(loudness), 1),
        "true_peak": round(float(true_peak), 1),
        "dynamic_range": round(float(dynamic_range), 1),
    }


def export_mix(tracks_data, output_path, format="wav", sample_rate=44100, bit_depth=24):
    """Render all tracks to a single output file."""
    # Find the longest track
    max_len = max(len(t) for t in tracks_data) if tracks_data else 0
    if max_len == 0:
        return None

    # Mix all tracks
    mix = np.zeros((max_len, 2), dtype=np.float64)
    for track_audio in tracks_data:
        mix[:len(track_audio)] += track_audio

    mix = np.clip(mix, -1.0, 1.0).astype(np.float32)

    ext = {"wav": ".wav", "mp3": ".mp3", "flac": ".flac", "ogg": ".ogg", "aiff": ".aiff"}
    out_path = Path(output_path).with_suffix(ext.get(format, ".wav"))

    if format == "mp3":
        # soundfile doesn't support mp3 — use pydub
        try:
            from pydub import AudioSegment
            import io
            buf = io.BytesIO()
            sf.write(buf, mix, sample_rate, format='WAV')
            buf.seek(0)
            audio = AudioSegment.from_wav(buf)
            audio.export(str(out_path), format="mp3", bitrate="320k")
        except ImportError:
            # Fallback to WAV
            out_path = out_path.with_suffix(".wav")
            sf.write(str(out_path), mix, sample_rate)
    else:
        subtype = f"PCM_{bit_depth}" if format in ("wav", "aiff") else None
        sf.write(str(out_path), mix, sample_rate, subtype=subtype)

    return str(out_path)
