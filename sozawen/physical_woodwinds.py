"""Sozawen Physical Woodwinds — reed, bore, tone holes.

Each woodwind has its own excitation mechanism:
- Flute: air jet across embouchure hole (jet-drive oscillator)
- Clarinet: single reed against mouthpiece (pressure-controlled valve)
- Oboe/Bassoon: double reed (two reeds vibrating against each other)
- Saxophone: single reed on conical bore

The bore shape determines the harmonic series:
- Cylindrical + closed end (clarinet): ODD harmonics only
  This is why clarinet has its characteristic hollow, woody sound
- Conical (sax, oboe, bassoon): ALL harmonics
  These instruments sound more "complete" and voice-like
- Cylindrical + open end (flute): ALL harmonics
  Flute can overblow at the octave, not the twelfth

Tone holes act as a lattice filter — open holes effectively
shorten the tube and add radiation points, changing both pitch
and tonal character.

Research: CCRMA Stanford digital waveguide single-reed implementation,
Acta Acustica tonehole lattice cutoff frequency, Euphonics woodwinds.
"""

import numpy as np
from scipy.signal import lfilter, butter
from sozawen.physical_guitar import body_resonance


# ═══════════════════════════════════════════════════════════════════
# WOODWIND SYNTHESIS ENGINE
# ═══════════════════════════════════════════════════════════════════

def woodwind_waveguide(freq, duration, sr=44100, breath_pressure=0.7,
                      embouchure=0.5, bore_type="cylindrical",
                      excitation_type="single_reed",
                      reed_hardness=0.5, breathiness=0.1,
                      vibrato_rate=5.0, vibrato_depth=0.003):
    """Synthesize a woodwind instrument using simplified waveguide.

    breath_pressure: 0-1 (dynamics and tone)
    embouchure: 0-1 (lip control — affects tuning and tone stability)
    bore_type: "cylindrical" (clarinet, flute) or "conical" (sax, oboe)
    excitation_type: "single_reed", "double_reed", "air_jet"
    reed_hardness: 0-1 (soft=dark, hard=bright)
    breathiness: 0-1 (air noise component)
    """
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # === VIBRATO ===
    if vibrato_depth > 0 and vibrato_rate > 0:
        vibrato_onset = np.minimum(t / 0.3, 1.0)
        freq_mod = freq * (1 + vibrato_depth * vibrato_onset *
                          np.sin(2 * np.pi * vibrato_rate * t))
    else:
        freq_mod = np.full(n_samples, freq, dtype=np.float32)

    # === EXCITATION MODEL ===
    signal = np.zeros(n_samples, dtype=np.float32)

    if excitation_type == "air_jet":
        # Flute: air jet creates near-sinusoidal tone with breathiness
        # All harmonics present (open tube), but upper partials are weak
        max_harmonics = int(5 + reed_hardness * 8)
        for n in range(1, max_harmonics + 1):
            h_freq = freq * n
            if h_freq >= sr / 2:
                break
            amp = 1.0 / (n ** (1.2 + embouchure * 0.5))
            amp *= breath_pressure
            phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
            signal += np.sin(phase) * amp

        # Flute breathiness — air noise is part of the sound
        breathiness = max(breathiness, 0.15)  # flute always has some breath

    elif excitation_type == "single_reed":
        if bore_type == "cylindrical":
            # Clarinet: ODD HARMONICS ONLY (closed-end cylindrical pipe)
            # This is the defining characteristic of clarinet sound
            max_harmonics = int(6 + reed_hardness * 12)
            for n in range(1, max_harmonics * 2 + 1, 2):  # odd only: 1, 3, 5, 7...
                h_freq = freq * n
                if h_freq >= sr / 2:
                    break
                amp = 1.0 / (n ** (0.8 + (1 - reed_hardness) * 0.4))
                amp *= breath_pressure
                phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
                signal += np.sin(phase) * amp
        else:
            # Saxophone: conical bore, all harmonics
            max_harmonics = int(6 + reed_hardness * 10)
            for n in range(1, max_harmonics + 1):
                h_freq = freq * n
                if h_freq >= sr / 2:
                    break
                amp = 1.0 / (n ** (0.7 + (1 - reed_hardness) * 0.5))
                amp *= breath_pressure
                # Sax has slightly emphasized even harmonics
                if n % 2 == 0:
                    amp *= 1.1
                phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
                signal += np.sin(phase) * amp

    elif excitation_type == "double_reed":
        # Oboe/Bassoon: more complex vibration, richer harmonics
        max_harmonics = int(8 + reed_hardness * 12)
        for n in range(1, max_harmonics + 1):
            h_freq = freq * n
            if h_freq >= sr / 2:
                break
            # Double reed produces stronger upper harmonics than single reed
            amp = 1.0 / (n ** (0.6 + (1 - reed_hardness) * 0.3))
            amp *= breath_pressure
            phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
            signal += np.sin(phase) * amp

    # === BREATH NOISE ===
    if breathiness > 0.01:
        breath = np.random.randn(n_samples).astype(np.float32) * breathiness * 0.15
        # Filter breath noise to instrument's range
        breath_cutoff = min(freq * 10, sr / 2 - 1)
        b, a = butter(2, breath_cutoff / (sr / 2), btype='low')
        breath = lfilter(b, a, breath).astype(np.float32)
        signal += breath * breath_pressure

    # === ENVELOPE ===
    # Woodwinds have fast attack (reed starts vibrating quickly)
    attack_samples = int(0.02 * sr)
    if attack_samples > 0 and attack_samples < n_samples:
        signal[:attack_samples] *= np.linspace(0, 1, attack_samples)

    # Release
    release_samples = int(0.03 * sr)
    if release_samples > 0 and release_samples < n_samples:
        signal[-release_samples:] *= np.linspace(1, 0, release_samples)

    return signal


