"""Sozawen Physical Piano — hammer, string, soundboard, soul.

Not a sampled piano. A MODELED piano. The hammer is a nonlinear
felt spring that changes hardness with velocity — soft touch gives
you the fundamental, hard touch gives you harmonics. This is WHY
piano changes TONE with dynamics, not just volume.

The strings have inharmonicity — stiffness stretches the harmonics
sharp. This is the piano's signature sound. Without it, a piano
sounds like an organ.

The soundboard couples everything. It's what makes the piano SING.

Research: Penn State piano acoustics, CCRMA Stanford waveguide,
Juan José Burred piano acoustics, arXiv:2409.03481
"""

import numpy as np
from scipy.signal import lfilter, butter

from sozawen.physical_guitar import body_resonance


# ═══════════════════════════════════════════════════════════════════
# INHARMONICITY — what makes a piano a piano
# ═══════════════════════════════════════════════════════════════════

def inharmonic_partials(fundamental, num_partials, B):
    """Compute stretched partial frequencies due to string stiffness.

    Real piano partials follow: f_n = n * f0 * sqrt(1 + B * n²)
    where B is the inharmonicity coefficient.

    B depends on string properties:
    B = π³ × E × d⁴ / (64 × T × L²)
    E = Young's modulus, d = diameter, T = tension, L = length

    Typical values:
    Bass strings (A0): B ≈ 0.00004
    Middle C: B ≈ 0.0003
    Treble (C7): B ≈ 0.004
    """
    partials = []
    for n in range(1, num_partials + 1):
        freq = n * fundamental * np.sqrt(1 + B * n * n)
        partials.append(freq)
    return partials


# Pre-computed inharmonicity coefficients for 88 keys
# Smoothly interpolated from measured values
def get_inharmonicity(midi_note):
    """Get inharmonicity coefficient B for a given MIDI note.

    MIDI 21 (A0) → B ≈ 0.00004
    MIDI 60 (C4) → B ≈ 0.0003
    MIDI 108 (C8) → B ≈ 0.006
    """
    # Exponential interpolation from bass to treble
    # Lower notes: long thick strings, low B
    # Higher notes: short thin strings, high B
    normalized = (midi_note - 21) / 87  # 0 to 1 across keyboard
    B = 0.00004 * np.exp(normalized * 5)  # exponential rise
    return min(B, 0.01)


# ═══════════════════════════════════════════════════════════════════
# HAMMER MODEL — nonlinear felt
# ═══════════════════════════════════════════════════════════════════

def hammer_spectrum(velocity, num_partials):
    """Compute per-partial amplitudes based on hammer velocity.

    Soft hit (low velocity): hammer is soft, acts as lowpass filter.
    Only fundamental and low harmonics come through.

    Hard hit (high velocity): felt compresses, hammer becomes rigid.
    Full harmonic spectrum with strong high partials.

    This is the physics that makes piano expressive — velocity
    changes TIMBRE not just volume.
    """
    # Velocity 0-1 maps to hammer hardness
    # hardness controls the spectral rolloff rate
    hardness = 0.3 + velocity * 0.7  # 0.3 (pianissimo) to 1.0 (fortissimo)

    amplitudes = []
    for n in range(1, num_partials + 1):
        # Higher harmonics roll off faster for soft hammer
        # The rolloff is steeper for lower hardness
        rolloff = np.exp(-n * (1 - hardness) * 0.8)

        # Even partials are slightly weaker (hammer hits near node)
        if n % 2 == 0:
            rolloff *= 0.85

        amplitudes.append(rolloff)

    return amplitudes


# ═══════════════════════════════════════════════════════════════════
# STRING DECAY — frequency-dependent damping
# ═══════════════════════════════════════════════════════════════════

def string_decay_rates(fundamental, num_partials, sustain_pedal=False):
    """Compute per-partial decay rates.

    Higher partials decay faster than lower ones (air resistance
    and internal friction affect short wavelengths more).

    With sustain pedal: all decay rates decrease (strings ring longer
    because dampers are lifted).
    """
    rates = []
    base_decay = 2.0 if fundamental > 500 else (4.0 if fundamental < 100 else 3.0)

    if sustain_pedal:
        base_decay *= 1.5  # longer sustain

    for n in range(1, num_partials + 1):
        # Higher partials decay faster
        rate = base_decay / (1 + n * 0.3)
        rates.append(rate)

    return rates


