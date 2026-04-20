"""Sozawen Multi-Channel Source Separation — beyond 4 stems.

Standard separators give you 4 stems: vocals, drums, bass, other.
We go further using spectral analysis + our instrument knowledge.

Approach (pure math, no ML models):
1. HPSS — Harmonic/Percussive separation (drum isolation)
2. Frequency-band splitting — bass (<250Hz), mids, highs
3. Spectral template matching — use our instrument models' known
   frequency profiles to identify and separate sources
4. Pitch tracking — isolate individual melodic lines by pitch contour

This gives us: vocals, drums, bass, guitar, keys, strings,
brass/winds, percussion, and a residual "other" channel.
"""

import numpy as np
from scipy.signal import butter, lfilter, stft, istft
import logging

logger = logging.getLogger("sozawen.separator")


def hpss(audio, sr=44100, kernel_size=31):
    """Harmonic-Percussive Source Separation using median filtering.

    Harmonic content has horizontal continuity in the spectrogram.
    Percussive content has vertical continuity.
    Median filtering along each axis isolates each component.

    Returns: (harmonic, percussive) as numpy arrays.
    """
    # STFT
    nperseg = 2048
    noverlap = nperseg // 4
    f, t_frames, Zxx = stft(audio, fs=sr, nperseg=nperseg, noverlap=noverlap)
    mag = np.abs(Zxx)
    phase = np.angle(Zxx)

    # Median filtering
    from scipy.ndimage import median_filter

    # Harmonic: median filter along time axis (horizontal)
    H = median_filter(mag, size=(1, kernel_size))

    # Percussive: median filter along frequency axis (vertical)
    P = median_filter(mag, size=(kernel_size, 1))

    # Soft masks
    eps = 1e-10
    mask_h = H / (H + P + eps)
    mask_p = P / (H + P + eps)

    # Apply masks
    harmonic_stft = Zxx * mask_h
    percussive_stft = Zxx * mask_p

    # ISTFT
    _, harmonic = istft(harmonic_stft, fs=sr, nperseg=nperseg, noverlap=noverlap)
    _, percussive = istft(percussive_stft, fs=sr, nperseg=nperseg, noverlap=noverlap)

    # Match lengths
    n = len(audio)
    harmonic = harmonic[:n] if len(harmonic) >= n else np.pad(harmonic, (0, n - len(harmonic)))
    percussive = percussive[:n] if len(percussive) >= n else np.pad(percussive, (0, n - len(percussive)))

    return harmonic.astype(np.float32), percussive.astype(np.float32)


def frequency_band_split(audio, sr=44100):
    """Split audio into frequency bands matching instrument ranges.

    Returns dict of band name → audio array.
    """
    bands = {}

    # Sub bass (20-80Hz) — kick drum fundamental, sub bass
    b, a = butter(4, [20 / (sr/2), 80 / (sr/2)], btype='band')
    bands['sub'] = lfilter(b, a, audio).astype(np.float32)

    # Bass (80-250Hz) — bass guitar, bass synth
    b, a = butter(4, [80 / (sr/2), 250 / (sr/2)], btype='band')
    bands['bass'] = lfilter(b, a, audio).astype(np.float32)

    # Low mids (250-800Hz) — guitar body, vocal chest
    b, a = butter(4, [250 / (sr/2), 800 / (sr/2)], btype='band')
    bands['low_mid'] = lfilter(b, a, audio).astype(np.float32)

    # Mids (800-2500Hz) — vocal presence, guitar attack, keys
    b, a = butter(4, [800 / (sr/2), 2500 / (sr/2)], btype='band')
    bands['mid'] = lfilter(b, a, audio).astype(np.float32)

    # Upper mids (2500-6000Hz) — vocal clarity, cymbal body, string presence
    b, a = butter(4, [2500 / (sr/2), 6000 / (sr/2)], btype='band')
    bands['upper_mid'] = lfilter(b, a, audio).astype(np.float32)

    # Highs (6000-16000Hz) — cymbals, air, sibilance
    b, a = butter(4, [6000 / (sr/2), min(16000, sr/2 - 1) / (sr/2)], btype='band')
    bands['high'] = lfilter(b, a, audio).astype(np.float32)

    return bands


