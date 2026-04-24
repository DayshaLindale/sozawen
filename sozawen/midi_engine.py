"""Sozawen MIDI Engine — piano roll, note editing, real-time input.

MIDI notes, patterns, quantization, and keyboard input.
Renders to audio through the synth engine.
"""

import numpy as np
import logging
import time

logger = logging.getLogger("sozawen.midi")


# ═══════════════════════════════════════════════════════════════════
# MIDI NOTE REPRESENTATION
# ═══════════════════════════════════════════════════════════════════

class MidiNote:
    """A single MIDI note event."""
    __slots__ = ['pitch', 'velocity', 'start_beat', 'duration_beats', 'channel']

    def __init__(self, pitch=60, velocity=100, start_beat=0, duration_beats=1, channel=0):
        self.pitch = pitch          # 0-127 (60 = middle C)
        self.velocity = velocity    # 0-127
        self.start_beat = start_beat
        self.duration_beats = duration_beats
        self.channel = channel

    def to_dict(self):
        return {
            'note': self.pitch, 'velocity': self.velocity,
            'start_beat': self.start_beat, 'duration_beats': self.duration_beats,
        }

    @staticmethod
    def from_dict(d):
        return MidiNote(d.get('note', 60), d.get('velocity', 100),
                       d.get('start_beat', 0), d.get('duration_beats', 1))


class MidiPattern:
    """A collection of MIDI notes — one pattern per track."""

    def __init__(self, name="Pattern", length_beats=16):
        self.name = name
        self.length_beats = length_beats
        self.notes = []  # list of MidiNote

    def add_note(self, pitch, start_beat, duration_beats=1, velocity=100):
        note = MidiNote(pitch, velocity, start_beat, duration_beats)
        self.notes.append(note)
        return note

    def remove_note(self, pitch, start_beat):
        """Remove note at the given position."""
        self.notes = [n for n in self.notes
                      if not (n.pitch == pitch and abs(n.start_beat - start_beat) < 0.01)]

    def toggle_note(self, pitch, start_beat, duration_beats=0.25, velocity=100):
        """Toggle a note on/off — for piano roll click."""
        existing = [n for n in self.notes
                    if n.pitch == pitch and abs(n.start_beat - start_beat) < 0.01]
        if existing:
            self.remove_note(pitch, start_beat)
            return False  # removed
        else:
            self.add_note(pitch, start_beat, duration_beats, velocity)
            return True  # added

    def quantize(self, grid=0.25):
        """Snap all notes to the nearest grid position."""
        for note in self.notes:
            note.start_beat = round(note.start_beat / grid) * grid
            note.duration_beats = max(grid, round(note.duration_beats / grid) * grid)

    def transpose(self, semitones):
        """Transpose all notes by N semitones."""
        for note in self.notes:
            note.pitch = max(0, min(127, note.pitch + semitones))

    def to_dict(self):
        return {
            'name': self.name,
            'length_beats': self.length_beats,
            'notes': [n.to_dict() for n in self.notes],
        }

    @staticmethod
    def from_dict(d):
        pat = MidiPattern(d.get('name', 'Pattern'), d.get('length_beats', 16))
        for nd in d.get('notes', []):
            pat.notes.append(MidiNote.from_dict(nd))
        return pat


# ═══════════════════════════════════════════════════════════════════
# MIDI EFFECTS — pattern transformations
# ═══════════════════════════════════════════════════════════════════

