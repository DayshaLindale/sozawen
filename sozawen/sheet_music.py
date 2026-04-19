"""Sozawen Sheet Music — write it, read it, translate it.

Standard notation ↔ tablature for every instrument.
A guitarist who reads tabs can learn sheet music.
A pianist who reads sheet music can understand tabs.
Everyone speaks the same language.

Features:
- Tab parser: reads standard text tabs for any stringed instrument
- Tab → sheet music: converts fret positions to standard notation
- Sheet music → tab: converts standard notation to optimal fret positions
- Notation rendering: produces clean SVG notation for display
- Supports: guitar (6/7/8 string), bass (4/5/6), ukulele, banjo, mandolin
"""

from sozawen.music_theory import (
    NOTE_NAMES, ENHARMONIC, note_to_midi, midi_to_note,
    KEY_SIGNATURES, get_scale
)


# ═══════════════════════════════════════════════════════════════════
# INSTRUMENT TUNINGS — open string MIDI notes, lowest to highest
# ═══════════════════════════════════════════════════════════════════

TUNINGS = {
    # Guitar
    "guitar_standard":      [40, 45, 50, 55, 59, 64],           # E2 A2 D3 G3 B3 E4
    "guitar_drop_d":        [38, 45, 50, 55, 59, 64],           # D2 A2 D3 G3 B3 E4
    "guitar_open_g":        [38, 43, 50, 55, 59, 62],           # D2 G2 D3 G3 B3 D4
    "guitar_open_d":        [38, 45, 50, 54, 57, 62],           # D2 A2 D3 F#3 A3 D4
    "guitar_dadgad":        [38, 45, 50, 55, 57, 62],           # D2 A2 D3 G3 A3 D4
    "guitar_half_step_down": [39, 44, 49, 54, 58, 63],          # Eb2 Ab2 Db3 Gb3 Bb3 Eb4
    "guitar_full_step_down": [38, 43, 48, 53, 57, 62],          # D2 G2 C3 F3 A3 D4
    "guitar_7_string":      [35, 40, 45, 50, 55, 59, 64],       # B1 E2 A2 D3 G3 B3 E4
    "guitar_8_string":      [30, 35, 40, 45, 50, 55, 59, 64],   # F#1 B1 E2 A2 D3 G3 B3 E4

    # Bass
    "bass_4_standard":      [28, 33, 38, 43],                   # E1 A1 D2 G2
    "bass_4_drop_d":        [26, 33, 38, 43],                   # D1 A1 D2 G2
    "bass_5_standard":      [23, 28, 33, 38, 43],               # B0 E1 A1 D2 G2
    "bass_6_standard":      [23, 28, 33, 38, 43, 48],           # B0 E1 A1 D2 G2 C3

    # Other strings
    "ukulele_standard":     [67, 60, 64, 69],                   # G4 C4 E4 A4 (re-entrant)
    "ukulele_baritone":     [50, 55, 59, 64],                   # D3 G3 B3 E4
    "banjo_standard":       [62, 47, 50, 55, 59],               # D4 B2 D3 G3 B3 (5-string, 5th is high)
    "mandolin_standard":    [55, 55, 62, 62, 69, 69, 76, 76],   # G3G3 D4D4 A4A4 E5E5 (paired)
}

# Display names
TUNING_NAMES = {
    "guitar_standard": "Standard (EADGBE)",
    "guitar_drop_d": "Drop D (DADGBE)",
    "guitar_open_g": "Open G (DGDGBD)",
    "guitar_open_d": "Open D (DADF#AD)",
    "guitar_dadgad": "DADGAD",
    "guitar_half_step_down": "Half Step Down (Eb)",
    "guitar_full_step_down": "Full Step Down (D)",
    "guitar_7_string": "7-String Standard",
    "guitar_8_string": "8-String Standard",
    "bass_4_standard": "4-String Standard (EADG)",
    "bass_4_drop_d": "4-String Drop D",
    "bass_5_standard": "5-String Standard (BEADG)",
    "bass_6_standard": "6-String Standard (BEADGC)",
    "ukulele_standard": "Ukulele Standard (GCEA)",
    "ukulele_baritone": "Baritone Ukulele (DGBE)",
    "banjo_standard": "Banjo 5-String (gDGBD)",
    "mandolin_standard": "Mandolin Standard (GDAE)",
}

# String names for tab display
def get_string_names(tuning_key):
    """Get the string note names for tab display."""
    midi_notes = TUNINGS.get(tuning_key, TUNINGS["guitar_standard"])
    return [midi_to_note(m)[0] for m in midi_notes]


# ═══════════════════════════════════════════════════════════════════
# TAB PARSER — reads standard text tablature
# ═══════════════════════════════════════════════════════════════════

def parse_tab(tab_text, tuning_key="guitar_standard"):
    """Parse a text tablature into a list of notes/chords.

    Reads standard tab format:
    e|--0--2--3--|
    B|--1--3--0--|
    G|--0--2--0--|
    D|--2--0--0--|
    A|--3-----2--|
    E|--------3--|

    Returns list of 'columns' — each column is a list of
    {string, fret, midi, note, octave} for each fretted note.
    """
    tuning = TUNINGS.get(tuning_key, TUNINGS["guitar_standard"])
    lines = tab_text.strip().split('\n')

    # Find tab lines (contain |, -, and numbers)
    tab_lines = []
    for line in lines:
        cleaned = line.strip()
        # Remove string label (e.g., "e|" or "E|")
        if '|' in cleaned:
            parts = cleaned.split('|')
            # Take the part after the first | (the tab content)
            if len(parts) >= 2:
                tab_content = '|'.join(parts[1:])
                tab_lines.append(tab_content)

    if not tab_lines:
        return []

    # Parse columns — each character position is a time step
    num_strings = min(len(tab_lines), len(tuning))
    max_len = max(len(line) for line in tab_lines)

    columns = []
    col = 0
    while col < max_len:
        column_notes = []
        has_note = False

        for string_idx in range(num_strings):
            line = tab_lines[string_idx] if string_idx < len(tab_lines) else ''
            if col >= len(line):
                continue

            char = line[col]

            # Check for multi-digit fret numbers (e.g., "12")
            if char.isdigit():
                fret_str = char
                # Look ahead for more digits
                look = col + 1
                while look < len(line) and line[look].isdigit():
                    fret_str += line[look]
                    look += 1

                fret = int(fret_str)
                # String index in tab: top line = highest string
                # In our tuning array: index 0 = lowest string
                actual_string = num_strings - 1 - string_idx
                if actual_string < len(tuning):
                    midi = tuning[actual_string] + fret
                    note_name, octave = midi_to_note(midi)

                    column_notes.append({
                        "string": actual_string,
                        "fret": fret,
                        "midi": midi,
                        "note": note_name,
                        "octave": octave,
                    })
                    has_note = True

            # Tab notation symbols
            elif char == 'h':
                pass  # hammer-on (previous note sustained)
            elif char == 'p':
                pass  # pull-off
            elif char == '/':
                pass  # slide up
            elif char == '\\':
                pass  # slide down
            elif char == 'b':
                pass  # bend
            elif char == 'x':
                column_notes.append({
                    "string": num_strings - 1 - string_idx,
                    "fret": -1,  # muted
                    "midi": 0,
                    "note": "X",
                    "octave": 0,
                })

        if has_note:
            columns.append(column_notes)

        col += 1

    return columns


# ═══════════════════════════════════════════════════════════════════
# TAB → SHEET MUSIC
# ═══════════════════════════════════════════════════════════════════

