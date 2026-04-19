"""Sozawen Physical Keys — Rhodes, Wurlitzer, Clavinet, Hammond.

Each keyboard has its own physics. A Rhodes is NOT a piano with
effects — it's a tine struck by a hammer, resonating against a
tonebar, picked up by an electromagnetic coil. Different physics,
different soul.

Rhodes Mark I: warm, bell-like, the sound of neo-soul and jazz.
  Tine (metal prong) vibrates → tonebar (tuning fork) resonates
  → pickup (electromagnetic) captures the motion.
  At low velocity: pure, bell-like (fundamental dominates).
  At high velocity: bark, growl (asymmetric clipping from pickup).

Wurlitzer 200A: reedy, biting, aggressive.
  Steel reed struck by hammer → vibrates over electromagnetic pickup.
  Thinner sound than Rhodes, more midrange bite.
  Built-in tremolo circuit. Built-in speaker with its own character.

Clavinet D6: funky, percussive, the sound of Stevie Wonder.
  String pressed against anvil by rubber tip → electromagnetic pickup.
  Two pickups (upper/lower) with phase options.
  Essentially a plucked string but with anvil contact creating buzz.

Hammond B3: the king of organs. Tonewheels + drawbars + Leslie.
  9 drawbars = 9 harmonics = additive synthesis with physical character.
  Tonewheel imperfections = warmth. Key click = percussion.
  Leslie speaker = the rotating sound that defines gospel/rock/jazz organ.

Research: Sound On Sound synthesis tutorials, Wikipedia Hammond organ,
Yorkshire Sound Women Hammond analysis.
"""

import numpy as np
from scipy.signal import lfilter, butter


# ═══════════════════════════════════════════════════════════════════
# RHODES ELECTRIC PIANO
# ═══════════════════════════════════════════════════════════════════

