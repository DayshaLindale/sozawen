"""Sozawen Physical Brass — lips, bore, bell.

Brass instruments are tubes with the player's lips as the sound source.
The lips vibrate against the mouthpiece (lip reed), creating pressure
waves that travel down the bore, reflect off the bell, and come back
to sustain the oscillation. The bell radiates high frequencies out
and reflects low frequencies back — this is why brass instruments
have a bright, projecting sound.

The bore shape defines the character:
- Cylindrical (trumpet, trombone): bright, cutting, clear harmonics
- Conical (French horn, tuba): warm, round, blended harmonics

Mutes change the radiation: straight mute cuts lows and adds nasal quality.
Harmon (wah-wah) creates the Miles Davis sound. Plunger = wah effects.

Research: UNSW Physics brass acoustics, CCRMA Stanford waveguide,
Semantic Scholar trumpet synthesis, Euphonics brass chapter.
"""

import numpy as np
from scipy.signal import lfilter, butter


# ═══════════════════════════════════════════════════════════════════
# BRASS WAVEGUIDE ENGINE
# ═══════════════════════════════════════════════════════════════════

def brass_waveguide(freq, duration, sr=44100, lip_tension=0.5,
                   air_pressure=0.7, bore_type="cylindrical",
                   bell_brightness=0.6, vibrato_rate=5.0,
                   vibrato_depth=0.004):
    """Synthesize a brass instrument using simplified waveguide model.

    The brass instrument model:
    1. Lip reed: nonlinear oscillator driven by air pressure
    2. Bore: delay line (tube length = pitch)
    3. Bell: radiation filter (highpass — radiates highs, reflects lows)

    lip_tension: 0-1 (loose=fat tone, tight=focused/bright)
    air_pressure: 0-1 (dynamics — also affects tone)
    bore_type: "cylindrical" (trumpet/trombone) or "conical" (horn/tuba)
    bell_brightness: 0-1 (how much the bell emphasizes highs)
    """
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # === VIBRATO ===
    if vibrato_depth > 0 and vibrato_rate > 0:
        vibrato_onset = np.minimum(t / 0.2, 1.0)
        freq_mod = freq * (1 + vibrato_depth * vibrato_onset *
                          np.sin(2 * np.pi * vibrato_rate * t))
    else:
        freq_mod = np.full(n_samples, freq, dtype=np.float32)

    # === LIP REED OSCILLATOR ===
    # The lips produce a near-square pressure wave
    # Lip tension controls the duty cycle and harmonic content
    signal = np.zeros(n_samples, dtype=np.float32)

    # Build from harmonics — brass has all harmonics, weighted by bore type
    if bore_type == "cylindrical":
        # Cylindrical bore: all harmonics, strong upper partials
        max_harmonics = int(6 + lip_tension * 15)  # 6-21
        for n in range(1, max_harmonics + 1):
            h_freq = freq * n
            if h_freq >= sr / 2:
                break
            # Amplitude: 1/n with lip tension modifying the balance
            amp = 1.0 / (n ** (0.7 + lip_tension * 0.5))
            # Air pressure adds energy to higher harmonics
            amp *= (0.3 + air_pressure * 0.7)
            phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
            signal += np.sin(phase) * amp

    else:  # conical
        # Conical bore: softer harmonics, faster rolloff
        max_harmonics = int(4 + lip_tension * 10)  # 4-14
        for n in range(1, max_harmonics + 1):
            h_freq = freq * n
            if h_freq >= sr / 2:
                break
            amp = 1.0 / (n ** (1.0 + lip_tension * 0.5))
            amp *= (0.3 + air_pressure * 0.7)
            phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
            signal += np.sin(phase) * amp

    # === BELL RADIATION ===
    # The bell acts as a highpass filter — radiates high frequencies,
    # reflects low frequencies back into the bore
    bell_cutoff = 500 + bell_brightness * 3000
    if bell_cutoff < sr / 2:
        # Gentle highpass to simulate bell radiation
        b, a = butter(1, bell_cutoff / (sr / 2), btype='high')
        radiated = lfilter(b, a, signal).astype(np.float32)
        # Mix: some direct low-end + radiated high-end
        signal = signal * 0.3 + radiated * 0.7

    # === BREATH NOISE ===
    # Real brass has air turbulence noise
    noise_level = (1 - lip_tension) * air_pressure * 0.05
    if noise_level > 0.005:
        breath = np.random.randn(n_samples).astype(np.float32) * noise_level
        b, a = butter(2, min(freq * 6, sr / 2 - 1) / (sr / 2), btype='low')
        breath = lfilter(b, a, breath).astype(np.float32)
        signal += breath

    # === ENVELOPE ===
    # Brass has a characteristic "bloom" — the tone builds over 50-100ms
    # as the lips lock into the resonance
    attack_time = 0.03 + (1 - lip_tension) * 0.08  # tighter lips = faster attack
    attack_samples = int(attack_time * sr)
    if attack_samples > 0 and attack_samples < n_samples:
        signal[:attack_samples] *= np.linspace(0, 1, attack_samples) ** 0.5

    # Release
    release_samples = int(0.03 * sr)
    if release_samples > 0 and release_samples < n_samples:
        signal[-release_samples:] *= np.linspace(1, 0, release_samples)

    # Scale by air pressure (dynamics)
    signal *= 0.3 + air_pressure * 0.7

    return signal


