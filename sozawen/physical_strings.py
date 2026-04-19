"""Sozawen Physical Strings — the bow sings through friction.

Bowed string instruments produce sound through stick-slip friction
between bow hair and string. The bow grips the string (stick phase),
pulls it until tension overcomes friction, and the string snaps back
(slip phase). This creates Helmholtz motion — a sawtooth-like
waveform with a traveling "corner" that bounces between bridge and nut.

The beauty of bowed strings is in the control:
- Bow speed → volume (faster = louder)
- Bow pressure → tone quality (light = ethereal, heavy = gritty)
- Bow position → harmonics (near bridge = glassy, near fingerboard = soft)
- Vibrato → expressiveness (finger oscillation on string)

Each instrument has its own body resonance. A Stradivarius violin
has a "singer's formant" around 2.5-3.5kHz that lets it project
over an orchestra. A cello has warm resonances around 300-800Hz
that give it its singing quality.

Research: INRIA Hal friction models, CCRMA Stanford bowed strings,
OSTI.gov Helmholtz vibrations, Peder Larson virtual cello (CCRMA).
"""

import numpy as np
from scipy.signal import lfilter, butter
from sozawen.physical_guitar import body_resonance, karplus_strong


# ═══════════════════════════════════════════════════════════════════
# BOWED STRING SYNTHESIS
# ═══════════════════════════════════════════════════════════════════

def bowed_string(freq, duration, sr=44100, bow_speed=0.5, bow_pressure=0.5,
                bow_position=0.12, vibrato_rate=5.5, vibrato_depth=0.003):
    """Synthesize a bowed string using simplified friction model.

    The bow-string interaction creates Helmholtz motion:
    - Stick phase: bow drags string (linear ramp up in waveform)
    - Slip phase: string snaps back (fast ramp down)
    - Result: sawtooth-like wave with rounded corners

    bow_speed: 0-1 (controls amplitude / dynamics)
    bow_pressure: 0-1 (controls tone — light=pure, heavy=scratchy)
    bow_position: 0-1 (0=bridge/sul ponticello, 1=fingerboard/sul tasto)
                  Normal playing is ~0.08-0.15 (close to bridge)
    vibrato_rate: Hz (typically 5-7 for expressive playing)
    vibrato_depth: fraction of frequency (0.003 = ~5 cents)
    """
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # === VIBRATO ===
    # Frequency modulation from finger oscillation
    if vibrato_depth > 0 and vibrato_rate > 0:
        # Vibrato develops gradually (doesn't start immediately)
        vibrato_onset = np.minimum(t / 0.3, 1.0)  # ramps up over 300ms
        freq_mod = freq * (1 + vibrato_depth * vibrato_onset *
                          np.sin(2 * np.pi * vibrato_rate * t))
    else:
        freq_mod = np.full(n_samples, freq, dtype=np.float32)

    # === HELMHOLTZ MOTION ===
    # Build sawtooth-like wave with bow-position-dependent harmonic content
    signal = np.zeros(n_samples, dtype=np.float32)

    # Number of harmonics depends on bow position and pressure
    # Near bridge: many harmonics (bright, glassy)
    # Near fingerboard: few harmonics (soft, flute-like)
    max_harmonics = int(3 + (1 - bow_position) * 25)  # 3-28 harmonics

    # Bow pressure affects harmonic balance
    # Light pressure: clean harmonics, pure tone
    # Heavy pressure: subharmonics, noise, scratchy
    brightness = (1 - bow_position) * (0.5 + bow_pressure * 0.5)

    for n in range(1, max_harmonics + 1):
        harmonic_freq = freq * n

        if harmonic_freq >= sr / 2:
            break

        # Sawtooth harmonic amplitudes: 1/n
        # Modified by bow position: harmonics at multiples of 1/bow_position are reduced
        amp = 1.0 / n

        # Bow position filtering: plucking at 1/n cancels nth harmonic
        # For bowing, this creates notches in the spectrum
        if bow_position > 0.01:
            notch = abs(np.sin(np.pi * n * bow_position))
            amp *= max(0.1, notch)

        # Pressure effect: more pressure = more even-odd balance shift
        if bow_pressure > 0.7 and n % 2 == 0:
            amp *= 1 + (bow_pressure - 0.7) * 0.5

        # Frequency-dependent decay: higher harmonics decay faster
        decay_rate = 0.5 + n * 0.2
        env = np.exp(-t * decay_rate * (1 - bow_speed * 0.8))

        # Use vibrato-modulated frequency
        phase = np.cumsum(freq_mod * n / sr) * 2 * np.pi
        partial = np.sin(phase) * amp * env

        signal += partial

    # === BOW NOISE ===
    # Real bowing has noise from rosin and hair
    # More noise at high pressure and low speed
    noise_level = bow_pressure * 0.1 * (1 - bow_speed * 0.5)
    if noise_level > 0.01:
        bow_noise = np.random.randn(n_samples).astype(np.float32) * noise_level
        # Filter noise to string's frequency range
        b, a = butter(2, min(freq * 8, sr / 2 - 1) / (sr / 2), btype='low')
        bow_noise = lfilter(b, a, bow_noise).astype(np.float32)
        signal += bow_noise

    # === AMPLITUDE ENVELOPE ===
    # Bowed strings have a characteristic slow attack (bow grabs string)
    attack_time = 0.05 + (1 - bow_pressure) * 0.1  # lighter pressure = slower attack
    attack_samples = int(attack_time * sr)
    if attack_samples > 0 and attack_samples < n_samples:
        signal[:attack_samples] *= np.linspace(0, 1, attack_samples) ** 0.7

    # Amplitude from bow speed
    signal *= bow_speed

    # Release
    release_samples = int(0.05 * sr)
    if release_samples > 0 and release_samples < n_samples:
        signal[-release_samples:] *= np.linspace(1, 0, release_samples)

    return signal


