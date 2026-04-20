"""Sozawen Room Modeling — virtual microphone positions.

Simulates the acoustic environment around an instrument.
Instead of one flat signal, generates multiple "mic" perspectives:
- Close mic: dry, detailed, present
- Overhead: balanced, natural, with room reflections
- Room mic: ambient, spacious, with natural reverb

Uses early reflections + diffuse reverb tail modeled from
room dimensions and surface absorption. Pure math.
"""

import numpy as np


def generate_room_ir(room_type="studio", mic_position="close", sr=44100):
    """Generate an impulse response for a virtual room + mic position.

    Parameters:
        room_type: "studio" (small, tight), "live_room" (medium, warm),
                   "hall" (large, spacious), "booth" (tiny, dry)
        mic_position: "close" (1-2ft), "overhead" (4-6ft),
                      "room" (10-15ft), "ambient" (20ft+)

    Returns: impulse response as numpy array.
    """
    # Room parameters (reverb time, early reflection density, pre-delay)
    rooms = {
        "booth":     {"rt60": 0.15, "density": 0.3, "predelay": 0.001, "size": 0.2},
        "studio":    {"rt60": 0.4,  "density": 0.5, "predelay": 0.005, "size": 0.5},
        "live_room": {"rt60": 0.8,  "density": 0.7, "predelay": 0.012, "size": 0.8},
        "hall":      {"rt60": 2.0,  "density": 0.9, "predelay": 0.025, "size": 1.0},
    }

    # Mic distance affects direct/reverb ratio
    mic_params = {
        "close":    {"direct": 0.95, "early": 0.04, "late": 0.01, "hf_roll": 1.0},
        "overhead": {"direct": 0.60, "early": 0.25, "late": 0.15, "hf_roll": 0.85},
        "room":     {"direct": 0.20, "early": 0.35, "late": 0.45, "hf_roll": 0.7},
        "ambient":  {"direct": 0.05, "early": 0.30, "late": 0.65, "hf_roll": 0.5},
    }

    room = rooms.get(room_type, rooms["studio"])
    mic = mic_params.get(mic_position, mic_params["close"])

    rt60 = room["rt60"]
    ir_length = int(rt60 * 1.5 * sr)  # IR slightly longer than RT60
    ir = np.zeros(ir_length, dtype=np.float64)

    # Direct sound (delta at pre-delay)
    predelay_samples = int(room["predelay"] * sr)
    if predelay_samples < ir_length:
        ir[predelay_samples] = mic["direct"]

    # Early reflections — discrete echoes from walls/ceiling/floor
    n_early = int(8 + room["density"] * 20)
    for i in range(n_early):
        # Reflection time increases with room size
        delay = predelay_samples + int((0.005 + i * 0.003 * room["size"]) * sr)
        if delay < ir_length:
            # Each reflection is weaker and has more HF absorption
            amp = mic["early"] * (0.8 ** i) * np.random.uniform(0.5, 1.0)
            # Random polarity (some reflections are phase-inverted)
            amp *= np.random.choice([-1, 1])
            ir[delay] += amp

    # Late reverb tail — exponentially decaying noise
    if mic["late"] > 0.01:
        tail_start = predelay_samples + int(0.03 * sr)  # tail begins after early reflections
        if tail_start < ir_length:
            tail_length = ir_length - tail_start
            tail = np.random.randn(tail_length) * mic["late"]
            # Exponential decay matching RT60
            decay = np.exp(-np.linspace(0, 6.9, tail_length))  # 6.9 = -60dB
            tail *= decay
            # HF absorption — room air absorbs high frequencies over distance
            if mic["hf_roll"] < 1.0:
                from scipy.signal import butter, lfilter
                cutoff = 2000 + mic["hf_roll"] * 12000  # 2-14kHz
                b, a = butter(1, min(cutoff, sr/2-1) / (sr/2), btype='low')
                tail = lfilter(b, a, tail)
            ir[tail_start:] += tail

    # Normalize IR
    peak = np.max(np.abs(ir))
    if peak > 0:
        ir /= peak

    return ir.astype(np.float32)


def apply_room(audio, room_type="studio", mic_position="close", mix=0.3, sr=44100):
    """Apply room modeling to audio.

    Parameters:
        audio: numpy array
        room_type: "booth", "studio", "live_room", "hall"
        mic_position: "close", "overhead", "room", "ambient"
        mix: 0-1 wet/dry ratio (0=dry, 1=full room)
        sr: sample rate

    Returns: audio with room applied.
    """
    if mix <= 0.001:
        return audio

    ir = generate_room_ir(room_type, mic_position, sr)

    # Convolve
    wet = np.convolve(audio.astype(np.float64), ir.astype(np.float64))[:len(audio)]

    # Mix
    result = audio.astype(np.float64) * (1 - mix) + wet * mix

    # Normalize to match input level
    input_peak = np.max(np.abs(audio))
    output_peak = np.max(np.abs(result))
    if output_peak > 0 and input_peak > 0:
        result *= input_peak / output_peak

    return result.astype(np.float32)