def tab_to_notes(tab_text, tuning_key="guitar_standard"):
    """Convert tablature to a list of note events.

    Returns list of events, each being:
    {notes: [{note, octave, midi}], beat: int}
    """
    columns = parse_tab(tab_text, tuning_key)

    events = []
    for i, col in enumerate(columns):
        if not col:
            continue

        notes = []
        for n in col:
            if n["midi"] > 0:
                notes.append({
                    "note": n["note"],
                    "octave": n["octave"],
                    "midi": n["midi"],
                    "string": n["string"],
                    "fret": n["fret"],
                })

        if notes:
            events.append({
                "notes": notes,
                "beat": i,
                "is_chord": len(notes) > 1,
            })

    return events


# ═══════════════════════════════════════════════════════════════════
# SHEET MUSIC → TAB
# ═══════════════════════════════════════════════════════════════════

def notes_to_tab(note_events, tuning_key="guitar_standard", max_fret=24):
    """Convert standard notation note events to tablature.

    For each note, finds the optimal fret position on the instrument.
    Prefers lower fret positions and tries to keep hand position stable.

    note_events: list of {notes: [{note, octave}], ...}
    Returns: tab string ready to display
    """
    tuning = TUNINGS.get(tuning_key, TUNINGS["guitar_standard"])
    num_strings = len(tuning)
    string_names = get_string_names(tuning_key)

    # Build tab grid
    tab_grid = []  # list of columns, each column = [fret_per_string or None]
    last_position = 5  # preferred hand position (fret center)

    for event in note_events:
        column = [None] * num_strings

        for note_data in event.get("notes", []):
            note = note_data.get("note", "C")
            octave = note_data.get("octave", 4)
            midi = note_data.get("midi") or note_to_midi(note, octave)

            # Find all possible fret positions
            candidates = []
            for s in range(num_strings):
                fret = midi - tuning[s]
                if 0 <= fret <= max_fret:
                    # Score: prefer positions close to last hand position
                    dist = abs(fret - last_position)
                    candidates.append((s, fret, dist))

            if candidates:
                # Pick the best: closest to current hand position, prefer lower fret
                candidates.sort(key=lambda x: (x[2], x[1]))
                best_string, best_fret, _ = candidates[0]

                # Don't double-assign a string
                if column[best_string] is None:
                    column[best_string] = best_fret
                    last_position = best_fret
                else:
                    # Try next best
                    for s, f, _ in candidates[1:]:
                        if column[s] is None:
                            column[s] = f
                            break

        tab_grid.append(column)

    # Render as text tab
    if not tab_grid:
        return ""

    lines = []
    for s in range(num_strings - 1, -1, -1):  # highest string first
        label = string_names[s]
        parts = [f"{label}|"]
        for col in tab_grid:
            fret = col[s]
            if fret is not None:
                parts.append(f"-{fret}-")
            else:
                parts.append("---")
        parts.append("|")
        lines.append("".join(parts))

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# NOTATION DATA — for rendering staff notation
# ═══════════════════════════════════════════════════════════════════

# Staff line positions for treble clef (bottom line = E4)
TREBLE_STAFF = {
    'E4': 0, 'F4': 0.5, 'G4': 1, 'A4': 1.5, 'B4': 2,
    'C5': 2.5, 'D5': 3, 'E5': 3.5, 'F5': 4,
    'G5': 4.5, 'A5': 5, 'B5': 5.5, 'C6': 6,
    'D4': -0.5, 'C4': -1, 'B3': -1.5, 'A3': -2,
}

# Staff line positions for bass clef (bottom line = G2)
BASS_STAFF = {
    'G2': 0, 'A2': 0.5, 'B2': 1, 'C3': 1.5, 'D3': 2,
    'E3': 2.5, 'F3': 3, 'G3': 3.5, 'A3': 4,
    'B3': 4.5, 'C4': 5, 'D4': 5.5, 'E4': 6,
    'F2': -0.5, 'E2': -1, 'D2': -1.5, 'C2': -2,
}


def get_staff_position(note, octave, clef='treble'):
    """Get the vertical position on the staff for a note.

    Returns: float (0 = bottom line, 1 = second line, etc.)
    Negative = below staff (ledger lines), > 4 = above staff.
    """
    key = f"{note}{octave}"
    if clef == 'treble':
        return TREBLE_STAFF.get(key, _calc_position(note, octave, 'treble'))
    else:
        return BASS_STAFF.get(key, _calc_position(note, octave, 'bass'))


def _calc_position(note, octave, clef):
    """Calculate staff position for notes outside the common range."""
    # Natural note order (no sharps/flats on staff)
    natural_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    base_note = note.replace('#', '').replace('b', '')
    if base_note not in natural_order:
        return 0

    note_idx = natural_order.index(base_note)

    if clef == 'treble':
        # E4 = position 0, each natural note step = 0.5
        ref_octave = 4
        ref_idx = natural_order.index('E')
        offset = (octave - ref_octave) * 3.5 + (note_idx - ref_idx) * 0.5
    else:
        # G2 = position 0
        ref_octave = 2
        ref_idx = natural_order.index('G')
        offset = (octave - ref_octave) * 3.5 + (note_idx - ref_idx) * 0.5

    return offset


def needs_ledger_lines(position):
    """Check if a note needs ledger lines (below or above staff)."""
    lines_below = max(0, int(-position + 0.5)) if position < 0 else 0
    lines_above = max(0, int(position - 4 + 0.5)) if position > 4 else 0
    return lines_below, lines_above


def choose_clef(note_events):
    """Choose the best clef for a set of notes."""
    if not note_events:
        return 'treble'

    midis = []
    for event in note_events:
        for n in event.get("notes", []):
            midi = n.get("midi", 60)
            midis.append(midi)

    if not midis:
        return 'treble'

    avg = sum(midis) / len(midis)
    # Below middle C (60) → bass clef, above → treble
    return 'bass' if avg < 55 else 'treble'


# ═══════════════════════════════════════════════════════════════════
# NOTATION RENDERING HELPERS
# ═══════════════════════════════════════════════════════════════════

# Duration values: 1 = whole, 0.5 = half, 0.25 = quarter, 0.125 = eighth, 0.0625 = sixteenth
DURATION_NAMES = {1: "whole", 0.5: "half", 0.25: "quarter", 0.125: "eighth", 0.0625: "sixteenth"}
DURATION_BEATS = {1: 4.0, 0.5: 2.0, 0.25: 1.0, 0.125: 0.5, 0.0625: 0.25}

# Dynamic markings (rendered below staff)
DYNAMICS = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]

# Spacing multipliers per duration (wider notes for longer durations)
DURATION_SPACING = {1: 3.0, 0.5: 2.0, 0.25: 1.0, 0.125: 0.75, 0.0625: 0.6}


def _render_note_head(x, y, duration, color="#2dd4a8"):
    """Render a note head with shape based on duration.

    whole = open oval, no stem
    half = open oval + stem
    quarter/eighth/sixteenth = filled oval + stem (+ flags)
    """
    parts = []
    # Whole and half notes: open (unfilled) head
    if duration >= 0.5:
        parts.append(
            f'<ellipse cx="{x}" cy="{y}" rx="6.5" ry="4.5" '
            f'fill="none" stroke="{color}" stroke-width="1.8" '
            f'transform="rotate(-10 {x} {y})"/>'
        )
        # Whole note has a wider, more oval shape with inner line
        if duration >= 1:
            parts.append(
                f'<ellipse cx="{x}" cy="{y}" rx="3" ry="4" '
                f'fill="none" stroke="{color}" stroke-width="0.8" '
                f'transform="rotate(-10 {x} {y})"/>'
            )
    else:
        # Quarter, eighth, sixteenth: filled head
        parts.append(
            f'<ellipse cx="{x}" cy="{y}" rx="5.5" ry="4" '
            f'fill="{color}" stroke="{color}" stroke-width="1" '
            f'transform="rotate(-10 {x} {y})"/>'
        )
    return parts


