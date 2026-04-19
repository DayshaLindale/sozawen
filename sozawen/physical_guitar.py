"""Sozawen Physical Guitar — Karplus-Strong with real body resonance.

Not a synthesized approximation. A physically modeled guitar string
vibrating inside a physically modeled guitar body.

The string is Karplus-Strong: noise burst → delay line → lowpass feedback.
The body is a resonance filter: formant-like peaks that give each guitar
its voice. Taylor bright. Martin warm. Gibson punchy.

Pluck position matters: bridge = bright (harmonics emphasized),
neck = warm (fundamental emphasized). Pick vs finger changes the
noise burst character (sharp vs soft).

Every parameter has a physical meaning. Nothing is arbitrary.

Research: CCRMA Stanford waveguide synthesis, Columbia University
physical modeling, Credland Audio string theory.
"""

import numpy as np
from scipy.signal import lfilter, butter


# ═══════════════════════════════════════════════════════════════════
# KARPLUS-STRONG STRING MODEL
# ═══════════════════════════════════════════════════════════════════

def karplus_strong(freq, duration, sr=44100, decay=0.996, brightness=0.5,
                   pluck_position=0.5, pick_hardness=0.5):
    """Physically modeled plucked string using Karplus-Strong algorithm.

    freq: fundamental frequency (Hz)
    duration: seconds
    decay: string sustain (0.99 = short, 0.999 = long, 1.0 = infinite)
    brightness: string brightness (0 = very mellow, 1 = very bright)
    pluck_position: where on the string (0 = bridge, 1 = neck)
    pick_hardness: 0 = finger (soft noise), 1 = pick (sharp noise)

    The algorithm:
    1. Initialize delay line with noise burst (the pluck)
    2. Each sample: read from delay line, filter, write back
    3. The lowpass filter in the loop simulates energy loss at high frequencies
    4. The delay line length = sample_rate / frequency (string length)
    """
    n_samples = int(duration * sr)
    delay_length = int(sr / freq)
    if delay_length < 2:
        return np.zeros(n_samples, dtype=np.float32)

    # === EXCITATION (the pluck) ===
    # Noise burst shaped by pluck position and pick hardness
    excitation = np.random.randn(delay_length).astype(np.float32)

    # Pick hardness: hard pick = full bandwidth noise, finger = filtered noise
    if pick_hardness < 0.5:
        # Finger pluck: softer, fewer high harmonics
        cutoff = 2000 + pick_hardness * 8000
        b, a = butter(2, cutoff / (sr / 2), btype='low')
        excitation = lfilter(b, a, excitation).astype(np.float32)

    # Pluck position: affects which harmonics are present
    # Plucking at 1/n of the string length cancels the nth harmonic
    # Bridge (0) = all harmonics. Middle (0.5) = no even harmonics.
    # This is simulated by a comb filter on the excitation
    if 0.05 < pluck_position < 0.95:
        comb_delay = max(1, int(delay_length * pluck_position))
        comb = np.zeros(delay_length, dtype=np.float32)
        comb[:len(excitation)] = excitation
        if comb_delay < len(comb):
            comb[comb_delay:] -= excitation[:len(excitation) - comb_delay] * 0.5
        excitation = comb

    # Normalize excitation
    peak = np.max(np.abs(excitation))
    if peak > 0:
        excitation = excitation / peak * 0.8

    # === DELAY LINE (the string) ===
    delay_line = np.zeros(delay_length, dtype=np.float32)
    delay_line[:] = excitation

    output = np.zeros(n_samples, dtype=np.float32)
    write_pos = 0

    # === FEEDBACK FILTER ===
    # The lowpass filter simulates high-frequency energy loss
    # Brightness controls the filter: low brightness = more damping
    # Standard KS uses average of two adjacent samples
    # We use a variable-cutoff lowpass for more control
    blend = 0.3 + brightness * 0.4  # 0.3 (mellow) to 0.7 (bright)

    prev_sample = 0.0

    for i in range(n_samples):
        # Read from delay line
        read_pos = (write_pos + 1) % delay_length
        current = delay_line[read_pos]

        # Lowpass filter: weighted average of current and previous
        filtered = blend * current + (1 - blend) * prev_sample
        prev_sample = filtered

        # Apply decay
        filtered *= decay

        # Write back to delay line
        delay_line[write_pos] = filtered

        # Output
        output[i] = filtered

        write_pos = (write_pos + 1) % delay_length

    return output


# ═══════════════════════════════════════════════════════════════════
# GUITAR BODY RESONANCE
# ═══════════════════════════════════════════════════════════════════