def synthesize_rhodes(midi_note, duration, sr=44100, velocity=0.7,
                     model="mark1", tremolo_rate=3.5, tremolo_depth=0.3):
    """Synthesize a Rhodes electric piano note.

    The Rhodes sound comes from:
    1. Hammer strikes tine (metal prong) — creates initial partials
    2. Tonebar resonates at tine's frequency — sustains the note
    3. Electromagnetic pickup captures motion — creates asymmetric waveform
    4. At high velocity, tine overdrives the pickup — "bark"

    model: "mark1" (warm, dark) or "mark2" (brighter)
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # === TINE + TONEBAR ===
    # Fundamental from tonebar resonance
    signal = np.sin(2 * np.pi * freq * t) * 0.6

    # Tine harmonics — the bell-like quality
    # Rhodes has strong 2nd and 3rd harmonics that decay faster than fundamental
    signal += np.sin(2 * np.pi * freq * 2 * t) * 0.3 * np.exp(-t * 4)
    signal += np.sin(2 * np.pi * freq * 3 * t) * 0.15 * np.exp(-t * 6)
    signal += np.sin(2 * np.pi * freq * 4 * t) * 0.08 * np.exp(-t * 8)

    # Higher partials for Mark II (brighter)
    if model == "mark2":
        signal += np.sin(2 * np.pi * freq * 5 * t) * 0.06 * np.exp(-t * 10)
        signal += np.sin(2 * np.pi * freq * 6 * t) * 0.04 * np.exp(-t * 12)

    # === PICKUP ASYMMETRY ===
    # The electromagnetic pickup creates an asymmetric response
    # This is what gives Rhodes its characteristic "not-quite-sine" quality
    # At low velocity: nearly pure sine (bell-like)
    # At high velocity: asymmetric clipping → bark/growl
    if velocity > 0.5:
        bark = velocity * 0.5
        # Soft asymmetric clipping — positive peaks clip more than negative
        signal = np.where(signal > 0,
                         np.tanh(signal * (1 + bark * 2)) / (1 + bark),
                         signal * (1 + bark * 0.3))

    # === ENVELOPE ===
    # Rhodes has a distinctive envelope: sharp attack, medium decay, long sustain
    attack = 0.002
    decay_time = 0.3 + (1 - velocity) * 0.5  # softer = slower decay
    sustain_level = 0.4

    env = np.ones(n_samples, dtype=np.float32)
    attack_samples = int(attack * sr)
    decay_samples = int(decay_time * sr)

    # Attack
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay to sustain
    decay_end = attack_samples + decay_samples
    if decay_samples > 0 and decay_end < n_samples:
        env[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_samples)
        env[decay_end:] = sustain_level

    # Release (last 15% of duration)
    release_start = int(n_samples * 0.85)
    if release_start < n_samples:
        release_len = n_samples - release_start
        env[release_start:] *= np.exp(-np.linspace(0, 5, release_len))

    signal *= env

    # === TREMOLO ===
    # Built-in tremolo from the Rhodes suitcase amp
    if tremolo_depth > 0:
        trem = 1.0 - tremolo_depth * 0.5 * (1 + np.sin(2 * np.pi * tremolo_rate * t))
        signal *= trem

    # Scale by velocity
    signal *= 0.3 + velocity * 0.7

    # Normalize
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8

    return signal.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# WURLITZER ELECTRIC PIANO
# ═══════════════════════════════════════════════════════════════════

def synthesize_wurlitzer(midi_note, duration, sr=44100, velocity=0.7,
                        tremolo_rate=5.0, tremolo_depth=0.4):
    """Synthesize a Wurlitzer 200A electric piano note.

    The Wurlitzer uses steel reeds instead of tines:
    - Hammer strikes reed → reed vibrates over electromagnetic pickup
    - Thinner, more nasal/reedy tone than Rhodes
    - More distortion at high velocity (built-in amp overdrives easily)
    - Stronger odd harmonics (reed vibration mode)
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # === REED VIBRATION ===
    # Steel reed has more odd harmonics than a tine (like a clarinet reed)
    signal = np.sin(2 * np.pi * freq * t) * 0.5
    signal += np.sin(2 * np.pi * freq * 3 * t) * 0.25 * np.exp(-t * 5)   # strong 3rd
    signal += np.sin(2 * np.pi * freq * 5 * t) * 0.12 * np.exp(-t * 8)   # 5th harmonic
    signal += np.sin(2 * np.pi * freq * 2 * t) * 0.15 * np.exp(-t * 6)   # some even
    signal += np.sin(2 * np.pi * freq * 7 * t) * 0.06 * np.exp(-t * 10)  # brightness

    # === BUILT-IN AMP DISTORTION ===
    # Wurlitzer's internal amp overdrives easily — more aggressive than Rhodes
    drive = 0.3 + velocity * 0.7
    signal = np.tanh(signal * drive * 2) / (1 + drive * 0.5)

    # === ENVELOPE ===
    # Shorter sustain than Rhodes, more percussive
    attack = 0.001
    decay_time = 0.2
    sustain_level = 0.25

    env = np.ones(n_samples, dtype=np.float32)
    a_s = int(attack * sr)
    d_s = int(decay_time * sr)
    if a_s > 0:
        env[:a_s] = np.linspace(0, 1, a_s)
    d_end = a_s + d_s
    if d_s > 0 and d_end < n_samples:
        env[a_s:d_end] = np.linspace(1, sustain_level, d_s)
        env[d_end:] = sustain_level

    release_start = int(n_samples * 0.8)
    if release_start < n_samples:
        release_len = n_samples - release_start
        env[release_start:] *= np.exp(-np.linspace(0, 6, release_len))

    signal *= env

    # === TREMOLO ===
    if tremolo_depth > 0:
        trem = 1.0 - tremolo_depth * 0.5 * (1 + np.sin(2 * np.pi * tremolo_rate * t))
        signal *= trem

    signal *= 0.3 + velocity * 0.7

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8

    return signal.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# CLAVINET
# ═══════════════════════════════════════════════════════════════════

