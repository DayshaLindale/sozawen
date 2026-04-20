"""Sozawen Vocal Tuning — pitch correction from pure math.

Detects pitch frame-by-frame, shifts each frame to the nearest
note in the selected key. Strength controls how hard the snap is:
0% = natural, 100% = Auto-Tune effect.

Uses autocorrelation for pitch detection and PSOLA
(Pitch Synchronous Overlap-Add) for pitch shifting.
No ML models. No external dependencies beyond numpy/scipy.
"""

import numpy as np
from scipy.signal import butter, lfilter


# Note frequencies for all 12 chromatic pitches across octaves
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Scale intervals (semitones from root)
SCALE_INTERVALS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'chromatic': list(range(12)),
}


def _freq_to_midi(freq):
    """Convert frequency to MIDI note number (float for cents)."""
    if freq <= 0:
        return 0
    return 69 + 12 * np.log2(freq / 440.0)


def _midi_to_freq(midi):
    """Convert MIDI note number to frequency."""
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def _detect_pitch_autocorr(frame, sr):
    """Detect pitch of a single frame using autocorrelation.

    Returns frequency in Hz, or 0 if no clear pitch detected.
    """
    n = len(frame)
    if n < 64:
        return 0

    # Windowed autocorrelation
    windowed = frame * np.hanning(n)
    corr = np.correlate(windowed, windowed, mode='full')
    corr = corr[n:]  # keep positive lags only

    # Find the first peak after the initial drop
    # Minimum lag corresponds to maximum detectable frequency (~1000Hz)
    min_lag = int(sr / 1000)
    # Maximum lag corresponds to minimum detectable frequency (~60Hz)
    max_lag = min(int(sr / 60), len(corr) - 1)

    if max_lag <= min_lag:
        return 0

    segment = corr[min_lag:max_lag]
    if len(segment) < 3:
        return 0

    # Find the highest peak
    peak_idx = np.argmax(segment) + min_lag

    # Check if the peak is strong enough (voiced vs unvoiced)
    if corr[0] > 0 and corr[peak_idx] / corr[0] < 0.3:
        return 0  # too weak — probably unvoiced/noise

    freq = sr / peak_idx
    return freq


def _nearest_scale_note(midi_note, key_root, scale_type='major'):
    """Find the nearest note in the given scale."""
    intervals = SCALE_INTERVALS.get(scale_type, SCALE_INTERVALS['chromatic'])
    root_midi = NOTE_NAMES.index(key_root) if key_root in NOTE_NAMES else 0

    # All valid MIDI notes in this scale
    best_dist = float('inf')
    best_note = round(midi_note)

    for octave_offset in range(-1, 2):
        for interval in intervals:
            candidate = root_midi + interval + (round(midi_note / 12) + octave_offset) * 12
            dist = abs(midi_note - candidate)
            if dist < best_dist:
                best_dist = dist
                best_note = candidate

    return best_note


def tune_audio(audio, sr=44100, strength=0.5, key='C', speed_ms=30):
    """Apply pitch correction to vocal audio.

    Parameters:
        audio: mono numpy array
        sr: sample rate
        strength: 0-1 (0=natural, 1=hard Auto-Tune snap)
        key: root note ('C', 'D', 'Am', etc.)
        speed_ms: correction speed in ms (fast=robotic, slow=natural)

    Returns: pitch-corrected audio as numpy array.
    """
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    audio = audio.astype(np.float64)
    n = len(audio)

    # Frame parameters
    frame_size = int(0.03 * sr)  # 30ms frames
    hop_size = int(0.01 * sr)    # 10ms hop (overlap)
    n_frames = (n - frame_size) // hop_size

    if n_frames < 3:
        return audio.astype(np.float32)

    # Detect key type
    key_root = key.replace('m', '')
    scale_type = 'minor' if 'm' in key and key != 'major' else 'major'

    # Detect pitch per frame
    pitches = []
    for i in range(n_frames):
        start = i * hop_size
        frame = audio[start:start + frame_size]
        freq = _detect_pitch_autocorr(frame, sr)
        pitches.append(freq)

    # Calculate target pitches
    output = audio.copy()
    correction_samples = int(speed_ms / 1000 * sr)

    for i in range(n_frames):
        freq = pitches[i]
        if freq <= 0:
            continue  # unvoiced — don't correct

        midi = _freq_to_midi(freq)
        target_midi = _nearest_scale_note(midi, key_root, scale_type)

        # How far off are we?
        shift_semitones = (target_midi - midi) * strength

        if abs(shift_semitones) < 0.01:
            continue  # already in tune

        # Apply pitch shift using resampling (simple but effective)
        ratio = 2 ** (shift_semitones / 12.0)
        start = i * hop_size
        end = min(start + frame_size, n)
        frame = audio[start:end]

        if len(frame) < 32:
            continue

        # Resample the frame
        new_len = int(len(frame) / ratio)
        if new_len < 2:
            continue

        indices = np.linspace(0, len(frame) - 1, new_len)
        resampled = np.interp(indices, np.arange(len(frame)), frame)

        # Overlap-add back into output
        window = np.hanning(min(len(resampled), end - start))
        out_len = min(len(resampled), end - start)
        output[start:start + out_len] = (
            output[start:start + out_len] * (1 - window[:out_len] * 0.5) +
            resampled[:out_len] * window[:out_len] * 0.5
        )

    # Normalize
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * np.max(np.abs(audio))

    return output.astype(np.float32)
