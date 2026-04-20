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

def _tube_stage(signal, gain=1.0, bias=0.0):
    """Single 12AX7 tube gain stage — ASYMMETRIC soft clipping.

    Real tube transfer function (from ampbooks.com/dsp/preamp):
    - Positive clip at ~+0.7 (grid current limiting)
    - Negative clip at ~-0.33 (cutoff)
    - Asymmetry generates EVEN harmonics (2nd, 4th) = "warmth"
    - Bias shifts the operating point — affects which harmonics dominate

    The key insight from SRV/Hendrix research: the tube responds to
    INPUT LEVEL. Louder input = more clipping = more harmonics.
    This is "edge of breakup" — the amp is responsive to touch.
    """
    x = signal * gain + bias
    # Asymmetric soft clip: positive clips higher than negative
    # At low gain: gradual, responsive to touch (edge of breakup)
    # At high gain: approaches hard clip (metal saturation)
    #
    # Blend between soft (rational) and hard (tanh) based on signal level
    # This gives clean dynamics at low gain and heavy saturation at high gain
    abs_x = np.abs(x)

    # Soft component (responsive, dynamic)
    soft_pos = np.where(x > 0, x / (1 + abs_x * 1.2) * 0.7, 0)
    soft_neg = np.where(x < 0, x / (1 + abs_x * 2.5) * 0.33, 0)
    soft = soft_pos + soft_neg

    # Hard component (saturated, compressed)
    hard_pos = np.where(x > 0, np.tanh(x * 2.0) * 0.65, 0)
    hard_neg = np.where(x < 0, np.tanh(x * 4.0) * 0.30, 0)
    hard = hard_pos + hard_neg

    # Blend: at low levels, mostly soft. At high levels, mostly hard.
    blend = np.minimum(abs_x * 0.8, 1.0)  # 0→soft, 1→hard
    return ((1 - blend) * soft + blend * hard).astype(np.float32)


def _diode_clip(signal, gain=1.0, vf=0.6):
    """Diode clipping — TS808 style.

    Silicon diodes: Vf ≈ 0.6V, sharp knee
    Germanium diodes: Vf ≈ 0.3V, softer knee

    Real TS808 has a 51pF cap across the diodes that softens
    the clipping corners — simulated by gentle lowpass after clip.
    Source: electrosmash.com/tube-screamer-analysis
    """
    x = signal * gain
    # Hard clip at forward voltage thresholds
    clipped = np.clip(x, -vf, vf)
    return clipped.astype(np.float32)


def _tone_stack(signal, bass=0.5, mid=0.5, treble=0.5, sr=44100):
    """Interactive 3-band tone stack — like a real amp's bass/mid/treble.

    In real amps, the tone controls are PASSIVE and INTERACTIVE —
    changing one affects the others. This simplified version captures
    the key behavior: the EQ shapes WHAT gets distorted in the next stage.
    """
    output = np.zeros_like(signal)

    # Bass (below 300Hz)
    b, a = butter(2, 300 / (sr / 2), btype='low')
    low = lfilter(b, a, signal).astype(np.float32) * (0.2 + bass * 1.0)

    # Mid (300-3000Hz)
    b, a = butter(2, [300 / (sr / 2), 3000 / (sr / 2)], btype='band')
    mids = lfilter(b, a, signal).astype(np.float32) * (0.2 + mid * 1.0)

    # Treble (above 3000Hz)
    b, a = butter(2, 3000 / (sr / 2), btype='high')
    high = lfilter(b, a, signal).astype(np.float32) * (0.2 + treble * 1.0)

    return (low + mids + high).astype(np.float32)


def _speaker_cab(signal, cab_type="4x12", sr=44100):
    """Speaker cabinet simulation — the final tone shaping.

    Without a cab, distorted guitar sounds fizzy and thin.
    The cab is a lowpass + resonance that removes harsh highs
    and adds body. Different cabs sound different.
    """
    if cab_type == "4x12":
        # Marshall 4x12: mid-focused, tight, rock standard
        b, a = butter(3, 5000 / (sr / 2), btype='low')
        output = lfilter(b, a, signal).astype(np.float32)
        b, a = butter(1, 80 / (sr / 2), btype='high')
        output = lfilter(b, a, output).astype(np.float32)
        # Cabinet resonance around 2kHz
        b, a = butter(2, [1500 / (sr / 2), 3000 / (sr / 2)], btype='band')
        res = lfilter(b, a, output).astype(np.float32) * 0.3
        return output + res

    elif cab_type == "1x12":
        # Fender combo: more open, brighter, less low end
        b, a = butter(2, 6000 / (sr / 2), btype='low')
        output = lfilter(b, a, signal).astype(np.float32)
        b, a = butter(1, 100 / (sr / 2), btype='high')
        return lfilter(b, a, output).astype(np.float32)

    elif cab_type == "2x12":
        # Vox/Mesa 2x12: balanced, open back character
        b, a = butter(2, 5500 / (sr / 2), btype='low')
        output = lfilter(b, a, signal).astype(np.float32)
        b, a = butter(1, 90 / (sr / 2), btype='high')
        return lfilter(b, a, output).astype(np.float32)

    return signal


