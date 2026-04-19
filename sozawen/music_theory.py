"""Sozawen Music Theory — scales, chords, circle of fifths.

Accurate music theory data for key detection, synth patterns,
chord suggestions, and the Bandmate.
"""

# ═══════════════════════════════════════════════════════════════════
# NOTE NAMES
# ═══════════════════════════════════════════════════════════════════

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ENHARMONIC = {'Db':'C#', 'Eb':'D#', 'Gb':'F#', 'Ab':'G#', 'Bb':'A#'}

def note_to_midi(name, octave=4):
    """Convert note name to MIDI number. C4 = 60."""
    n = ENHARMONIC.get(name, name)
    idx = NOTE_NAMES.index(n) if n in NOTE_NAMES else 0
    return (octave + 1) * 12 + idx

def midi_to_note(midi):
    """Convert MIDI number to (name, octave)."""
    return NOTE_NAMES[midi % 12], (midi // 12) - 1

def freq_to_midi(freq):
    """Convert frequency to nearest MIDI note."""
    import math
    if freq <= 0: return 0
    return round(69 + 12 * math.log2(freq / 440.0))


# ═══════════════════════════════════════════════════════════════════
# SCALES — intervals from root (semitones)
# ═══════════════════════════════════════════════════════════════════

SCALES = {
    # Major modes
    'major':            [0, 2, 4, 5, 7, 9, 11],      # Ionian
    'dorian':           [0, 2, 3, 5, 7, 9, 10],
    'phrygian':         [0, 1, 3, 5, 7, 8, 10],
    'lydian':           [0, 2, 4, 6, 7, 9, 11],
    'mixolydian':       [0, 2, 4, 5, 7, 9, 10],
    'minor':            [0, 2, 3, 5, 7, 8, 10],       # Aeolian / Natural Minor
    'locrian':          [0, 1, 3, 5, 6, 8, 10],

    # Harmonic & Melodic Minor
    'harmonic_minor':   [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor':    [0, 2, 3, 5, 7, 9, 11],       # ascending

    # Pentatonic
    'major_pentatonic': [0, 2, 4, 7, 9],
    'minor_pentatonic': [0, 3, 5, 7, 10],

    # Blues
    'blues':            [0, 3, 5, 6, 7, 10],
    'major_blues':      [0, 2, 3, 4, 7, 9],

    # Other
    'chromatic':        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'whole_tone':       [0, 2, 4, 6, 8, 10],
    'diminished':       [0, 2, 3, 5, 6, 8, 9, 11],    # half-whole
    'hungarian_minor':  [0, 2, 3, 6, 7, 8, 11],
    'arabic':           [0, 1, 4, 5, 7, 8, 11],
    'japanese':         [0, 1, 5, 7, 8],               # In scale
    'hirajoshi':        [0, 2, 3, 7, 8],
}

def get_scale(root, scale_name='major'):
    """Get MIDI notes for a scale starting at a given root.
    root: note name (e.g., 'C', 'F#', 'Bb')
    Returns list of MIDI note numbers in one octave.
    """
    root_name = ENHARMONIC.get(root, root)
    root_idx = NOTE_NAMES.index(root_name) if root_name in NOTE_NAMES else 0
    intervals = SCALES.get(scale_name, SCALES['major'])
    return [(root_idx + i) % 12 for i in intervals]


# ═══════════════════════════════════════════════════════════════════
# CHORDS — intervals from root
# ═══════════════════════════════════════════════════════════════════

CHORDS = {
    'major':        [0, 4, 7],
    'minor':        [0, 3, 7],
    'diminished':   [0, 3, 6],
    'augmented':    [0, 4, 8],
    'sus2':         [0, 2, 7],
    'sus4':         [0, 5, 7],
    'major7':       [0, 4, 7, 11],
    'minor7':       [0, 3, 7, 10],
    'dominant7':    [0, 4, 7, 10],
    'diminished7':  [0, 3, 6, 9],
    'half_dim7':    [0, 3, 6, 10],
    'add9':         [0, 4, 7, 14],
    'minor_add9':   [0, 3, 7, 14],
    'major9':       [0, 4, 7, 11, 14],
    'minor9':       [0, 3, 7, 10, 14],
    'power':        [0, 7],         # 5th chord
    '6':            [0, 4, 7, 9],
    'minor6':       [0, 3, 7, 9],
}

def identify_chord(midi_notes):
    """Identify a chord from a list of MIDI note numbers.

    Returns chord name string like 'C Major', 'Am7', or None if unrecognized.
    """
    if len(midi_notes) < 2:
        return None

    # Normalize to pitch classes (0-11) and sort
    pcs = sorted(set(n % 12 for n in midi_notes))
    if len(pcs) < 2:
        return None

    # Try every pitch class as potential root
    best = None
    for root_pc in pcs:
        intervals = sorted((pc - root_pc) % 12 for pc in pcs)
        root_name = NOTE_NAMES[root_pc]

        # Match against known chord types
        for chord_name, chord_intervals in CHORDS.items():
            # Normalize chord intervals to pitch classes
            ci = sorted(i % 12 for i in chord_intervals)
            if intervals == ci:
                # Format nice name
                display = {
                    'major': 'Major', 'minor': 'Minor', 'diminished': 'Dim',
                    'augmented': 'Aug', 'sus2': 'sus2', 'sus4': 'sus4',
                    'major7': 'Maj7', 'minor7': 'm7', 'dominant7': '7',
                    'diminished7': 'dim7', 'half_dim7': 'm7b5',
                    'add9': 'add9', 'minor_add9': 'madd9',
                    'major9': 'Maj9', 'minor9': 'm9',
                    'power': '5', '6': '6', 'minor6': 'm6',
                }
                label = display.get(chord_name, chord_name)
                best = root_name + ' ' + label if label[0].isupper() else root_name + label
                # Prefer root = lowest note
                lowest_pc = min(midi_notes) % 12
                if root_pc == lowest_pc:
                    return best

    return best


def get_chord(root_note, chord_type='major', octave=4):
    """Get MIDI notes for a chord.
    root_note: note name
    Returns list of MIDI note numbers.
    """
    root = note_to_midi(root_note, octave)
    intervals = CHORDS.get(chord_type, CHORDS['major'])
    return [root + i for i in intervals]


# ═══════════════════════════════════════════════════════════════════
# CIRCLE OF FIFTHS
# ═══════════════════════════════════════════════════════════════════

# Major keys around the circle (clockwise = sharps, counter = flats)
CIRCLE_OF_FIFTHS_MAJOR = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F']
CIRCLE_OF_FIFTHS_MINOR = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Bbm', 'Fm', 'Cm', 'Gm', 'Dm']

# Key signatures (number of sharps/flats)
KEY_SIGNATURES = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6,
    'Am': 0, 'Em': 1, 'Bm': 2, 'F#m': 3, 'C#m': 4, 'G#m': 5, 'D#m': 6,
    'Dm': -1, 'Gm': -2, 'Cm': -3, 'Fm': -4, 'Bbm': -5, 'Ebm': -6,
}

def get_relative_minor(major_key):
    """Get the relative minor of a major key."""
    idx = CIRCLE_OF_FIFTHS_MAJOR.index(major_key) if major_key in CIRCLE_OF_FIFTHS_MAJOR else 0
    return CIRCLE_OF_FIFTHS_MINOR[idx]

def get_relative_major(minor_key):
    """Get the relative major of a minor key."""
    clean = minor_key.replace('m', '')
    idx = [k.replace('m','') for k in CIRCLE_OF_FIFTHS_MINOR].index(clean) if clean in [k.replace('m','') for k in CIRCLE_OF_FIFTHS_MINOR] else 0
    return CIRCLE_OF_FIFTHS_MAJOR[idx]

def get_compatible_keys(key):
    """Get keys that work well with the given key (for key changes, modulation)."""
    if key in CIRCLE_OF_FIFTHS_MAJOR:
        idx = CIRCLE_OF_FIFTHS_MAJOR.index(key)
        return {
            'parallel_minor': key + 'm',
            'relative_minor': CIRCLE_OF_FIFTHS_MINOR[idx],
            'dominant': CIRCLE_OF_FIFTHS_MAJOR[(idx + 1) % 12],
            'subdominant': CIRCLE_OF_FIFTHS_MAJOR[(idx - 1) % 12],
        }
    # Minor key
    clean = key.replace('m', '')
    minor_names = [k.replace('m','') for k in CIRCLE_OF_FIFTHS_MINOR]
    if clean in minor_names:
        idx = minor_names.index(clean)
        return {
            'parallel_major': clean,
            'relative_major': CIRCLE_OF_FIFTHS_MAJOR[idx],
            'dominant_minor': CIRCLE_OF_FIFTHS_MINOR[(idx + 1) % 12],
            'subdominant_minor': CIRCLE_OF_FIFTHS_MINOR[(idx - 1) % 12],
        }
    return {}


# ═══════════════════════════════════════════════════════════════════
# DIATONIC CHORDS — chords built from a scale
# ═══════════════════════════════════════════════════════════════════

def get_diatonic_chords(key, scale_type='major'):
    """Get the 7 diatonic chords for a key.
    Returns list of (root_name, chord_quality, roman_numeral).
    """
    root = ENHARMONIC.get(key.replace('m',''), key.replace('m',''))
    root_idx = NOTE_NAMES.index(root) if root in NOTE_NAMES else 0

    if scale_type == 'minor' or key.endswith('m'):
        intervals = SCALES['minor']
        qualities = ['minor', 'diminished', 'major', 'minor', 'minor', 'major', 'major']
        numerals = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']
    else:
        intervals = SCALES['major']
        qualities = ['major', 'minor', 'minor', 'major', 'major', 'minor', 'diminished']
        numerals = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']

    chords = []
    for i, (interval, quality, numeral) in enumerate(zip(intervals, qualities, numerals)):
        note_name = NOTE_NAMES[(root_idx + interval) % 12]
        chords.append({
            'root': note_name,
            'quality': quality,
            'numeral': numeral,
            'notes': get_chord(note_name, quality),
        })

    return chords


# ═══════════════════════════════════════════════════════════════════
# COMMON PROGRESSIONS
# ═══════════════════════════════════════════════════════════════════

PROGRESSIONS = {
    'pop':          [0, 4, 5, 3],       # I-V-vi-IV (most pop songs ever)
    'blues':        [0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4],  # 12-bar blues
    'jazz_251':     [1, 4, 0],           # ii-V-I
    'andalusian':   [5, 4, 3, 0],        # Am-G-F-E (flamenco)
    'axis':         [0, 4, 5, 3],        # I-V-vi-IV
    'fifties':      [0, 5, 3, 4],        # I-vi-IV-V (doo-wop)
    'rock':         [0, 3, 4],           # I-IV-V
    'emo':          [0, 5, 3, 4],        # I-vi-IV-V
    'minor_pop':    [0, 3, 4, 5],        # i-iv-v-vi
    'sad':          [0, 5, 2, 4],        # i-vi-iii-v
}

def get_progression(key, progression_name='pop'):
    """Get chords for a common progression in a given key."""
    diatonic = get_diatonic_chords(key)
    indices = PROGRESSIONS.get(progression_name, PROGRESSIONS['pop'])
    return [diatonic[i % len(diatonic)] for i in indices]