def _render_stem_and_flags(x, y, pos, duration, color="#2dd4a8"):
    """Render stem (and flags for eighth/sixteenth) based on duration and position."""
    parts = []
    if duration >= 1:
        return parts  # whole notes have no stem

    # Stem direction: up if note is below middle line, down if above
    stem_up = pos < 2
    stem_x = x + (5.5 if stem_up else -5.5)
    stem_len = 30
    stem_end_y = y + (-stem_len if stem_up else stem_len)

    parts.append(
        f'<line x1="{stem_x}" y1="{y}" x2="{stem_x}" y2="{stem_end_y}" '
        f'stroke="{color}" stroke-width="1.3"/>'
    )

    # Flags for eighth notes
    if duration <= 0.125:
        flag_dir = -1 if stem_up else 1
        fy = stem_end_y
        # First flag
        if stem_up:
            parts.append(
                f'<path d="M{stem_x},{fy} C{stem_x + 8},{fy + 6} {stem_x + 10},{fy + 12} {stem_x + 4},{fy + 18}" '
                f'fill="none" stroke="{color}" stroke-width="1.5"/>'
            )
        else:
            parts.append(
                f'<path d="M{stem_x},{fy} C{stem_x - 8},{fy - 6} {stem_x - 10},{fy - 12} {stem_x - 4},{fy - 18}" '
                f'fill="none" stroke="{color}" stroke-width="1.5"/>'
            )

        # Second flag for sixteenth
        if duration <= 0.0625:
            offset = 6 if stem_up else -6
            fy2 = fy + offset
            if stem_up:
                parts.append(
                    f'<path d="M{stem_x},{fy2} C{stem_x + 8},{fy2 + 6} {stem_x + 10},{fy2 + 12} {stem_x + 4},{fy2 + 18}" '
                    f'fill="none" stroke="{color}" stroke-width="1.5"/>'
                )
            else:
                parts.append(
                    f'<path d="M{stem_x},{fy2} C{stem_x - 8},{fy2 - 6} {stem_x - 10},{fy2 - 12} {stem_x - 4},{fy2 - 18}" '
                    f'fill="none" stroke="{color}" stroke-width="1.5"/>'
                )

    return parts


def _render_rest(x, staff_top, line_spacing, duration, color="#aaa"):
    """Render a rest symbol at the given position."""
    parts = []
    center_y = staff_top + 2 * line_spacing  # middle of staff

    if duration >= 1:
        # Whole rest: filled rectangle hanging from 4th line
        ry = staff_top + 1 * line_spacing
        parts.append(
            f'<rect x="{x - 6}" y="{ry}" width="12" height="{line_spacing / 2 + 1}" '
            f'fill="{color}"/>'
        )
    elif duration >= 0.5:
        # Half rest: filled rectangle sitting on 3rd line
        ry = staff_top + 2 * line_spacing - line_spacing / 2
        parts.append(
            f'<rect x="{x - 6}" y="{ry}" width="12" height="{line_spacing / 2 + 1}" '
            f'fill="{color}"/>'
        )
    elif duration >= 0.25:
        # Quarter rest: squiggly line
        parts.append(
            f'<path d="M{x + 2},{staff_top + 8} L{x - 3},{staff_top + 14} '
            f'L{x + 3},{staff_top + 20} L{x - 2},{staff_top + 26} '
            f'L{x + 4},{staff_top + 32}" '
            f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
        )
    elif duration >= 0.125:
        # Eighth rest: dot + flag
        parts.append(
            f'<circle cx="{x + 2}" cy="{center_y - 4}" r="1.8" fill="{color}"/>'
        )
        parts.append(
            f'<path d="M{x + 2},{center_y - 4} L{x - 2},{center_y + 8}" '
            f'fill="none" stroke="{color}" stroke-width="1.5"/>'
        )
    else:
        # Sixteenth rest: two dots + two flags
        parts.append(
            f'<circle cx="{x + 2}" cy="{center_y - 7}" r="1.8" fill="{color}"/>'
        )
        parts.append(
            f'<circle cx="{x + 2}" cy="{center_y - 1}" r="1.8" fill="{color}"/>'
        )
        parts.append(
            f'<path d="M{x + 2},{center_y - 7} L{x - 2},{center_y + 8}" '
            f'fill="none" stroke="{color}" stroke-width="1.5"/>'
        )

    return parts


def _render_articulation(x, y, pos, articulation, color="#ccc"):
    """Render articulation marks on a note."""
    parts = []
    # Place above note if stem down, below if stem up
    above = pos >= 2  # stem goes up, articulation goes above
    offset = -14 if above else 14

    ay = y + offset

    if articulation == "staccato":
        parts.append(f'<circle cx="{x}" cy="{ay}" r="1.8" fill="{color}"/>')
    elif articulation == "accent":
        parts.append(
            f'<path d="M{x - 5},{ay + 3} L{x},{ay - 3} L{x + 5},{ay + 3}" '
            f'fill="none" stroke="{color}" stroke-width="1.5"/>'
        )
    elif articulation == "tenuto":
        parts.append(
            f'<line x1="{x - 5}" y1="{ay}" x2="{x + 5}" y2="{ay}" '
            f'stroke="{color}" stroke-width="1.5"/>'
        )
    elif articulation == "fermata":
        # Dot + arc above
        fy = y - 18 if pos < 2 else y - 18
        parts.append(f'<circle cx="{x}" cy="{fy + 4}" r="1.5" fill="{color}"/>')
        parts.append(
            f'<path d="M{x - 7},{fy + 7} Q{x},{fy - 5} {x + 7},{fy + 7}" '
            f'fill="none" stroke="{color}" stroke-width="1.3"/>'
        )
    elif articulation == "marcato":
        parts.append(
            f'<path d="M{x - 4},{ay + 4} L{x},{ay - 4} L{x + 4},{ay + 4}" '
            f'fill="none" stroke="{color}" stroke-width="1.8"/>'
        )
    elif articulation == "trill":
        parts.append(
            f'<text x="{x - 6}" y="{y - 18}" '
            f'font-size="12" fill="{color}" font-family="serif" font-style="italic">tr</text>'
        )

    return parts