_SCALE_INTERVALS = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "minor":            [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "lydian":           [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":            [0, 3, 5, 6, 7, 10],
    "chromatic":        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
}

_KEY_ROOTS = {"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,
              "G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}


def _allowed_pitch_classes(key, scale):
    root = _KEY_ROOTS.get(key, 0)
    intervals = _SCALE_INTERVALS.get(scale, _SCALE_INTERVALS["major"])
    return {(root + i) % 12 for i in intervals}


def force_to_scale(pattern, key="C", scale="major"):
    """Snap every note in the pattern to the nearest in-scale pitch.

    For a note not in the scale, move it up or down by the minimum number of
    semitones to reach a valid pitch. Ties go to the UPPER pitch (musically
    brighter resolution).
    """
    allowed = _allowed_pitch_classes(key, scale)
    out = MidiPattern(pattern.name + " (scaled)", pattern.length_beats)
    for n in pattern.notes:
        pc = n.pitch % 12
        if pc in allowed:
            out.add_note(n.pitch, n.start_beat, n.duration_beats, n.velocity)
            continue
        # Search out ±1, ±2... until we find an allowed pitch class
        new_pitch = n.pitch
        for delta in range(1, 7):
            if (n.pitch + delta) % 12 in allowed:
                new_pitch = n.pitch + delta
                break
            if (n.pitch - delta) % 12 in allowed:
                new_pitch = n.pitch - delta
                break
        new_pitch = max(0, min(127, new_pitch))
        out.add_note(new_pitch, n.start_beat, n.duration_beats, n.velocity)
    return out


def arpeggiate_pattern(pattern, mode="up", rate_beats=0.25, octaves=1, gate=0.9):
    """Treat simultaneous (or near-simultaneous) notes as chords and spray them
    as an arpeggio.

    mode: 'up', 'down', 'updown', 'random', 'order' (order = input order)
    rate_beats: subdivision of each arp step (0.25 = 16th notes)
    octaves: 1-4, number of octaves the arp spans
    gate: 0-1, fraction of rate_beats each arp note plays (0.9 = slight detached)
    """
    import random as _random
    out = MidiPattern(pattern.name + " (arp)", pattern.length_beats)
    if not pattern.notes:
        return out

    # Group notes into chord events by start_beat (rounded to arp rate)
    groups = {}
    for n in pattern.notes:
        key = round(n.start_beat / rate_beats) * rate_beats
        groups.setdefault(key, []).append(n)

    sorted_keys = sorted(groups.keys())
    for i, start in enumerate(sorted_keys):
        group = sorted(groups[start], key=lambda nn: nn.pitch)
        # Build the arp sequence — repeat group across octaves
        sequence = []
        for o in range(octaves):
            for nn in group:
                sequence.append((nn.pitch + 12 * o, nn.velocity))

        if mode == "down":
            sequence = list(reversed(sequence))
        elif mode == "updown":
            sequence = sequence + list(reversed(sequence[1:-1])) if len(sequence) > 2 else sequence
        elif mode == "random":
            _random.shuffle(sequence)
        # else up / order

        # Next chord change limits how many arp notes fit
        end_key = sorted_keys[i + 1] if i + 1 < len(sorted_keys) else pattern.length_beats
        span = end_key - start
        max_steps = int(span / rate_beats)
        for step in range(max_steps):
            if not sequence:
                break
            pitch, vel = sequence[step % len(sequence)]
            t = start + step * rate_beats
            if t >= pattern.length_beats:
                break
            out.add_note(pitch, t, rate_beats * gate, vel)
    return out


def generate_chords_from_melody(pattern, chord_type="triad", key="C", scale="major",
                                 inversion=0, octave_offset=-1):
    """For each melody note, build a harmonizing chord BELOW it in the given key/scale.

    chord_type: triad | seventh | ninth | power
    inversion: 0, 1, 2 (for triads)
    octave_offset: -1 puts the chord an octave below the melody
    """
    allowed = _allowed_pitch_classes(key, scale)
    intervals_map = {
        "triad":   [0, 2, 4],         # root, third, fifth (scale degrees within the scale)
        "seventh": [0, 2, 4, 6],
        "ninth":   [0, 2, 4, 6, 8],
        "power":   [0, 4],
    }
    intervals = intervals_map.get(chord_type, intervals_map["triad"])

    out = MidiPattern(pattern.name + " + chords", pattern.length_beats)
    # Keep the melody
    for n in pattern.notes:
        out.add_note(n.pitch, n.start_beat, n.duration_beats, n.velocity)
    # Add chord tones
    root = _KEY_ROOTS.get(key, 0)
    scale_intervals = _SCALE_INTERVALS.get(scale, _SCALE_INTERVALS["major"])
    for n in pattern.notes:
        # Find the scale degree of this pitch (closest within key)
        pc = n.pitch % 12
        # Map pitch class to scale degree index by rotating scale root
        try:
            base_pc_in_scale = (pc - root) % 12
            if base_pc_in_scale not in scale_intervals:
                continue  # skip chord tones for out-of-scale melody notes
            deg = scale_intervals.index(base_pc_in_scale)
        except (ValueError, IndexError):
            continue
        # Build chord tones
        chord_pitches = []
        for iv in intervals:
            step = (deg + iv) % len(scale_intervals)
            octave_add = ((deg + iv) // len(scale_intervals)) * 12
            chord_pc = scale_intervals[step]
            chord_pitches.append(root + chord_pc + octave_add)
        # Apply inversion
        for _ in range(inversion):
            chord_pitches.append(chord_pitches.pop(0) + 12)
        # Shift whole chord by octave_offset
        base_pitch = n.pitch + octave_offset * 12
        # Align chord around base_pitch — take the chord root near base_pitch
        while base_pitch - chord_pitches[0] > 12:
            chord_pitches = [p + 12 for p in chord_pitches]
        while chord_pitches[0] - base_pitch > 12:
            chord_pitches = [p - 12 for p in chord_pitches]

        chord_vel = max(40, n.velocity - 30)  # quieter than melody
        for p in chord_pitches:
            p = max(0, min(127, p))
            out.add_note(p, n.start_beat, n.duration_beats, chord_vel)
    return out


# ═══════════════════════════════════════════════════════════════════
# CHORD DETECTION — analyze audio for chords
# ═══════════════════════════════════════════════════════════════════

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Chord templates — which pitch classes are present
CHORD_TEMPLATES = {
    'major':     [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    'minor':     [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    'dim':       [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    'aug':       [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    'sus2':      [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    'sus4':      [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    '7':         [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    'maj7':      [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    'm7':        [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
}


def detect_chords(audio_path, sr=None):
    """Detect chords from an audio file. Returns list of {time, chord}."""
    import librosa

    y, sr = librosa.load(audio_path, sr=sr)

    # Compute chromagram — 12 pitch classes over time
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=2048)
    times = librosa.frames_to_time(range(chroma.shape[1]), sr=sr, hop_length=2048)

    results = []
    prev_chord = None

    for i in range(chroma.shape[1]):
        frame = chroma[:, i]

        # Normalize
        frame_norm = frame / (np.max(frame) + 1e-10)

        # Match against chord templates
        best_score = -1
        best_chord = "N/C"

        for root in range(12):
            for chord_name, template in CHORD_TEMPLATES.items():
                # Rotate template to match root
                rotated = np.roll(template, root)
                score = np.dot(frame_norm, rotated)

                if score > best_score:
                    best_score = score
                    suffix = '' if chord_name == 'major' else ('m' if chord_name == 'minor' else chord_name)
                    best_chord = NOTE_NAMES[root] + suffix

        # Only record changes and strong matches
        if best_score > 0.6 and best_chord != prev_chord:
            results.append({
                'time': round(float(times[i]), 2),
                'chord': best_chord,
                'confidence': round(float(best_score), 2),
            })
            prev_chord = best_chord

    return results


# ═══════════════════════════════════════════════════════════════════
# AUDIO TO MIDI — detect pitch from audio
# ═══════════════════════════════════════════════════════════════════

def audio_to_midi(audio_path, sr=None, min_note=36, max_note=84):
    """Convert monophonic audio to MIDI notes.

    Works best on isolated single-instrument tracks (vocals, bass, lead).
    Uses pitch detection + onset detection.
    Returns a MidiPattern.
    """
    import librosa

    y, sr = librosa.load(audio_path, sr=sr, mono=True)

    # Detect onsets (note boundaries)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # Detect pitch using pyin (probabilistic YIN)
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.midi_to_hz(min_note),
        fmax=librosa.midi_to_hz(max_note), sr=sr)

    f0_times = librosa.times_like(f0, sr=sr)

    # Build MIDI notes from onsets + pitch
    pattern = MidiPattern(name="Transcribed", length_beats=0)
    tempo_result = librosa.beat.beat_track(y=y, sr=sr)[0]
    bpm = float(np.atleast_1d(np.asarray(tempo_result)).flatten()[0])
    beat_sec = 60.0 / max(bpm, 60)

    for i in range(len(onset_times)):
        onset = onset_times[i]
        # Find the next onset or end of audio
        if i + 1 < len(onset_times):
            offset = onset_times[i + 1]
        else:
            offset = len(y) / sr

        duration = offset - onset

        # Find the dominant pitch during this note
        mask = (f0_times >= onset) & (f0_times < offset)
        pitches = f0[mask]
        voiced = voiced_flag[mask] if voiced_flag is not None else np.ones_like(pitches, dtype=bool)

        voiced_pitches = pitches[voiced & (pitches > 0)]
        if len(voiced_pitches) < 2:
            continue

        # Median pitch for stability
        median_freq = np.median(voiced_pitches)
        midi_note = int(round(librosa.hz_to_midi(median_freq)))
        midi_note = max(min_note, min(max_note, midi_note))

        start_beat = onset / beat_sec
        dur_beats = max(0.125, duration / beat_sec)

        pattern.add_note(midi_note, start_beat, dur_beats, velocity=90)

    pattern.length_beats = max(n.start_beat + n.duration_beats for n in pattern.notes) if pattern.notes else 0

    return pattern, bpm
