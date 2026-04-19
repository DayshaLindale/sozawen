"""Sozawen Instruments — synthesizer and drum machine from pure math.

No samples, no dependencies, no borrowed sounds.
Every tone generated from oscillators, noise, and envelopes.
GPL-free. BSD-compatible. Ours.
"""

import numpy as np
import logging

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

    # Lowpass — but not too aggressive (let the beater click through)
    return lowpass(result, 150, sr) * 0.9


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


def drum_hihat_closed(sr=44100, decay_ms=50, brightness=0.7):
    """Synthesize a closed hi-hat — mostly noise with metallic character.

    Real hi-hats: two bronze cymbals pressed together. The sound is
    primarily broadband noise shaped by the metal's resonance.
    The tonal components are very high (6-12kHz) and quickly masked
    by the noise. Closed = very short, tight, "chick" sound.
    """
    dur = max(0.02, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # PRIMARY: filtered noise — this IS the hi-hat sound
    nz = noise(dur, sr) * 0.6
    # Bandpass to hi-hat frequency range (5-12kHz)
    nz = highpass(nz, 5000, sr)
    nz = lowpass(nz, 13000, sr)

    # SECONDARY: subtle metallic ring (much quieter than noise)
    metal = np.zeros(n, dtype=np.float32)
    for freq in [6500, 8200, 10500]:
        metal += np.sin(2 * np.pi * freq * t) * 0.04
    metal *= np.exp(-t * 50)  # metallic ring dies very fast when closed

    # Very fast envelope — closed hi-hat is TIGHT
    env = np.exp(-t * (1000 / max(decay_ms, 10)))

    result = (nz + metal) * env * brightness
    return result.astype(np.float32) * 0.4


def drum_hihat_open(sr=44100, decay_ms=500, brightness=0.7):
    """Synthesize an open hi-hat — same character, longer sustain.

    Open hi-hat: cymbals separated, vibrating freely. Much longer
    ring, more metallic shimmer audible because the noise sustains.
    """
    dur = max(0.1, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Noise — longer, with more mid-high content
    nz = noise(dur, sr) * 0.5
    nz = highpass(nz, 4000, sr)
    nz = lowpass(nz, 14000, sr)

    # More metallic shimmer audible when open (longer decay)
    metal = np.zeros(n, dtype=np.float32)
    for freq in [6200, 7800, 9500, 11200, 13000]:
        metal += np.sin(2 * np.pi * freq * t) * 0.05
    metal *= np.exp(-t * 4)  # ring sustains when open

    # Longer envelope with sustain
    env = np.exp(-t * (3 / max(dur, 0.1)))

    result = (nz + metal) * env * brightness
    return result.astype(np.float32) * 0.4


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

    Research: pitch sweep from 1.5x to base, body resonance from shell.
    """
    dur = max(0.1, sustain_ms / 1000)
    n = int(dur * sr)

    # Body — pitch-swept sine
    body = pitch_envelope(pitch * 1.5, pitch, dur, sr)
    body_env = adsr(n, 0.001, 0.04, 0.25, dur * 0.4, sr)

    # Resonance — second harmonic for shell character
    shell = sine(pitch * 2.2, dur, sr) * resonance * 0.15
    shell_env = adsr(n, 0.005, 0.08, 0.1, dur * 0.2, sr)

    result = np.zeros(n, dtype=np.float32)
    result[:len(body)] += body[:n] * body_env * 0.6
    result[:len(shell)] += shell[:n] * shell_env

    return result.astype(np.float32)


def drum_rim(sr=44100):
    """Synthesize a rim shot — sharp metallic click with ring."""
    dur = 0.05
    n = int(dur * sr)
    click = sine(900, dur, sr) * 0.5
    ring = sine(2200, dur, sr) * 0.2  # metallic ring
    nz = noise(0.003, sr) * 0.3
    env = adsr(n, 0.0003, 0.008, 0.05, 0.02, sr)
    result = np.zeros(n, dtype=np.float32)
    result[:n] += (click + ring) * env
    result[:len(nz)] += nz
    return result.astype(np.float32)


def drum_crash(sr=44100, decay_ms=1500):
    """Synthesize a crash cymbal — long metallic wash."""
    dur = max(0.5, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Rich metallic harmonics
    metal = np.zeros(n, dtype=np.float32)
    for freq in [2800, 4100, 5300, 6800, 8400, 10200, 12500]:
        metal += np.sin(2 * np.pi * freq * t * (1 + np.random.randn() * 0.01)) * 0.07

    nz = noise(dur, sr) * 0.3
    env = adsr(n, 0.001, 0.1, 0.3, dur * 0.5, sr)

    result = (metal + nz) * env
    return highpass(result * 0.3, 3000, sr)


def drum_ride(sr=44100, decay_ms=800):
    """Synthesize a ride cymbal — clear bell with sustain."""
    dur = max(0.3, decay_ms / 1000)
    n = int(dur * sr)
    t = np.linspace(0, dur, n, dtype=np.float32)

    # Bell-like tone + metallic wash
    bell = np.sin(2 * np.pi * 3200 * t) * 0.2
    metal = np.zeros(n, dtype=np.float32)
    for freq in [4500, 6200, 7800, 9400]:
        metal += np.sin(2 * np.pi * freq * t) * 0.06

    nz = noise(dur, sr) * 0.1
    env = adsr(n, 0.0005, 0.05, 0.4, dur * 0.3, sr)

    result = (bell + metal + nz) * env
    return highpass(result * 0.3, 2500, sr)


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
    """Double bass drum hit — alternating left/right foot.

    Each hit is slightly different (human imprecision).
    The two hits overlap — second beater contacts before first decay.
    Used in metal, prog, and fusion at high tempos (160-220+ BPM).
    """
    # Two kicks with slight timing and velocity variation
    kick1 = drum_kick(sr, sustain_ms=150, pitch=48, punch=0.5, sub=0.4)
    kick2 = drum_kick(sr, sustain_ms=140, pitch=50, punch=0.45, sub=0.35)

    # Offset: second kick comes ~60ms after first (typical double bass gap)
    gap = int(0.06 * sr)
    total = max(len(kick1), gap + len(kick2))
    result = np.zeros(total, dtype=np.float32)
    result[:len(kick1)] += kick1 * 0.9
    result[gap:gap + len(kick2)] += kick2 * 0.85  # second hit slightly softer

    return result


# All available drum sounds
DRUM_SOUNDS = {
    'kick': drum_kick,
    'double_kick': drum_double_kick,
    'snare': drum_snare,
    'hihat': drum_hihat_closed,
    'hihat_open': drum_hihat_open,
    'clap': drum_clap,
    'tom_high': lambda sr=44100: drum_tom(150, sr),
    'tom_mid': lambda sr=44100: drum_tom(100, sr),
    'tom_low': lambda sr=44100: drum_tom(70, sr),
    'rim': drum_rim,
    'crash': drum_crash,
    'ride': drum_ride,
    'shaker': drum_shaker,
    'cowbell': drum_cowbell,
}


def render_drum_pattern(pattern, sr=44100, bpm=120):
    """Render a drum pattern to audio.

    pattern: list of {sound: str, beat: float, velocity: float (0-1)}
    Returns stereo numpy array.
    """
    beat_sec = 60.0 / bpm

    if not pattern:
        return np.zeros((sr, 2), dtype=np.float32)

    end_beat = max(p['beat'] for p in pattern) + 0.5  # half beat after last hit (not full beat)
    total_samples = int(end_beat * beat_sec * sr) + int(0.3 * sr)  # 300ms tail for decay
    audio = np.zeros(total_samples, dtype=np.float64)

    # Cache rendered drum sounds
    cache = {}

    for hit in pattern:
        sound_name = hit.get('sound', 'kick')
        beat = hit.get('beat', 0)
        vel = hit.get('velocity', 0.8)

        if sound_name not in cache:
            gen = DRUM_SOUNDS.get(sound_name)
            if gen:
                cache[sound_name] = gen(sr)
            else:
                continue

        sample = cache[sound_name]
        start = int(beat * beat_sec * sr)
        end = min(start + len(sample), total_samples)
        audio[start:end] += sample[:end-start] * vel

    audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
    return np.column_stack([audio, audio])