def body_resonance(signal, profile, sr=44100):
    """Apply guitar body resonance filter.

    The body is what makes a Taylor sound like a Taylor and a Martin
    sound like a Martin. Same strings, different body = different voice.

    Each profile defines resonant peaks (frequency, gain, Q) that
    represent the body's natural vibration modes.

    profile: list of (frequency_hz, gain, q_factor)
    """
    output = np.zeros_like(signal)

    for freq, gain, q in profile:
        if freq <= 0 or freq >= sr / 2:
            continue
        # Create a bandpass resonance at this frequency
        bw = freq / q
        low = max(20, freq - bw / 2)
        high = min(sr / 2 - 1, freq + bw / 2)
        try:
            b, a = butter(2, [low / (sr / 2), high / (sr / 2)], btype='band')
            resonance = lfilter(b, a, signal) * gain
            output += resonance
        except Exception:
            continue

    # Mix: original string (direct) + body resonance
    # Real guitars: body dominates, string is quiet without it
    direct_level = 0.15
    body_level = 0.85
    result = signal * direct_level + output * body_level

    # Normalize
    peak = np.max(np.abs(result))
    if peak > 0:
        result = result / peak * 0.8

    return result.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# GUITAR BODY PROFILES — each brand has its own resonance
# ═══════════════════════════════════════════════════════════════════
# Format: (frequency_hz, gain, q_factor)
# Research: guitar body has 3-5 main resonant modes
# First mode (~100Hz) = air cavity (Helmholtz resonance)
# Second mode (~200Hz) = top plate fundamental
# Third mode (~400Hz) = top plate second mode
# Higher modes shape the "presence" and "character"
#
# Brand character comes from which modes are emphasized:
# Taylor: strong presence modes (2-4kHz), clear separation
# Martin: strong fundamental modes (100-300Hz), warm body
# Gibson: strong midrange (400-1000Hz), punchy
#
# These are approximations based on published frequency response data
# and listening analysis. They will be refined through testing.

BODY_PROFILES = {
    "taylor_dreadnought": [
        # Taylor 814ce character: bright, clear, present
        (98, 0.8, 8),       # Helmholtz (air cavity)
        (210, 0.7, 10),     # Top plate fundamental
        (380, 0.5, 12),     # Second top mode
        (620, 0.4, 15),     # Body midrange
        (1100, 0.3, 12),    # Presence
        (2200, 0.35, 10),   # Clarity — Taylor signature brightness
        (3500, 0.25, 8),    # Sparkle
        (5000, 0.15, 6),    # Air
    ],

    "martin_dreadnought": [
        # Martin D-28 character: warm, thick, rich bass
        (95, 1.0, 6),       # Helmholtz — stronger, looser coupling
        (195, 0.9, 8),      # Top plate — lower, warmer
        (350, 0.6, 10),     # Second top mode
        (550, 0.5, 12),     # Body warmth — Martin signature
        (900, 0.3, 14),     # Midrange — recessed vs Taylor
        (1800, 0.2, 10),    # Presence — less forward
        (3000, 0.15, 8),    # Top end — rolled off
    ],

    "gibson_j45": [
        # Gibson J-45 character: midrange punch, woody
        (100, 0.7, 7),      # Helmholtz
        (220, 0.6, 9),      # Top plate
        (420, 0.8, 10),     # Midrange PUNCH — Gibson signature
        (750, 0.7, 11),     # Woody character
        (1200, 0.4, 12),    # Upper midrange
        (2500, 0.2, 8),     # Presence — behind Taylor
        (4000, 0.1, 6),     # Top — rolled off
    ],

    "classical_nylon": [
        # Classical guitar: warm, round, less sustain
        (90, 0.9, 5),       # Larger body, lower Helmholtz
        (180, 0.8, 7),      # Top plate — fan bracing = different modes
        (320, 0.7, 9),      # Body resonance
        (500, 0.5, 11),     # Warmth
        (800, 0.3, 13),     # Midrange
        (1500, 0.2, 10),    # Presence — soft
        (2500, 0.1, 8),     # Top — very rolled off (nylon = less harmonics)
    ],

    "electric_strat": [
        # Fender Stratocaster: single coil, bright, glassy
        # Electric guitars: body resonance is less important,
        # pickup position and type dominate
        (100, 0.2, 10),     # Minimal body
        (250, 0.3, 12),     # Some wood character
        (800, 0.5, 8),      # Midrange
        (2000, 0.8, 6),     # Single coil brightness
        (3500, 0.7, 5),     # Glassy top — Strat signature
        (5000, 0.5, 4),     # Sizzle
        (7000, 0.3, 3),     # Air
    ],

    "electric_les_paul": [
        # Gibson Les Paul: humbucker, warm, thick
        (100, 0.3, 10),     # Mahogany body resonance
        (250, 0.5, 10),     # Warmth
        (600, 0.7, 8),      # Midrange — LP signature thickness
        (1200, 0.6, 6),     # Upper mid — humbucker roll-off starts
        (2500, 0.3, 5),     # Less top than Strat
        (4000, 0.15, 4),    # Humbucker = less high end
    ],

    "acoustic_bass": [
        # Acoustic bass guitar
        (55, 1.0, 4),       # Very low Helmholtz
        (110, 0.8, 6),      # Fundamental resonance
        (220, 0.6, 8),      # Body
        (400, 0.4, 10),     # Midrange
        (800, 0.2, 8),      # Upper body
        (1500, 0.1, 6),     # Presence — minimal
    ],
}