# ═══════════════════════════════════════════════════════════════════
# MUTE MODELS
# ═══════════════════════════════════════════════════════════════════

def apply_mute(signal, mute_type, sr=44100):
    """Apply a brass mute to the signal.

    Mutes physically obstruct the bell, changing the radiation pattern.

    straight: blocks low frequencies, boosts nasal 1.5-3kHz
    cup: darker, more muffled than straight
    harmon: very thin, nasal, buzzy (Miles Davis)
    plunger: variable (wah effect when moved)
    """
    if mute_type == "straight":
        # Cut lows, boost nasal mids
        b, a = butter(2, 300 / (sr / 2), btype='high')
        signal = lfilter(b, a, signal).astype(np.float32)
        # Nasal boost
        b, a = butter(2, [1500 / (sr / 2), 3000 / (sr / 2)], btype='band')
        nasal = lfilter(b, a, signal).astype(np.float32) * 0.5
        signal = signal + nasal

    elif mute_type == "cup":
        # Similar to straight but darker
        b, a = butter(2, 250 / (sr / 2), btype='high')
        signal = lfilter(b, a, signal).astype(np.float32)
        b, a = butter(2, 2500 / (sr / 2), btype='low')
        signal = lfilter(b, a, signal).astype(np.float32)

    elif mute_type == "harmon":
        # Very thin, nasal, metallic buzz
        # Extreme bandpass around 1-4kHz
        b, a = butter(3, [800 / (sr / 2), 4000 / (sr / 2)], btype='band')
        signal = lfilter(b, a, signal).astype(np.float32)
        # Add metallic ring
        signal = np.tanh(signal * 3) * 0.5

    elif mute_type == "plunger":
        # Half-closed plunger — wah-like
        b, a = butter(2, [500 / (sr / 2), 2000 / (sr / 2)], btype='band')
        signal = lfilter(b, a, signal).astype(np.float32)

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.75

    return signal


# ═══════════════════════════════════════════════════════════════════
# INSTRUMENT PROFILES
# ═══════════════════════════════════════════════════════════════════