def synthesize_clavinet(midi_note, duration, sr=44100, velocity=0.7,
                       pickup="both"):
    """Synthesize a Hohner Clavinet D6 note.

    The Clavinet is essentially an electrified clavichord:
    - Rubber-tipped key presses string against metal anvil
    - String vibrates between anvil (fret) and bridge
    - Two electromagnetic pickups: upper (bright) and lower (warm)
    - Phase switching creates different timbres

    Very percussive, funky. Stevie Wonder, Led Zeppelin.

    pickup: "both", "upper" (bright), "lower" (warm)
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # === STRING + ANVIL BUZZ ===
    # The anvil contact creates a buzzy, bright tone with strong harmonics
    signal = np.sin(2 * np.pi * freq * t) * 0.4

    # Rich harmonic content — string against metal
    for h in range(2, 10):
        amp = 0.3 / h
        decay = 3 + h * 0.5
        signal += np.sin(2 * np.pi * freq * h * t) * amp * np.exp(-t * decay)

    # === PICKUP SIMULATION ===
    # Upper pickup (near bridge): emphasizes high harmonics
    # Lower pickup (near tuning pins): warmer, more fundamental
    if pickup == "upper":
        b, a = butter(2, 1500 / (sr / 2), btype='high')
        signal = lfilter(b, a, signal).astype(np.float32) * 1.5
    elif pickup == "lower":
        b, a = butter(2, 3000 / (sr / 2), btype='low')
        signal = lfilter(b, a, signal).astype(np.float32) * 1.2
    # "both" = natural mix

    # === PERCUSSIVE ENVELOPE ===
    # Very fast attack, short decay — the most percussive keyboard
    env = np.exp(-t * (4 + velocity * 3))  # faster decay at higher velocity
    env = np.maximum(env, 0.05)  # tiny sustain floor

    # Sharp attack click
    click_samples = int(0.002 * sr)
    click = np.random.randn(click_samples).astype(np.float32) * velocity * 0.2
    signal[:click_samples] += click

    signal *= env
    signal *= velocity

    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8

    return signal.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# HAMMOND ORGAN
# ═══════════════════════════════════════════════════════════════════

# Drawbar footage → frequency multiplier relative to fundamental
DRAWBAR_MULTIPLIERS = [
    0.5,    # 16' — sub-octave
    1.5,    # 5⅓' — 5th + octave (quint)
    1.0,    # 8' — fundamental
    2.0,    # 4' — octave
    3.0,    # 2⅔' — octave + 5th
    4.0,    # 2' — 2 octaves
    5.0,    # 1⅗' — 2 octaves + major 3rd
    6.0,    # 1⅓' — 2 octaves + 5th
    8.0,    # 1' — 3 octaves
]

# Classic drawbar presets
DRAWBAR_PRESETS = {
    "full": [8, 8, 8, 8, 8, 8, 8, 8, 8],
    "jazz": [8, 3, 8, 0, 0, 0, 0, 0, 0],
    "gospel": [6, 8, 8, 8, 4, 8, 5, 8, 8],
    "blues": [8, 8, 8, 8, 0, 0, 0, 0, 0],
    "rock": [8, 8, 8, 6, 0, 0, 0, 0, 0],
    "ballad": [0, 0, 6, 6, 0, 4, 0, 3, 0],
    "booker_t": [8, 8, 8, 0, 0, 0, 0, 0, 8],
    "jimmy_smith": [8, 8, 8, 0, 0, 0, 0, 0, 0],
    "gospel_shout": [8, 8, 8, 8, 8, 8, 8, 8, 8],
    "pipe_flute": [0, 0, 8, 0, 0, 0, 0, 0, 0],
    "pipe_principal": [0, 0, 8, 4, 0, 2, 0, 1, 0],
    "pipe_reed": [0, 0, 8, 8, 0, 8, 0, 8, 0],
}

ORGAN_NAMES = {
    "full": "Hammond Full (gospel/rock)",
    "jazz": "Hammond Jazz (Jimmy Smith)",
    "gospel": "Hammond Gospel (church)",
    "blues": "Hammond Blues",
    "rock": "Hammond Rock",
    "ballad": "Hammond Ballad (soft)",
    "booker_t": "Hammond Booker T (Green Onions)",
    "jimmy_smith": "Hammond Jimmy Smith",
    "gospel_shout": "Hammond Gospel Shout",
    "pipe_flute": "Pipe Organ — Flute Stop",
    "pipe_principal": "Pipe Organ — Principal Stop",
    "pipe_reed": "Pipe Organ — Reed Stop",
}


def synthesize_organ(midi_note, duration, sr=44100, velocity=0.7,
                    drawbar_preset="jazz", drawbars=None,
                    key_click=0.5, percussion=True,
                    leslie="off", overdrive=0.0):
    """Synthesize a Hammond-style organ note.

    drawbar_preset: preset name or None if using custom drawbars
    drawbars: list of 9 values (0-8) for custom registration
    key_click: 0-1, loudness of the key contact click
    percussion: if True, add 2nd/3rd harmonic attack accent
    leslie: "off", "slow" (~0.8Hz), "fast" (~6.5Hz)
    overdrive: 0-1, tube amp saturation
    """
    freq = 440.0 * 2 ** ((midi_note - 69) / 12)
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, dtype=np.float32)

    # Get drawbar settings
    if drawbars is None:
        drawbars = DRAWBAR_PRESETS.get(drawbar_preset, DRAWBAR_PRESETS["jazz"])

    # === TONEWHEEL ADDITIVE SYNTHESIS ===
    signal = np.zeros(n_samples, dtype=np.float32)

    for i, (multiplier, level) in enumerate(zip(DRAWBAR_MULTIPLIERS, drawbars)):
        if level == 0:
            continue

        tone_freq = freq * multiplier
        if tone_freq >= sr / 2:
            continue

        # Drawbar level: 0-8 maps to amplitude
        amp = level / 8.0

        # Tonewheel imperfection — not a perfect sine
        # Real tonewheels have slight distortion from manufacturing
        tone = np.sin(2 * np.pi * tone_freq * t) * amp
        # Add tiny 2nd harmonic of the tonewheel (imperfection)
        tone += np.sin(2 * np.pi * tone_freq * 2 * t) * amp * 0.02

        signal += tone

    # === KEY CLICK ===
    # Real Hammond B3 has a distinctive click from switch contacts
    if key_click > 0:
        click_dur = int(0.003 * sr)
        click = np.random.randn(click_dur).astype(np.float32) * key_click * 0.3
        # Filter click to ~1-3kHz range
        if sr > 6000:
            b, a = butter(2, [1000 / (sr / 2), 3000 / (sr / 2)], btype='band')
            click = lfilter(b, a, click).astype(np.float32)
        signal[:click_dur] += click

    # === PERCUSSION ===
    # Hammond percussion: accent on 2nd or 3rd harmonic at note-on
    if percussion:
        perc_freq = freq * 3  # 3rd harmonic percussion
        if perc_freq < sr / 2:
            perc_dur = 0.15
            perc_samples = min(int(perc_dur * sr), n_samples)
            perc_t = np.linspace(0, perc_dur, perc_samples, dtype=np.float32)
            perc = np.sin(2 * np.pi * perc_freq * perc_t) * 0.3
            perc *= np.exp(-perc_t * 15)  # fast decay
            signal[:perc_samples] += perc

    # === OVERDRIVE ===
    # Tube preamp saturation
    if overdrive > 0.1:
        signal = np.tanh(signal * (1 + overdrive * 4)) / (1 + overdrive)

    # === LESLIE SPEAKER ===
    if leslie != "off":
        # Leslie = amplitude modulation (speaker rotating) + slight pitch mod (Doppler)
        if leslie == "slow":
            rate = 0.8   # chorale speed
            depth = 0.15
        else:  # fast
            rate = 6.5   # tremolo speed
            depth = 0.3

        # Amplitude modulation (speaker distance changes)
        am = 1.0 - depth * 0.5 * (1 + np.sin(2 * np.pi * rate * t))
        signal *= am

        # Doppler pitch modulation (very subtle)
        # Phase modulation simulates the Doppler effect
        doppler_depth = depth * 0.002  # very small pitch variation
        phase_mod = doppler_depth * np.sin(2 * np.pi * rate * t)
        # Apply as time-domain stretching (simplified)
        # For a more accurate Leslie, this would be a proper Doppler simulation
        # This approximation adds subtle chorus-like character
        modulated = np.zeros(n_samples, dtype=np.float32)
        for idx in range(n_samples):
            offset = int(phase_mod[idx] * sr * 0.01)
            src = idx + offset
            if 0 <= src < n_samples:
                modulated[idx] = signal[src]
        signal = signal * 0.5 + modulated * 0.5

    # === ENVELOPE ===
    # Organ has instant attack and instant release (no ADSR like piano)
    # But real organs have a slight ramp from key mechanics
    attack_samples = int(0.005 * sr)
    if attack_samples > 0 and attack_samples < n_samples:
        signal[:attack_samples] *= np.linspace(0, 1, attack_samples)

    # Release
    release_samples = int(0.01 * sr)
    if release_samples > 0 and release_samples < n_samples:
        signal[-release_samples:] *= np.linspace(1, 0, release_samples)

    # Scale by velocity (organs are velocity-sensitive through drawbar levels)
    signal *= 0.3 + velocity * 0.7

    # Normalize
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.8

    return signal.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# COMBINED INTERFACE
# ═══════════════════════════════════════════════════════════════════

def synthesize_keys_note(midi_note, duration, sr=44100, velocity=0.7,
                        instrument="rhodes_mark1", **kwargs):
    """Unified interface for all keyboard instruments."""
    if instrument.startswith("rhodes"):
        model = "mark2" if "mark2" in instrument else "mark1"
        return synthesize_rhodes(midi_note, duration, sr, velocity, model,
                               kwargs.get("tremolo_rate", 3.5),
                               kwargs.get("tremolo_depth", 0.3))
    elif instrument == "wurlitzer":
        return synthesize_wurlitzer(midi_note, duration, sr, velocity,
                                   kwargs.get("tremolo_rate", 5.0),
                                   kwargs.get("tremolo_depth", 0.4))
    elif instrument == "clavinet":
        return synthesize_clavinet(midi_note, duration, sr, velocity,
                                  kwargs.get("pickup", "both"))
    elif instrument.startswith("organ") or instrument.startswith("pipe"):
        preset = instrument.replace("organ_", "").replace("pipe_", "pipe_")
        if preset not in DRAWBAR_PRESETS:
            preset = "jazz"
        return synthesize_organ(midi_note, duration, sr, velocity,
                              drawbar_preset=preset,
                              key_click=kwargs.get("key_click", 0.5),
                              percussion=kwargs.get("percussion", True),
                              leslie=kwargs.get("leslie", "off"),
                              overdrive=kwargs.get("overdrive", 0.0))
    else:
        return synthesize_rhodes(midi_note, duration, sr, velocity)


def list_keys_instruments():
    """List all available keyboard instruments."""
    instruments = [
        {"id": "rhodes_mark1", "name": "Rhodes Mark I (warm, bell-like)"},
        {"id": "rhodes_mark2", "name": "Rhodes Mark II (brighter)"},
        {"id": "wurlitzer", "name": "Wurlitzer 200A (reedy, aggressive)"},
        {"id": "clavinet", "name": "Clavinet D6 (funky, percussive)"},
    ]
    for key, name in ORGAN_NAMES.items():
        instruments.append({"id": f"organ_{key}", "name": name})
    return instruments


def list_drawbar_presets():
    """List available Hammond drawbar presets."""
    return [{"id": k, "name": ORGAN_NAMES.get(k, k)} for k in DRAWBAR_PRESETS]
