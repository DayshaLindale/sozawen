"""Sozawen Physical Bass — from the same physics as guitar, deeper.

Same Karplus-Strong string model. Different body. Different strings.
Different character. A Fender Precision thumps different from a
Rickenbacker growl because the BODIES are different shapes, different
woods, different pickup positions.

The string is the same physics — delay line, lowpass feedback, decay.
The body is where the personality lives.

Amp models add the final character — Ampeg SVT tube warmth vs
Darkglass modern clarity vs clean DI transparency.
"""

import numpy as np
from scipy.signal import lfilter, butter

from sozawen.physical_guitar import (
    karplus_strong, body_resonance,
)


# ═══════════════════════════════════════════════════════════════════
# BASS BODY PROFILES
# ═══════════════════════════════════════════════════════════════════
# Same format as guitar: (frequency_hz, gain, q_factor)
# Bass bodies are larger → lower Helmholtz, lower resonances
# Pickup position dominates electric bass tone more than body wood

BASS_BODIES = {
    "precision": [
        # Fender Precision: split single-coil pickup at ~60% position
        # Thumpy, focused midrange, "the" bass sound
        (42, 0.7, 5),       # Helmholtz — large body
        (110, 0.6, 7),      # Body fundamental
        (250, 0.5, 10),     # Low-mid warmth
        (400, 0.8, 8),      # Midrange THUMP — P-Bass signature
        (800, 0.4, 10),     # Upper mid
        (1500, 0.2, 8),     # Presence — rolls off
        (3000, 0.1, 6),     # Top — minimal (split coil = warm)
    ],

    "jazz": [
        # Fender Jazz Bass: two single-coil pickups (bridge + neck)
        # Scooped mids, bright top, growly when both pickups blend
        (45, 0.6, 5),       # Helmholtz
        (100, 0.7, 7),      # Bass fundamental — strong low end
        (200, 0.5, 10),     # Low mid
        (500, 0.3, 12),     # Mid SCOOP — Jazz signature
        (1000, 0.5, 8),     # Upper mid return
        (2000, 0.6, 6),     # Brightness — bridge pickup
        (4000, 0.4, 5),     # Top — single coil sizzle
    ],

    "rickenbacker": [
        # Rickenbacker 4003: through-body neck, dual pickups
        # Growl, aggressive high-mid, piano-like clarity
        (48, 0.5, 6),       # Helmholtz
        (120, 0.6, 8),      # Body
        (300, 0.5, 10),     # Low mid
        (600, 0.4, 10),     # Mid
        (800, 0.8, 7),      # HIGH-MID GROWL — Rick signature
        (1600, 0.6, 6),     # Presence — piano-like
        (3500, 0.4, 5),     # Treble bite
        (5000, 0.2, 4),     # Top
    ],

    "stingray": [
        # Music Man StingRay: single humbucker at bridge, active preamp
        # Aggressive, punchy, modern. Slap bass standard.
        (45, 0.6, 5),       # Helmholtz
        (100, 0.7, 7),      # Low end — strong
        (250, 0.4, 10),     # Low mid
        (600, 0.9, 6),      # PUNCH — StingRay signature (active boost)
        (1200, 0.6, 7),     # Upper mid — aggressive
        (2500, 0.5, 5),     # Presence
        (4500, 0.3, 4),     # Top — humbucker still has some top
    ],

    "hofner": [
        # Hofner 500/1 "Beatle Bass": hollow body, short scale
        # Thumpy, dark, very little sustain. McCartney's sound.
        (50, 0.9, 4),       # Helmholtz — hollow body resonates more
        (120, 0.8, 6),      # Body — strong fundamental coupling
        (250, 0.7, 8),      # Warmth — dominates
        (400, 0.5, 10),     # Mid
        (700, 0.3, 12),     # Upper mid — rolled off
        (1200, 0.15, 8),    # Presence — very little
    ],

    "upright": [
        # Upright/acoustic bass: large body, no electronics
        # Deep, woody, warm. The jazz bass sound.
        (35, 1.0, 3),       # Helmholtz — very large body
        (80, 0.9, 5),       # Body fundamental — deep
        (160, 0.7, 7),      # Second mode
        (300, 0.5, 9),      # Warmth
        (550, 0.4, 11),     # Mid
        (900, 0.2, 10),     # Upper body
        (1500, 0.1, 8),     # Presence — soft
    ],

    "thunderbird": [
        # Gibson Thunderbird: through-body neck, T-Bird pickups
        # Massive low end, thick midrange, rock bass
        (40, 0.8, 4),       # Helmholtz — mahogany body
        (90, 0.7, 6),       # Very deep body resonance
        (200, 0.6, 8),      # Low mid — thick
        (450, 0.7, 7),      # MIDRANGE THICKNESS — Thunderbird signature
        (900, 0.4, 9),      # Upper mid
        (1800, 0.2, 7),     # Presence
        (3000, 0.1, 5),     # Top — rolled off
    ],
}