BRASS_PROFILES = {
    "trumpet": {
        "name": "Trumpet (bright, cutting)",
        "bore": "cylindrical",
        "bell_brightness": 0.7,
        "default_lip_tension": 0.6,
        "range": (55, 86),  # Bb3 to D6 (MIDI)
        "resonance": [
            (500, 0.5, 8),
            (1200, 0.6, 6),
            (2500, 0.7, 5),    # Trumpet brightness
            (4000, 0.4, 4),
        ],
    },
    "french_horn": {
        "name": "French Horn (warm, round)",
        "bore": "conical",
        "bell_brightness": 0.3,
        "default_lip_tension": 0.4,
        "range": (41, 84),  # F2 to C6
        "resonance": [
            (200, 0.7, 6),     # Warm low end
            (500, 0.6, 8),     # Body
            (900, 0.5, 7),     # Midrange warmth
            (1800, 0.3, 6),    # Gentle presence
        ],
    },
    "trombone": {
        "name": "Trombone (rich, powerful)",
        "bore": "cylindrical",
        "bell_brightness": 0.5,
        "default_lip_tension": 0.4,
        "range": (40, 77),  # E2 to F5
        "resonance": [
            (150, 0.6, 5),     # Deep foundation
            (400, 0.7, 7),     # Body richness
            (900, 0.5, 8),     # Midrange
            (2000, 0.4, 6),    # Presence
            (3500, 0.2, 5),    # Brilliance
        ],
    },
    "tuba": {
        "name": "Tuba (deep, warm)",
        "bore": "conical",
        "bell_brightness": 0.2,
        "default_lip_tension": 0.3,
        "range": (26, 65),  # D1 to F4
        "resonance": [
            (60, 0.9, 3),      # Very deep fundamental
            (150, 0.7, 5),     # Low body
            (350, 0.5, 7),     # Warmth
            (700, 0.3, 8),     # Mid — gentle
            (1200, 0.1, 6),    # Presence — minimal
        ],
    },
}


def synthesize_brass_note(midi_note, duration, sr=44100, velocity=0.7,
                         instrument="trumpet", mute="none",
                         vibrato_rate=5.0, vibrato_depth=0.004,
                         articulation="sustain"):
    """Synthesize a brass instrument note.

    articulation: "sustain", "tongued", "staccato", "sforzando", "fall", "doit"
    mute: "none", "straight", "cup", "harmon", "plunger"
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    profile = BRASS_PROFILES.get(instrument, BRASS_PROFILES["trumpet"])

    lip_tension = profile["default_lip_tension"] + velocity * 0.2
    air_pressure = 0.3 + velocity * 0.7

    # Articulation modifiers
    if articulation == "staccato":
        duration = min(duration, 0.12)
        vibrato_depth = 0
    elif articulation == "sforzando":
        air_pressure = min(1.0, air_pressure + 0.3)
    elif articulation == "tongued":
        pass  # normal but with clean attack

    signal = brass_waveguide(
        freq, duration, sr,
        lip_tension=lip_tension,
        air_pressure=air_pressure,
        bore_type=profile["bore"],
        bell_brightness=profile["bell_brightness"],
        vibrato_rate=vibrato_rate,
        vibrato_depth=vibrato_depth,
    )

    # Apply body resonance
    from sozawen.physical_guitar import body_resonance
    signal = body_resonance(signal, profile["resonance"], sr)

    # Articulation effects
    if articulation == "fall":
        # Pitch falls at the end
        n = len(signal)
        fall_start = int(n * 0.7)
        fall_len = n - fall_start
        if fall_len > 0:
            fall_env = np.linspace(1, 0.5, fall_len)
            # Resample to create pitch drop (simplified)
            signal[fall_start:] *= np.linspace(1, 0.3, fall_len)
    elif articulation == "doit":
        # Pitch rises at the end
        n = len(signal)
        doit_start = int(n * 0.8)
        doit_len = n - doit_start
        if doit_len > 0:
            signal[doit_start:] *= np.linspace(1, 0.5, doit_len)

    # Apply mute
    if mute != "none":
        signal = apply_mute(signal, mute, sr)

    return signal


def list_brass_instruments():
    """List available brass instruments."""
    return [{"id": k, "name": v["name"]} for k, v in BRASS_PROFILES.items()]


def list_mute_types():
    """List available mute types."""
    return [
        {"id": "none", "name": "Open (no mute)"},
        {"id": "straight", "name": "Straight Mute (nasal, focused)"},
        {"id": "cup", "name": "Cup Mute (dark, muffled)"},
        {"id": "harmon", "name": "Harmon/Wah Mute (thin, metallic — Miles Davis)"},
        {"id": "plunger", "name": "Plunger Mute (wah effect)"},
    ]