def _render_beams(beam_group, staff_top, line_spacing, color="#2dd4a8"):
    """Render beams connecting a group of eighth/sixteenth notes.

    beam_group: list of (x, y, pos, duration) for consecutive beamable notes.
    Beams replace individual flags — a single horizontal bar for eighths,
    double bar for sixteenths.
    """
    parts = []
    if len(beam_group) < 2:
        return parts

    # Determine beam direction: majority vote on stem direction
    up_count = sum(1 for _, _, pos, _ in beam_group if pos < 2)
    stems_up = up_count > len(beam_group) / 2

    # Calculate stem endpoints
    stem_len = 30
    beam_points = []
    for x, y, pos, dur in beam_group:
        stem_x = x + (5.5 if stems_up else -5.5)
        stem_end_y = y + (-stem_len if stems_up else stem_len)
        beam_points.append((stem_x, stem_end_y, dur))

    # Primary beam (all eighth and sixteenth notes)
    first = beam_points[0]
    last = beam_points[-1]
    beam_y_start = first[1]
    beam_y_end = last[1]

    # Draw primary beam
    parts.append(
        f'<line x1="{first[0]}" y1="{beam_y_start}" '
        f'x2="{last[0]}" y2="{beam_y_end}" '
        f'stroke="{color}" stroke-width="3"/>'
    )

    # Secondary beam for sixteenth notes (duration <= 0.0625)
    # Only between consecutive sixteenth notes
    i = 0
    while i < len(beam_points):
        # Find runs of sixteenth notes
        if beam_points[i][2] <= 0.0625:
            run_start = i
            while i < len(beam_points) and beam_points[i][2] <= 0.0625:
                i += 1
            run_end = i - 1
            if run_end > run_start:
                # Full secondary beam across the run
                offset = 4 if stems_up else -4
                sx = beam_points[run_start][0]
                sy = beam_y_start + (beam_y_end - beam_y_start) * (run_start / max(1, len(beam_points) - 1)) + offset
                ex = beam_points[run_end][0]
                ey = beam_y_start + (beam_y_end - beam_y_start) * (run_end / max(1, len(beam_points) - 1)) + offset
                parts.append(
                    f'<line x1="{sx}" y1="{sy}" '
                    f'x2="{ex}" y2="{ey}" '
                    f'stroke="{color}" stroke-width="3"/>'
                )
            else:
                # Single sixteenth: short beam stub
                offset = 4 if stems_up else -4
                sx = beam_points[run_start][0]
                sy = beam_y_start + (beam_y_end - beam_y_start) * (run_start / max(1, len(beam_points) - 1)) + offset
                stub_dir = 1 if run_start == 0 else -1
                parts.append(
                    f'<line x1="{sx}" y1="{sy}" '
                    f'x2="{sx + stub_dir * 8}" y2="{sy}" '
                    f'stroke="{color}" stroke-width="3"/>'
                )
        else:
            i += 1

    return parts


def _render_volta(x1, x2, staff_top, number, color="#ccc"):
    """Render a volta bracket (1st/2nd ending)."""
    parts = []
    vy = staff_top - 16
    # Bracket
    parts.append(
        f'<path d="M{x1},{vy + 10} L{x1},{vy} L{x2},{vy}" '
        f'fill="none" stroke="{color}" stroke-width="1.3"/>'
    )
    # Number
    parts.append(
        f'<text x="{x1 + 4}" y="{vy + 9}" font-size="9" fill="{color}" '
        f'font-family="sans-serif">{number}.</text>'
    )
    return parts


def _render_multi_rest(x, staff_top, line_spacing, num_bars, color="#aaa"):
    """Render a multi-measure rest with bar count."""
    parts = []
    center_y = staff_top + 2 * line_spacing
    # Thick horizontal bar
    parts.append(
        f'<rect x="{x - 15}" y="{center_y - 3}" width="30" height="6" '
        f'fill="{color}" rx="1"/>'
    )
    # Vertical lines on each end
    parts.append(
        f'<line x1="{x - 15}" y1="{center_y - 8}" x2="{x - 15}" y2="{center_y + 8}" '
        f'stroke="{color}" stroke-width="1.5"/>'
    )
    parts.append(
        f'<line x1="{x + 15}" y1="{center_y - 8}" x2="{x + 15}" y2="{center_y + 8}" '
        f'stroke="{color}" stroke-width="1.5"/>'
    )
    # Number above
    parts.append(
        f'<text x="{x}" y="{staff_top - 4}" font-size="12" fill="{color}" '
        f'font-family="serif" font-weight="bold" text-anchor="middle">{num_bars}</text>'
    )
    return parts


def _render_triplet_bracket(x, staff_top, color="#ccc"):
    """Render a triplet bracket with '3' above the note."""
    parts = []
    ty = staff_top - 14
    parts.append(
        f'<text x="{x}" y="{ty}" font-size="10" fill="{color}" '
        f'font-family="serif" font-style="italic" text-anchor="middle">3</text>'
    )
    return parts


def _render_slur(x1, x2, y1, y2, above=True, color="#2dd4a8"):
    """Render a slur arc between two notes at different positions."""
    parts = []
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    curve_offset = -16 if above else 16
    curve_y = mid_y + curve_offset
    parts.append(
        f'<path d="M{x1 + 6},{y1} Q{mid_x},{curve_y} {x2 - 6},{y2}" '
        f'fill="none" stroke="{color}" stroke-width="1.5" stroke-opacity="0.6"/>'
    )
    return parts


def _render_crescendo(x1, x2, staff_top, staff_height, cresc=True, color="#aaa"):
    """Render crescendo (opening hairpin) or decrescendo (closing hairpin)."""
    parts = []
    y = staff_top + staff_height + 16
    if cresc:
        # Opening hairpin: < shape
        parts.append(
            f'<path d="M{x1},{y} L{x2},{y - 4} M{x1},{y} L{x2},{y + 4}" '
            f'fill="none" stroke="{color}" stroke-width="1.2"/>'
        )
    else:
        # Closing hairpin: > shape
        parts.append(
            f'<path d="M{x1},{y - 4} L{x2},{y} M{x1},{y + 4} L{x2},{y}" '
            f'fill="none" stroke="{color}" stroke-width="1.2"/>'
        )
    return parts


def _render_tempo(x, staff_top, tempo_text, color="#ddd"):
    """Render a tempo marking above the staff."""
    parts = []
    parts.append(
        f'<text x="{x}" y="{staff_top - 16}" font-size="11" fill="{color}" '
        f'font-family="serif" font-weight="bold">{tempo_text}</text>'
    )
    return parts


def _render_ottava(x1, x2, staff_top, above=True, color="#aaa"):
    """Render 8va (above) or 8vb (below) bracket."""
    parts = []
    if above:
        y = staff_top - 22
        label = "8va"
    else:
        y = staff_top + 50 + 14
        label = "8vb"
    parts.append(
        f'<text x="{x1}" y="{y + 3}" font-size="9" fill="{color}" '
        f'font-family="serif" font-style="italic">{label}</text>'
    )
    parts.append(
        f'<line x1="{x1 + 20}" y1="{y}" x2="{x2}" y2="{y}" '
        f'stroke="{color}" stroke-width="0.8" stroke-dasharray="4,3"/>'
    )
    parts.append(
        f'<line x1="{x2}" y1="{y}" x2="{x2}" y2="{y + (6 if above else -6)}" '
        f'stroke="{color}" stroke-width="0.8"/>'
    )
    return parts


def _render_pedal(x, staff_top, staff_height, action="down", color="#aaa"):
    """Render piano pedal marking (Ped. or *)."""
    parts = []
    py = staff_top + staff_height + 30
    if action == "down":
        parts.append(
            f'<text x="{x}" y="{py}" font-size="11" fill="{color}" '
            f'font-family="serif" font-style="italic">Ped.</text>'
        )
    else:
        parts.append(
            f'<text x="{x}" y="{py}" font-size="14" fill="{color}" '
            f'font-family="serif">*</text>'
        )
    return parts