# ═══════════════════════════════════════════════════════════════════
# BODY RESONANCE PROFILES
# ═══════════════════════════════════════════════════════════════════

STRING_BODIES = {
    "violin": [
        # Violin body resonances
        # A0 (air) ~280Hz, B1- ~460Hz, B1+ ~550Hz
        # Singer's formant ~2.5-3.5kHz for projection
        (280, 0.9, 6),       # A0 air resonance
        (460, 0.7, 8),       # B1- body mode
        (550, 0.8, 7),       # B1+ body mode
        (900, 0.4, 10),      # Body midrange
        (1500, 0.3, 8),      # Upper body
        (2800, 0.5, 6),      # Singer's formant — projection
        (3500, 0.4, 5),      # Brilliance
        (5000, 0.2, 4),      # Air/presence
    ],

    "stradivarius": [
        # Stradivarius: stronger singer's formant, more complex overtones
        (275, 1.0, 5),       # Slightly lower A0
        (450, 0.8, 7),       # Strong B1-
        (540, 0.9, 6),       # Strong B1+
        (850, 0.5, 9),       # Rich midrange
        (1400, 0.4, 7),      # Body
        (2500, 0.7, 5),      # STRONG singer's formant — Strad signature
        (3200, 0.6, 5),      # Extended brilliance
        (4500, 0.3, 4),      # Complex top
    ],

    "viola": [
        # Viola: larger than violin, lower resonances, nasal quality
        (220, 0.8, 5),       # A0 — lower
        (350, 0.7, 7),       # B1-
        (440, 0.6, 8),       # B1+
        (800, 0.7, 6),       # Nasal midrange — viola signature
        (1200, 0.5, 8),      # Upper body
        (2200, 0.3, 6),      # Presence — less than violin
        (3000, 0.2, 5),      # Top — darker
    ],

    "cello": [
        # Cello: warm, singing, rich 300-800Hz
        (115, 0.9, 4),       # A0 — deep
        (175, 0.8, 6),       # Body fundamental
        (350, 0.7, 7),       # Warm midrange
        (550, 0.6, 8),       # Body
        (800, 0.5, 7),       # Singing quality
        (1500, 0.3, 6),      # Presence
        (2500, 0.2, 5),      # Brilliance — gentle
    ],

    "contrabass": [
        # Contrabass: deep, rumbling, fundamental-dominant
        (65, 1.0, 3),        # A0 — very deep
        (110, 0.8, 5),       # Body
        (200, 0.6, 7),       # Low mid
        (400, 0.4, 8),       # Mid
        (700, 0.2, 7),       # Upper body
        (1200, 0.1, 6),      # Presence — minimal
    ],
}

STRING_NAMES = {
    "violin": "Violin (bright, singing)",
    "stradivarius": "Stradivarius Violin (extraordinary projection)",
    "viola": "Viola (warm, nasal)",
    "cello": "Cello (rich, warm, singing)",
    "contrabass": "Contrabass (deep, powerful)",
}


# ═══════════════════════════════════════════════════════════════════
# ARTICULATIONS
# ═══════════════════════════════════════════════════════════════════

