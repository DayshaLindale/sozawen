"""Sozawen Audio Effects — pure scipy/numpy DSP. No GPL dependencies.

Each function takes an input file, applies the effect, saves the result.
Non-destructive: original file is never modified. Output goes to a new file.

All effects use scipy.signal for filter design and numpy for audio math.
Licensed under BSD-compatible terms only.
"""

import numpy as np
import soundfile as sf
import logging
from pathlib import Path
from scipy.signal import butter, sosfilt, iirnotch, filtfilt, iirpeak

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


def _db_to_linear(db):
    return 10.0 ** (db / 20.0)


def _envelope_follower(signal, attack_samples, release_samples):
    """Compute the amplitude envelope of a signal."""
    envelope = np.zeros_like(signal)
    env = 0.0
    attack_coeff = 1.0 - np.exp(-1.0 / max(attack_samples, 1))
    release_coeff = 1.0 - np.exp(-1.0 / max(release_samples, 1))
    for i in range(len(signal)):
        level = abs(signal[i])
        if level > env:
            env += attack_coeff * (level - env)
        else:
            env += release_coeff * (level - env)
        envelope[i] = env
    return envelope


# ═══════════════════════════════════════════════════════════════════
# NOISE GATE — silences audio below threshold
# ═══════════════════════════════════════════════════════════════════

def apply_noise_gate(path, threshold_db=-40, attack_ms=10, release_ms=100):
    """Gate: silences audio below threshold. Pure envelope follower."""
    data, sr = _load(path)
    threshold = _db_to_linear(threshold_db)
    attack_samples = int(attack_ms / 1000 * sr)
    release_samples = int(release_ms / 1000 * sr)

    result = data.copy()
    for ch in range(result.shape[1]):
        env = _envelope_follower(result[:, ch], attack_samples, release_samples)
        # Smooth gate: below threshold fades to silence
        gate = np.where(env > threshold, 1.0, env / (threshold + 1e-10))
        gate = np.clip(gate, 0.0, 1.0)
        result[:, ch] *= gate.astype(np.float32)

    return _save(result, sr, path, "gated")


# ═══════════════════════════════════════════════════════════════════
# EQ — 5-band parametric equalizer via biquad filters
# ═══════════════════════════════════════════════════════════════════

def _biquad_peak(freq, gain_db, q, sr):
    """Design a peaking EQ biquad filter (second-order section)."""
    if abs(gain_db) < 0.01:
        return None
    A = _db_to_linear(gain_db / 2.0)
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / (2 * q)

    b0 = 1 + alpha * A
    b1 = -2 * np.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha / A

    # Return as second-order section [b0/a0, b1/a0, b2/a0, 1, a1/a0, a2/a0]
    return np.array([b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0])