def _render_coda_segno(x, staff_top, mark, color="#ddd"):
    """Render coda, segno, D.C., D.S. marks."""
    parts = []
    y = staff_top - 18
    symbols = {
        "coda": "\u00A4",          # ¤ as coda stand-in (works in all fonts)
        "segno": "%",              # % as segno stand-in
        "dc": "D.C.",
        "ds": "D.S.",
        "dc_al_fine": "D.C. al Fine",
        "ds_al_coda": "D.S. al Coda",
        "fine": "Fine",
    }
    text = symbols.get(mark, mark)
    size = "14" if mark in ("coda", "segno") else "10"
    # For coda and segno, draw actual symbols as SVG paths instead
    if mark == "segno":
        parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-family="serif" font-weight="bold" text-anchor="middle">S</text>'
        )
        # Add the segno decorations
        parts.append(
            f'<line x1="{x - 6}" y1="{y - 10}" x2="{x + 6}" y2="{y + 2}" '
            f'stroke="{color}" stroke-width="1"/>'
        )
        parts.append(f'<circle cx="{x - 4}" cy="{y - 2}" r="1.5" fill="{color}"/>')
        parts.append(f'<circle cx="{x + 4}" cy="{y - 8}" r="1.5" fill="{color}"/>')
        return parts
    if mark == "coda":
        # Circle with cross
        parts.append(
            f'<circle cx="{x}" cy="{y - 4}" r="6" fill="none" stroke="{color}" stroke-width="1.3"/>'
        )
        parts.append(
            f'<line x1="{x}" y1="{y - 12}" x2="{x}" y2="{y + 4}" stroke="{color}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{x - 8}" y1="{y - 4}" x2="{x + 8}" y2="{y - 4}" stroke="{color}" stroke-width="1"/>'
        )
        return parts
    parts.append(
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
        f'font-family="serif" font-style="italic" text-anchor="middle">{text}</text>'
    )
    return parts


def _render_grace_note(x, y, color="#2dd4a8"):
    """Render a small grace note before the main note."""
    parts = []
    gx = x - 12
    # Small filled note head
    parts.append(
        f'<ellipse cx="{gx}" cy="{y}" rx="3.5" ry="2.5" '
        f'fill="{color}" fill-opacity="0.7" transform="rotate(-10 {gx} {y})"/>'
    )
    # Small stem
    parts.append(
        f'<line x1="{gx + 3}" y1="{y}" x2="{gx + 3}" y2="{y - 16}" '
        f'stroke="{color}" stroke-width="0.8" stroke-opacity="0.7"/>'
    )
    # Slash through stem (acciaccatura)
    parts.append(
        f'<line x1="{gx}" y1="{y - 10}" x2="{gx + 6}" y2="{y - 16}" '
        f'stroke="{color}" stroke-width="0.7" stroke-opacity="0.7"/>'
    )
    return parts


def _render_measure_number(x, staff_top, number, color="#555"):
    """Render a measure number above the staff."""
    parts = []
    parts.append(
        f'<text x="{x}" y="{staff_top - 6}" font-size="8" fill="{color}" '
        f'font-family="sans-serif">{number}</text>'
    )
    return parts


def _render_tie(x1, x2, y, pos, color="#2dd4a8"):
    """Render a tie arc between two notes at positions x1 and x2, both at y."""
    parts = []
    # Tie curves away from staff center — above if stem down, below if stem up
    above = pos >= 2  # stem goes up → tie goes below; stem down → tie above
    mid_x = (x1 + x2) / 2
    curve_y = y + (10 if above else -10)
    parts.append(
        f'<path d="M{x1 + 6},{y} Q{mid_x},{curve_y} {x2 - 6},{y}" '
        f'fill="none" stroke="{color}" stroke-width="1.3" stroke-opacity="0.7"/>'
    )
    return parts


def _render_dynamic(x, staff_top, staff_height, dynamic, color="#c48dff"):
    """Render a dynamic marking below the staff."""
    parts = []
    dy = staff_top + staff_height + 22
    parts.append(
        f'<text x="{x}" y="{dy}" font-size="13" fill="{color}" '
        f'font-family="serif" font-style="italic" text-anchor="middle">{dynamic}</text>'
    )
    return parts


def _render_barline(x, staff_top, line_spacing, style="single", color="#888"):
    """Render a barline."""
    parts = []
    y1 = staff_top
    y2 = staff_top + 4 * line_spacing

    if style == "single":
        parts.append(
            f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1.5"/>'
        )
    elif style == "double":
        parts.append(
            f'<line x1="{x - 3}" y1="{y1}" x2="{x - 3}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1"/>'
        )
    elif style == "final":
        parts.append(
            f'<line x1="{x - 5}" y1="{y1}" x2="{x - 5}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{x - 1}" y1="{y1}" x2="{x - 1}" y2="{y2}" '
            f'stroke="{color}" stroke-width="3"/>'
        )
    elif style == "repeat_start":
        parts.append(
            f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" '
            f'stroke="{color}" stroke-width="3"/>'
        )
        parts.append(
            f'<line x1="{x + 4}" y1="{y1}" x2="{x + 4}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1"/>'
        )
        dot_y1 = staff_top + 1.5 * line_spacing
        dot_y2 = staff_top + 2.5 * line_spacing
        parts.append(f'<circle cx="{x + 8}" cy="{dot_y1}" r="1.8" fill="{color}"/>')
        parts.append(f'<circle cx="{x + 8}" cy="{dot_y2}" r="1.8" fill="{color}"/>')
    elif style == "repeat_end":
        dot_y1 = staff_top + 1.5 * line_spacing
        dot_y2 = staff_top + 2.5 * line_spacing
        parts.append(f'<circle cx="{x - 8}" cy="{dot_y1}" r="1.8" fill="{color}"/>')
        parts.append(f'<circle cx="{x - 8}" cy="{dot_y2}" r="1.8" fill="{color}"/>')
        parts.append(
            f'<line x1="{x - 4}" y1="{y1}" x2="{x - 4}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" '
            f'stroke="{color}" stroke-width="3"/>'
        )

    return parts


# ═══════════════════════════════════════════════════════════════════
# NOTATION RENDERING — SVG output
# ═══════════════════════════════════════════════════════════════════