# ═══════════════════════════════════════════════════════════════════
# INSTRUMENT PROFILES
# ═══════════════════════════════════════════════════════════════════

WIND_PROFILES = {
    "flute": {
        "name": "Flute (pure, bright, breathy)",
        "excitation": "air_jet",
        "bore": "cylindrical",
        "default_reed_hardness": 0.5,
        "default_breathiness": 0.2,
        "range": (60, 96),  # C4 to C7
        "resonance": [
            (800, 0.4, 8),      # Body resonance
            (2000, 0.5, 6),     # Presence
            (4000, 0.4, 5),     # Brilliance
            (6000, 0.3, 4),     # Air — flute has high-end sparkle
        ],
    },
    "clarinet": {
        "name": "Clarinet (warm, woody, hollow)",
        "excitation": "single_reed",
        "bore": "cylindrical",  # THIS is what makes clarinet special — odd harmonics
        "default_reed_hardness": 0.5,
        "default_breathiness": 0.05,
        "range": (50, 90),  # D3 to F#6
        "resonance": [
            (300, 0.6, 7),      # Chalumeau register warmth
            (600, 0.5, 8),      # Woody character
            (1200, 0.4, 7),     # Throat tones
            (2500, 0.3, 6),     # Clarion register brightness
        ],
    },
    "oboe": {
        "name": "Oboe (nasal, penetrating, singing)",
        "excitation": "double_reed",
        "bore": "conical",
        "default_reed_hardness": 0.6,
        "default_breathiness": 0.03,
        "range": (58, 91),  # Bb3 to G6
        "resonance": [
            (500, 0.5, 7),      # Body
            (1000, 0.7, 5),     # Nasal midrange — oboe signature
            (2000, 0.6, 5),     # Penetrating quality
            (3500, 0.4, 4),     # Brilliance
        ],
    },
    "bassoon": {
        "name": "Bassoon (dark, warm, complex)",
        "excitation": "double_reed",
        "bore": "conical",
        "default_reed_hardness": 0.4,
        "default_breathiness": 0.05,
        "range": (34, 75),  # Bb1 to Eb5
        "resonance": [
            (100, 0.7, 5),      # Deep body
            (250, 0.6, 7),      # Warmth
            (500, 0.5, 8),      # Mid
            (1000, 0.3, 7),     # Upper body
            (2000, 0.2, 6),     # Presence — gentle
        ],
    },
    "alto_sax": {
        "name": "Alto Saxophone (warm, expressive)",
        "excitation": "single_reed",
        "bore": "conical",
        "default_reed_hardness": 0.5,
        "default_breathiness": 0.08,
        "range": (49, 80),  # Db3 to Ab5
        "resonance": [
            (300, 0.6, 6),      # Body warmth
            (700, 0.7, 5),      # Fat midrange — sax signature
            (1500, 0.5, 6),     # Presence
            (3000, 0.3, 5),     # Brightness
            (5000, 0.15, 4),    # Edge
        ],
    },
    "tenor_sax": {
        "name": "Tenor Saxophone (rich, soulful)",
        "excitation": "single_reed",
        "bore": "conical",
        "default_reed_hardness": 0.5,
        "default_breathiness": 0.08,
        "range": (44, 76),  # Ab2 to E5
        "resonance": [
            (200, 0.7, 5),      # Deep body
            (500, 0.8, 5),      # Rich midrange
            (1000, 0.5, 6),     # Body
            (2200, 0.4, 5),     # Presence
            (4000, 0.2, 4),     # Top
        ],
    },
    "soprano_sax": {
        "name": "Soprano Saxophone (bright, piercing)",
        "excitation": "single_reed",
        "bore": "conical",
        "default_reed_hardness": 0.6,
        "default_breathiness": 0.06,
        "range": (56, 88),  # Ab3 to E6
        "resonance": [
            (500, 0.5, 7),      # Body
            (1200, 0.6, 5),     # Bright midrange
            (2500, 0.7, 5),     # Piercing quality
            (4500, 0.4, 4),     # Edge
        ],
    },
    "baritone_sax": {
        "name": "Baritone Saxophone (deep, powerful)",
        "excitation": "single_reed",
        "bore": "conical",
        "default_reed_hardness": 0.4,
        "default_breathiness": 0.1,
        "range": (36, 68),  # C2 to Ab4
        "resonance": [
            (100, 0.8, 4),      # Very deep
            (300, 0.7, 6),      # Body
            (600, 0.6, 7),      # Warmth
            (1200, 0.4, 6),     # Mid
            (2500, 0.2, 5),     # Presence
        ],
    },
}


def synthesize_wind_note(midi_note, duration, sr=44100, velocity=0.7,
                        instrument="alto_sax", vibrato_rate=5.0,
                        vibrato_depth=0.003, articulation="legato"):
    """Synthesize a woodwind note.

    articulation: "legato", "tongued", "staccato"
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    profile = WIND_PROFILES.get(instrument, WIND_PROFILES["alto_sax"])

    breath = 0.3 + velocity * 0.7
    reed = profile["default_reed_hardness"] + velocity * 0.15

    if articulation == "staccato":
        duration = min(duration, 0.15)
        vibrato_depth = 0

    signal = woodwind_waveguide(
        freq, duration, sr,
        breath_pressure=breath,
        embouchure=0.5 + velocity * 0.2,
        bore_type=profile["bore"],
        excitation_type=profile["excitation"],
        reed_hardness=reed,
        breathiness=profile["default_breathiness"],
        vibrato_rate=vibrato_rate,
        vibrato_depth=vibrato_depth,
    )

    # Body resonance
    signal = body_resonance(signal, profile["resonance"], sr)

    return signal


def list_wind_instruments():
    """List available woodwind instruments."""
    return [{"id": k, "name": v["name"]} for k, v in WIND_PROFILES.items()]
