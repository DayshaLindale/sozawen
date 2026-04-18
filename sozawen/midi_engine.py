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
