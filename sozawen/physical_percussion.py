"""Sozawen Physical Percussion — every struck object sings its own modes.

Modal synthesis: each instrument has specific resonant frequencies
determined by its physical dimensions, material, and shape.
Unlike harmonic instruments, these frequencies are NOT integer
multiples of a fundamental. That inharmonicity is what makes
a bell sound like a bell and a drum sound like a drum.

Timpani: membrane modes (1,1), (2,1), (3,1) at ~1:1.5:2
Xylophone: bar modes at 1:2.76:5.40 (very inharmonic)
Marimba: undercut bars tuned to 1:4:9 (arch-cut makes them harmonic)
Glockenspiel: steel bars, only fundamental sustains = clear ring
Vibraphone: aluminum bars with motor-driven vibrato
Tubular bells: tube modes, perceived pitch is NOT the fundamental
Triangle: dense inharmonic modes = shimmer

Research: CCRMA Stanford percussion, Euphonics.org bar/membrane physics,
Sound On Sound practical percussion synthesis.
"""

import numpy as np
from scipy.signal import lfilter, butter


# ═══════════════════════════════════════════════════════════════════
# MODAL SYNTHESIS ENGINE
# ═══════════════════════════════════════════════════════════════════

def modal_synthesis(fundamental, duration, sr, modes, mallet_hardness=0.5,
                   strike_position=0.5, velocity=0.7, material_damping=1.0):
    """Core modal synthesis: generate sound from resonant modes.

    modes: list of (freq_ratio, amplitude, decay_time_seconds)
    mallet_hardness: 0 (soft) to 1 (hard) — harder = more high modes
    strike_position: 0 (center) to 1 (edge) — affects mode excitation
    material_damping: multiplier on decay times (metal=1.5, wood=0.7, skin=0.5)
    """
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    signal = np.zeros(n_samples, dtype=np.float32)

    for freq_ratio, base_amp, base_decay in modes:
        freq = fundamental * freq_ratio
        if freq >= sr / 2:
            continue

        # Mallet hardness filtering:
        # Soft mallet = only low modes excited (lowpass on excitation)
        # Hard mallet = all modes excited equally
        mode_number = freq_ratio  # proxy for mode order
        hardness_filter = 1.0 - (1.0 - mallet_hardness) * min(1.0, mode_number / 10)
        if hardness_filter < 0.05:
            continue

        # Strike position affects which modes are excited
        # Center strike: symmetric modes strong, asymmetric weak
        # Edge strike: all modes excited
        if strike_position < 0.3:  # center
            # Even modes are suppressed at center
            if int(freq_ratio + 0.5) % 2 == 0:
                base_amp *= 0.3
        elif strike_position > 0.7:  # edge
            base_amp *= 0.9  # edge excites everything

        amp = base_amp * hardness_filter * velocity
        decay = base_decay * material_damping

        # Generate partial with exponential decay
        partial = np.sin(2 * np.pi * freq * t) * amp * np.exp(-t / max(decay, 0.01))
        signal += partial

    # Excitation transient — mallet impact noise
    transient_dur = 0.002 + (1 - mallet_hardness) * 0.005
    transient_samples = int(transient_dur * sr)
    transient = np.random.randn(transient_samples).astype(np.float32)
    transient *= velocity * mallet_hardness * 0.3
    # Hard mallet = brighter click
    cutoff = 3000 + mallet_hardness * 8000
    if cutoff < sr / 2:
        b, a = butter(2, cutoff / (sr / 2), btype='low')
        transient = lfilter(b, a, transient).astype(np.float32)
    transient *= np.exp(-np.linspace(0, 10, transient_samples))

    signal[:transient_samples] += transient

    # Normalize
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8 * velocity

    return signal


# ═══════════════════════════════════════════════════════════════════
# INSTRUMENT MODE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════
# Format: (frequency_ratio, amplitude, decay_time_seconds)
# Ratios are relative to the perceived fundamental pitch.
# Research sources cited per instrument.