def synthesize_string_note(midi_note, duration, sr=44100, velocity=0.7,
                          instrument="violin", articulation="sustain",
                          bow_position=0.12, vibrato_rate=5.5,
                          vibrato_depth=0.003):
    """Synthesize a bowed string note with articulation.

    articulation:
    - "sustain" (arco): normal sustained bowing
    - "detache": separate bow strokes, slight gap between notes
    - "staccato": short, accented bow strokes
    - "tremolo": rapid bow alternation
    - "pizzicato": plucked (no bow)
    - "sul_ponticello": bow near bridge (glassy, harmonic-rich)
    - "sul_tasto": bow near fingerboard (soft, muted)
    - "col_legno": wood of bow (percussive tap)
    - "harmonics": natural harmonics (touch at node)
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)

    # Map velocity to bow parameters
    bow_speed = 0.2 + velocity * 0.6
    bow_pressure = 0.3 + velocity * 0.4

    # === ARTICULATION MODIFIERS ===
    if articulation == "pizzicato":
        # Use Karplus-Strong instead of bow
        body = STRING_BODIES.get(instrument, STRING_BODIES["violin"])
        signal = karplus_strong(freq, duration, sr,
                               decay=0.995, brightness=0.4,
                               pluck_position=0.3, pick_hardness=0.3)
        return body_resonance(signal, body, sr)

    elif articulation == "staccato":
        duration = min(duration, 0.15)
        bow_pressure = min(1.0, bow_pressure + 0.2)
        vibrato_depth = 0  # no vibrato on short notes

    elif articulation == "detache":
        # Slight gap at end
        bow_speed *= 0.9

    elif articulation == "tremolo":
        # Rapid bow changes — create amplitude modulation
        pass  # handled below

    elif articulation == "sul_ponticello":
        bow_position = 0.03  # very close to bridge
        vibrato_depth *= 0.5

    elif articulation == "sul_tasto":
        bow_position = 0.3   # near fingerboard
        bow_pressure *= 0.6

    elif articulation == "col_legno":
        # Wood of bow tapping — percussive, very short
        duration = min(duration, 0.1)
        n = int(duration * sr)
        tap = np.random.randn(n).astype(np.float32) * velocity * 0.3
        tap *= np.exp(-np.linspace(0, 20, n))
        body = STRING_BODIES.get(instrument, STRING_BODIES["violin"])
        return body_resonance(tap, body, sr)

    elif articulation == "harmonics":
        # Natural harmonics — touch at node, string vibrates at harmonic
        # Sounds an octave or more above the fingered note
        freq *= 2  # first natural harmonic = octave
        bow_pressure = 0.15  # very light
        vibrato_depth = 0

    # Generate bowed signal
    signal = bowed_string(freq, duration, sr,
                         bow_speed=bow_speed,
                         bow_pressure=bow_pressure,
                         bow_position=bow_position,
                         vibrato_rate=vibrato_rate,
                         vibrato_depth=vibrato_depth)

    # Tremolo: rapid amplitude modulation
    if articulation == "tremolo":
        t = np.linspace(0, duration, len(signal), dtype=np.float32)
        trem_rate = 12  # bow changes per second
        trem = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * trem_rate * t))
        signal *= trem

    # Apply body resonance
    body = STRING_BODIES.get(instrument, STRING_BODIES["violin"])
    signal = body_resonance(signal, body, sr)

    return signal


def list_string_instruments():
    """List available bowed string instruments."""
    return [{"id": k, "name": v} for k, v in STRING_NAMES.items()]


def list_string_articulations():
    """List available articulations."""
    return [
        {"id": "sustain", "name": "Sustain (arco)", "description": "Normal sustained bowing"},
        {"id": "detache", "name": "Détaché", "description": "Separate bow strokes"},
        {"id": "staccato", "name": "Staccato", "description": "Short, accented strokes"},
        {"id": "tremolo", "name": "Tremolo", "description": "Rapid bow alternation"},
        {"id": "pizzicato", "name": "Pizzicato", "description": "Plucked"},
        {"id": "sul_ponticello", "name": "Sul ponticello", "description": "Bow near bridge (glassy)"},
        {"id": "sul_tasto", "name": "Sul tasto", "description": "Bow near fingerboard (soft)"},
        {"id": "col_legno", "name": "Col legno", "description": "Wood of bow (percussive)"},
        {"id": "harmonics", "name": "Harmonics", "description": "Natural harmonics (ethereal)"},
    ]