def render_notation_svg(note_events, key='C', time_sig='4/4', clef=None,
                       width=800, note_spacing=40):
    """Render note events as an SVG music staff with full notation.

    Each event can have:
        notes: [{note, octave, midi}]     — the pitches
        beat: float                        — position in beats
        duration: float                    — 1/0.5/0.25/0.125/0.0625
        type: "note" or "rest"            — rests rendered as rest symbols
        dynamic: "pp"/"p"/"mp"/"mf"/"f"/"ff"  — shown below staff
        articulation: "staccato"/"accent"/"tenuto"/"fermata"/"marcato"/"trill"
        barline: "single"/"double"/"final"/"repeat_start"/"repeat_end"

    Returns SVG string ready to embed in HTML.
    """
    if clef is None:
        clef = choose_clef(note_events)

    staff_top = 60
    line_spacing = 10
    staff_height = line_spacing * 4

    # Parse time signature for bar lines
    ts_parts = time_sig.split('/')
    beats_per_bar = int(ts_parts[0])
    beat_unit = int(ts_parts[1])
    # Beats per bar in quarter-note units
    bar_length = beats_per_bar * (4.0 / beat_unit)

    height = staff_top + staff_height + 50
    margin_left = 80

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="background:#1a1a2e;">',
    ]

    # Staff lines
    for i in range(5):
        y = staff_top + i * line_spacing
        svg_parts.append(
            f'<line x1="{margin_left - 10}" y1="{y}" x2="{width - 20}" y2="{y}" '
            f'stroke="#555" stroke-width="1"/>'
        )

    # Clef
    if clef == 'treble':
        svg_parts.append(
            f'<text x="{margin_left - 5}" y="{staff_top + 32}" '
            f'font-size="42" fill="#aaa" font-family="serif">\U0001D11E</text>'
        )
    else:
        svg_parts.append(
            f'<text x="{margin_left - 5}" y="{staff_top + 28}" '
            f'font-size="36" fill="#aaa" font-family="serif">\U0001D122</text>'
        )

    # Key signature
    num_sharps_flats = KEY_SIGNATURES.get(key, 0)
    ks_x = margin_left + 30
    if num_sharps_flats > 0:
        sharp_positions = [4, 2.5, 4.5, 3, 1.5, 3.5, 2]
        for i in range(min(num_sharps_flats, 7)):
            y = staff_top + (4 - sharp_positions[i]) * line_spacing
            svg_parts.append(
                f'<text x="{ks_x + i * 10}" y="{y + 4}" '
                f'font-size="14" fill="#ccc" font-family="serif">\u266F</text>'
            )
    elif num_sharps_flats < 0:
        flat_positions = [2, 3.5, 1.5, 3, 1, 2.5, 0.5]
        for i in range(min(-num_sharps_flats, 7)):
            y = staff_top + (4 - flat_positions[i]) * line_spacing
            svg_parts.append(
                f'<text x="{ks_x + i * 10}" y="{y + 4}" '
                f'font-size="14" fill="#ccc" font-family="serif">\u266D</text>'
            )

    # Time signature
    ts_x = margin_left + 30 + abs(num_sharps_flats) * 10 + 10
    svg_parts.append(
        f'<text x="{ts_x}" y="{staff_top + 15}" '
        f'font-size="18" fill="#ccc" font-weight="bold" font-family="serif">{beats_per_bar}</text>'
    )
    svg_parts.append(
        f'<text x="{ts_x}" y="{staff_top + 35}" '
        f'font-size="18" fill="#ccc" font-weight="bold" font-family="serif">{beat_unit}</text>'
    )

    # Pre-pass: identify beam groups (consecutive eighth/sixteenth notes)
    beam_groups = []  # list of sets of event indices that should be beamed
    current_beam = []
    for i, event in enumerate(note_events):
        dur = event.get("duration", 0.25)
        is_beamable = dur <= 0.125 and event.get("type") != "rest" and event.get("notes")
        if is_beamable:
            current_beam.append(i)
        else:
            if len(current_beam) >= 2:
                beam_groups.append(current_beam)
            current_beam = []
    if len(current_beam) >= 2:
        beam_groups.append(current_beam)

    # Set of indices that are part of a beam group
    beamed_indices = set()
    for group in beam_groups:
        for idx in group:
            beamed_indices.add(idx)

    # Render notes and rests with proper spacing
    start_x = ts_x + 30
    base_spacing = note_spacing
    last_barline_beat = 0
    beam_data = {}  # idx -> (x, y, pos, dur) for beam rendering

    for i, event in enumerate(note_events):
        dur = event.get("duration", 0.25)
        spacing = base_spacing * DURATION_SPACING.get(dur, 1.0)
        x = start_x + i * base_spacing

        if x > width - 30:
            break

        # Bar lines — placed halfway between previous note and this one
        beat = event.get("beat", i)
        if bar_length > 0 and beat > 0:
            bar_num = beat / bar_length
            last_bar = last_barline_beat / bar_length
            if int(bar_num) > int(last_bar):
                bar_x = x - base_spacing * 0.5
                svg_parts.extend(_render_barline(bar_x, staff_top, line_spacing))
        last_barline_beat = beat

        # Explicit barline in event
        bl = event.get("barline")
        if bl:
            svg_parts.extend(_render_barline(x - 8, staff_top, line_spacing, style=bl))

        # Measure numbers (at barline positions)
        if bar_length > 0 and beat > 0 and i > 0:
            bar_num_check = beat / bar_length
            if bar_num_check == int(bar_num_check) and bar_num_check > 0:
                svg_parts.extend(_render_measure_number(x - 4, staff_top, int(bar_num_check) + 1))

        # Tempo marking
        tempo = event.get("tempo")
        if tempo:
            svg_parts.extend(_render_tempo(x, staff_top, tempo))

        # Coda / Segno / D.C. / D.S.
        nav = event.get("navigation")
        if nav:
            svg_parts.extend(_render_coda_segno(x, staff_top, nav))

        # Dynamic marking
        dyn = event.get("dynamic")
        if dyn:
            svg_parts.extend(_render_dynamic(x, staff_top, staff_height, dyn))

        # Crescendo/decrescendo hairpins
        if event.get("crescendo"):
            if i + 1 < len(note_events):
                next_x = start_x + (i + 1) * base_spacing
            else:
                next_x = x + base_spacing * 2  # extend 2 beats if no next event
            svg_parts.extend(_render_crescendo(x, min(next_x, width - 30), staff_top, staff_height, cresc=True))
        if event.get("decrescendo"):
            if i + 1 < len(note_events):
                next_x = start_x + (i + 1) * base_spacing
            else:
                next_x = x + base_spacing * 2
            svg_parts.extend(_render_crescendo(x, min(next_x, width - 30), staff_top, staff_height, cresc=False))

        # Triplet bracket
        if event.get("triplet"):
            svg_parts.extend(_render_triplet_bracket(x, staff_top))

        # Pedal markings
        pedal = event.get("pedal")
        if pedal:
            svg_parts.extend(_render_pedal(x, staff_top, staff_height, action=pedal))

        # REST
        if event.get("type") == "rest":
            svg_parts.extend(_render_rest(x, staff_top, line_spacing, dur))
            continue

        # NOTES
        for note_data in event.get("notes", []):
            note = note_data.get("note", "C")
            octave = note_data.get("octave", 4)
            # Per-note duration overrides event duration (for polyphonic voices)
            note_dur = note_data.get("duration", dur)

            pos = get_staff_position(note, octave, clef)
            y = staff_top + (4 - pos) * line_spacing

            # Grace note (small note before main note)
            if event.get("grace_note"):
                svg_parts.extend(_render_grace_note(x, y))

            # Note head (shape depends on this note's duration)
            svg_parts.extend(_render_note_head(x, y, note_dur))

            # Stem — if beamed, draw stem only (no flags); beams added later
            if i in beamed_indices:
                # Stem only, no flags
                if note_dur < 1:  # not a whole note
                    stem_up = pos < 2
                    stem_x = x + (5.5 if stem_up else -5.5)
                    stem_end_y = y + (-30 if stem_up else 30)
                    svg_parts.append(
                        f'<line x1="{stem_x}" y1="{y}" x2="{stem_x}" y2="{stem_end_y}" '
                        f'stroke="#2dd4a8" stroke-width="1.3"/>'
                    )
                beam_data[i] = (x, y, pos, note_dur)
            else:
                svg_parts.extend(_render_stem_and_flags(x, y, pos, note_dur))

            # Ledger lines
            lines_below, lines_above = needs_ledger_lines(pos)
            for ll in range(lines_below):
                ly = staff_top + (5 + ll) * line_spacing
                svg_parts.append(
                    f'<line x1="{x - 10}" y1="{ly}" x2="{x + 10}" y2="{ly}" '
                    f'stroke="#555" stroke-width="1"/>'
                )
            for ll in range(lines_above):
                ly = staff_top - (1 + ll) * line_spacing
                svg_parts.append(
                    f'<line x1="{x - 10}" y1="{ly}" x2="{x + 10}" y2="{ly}" '
                    f'stroke="#555" stroke-width="1"/>'
                )

            # Sharp/flat accidental
            if '#' in note:
                svg_parts.append(
                    f'<text x="{x - 14}" y="{y + 4}" '
                    f'font-size="12" fill="#ccc" font-family="serif">\u266F</text>'
                )
            elif 'b' in note and len(note) > 1:
                svg_parts.append(
                    f'<text x="{x - 14}" y="{y + 4}" '
                    f'font-size="12" fill="#ccc" font-family="serif">\u266D</text>'
                )

            # Articulation
            art = event.get("articulation")
            if art:
                svg_parts.extend(_render_articulation(x, y, pos, art))

            # Dot for dotted notes
            if event.get("dotted"):
                svg_parts.append(
                    f'<circle cx="{x + 9}" cy="{y}" r="1.5" fill="#2dd4a8"/>'
                )

            # Tie — draw arc to next event if tie is set
            if event.get("tie") and i + 1 < len(note_events):
                next_x = start_x + (i + 1) * base_spacing
                if next_x <= width - 30:
                    svg_parts.extend(_render_tie(x, next_x, y, pos))

            # Slur — connects different pitches (legato)
            if event.get("slur"):
                if i + 1 < len(note_events):
                    next_event = note_events[i + 1]
                    next_x = start_x + (i + 1) * base_spacing
                    if next_x <= width - 30:
                        if next_event.get("notes"):
                            next_note = next_event["notes"][0]
                            next_pos = get_staff_position(
                                next_note.get("note", "C"),
                                next_note.get("octave", 4), clef)
                            next_y = staff_top + (4 - next_pos) * line_spacing
                        else:
                            next_y = y  # same height if next has no notes
                        above = pos < 2
                        svg_parts.extend(_render_slur(x, next_x, y, next_y, above=above))
                else:
                    # No next event — draw short slur
                    next_x = x + base_spacing
                    above = pos < 2
                    svg_parts.extend(_render_slur(x, next_x, y, y, above=above))

    # Render beams for beam groups
    for group in beam_groups:
        beam_notes = [beam_data[idx] for idx in group if idx in beam_data]
        if len(beam_notes) >= 2:
            svg_parts.extend(_render_beams(beam_notes, staff_top, line_spacing))

    # Volta brackets (1st/2nd endings)
    for i, event in enumerate(note_events):
        volta = event.get("volta")
        if volta and i + 1 < len(note_events):
            x1 = start_x + i * base_spacing
            # Find end of volta (next volta or end)
            end_i = i + 1
            while end_i < len(note_events) and not note_events[end_i].get("volta"):
                end_i += 1
            x2 = start_x + min(end_i, len(note_events) - 1) * base_spacing
            svg_parts.extend(_render_volta(x1, x2, staff_top, volta))

    # Multi-measure rests
    for i, event in enumerate(note_events):
        multi_rest = event.get("multi_rest")
        if multi_rest:
            x = start_x + i * base_spacing
            svg_parts.extend(_render_multi_rest(x, staff_top, line_spacing, multi_rest))

    # Ottava lines
    for i, event in enumerate(note_events):
        ottava = event.get("ottava")
        if ottava and i + 1 < len(note_events):
            x1 = start_x + i * base_spacing
            # Find end of ottava marking
            end_i = i + 1
            while end_i < len(note_events) and not note_events[end_i].get("ottava_end"):
                end_i += 1
            x2 = start_x + min(end_i, len(note_events) - 1) * base_spacing
            svg_parts.extend(_render_ottava(x1, x2, staff_top,
                                           above=(ottava == "8va")))

    # Final barline
    svg_parts.extend(_render_barline(width - 22, staff_top, line_spacing, style="final"))

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


