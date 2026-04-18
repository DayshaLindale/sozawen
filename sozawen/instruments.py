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
    if a > 0:
        env[pos:pos+a] = np.linspace(0, 1, a)
        pos += a
    # Decay: 1 to sustain
    if d > 0:
        env[pos:pos+d] = np.linspace(1, sustain, d)
        pos += d
    # Sustain
    if s_len > 0:
        env[pos:pos+s_len] = sustain
        pos += s_len
    # Release: sustain to 0
    if r > 0 and pos < length:
        remaining = min(r, length - pos)
        env[pos:pos+remaining] = np.linspace(sustain, 0, remaining)

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
    n_samples = int(duration * sr)
    vel = velocity / 127.0

    # Generate oscillator
    osc_funcs = {'sine': sine, 'saw': saw, 'square': square, 'triangle': triangle}
    gen = osc_funcs.get(waveform, saw)
    osc = gen(freq, duration, sr)

    # Optional detuning (chorus-like thickness)
    if detune > 0:
        osc2 = gen(freq * (1 + detune/100), duration, sr)
        osc = (osc + osc2) * 0.5

    # Filter
    if cutoff < sr / 2 - 100:
        osc = lowpass(osc, cutoff, sr)

    # Envelope
    env = adsr(n_samples, attack, decay, sustain, release, sr)

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
        start_sample = int(n['start_beat'] * beat_sec * sr)
        dur = n.get('duration_beats', 1) * beat_sec
        vel = n.get('velocity', 100)
        note_audio = synth_note(n['note'], dur, vel, sr, **synth_params)

        end = min(start_sample + len(note_audio), total_samples)
        audio[start_sample:end] += note_audio[:end - start_sample]

    audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
    return np.column_stack([audio, audio])  # stereo


# ═══════════════════════════════════════════════════════════════════
# DRUM MACHINE — synthesized drums from math
# ═══════════════════════════════════════════════════════════════════

def drum_kick(sr=44100):
    """Synthesize a kick drum — pitch-swept sine with fast decay."""
    dur = 0.3
    body = pitch_envelope(150, 40, dur, sr) * 0.9
    env = adsr(len(body), 0.001, 0.05, 0.3, 0.15, sr)
    click = noise(0.005, sr) * 0.3
    result = np.zeros(int(dur * sr), dtype=np.float32)
    result[:len(body)] += body * env
    result[:len(click)] += click
    return lowpass(result, 200, sr) * 0.9


def drum_snare(sr=44100):
    """Synthesize a snare — sine body + filtered noise."""
    dur = 0.2
    body = sine(200, dur, sr) * adsr(int(dur*sr), 0.001, 0.03, 0.1, 0.1, sr) * 0.4
    nz = noise(dur, sr) * adsr(int(dur*sr), 0.001, 0.05, 0.15, 0.1, sr) * 0.5
    nz = highpass(nz, 1000, sr)
    return (body + nz).astype(np.float32)


def drum_hihat_closed(sr=44100):
    """Synthesize a closed hi-hat — short filtered noise burst."""
    dur = 0.05
    nz = noise(dur, sr) * adsr(int(dur*sr), 0.001, 0.01, 0.1, 0.02, sr)
    return highpass(nz * 0.3, 5000, sr)


def drum_hihat_open(sr=44100):
    """Synthesize an open hi-hat — longer filtered noise."""
    dur = 0.3
    nz = noise(dur, sr) * adsr(int(dur*sr), 0.001, 0.05, 0.3, 0.15, sr)
    return highpass(nz * 0.3, 4000, sr)


def drum_clap(sr=44100):
    """Synthesize a clap — layered noise bursts."""
    dur = 0.15
    clap = np.zeros(int(dur * sr), dtype=np.float32)
    # Multiple short noise bursts
    for offset_ms in [0, 8, 15, 22]:
        start = int(offset_ms / 1000 * sr)
        burst = noise(0.01, sr) * 0.4
        end = min(start + len(burst), len(clap))
        clap[start:end] += burst[:end-start]
    env = adsr(len(clap), 0.001, 0.03, 0.2, 0.08, sr)
    return highpass(clap * env, 800, sr)


def drum_tom(pitch=100, sr=44100):
    """Synthesize a tom — pitched sine with decay."""
    dur = 0.25
    body = pitch_envelope(pitch * 1.5, pitch, dur, sr)
    env = adsr(int(dur*sr), 0.001, 0.05, 0.2, 0.12, sr)
    return (body * env * 0.5).astype(np.float32)


def drum_rim(sr=44100):
    """Synthesize a rim shot — short high click."""
    dur = 0.03
    click = sine(800, dur, sr) * 0.6
    nz = noise(dur, sr) * 0.2
    env = adsr(int(dur*sr), 0.001, 0.005, 0.1, 0.01, sr)
    return ((click + nz) * env).astype(np.float32)


# All available drum sounds
DRUM_SOUNDS = {
    'kick': drum_kick,
    'snare': drum_snare,
    'hihat': drum_hihat_closed,
    'hihat_open': drum_hihat_open,
    'clap': drum_clap,
    'tom_high': lambda sr=44100: drum_tom(150, sr),
    'tom_mid': lambda sr=44100: drum_tom(100, sr),
    'tom_low': lambda sr=44100: drum_tom(70, sr),
    'rim': drum_rim,
}


def render_drum_pattern(pattern, sr=44100, bpm=120):
    """Render a drum pattern to audio.

    pattern: list of {sound: str, beat: float, velocity: float (0-1)}
    Returns stereo numpy array.
    """
    beat_sec = 60.0 / bpm

    if not pattern:
        return np.zeros((sr, 2), dtype=np.float32)

    end_beat = max(p['beat'] for p in pattern) + 1
    total_samples = int((end_beat * beat_sec + 0.5) * sr)
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
