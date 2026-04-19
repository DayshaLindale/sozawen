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
# NOTATION RENDERING — SVG output
# ═══════════════════════════════════════════════════════════════════

def render_notation_svg(note_events, key='C', time_sig='4/4', clef=None,
                       width=800, note_spacing=40):
    """Render note events as an SVG music staff.

    Returns SVG string ready to embed in HTML.
    """
    if clef is None:
        clef = choose_clef(note_events)

    staff_top = 60
    line_spacing = 10
    staff_height = line_spacing * 4

    height = staff_top + staff_height + 80
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
            f'font-size="42" fill="#aaa" font-family="serif">𝄞</text>'
        )
    else:
        svg_parts.append(
            f'<text x="{margin_left - 5}" y="{staff_top + 28}" '
            f'font-size="36" fill="#aaa" font-family="serif">𝄢</text>'
        )

    # Key signature
    num_sharps_flats = KEY_SIGNATURES.get(key, 0)
    ks_x = margin_left + 30
    if num_sharps_flats > 0:
        sharp_positions = [4, 2.5, 4.5, 3, 1.5, 3.5, 2]  # F C G D A E B
        for i in range(min(num_sharps_flats, 7)):
            y = staff_top + (4 - sharp_positions[i]) * line_spacing
            svg_parts.append(
                f'<text x="{ks_x + i * 10}" y="{y + 4}" '
                f'font-size="14" fill="#ccc" font-family="serif">♯</text>'
            )
    elif num_sharps_flats < 0:
        flat_positions = [2, 3.5, 1.5, 3, 1, 2.5, 0.5]  # B E A D G C F
        for i in range(min(-num_sharps_flats, 7)):
            y = staff_top + (4 - flat_positions[i]) * line_spacing
            svg_parts.append(
                f'<text x="{ks_x + i * 10}" y="{y + 4}" '
                f'font-size="14" fill="#ccc" font-family="serif">♭</text>'
            )

    # Time signature
    ts_x = margin_left + 30 + abs(num_sharps_flats) * 10 + 10
    beats, beat_type = time_sig.split('/')
    svg_parts.append(
        f'<text x="{ts_x}" y="{staff_top + 15}" '
        f'font-size="18" fill="#ccc" font-weight="bold" font-family="serif">{beats}</text>'
    )
    svg_parts.append(
        f'<text x="{ts_x}" y="{staff_top + 35}" '
        f'font-size="18" fill="#ccc" font-weight="bold" font-family="serif">{beat_type}</text>'
    )

    # Notes
    start_x = ts_x + 30
    for i, event in enumerate(note_events):
        x = start_x + i * note_spacing

        if x > width - 30:
            break

        for note_data in event.get("notes", []):
            note = note_data.get("note", "C")
            octave = note_data.get("octave", 4)

            pos = get_staff_position(note, octave, clef)
            y = staff_top + (4 - pos) * line_spacing

            # Note head (filled oval)
            is_sharp = '#' in note or (note in ENHARMONIC.values() and '#' in note)

            svg_parts.append(
                f'<ellipse cx="{x}" cy="{y}" rx="6" ry="4.5" '
                f'fill="#2dd4a8" stroke="#2dd4a8" stroke-width="1" '
                f'transform="rotate(-10 {x} {y})"/>'
            )

            # Stem
            stem_dir = -1 if pos >= 2 else 1  # up if below middle, down if above
            stem_y = y + stem_dir * 30
            svg_parts.append(
                f'<line x1="{x + 5 * (-stem_dir)}" y1="{y}" '
                f'x2="{x + 5 * (-stem_dir)}" y2="{stem_y}" '
                f'stroke="#2dd4a8" stroke-width="1.5"/>'
            )

            # Ledger lines
            lines_below, lines_above = needs_ledger_lines(pos)
            for l in range(lines_below):
                ly = staff_top + (5 + l) * line_spacing
                svg_parts.append(
                    f'<line x1="{x - 10}" y1="{ly}" x2="{x + 10}" y2="{ly}" '
                    f'stroke="#555" stroke-width="1"/>'
                )
            for l in range(lines_above):
                ly = staff_top - (1 + l) * line_spacing
                svg_parts.append(
                    f'<line x1="{x - 10}" y1="{ly}" x2="{x + 10}" y2="{ly}" '
                    f'stroke="#555" stroke-width="1"/>'
                )

            # Sharp/flat accidental
            if '#' in note:
                svg_parts.append(
                    f'<text x="{x - 14}" y="{y + 4}" '
                    f'font-size="12" fill="#ccc" font-family="serif">♯</text>'
                )

            # Note name below staff (for learning)
            svg_parts.append(
                f'<text x="{x - 4}" y="{staff_top + staff_height + 20}" '
                f'font-size="9" fill="#666" font-family="sans-serif">'
                f'{note}{octave}</text>'
            )

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