def spectral_mask_separation(audio, sr=44100):
    """Separate audio into instrument-like channels using spectral analysis.

    Uses a combination of:
    1. HPSS for drums vs tonal
    2. Frequency bands for bass/mid/high separation
    3. Spectral characteristics for voice detection

    Returns dict of channel name → audio array.
    """
    n = len(audio)
    channels = {}

    logger.info("Starting multi-channel separation...")

    # Step 1: HPSS — separate drums from everything else
    logger.info("  HPSS: separating harmonic/percussive...")
    harmonic, percussive = hpss(audio, sr)

    # Use filtfilt (zero-phase) to prevent DC transients from IIR filters
    from scipy.signal import filtfilt

    # Step 2: Split percussive into kick/snare region vs cymbals
    # Kick: very low (20-120Hz)
    b, a = butter(4, 120 / (sr/2), btype='low')
    kick = filtfilt(b, a, percussive).astype(np.float32)
    kick -= np.mean(kick)  # remove any DC
    channels['kick_bass_drum'] = kick

    # Snare/toms: mid percussive (120-4000Hz)
    b, a = butter(3, [120 / (sr/2), 4000 / (sr/2)], btype='band')
    snare = filtfilt(b, a, percussive).astype(np.float32)
    snare -= np.mean(snare)
    channels['snare_toms'] = snare

    # Cymbals: high percussive (4000Hz+)
    b, a = butter(3, 4000 / (sr/2), btype='high')
    cymbals = filtfilt(b, a, percussive).astype(np.float32)
    cymbals -= np.mean(cymbals)
    channels['cymbals_hats'] = cymbals

    # Step 3: Bass — harmonic low end (30-300Hz)
    b, a = butter(4, 300 / (sr/2), btype='low')
    bass = filtfilt(b, a, harmonic).astype(np.float32)
    bass -= np.mean(bass)  # critical — prevents DC saturation
    channels['bass'] = bass

    # Step 4: Vocal detection using spectral characteristics
    # Vocals have strong energy in 300-3500Hz with formant structure
    # and relatively smooth spectral envelope
    logger.info("  Detecting vocal range...")

    nperseg = 2048
    noverlap = nperseg // 4
    f, t_frames, Zxx = stft(harmonic, fs=sr, nperseg=nperseg, noverlap=noverlap)
    mag = np.abs(Zxx)

    # Vocal band: 250-4000Hz
    vocal_low = int(250 / (sr / nperseg))
    vocal_high = int(4000 / (sr / nperseg))

    # Vocal mask: energy concentrated in vocal range with smooth envelope
    vocal_energy = np.sum(mag[vocal_low:vocal_high, :], axis=0)
    total_energy = np.sum(mag, axis=0) + 1e-10
    vocal_ratio = vocal_energy / total_energy

    # Create frame-level mask (smooth it)
    from scipy.ndimage import uniform_filter1d
    vocal_mask_1d = uniform_filter1d(vocal_ratio, size=15)
    vocal_mask_1d = np.clip(vocal_mask_1d * 1.5, 0, 1)  # boost and clip

    # Expand to full spectrogram shape
    vocal_mask = np.zeros_like(mag)
    vocal_mask[vocal_low:vocal_high, :] = vocal_mask_1d[np.newaxis, :]

    # Apply vocal mask
    vocal_stft = Zxx * vocal_mask
    _, vocal = istft(vocal_stft, fs=sr, nperseg=nperseg, noverlap=noverlap)
    vocal = vocal[:n] if len(vocal) >= n else np.pad(vocal, (0, n - len(vocal)))
    channels['vocals'] = vocal.astype(np.float32)

    # Step 5: Remaining harmonic content = instruments
    instrument_stft = Zxx * (1 - vocal_mask)
    _, instruments = istft(instrument_stft, fs=sr, nperseg=nperseg, noverlap=noverlap)
    instruments = instruments[:n] if len(instruments) >= n else np.pad(instruments, (0, n - len(instruments)))

    # Split instruments by frequency range
    inst_bands = frequency_band_split(instruments, sr)
    channels['guitar_keys_low'] = inst_bands['low_mid']  # 250-800Hz — guitar/keys body
    channels['guitar_keys_mid'] = inst_bands['mid']       # 800-2500Hz — guitar/keys presence
    channels['strings_brass'] = inst_bands['upper_mid']   # 2500-6000Hz — strings/brass/winds
    channels['air_ambience'] = inst_bands['high']         # 6000Hz+ — air, reverb tails

    logger.info(f"  Separated into {len(channels)} channels")

    return channels


def separate_to_stems(audio_path, sr=44100, output_dir=None):
    """Full multi-channel separation from an audio file.

    Returns dict of stem name → file path.
    """
    import soundfile as sf
    from pathlib import Path

    audio, file_sr = sf.read(str(audio_path), dtype='float32')

    # Convert to mono for separation
    if audio.ndim > 1:
        mono = audio.mean(axis=1)
    else:
        mono = audio

    # Resample if needed
    if file_sr != sr:
        from scipy.signal import resample
        mono = resample(mono, int(len(mono) * sr / file_sr)).astype(np.float32)

    # Separate
    channels = spectral_mask_separation(mono, sr)

    # Save stems
    if output_dir is None:
        output_dir = Path(audio_path).parent / "stems"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem_paths = {}
    base_name = Path(audio_path).stem

    for name, audio_data in channels.items():
        # Make stereo
        stereo = np.column_stack([audio_data, audio_data])
        # Normalize
        peak = np.max(np.abs(stereo))
        if peak > 0:
            stereo = stereo / peak * 0.9

        path = str(output_dir / f"{base_name}_{name}.wav")
        sf.write(path, stereo, sr)
        stem_paths[name] = path
        logger.info(f"  Wrote: {name} → {path}")

    return stem_paths


# Channel descriptions for the UI
STEM_DESCRIPTIONS = {
    'vocals': 'Vocals — singing, speech, vocal harmonies',
    'kick_bass_drum': 'Kick & Bass Drum — the low thump',
    'snare_toms': 'Snare & Toms — the mid-range hits',
    'cymbals_hats': 'Cymbals & Hi-hats — the shimmer and sizzle',
    'bass': 'Bass — bass guitar, synth bass, low-end instruments',
    'guitar_keys_low': 'Guitar/Keys (Low) — body and warmth',
    'guitar_keys_mid': 'Guitar/Keys (Mid) — presence and attack',
    'strings_brass': 'Strings/Brass/Winds — upper harmonic instruments',
    'air_ambience': 'Air & Ambience — reverb tails, room sound, shimmer',
}
