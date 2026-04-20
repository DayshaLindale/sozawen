"""Sozawen Humanize Engine — no two notes are ever the same.

The difference between a synthesizer and an instrument is that instruments
are played by humans. Humans aren't perfect. That imperfection IS the
music. This module adds the micro-variations that make physics-modeled
instruments feel alive.

Applied to ALL 62 instruments automatically.

Research basis:
- Superior Drummer 3: 20-25 velocity layers x 8-12 round-robins per articulation
- BFD3: 32 velocity layers, "pre-warmed" cymbal captures
- Sensory Percussion: ML-based hit position detection
- Roland V-Drums: continuous positional sensing, S-curve velocity mapping

We achieve similar variation through math instead of samples.
"""

import numpy as np


def humanize_audio(audio, velocity=0.7, sr=44100, instrument_type="default"):
    """Apply humanization to a rendered instrument note.

    Adds micro-variations that make each note sound slightly different,
    even with identical input parameters. This is the difference between
    a synth patch and a living instrument.

    Parameters:
        audio: numpy array of rendered audio
        velocity: 0-1 how hard the note was played
        sr: sample rate
        instrument_type: affects which humanizations are applied
            "plucked" — guitar, bass, harp
            "bowed" — violin, viola, cello
            "struck" — piano, percussion, drums
            "blown" — brass, woodwinds, flute
            "keys" — rhodes, wurlitzer, organ
            "default" — generic
    """
    if audio is None or len(audio) == 0:
        return audio

    result = audio.copy().astype(np.float64)
    n = len(result)

    # ═══ 1. MICRO PITCH VARIATION ═══
    # Real instruments are never perfectly in tune — wood expands,
    # strings stretch, reeds warm up. ±3 cents is imperceptible
    # but adds life.
    pitch_drift_cents = np.random.uniform(-3, 3)
    pitch_ratio = 2 ** (pitch_drift_cents / 1200)
    # Apply by resampling slightly
    if abs(pitch_ratio - 1.0) > 0.0001 and n > 100:
        new_n = int(n / pitch_ratio)
        indices = np.linspace(0, n - 1, new_n)
        result_resampled = np.interp(indices, np.arange(n), result)
        # Pad or truncate to original length
        if len(result_resampled) >= n:
            result = result_resampled[:n]
        else:
            padded = np.zeros(n, dtype=np.float64)
            padded[:len(result_resampled)] = result_resampled
            result = padded

    # ═══ 2. AMPLITUDE MICRO-VARIATION ═══
    # Every hit/bow/breath has slightly different energy.
    # ±5% variation at the sample level, shaped by a slow envelope.
    amp_variation = 1.0 + np.random.uniform(-0.05, 0.05)
    # Slow amplitude wobble (~2-5Hz) simulates hand/breath instability
    wobble_freq = np.random.uniform(2, 5)
    wobble_depth = 0.02 + velocity * 0.01  # harder playing = more stable
    t = np.linspace(0, n / sr, n, dtype=np.float64)
    wobble = 1.0 + wobble_depth * np.sin(2 * np.pi * wobble_freq * t + np.random.uniform(0, 2 * np.pi))
    result *= amp_variation * wobble

    # ═══ 3. VELOCITY-DEPENDENT TIMBRE ═══
    # Real instruments change TONE with velocity, not just volume.
    # Soft = warmer, fewer harmonics. Hard = brighter, more harmonics.
    if velocity < 0.3:
        # Soft playing: gentle lowpass, warmer
        from scipy.signal import butter, lfilter
        cutoff = 3000 + velocity * 10000  # 3kHz-6kHz for soft
        b, a = butter(1, min(cutoff, sr/2 - 1) / (sr/2), btype='low')
        result = lfilter(b, a, result)
    elif velocity > 0.85:
        # Hard playing: add presence/brightness
        # Gentle high shelf boost simulates harder attack exciting more harmonics
        from scipy.signal import butter, lfilter
        b, a = butter(1, 2000 / (sr/2), btype='high')
        highs = lfilter(b, a, result) * 0.15 * velocity
        result = result + highs

    # ═══ 4. ATTACK VARIATION ═══
    # The initial transient is never identical — pick angle, bow pressure,
    # hammer felt condition, embouchure tightness all vary per note.
    attack_samples = int(0.005 * sr)  # first 5ms
    if attack_samples > 0 and attack_samples < n:
        # Vary the attack shape slightly
        attack_jitter = np.random.uniform(0.8, 1.2)
        attack_curve = np.linspace(0, 1, attack_samples) ** attack_jitter
        result[:attack_samples] *= attack_curve / (np.linspace(0, 1, attack_samples) + 0.001)
        # Clip to prevent explosion
        result[:attack_samples] = np.clip(result[:attack_samples], -2.0, 2.0)

    # ═══ 5. NOISE FLOOR ═══
    # Real instruments have mechanical noise — key clicks, fret buzz,
    # bow hair texture, valve clicks. Very subtle.
    noise_level = 0.003 + velocity * 0.002  # harder = slightly more mechanical noise
    if instrument_type in ("plucked", "struck"):
        noise_level *= 1.5  # picks and hammers are noisier
    elif instrument_type == "bowed":
        noise_level *= 0.7  # bowing is smoother
    elif instrument_type == "blown":
        noise_level *= 0.5  # breath is the noise, already modeled

    mech_noise = np.random.randn(min(int(0.01 * sr), n)) * noise_level
    result[:len(mech_noise)] += mech_noise

    # ═══ 6. RELEASE VARIATION ═══
    # Notes don't end identically — finger lift speed, damper felt condition,
    # how quickly the bow leaves the string.
    release_samples = min(int(0.03 * sr), n)
    if release_samples > 0:
        release_jitter = np.random.uniform(0.7, 1.3)
        release_curve = np.linspace(1, 0, release_samples) ** release_jitter
        result[-release_samples:] *= release_curve

    # ═══ 7. INSTRUMENT-SPECIFIC VARIATION ═══
    if instrument_type == "plucked":
        # Guitar/bass: slight pick scrape noise on hard attacks
        if velocity > 0.6:
            scrape_n = int(0.003 * sr)
            scrape = np.random.randn(min(scrape_n, n)) * 0.01 * velocity
            from scipy.signal import butter, lfilter
            b, a = butter(2, [2000 / (sr/2), 8000 / (sr/2)], btype='band')
            scrape = lfilter(b, a, np.pad(scrape, (0, max(0, 256-len(scrape)))))[:scrape_n]
            result[:scrape_n] += scrape

    elif instrument_type == "struck":
        # Piano/percussion: hammer hardness varies with velocity
        # Already handled by velocity-dependent timbre above
        pass

    elif instrument_type == "bowed":
        # Strings: bow pressure micro-variation creates subtle AM
        bow_var_freq = np.random.uniform(3, 8)
        bow_var_depth = 0.01 + np.random.uniform(0, 0.02)
        bow_var = 1.0 + bow_var_depth * np.sin(2 * np.pi * bow_var_freq * t)
        result *= bow_var

    elif instrument_type == "blown":
        # Brass/woodwinds: breath pressure fluctuation
        breath_freq = np.random.uniform(4, 10)
        breath_depth = 0.015 + np.random.uniform(0, 0.01)
        breath_var = 1.0 + breath_depth * np.sin(2 * np.pi * breath_freq * t)
        result *= breath_var

    # ═══ 8. NORMALIZE SAFETY ═══
    peak = np.max(np.abs(result))
    if peak > 1.0:
        result /= peak * 1.05  # leave 5% headroom

    return result.astype(np.float32)