# ═══════════════════════════════════════════════════════════════════
# PIANO SYNTHESIZER
# ═══════════════════════════════════════════════════════════════════

def synthesize_piano_note(midi_note, duration, sr=44100, velocity=0.7,
                         piano_model="steinway_d", sustain_pedal=False,
                         una_corda=False):
    """Synthesize a physically modeled piano note.

    midi_note: MIDI note number (21-108 for standard piano)
    velocity: 0-1 (changes TONE and volume)
    piano_model: which piano to model
    sustain_pedal: if True, dampers lifted (longer sustain + sympathetic)
    una_corda: if True, soft pedal (softer, darker tone)
    """
    from sozawen.music_theory import midi_to_note

    # Fundamental frequency
    fundamental = 440.0 * 2 ** ((midi_note - 69) / 12)

    # Inharmonicity
    B = get_inharmonicity(midi_note)

    # Number of partials — more for lower notes, fewer for higher
    if midi_note < 40:
        num_partials = 30
    elif midi_note < 60:
        num_partials = 25
    elif midi_note < 80:
        num_partials = 18
    else:
        num_partials = 12

    # Compute stretched partial frequencies
    partials = inharmonic_partials(fundamental, num_partials, B)

    # Hammer spectrum (velocity-dependent)
    if una_corda:
        velocity *= 0.7  # softer
    amplitudes = hammer_spectrum(velocity, num_partials)

    # Decay rates
    decay_rates = string_decay_rates(fundamental, num_partials, sustain_pedal)

    # Duration
    actual_duration = duration
    if sustain_pedal:
        actual_duration = max(duration, duration * 1.5)
    n_samples = int(actual_duration * sr)

    # Generate audio — additive synthesis with inharmonic partials
    t = np.linspace(0, actual_duration, n_samples, dtype=np.float32)
    signal = np.zeros(n_samples, dtype=np.float32)

    for i, (freq, amp, decay) in enumerate(zip(partials, amplitudes, decay_rates)):
        if freq >= sr / 2:
            break  # skip partials above Nyquist

        # Each partial: sine wave × amplitude × exponential decay
        partial = np.sin(2 * np.pi * freq * t) * amp
        envelope = np.exp(-t / decay)
        signal += partial * envelope

    # === HAMMER IMPACT ===
    # Short noise burst for the hammer-string contact
    hammer_dur = 0.003 if velocity > 0.5 else 0.005  # harder = shorter contact
    hammer_samples = int(hammer_dur * sr)
    hammer = np.random.randn(hammer_samples).astype(np.float32) * velocity * 0.15

    # Filter hammer noise — higher velocity = more high-frequency content
    cutoff = 2000 + velocity * 6000
    if cutoff < sr / 2:
        b, a = butter(2, cutoff / (sr / 2), btype='low')
        hammer = lfilter(b, a, hammer).astype(np.float32)

    signal[:hammer_samples] += hammer

    # === COUPLED STRINGS ===
    # Piano has 1-3 strings per note. Multiple strings create chorus/beating.
    # Bass (1 string), mid (2), treble (3)
    if midi_note > 40:
        num_strings = 3 if midi_note > 60 else 2
        # Slightly detune additional strings (1-2 cents)
        for s in range(1, num_strings):
            detune_cents = (s * 0.8) * (1 if s % 2 else -1)  # alternating +/-
            detune_ratio = 2 ** (detune_cents / 1200)
            detuned = np.zeros(n_samples, dtype=np.float32)
            for freq, amp, decay in zip(partials, amplitudes, decay_rates):
                if freq * detune_ratio >= sr / 2:
                    break
                p = np.sin(2 * np.pi * freq * detune_ratio * t) * amp * 0.7
                env = np.exp(-t / decay)
                detuned += p * env
            signal += detuned * 0.3

    # === DAMPER RELEASE ===
    if not sustain_pedal:
        # Apply damper at note-off (exponential decay in last portion)
        release_start = int(duration * 0.85 * sr)
        release_samples = n_samples - release_start
        if release_samples > 0:
            release_env = np.exp(-np.linspace(0, 5, release_samples))
            signal[release_start:] *= release_env

    # === SOUNDBOARD RESONANCE ===
    profile = PIANO_PROFILES.get(piano_model, PIANO_PROFILES["steinway_d"])
    signal = body_resonance(signal, profile, sr)

    # Scale by velocity
    signal *= 0.3 + velocity * 0.7

    # Una corda darkening
    if una_corda:
        b, a = butter(2, 3000 / (sr / 2), btype='low')
        signal = lfilter(b, a, signal).astype(np.float32)

    return signal


