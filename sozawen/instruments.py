"""Sozawen Instruments — synthesizer and drum machine from pure math.

No samples, no dependencies, no borrowed sounds.
Every tone generated from oscillators, noise, and envelopes.
GPL-free. BSD-compatible. Ours.
"""

import numpy as np
import logging
from scipy.signal import butter, lfilter

logger = logging.getLogger("sozawen.instruments")


# ═══════════════════════════════════════════════════════════════════
# OSCILLATORS — the raw waves
# ═══════════════════════════════════════════════════════════════════

def sine(freq, duration, sr=44100):
    t = np.arange(int(duration * sr)) / sr
    return np.sin(2 * np.pi * freq * t).astype(np.float32)

def saw(freq, duration, sr=44100):
    t = np.arange(int(duration * sr)) / sr
    return (2 * (t * freq % 1) - 1).astype(np.float32)

def square(freq, duration, sr=44100):
    return np.sign(sine(freq, duration, sr))

def triangle(freq, duration, sr=44100):
    t = np.arange(int(duration * sr)) / sr
    return (2 * np.abs(2 * (t * freq % 1) - 1) - 1).astype(np.float32)

def noise(duration, sr=44100):
    return np.random.uniform(-1, 1, int(duration * sr)).astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# ENVELOPES — shape the sound over time
# ═══════════════════════════════════════════════════════════════════

def adsr(length, attack, decay, sustain, release, sr=44100):
    """Generate an ADSR envelope.

    attack, decay, release in seconds. sustain is a level (0-1).
    """
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    s_len = max(0, length - a - d - r)

    env = np.zeros(length, dtype=np.float32)
    pos = 0
    # Attack: 0 to 1
    seg = min(a, length - pos)
    if seg > 0:
        env[pos:pos+seg] = np.linspace(0, 1, seg)
        pos += seg
    # Decay: 1 to sustain
    seg = min(d, length - pos)
    if seg > 0:
        env[pos:pos+seg] = np.linspace(1, sustain, seg)
        pos += seg
    # Sustain
    s_len = max(0, length - pos - min(r, length - pos))
    if s_len > 0:
        env[pos:pos+s_len] = sustain
        pos += s_len
    # Release: sustain to 0
    seg = min(r, length - pos)
    if seg > 0:
        env[pos:pos+seg] = np.linspace(sustain, 0, seg)

    return env


def pitch_envelope(start_freq, end_freq, duration, sr=44100):
    """Frequency sweep — for kick drums and effects."""
    t = np.arange(int(duration * sr)) / sr
    freq = start_freq + (end_freq - start_freq) * np.exp(-t * 20)
    phase = np.cumsum(freq / sr) * 2 * np.pi
    return np.sin(phase).astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# FILTERS — shape the tone
# ═══════════════════════════════════════════════════════════════════

def lowpass(signal, cutoff, sr=44100):
    """Simple one-pole lowpass filter."""
    from scipy.signal import butter, sosfilt
    sos = butter(2, min(cutoff, sr/2 - 1), btype='low', fs=sr, output='sos')
    return sosfilt(sos, signal).astype(np.float32)

def highpass(signal, cutoff, sr=44100):
    from scipy.signal import butter, sosfilt
    sos = butter(2, max(cutoff, 20), btype='high', fs=sr, output='sos')
    return sosfilt(sos, signal).astype(np.float32)


# ═══════════════════════════════════════════════════════════════════
# SYNTH — subtractive synthesizer
# ═══════════════════════════════════════════════════════════════════

def midi_to_freq(note):
    """Convert MIDI note number to frequency. A4 (69) = 440Hz."""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def synth_note(note, duration, velocity=100, sr=44100,
               waveform='saw', cutoff=4000,
               attack=0.01, decay=0.1, sustain=0.7, release=0.1,
               detune=0.0):
    """Render a single synth note.

    note: MIDI note number (60 = middle C)
    duration: seconds
    velocity: 0-127
    waveform: 'sine', 'saw', 'square', 'triangle'
    cutoff: lowpass filter frequency
    """
    freq = midi_to_freq(note)
    duration = max(0.01, min(30.0, float(duration)))  # clamp duration
    n_samples = int(duration * sr)
    vel = velocity / 127.0

    # Generate oscillator
    osc_funcs = {'sine': sine, 'saw': saw, 'square': square, 'triangle': triangle}
    gen = osc_funcs.get(waveform, saw)
    osc = gen(freq, duration, sr)[:n_samples]

    # Optional detuning (chorus-like thickness)
    if detune > 0:
        osc2 = gen(freq * (1 + detune/100), duration, sr)[:n_samples]
        min_l = min(len(osc), len(osc2))
        osc = (osc[:min_l] + osc2[:min_l]) * 0.5

    # Filter
    if cutoff < sr / 2 - 100 and len(osc) > 10:
        try:
            osc = lowpass(osc, cutoff, sr)
        except Exception:
            pass  # skip filter if it fails

    # Envelope — force to exact oscillator length
    env = adsr(len(osc), attack, decay, sustain, release, sr)[:len(osc)]

    return (osc * env * vel * 0.5).astype(np.float32)


def render_synth_pattern(notes, sr=44100, bpm=120, **synth_params):
    """Render a list of notes to audio.

    notes: list of {note: int, start_beat: float, duration_beats: float, velocity: int}
    Returns stereo numpy array.
    """
    beat_sec = 60.0 / bpm

    # Find total duration
    if not notes:
        return np.zeros((sr, 2), dtype=np.float32)

    end_beat = max(n['start_beat'] + n.get('duration_beats', 1) for n in notes)
    total_samples = int((end_beat * beat_sec + 1) * sr)
    audio = np.zeros(total_samples, dtype=np.float64)

    for n in notes:
        try:
            start_sample = int(n['start_beat'] * beat_sec * sr)
            dur = n.get('duration_beats', 1) * beat_sec
            vel = n.get('velocity', 100)
            note_audio = synth_note(n['note'], dur, vel, sr, **synth_params)

            end = min(start_sample + len(note_audio), total_samples)
            if end > start_sample:
                audio[start_sample:end] += note_audio[:end - start_sample]
        except Exception:
            continue  # skip notes that fail to render

    audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
    return np.column_stack([audio, audio])  # stereo


# ═══════════════════════════════════════════════════════════════════
# DRUM MACHINE — synthesized drums from math
# ═══════════════════════════════════════════════════════════════════