def electric_amp(signal, amp_type="clean", drive=0.3, sr=44100):
    """Process guitar through a physically modeled amp chain.

    Based on how famous tones actually work:
    - Hendrix: Fuzz Face → barely-breaking-up Marshall Plexi
    - SRV: TS808 as boost (low gain, high output) → edge-of-breakup Fender
    - Metallica: EMG → Mesa IIC+ four stages → V-shaped EQ scoop

    Key insight: EQ sits BETWEEN gain stages. The EQ shapes what
    gets distorted, not just what you hear after. This is why turning
    up the mids on a Marshall changes the DISTORTION CHARACTER, not
    just the overall tone.
    """
    output = signal.copy()

    if amp_type == "clean":
        # Fender Twin Reverb: single tube stage, clean headroom
        # The amp barely clips — sparkly, glassy, responsive to touch
        # SRV's foundation: this amp on the edge, TS808 pushes it over
        output = _tube_stage(output, 1.0 + drive * 2.5, bias=0.05)
        output = _tone_stack(output, bass=0.4, mid=0.3, treble=0.7, sr=sr)
        output = _speaker_cab(output, "1x12", sr)

    elif amp_type == "crunch":
        # Marshall JCM800 / Plexi: THE rock amp
        # Two tube stages with tone stack BETWEEN them
        # Hendrix ran this just past breakup with fuzz in front
        output = _tube_stage(output, 2.0 + drive * 5, bias=0.08)  # V1 preamp

        # TONE STACK BETWEEN STAGES — shapes what V2 distorts
        output = _tone_stack(output, bass=0.4, mid=0.7, treble=0.5, sr=sr)

        output = _tube_stage(output, 1.5 + drive * 3, bias=0.05)  # V2 preamp

        # Power amp — adds compression and body
        output = _tube_stage(output, 1.2 + drive * 1.5)  # power tubes

        output = _speaker_cab(output, "4x12", sr)

    elif amp_type == "overdrive":
        # TS808 Tube Screamer: the SRV/blues sound
        # Op-amp gain → diode clip → tone filter → into amp
        # SRV settings: drive 3, volume 9 (boost, not distortion)

        # Input filter — the TS808's mid hump BEFORE clipping
        b, a = butter(2, [250 / (sr / 2), 4000 / (sr / 2)], btype='band')
        output = lfilter(b, a, output).astype(np.float32)

        # Op-amp gain stage
        output = output * (2.5 + drive * 8)

        # Diode clipping (back-to-back 1N914 silicon, Vf=0.6V)
        output = _diode_clip(output, 1.0, 0.6)

        # 51pF capacitor across diodes — softens clipping corners
        b, a = butter(1, 4500 / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)

        # Output tone control — the TS808's output filter
        output = _tone_stack(output, bass=0.3, mid=0.8, treble=0.4, sr=sr)

        # Into a clean amp (like SRV: TS → Fender at edge of breakup)
        output = _tube_stage(output, 1.3 + drive * 1.5, bias=0.03)
        output = _speaker_cab(output, "1x12", sr)

    elif amp_type == "high_gain":
        # Mesa Mark IIC+ — Metallica's Black Album tone
        # EMG 81 → four stages → scooped mids → tight cab
        output = output * 1.5  # hot EMG input
        output = _tube_stage(output, 4.0 + drive * 8, bias=0.12)
        output = _tone_stack(output, bass=0.8, mid=0.15, treble=0.9, sr=sr)
        output = _tube_stage(output, 3.0 + drive * 6, bias=0.1)
        b, a = butter(1, 5500 / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)
        output = _tube_stage(output, 2.5 + drive * 4, bias=0.08)
        output = _tube_stage(output, 2.0 + drive * 3, bias=0.05)
        output = _speaker_cab(output, "4x12", sr)

    elif amp_type == "mesa_rectifier":
        # Mesa Dual Rectifier — Lamb of God, Tool, Deftones
        # Thick, warm saturation with massive low end
        # Rectifier tubes cause "sag" — compression bloom under sustain

        output = output * 1.4  # active pickup
        # Tight gate — kill noise below threshold
        gate_threshold = 0.01
        gate = np.where(np.abs(output) > gate_threshold, 1.0, 0.0).astype(np.float32)
        # Smooth gate to avoid clicks
        from scipy.ndimage import uniform_filter1d
        gate = uniform_filter1d(gate.astype(np.float64), size=int(0.002 * sr)).astype(np.float32)

        # Stage 1: preamp — moderate gain, Mesa warmth
        output = _tube_stage(output, 3.5 + drive * 7, bias=0.10)

        # Rectifier sag simulation — output level compresses the signal
        # Louder = more sag = less gain (natural compression bloom)
        rms = np.sqrt(np.convolve(output ** 2, np.ones(256) / 256, mode='same'))
        sag = 1.0 / (1.0 + rms * 2.0)  # gain reduces as RMS rises
        output = output * (0.6 + sag * 0.4)

        # EQ — Mesa Rectifier has LESS scoop than Mark series
        # More mids = thicker, heavier, less "scooped" character
        output = _tone_stack(output, bass=0.9, mid=0.35, treble=0.7, sr=sr)

        # Stage 2: cascaded preamp
        output = _tube_stage(output, 2.8 + drive * 5, bias=0.09)

        # Tight low cut — prevent sub-bass mush at high gain
        b, a = butter(2, 80 / (sr / 2), btype='high')
        output = lfilter(b, a, output).astype(np.float32)

        # Stage 3: saturation
        output = _tube_stage(output, 2.2 + drive * 3.5, bias=0.07)

        # Presence — adjustable via drive (more drive = darker)
        pres_freq = 6000 - drive * 1500  # 6000Hz at clean, 4500Hz at max
        b, a = butter(1, pres_freq / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)

        # Stage 4: power amp with sag
        output = _tube_stage(output, 1.8 + drive * 2.5, bias=0.04)

        # Apply gate
        output = output * gate

        # Mesa Recto 4x12 — deeper than Marshall, V30 speakers
        output = _speaker_cab(output, "4x12", sr)
        # Extra low-end body from Recto cab
        b, a = butter(1, 200 / (sr / 2), btype='low')
        low_body = lfilter(b, a, output).astype(np.float32) * 0.15
        output = output + low_body

    elif amp_type == "5150":
        # Peavey 5150 / EVH — Van Halen, Periphery, August Burns Red
        # THE djent amp. Tight, aggressive, percussive pick attack
        # Less sag than Mesa — tighter power section

        output = output * 1.6  # hot input — 5150 input is LOUD
        # Hard noise gate (5150 players always gate)
        gate_threshold = 0.012
        gate = np.where(np.abs(output) > gate_threshold, 1.0, 0.0).astype(np.float32)
        from scipy.ndimage import uniform_filter1d
        gate = uniform_filter1d(gate.astype(np.float64), size=int(0.001 * sr)).astype(np.float32)

        # Stage 1: aggressive preamp — 5150 has more bite than Mesa
        output = _tube_stage(output, 4.5 + drive * 9, bias=0.13)

        # 5150 EQ — harder scoop than Mesa, more treble bite
        output = _tone_stack(output, bass=0.7, mid=0.10, treble=0.95, sr=sr)

        # Tight sub filter EARLY — 5150 is known for tight bass
        b, a = butter(3, 100 / (sr / 2), btype='high')
        output = lfilter(b, a, output).astype(np.float32)

        # Stage 2: crunch — 5150 stays tight
        output = _tube_stage(output, 3.5 + drive * 7, bias=0.11)

        # Presence — 5150 has aggressive upper mids
        b, a = butter(1, 5000 / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)

        # Stage 3: saturation — tighter bias than Mesa
        output = _tube_stage(output, 2.8 + drive * 4.5, bias=0.09)

        # Stage 4: solid-state-like power section (6L6 tubes, very tight)
        output = _tube_stage(output, 2.0 + drive * 2.5, bias=0.03)

        # Apply gate
        output = output * gate

        # 5150 cab — even tighter than Marshall, very focused
        output = _speaker_cab(output, "4x12", sr)

    elif amp_type == "metal":
        # General-purpose metal — TS808 boost → high gain → tight cab
        # The classic modern metal signal chain:
        # Guitar → TS808 (low gain, high output) → High gain amp → 4x12

        # TS808 boost stage (gain low, mids boosted, output hot)
        b, a = butter(2, [250 / (sr / 2), 4000 / (sr / 2)], btype='band')
        mid_boosted = lfilter(b, a, output).astype(np.float32)
        output = output * 0.4 + mid_boosted * 0.8  # mid push
        output = _tube_stage(output, 1.5 + drive * 2, bias=0.03)  # light OD
        output = _diode_clip(output, 1.0, 0.6)  # silicon clip
        b, a = butter(1, 4500 / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)

        # Into high gain amp (5150 style)
        output = output * 1.3
        output = _tube_stage(output, 4.0 + drive * 8, bias=0.12)
        output = _tone_stack(output, bass=0.75, mid=0.20, treble=0.85, sr=sr)
        b, a = butter(2, 90 / (sr / 2), btype='high')
        output = lfilter(b, a, output).astype(np.float32)
        output = _tube_stage(output, 3.0 + drive * 5, bias=0.10)
        output = _tube_stage(output, 2.5 + drive * 3.5, bias=0.07)
        output = _tube_stage(output, 1.8 + drive * 2, bias=0.04)
        output = _speaker_cab(output, "4x12", sr)

    elif amp_type == "fuzz":
        # Fuzz Face: Hendrix, Gilmour
        # Germanium transistors clip at ~0.3V
        # The fuzz goes INTO a slightly dirty amp — not alone

        # Germanium fuzz circuit
        output = output * (4 + drive * 15)
        output = _diode_clip(output, 1.0, 0.3)  # germanium Vf

        # Fuzz tone knob — typically rolled off
        b, a = butter(2, 2000 / (sr / 2), btype='low')
        output = lfilter(b, a, output).astype(np.float32)

        # Octave-up artifact (full-wave rectification in real circuits)
        rectified = np.abs(output) * 0.15
        output = output + rectified

        # Into a Marshall on the edge of breakup (Hendrix approach)
        output = _tube_stage(output, 1.3 + drive * 1.5, bias=0.05)
        output = _tone_stack(output, bass=0.4, mid=0.6, treble=0.5, sr=sr)
        output = _speaker_cab(output, "4x12", sr)

    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * 0.8
    return output.astype(np.float32)