def _biquad_low_shelf(freq, gain_db, sr):
    """Design a low shelf biquad filter."""
    if abs(gain_db) < 0.01:
        return None
    A = _db_to_linear(gain_db / 2.0)
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / 2.0 * np.sqrt(2.0)

    b0 = A * ((A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
    b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(w0))
    b2 = A * ((A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
    a1 = -2 * ((A - 1) + (A + 1) * np.cos(w0))
    a2 = (A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha

    return np.array([b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0])


def _biquad_high_shelf(freq, gain_db, sr):
    """Design a high shelf biquad filter."""
    if abs(gain_db) < 0.01:
        return None
    A = _db_to_linear(gain_db / 2.0)
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / 2.0 * np.sqrt(2.0)

    b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
    b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
    a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha

    return np.array([b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0])


def apply_eq(path, hpf_freq=20, lpf_freq=20000,
             low_freq=80, low_gain=0, low_q=0.7, low_type='shelf',
             lomid_freq=250, lomid_gain=0, lomid_q=1.0,
             himid_freq=4000, himid_gain=0, himid_q=1.0,
             high_freq=12000, high_gain=0, high_q=0.7, high_type='shelf',
             # Legacy params for backward compatibility
             low_db=None, low_mid_db=None, mid_db=None, high_mid_db=None, high_db=None,
             **kwargs):
    """Fully parametric EQ with HPF, LPF, and 4 bands (shelf/bell selectable).

    Matches hardware console layout: HPF + Low + Lo-Mid + Hi-Mid + High + LPF.
    Each band has independent frequency, gain, and Q controls.
    """
    # Handle legacy 5-band simple params
    if low_db is not None: low_gain = low_db
    if low_mid_db is not None: lomid_gain = low_mid_db
    if mid_db is not None: himid_gain = mid_db  # map old 'mid' to hi-mid
    if high_mid_db is not None: himid_gain = high_mid_db
    if high_db is not None: high_gain = high_db

    data, sr = _load(path)
    sections = []

    # High-pass filter (removes lows below cutoff)
    hpf_freq = float(hpf_freq)
    if hpf_freq > 25:
        sos_hp = butter(2, hpf_freq, btype='highpass', fs=sr, output='sos')
        sections.extend(sos_hp.tolist())

    # Low band (shelf or bell)
    if low_type == 'shelf':
        s = _biquad_low_shelf(float(low_freq), float(low_gain), sr)
    else:
        s = _biquad_peak(float(low_freq), float(low_gain), float(low_q), sr)
    if s is not None: sections.append(s.tolist())

    # Lo-mid band (always bell)
    s = _biquad_peak(float(lomid_freq), float(lomid_gain), float(lomid_q), sr)
    if s is not None: sections.append(s.tolist())

    # Hi-mid band (always bell)
    s = _biquad_peak(float(himid_freq), float(himid_gain), float(himid_q), sr)
    if s is not None: sections.append(s.tolist())

    # High band (shelf or bell)
    if high_type == 'shelf':
        s = _biquad_high_shelf(float(high_freq), float(high_gain), sr)
    else:
        s = _biquad_peak(float(high_freq), float(high_gain), float(high_q), sr)
    if s is not None: sections.append(s.tolist())

    # Low-pass filter (removes highs above cutoff)
    lpf_freq = float(lpf_freq)
    if lpf_freq < 19500:
        sos_lp = butter(2, lpf_freq, btype='lowpass', fs=sr, output='sos')
        sections.extend(sos_lp.tolist())

    if not sections:
        return _save(data, sr, path, "eq")

    sos = np.array(sections)
    result = data.copy()
    for ch in range(result.shape[1]):
        result[:, ch] = sosfilt(sos, result[:, ch]).astype(np.float32)

    return _save(result, sr, path, "eq")


# ═══════════════════════════════════════════════════════════════════
# COMPRESSOR — dynamic range compression
# ═══════════════════════════════════════════════════════════════════

def apply_compressor(path, threshold_db=-20, ratio=3.0, attack_ms=10, release_ms=100, makeup_db=0):
    """Compressor with envelope follower and gain reduction."""
    data, sr = _load(path)
    threshold = _db_to_linear(threshold_db)
    makeup = _db_to_linear(makeup_db)
    attack_samples = int(attack_ms / 1000 * sr)
    release_samples = int(release_ms / 1000 * sr)

    result = data.copy()
    for ch in range(result.shape[1]):
        env = _envelope_follower(result[:, ch], attack_samples, release_samples)

        # Compute gain reduction
        gain = np.ones_like(env)
        above = env > threshold
        if np.any(above):
            # How many dB above threshold
            db_over = 20 * np.log10(env[above] / threshold + 1e-10)
            # Reduce by (1 - 1/ratio) of the overshoot
            db_reduction = db_over * (1.0 - 1.0 / ratio)
            gain[above] = _db_to_linear(-db_reduction)

        result[:, ch] *= gain.astype(np.float32)

    # Makeup gain
    result *= makeup
    result = np.clip(result, -1.0, 1.0)
    return _save(result.astype(np.float32), sr, path, "compressed")


# ═══════════════════════════════════════════════════════════════════
# REVERB — Schroeder reverb (4 comb + 2 allpass)
# ═══════════════════════════════════════════════════════════════════

def apply_reverb(path, room_size=0.4, decay=1.5, wet_dry=0.25):
    """Schroeder reverb — 4 parallel comb filters + 2 series allpass filters."""
    data, sr = _load(path)

    # Comb filter delay times (in samples), scaled by room size
    base_delays = [1557, 1617, 1491, 1422]  # classic Schroeder values for 44.1kHz
    scale = sr / 44100.0
    delays = [int(d * scale * (0.5 + room_size)) for d in base_delays]

    # Feedback coefficient from decay time
    # RT60 = -3 * delay / log10(g) => g = 10^(-3*delay/(RT60*sr))
    feedbacks = [10 ** (-3.0 * d / (decay * sr + 1e-10)) for d in delays]
    feedbacks = [min(f, 0.98) for f in feedbacks]  # stability limit

    # Allpass delays
    ap_delays = [int(225 * scale), int(556 * scale)]
    ap_gain = 0.5

    result = np.zeros_like(data)

    for ch in range(data.shape[1]):
        mono = data[:, ch].astype(np.float64)
        n = len(mono)

        # 4 parallel comb filters
        comb_out = np.zeros(n, dtype=np.float64)
        for delay, fb in zip(delays, feedbacks):
            buf = np.zeros(n, dtype=np.float64)
            for i in range(n):
                read_pos = i - delay
                delayed = buf[read_pos] if read_pos >= 0 else 0.0
                buf[i] = mono[i] + fb * delayed
            comb_out += buf
        comb_out /= len(delays)

        # 2 series allpass filters
        signal = comb_out.copy()
        for ap_d in ap_delays:
            out = np.zeros(n, dtype=np.float64)
            for i in range(n):
                read_pos = i - ap_d
                delayed = out[read_pos] if read_pos >= 0 else 0.0
                out[i] = -ap_gain * signal[i] + delayed + ap_gain * (signal[i] if read_pos < 0 else signal[read_pos])
            signal = out

        # Wet/dry mix
        result[:, ch] = ((1.0 - wet_dry) * mono + wet_dry * signal).astype(np.float32)

    result = np.clip(result, -1.0, 1.0)
    return _save(result.astype(np.float32), sr, path, "reverb")


# ═══════════════════════════════════════════════════════════════════
# DELAY — simple feedback delay
# ═══════════════════════════════════════════════════════════════════

def apply_delay(path, delay_ms=375, feedback=0.3, mix=0.2):
    """Feedback delay line."""
    data, sr = _load(path)
    delay_samples = int(delay_ms / 1000 * sr)
    feedback = min(feedback, 0.95)  # prevent runaway

    result = data.copy().astype(np.float64)
    for ch in range(result.shape[1]):
        # Create delay buffer with enough room for feedback tails
        n = len(result[:, ch])
        buf = np.zeros(n + delay_samples * 10, dtype=np.float64)
        buf[:n] = result[:, ch]

        # Apply feedback delay
        for tap in range(1, 10):
            offset = delay_samples * tap
            gain = feedback ** tap
            if gain < 0.001 or offset >= len(buf):
                break
            end = min(n, len(buf) - offset)
            buf[offset:offset + end] += result[:end, ch] * gain

        # Wet/dry mix
        result[:, ch] = (1.0 - mix) * result[:, ch] + mix * buf[:n]

    result = np.clip(result, -1.0, 1.0)
    return _save(result.astype(np.float32), sr, path, "delay")


# ═══════════════════════════════════════════════════════════════════
# LIMITER — brick-wall limiter with lookahead
# ═══════════════════════════════════════════════════════════════════

def apply_limiter(path, ceiling_db=-1.0, input_gain_db=0):
    """Brick-wall limiter — nothing exceeds the ceiling."""
    data, sr = _load(path)

    # Input gain
    if input_gain_db != 0:
        data = data * _db_to_linear(input_gain_db)

    ceiling = _db_to_linear(ceiling_db)

    # Lookahead: find peaks and reduce gain smoothly
    lookahead = int(sr * 0.005)  # 5ms lookahead
    result = data.copy()

    for ch in range(result.shape[1]):
        channel = result[:, ch].astype(np.float64)
        gain = np.ones(len(channel), dtype=np.float64)

        for i in range(len(channel)):
            level = abs(channel[i])
            if level > ceiling:
                reduction = ceiling / (level + 1e-10)
                # Apply reduction with smooth attack over lookahead window
                start = max(0, i - lookahead)
                for j in range(start, min(i + 1, len(gain))):
                    t = (j - start) / (lookahead + 1)
                    new_gain = 1.0 - (1.0 - reduction) * t
                    gain[j] = min(gain[j], new_gain)
                gain[i] = min(gain[i], reduction)

        result[:, ch] = (channel * gain).astype(np.float32)

    result = np.clip(result, -ceiling, ceiling)
    return _save(result.astype(np.float32), sr, path, "limited")


# ═══════════════════════════════════════════════════════════════════
# HUM REMOVAL — notch filters (already scipy, no change needed)
# ═══════════════════════════════════════════════════════════════════

def apply_hum_removal(path, frequency=60, harmonics=4, strength=0.7):
    """Remove hum using notch filters at the fundamental and harmonics."""
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


# ═══════════════════════════════════════════════════════════════════
# DE-ESSER — frequency-selective compression via high shelf
# ═══════════════════════════════════════════════════════════════════

def apply_deesser(path, frequency=6000, reduction_db=6):
    """De-esser using a dynamic high-frequency shelf reduction."""
    data, sr = _load(path)

    # Design high shelf filter for the sibilant range
    sos_detect = _biquad_high_shelf(frequency, 12, sr)  # boost for detection
    sos_cut = _biquad_high_shelf(frequency, -reduction_db, sr)

    if sos_detect is None or sos_cut is None:
        return _save(data, sr, path, "deessed")

    result = data.copy()
    for ch in range(result.shape[1]):
        # Detect sibilance: filter to isolate high frequencies
        highs = sosfilt(np.array([sos_detect]), result[:, ch])
        env = _envelope_follower(highs.astype(np.float32), int(0.001 * sr), int(0.01 * sr))

        # When sibilance is detected (envelope above threshold), apply cut
        threshold = np.mean(env) * 2.0  # adaptive threshold
        mask = env > threshold

        if np.any(mask):
            # Apply high shelf cut to sibilant regions
            cut = sosfilt(np.array([sos_cut]), result[:, ch]).astype(np.float32)
            # Blend: use cut version where sibilance detected, original elsewhere
            blend = mask.astype(np.float32) * 0.8  # don't cut 100%, keep some natural
            result[:, ch] = result[:, ch] * (1 - blend) + cut * blend

    return _save(result, sr, path, "deessed")


# ═══════════════════════════════════════════════════════════════════
# NORMALIZE — peak/RMS/LUFS (already pure numpy, no change)
# ═══════════════════════════════════════════════════════════════════

def apply_normalize(path, target_db=-1.0, mode="peak"):
    data, sr = _load(path)
    if mode == "peak":
        peak = np.max(np.abs(data))
        if peak > 0:
            gain = _db_to_linear(target_db) / peak
            data = data * gain
    elif mode == "rms":
        rms = np.sqrt(np.mean(data ** 2))
        if rms > 0:
            gain = _db_to_linear(target_db) / rms
            data = data * gain
    data = np.clip(data, -1.0, 1.0)
    return _save(data, sr, path, "normalized")


# ═══════════════════════════════════════════════════════════════════
# CROSSFADE — fade in/out at boundaries (already pure numpy)
# ═══════════════════════════════════════════════════════════════════

def apply_crossfade(path, duration_ms=100, curve="equal_power"):
    """Apply a fade-in and fade-out crossfade to a clip."""
    data, sr = _load(path)
    fade_samples = int(duration_ms / 1000 * sr)
    fade_samples = min(fade_samples, len(data) // 4)

    if fade_samples < 2:
        return _save(data, sr, path, "crossfade")

    t_in = np.linspace(0, 1, fade_samples)
    t_out = np.linspace(1, 0, fade_samples)

    if curve == "equal_power":
        fade_in = np.sin(t_in * np.pi / 2) ** 2
        fade_out = np.sin(t_out * np.pi / 2) ** 2
    elif curve == "s_curve":
        fade_in = t_in ** 2 * (3 - 2 * t_in)
        fade_out = t_out ** 2 * (3 - 2 * t_out)
    else:
        fade_in = t_in
        fade_out = t_out

    result = data.copy()
    for ch in range(result.shape[1]):
        result[:fade_samples, ch] *= fade_in
        result[-fade_samples:, ch] *= fade_out

    return _save(result, sr, path, "crossfade")


# ═══════════════════════════════════════════════════════════════════
# TIME STRETCH — via librosa (ISC license, clean)
# ═══════════════════════════════════════════════════════════════════

def apply_time_stretch(path, rate=1.0, original_bpm=None, target_bpm=None):
    """Change speed/duration without changing pitch."""
    import librosa

    if original_bpm and target_bpm and float(original_bpm) > 0:
        rate = float(target_bpm) / float(original_bpm)

    rate = max(0.1, min(10.0, float(rate)))
    if abs(rate - 1.0) < 0.01:
        return path

    data, sr = _load(path)
    result_channels = []
    for ch in range(data.shape[1]):
        stretched = librosa.effects.time_stretch(data[:, ch], rate=rate)
        result_channels.append(stretched)

    min_len = min(len(ch) for ch in result_channels)
    result = np.column_stack([ch[:min_len] for ch in result_channels])
    return _save(result.astype(np.float32), sr, path, f"stretch_{rate:.2f}")


# ═══════════════════════════════════════════════════════════════════
# PITCH SHIFT — via librosa (ISC license, clean)
# ═══════════════════════════════════════════════════════════════════

def apply_pitch_shift(path, semitones=0, cents=0, preserve_formants=True):
    """Change pitch without changing speed."""
    import librosa

    total_semitones = float(semitones) + float(cents) / 100.0
    if abs(total_semitones) < 0.01:
        return path

    data, sr = _load(path)
    result_channels = []
    for ch in range(data.shape[1]):
        shifted = librosa.effects.pitch_shift(data[:, ch], sr=sr, n_steps=total_semitones)
        result_channels.append(shifted)

    min_len = min(len(ch) for ch in result_channels)
    result = np.column_stack([ch[:min_len] for ch in result_channels])

    sign = "up" if total_semitones > 0 else "down"
    return _save(result.astype(np.float32), sr, path, f"pitch_{sign}_{abs(total_semitones):.1f}")


# ═══════════════════════════════════════════════════════════════════
# STEREO WIDTH — mid/side (already pure numpy)
# ═══════════════════════════════════════════════════════════════════

def apply_stereo_width(path, width=100):
    """Adjust stereo width using mid/side processing."""
    data, sr = _load(path)
    width_factor = float(width) / 100.0
    mid = (data[:, 0] + data[:, 1]) / 2.0
    side = (data[:, 0] - data[:, 1]) / 2.0
    side = side * width_factor
    result = np.column_stack([
        np.clip(mid + side, -1.0, 1.0),
        np.clip(mid - side, -1.0, 1.0),
    ])
    return _save(result.astype(np.float32), sr, path, f"width_{width}")


# ═══════════════════════════════════════════════════════════════════
# DE-CLIP — cubic spline reconstruction (already scipy)
# ═══════════════════════════════════════════════════════════════════

def apply_declip(path, sensitivity=50):
    """Repair clipped audio by reconstructing flattened peaks."""
    from scipy.interpolate import CubicSpline

    data, sr = _load(path)
    threshold = 1.0 - (float(sensitivity) / 100.0) * 0.05
    result = data.copy()

    for ch in range(result.shape[1]):
        channel = result[:, ch]
        clipped = np.abs(channel) >= threshold

        if not np.any(clipped):
            continue

        clean_mask = ~clipped
        clean_indices = np.where(clean_mask)[0]
        clean_values = channel[clean_mask]

        if len(clean_indices) < 4:
            continue

        try:
            spline = CubicSpline(clean_indices, clean_values, extrapolate=True)
            clipped_indices = np.where(clipped)[0]
            channel[clipped_indices] = spline(clipped_indices).astype(np.float32)
            channel[clipped_indices] = np.tanh(channel[clipped_indices])
        except Exception:
            pass

        result[:, ch] = channel

    return _save(result, sr, path, "declipped")


# ═══════════════════════════════════════════════════════════════════
# REVERSE (already pure numpy)
# ═══════════════════════════════════════════════════════════════════

def apply_bleed_removal(target_path, reference_path, filter_length=4096, step_size=0.1):
    """Remove bleed/leakage from one channel using another as reference.

    If you're recording guitar DI on input 1 and vocals on input 2,
    the mic picks up guitar bleed. This uses the clean guitar (reference)
    to adaptively cancel the bleed from the vocal track (target).

    Uses Normalized LMS adaptive filter — the same math used in
    noise-cancelling headphones and conference call echo cancellation.

    target_path: the track WITH bleed (e.g., vocal mic)
    reference_path: the clean source causing the bleed (e.g., guitar DI)
    filter_length: how many taps in the adaptive filter (longer = handles more room delay)
    step_size: learning rate (0.01-0.5, lower = more precise, higher = faster adaptation)
    """
    target, sr = _load(target_path)
    reference, sr2 = _load(reference_path)

    # Work in mono for the adaptive filter
    target_mono = target.mean(axis=1) if target.ndim > 1 else target
    ref_mono = reference.mean(axis=1) if reference.ndim > 1 else reference

    # Align lengths
    n = min(len(target_mono), len(ref_mono))
    target_mono = target_mono[:n]
    ref_mono = ref_mono[:n]

    # Normalize reference to prevent numerical issues
    ref_power = np.sqrt(np.mean(ref_mono ** 2)) + 1e-10
    ref_norm = ref_mono / ref_power

    # NLMS adaptive filter
    filter_len = min(filter_length, n // 4)
    w = np.zeros(filter_len, dtype=np.float64)  # filter weights
    mu = float(step_size)
    output = np.zeros(n, dtype=np.float64)

    for i in range(filter_len, n):
        # Reference signal window
        x = ref_norm[i - filter_len:i][::-1]
        # Estimated bleed = filter applied to reference
        bleed_estimate = np.dot(w, x)
        # Error = target minus estimated bleed = clean signal
        error = target_mono[i] - bleed_estimate
        # Update filter weights (NLMS)
        norm = np.dot(x, x) + 1e-10
        w += mu * error * x / norm
        output[i] = error

    # Copy the initial samples unchanged (filter needs warmup)
    output[:filter_len] = target_mono[:filter_len]

    # Reconstruct stereo from the cleaned mono
    if target.ndim > 1 and target.shape[1] == 2:
        # Apply the same gain change to both channels
        gain = np.zeros(n, dtype=np.float32)
        safe = np.abs(target_mono) > 1e-6
        gain[safe] = (output[safe] / target_mono[safe]).astype(np.float32)
        gain[~safe] = 1.0
        # Smooth the gain to avoid artifacts
        from scipy.ndimage import uniform_filter1d
        gain = uniform_filter1d(gain, size=512).astype(np.float32)
        gain = np.clip(gain, 0.0, 2.0)
        result = target[:n].copy()
        result[:, 0] *= gain
        result[:, 1] *= gain
    else:
        result = np.column_stack([output, output]).astype(np.float32)

    result = np.clip(result, -1.0, 1.0)
    return _save(result.astype(np.float32), sr, target_path, "bleed_removed")


def apply_reverse(path):
    """Reverse the audio."""
    data, sr = _load(path)
    result = data[::-1].copy()
    return _save(result, sr, path, "reversed")


# ═══════════════════════════════════════════════════════════════════
# MEASUREMENT — LUFS via pyloudnorm (MIT license, clean)
# ═══════════════════════════════════════════════════════════════════

def measure_loudness(path):
    """Measure LUFS, true peak, and dynamic range."""
    import pyloudnorm as pyln
    data, sr = _load(path)
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(data)
    true_peak = 20 * np.log10(np.max(np.abs(data)) + 1e-10)
    rms = 20 * np.log10(np.sqrt(np.mean(data ** 2)) + 1e-10)
    dynamic_range = true_peak - rms
    return {
        "lufs": round(float(loudness), 1),
        "true_peak": round(float(true_peak), 1),
        "dynamic_range": round(float(dynamic_range), 1),
    }


# ═══════════════════════════════════════════════════════════════════
# EXPORT — mix to file (already clean)
# ═══════════════════════════════════════════════════════════════════

def export_mix(tracks_data, output_path, format="wav", sample_rate=44100, bit_depth=24):
    """Render all tracks to a single output file."""
    max_len = max(len(t) for t in tracks_data) if tracks_data else 0
    if max_len == 0:
        return None

    mix = np.zeros((max_len, 2), dtype=np.float64)
    for track_audio in tracks_data:
        mix[:len(track_audio)] += track_audio

    mix = np.clip(mix, -1.0, 1.0).astype(np.float32)

    ext = {"wav": ".wav", "mp3": ".mp3", "flac": ".flac", "ogg": ".ogg", "aiff": ".aiff"}
    out_path = Path(output_path).with_suffix(ext.get(format, ".wav"))

    if format == "mp3":
        try:
            from pydub import AudioSegment
            import io
            buf = io.BytesIO()
            sf.write(buf, mix, sample_rate, format='WAV')
            buf.seek(0)
            audio = AudioSegment.from_wav(buf)
            audio.export(str(out_path), format="mp3", bitrate="320k")
        except ImportError:
            out_path = out_path.with_suffix(".wav")
            sf.write(str(out_path), mix, sample_rate)
    else:
        subtype = f"PCM_{bit_depth}" if format in ("wav", "aiff") else None
        sf.write(str(out_path), mix, sample_rate, subtype=subtype)

    return str(out_path)