# Timpani: circular membrane loaded by air cavity
# Modes: (1,1)=1.00, (2,1)=1.50, (3,1)=1.99, (4,1)=2.44, (1,2)=2.89
# Source: CCRMA Stanford, Euphonics.org
TIMPANI_MODES = [
    (1.00, 1.0, 1.5),     # (1,1) principal note
    (1.50, 0.6, 1.2),     # (2,1) perfect fifth above
    (1.99, 0.4, 1.0),     # (3,1) near-octave
    (2.44, 0.2, 0.8),     # (4,1)
    (2.89, 0.1, 0.6),     # (1,2)
    (0.63, 0.15, 0.4),    # (0,1) sub-fundamental (not heard as pitch)
]

# Marimba: undercut wooden bars tuned to near-harmonic ratios
# 2nd partial tuned to 4:1 (two octaves), 3rd at ~9.2:1
# Source: Euphonics.org marimba bar physics
MARIMBA_MODES = [
    (1.00, 1.0, 0.8),     # Fundamental
    (4.00, 0.3, 0.5),     # 2nd partial (tuned to 2 octaves)
    (9.20, 0.1, 0.3),     # 3rd partial
    (16.0, 0.03, 0.15),   # 4th partial (faint)
]

# Xylophone: wooden bars, less undercut than marimba
# 2nd partial at 3:1 (twelfth), higher partials very inharmonic
# Source: Basic physics of xylophone and marimba bars (ResearchGate)
XYLOPHONE_MODES = [
    (1.00, 1.0, 0.5),     # Fundamental
    (3.00, 0.4, 0.3),     # 2nd partial (twelfth)
    (5.40, 0.15, 0.2),    # 3rd partial
    (8.93, 0.05, 0.1),    # 4th partial
]

# Vibraphone: aluminum bars with resonator tubes
# Similar ratios to xylophone but metal = longer sustain
# Motor-driven fans create vibrato (amplitude modulation)
VIBRAPHONE_MODES = [
    (1.00, 1.0, 3.0),     # Long sustain (metal)
    (4.00, 0.3, 2.0),     # Tuned 2nd partial
    (9.20, 0.1, 1.0),     # 3rd partial
]

# Glockenspiel: steel bars, very bright, long ring
# Only fundamental sustains significantly — clear pitch
# Source: Euphonics.org
GLOCKENSPIEL_MODES = [
    (1.00, 1.0, 5.0),     # Very long fundamental ring
    (2.76, 0.2, 0.5),     # 2nd partial — decays fast
    (5.40, 0.05, 0.2),    # 3rd partial — barely audible
]

# Tubular bells: struck metal tubes
# Perceived pitch is NOT the lowest mode — it's a learned association
# Modes at 1:2.76:5.40:8.93 (same as free bar)
TUBULAR_BELL_MODES = [
    (0.93, 0.3, 2.0),     # Sub-mode
    (1.00, 1.0, 4.0),     # "Fundamental" (perceived pitch)
    (2.76, 0.6, 3.0),     # Strong 2nd mode
    (5.40, 0.3, 2.0),     # 3rd mode
    (8.93, 0.15, 1.0),    # 4th mode
    (13.3, 0.05, 0.5),    # 5th mode
]

# Triangle: bent metal rod, dense inharmonic modes
# The shimmer comes from many closely-spaced modes
TRIANGLE_MODES = [
    (1.00, 1.0, 6.0),
    (2.83, 0.7, 5.0),
    (5.66, 0.5, 4.0),
    (9.43, 0.4, 3.0),
    (14.1, 0.3, 2.5),
    (19.8, 0.2, 2.0),
    (26.5, 0.15, 1.5),
    (34.2, 0.1, 1.0),
]

# Concert snare drum: tight membrane + snare wires
CONCERT_SNARE_MODES = [
    (1.00, 1.0, 0.3),     # Membrane fundamental
    (1.59, 0.5, 0.2),
    (2.14, 0.3, 0.15),
    (2.65, 0.2, 0.1),
]

# Concert bass drum: large membrane, very deep
CONCERT_BASS_DRUM_MODES = [
    (1.00, 1.0, 1.5),     # Deep fundamental
    (1.50, 0.4, 1.0),
    (1.99, 0.2, 0.7),
    (0.63, 0.3, 0.5),     # Sub-mode — feel more than hear
]