# ═══════════════════════════════════════════════════════════════════
# TAB RENDERING — text + visual
# ═══════════════════════════════════════════════════════════════════

def render_tab_svg(tab_text, tuning_key="guitar_standard",
                  width=800, fret_spacing=30):
    """Render tablature as SVG with string lines and fret numbers."""
    tuning = TUNINGS.get(tuning_key, TUNINGS["guitar_standard"])
    string_names = get_string_names(tuning_key)
    num_strings = len(tuning)

    columns = parse_tab(tab_text, tuning_key)
    if not columns:
        return ""

    line_spacing = 16
    top = 30
    margin_left = 40
    height = top + num_strings * line_spacing + 30

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="background:#1a1a2e;">',
    ]

    # String lines
    for s in range(num_strings):
        y = top + (num_strings - 1 - s) * line_spacing
        svg_parts.append(
            f'<line x1="{margin_left}" y1="{y}" x2="{width - 20}" y2="{y}" '
            f'stroke="#444" stroke-width="1"/>'
        )
        # String label
        svg_parts.append(
            f'<text x="10" y="{y + 4}" font-size="12" fill="#888" '
            f'font-family="monospace">{string_names[s]}</text>'
        )

    # Fret numbers
    for i, col in enumerate(columns):
        x = margin_left + 20 + i * fret_spacing
        if x > width - 30:
            break
        for note in col:
            s = note["string"]
            fret = note["fret"]
            y = top + (num_strings - 1 - s) * line_spacing
            if fret >= 0:
                svg_parts.append(
                    f'<rect x="{x - 7}" y="{y - 8}" width="14" height="16" '
                    f'fill="#1a1a2e" rx="2"/>'
                )
                svg_parts.append(
                    f'<text x="{x}" y="{y + 4}" font-size="12" fill="#2dd4a8" '
                    f'text-anchor="middle" font-family="monospace">{fret}</text>'
                )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


# ═══════════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════════