BASS_NAMES = {
    "precision": "Fender Precision (thumpy, focused)",
    "jazz": "Fender Jazz (scooped, bright)",
    "rickenbacker": "Rickenbacker 4003 (growl, clarity)",
    "stingray": "Music Man StingRay (punch, aggressive)",
    "hofner": "Hofner Beatle Bass (dark, thumpy)",
    "upright": "Upright/Acoustic Bass (deep, woody)",
    "thunderbird": "Gibson Thunderbird (massive, thick)",
}


# ═══════════════════════════════════════════════════════════════════
# BASS STRING SETS
# ═══════════════════════════════════════════════════════════════════

BASS_STRINGS = {
    "roundwound": {
        "name": "Roundwound (.045-.105)",
        "decay": [0.998, 0.997, 0.997, 0.996],
        "brightness": [0.55, 0.5, 0.45, 0.4],
        "description": "Bright, zingy, standard rock/pop",
    },
    "flatwound": {
        "name": "Flatwound (.045-.105)",
        "decay": [0.997, 0.996, 0.996, 0.995],
        "brightness": [0.3, 0.28, 0.25, 0.22],
        "description": "Warm, thumpy, classic Motown/jazz",
    },
    "tapewound": {
        "name": "Tapewound (.050-.105)",
        "decay": [0.996, 0.995, 0.995, 0.994],
        "brightness": [0.25, 0.22, 0.2, 0.18],
        "description": "Deep, upright-like feel on electric",
    },
    "stainless": {
        "name": "Stainless Steel (.040-.100)",
        "decay": [0.999, 0.998, 0.998, 0.997],
        "brightness": [0.65, 0.6, 0.55, 0.5],
        "description": "Very bright, aggressive, slap-friendly",
    },
}


# ═══════════════════════════════════════════════════════════════════
# AMP MODELS
# ═══════════════════════════════════════════════════════════════════

