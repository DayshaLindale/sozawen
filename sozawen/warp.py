"""Sozawen Warp Engine — time stretch without pitch change.

Uses a phase vocoder to stretch or compress audio in time
while preserving pitch. This is how you make a recording
fit a different tempo without sounding like chipmunks.

The phase vocoder works by:
1. STFT — decompose audio into overlapping frequency frames
2. Modify the time axis — stretch/compress the frame spacing
3. Phase correction — maintain phase coherence between frames
4. ISTFT — reconstruct audio from modified frames

Pure math. No ML. No libraries beyond numpy/scipy.
"""

import numpy as np
from scipy.signal import stft, istft


def time_stretch(audio, rate, sr=44100):
    """Stretch audio in time without changing pitch.

    Parameters:
        audio: mono numpy array
        rate: stretch factor (0.5 = half speed/double length,
              2.0 = double speed/half length)
        sr: sample rate

    Returns: time-stretched audio as numpy array.
    """
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if abs(rate - 1.0) < 0.01:
        return audio  # no change needed

    audio = audio.astype(np.float64)
    n = len(audio)

    # STFT parameters
    n_fft = 2048
    hop_in = n_fft // 4  # input hop
    hop_out = int(hop_in / rate)  # output hop — this changes the time scale

    # Forward STFT
    f, t_frames, Zxx = stft(audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_in)

    n_frames = Zxx.shape[1]
    n_bins = Zxx.shape[0]

    # Phase vocoder — correct phases for the new hop size
    phase = np.angle(Zxx)
    magnitude = np.abs(Zxx)

    # Expected phase advance per frame at each frequency
    freq_bins = np.arange(n_bins)
    expected_phase_advance = 2 * np.pi * freq_bins * hop_in / n_fft

    # Reconstruct with corrected phase
    output_phase = np.zeros(n_bins)
    output_frames = []

    for i in range(n_frames):
        if i == 0:
            output_phase = phase[:, 0]
        else:
            # Phase difference from input
            phase_diff = phase[:, i] - phase[:, i - 1]
            # Remove expected advance
            phase_diff -= expected_phase_advance
            # Wrap to [-pi, pi]
            phase_diff = phase_diff - 2 * np.pi * np.round(phase_diff / (2 * np.pi))
            # Instantaneous frequency deviation
            inst_freq = expected_phase_advance + phase_diff
            # Accumulate output phase with output hop
            output_phase += inst_freq * (hop_out / hop_in)

        # Reconstruct frame
        frame = magnitude[:, i] * np.exp(1j * output_phase)
        output_frames.append(frame)

    # Build output STFT matrix
    output_stft = np.array(output_frames).T

    # Inverse STFT with output hop
    _, output = istft(output_stft, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_out)

    return output.astype(np.float32)


def fit_to_tempo(audio, original_bpm, target_bpm, sr=44100):
    """Stretch audio to match a target tempo.

    Parameters:
        audio: numpy array
        original_bpm: detected BPM of the audio
        target_bpm: desired BPM
        sr: sample rate

    Returns: tempo-matched audio.
    """
    if original_bpm <= 0 or target_bpm <= 0:
        return audio

    rate = target_bpm / original_bpm
    return time_stretch(audio, rate, sr)