# Tambourine: membrane + jingles
TAMBOURINE_JINGLE_MODES = [
    (1.00, 0.3, 0.1),     # Membrane (if struck)
    (8.0, 0.8, 0.8),      # Jingle fundamental
    (12.5, 0.6, 0.6),     # Jingle harmonics
    (17.0, 0.4, 0.5),
    (22.0, 0.3, 0.4),
    (28.0, 0.2, 0.3),
]


# ═══════════════════════════════════════════════════════════════════
# INSTRUMENT SYNTHESIZERS
# ═══════════════════════════════════════════════════════════════════

def synthesize_timpani(midi_note, duration, sr=44100, velocity=0.7,
                      mallet_hardness=0.4, damping=0.0):
    """Synthesize a timpani note.

    Timpani are tuned — midi_note maps to the fundamental.
    mallet_hardness: soft felt (0) to hard (1)
    damping: hand-damping (0=open, 1=muted)
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    mat_damp = 0.5 * (1 - damping * 0.7)  # damping reduces sustain
    return modal_synthesis(freq, duration, sr, TIMPANI_MODES,
                          mallet_hardness, 0.25, velocity, mat_damp)


def synthesize_marimba(midi_note, duration, sr=44100, velocity=0.7,
                      mallet_hardness=0.3):
    """Synthesize a marimba note. Rosewood bars, soft mallets."""
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    return modal_synthesis(freq, duration, sr, MARIMBA_MODES,
                          mallet_hardness, 0.4, velocity, 0.7)  # wood=shorter decay


def synthesize_xylophone(midi_note, duration, sr=44100, velocity=0.7,
                        mallet_hardness=0.7):
    """Synthesize a xylophone note. Harder mallets than marimba."""
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    return modal_synthesis(freq, duration, sr, XYLOPHONE_MODES,
                          mallet_hardness, 0.4, velocity, 0.8)


def synthesize_vibraphone(midi_note, duration, sr=44100, velocity=0.7,
                         mallet_hardness=0.4, motor_speed=5.0, motor_on=True,
                         pedal_down=True):
    """Synthesize a vibraphone note.

    motor_on: rotating fans create vibrato
    motor_speed: Hz (typically 3-7)
    pedal_down: sustain pedal (True=notes ring, False=damped)
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    mat_damp = 1.5 if pedal_down else 0.5  # metal + pedal = long sustain
    signal = modal_synthesis(freq, duration, sr, VIBRAPHONE_MODES,
                            mallet_hardness, 0.4, velocity, mat_damp)

    # Motor vibrato (amplitude modulation from rotating fans)
    if motor_on and motor_speed > 0:
        t = np.linspace(0, duration, len(signal), dtype=np.float32)
        vibrato = 1.0 - 0.3 * (1 + np.sin(2 * np.pi * motor_speed * t)) * 0.5
        signal *= vibrato

    return signal


def synthesize_glockenspiel(midi_note, duration, sr=44100, velocity=0.7,
                           mallet_hardness=0.8):
    """Synthesize a glockenspiel note. Clear, ringing, very bright."""
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    return modal_synthesis(freq, duration, sr, GLOCKENSPIEL_MODES,
                          mallet_hardness, 0.5, velocity, 1.5)  # metal=long


def synthesize_tubular_bells(midi_note, duration, sr=44100, velocity=0.7):
    """Synthesize tubular bells. Church bell character."""
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    return modal_synthesis(freq, duration, sr, TUBULAR_BELL_MODES,
                          0.6, 0.3, velocity, 1.3)


def synthesize_triangle(duration, sr=44100, velocity=0.7, damped=False):
    """Synthesize a triangle hit. No pitch — it's inharmonic shimmer.

    damped: True = finger-damped (short ring)
    """
    freq = 3000  # triangle is unpitched, centered around 3kHz
    mat_damp = 0.3 if damped else 1.5
    return modal_synthesis(freq, duration, sr, TRIANGLE_MODES,
                          0.9, 0.5, velocity, mat_damp)