# ═══════════════════════════════════════════════════════════════════
# PIANO SOUNDBOARD PROFILES
# ═══════════════════════════════════════════════════════════════════

PIANO_PROFILES = {
    "steinway_d": [
        # Steinway Model D concert grand
        # Bright, clear separation, complex overtones, singing sustain
        (90, 0.7, 6),       # Soundboard fundamental
        (200, 0.6, 8),      # Low resonance
        (450, 0.5, 10),     # Body warmth
        (900, 0.4, 12),     # Midrange
        (1800, 0.5, 8),     # Presence — Steinway clarity
        (3200, 0.4, 6),     # Brilliance — singing quality
        (5500, 0.2, 5),     # Air
    ],

    "yamaha_cfx": [
        # Yamaha CFX concert grand
        # Balanced, precise, clear, modern
        (100, 0.6, 7),      # Slightly higher fundamental
        (250, 0.5, 9),      # Low resonance
        (500, 0.5, 10),     # Body
        (1200, 0.5, 8),     # Midrange — even
        (2500, 0.4, 7),     # Presence
        (4000, 0.3, 6),     # Brilliance
        (6000, 0.2, 5),     # Air — clean top
    ],

    "bosendorfer": [
        # Bösendorfer Imperial
        # Warm bass, rich low end, singing sustain, dark warmth
        (70, 0.9, 5),       # Extended low resonance
        (160, 0.8, 7),      # Rich bass — Bösendorfer signature
        (380, 0.6, 9),      # Warmth
        (800, 0.4, 11),     # Midrange — less forward
        (1600, 0.3, 8),     # Presence — recessed
        (2800, 0.2, 6),     # Brilliance — soft
    ],

    "upright": [
        # Generic upright piano
        # More compact, less sustain, brighter attack, more "boxy"
        (120, 0.5, 8),      # Higher Helmholtz (smaller cavity)
        (280, 0.6, 10),     # Body — more prominent
        (600, 0.7, 8),      # Midrange — boxy character
        (1100, 0.5, 10),    # Upper mid
        (2200, 0.3, 7),     # Presence
        (3500, 0.2, 5),     # Top — less air
    ],

    "honky_tonk": [
        # Honky-tonk / barroom piano
        # Detuned, bright, jangly — character comes from extreme string detuning
        (110, 0.4, 9),
        (300, 0.5, 10),
        (700, 0.6, 7),      # Midrange emphasis
        (1500, 0.5, 6),
        (3000, 0.4, 5),     # Bright top
        (5000, 0.3, 4),
    ],
}

PIANO_NAMES = {
    "steinway_d": "Steinway Model D (concert grand, bright, clear)",
    "yamaha_cfx": "Yamaha CFX (concert grand, balanced, precise)",
    "bosendorfer": "Bösendorfer Imperial (warm, rich bass)",
    "upright": "Upright Piano (compact, boxy character)",
    "honky_tonk": "Honky-Tonk (detuned, jangly, barroom)",
}


# ═══════════════════════════════════════════════════════════════════
# CHORD & PATTERN RENDERING
# ═══════════════════════════════════════════════════════════════════

def synthesize_piano_chord(midi_notes, duration=2.0, sr=44100,
                          velocity=0.7, piano_model="steinway_d",
                          sustain_pedal=True, stagger_ms=15):
    """Synthesize a piano chord — notes slightly staggered for realism."""
    max_dur = duration + stagger_ms * len(midi_notes) / 1000
    n_samples = int(max_dur * sr)
    output = np.zeros(n_samples, dtype=np.float32)

    for i, note in enumerate(midi_notes):
        delay = int(i * stagger_ms / 1000 * sr)
        # Slight velocity variation per note (human imprecision)
        v = velocity * (0.9 + np.random.rand() * 0.2)
        audio = synthesize_piano_note(
            note, duration, sr, v, piano_model, sustain_pedal
        )
        end = min(delay + len(audio), n_samples)
        output[delay:end] += audio[:end - delay]

    # Normalize
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * 0.85

    return output


def list_piano_models():
    """List available piano models."""
    return [{"id": k, "name": v} for k, v in PIANO_NAMES.items()]