def render_orchestral_score(parts, key='C', time_sig='4/4', width=900):
    """Render a multi-staff orchestral score with full notation.

    parts: list of {name, clef, events} where:
        name: instrument name (e.g. "Violin I")
        clef: "treble" or "bass"
        events: list of {notes, beat, duration, type, dynamic, articulation}

    Returns SVG string with all staves stacked vertically,
    connected by a system bracket on the left.
    """
    if not parts:
        return ""

    staff_height = 50  # 5 lines * 10px spacing
    staff_gap = 60     # gap between staves
    line_spacing = 10
    margin_top = 40
    margin_left = 100

    # Parse time signature for bar lines
    ts_parts = time_sig.split('/')
    beats_per_bar = int(ts_parts[0])
    beat_unit = int(ts_parts[1])
    bar_length = beats_per_bar * (4.0 / beat_unit)

    total_height = margin_top + len(parts) * (staff_height + staff_gap) + 40

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" '
        f'viewBox="0 0 {width} {total_height}" style="background:#1a1a2e;">'
    ]

    # System bracket
    first_staff_y = margin_top
    last_staff_y = margin_top + (len(parts) - 1) * (staff_height + staff_gap) + staff_height
    svg.append(
        f'<line x1="{margin_left - 15}" y1="{first_staff_y}" '
        f'x2="{margin_left - 15}" y2="{last_staff_y}" '
        f'stroke="#888" stroke-width="3"/>'
    )
    svg.append(
        f'<path d="M{margin_left - 18},{first_staff_y} Q{margin_left - 25},{(first_staff_y + last_staff_y) / 2} {margin_left - 18},{last_staff_y}" '
        f'fill="none" stroke="#888" stroke-width="2"/>'
    )

    num_sf = KEY_SIGNATURES.get(key, 0)

    for part_idx, part in enumerate(parts):
        staff_top = margin_top + part_idx * (staff_height + staff_gap)
        clef = part.get("clef", "treble")
        name = part.get("name", f"Part {part_idx + 1}")
        events = part.get("events", [])

        # Instrument name
        name_y = staff_top + staff_height // 2 + 4
        svg.append(
            f'<text x="{margin_left - 20}" y="{name_y}" '
            f'font-size="10" fill="#aaa" font-family="sans-serif" '
            f'text-anchor="end">{name}</text>'
        )

        # Staff lines
        for i in range(5):
            y = staff_top + i * line_spacing
            svg.append(
                f'<line x1="{margin_left}" y1="{y}" x2="{width - 20}" y2="{y}" '
                f'stroke="#555" stroke-width="1"/>'
            )

        # Clef
        if clef == 'treble':
            svg.append(
                f'<text x="{margin_left + 5}" y="{staff_top + 32}" '
                f'font-size="38" fill="#aaa" font-family="serif">\U0001D11E</text>'
            )
        else:
            svg.append(
                f'<text x="{margin_left + 5}" y="{staff_top + 28}" '
                f'font-size="32" fill="#aaa" font-family="serif">\U0001D122</text>'
            )

        # Time signature
        ks_x = margin_left + 40
        ts_x = ks_x + abs(num_sf) * 10 + 10
        svg.append(
            f'<text x="{ts_x}" y="{staff_top + 15}" '
            f'font-size="16" fill="#ccc" font-weight="bold" font-family="serif">{beats_per_bar}</text>'
        )
        svg.append(
            f'<text x="{ts_x}" y="{staff_top + 33}" '
            f'font-size="16" fill="#ccc" font-weight="bold" font-family="serif">{beat_unit}</text>'
        )

        # Notes, rests, bar lines
        note_spacing = 35
        start_x = ts_x + 30
        last_barline_beat = 0

        for i, event in enumerate(events):
            dur = event.get("duration", 0.25)
            x = start_x + i * note_spacing
            if x > width - 30:
                break

            beat = event.get("beat", i)

            # Auto bar lines
            if bar_length > 0 and beat > 0:
                bar_num = beat / bar_length
                last_bar = last_barline_beat / bar_length
                if int(bar_num) > int(last_bar):
                    bar_x = x - note_spacing * 0.5
                    svg.extend(_render_barline(bar_x, staff_top, line_spacing))
            last_barline_beat = beat

            # Measure numbers
            if bar_length > 0 and beat > 0:
                bar_num_check = beat / bar_length
                if bar_num_check == int(bar_num_check) and bar_num_check > 0:
                    svg.extend(_render_measure_number(x - 4, staff_top, int(bar_num_check) + 1))

            # Tempo marking
            tempo = event.get("tempo")
            if tempo:
                svg.extend(_render_tempo(x, staff_top, tempo))

            # Coda / Segno / D.C. / D.S.
            nav = event.get("navigation")
            if nav:
                svg.extend(_render_coda_segno(x, staff_top, nav))

            # Dynamic
            dyn = event.get("dynamic")
            if dyn:
                svg.extend(_render_dynamic(x, staff_top, staff_height, dyn))

            # Crescendo/decrescendo hairpins
            if event.get("crescendo"):
                next_x = start_x + (i + 1) * note_spacing if i + 1 < len(events) else x + note_spacing * 2
                svg.extend(_render_crescendo(x, min(next_x, width - 30), staff_top, staff_height, cresc=True))
            if event.get("decrescendo"):
                next_x = start_x + (i + 1) * note_spacing if i + 1 < len(events) else x + note_spacing * 2
                svg.extend(_render_crescendo(x, min(next_x, width - 30), staff_top, staff_height, cresc=False))

            # Triplet bracket
            if event.get("triplet"):
                svg.extend(_render_triplet_bracket(x, staff_top))

            # Pedal markings
            pedal = event.get("pedal")
            if pedal:
                svg.extend(_render_pedal(x, staff_top, staff_height, action=pedal))

            # Explicit barline
            bl = event.get("barline")
            if bl:
                svg.extend(_render_barline(x - 8, staff_top, line_spacing, style=bl))

            # Rest
            if event.get("type") == "rest":
                svg.extend(_render_rest(x, staff_top, line_spacing, dur))
                continue

            for note_data in event.get("notes", []):
                note = note_data.get("note", "C")
                octave = note_data.get("octave", 4)
                note_dur = note_data.get("duration", dur)
                pos = get_staff_position(note, octave, clef)
                y = staff_top + (4 - pos) * line_spacing

                # Grace note
                if event.get("grace_note"):
                    svg.extend(_render_grace_note(x, y))

                svg.extend(_render_note_head(x, y, note_dur))
                svg.extend(_render_stem_and_flags(x, y, pos, note_dur))

                # Ledger lines
                lines_below, lines_above = needs_ledger_lines(pos)
                for ll in range(lines_below):
                    ly = staff_top + (5 + ll) * line_spacing
                    svg.append(
                        f'<line x1="{x - 8}" y1="{ly}" x2="{x + 8}" y2="{ly}" '
                        f'stroke="#555" stroke-width="1"/>'
                    )
                for ll in range(lines_above):
                    ly = staff_top - (1 + ll) * line_spacing
                    svg.append(
                        f'<line x1="{x - 8}" y1="{ly}" x2="{x + 8}" y2="{ly}" '
                        f'stroke="#555" stroke-width="1"/>'
                    )

                # Accidentals
                if '#' in note:
                    svg.append(
                        f'<text x="{x - 13}" y="{y + 4}" '
                        f'font-size="11" fill="#ccc" font-family="serif">\u266F</text>'
                    )
                elif 'b' in note and len(note) > 1:
                    svg.append(
                        f'<text x="{x - 13}" y="{y + 4}" '
                        f'font-size="11" fill="#ccc" font-family="serif">\u266D</text>'
                    )

                # Articulation
                art = event.get("articulation")
                if art:
                    svg.extend(_render_articulation(x, y, pos, art))

                # Dotted note
                if event.get("dotted"):
                    svg.append(
                        f'<circle cx="{x + 9}" cy="{y}" r="1.5" fill="#2dd4a8"/>'
                    )

                # Tie
                if event.get("tie") and i + 1 < len(events):
                    next_x = start_x + (i + 1) * note_spacing
                    if next_x <= width - 30:
                        svg.extend(_render_tie(x, next_x, y, pos))

                # Slur
                if event.get("slur"):
                    if i + 1 < len(events):
                        next_event = events[i + 1]
                        next_x = start_x + (i + 1) * note_spacing
                        if next_x <= width - 30:
                            if next_event.get("notes"):
                                nn = next_event["notes"][0]
                                next_pos = get_staff_position(nn.get("note","C"), nn.get("octave",4), clef)
                                next_y = staff_top + (4 - next_pos) * line_spacing
                            else:
                                next_y = y
                            svg.extend(_render_slur(x, next_x, y, next_y, above=(pos < 2)))
                    else:
                        svg.extend(_render_slur(x, x + note_spacing, y, y, above=(pos < 2)))

        # Final barline for each staff
        svg.extend(_render_barline(width - 22, staff_top, line_spacing, style="final"))

    svg.append('</svg>')
    return '\n'.join(svg)


def list_tunings(instrument=None):
    """List available tunings, optionally filtered by instrument."""
    result = []
    for key, name in TUNING_NAMES.items():
        if instrument:
            if instrument.lower() not in key.lower():
                continue
        result.append({
            "id": key,
            "name": name,
            "strings": len(TUNINGS[key]),
            "notes": get_string_names(key),
        })
    return result