# Instrument type mapping for the 62 instruments
INSTRUMENT_TYPES = {
    # Guitar
    "taylor_dreadnought": "plucked", "martin_d28": "plucked", "gibson_j45": "plucked",
    "classical_nylon": "plucked", "electric_strat": "plucked", "les_paul": "plucked",
    "acoustic_bass_guitar": "plucked",
    # Bass
    "precision": "plucked", "jazz": "plucked", "rickenbacker": "plucked",
    "stingray": "plucked", "hofner": "plucked", "upright": "plucked",
    "thunderbird": "plucked",
    # Piano
    "steinway_d": "struck", "yamaha_cfx": "struck", "bosendorfer": "struck",
    "upright_piano": "struck", "honkytonk": "struck",
    # Keys
    "rhodes_mark1": "struck", "rhodes_mark2": "struck", "wurlitzer_200a": "struck",
    "clavinet_d6": "plucked", "hammond_b3": "keys",
    # Strings
    "violin": "bowed", "stradivarius": "bowed", "viola": "bowed",
    "cello": "bowed", "contrabass": "bowed",
    # Brass
    "trumpet": "blown", "french_horn": "blown", "trombone": "blown", "tuba": "blown",
    # Woodwinds
    "flute": "blown", "clarinet": "blown", "oboe": "blown", "bassoon": "blown",
    "alto_sax": "blown", "tenor_sax": "blown", "soprano_sax": "blown", "bari_sax": "blown",
    # Percussion
    "timpani": "struck", "marimba": "struck", "xylophone": "struck",
    "vibraphone": "struck", "glockenspiel": "struck", "tubular_bells": "struck",
    "triangle": "struck", "tambourine": "struck",
}


def get_instrument_type(model_name):
    """Get the humanization type for an instrument model."""
    return INSTRUMENT_TYPES.get(model_name, "default")
