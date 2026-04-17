"""Sozawen Editing Operations — split, trim, count-in, channel detection.

All operations are non-destructive. They modify regions (pointers to source files)
not the source files themselves.
"""

import numpy as np
import soundfile as sf
import logging
from pathlib import Path

logger = logging.getLogger("sozawen.editing")


def detect_channels(file_path):
    """Detect how many audio channels are in a file."""
    try:
        info = sf.info(file_path)
        return {
            "channels": info.channels,
            "sample_rate": info.samplerate,
            "duration": info.duration,
            "frames": info.frames,
            "format": info.format,
            "subtype": info.subtype,
        }
    except Exception as e:
        return {"error": str(e)}


def split_channels(file_path, output_dir=None):
    """Split a multi-channel file into individual mono files."""
    data, sr = sf.read(file_path, dtype='float32')
    if data.ndim == 1:
        return [{"path": file_path, "channel": 0, "name": "Mono"}]

    n_channels = data.shape[1]
    stem = Path(file_path).stem
    out_dir = Path(output_dir) if output_dir else Path(file_path).parent
    out_dir.mkdir(exist_ok=True)

    results = []
    channel_names = {
        1: ["Mono"],
        2: ["Left", "Right"],
        4: ["Front Left", "Front Right", "Rear Left", "Rear Right"],
        6: ["Front Left", "Front Right", "Center", "LFE", "Surround Left", "Surround Right"],
    }
    names = channel_names.get(n_channels, [f"Channel {i+1}" for i in range(n_channels)])

    for ch in range(n_channels):
        name = names[ch] if ch < len(names) else f"Channel {ch+1}"
        out_path = out_dir / f"{stem}_{name.lower().replace(' ', '_')}.wav"
        sf.write(str(out_path), data[:, ch], sr)
        results.append({
            "path": str(out_path),
            "channel": ch,
            "name": name,
        })

    return results


def split_region_at_sample(region, split_sample):
    """Split a region into two at the given sample position (relative to track).

    Returns (left_region_dict, right_region_dict) or None if split point is outside region.
    """
    if split_sample <= region.track_offset or split_sample >= region.end_sample:
        return None

    # Split point relative to region start
    relative_split = split_sample - region.track_offset

    left = {
        "source_path": region.source_path,
        "start_sample": region.start_sample,
        "track_offset": region.track_offset,
        "length": relative_split,
        "gain": region.gain,
        "name": region.name + " (L)",
        "source_type": region.source_type,
    }

    right = {
        "source_path": region.source_path,
        "start_sample": region.start_sample + relative_split,
        "track_offset": split_sample,
        "length": region.length - relative_split,
        "gain": region.gain,
        "name": region.name + " (R)",
        "source_type": region.source_type,
    }

    return left, right


def generate_click_track(bpm, duration_seconds, sample_rate=44100,
                         time_sig_num=4, time_sig_den=4,
                         count_in_bars=0):
    """Generate a metronome click track.

    Returns numpy array of click audio.
    count_in_bars: if > 0, generates only the count-in portion.
    """
    beat_duration = 60.0 / bpm
    samples_per_beat = int(beat_duration * sample_rate)

    if count_in_bars > 0:
        total_beats = count_in_bars * time_sig_num
        total_samples = total_beats * samples_per_beat
    else:
        total_samples = int(duration_seconds * sample_rate)
        total_beats = int(total_samples / samples_per_beat) + 1

    audio = np.zeros(total_samples, dtype=np.float32)

    # Click sound: short sine burst
    click_duration = 0.015  # 15ms
    click_samples = int(click_duration * sample_rate)
    t = np.arange(click_samples) / sample_rate

    # Downbeat (beat 1): higher pitch, louder
    downbeat = np.sin(2 * np.pi * 1500 * t) * 0.7
    downbeat *= np.exp(-t * 200)  # fast decay

    # Other beats: lower pitch, quieter
    upbeat = np.sin(2 * np.pi * 1000 * t) * 0.4
    upbeat *= np.exp(-t * 200)

    for beat in range(total_beats):
        pos = beat * samples_per_beat
        if pos + click_samples > len(audio):
            break

        is_downbeat = (beat % time_sig_num) == 0
        click = downbeat if is_downbeat else upbeat
        audio[pos:pos + click_samples] += click

    return audio


def detect_silence(file_path, threshold_db=-40, min_duration_ms=500):
    """Detect silent sections in audio. Returns list of (start_sec, end_sec) tuples."""
    data, sr = sf.read(file_path, dtype='float32')
    if data.ndim > 1:
        data = data.mean(axis=1)

    threshold = 10 ** (threshold_db / 20)
    min_samples = int(min_duration_ms / 1000 * sr)

    silent_regions = []
    in_silence = False
    silence_start = 0

    # Process in small windows
    window_size = int(sr * 0.01)  # 10ms windows
    for i in range(0, len(data) - window_size, window_size):
        rms = np.sqrt(np.mean(data[i:i+window_size] ** 2))

        if rms < threshold:
            if not in_silence:
                silence_start = i
                in_silence = True
        else:
            if in_silence:
                silence_length = i - silence_start
                if silence_length >= min_samples:
                    silent_regions.append((
                        round(silence_start / sr, 3),
                        round(i / sr, 3),
                    ))
                in_silence = False

    # Handle trailing silence
    if in_silence:
        silence_length = len(data) - silence_start
        if silence_length >= min_samples:
            silent_regions.append((
                round(silence_start / sr, 3),
                round(len(data) / sr, 3),
            ))

    return silent_regions


def detect_transients(file_path, sensitivity=0.5):
    """Detect transient/attack points in audio. Returns list of timestamps in seconds."""
    import librosa

    y, sr = librosa.load(file_path, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=sr,
        delta=0.1 + (1.0 - sensitivity) * 0.5,
        backtrack=True,
    )
    times = librosa.frames_to_time(onsets, sr=sr)
    return [round(float(t), 3) for t in times]