def amp_model(signal, model="clean_di", sr=44100, drive=0.3):
    """Apply bass amp character to the signal.

    model: "ampeg_svt", "darkglass", "clean_di", "orange", "mesa"
    drive: overdrive amount (0 = clean, 1 = heavy)
    """
    output = signal.copy()

    if model == "ampeg_svt":
        # Ampeg SVT: tube warmth, mid presence, compression
        # ALWAYS apply tube saturation — SVT is never truly clean
        output = np.tanh(output * (1.5 + drive * 4)) / (1.2 + drive)
        # Strong mid boost — SVT signature
        b, a = butter(2, [300 / (sr / 2), 2000 / (sr / 2)], btype='band')
        mid = lfilter(b, a, output) * 0.6
        output = output * 0.7 + mid
        # Low-end rolloff (tube transformer character)
        b, a = butter(1, 40 / (sr / 2), btype='high')
        output = lfilter(b, a, output)
        # High-end rolloff (tube amps are never harsh)
        b, a = butter(1, 6000 / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)

    elif model == "darkglass":
        # Darkglass: modern aggressive distortion with clean low-end blend
        clean = output.copy()
        # ALWAYS distort — Darkglass is never subtle
        distorted = np.tanh(output * (2.0 + drive * 6)) * 0.8
        # High-pass the distortion (keep clean lows — the Darkglass signature)
        b, a = butter(2, 300 / (sr / 2), btype='high')
        distorted = lfilter(b, a, distorted).astype(np.float32)
        # Blend: clean low end + distorted highs
        b, a = butter(2, 300 / (sr / 2), btype='low')
        clean_lows = lfilter(b, a, clean).astype(np.float32)
        output = clean_lows * 0.7 + distorted * 0.8
        # Strong presence boost — modern clarity
        b, a = butter(2, [2000 / (sr / 2), 6000 / (sr / 2)], btype='band')
        presence = lfilter(b, a, output).astype(np.float32) * 0.5
        output = output + presence

    elif model == "orange":
        # Orange: warm, compressed, grinding mids
        if drive > 0.1:
            output = np.tanh(output * (1 + drive * 4)) / (1 + drive)
        # Low-mid emphasis
        b, a = butter(2, [200 / (sr / 2), 800 / (sr / 2)], btype='band')
        low_mid = lfilter(b, a, output) * 0.4
        output = output + low_mid

    elif model == "mesa":
        # Mesa Boogie: tight low end, aggressive mids, modern
        if drive > 0.1:
            output = np.tanh(output * (1 + drive * 6)) * 0.8
        # Tight low end (high-pass higher than SVT)
        b, a = butter(2, 50 / (sr / 2), btype='high')
        output = lfilter(b, a, output)
        # Mid scoop then presence lift
        b, a = butter(2, [2000 / (sr / 2), 4000 / (sr / 2)], btype='band')
        presence = lfilter(b, a, output) * 0.3
        output = output + presence

    # else: clean_di — no processing

    # Normalize
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * 0.85

    return output.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# PLAYING TECHNIQUES
# ═══════════════════════════════════════════════════════════════════

def slap(freq, duration, sr=44100, body_profile="stingray", string_set="stainless"):
    """Slap bass technique — thumb strike on string against fretboard.

    Dramatically different from fingerstyle: loud percussive transient,
    much brighter, the string bounces off the fretboard creating buzz.
    """
    strings = BASS_STRINGS.get(string_set, BASS_STRINGS["stainless"])
    idx = 0

    # Very bright, very hard pluck — nothing like fingerstyle
    note = karplus_strong(
        freq, duration, sr,
        decay=strings["decay"][idx] * 0.997,
        brightness=min(1.0, strings["brightness"][idx] + 0.5),  # much brighter
        pluck_position=0.1,   # near fretboard end
        pick_hardness=1.0,    # maximum impact
    )

    # LOUD click transient — the thumb hitting the string against the fret
    click_len = int(0.008 * sr)
    click = np.random.randn(click_len).astype(np.float32) * 0.7
    b, a = butter(2, 2500 / (sr / 2), btype='high')
    click = lfilter(b, a, click).astype(np.float32)
    click *= np.exp(-np.linspace(0, 15, click_len))  # fast decay

    # Fret buzz — harmonics from string bouncing on frets
    buzz_len = int(0.015 * sr)
    t = np.linspace(0, 0.015, buzz_len, dtype=np.float32)
    buzz = np.zeros(buzz_len, dtype=np.float32)
    for h in [2, 3, 4, 5, 6]:
        buzz += np.sin(2 * np.pi * freq * h * t) * 0.15 / h
    buzz *= np.exp(-t * 300)

    result = np.zeros(len(note), dtype=np.float32)
    result[:len(note)] = note
    result[:click_len] += click
    result[:buzz_len] += buzz

    body = BASS_BODIES.get(body_profile, BASS_BODIES["stingray"])
    return body_resonance(result, body, sr)