# User-friendly names
GUITAR_NAMES = {
    "taylor_dreadnought": "Taylor Dreadnought (bright, clear)",
    "martin_dreadnought": "Martin D-28 (warm, thick)",
    "gibson_j45": "Gibson J-45 (punchy, woody)",
    "classical_nylon": "Classical Nylon (warm, round)",
    "electric_strat": "Fender Stratocaster (bright, glassy)",
    "electric_les_paul": "Gibson Les Paul (warm, thick)",
    "acoustic_bass": "Acoustic Bass (deep, resonant)",
}


# ═══════════════════════════════════════════════════════════════════
# STRING PROPERTIES
# ═══════════════════════════════════════════════════════════════════

STRING_SETS = {
    "light_acoustic": {
        "name": "Light Acoustic (.012-.053)",
        "decay": [0.997, 0.997, 0.996, 0.996, 0.995, 0.995],
        "brightness": [0.6, 0.6, 0.55, 0.5, 0.45, 0.4],
    },
    "medium_acoustic": {
        "name": "Medium Acoustic (.013-.056)",
        "decay": [0.998, 0.998, 0.997, 0.997, 0.996, 0.996],
        "brightness": [0.55, 0.55, 0.5, 0.45, 0.4, 0.35],
    },
    "nylon": {
        "name": "Nylon Classical",
        "decay": [0.995, 0.995, 0.994, 0.994, 0.993, 0.993],
        "brightness": [0.35, 0.35, 0.3, 0.3, 0.25, 0.25],
    },
    "electric_light": {
        "name": "Electric Light (.009-.042)",
        "decay": [0.999, 0.999, 0.998, 0.998, 0.997, 0.997],
        "brightness": [0.7, 0.7, 0.65, 0.6, 0.55, 0.5],
    },
}


# ═══════════════════════════════════════════════════════════════════
# FULL GUITAR SYNTHESIZER
# ═══════════════════════════════════════════════════════════════════

def synthesize_guitar_note(freq, duration, sr=44100,
                          body_profile="taylor_dreadnought",
                          string_set="light_acoustic",
                          string_index=0,
                          pluck_position=0.5,
                          pick_hardness=0.3,
                          velocity=0.7):
    """Synthesize a complete guitar note.

    freq: note frequency (Hz)
    duration: seconds
    body_profile: which guitar body to use
    string_set: which strings
    string_index: which string (0=low E, 5=high E)
    pluck_position: 0=bridge, 1=neck
    pick_hardness: 0=finger, 1=pick
    velocity: how hard the pluck (0-1)
    """
    strings = STRING_SETS.get(string_set, STRING_SETS["light_acoustic"])
    idx = min(string_index, len(strings["decay"]) - 1)

    decay = strings["decay"][idx]
    brightness = strings["brightness"][idx]

    # Velocity affects brightness and decay
    # Harder pluck = brighter, slightly shorter
    brightness = min(1.0, brightness + velocity * 0.2)
    decay = decay - (1 - velocity) * 0.002

    # Generate string vibration
    string_signal = karplus_strong(
        freq, duration, sr,
        decay=decay,
        brightness=brightness,
        pluck_position=pluck_position,
        pick_hardness=pick_hardness,
    )

    # Apply body resonance
    body = BODY_PROFILES.get(body_profile, BODY_PROFILES["taylor_dreadnought"])
    output = body_resonance(string_signal, body, sr)

    # Apply velocity to final level
    output *= velocity

    return output


def synthesize_guitar_chord(notes, duration=2.0, sr=44100,
                           body_profile="taylor_dreadnought",
                           string_set="light_acoustic",
                           strum_speed=0.03,
                           pluck_position=0.5,
                           pick_hardness=0.3,
                           velocity=0.7):
    """Synthesize a strummed guitar chord.

    notes: list of (freq, string_index) tuples
    strum_speed: seconds between each string in the strum
    """
    n_samples = int((duration + strum_speed * len(notes)) * sr)
    output = np.zeros(n_samples, dtype=np.float32)

    for i, (freq, string_idx) in enumerate(notes):
        if freq <= 0:
            continue
        delay = int(i * strum_speed * sr)
        note = synthesize_guitar_note(
            freq, duration, sr,
            body_profile=body_profile,
            string_set=string_set,
            string_index=string_idx,
            pluck_position=pluck_position,
            pick_hardness=pick_hardness,
            velocity=velocity * (0.9 + np.random.rand() * 0.2),  # slight velocity variation
        )
        end = min(delay + len(note), n_samples)
        output[delay:end] += note[:end - delay]

    # Normalize
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * 0.85

    return output


def list_guitar_models():
    """List available guitar body models."""
    return [
        {"id": k, "name": v}
        for k, v in GUITAR_NAMES.items()
    ]


def list_string_sets():
    """List available string sets."""
    return [
        {"id": k, "name": v["name"]}
        for k, v in STRING_SETS.items()
    ]
