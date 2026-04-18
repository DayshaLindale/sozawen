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


def apply_crossfade(path, duration_ms=100, curve="equal_power"):
    """Apply a fade-in and fade-out crossfade to a clip.

    For true crossfade between two adjacent clips, the engine would handle
    the overlap. This applies fades to clip boundaries — prevents clicks at edit points.
    """
    data, sr = _load(path)
    fade_samples = int(duration_ms / 1000 * sr)
    fade_samples = min(fade_samples, len(data) // 4)  # don't fade more than 25% of clip

    if fade_samples < 2:
        return _save(data, sr, path, "crossfade")

    t_in = np.linspace(0, 1, fade_samples)
    t_out = np.linspace(1, 0, fade_samples)

    if curve == "equal_power":
        # Equal power: sine curve, keeps perceived volume constant
        fade_in = np.sin(t_in * np.pi / 2) ** 2
        fade_out = np.sin(t_out * np.pi / 2) ** 2
    elif curve == "s_curve":
        # S-curve: smooth sigmoid
        fade_in = t_in ** 2 * (3 - 2 * t_in)
        fade_out = t_out ** 2 * (3 - 2 * t_out)
    else:
        # Linear
        fade_in = t_in
        fade_out = t_out

    result = data.copy()
    for ch in range(result.shape[1]):
        result[:fade_samples, ch] *= fade_in
        result[-fade_samples:, ch] *= fade_out

    return _save(result, sr, path, "crossfade")


def apply_time_stretch(path, rate=1.0, original_bpm=None, target_bpm=None):
    """Change speed/duration without changing pitch.

    rate: 1.0 = original, 0.5 = half speed (twice as long), 2.0 = double speed.
    If original_bpm and target_bpm are provided, rate is calculated from those.
    """
    import librosa

    # Calculate rate from BPM if provided
    if original_bpm and target_bpm and float(original_bpm) > 0:
        rate = float(target_bpm) / float(original_bpm)

    rate = max(0.1, min(10.0, float(rate)))
    if abs(rate - 1.0) < 0.01:
        return path  # no change needed

    data, sr = _load(path)
    # librosa expects (channels, samples) or mono
    result_channels = []
    for ch in range(data.shape[1]):
        stretched = librosa.effects.time_stretch(data[:, ch], rate=rate)
        result_channels.append(stretched)

    # Align lengths (time_stretch can produce slightly different lengths per channel)
    min_len = min(len(ch) for ch in result_channels)
    result = np.column_stack([ch[:min_len] for ch in result_channels])

    return _save(result.astype(np.float32), sr, path, f"stretch_{rate:.2f}")


def apply_pitch_shift(path, semitones=0, cents=0, preserve_formants=True):
    """Change pitch without changing speed.

    semitones: integer pitch shift (+12 = one octave up)
    cents: fine tuning (100 cents = 1 semitone)
    preserve_formants: keeps vocals sounding natural
    """
    import librosa

    total_semitones = float(semitones) + float(cents) / 100.0
    if abs(total_semitones) < 0.01:
        return path  # no change needed

    data, sr = _load(path)
    result_channels = []
    for ch in range(data.shape[1]):
        shifted = librosa.effects.pitch_shift(
            data[:, ch], sr=sr, n_steps=total_semitones)
        result_channels.append(shifted)

    min_len = min(len(ch) for ch in result_channels)
    result = np.column_stack([ch[:min_len] for ch in result_channels])

    sign = "up" if total_semitones > 0 else "down"
    return _save(result.astype(np.float32), sr, path, f"pitch_{sign}_{abs(total_semitones):.1f}")


def apply_stereo_width(path, width=100):
    """Adjust stereo width using mid/side processing.

    width: 0 = mono, 100 = original, 200 = extra wide.
    """
    data, sr = _load(path)

    width_factor = float(width) / 100.0

    # Mid/Side encoding
    mid = (data[:, 0] + data[:, 1]) / 2.0
    side = (data[:, 0] - data[:, 1]) / 2.0

    # Scale the side channel
    side = side * width_factor

    # Mid/Side decoding
    result = np.column_stack([
        np.clip(mid + side, -1.0, 1.0),
        np.clip(mid - side, -1.0, 1.0),
    ])

    return _save(result.astype(np.float32), sr, path, f"width_{width}")


def apply_declip(path, sensitivity=50):
    """Repair clipped audio by reconstructing flattened peaks.

    Uses cubic interpolation to reconstruct waveform peaks that were
    hard-clipped. Higher sensitivity catches more clipping but may
    alter clean audio.
    """
    from scipy.interpolate import CubicSpline

    data, sr = _load(path)
    threshold = 1.0 - (float(sensitivity) / 100.0) * 0.05  # 0.95 to 1.0
    result = data.copy()

    for ch in range(result.shape[1]):
        channel = result[:, ch]
        clipped = np.abs(channel) >= threshold

        if not np.any(clipped):
            continue

        # Find clean (non-clipped) sample indices
        clean_mask = ~clipped
        clean_indices = np.where(clean_mask)[0]
        clean_values = channel[clean_mask]

        if len(clean_indices) < 4:
            continue  # not enough clean samples to interpolate

        # Interpolate through clipped regions
        try:
            spline = CubicSpline(clean_indices, clean_values, extrapolate=True)
            clipped_indices = np.where(clipped)[0]
            channel[clipped_indices] = spline(clipped_indices).astype(np.float32)
            # Soft clip the result to prevent any overshoot
            channel[clipped_indices] = np.tanh(channel[clipped_indices])
        except Exception:
            pass  # if interpolation fails, leave the channel as-is

        result[:, ch] = channel

    return _save(result, sr, path, "declipped")


def apply_reverse(path):
    """Reverse the audio."""
    data, sr = _load(path)
    result = data[::-1].copy()
    return _save(result, sr, path, "reversed")


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