def pop(freq, duration, sr=44100, body_profile="stingray", string_set="stainless"):
    """Pop bass technique — finger pulls string away from fretboard.

    Creates a very bright, snappy tone. The string slaps back against
    the frets creating a percussive attack.
    """
    strings = BASS_STRINGS.get(string_set, BASS_STRINGS["stainless"])
    idx = min(2, len(strings["decay"]) - 1)  # pop is usually on higher strings

    note = karplus_strong(
        freq, duration, sr,
        decay=strings["decay"][idx] * 0.997,
        brightness=min(1.0, strings["brightness"][idx] + 0.4),
        pluck_position=0.1,   # very close to bridge
        pick_hardness=1.0,    # maximum attack
    )

    # Fret buzz — short burst of harmonics
    buzz_len = int(0.008 * sr)
    buzz = np.zeros(buzz_len, dtype=np.float32)
    t = np.linspace(0, 0.008, buzz_len, dtype=np.float32)
    for harmonic in range(2, 8):
        buzz += np.sin(2 * np.pi * freq * harmonic * t) * 0.1 / harmonic
    env = np.exp(-t * 500)
    buzz *= env

    result = np.zeros(len(note), dtype=np.float32)
    result[:len(note)] = note
    result[:buzz_len] += buzz

    body = BASS_BODIES.get(body_profile, BASS_BODIES["stingray"])
    return body_resonance(result, body, sr)


# ═══════════════════════════════════════════════════════════════════
# FULL BASS SYNTHESIZER
# ═══════════════════════════════════════════════════════════════════

def synthesize_bass_note(freq, duration, sr=44100,
                        body_profile="precision",
                        string_set="roundwound",
                        string_index=0,
                        technique="finger",
                        velocity=0.7,
                        amp="clean_di",
                        drive=0.0):
    """Synthesize a complete bass note.

    technique: "finger", "pick", "slap", "pop", "muted"
    """
    strings = BASS_STRINGS.get(string_set, BASS_STRINGS["roundwound"])
    idx = min(string_index, len(strings["decay"]) - 1)

    if technique == "slap":
        note = slap(freq, duration, sr, body_profile, string_set)
    elif technique == "pop":
        note = pop(freq, duration, sr, body_profile, string_set)
    else:
        decay = strings["decay"][idx]
        brightness = strings["brightness"][idx]

        # Technique modifiers
        if technique == "pick":
            brightness = min(1.0, brightness + 0.15)
            pick_hard = 0.8
        elif technique == "muted":
            decay *= 0.99
            brightness *= 0.6
            pick_hard = 0.2
        else:  # finger
            pick_hard = 0.2

        # Velocity affects brightness
        brightness = min(1.0, brightness + velocity * 0.15)

        string_signal = karplus_strong(
            freq, duration, sr,
            decay=decay,
            brightness=brightness,
            pluck_position=0.45,
            pick_hardness=pick_hard,
        )

        body = BASS_BODIES.get(body_profile, BASS_BODIES["precision"])
        note = body_resonance(string_signal, body, sr)

    # Apply amp model
    if amp != "clean_di" or drive > 0.1:
        note = amp_model(note, amp, sr, drive)

    # Apply velocity
    note *= velocity

    return note


def list_bass_models():
    """List available bass models."""
    return [{"id": k, "name": v} for k, v in BASS_NAMES.items()]


def list_bass_strings():
    """List available string sets."""
    return [{"id": k, "name": v["name"], "description": v["description"]}
            for k, v in BASS_STRINGS.items()]


def list_bass_amps():
    """List available amp models."""
    return [
        {"id": "clean_di", "name": "Clean DI (transparent)"},
        {"id": "ampeg_svt", "name": "Ampeg SVT (tube warmth)"},
        {"id": "darkglass", "name": "Darkglass (modern clarity)"},
        {"id": "orange", "name": "Orange (grinding warmth)"},
        {"id": "mesa", "name": "Mesa Boogie (tight, aggressive)"},
    ]


def list_bass_techniques():
    """List available playing techniques."""
    return [
        {"id": "finger", "name": "Fingerstyle", "description": "Standard plucking with fingers"},
        {"id": "pick", "name": "Pick", "description": "Brighter attack with a plectrum"},
        {"id": "slap", "name": "Slap", "description": "Thumb strike — percussive funk sound"},
        {"id": "pop", "name": "Pop", "description": "Finger pull — bright, snappy"},
        {"id": "muted", "name": "Palm Mute", "description": "Dampened, short notes"},
    ]