# Electric vs acoustic detection
ELECTRIC_PROFILES = {"electric_strat", "electric_les_paul"}


def synthesize_guitar_note(freq, duration, sr=44100,
                          body_profile="taylor_dreadnought",
                          string_set="light_acoustic",
                          string_index=0,
                          pluck_position=0.5,
                          pick_hardness=0.3,
                          velocity=0.7,
                          amp="", drive=0.3):
    """Synthesize a complete guitar note.

    For electric guitars (Strat, Les Paul), applies pickup simulation
    and optional amp processing. For acoustic, uses body resonance.

    amp: "" (default for type), "clean", "crunch", "overdrive", "high_gain",
         "mesa_rectifier", "5150", "metal", "fuzz"
    drive: 0-1 amp gain
    """
    is_electric = body_profile in ELECTRIC_PROFILES

    strings = STRING_SETS.get(string_set,
                             STRING_SETS["electric_light"] if is_electric
                             else STRING_SETS["light_acoustic"])
    idx = min(string_index, len(strings["decay"]) - 1)

    decay = strings["decay"][idx]
    brightness = strings["brightness"][idx]

    brightness = min(1.0, brightness + velocity * 0.2)
    decay = decay - (1 - velocity) * 0.002

    string_signal = karplus_strong(
        freq, duration, sr,
        decay=decay,
        brightness=brightness,
        pluck_position=pluck_position,
        pick_hardness=pick_hardness,
    )

    if is_electric:
        # Electric: pickup simulation (body resonance is subtle) + amp
        body = BODY_PROFILES.get(body_profile, BODY_PROFILES["electric_strat"])
        output = body_resonance(string_signal, body, sr)

        # Default amp based on guitar type
        if not amp:
            amp = "clean" if body_profile == "electric_strat" else "crunch"
        output = electric_amp(output, amp, drive, sr)
    else:
        # Acoustic: body resonance only, no amp
        body = BODY_PROFILES.get(body_profile, BODY_PROFILES["taylor_dreadnought"])
        output = body_resonance(string_signal, body, sr)

        # But allow amp if explicitly requested (acoustic through amp)
        if amp:
            output = electric_amp(output, amp, drive, sr)

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