def drum_kick(sr=44100, sustain_ms=200, pitch=50, punch=0.5, sub=0.5):
    """Synthesize a kick drum using modal membrane physics.

    A kick drum is a circular membrane (head) coupled to a cylindrical
    shell and an air cavity (the port). The fundamental mode of the
    membrane dominates, with the shell adding resonance character.

    Three components based on real drum physics:
    1. Beater impact: transient noise from stick/beater hitting head
    2. Membrane modes: the drum head's vibration (pitch-swept because
       the head deforms under impact then relaxes)
    3. Shell/port resonance: the body adds low-end weight
    """
    dur = max(0.1, sustain_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Component 1: Beater impact transient
    click_n = int(0.003 * sr)
    click = noise(0.003, sr) * punch * 0.5
    click = highpass(click, 2500, sr)
    click *= np.exp(-np.linspace(0, 20, click_n))

    # Component 2: Membrane — VERY fast pitch sweep (under 10ms)
    # Real kick: beater deforms head, frequency drops instantly
    # The sweep must be so fast you DON'T hear it as pitch — just "thump"
    sweep_dur = 0.008  # 8ms — inaudible as a pitch change
    sweep_n = int(sweep_dur * sr)
    sweep_t = np.linspace(0, sweep_dur, sweep_n, dtype=np.float32)
    # Exponential frequency drop: 160Hz → pitch in 8ms
    sweep_freq = pitch + (160 - pitch) * np.exp(-sweep_t * 600)
    sweep = np.sin(2 * np.pi * np.cumsum(sweep_freq / sr)) * 0.9

    # Sustained body at the fundamental — this is the "weight"
    body = sine(pitch, dur, sr)
    body_env = np.exp(-t * (5 / dur))  # decay relative to duration

    # Mode 2 (shell overtone)
    mode2_freq = pitch * 2.29
    mode2 = sine(mode2_freq, dur * 0.15, sr) * 0.1
    mode2_n = len(mode2)
    mode2_env = np.exp(-np.linspace(0, dur * 0.15, mode2_n) * 20)

    # Component 3: Sub weight — just a pure sine at fundamental
    # No separate "sub tail" — the body IS the sub

    # Mix all components
    result = np.zeros(n, dtype=np.float32)
    # Beater click — loud, first thing you hear
    result[:min(click_n, n)] += click[:min(click_n, n)]
    # Fast sweep — the initial "thump"
    result[:min(sweep_n, n)] += sweep[:min(sweep_n, n)]
    # Body — the sustained weight
    result[:n] += (body[:n] * body_env) * 0.6
    # Shell overtone — brief
    result[:min(mode2_n, n)] += (mode2[:min(mode2_n, n)] * mode2_env[:min(mode2_n, n)])

    # Lowpass — keep the beater attack (2-5kHz) while controlling sub
    # Real kicks have energy from 30Hz (sub) to 5kHz+ (beater slap)
    return lowpass(result, 8000, sr) * 0.9


def drum_snare(sr=44100, sustain_ms=200, tone_pitch=200, noise_amount=0.6, body_amount=0.4):
    """Synthesize a snare drum using modal physics + snare wire model.

    A snare has TWO heads (batter + resonant) with snare wires
    stretched across the resonant head. The wires buzz sympathetically
    when the batter head is struck, creating the characteristic rattle.

    Components:
    1. Stick impact: sharp transient
    2. Batter head modes: membrane vibration (~180-250Hz fundamental)
    3. Snare wire buzz: filtered noise excited by the head vibration
    4. Shell resonance: adds body character
    """
    dur = max(0.1, sustain_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Component 1: Stick impact
    click_n = int(0.002 * sr)
    click = noise(0.002, sr) * 0.4
    click = highpass(click, 3500, sr)
    click *= np.exp(-np.linspace(0, 25, click_n))

    # Component 2: Batter head — membrane modes
    # Fundamental + mode at ~1.59x + mode at ~2.14x (drum membrane ratios)
    head = sine(tone_pitch, dur, sr) * body_amount * 0.5
    head *= np.exp(-t * 8)
    head2 = sine(tone_pitch * 1.59, dur, sr) * body_amount * 0.2
    head2 *= np.exp(-t * 12)
    head3 = sine(tone_pitch * 2.14, dur, sr) * body_amount * 0.1
    head3 *= np.exp(-t * 16)

    # Component 3: Snare wires — the rattling buzz
    # Broadband noise filtered to snare wire frequency range (2-8kHz)
    wire_noise = noise(dur, sr) * noise_amount * 0.45
    wire_env = np.exp(-t * 6)  # wires ring longer than the head
    wire_noise *= wire_env
    wire_noise = highpass(wire_noise, 2000, sr)
    wire_noise = lowpass(wire_noise, 9000, sr)

    # Component 4: Shell body — adds mid-range character
    shell = sine(tone_pitch * 0.75, dur * 0.5, sr) * 0.15
    shell_n = len(shell)
    shell *= np.exp(-np.linspace(0, 10, shell_n))

    # Mix
    result = np.zeros(n, dtype=np.float32)
    result[:click_n] += click[:min(click_n, n)]
    result[:n] += head[:n] + head2[:n] + head3[:n]
    result[:n] += wire_noise[:n]
    result[:min(shell_n, n)] += shell[:min(shell_n, n)]

    return result.astype(np.float32)


def _cymbal_modal_bank(t, modes, sr=44100, velocity=0.8):
    """Generate cymbal sound from physically modeled inharmonic modal resonators.

    Based on Perrin/Rossing (JASA), Touze/Chaigne nonlinear plate theory,
    and DAFx cymbal synthesis research.

    Physics implemented:
    1. Close-frequency pairs for shimmer (1-8Hz beating)
    2. Frequency-dependent damping (high modes decay faster)
    3. Amplitude-dependent frequency shift (hardening nonlinearity)
    4. Proper excitation envelope (not impulse)
    5. Double-decay envelope (fast initial + slow sustain)
    6. Radiation sway modulation on high-frequency content
    7. NONLINEAR MODE COUPLING — modes exchange energy (Touze/Chaigne)
    8. STATE-DEPENDENT — spectrum evolves over time, not static

    modes: list of (freq_hz, amplitude, base_decay, jitter)
    """
    n = len(t)
    dt = t[1] - t[0] if n > 1 else 1.0 / sr
    result = np.zeros(n, dtype=np.float64)

    # Nonlinearity scales with velocity (soft=linear, hard=chaotic)
    nonlin_strength = 0.01 + velocity * 0.04

    # Radiation sway — subtle AM on high-frequency modes
    sway_freq = 1.2 + np.random.uniform(-0.3, 0.3)
    sway = 1.0 + 0.12 * np.sin(2 * np.pi * sway_freq * t)

    for freq, amp, base_decay, jitter in modes:
        # Hand-hammered detuning
        detune = 1.0 + np.random.uniform(-jitter, jitter)
        f = freq * detune

        # CREATE SHIMMER: split each mode into a close-frequency pair
        # Detuning of 1-8Hz creates the beating that IS cymbal shimmer
        pair_detune = np.random.uniform(1.0, 6.0)  # Hz
        f_a = f - pair_detune / 2
        f_b = f + pair_detune / 2
        amp_b = amp * np.random.uniform(0.5, 0.95)  # slightly different amplitude

        # FREQUENCY-DEPENDENT DAMPING
        # xi(f) = xi_0 + xi_1*f + xi_2*f^2
        # High modes decay fast, low modes ring long
        xi_0 = 0.0003
        xi_1 = 2.5e-6
        xi_2 = 1.2e-10
        damping = xi_0 + xi_1 * f + xi_2 * f * f
        decay_rate = damping * 2 * np.pi * f  # convert to amplitude decay rate

        # DOUBLE-DECAY ENVELOPE
        # Fast initial energy redistribution + slow linear decay
        nonlin_time = 0.08 + 0.12 * (1.0 - velocity)
        nonlin_factor = 1.0 - 0.4 * velocity * np.exp(-t / nonlin_time)
        env = np.exp(-t * decay_rate) * np.maximum(nonlin_factor, 0.3)

        # AMPLITUDE-DEPENDENT FREQUENCY SHIFT (hardening)
        # Pitch is slightly sharp at high amplitude, settles as it decays
        gamma = nonlin_strength * (f / 1000) ** 0.3
        pitch_shift = 1.0 + gamma * env * velocity

        # Generate the pair (shimmer from beating)
        phase_a = np.cumsum(2 * np.pi * f_a * pitch_shift * dt)
        phase_b = np.cumsum(2 * np.pi * f_b * pitch_shift * dt)

        mode_a = np.sin(phase_a) * amp * env
        mode_b = np.sin(phase_b) * amp_b * env

        # Apply sway to high-frequency modes only
        if f > 4000:
            mode_a *= sway
            mode_b *= sway

        result += mode_a + mode_b

    # ═══ NONLINEAR MODE COUPLING (Touze/Chaigne) ═══
    # Energy cascades from low modes to high modes when amplitude is high.
    # This creates the "wash" that builds up on repeated/hard hits.
    # The spectrum EVOLVES over time — it's not static.
    if velocity > 0.4 and len(modes) > 2:
        # Coupling strength scales with velocity (soft=linear, hard=chaotic)
        coupling = 0.05 + velocity * 0.15

        # Energy cascade: low-frequency energy feeds into high-frequency noise
        # This simulates wave turbulence in the cymbal plate
        cascade_delay = int(0.05 * sr)  # cascade starts ~50ms after impact
        if n > cascade_delay:
            # Measure the low-frequency energy over time
            block = min(2048, n)
            for i in range(cascade_delay, n - block, block):
                segment = result[i:i + block]
                energy = np.sqrt(np.mean(segment ** 2))

                if energy > 0.01:
                    # Generate high-frequency noise proportional to low energy
                    # This is the spectral broadening from nonlinear coupling
                    hf_noise = np.random.randn(block).astype(np.float64)
                    hf_noise *= energy * coupling * np.exp(-(i / sr) * 2.0)
                    # Bandpass to upper cymbal range
                    from scipy.signal import butter, lfilter
                    b, a = butter(2, [3000 / (sr/2), min(12000, sr/2-1) / (sr/2)], btype='band')
                    hf_noise = lfilter(b, a, hf_noise).astype(np.float64)
                    result[i:i + block] += hf_noise * 0.3

    return result.astype(np.float32)


# ═══════════════════════════════════════════════════════════════
# STATEFUL CYMBAL VOICE — hitting a ringing cymbal sums nonlinearly.
# ═══════════════════════════════════════════════════════════════
# Modes profiles extracted from the single-shot cymbal functions below.
# The voice tracks each mode's current amplitude and phase across strikes,
# so a new strike on a still-ringing cymbal adds energy with phase
# coherence and amplitude saturation — real cymbals can't exceed the
# plate's steady-state vibration.

CYMBAL_MODE_PROFILES = {
    "crash": [
        (3700, 0.03, 3.0, 0.015), (4165, 0.03, 3.5, 0.015),
        (5500, 0.03, 4.0, 0.018), (6300, 0.025, 5.0, 0.020),
        (7800, 0.02, 6.0, 0.020), (9500, 0.015, 7.0, 0.025),
    ],
    "ride": [
        (280, 0.015, 0.4, 0.005),   (482, 0.015, 0.5, 0.005),
        (731, 0.02, 0.6, 0.008),    (1025, 0.03, 0.8, 0.008),
        (1190, 0.035, 1.0, 0.010),  (1355, 0.035, 1.2, 0.010),
        (1540, 0.03, 1.5, 0.012),   (1730, 0.03, 1.8, 0.012),
        (2200, 0.03, 2.0, 0.015),   (2800, 0.025, 2.5, 0.015),
        (3500, 0.02, 3.0, 0.018),   (4500, 0.015, 4.0, 0.020),
        (5800, 0.01, 5.0, 0.020),   (7500, 0.008, 6.0, 0.025),
    ],
    "ride_bell": [
        (1200, 0.04, 1.0, 0.008), (1800, 0.05, 1.2, 0.008),
        (2800, 0.06, 1.5, 0.010), (3600, 0.05, 2.0, 0.012),
        (4800, 0.04, 2.5, 0.015), (6200, 0.03, 3.0, 0.015),
    ],
    "hihat_open": [
        (380, 0.04, 3.0, 0.03),   (654, 0.04, 3.5, 0.03),
        (990, 0.05, 4.0, 0.04),   (1390, 0.05, 4.5, 0.04),
        (1840, 0.06, 5.0, 0.05),  (2500, 0.06, 5.5, 0.05),
        (3200, 0.06, 6.0, 0.06),  (4100, 0.05, 7.0, 0.06),
        (5300, 0.04, 8.0, 0.07),  (6800, 0.04, 9.0, 0.07),
        (8500, 0.03, 10.0, 0.08), (10500, 0.02, 12.0, 0.08),
    ],
    "splash": [
        (4500, 0.03, 6.0, 0.015), (6000, 0.03, 7.0, 0.018),
        (8000, 0.02, 8.0, 0.020), (10000, 0.015, 10.0, 0.025),
    ],
    "china": [
        (850, 0.04, 1.5, 0.07),   (1200, 0.05, 1.8, 0.08),
        (1600, 0.05, 2.0, 0.08),  (2100, 0.04, 2.5, 0.09),
        (2800, 0.035, 3.0, 0.09), (3500, 0.03, 3.5, 0.10),
        (4500, 0.025, 4.0, 0.10), (5800, 0.02, 5.0, 0.10),
        (7500, 0.015, 6.0, 0.10),
    ],
}

# Sound names that route through the stateful cymbal voice.
# Stateful = carries mode amplitude and phase from hit to hit.
CYMBAL_STATEFUL_SOUNDS = {
    "crash":       ("crash", 2.5),
    "ride":        ("ride", 3.0),
    "ride_bell":   ("ride_bell", 1.5),
    "hihat_open":  ("hihat_open", 0.8),
    "china":       ("china", 1.5),
    "splash":      ("splash", 0.6),
}


class CymbalVoice:
    """A single cymbal that remembers it is still vibrating.

    Each strike adds energy to the existing modal state with saturating
    nonlinearity (a ringing plate resists further excitation) and phase
    coherence (so a well-timed second hit can reinforce or cancel).
    """

    def __init__(self, profile_name, sr=44100):
        modes_raw = CYMBAL_MODE_PROFILES[profile_name]
        self.sr = sr
        self.modes = []
        for freq, amp, _base_decay, jitter in modes_raw:
            # Detune each mode once (hand-hammered) — stays constant per voice
            f = freq * (1.0 + np.random.uniform(-jitter, jitter))
            damping = 0.0003 + 2.5e-6 * f + 1.2e-10 * f * f
            decay_rate = damping * 2 * np.pi * f
            # Shimmer: split each mode into a close-frequency pair
            pair_detune = np.random.uniform(1.0, 6.0)
            self.modes.append({
                "f_a": f - pair_detune / 2,
                "f_b": f + pair_detune / 2,
                "max_amp_a": amp,
                "max_amp_b": amp * np.random.uniform(0.5, 0.95),
                "amp_a": 0.0,
                "amp_b": 0.0,
                "phase_a": np.random.uniform(0, 2 * np.pi),
                "phase_b": np.random.uniform(0, 2 * np.pi),
                "decay_rate": decay_rate,
            })

    def strike(self, velocity):
        """Inject a strike. The new excitation sums nonlinearly with whatever
        amplitude is currently in each mode. Returns immediately — call
        render_interval() to get audio between strikes."""
        for m in self.modes:
            # Saturating sum: if a mode is already at max, a strike adds almost nothing
            cur_a = m["amp_a"]
            cur_b = m["amp_b"]
            headroom_a = max(0.0, 1.0 - cur_a / max(m["max_amp_a"] * 1.2, 1e-6))
            headroom_b = max(0.0, 1.0 - cur_b / max(m["max_amp_b"] * 1.2, 1e-6))
            add_a = m["max_amp_a"] * velocity * headroom_a
            add_b = m["max_amp_b"] * velocity * headroom_b
            m["amp_a"] = min(m["max_amp_a"] * 1.2, cur_a + add_a)
            m["amp_b"] = min(m["max_amp_b"] * 1.2, cur_b + add_b)

    def render_interval(self, samples):
        """Render `samples` of audio at the current state, then advance the state."""
        if samples <= 0:
            return np.zeros(0, dtype=np.float32)
        dt = 1.0 / self.sr
        t = np.arange(samples) * dt
        out = np.zeros(samples, dtype=np.float64)
        any_audible = False
        for m in self.modes:
            if m["amp_a"] < 1e-5 and m["amp_b"] < 1e-5:
                continue
            any_audible = True
            env_a = m["amp_a"] * np.exp(-m["decay_rate"] * t)
            env_b = m["amp_b"] * np.exp(-m["decay_rate"] * t)
            phase_a = m["phase_a"] + 2 * np.pi * m["f_a"] * t
            phase_b = m["phase_b"] + 2 * np.pi * m["f_b"] * t
            out += np.sin(phase_a) * env_a + np.sin(phase_b) * env_b
            # Advance stored state to end of window
            m["amp_a"] = env_a[-1] if samples > 0 else m["amp_a"]
            m["amp_b"] = env_b[-1] if samples > 0 else m["amp_b"]
            m["phase_a"] = (phase_a[-1]) % (2 * np.pi)
            m["phase_b"] = (phase_b[-1]) % (2 * np.pi)
        if not any_audible:
            return np.zeros(samples, dtype=np.float32)
        return out.astype(np.float32)


def render_cymbal_voice_pattern(profile_name, hits, total_samples, sr=44100):
    """Render an entire pattern of hits on a single stateful cymbal.

    `hits` is a list of (sample_position, velocity) sorted by position.
    Returns a mono signal of length `total_samples`.
    """
    voice = CymbalVoice(profile_name, sr=sr)
    out = np.zeros(total_samples, dtype=np.float32)
    cursor = 0
    for pos, vel in sorted(hits, key=lambda h: h[0]):
        pos = max(0, min(int(pos), total_samples))
        # Render the silence (actually, decaying state) up to the strike time
        if pos > cursor:
            chunk = voice.render_interval(pos - cursor)
            out[cursor:cursor + len(chunk)] += chunk
            cursor = pos
        # Inject the new strike — modifies state, no output yet
        voice.strike(float(vel))
        # Add an explosive noise transient at the strike point so the attack
        # still sounds like a real cymbal hit, not just pure tone
        attack_n = min(int(0.005 * sr), total_samples - pos)
        if attack_n > 0:
            attack = np.random.randn(attack_n).astype(np.float32) * 0.15 * float(vel)
            attack *= np.exp(-np.linspace(0, 15, attack_n))
            # Bandpass the attack to match cymbal brightness
            from scipy.signal import butter, lfilter as _lf
            b, a = butter(2, [1500 / (sr / 2), min(13000 / (sr / 2), 0.99)], btype='band')
            attack = _lf(b, a, attack).astype(np.float32)
            out[pos:pos + attack_n] += attack
    # Tail: render remaining samples of decay
    if cursor < total_samples:
        chunk = voice.render_interval(total_samples - cursor)
        out[cursor:cursor + len(chunk)] += chunk
    return out


def drum_hihat_closed(sr=44100, decay_ms=50, brightness=0.7):
    """Closed hi-hat — 13-14" B20 bronze cymbals pressed together.

    Research (JASA, Rossing): Two cymbals pressed = massive inter-plate
    damping. Air coupling kills low modes. Sound is broadband transient
    concentrated at 2-5kHz with Q factors of 5-15 (extremely damped).
    Total duration 150-300ms. Fundamental ~300-500Hz but heavily damped.
    """
    dur = max(0.02, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Modal bank — heavily damped (low Q from inter-plate contact)
    # Fundamental ~400Hz but modes are damped so fast they're barely tonal
    modes = [
        (400, 0.03, 40, 0.03),    # (2,0) fundamental — heavily damped
        (688, 0.03, 35, 0.03),    # (3,0)
        (1044, 0.04, 30, 0.04),   # (4,0)
        (1464, 0.04, 25, 0.04),   # (5,0)
        (1936, 0.05, 22, 0.05),   # (6,0)
        (2800, 0.06, 20, 0.05),   # higher modes — dominate the "chick"
        (3600, 0.06, 18, 0.06),
        (4500, 0.05, 16, 0.06),
        (5800, 0.04, 14, 0.07),
        (7200, 0.03, 12, 0.07),
    ]
    metal = _cymbal_modal_bank(t, modes, sr)

    # Broadband noise — the "chick" transient
    nz = noise(dur, sr) * 0.35
    b, a = butter(2, [2000 / (sr / 2), 10000 / (sr / 2)], btype='band')
    nz = lfilter(b, a, nz).astype(np.float32)
    nz *= np.exp(-t * (800 / max(decay_ms, 10)))  # very fast noise decay

    # Stick impact transient
    attack_n = int(0.0005 * sr)
    attack = np.random.randn(min(attack_n, n)).astype(np.float32) * 0.2
    attack *= np.linspace(1, 0, len(attack))

    result = np.zeros(n, dtype=np.float32)
    result[:len(attack)] += attack
    result += metal + nz

    # Overall envelope — tight
    env = np.exp(-t * (1000 / max(decay_ms, 10)))
    return (result * env * brightness * 0.4).astype(np.float32)


def drum_hihat_open(sr=44100, decay_ms=800, brightness=0.7):
    """Open hi-hat — 13-14" cymbals separated, ringing freely.

    Research: Separated cymbals have Q factors of 50-200. Two plates
    vibrate independently with air coupling creating beating.
    Duration 1-3 seconds. Full spectrum from 300Hz to 15kHz+.
    The "sizzle" is broadband from chaotic high-frequency modes.
    """
    dur = max(0.3, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Modal bank — higher Q than closed (cymbals ringing freely)
    modes = [
        (380, 0.04, 3.0, 0.03),   # (2,0) — now audible
        (654, 0.04, 3.5, 0.03),   # (3,0)
        (990, 0.05, 4.0, 0.04),   # (4,0)
        (1390, 0.05, 4.5, 0.04),  # (5,0)
        (1840, 0.06, 5.0, 0.05),  # (6,0)
        (2500, 0.06, 5.5, 0.05),  # higher modes
        (3200, 0.06, 6.0, 0.06),
        (4100, 0.05, 7.0, 0.06),  # "sizzle" region
        (5300, 0.04, 8.0, 0.07),
        (6800, 0.04, 9.0, 0.07),
        (8500, 0.03, 10.0, 0.08),
        (10500, 0.02, 12.0, 0.08),
    ]
    metal = _cymbal_modal_bank(t, modes, sr)

    # Beating between closely-spaced modes (two cymbals interfering)
    beat1 = np.sin(2 * np.pi * 3180 * t) * 0.03 * np.exp(-t * 5)
    beat2 = np.sin(2 * np.pi * 3220 * t) * 0.03 * np.exp(-t * 5)
    beating = beat1 + beat2  # creates ~40Hz amplitude modulation

    # Broadband wash — sustained noise from unresolved high modes
    wash = noise(dur, sr) * 0.15
    b, a = butter(2, [1500 / (sr / 2), 12000 / (sr / 2)], btype='band')
    wash = lfilter(b, a, wash).astype(np.float32)
    wash *= np.exp(-t * 2.5)

    # Stick impact
    attack_n = int(0.001 * sr)
    attack = np.random.randn(min(attack_n, n)).astype(np.float32) * 0.15
    attack *= np.linspace(1, 0, len(attack))

    result = np.zeros(n, dtype=np.float32)
    result[:len(attack)] += attack
    result += metal + beating + wash

    env = np.exp(-t * (3 / max(dur, 0.1)))
    return (result * env * brightness * 0.4).astype(np.float32)


def drum_hihat_pedal(sr=44100):
    """Hi-hat pedal/foot chick — closing motion creates air burst.

    Research: 30-100ms total. Pure transient — brief air compression
    between plates plus very short contact ring. Almost no sustain.
    Dominant energy 2-6kHz.
    """
    dur = 0.06
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Air compression pop — louder for audibility
    pop = noise(0.008, sr) * 0.8
    pop_n = len(pop)
    b, a = butter(2, [2000 / (sr / 2), 8000 / (sr / 2)], btype='band')
    pop = lfilter(b, a, pop).astype(np.float32)
    pop *= np.exp(-np.linspace(0, 15, pop_n))

    # Brief contact ring — stronger
    ring = np.sin(2 * np.pi * 3500 * t[:int(0.02 * sr)]) * 0.2
    ring *= np.exp(-np.linspace(0, 25, len(ring)))

    # Metallic click
    click_n = int(0.001 * sr)
    click = np.random.randn(min(click_n, n)).astype(np.float32) * 0.3
    click *= np.linspace(1, 0, len(click))

    result = np.zeros(n, dtype=np.float32)
    result[:len(click)] += click
    result[:pop_n] += pop
    result[:len(ring)] += ring
    return result * 0.35


def drum_clap(sr=44100, spread_ms=25, decay_ms=150):
    """Synthesize a clap — layered noise bursts with room character.

    Research: multiple short noise bursts 5-25ms apart, bandpass filtered,
    with a reverb tail for room ambience.
    """
    dur = max(0.08, (spread_ms + decay_ms) / 1000)
    n = int(dur * sr)
    clap = np.zeros(n, dtype=np.float32)

    # Multiple noise bursts — simulates multiple hands
    num_bursts = 4
    for i in range(num_bursts):
        offset = int(i * (spread_ms / num_bursts) / 1000 * sr)
        burst_dur = 0.008 + i * 0.002  # each burst slightly longer
        burst = noise(burst_dur, sr) * (0.3 + i * 0.05)
        burst = highpass(burst, 1000, sr)
        end = min(offset + len(burst), n)
        clap[offset:end] += burst[:end - offset]

    # Decay envelope for the tail
    env = adsr(n, 0.001, 0.03, 0.15, decay_ms / 1000, sr)
    clap = clap * env

    # Bandpass for body (keep 800-6000Hz)
    clap = highpass(clap, 800, sr)
    return lowpass(clap, 8000, sr)


def drum_tom(pitch=100, sr=44100, sustain_ms=250, resonance=0.5):
    """Synthesize a tom — pitched membrane with resonant decay.

    Real toms: stick impact deforms the head, frequency drops in ~10ms
    (inaudible as pitch — just adds "thwack"). Then the head rings at
    the fundamental with membrane modes and shell resonance.

    Research: membrane mode ratios (1,1)=1.59, (2,1)=2.14, (0,2)=2.30
    """
    dur = max(0.1, sustain_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Stick impact — short broadband transient
    attack_n = int(0.003 * sr)
    attack = np.random.randn(min(attack_n, n)).astype(np.float32) * 0.3
    attack *= np.exp(-np.linspace(0, 20, len(attack)))

    # Fast pitch sweep — 10ms, inaudible as pitch change (just "thwack")
    sweep_dur = 0.010
    sweep_n = min(int(sweep_dur * sr), n)
    sweep_t = np.linspace(0, sweep_dur, sweep_n, dtype=np.float32)
    sweep_freq = pitch + (pitch * 0.5) * np.exp(-sweep_t * 500)
    sweep = np.sin(2 * np.pi * np.cumsum(sweep_freq / sr)) * 0.5
    sweep *= np.exp(-sweep_t * 80)

    # Fundamental — the sustained note of the tom
    body = np.sin(2 * np.pi * pitch * t) * 0.5
    body *= np.exp(-t * (4.0 / max(dur, 0.05)))

    # Membrane mode 2 — ratio 1.59
    mode2 = np.sin(2 * np.pi * pitch * 1.59 * t) * 0.15
    mode2 *= np.exp(-t * 8)

    # Membrane mode 3 — ratio 2.14
    mode3 = np.sin(2 * np.pi * pitch * 2.14 * t) * 0.08
    mode3 *= np.exp(-t * 12)

    # Shell resonance — adds warmth
    shell = np.sin(2 * np.pi * pitch * 0.75 * t) * resonance * 0.1
    shell *= np.exp(-t * 6)

    result = np.zeros(n, dtype=np.float32)
    result[:len(attack)] += attack[:min(len(attack), n)]
    result[:sweep_n] += sweep.astype(np.float32)
    result += body + mode2 + mode3 + shell

    return result.astype(np.float32)


def drum_rim(sr=44100):
    """Synthesize a rim shot / cross-stick — two distinct sounds.

    Cross-stick (laying stick across head, clicking rim): dry, woody "tick"
    used in jazz, bossa, reggae. Higher pitched, very short.

    Research: the cross-stick sound comes from the stick vibrating against
    the head and rim simultaneously. Fundamental ~800-1200Hz with
    a sharp transient and quick decay.
    """
    dur = 0.08
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Sharp stick crack — the initial transient
    crack_n = int(0.002 * sr)
    crack = noise(0.002, sr) * 0.5
    crack = highpass(crack, 2000, sr)
    crack *= np.exp(-np.linspace(0, 30, crack_n))

    # Wood tone — the stick vibrating on the head
    wood = sine(950, dur, sr) * 0.35
    wood += sine(1400, dur, sr) * 0.15  # overtone
    wood *= np.exp(-t * 30)  # very fast decay

    # Rim ring — metallic ping from the metal rim
    ring = sine(2400, dur, sr) * 0.12
    ring += sine(3600, dur, sr) * 0.06
    ring *= np.exp(-t * 20)

    # Head resonance — very subtle low thump from head vibrating
    head = sine(280, dur * 0.3, sr) * 0.08
    head_n = len(head)
    head *= np.exp(-np.linspace(0, 15, head_n))

    result = np.zeros(n, dtype=np.float32)
    result[:crack_n] += crack[:min(crack_n, n)]
    result += wood + ring
    result[:head_n] += head

    return result.astype(np.float32)


def drum_crash(sr=44100, decay_ms=2500):
    """Crash cymbal — 16-18" thin B20 bronze.

    Key insight: cymbals are NOISE-DOMINANT instruments. The modal content
    adds subtle pitch/color but the sound is primarily shaped noise.
    Low modes decay fast and are quiet. High modes and noise dominate.
    """
    dur = max(1.0, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Modal content — subtle, high-frequency dominant, fast low-mode decay
    modes = [
        (3700, 0.03, 3.0, 0.015),   # measured peak
        (4165, 0.03, 3.5, 0.015),   # measured peak
        (5500, 0.03, 4.0, 0.018),   # measured peak
        (6300, 0.025, 5.0, 0.020),
        (7800, 0.02, 6.0, 0.020),
        (9500, 0.015, 7.0, 0.025),
    ]
    metal = _cymbal_modal_bank(t, modes, sr)

    # PRIMARY: Broadband noise shaped by cymbal resonance
    # This is the actual crash sound — noise filtered through bronze character
    nz = noise(dur, sr) * 0.30
    b, a = butter(2, [800 / (sr / 2), 13000 / (sr / 2)], btype='band')
    nz = lfilter(b, a, nz).astype(np.float32)
    nz *= np.exp(-t * 1.5)

    # Shimmer cascade — builds after impact
    cascade_env = np.minimum(t / 0.1, 1.0) * np.exp(-t * 2.0)
    shimmer = noise(dur, sr) * 0.15
    b, a = butter(2, [4000 / (sr / 2), 14000 / (sr / 2)], btype='band')
    shimmer = lfilter(b, a, shimmer).astype(np.float32) * cascade_env

    # Explosive attack
    attack_n = int(0.005 * sr)
    attack = np.random.randn(min(attack_n, n)).astype(np.float32) * 0.4
    attack *= np.exp(-np.linspace(0, 15, len(attack)))

    result = np.zeros(n, dtype=np.float32)
    result[:len(attack)] += attack
    result += nz + shimmer + metal * 0.5

    return (result * 0.35).astype(np.float32)


def drum_ride(sr=44100, decay_ms=3000, bell=False):
    """Ride cymbal — 20-22" heavy B20 bronze. Bow or bell strike.

    Research (Rossing, JASA): Thicker than crash = higher Q modes = more
    "ping" definition. Bow strike excites full mode spectrum (washy).
    Bell strike excites only radially symmetric modes (focused, cutting).

    Bow: ping 50-200ms, wash 2-6s, LF sustain 5-12s
    Bell: ring 1-3s, very little wash

    "Pingy" rides: Q=100-500 (peaks rise 15-25dB above noise floor)
    "Washy" rides: Q=20-80 (modes buried in noise)
    """
    dur = max(1.0, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    f0 = 280  # fundamental for 21" ride

    if bell:
        # Bell strike — the dome has its own mode structure
        # Focused, cutting, but still rings with sustain
        bell_modes = [
            (1200, 0.04, 1.0, 0.008),   # bell fundamental — rings clearly
            (1800, 0.05, 1.2, 0.008),
            (2800, 0.06, 1.5, 0.010),   # dominant bell tone
            (3600, 0.05, 2.0, 0.012),
            (4800, 0.04, 2.5, 0.015),
            (6200, 0.03, 3.0, 0.015),
        ]
        metal = _cymbal_modal_bank(t, bell_modes, sr)

        # Sharp metallic tick
        tick_n = int(0.002 * sr)
        tick = np.random.randn(min(tick_n, n)).astype(np.float32) * 0.25
        tick *= np.linspace(1, 0, len(tick))

        result = np.zeros(n, dtype=np.float32)
        result[:len(tick)] += tick
        result += metal
        return (result * 0.4).astype(np.float32)

    # Bow strike — dense modal bank creates the sustained ring
    # Ride is THICK bronze — modes ring long (5-12s), high Q = "pingy"
    # Low modes give body, mid modes give ping, high modes give shimmer
    f0 = 280
    bow_modes = [
        # Body (felt, not heard distinctly — gives warmth)
        (f0 * 1.00, 0.015, 0.4, 0.005),   # (2,0) very long ring
        (f0 * 1.72, 0.015, 0.5, 0.005),   # (3,0)
        (f0 * 2.61, 0.02, 0.6, 0.008),    # (4,0)
        # Ping region (1-3kHz — this is what you HEAR as the ride)
        (f0 * 3.66, 0.03, 0.8, 0.008),    # (5,0) ~1025Hz
        (f0 * 4.25, 0.035, 1.0, 0.010),   # (0,1) ~1190Hz
        (f0 * 4.84, 0.035, 1.2, 0.010),   # (6,0) ~1355Hz
        (f0 * 5.50, 0.03, 1.5, 0.012),    # (1,1) ~1540Hz
        (f0 * 6.18, 0.03, 1.8, 0.012),    # (7,0) ~1730Hz
        (2200, 0.03, 2.0, 0.015),
        (2800, 0.025, 2.5, 0.015),
        (3500, 0.02, 3.0, 0.018),
        # Shimmer (high — adds air and presence)
        (4500, 0.015, 4.0, 0.020),
        (5800, 0.01, 5.0, 0.020),
        (7500, 0.008, 6.0, 0.025),
    ]
    metal = _cymbal_modal_bank(t, bow_modes, sr)

    # Wash — noise representing unresolved dense upper modes
    wash = noise(dur, sr) * 0.06
    b, a = butter(2, [1000 / (sr / 2), 8000 / (sr / 2)], btype='band')
    wash = lfilter(b, a, wash).astype(np.float32)
    wash *= np.exp(-t * 0.8)  # slow decay — ride wash rings long

    # Stick tip "tick" — short broadband click
    tick_n = int(0.002 * sr)
    tick = np.random.randn(min(tick_n, n)).astype(np.float32) * 0.2
    tick *= np.linspace(1, 0, len(tick))

    result = np.zeros(n, dtype=np.float32)
    result[:len(tick)] += tick
    result += metal + wash

    return (result * 0.4).astype(np.float32)


def drum_splash(sr=44100, decay_ms=600):
    """Splash cymbal — 10" thin B20 bronze. Fast attack, quick decay.

    Research: Small diameter + thin = high fundamental (~600Hz),
    fast decay (300-1500ms total). Fewer modes than crash.
    Quick broadband burst that dies fast.
    """
    dur = max(0.3, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Splash: quick noise burst, high-pitched, fast decay
    modes = [
        (4500, 0.03, 6.0, 0.015),
        (6000, 0.03, 7.0, 0.018),
        (8000, 0.02, 8.0, 0.020),
        (10000, 0.015, 10.0, 0.025),
    ]
    metal = _cymbal_modal_bank(t, modes, sr)

    # Quick broadband burst — the splash IS this
    nz = noise(dur, sr) * 0.25
    b, a = butter(2, [2500 / (sr / 2), 13000 / (sr / 2)], btype='band')
    nz = lfilter(b, a, nz).astype(np.float32)
    nz *= np.exp(-t * 5.0)  # fast decay

    # Sharp attack
    burst_n = int(0.003 * sr)
    burst = np.random.randn(min(burst_n, n)).astype(np.float32) * 0.3
    burst *= np.exp(-np.linspace(0, 20, len(burst)))

    result = np.zeros(n, dtype=np.float32)
    result[:len(burst)] += burst
    result += nz + metal * 0.4
    return (result * 0.35).astype(np.float32)


def drum_china(sr=44100, decay_ms=1500):
    """China cymbal — 18" flanged edge, trashy/aggressive.

    Research: Upturned edge breaks radial symmetry. Rapid energy
    dissipation. Strong midrange "gurgle" 800-2000Hz. Fast decay
    (1-3s). Incoherent mode patterns from flange geometry.
    Mode frequency jitter is HIGH (5-10%) — irregular hammering.
    """
    dur = max(0.5, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # China: modes ring with trashy character from flange geometry
    # The flange breaks symmetry — modes have HIGH jitter (5-10%)
    # Strong midrange "gurgle" (800-2000Hz) is the china signature
    # On a kit this rings freely for 1-3 seconds
    modes = [
        # Midrange gurgle — the china's voice
        (850, 0.04, 1.5, 0.07),     # sustained ring
        (1200, 0.05, 1.8, 0.08),    # gurgle center
        (1600, 0.05, 2.0, 0.08),
        (2100, 0.04, 2.5, 0.09),
        # Upper harmonics — trashy edge
        (2800, 0.035, 3.0, 0.09),
        (3500, 0.03, 3.5, 0.10),
        (4500, 0.025, 4.0, 0.10),
        (5800, 0.02, 5.0, 0.10),
        (7500, 0.015, 6.0, 0.10),
    ]
    metal = _cymbal_modal_bank(t, modes, sr)

    # Trashy noise — present but doesn't dominate the ring
    trash = noise(dur, sr) * 0.12
    b, a = butter(2, [800 / (sr / 2), 10000 / (sr / 2)], btype='band')
    trash = lfilter(b, a, trash).astype(np.float32)
    trash *= np.exp(-t * 1.5)  # decays with the ring, not before

    # Aggressive attack
    attack_n = int(0.005 * sr)
    attack = np.random.randn(min(attack_n, n)).astype(np.float32) * 0.3
    attack *= np.exp(-np.linspace(0, 10, len(attack)))

    result = np.zeros(n, dtype=np.float32)
    result[:len(attack)] += attack
    result += metal + trash
    return (result * 0.35).astype(np.float32)


def drum_shaker(sr=44100):
    """Synthesize a shaker — rhythmic filtered noise."""
    dur = 0.08
    n = int(dur * sr)
    nz = noise(dur, sr) * 0.25
    env = adsr(n, 0.002, 0.02, 0.2, 0.03, sr)
    return highpass(nz * env, 6000, sr)


def drum_cowbell(sr=44100):
    """Synthesize a cowbell — two detuned square waves."""
    dur = 0.15
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)
    # Two slightly detuned tones (classic 808 cowbell)
    tone1 = np.sign(np.sin(2 * np.pi * 560 * t)) * 0.2
    tone2 = np.sign(np.sin(2 * np.pi * 845 * t)) * 0.2
    env = adsr(n, 0.0005, 0.02, 0.3, 0.08, sr)
    return ((tone1 + tone2) * env * 0.3).astype(np.float32)


def drum_double_kick(sr=44100):
    """Double bass drum — alternating left/right foot.

    Each hit is slightly different (human imprecision).
    The two hits overlap — second beater contacts before first decay.
    Returned mono for compatibility with render_drum_pattern mixing; the
    stereo placement is applied at mix time (left foot ~−0.25, right foot ~+0.25).
    Used in metal, prog, and fusion at high tempos (160-220+ BPM).
    """
    # Two kicks with slight timing, pitch, punch, and sub variation
    # — the left foot is fractionally weaker (most drummers have a dominant right)
    kick1 = drum_kick(sr, sustain_ms=150, pitch=48, punch=0.5, sub=0.4)
    kick2 = drum_kick(sr, sustain_ms=140, pitch=50, punch=0.45, sub=0.35)

    # Offset: second kick comes ~60ms after first (typical double bass gap)
    gap = int(0.06 * sr)
    total = max(len(kick1), gap + len(kick2))
    result = np.zeros(total, dtype=np.float32)
    result[:len(kick1)] += kick1 * 0.9
    result[gap:gap + len(kick2)] += kick2 * 0.85  # second hit slightly softer

    return result


# Default stereo placement per instrument (drummer's perspective)
# -1.0 = hard left, 0 = center, +1.0 = hard right
DRUM_PANS = {
    'kick': 0.0,
    'double_kick': 0.0,      # stereo split handled specially in render
    'snare': 0.0,
    'hihat': 0.35,           # hats right of drummer
    'hihat_open': 0.35,
    'hihat_pedal': 0.35,
    'clap': 0.0,
    'tom_high': -0.35,       # rack toms left → right
    'tom_mid': -0.10,
    'tom_low': 0.20,          # floor tom right
    'rim': 0.0,
    'crash': -0.55,           # crash cymbal upper-left
    'ride': 0.50,             # ride cymbal upper-right
    'ride_bell': 0.50,
    'splash': -0.65,
    'china': 0.65,
    'shaker': 0.15,
    'cowbell': -0.20,
}


# All available drum sounds
DRUM_SOUNDS = {
    'kick': drum_kick,
    'double_kick': drum_double_kick,
    'snare': drum_snare,
    'hihat': drum_hihat_closed,
    'hihat_open': drum_hihat_open,
    'hihat_pedal': drum_hihat_pedal,
    'clap': drum_clap,
    'tom_high': lambda sr=44100: drum_tom(150, sr),
    'tom_mid': lambda sr=44100: drum_tom(100, sr),
    'tom_low': lambda sr=44100: drum_tom(70, sr),
    'rim': drum_rim,
    'crash': drum_crash,
    'ride': drum_ride,
    'ride_bell': lambda sr=44100: drum_ride(sr, bell=True),
    'splash': drum_splash,
    'china': drum_china,
    'shaker': drum_shaker,
    'cowbell': drum_cowbell,
}


def render_sampler_note(sample_path, root_midi=60, target_midi=60, duration=1.0,
                         velocity=100, attack_ms=5, decay_ms=50, sustain=0.8, release_ms=150,
                         loop=False, sr=44100):
    """Render a pitch-shifted sample with an ADSR envelope.

    Basic multi-sample-instrument primitive: load a sample, resample by the pitch
    ratio, optionally loop to fill `duration`, apply ADSR + velocity gain.

    sample_path: WAV/FLAC/MP3 file.
    root_midi:   the MIDI note the sample was recorded at (default C4 = 60)
    target_midi: the MIDI note we want played. Pitch ratio = 2^((target-root)/12)
    duration:    seconds of output
    velocity:    0-127
    attack/decay/release: milliseconds
    sustain:     0-1, level after the decay stage
    loop:        if True, repeat the sample to fill duration
    """
    import numpy as np
    import soundfile as _sf
    from scipy.signal import resample_poly

    # Load
    data, src_sr = _sf.read(str(sample_path))
    if data.ndim > 1:
        data = data.mean(axis=1)  # mono for simplicity
    # Resample to the project sr if different
    if src_sr != sr:
        # Keep it simple with resample_poly rational ratio
        from math import gcd
        g = gcd(src_sr, sr)
        data = resample_poly(data, sr // g, src_sr // g)

    # Pitch-shift by resampling: target sample count = original / ratio
    semitones = target_midi - root_midi
    ratio = 2 ** (semitones / 12.0)
    if abs(ratio - 1.0) > 1e-6:
        # New length = original / ratio  (higher pitch → shorter)
        new_len = max(1, int(len(data) / ratio))
        # Use simple linear interpolation for speed; quality is fine for modest shifts
        idx = np.linspace(0, len(data) - 1, new_len)
        data = np.interp(idx, np.arange(len(data)), data).astype(np.float32)

    # Fill/truncate to duration
    target_samples = int(duration * sr)
    if target_samples <= 0:
        return np.zeros(0, dtype=np.float32)
    if len(data) < target_samples:
        if loop and len(data) > 0:
            # Repeat to fill
            reps = (target_samples // len(data)) + 1
            data = np.tile(data, reps)[:target_samples]
        else:
            # Pad with silence
            pad = np.zeros(target_samples - len(data), dtype=np.float32)
            data = np.concatenate([data, pad])
    else:
        data = data[:target_samples]

    # ADSR envelope
    a = int((attack_ms / 1000) * sr)
    d = int((decay_ms / 1000) * sr)
    r = int((release_ms / 1000) * sr)
    n = len(data)
    env = np.ones(n, dtype=np.float32)
    # Attack
    if a > 0 and a < n:
        env[:a] = np.linspace(0, 1, a)
    elif a >= n:
        env[:] = np.linspace(0, 1, n)
    # Decay to sustain
    if d > 0 and a + d < n:
        env[a:a + d] = np.linspace(1, sustain, d)
    # Sustain stays at `sustain` until release begins
    release_start = max(a + d, n - r)
    if a + d < release_start:
        env[a + d:release_start] = sustain
    # Release
    if r > 0:
        env[release_start:] = np.linspace(env[release_start - 1] if release_start > 0 else sustain, 0, n - release_start)

    # Velocity-scale amplitude
    amp = velocity / 127.0
    return (data * env * amp).astype(np.float32)


def render_sampler_pattern(sample_path, notes, root_midi=60, bpm=120,
                            attack_ms=5, decay_ms=50, sustain=0.8, release_ms=150,
                            loop=False, sr=44100):
    """Render a list of MIDI notes through a sampler.

    notes: list of {midi, beat, duration (beats), velocity}
    """
    import numpy as np
    beat_sec = 60.0 / bpm
    if not notes:
        return np.zeros(sr, dtype=np.float32)
    end_beat = max(n.get("beat", 0) + n.get("duration", 1) for n in notes) + 1
    total_samples = int(end_beat * beat_sec * sr)
    out = np.zeros(total_samples, dtype=np.float32)
    for note in notes:
        midi = int(note.get("midi", 60))
        beat = float(note.get("beat", 0))
        dur_beats = float(note.get("duration", 1))
        vel = int(note.get("velocity", 100))
        dur_sec = dur_beats * beat_sec
        audio = render_sampler_note(sample_path, root_midi=root_midi,
                                    target_midi=midi, duration=dur_sec,
                                    velocity=vel, attack_ms=attack_ms,
                                    decay_ms=decay_ms, sustain=sustain,
                                    release_ms=release_ms, loop=loop, sr=sr)
        start = int(beat * beat_sec * sr)
        end = min(start + len(audio), total_samples)
        out[start:end] += audio[:end - start]
    # Soft-clip to prevent blow-up
    import numpy as _np
    peak = _np.max(_np.abs(out))
    if peak > 1.0:
        out = out / peak * 0.95
    return out


def render_drum_pattern(pattern, sr=44100, bpm=120):
    """Render a drum pattern to audio.

    pattern: list of {sound: str, beat: float, velocity: float (0-1)}
    Returns stereo numpy array. Snaps to exact bar boundary with fade-out.
    """
    beat_sec = 60.0 / bpm

    if not pattern:
        return np.zeros((sr, 2), dtype=np.float32)

    # Snap end to bar boundary (4 beats per bar)
    max_beat = max(p['beat'] for p in pattern)
    end_bar = int(max_beat / 4) + 1  # next bar after last hit
    end_beat = end_bar * 4
    # Add a tiny tail for the last hit's decay (but not full cymbal ring)
    total_samples = int(end_beat * beat_sec * sr)
    # Stereo accumulator so per-kit-piece pans land correctly
    stereo_out = np.zeros((total_samples, 2), dtype=np.float64)
    # Alternating counter for double_kick L/R
    double_kick_flip = 0

    # ─── STATEFUL CYMBAL VOICES ───────────────────────────────────
    # Collect hits on stateful cymbal sounds, render each as a single
    # voice that remembers it was already ringing when the next strike
    # arrives. This is what makes closely-spaced crash/ride/china hits
    # sound physically right instead of like re-triggered samples.
    cymbal_buckets = {}  # sound_name -> list of (sample_position, velocity)
    for hit in pattern:
        sn = hit.get('sound', 'kick')
        if sn in CYMBAL_STATEFUL_SOUNDS:
            beat = hit.get('beat', 0)
            vel = hit.get('velocity', 0.8)
            pos = int(beat * beat_sec * sr) + int(np.random.uniform(-0.0005, 0.0005) * sr)
            cymbal_buckets.setdefault(sn, []).append((pos, vel))

    for sn, hits in cymbal_buckets.items():
        profile_name, _norm_factor = CYMBAL_STATEFUL_SOUNDS[sn]
        mono = render_cymbal_voice_pattern(profile_name, hits, total_samples, sr=sr)
        # Normalize and pan — per-instrument pan comes from DRUM_PANS
        peak = np.max(np.abs(mono)) if mono.size else 0.0
        if peak > 0.01:
            mono = mono / peak * 0.55
        pan = DRUM_PANS.get(sn, 0.0)
        pan_angle = (float(pan) + 1.0) * np.pi / 4.0
        stereo_out[:, 0] += mono * np.cos(pan_angle)
        stereo_out[:, 1] += mono * np.sin(pan_angle)

    # Cache rendered drum sounds — normalize to prevent clipping
    cache = {}

    for hit in pattern:
        sound_name = hit.get('sound', 'kick')
        beat = hit.get('beat', 0)
        vel = hit.get('velocity', 0.8)

        # Skip cymbals already handled by the stateful voice above
        if sound_name in CYMBAL_STATEFUL_SOUNDS:
            continue

        if sound_name not in cache:
            gen = DRUM_SOUNDS.get(sound_name)
            if gen:
                s = gen(sr).astype(np.float64)
                # Remove DC offset
                s -= np.mean(s)
                # Normalize to 0.8 peak (prevents clipping when layered)
                peak = np.max(np.abs(s))
                if peak > 0.01:
                    s = s / peak * 0.8
                # Micro fade-out (last 64 samples) to prevent end clicks
                fade = min(64, len(s))
                if fade > 0:
                    s[-fade:] *= np.linspace(1, 0, fade)
                cache[sound_name] = s.astype(np.float32)
            else:
                continue

        sample = cache[sound_name].copy()

        # Per-hit humanization — no two hits identical
        # Micro pitch variation (±5 cents)
        pitch_shift = np.random.uniform(-5, 5) / 1200
        # Amplitude variation (±8%)
        amp_var = 1.0 + np.random.uniform(-0.08, 0.08)
        # Tiny timing jitter (±0.5ms) — the human behind the sticks
        timing_jitter = int(np.random.uniform(-0.0005, 0.0005) * sr)

        sample = sample * amp_var

        start = max(0, int(beat * beat_sec * sr) + timing_jitter)
        end = min(start + len(sample), total_samples)
        # Per-instrument stereo pan
        pan = hit.get('pan')
        if pan is None:
            pan = DRUM_PANS.get(sound_name, 0.0)
        # Double kick alternates L/R by successive hit
        if sound_name == 'double_kick':
            pan = -0.28 if double_kick_flip % 2 == 0 else 0.28
            double_kick_flip += 1
        # Constant-power pan
        pan_angle = (float(pan) + 1.0) * np.pi / 4.0  # 0..pi/2
        left_gain = np.cos(pan_angle)
        right_gain = np.sin(pan_angle)
        chunk = sample[:end-start] * vel
        stereo_out[start:end, 0] += chunk * left_gain
        stereo_out[start:end, 1] += chunk * right_gain

    # Fade out last 20ms to prevent click at bar boundary
    fade_samples = min(int(0.02 * sr), total_samples)
    if fade_samples > 0:
        fade = np.linspace(1, 0, fade_samples)[:, None]
        stereo_out[-fade_samples:] *= fade

    stereo_out = np.clip(stereo_out, -1.0, 1.0).astype(np.float32)
    return stereo_out