def synthesize_tambourine(duration, sr=44100, velocity=0.7, shake=False):
    """Synthesize a tambourine hit or shake.

    shake: if True, creates a roll/shake pattern
    """
    freq = 5000  # jingle center frequency
    signal = modal_synthesis(freq, duration, sr, TAMBOURINE_JINGLE_MODES,
                            0.8, 0.5, velocity, 0.5)

    if shake:
        # Create rapid repeating pattern
        n = len(signal)
        shake_rate = 12  # shakes per second
        t = np.linspace(0, duration, n, dtype=np.float32)
        shake_env = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * shake_rate * t))
        signal *= shake_env

    return signal


def synthesize_concert_snare(midi_note=60, duration=0.5, sr=44100, velocity=0.7,
                            snare_tension=0.7):
    """Synthesize a concert snare drum hit.

    Tighter head and brighter wires than a kit snare.
    """
    freq = 200 + (midi_note - 60) * 5  # slight pitch variation
    signal = modal_synthesis(freq, duration, sr, CONCERT_SNARE_MODES,
                            0.7, 0.25, velocity, 0.5)

    # Add snare wire buzz (filtered noise)
    n = len(signal)
    t = np.linspace(0, duration, n, dtype=np.float32)
    wire_noise = np.random.randn(n).astype(np.float32) * snare_tension * 0.3
    wire_env = np.exp(-t * 8)
    wire_noise *= wire_env
    if sr > 4000:
        b, a = butter(2, [2000 / (sr / 2), min(8000, sr / 2 - 1) / (sr / 2)], btype='band')
        wire_noise = lfilter(b, a, wire_noise).astype(np.float32)

    signal[:n] += wire_noise

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8 * velocity

    return signal


def synthesize_concert_bass_drum(midi_note=36, duration=1.0, sr=44100, velocity=0.7):
    """Synthesize a concert bass drum. Very deep, long sustain."""
    freq = 40 + (midi_note - 36) * 2  # deep fundamental
    return modal_synthesis(freq, duration, sr, CONCERT_BASS_DRUM_MODES,
                          0.3, 0.3, velocity, 0.5)


# ═══════════════════════════════════════════════════════════════════
# UNIFIED INTERFACE
# ═══════════════════════════════════════════════════════════════════

PERCUSSION_INSTRUMENTS = {
    "timpani": {"name": "Timpani", "pitched": True, "func": synthesize_timpani},
    "marimba": {"name": "Marimba", "pitched": True, "func": synthesize_marimba},
    "xylophone": {"name": "Xylophone", "pitched": True, "func": synthesize_xylophone},
    "vibraphone": {"name": "Vibraphone", "pitched": True, "func": synthesize_vibraphone},
    "glockenspiel": {"name": "Glockenspiel", "pitched": True, "func": synthesize_glockenspiel},
    "tubular_bells": {"name": "Tubular Bells", "pitched": True, "func": synthesize_tubular_bells},
    "triangle": {"name": "Triangle", "pitched": False, "func": synthesize_triangle},
    "tambourine": {"name": "Tambourine", "pitched": False, "func": synthesize_tambourine},
    "concert_snare": {"name": "Concert Snare", "pitched": False, "func": synthesize_concert_snare},
    "concert_bass": {"name": "Concert Bass Drum", "pitched": False, "func": synthesize_concert_bass_drum},
}


def synthesize_percussion_note(instrument, midi_note=60, duration=1.0,
                              sr=44100, velocity=0.7, **kwargs):
    """Unified percussion synthesis interface."""
    info = PERCUSSION_INSTRUMENTS.get(instrument)
    if not info:
        return np.zeros(int(duration * sr), dtype=np.float32)

    func = info["func"]
    if info["pitched"]:
        return func(midi_note, duration, sr, velocity, **kwargs)
    else:
        return func(duration=duration, sr=sr, velocity=velocity, **kwargs)


def list_percussion_instruments():
    """List all available orchestral percussion instruments."""
    return [
        {"id": k, "name": v["name"], "pitched": v["pitched"]}
        for k, v in PERCUSSION_INSTRUMENTS.items()
    ]
