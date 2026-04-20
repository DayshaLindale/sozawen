"""Sozawen Context Engine — the program reads the room.

Watches what the user is doing and surfaces relevant tools automatically.
No mode switching. No tab clicking. The workspace adapts.

Context is determined by:
  - Track count (0 = onboarding, 1 = single track, 2+ = mixing)
  - Transport state (stopped, playing, recording)
  - Last user action (drop, select, edit, solo)
  - Audio content (detected issues, characteristics)
  - Time since last interaction (idle = suggestions)

Each context produces a tool priority list. The UI renders the top tools
prominently and fades the rest into a drawer.
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger("sozawen.context")


class Phase(Enum):
    """Where the user is in their workflow."""
    EMPTY = "empty"           # no tracks, fresh session
    IMPORT = "import"         # just dropped/loaded a file
    RECORD = "record"         # recording active
    EDIT = "edit"             # working with clips on timeline
    MIX = "mix"               # multiple tracks, adjusting levels
    MASTER = "master"         # master bus focused
    EXPORT = "export"         # preparing to export


class Action(Enum):
    """What the user just did."""
    NONE = "none"
    DROP_FILE = "drop_file"
    OPEN_FILE = "open_file"
    ADD_TRACK = "add_track"
    HIT_RECORD = "hit_record"
    HIT_PLAY = "hit_play"
    HIT_STOP = "hit_stop"
    SELECT_REGION = "select_region"
    SELECT_TRACK = "select_track"
    SELECT_TOOL = "select_tool"
    SOLO_TRACK = "solo_track"
    MUTE_TRACK = "mute_track"
    ADJUST_VOLUME = "adjust_volume"
    ADJUST_PAN = "adjust_pan"
    SPLIT_CLIP = "split_clip"
    RUN_SEPARATION = "run_separation"
    RUN_LYRICS = "run_lyrics"
    RUN_CLEANUP = "run_cleanup"
    SOLO_MASTER = "solo_master"
    IDLE = "idle"


@dataclass
class AudioIssue:
    """A detected issue in the audio."""
    type: str          # "clipping", "hum", "noise", "low_volume", "dc_offset"
    severity: float    # 0-1
    location: float    # seconds where it occurs (0 = whole file)
    description: str
    fix_available: bool = True


@dataclass
class ContextState:
    """Current state of the workspace context."""
    phase: Phase = Phase.EMPTY
    last_action: Action = Action.NONE
    last_action_time: float = 0
    track_count: int = 0
    selected_track_id: int = -1
    is_playing: bool = False
    is_recording: bool = False
    has_selection: bool = False
    audio_issues: list = field(default_factory=list)

    # Tool visibility — 0.0 (hidden) to 1.0 (prominent)
    tool_weights: dict = field(default_factory=dict)


# Tool definitions with their contexts
TOOLS = {
    # Import/Analysis tools
    # ═══ IMPORT / START ═══
    "open_file":    {"label": "Open File",        "icon": "📂", "group": "import",
                     "tip": "Start here. Import audio files to work with. After: Analyze to detect key/BPM, or Stem Split to separate instruments."},
    "stem_split":   {"label": "Stem Separation",  "icon": "✂", "group": "import",
                     "tip": "Separates a full mix into vocals, drums, bass, guitar, piano. Use after importing a song. After: Edit individual stems, or use as backing tracks."},
    "lyrics":       {"label": "Lyrics",           "icon": "♪", "group": "import",
                     "tip": "Transcribes vocals to text with timestamps. Use after recording or importing vocals. Export as LRC for karaoke or SRT for subtitles."},
    "analyze":      {"label": "Analyze",          "icon": "≈", "group": "import",
                     "tip": "Detects key, BPM, loudness, and duration. Use first on any imported track. After: Set your project BPM to match, or use key info for the Chord Builder."},
    "bandmate":     {"label": "Bandmate",         "icon": "💬", "group": "import",
                     "tip": "AI collaborator that sees your session — key, BPM, tracks, instruments — and suggests what to try next. Use anytime you're stuck."},
    "sample_browser":{"label": "Samples",         "icon": "📁", "group": "import",
                     "tip": "Browse your computer for audio files. Click to add to a track. Use when building arrangements from existing sounds."},
    "chord_detect": {"label": "Detect Chords",    "icon": "🎶", "group": "import",
                     "tip": "Analyzes audio and identifies chords playing at each moment. Use after importing a song to learn what chords it uses. After: Use Chord Builder to write your own progression."},
    "audio_to_midi":{"label": "Audio to MIDI",    "icon": "🎵", "group": "import",
                     "tip": "Converts a monophonic recording (vocals, bass, lead) into MIDI notes. Use to capture a melody you sang, then render it through any instrument."},
    "community":    {"label": "Community",        "icon": "🌐", "group": "master",
                     "tip": "Connect with other Sozawen musicians. Share work, get feedback, find collaborators."},

    # ═══ CREATE / RECORD ═══
    "instruments":  {"label": "Instruments",      "icon": "🎻", "group": "record",
                     "tip": "62 physically modeled instruments — guitar, bass, piano, strings, brass, woodwinds, percussion. Pick a family, choose a model, play the keyboard. All from physics, no samples."},
    "synth":        {"label": "Synth",            "icon": "🎹", "group": "record",
                     "tip": "Subtractive synthesizer — 4 waveforms, filter, ADSR envelope. Create pads, leads, bass. Use for electronic textures or layering with real instruments."},
    "drums":        {"label": "Drum Machine",     "icon": "🥁", "group": "record",
                     "tip": "18 physics-modeled drum sounds, 20 genre presets with verse/chorus/bridge sections. Build complete song structures. Use before recording other instruments — drums are the foundation."},
    "pad":          {"label": "Pad",              "icon": "🎛", "group": "record",
                     "tip": "MPC-style performance pad — tap to play sounds, build patterns by feel. Mapped to your key and scale. Use for quick ideas and jamming."},
    "vocal_tune":   {"label": "Vocal Tuning",      "icon": "🎤", "group": "edit",
                     "tip": "Pitch correction for vocals. Subtle correction (20-40%) keeps it natural. Heavy correction (80-100%) creates the Auto-Tune effect. Set your song key first. Use AFTER recording, BEFORE mixing."},
    "tempo_map":    {"label": "Tempo Map",        "icon": "⏱", "group": "edit",
                     "tip": "Change tempo mid-song. Add tempo change points along the timeline. Essential for live recordings that speed up/slow down, or for dramatic ritardando/accelerando in composed music."},
    "templates":    {"label": "Templates",         "icon": "📋", "group": "import",
                     "tip": "Pre-configured project sessions. Songwriting, Band Recording, Beat Making, Podcast, Mixing, Orchestral — start making music immediately instead of configuring software."},
    "spectrum":     {"label": "Spectrum Analyzer", "icon": "📊", "group": "mix",
                     "tip": "Real-time frequency display. See where sounds clash between tracks. Essential for EQ decisions — carve space for each instrument. Includes oscilloscope mode for sound design."},
    "lyrics_editor":{"label": "Lyrics Editor",    "icon": "✍", "group": "record",
                     "tip": "Write lyrics alongside your music. Structure your song with verse/chorus labels. Export as plain text or synced LRC for karaoke. Use alongside the Score for complete songwriting."},
    "practice":     {"label": "Practice Mode",    "icon": "🎓", "group": "record",
                     "tip": "Slow down playback to learn difficult parts without changing pitch. Loop a section, play along at 50%, gradually speed up. The metronome follows automatically."},
    "chords":       {"label": "Chord Builder",    "icon": "🎶", "group": "record",
                     "tip": "Pick a key, see every chord that fits, build progressions by clicking. 7 common presets (Pop, Rock, Blues, Jazz). Use before writing melody — chords are the harmonic foundation."},
    "scale_ref":    {"label": "Scale Reference",  "icon": "🎵", "group": "record",
                     "tip": "Visual guide to every scale — Major, Minor, Pentatonic, Blues, modes. See which notes are safe to play. Use while composing or soloing to stay in key."},
    "input_select": {"label": "Input Device",     "icon": "🎤", "group": "record",
                     "tip": "Choose your microphone or audio interface. Set the input channel if your interface has multiple inputs. Use before recording. After: Set levels, enable count-in, hit Record."},
    "midi_input":   {"label": "MIDI Input",       "icon": "🎹", "group": "record",
                     "tip": "Connect a MIDI keyboard or controller. Play notes in real-time through any instrument. Use if you have external hardware."},
    "tuner":        {"label": "Tuner",            "icon": "🎵", "group": "record",
                     "tip": "Chromatic tuner with cents display. Tune your instrument before recording. Shows note name, frequency, and how many cents sharp or flat."},
    "metronome":    {"label": "Metronome",        "icon": "⏱", "group": "record",
                     "tip": "Click track for keeping time. Set BPM, enable during recording. Use with Count-in for a clean start. Tip: Tap tempo to set BPM by feel."},
    "count_in":     {"label": "Count-in",         "icon": "⏳", "group": "record",
                     "tip": "Plays 1-2 bars of metronome before recording starts, so you can prepare. Use with Metronome. Standard practice: 1 bar count-in at your tempo."},

    # ═══ EDIT ═══
    "piano_roll":   {"label": "Piano Roll",       "icon": "🎹", "group": "edit",
                     "tip": "Visual MIDI editor — click a grid to place notes, see pitches vertically, time horizontally. Use after Audio-to-MIDI or to compose note by note."},
    "score":        {"label": "Score",            "icon": "🎼", "group": "edit",
                     "tip": "Full sheet music composition editor — every standard notation symbol. Write for orchestra, assign instruments, hear playback. Pop out for full-page editing."},
    "split":        {"label": "Split",            "icon": "✂", "group": "edit",
                     "tip": "Cut a region at the playhead position. Use to separate sections (verse from chorus) or remove a bad take. After: Trim, Crossfade, or delete the unwanted part."},
    "trim":         {"label": "Trim",             "icon": "↔", "group": "edit",
                     "tip": "Remove the beginning or end of a clip. Drag waveform edges on the timeline, or select a range and trim. Use after Split to clean up edges. After: Crossfade if two clips meet."},
    "crossfade":    {"label": "Crossfade",        "icon": "╳", "group": "edit",
                     "tip": "Smooth transition between two adjacent clips. Prevents clicks at edit points. Use after splitting or trimming. Standard: 10-50ms crossfade at every edit point."},
    "stretch":      {"label": "Time Stretch",     "icon": "↕", "group": "edit",
                     "tip": "Change the speed of audio without changing pitch. Use to match tempos between tracks, or slow down a passage for practice. After: Check that it still sounds natural."},
    "pitch":        {"label": "Pitch Shift",      "icon": "♯", "group": "edit",
                     "tip": "Change the pitch without changing speed. Use to transpose to a different key, or shift a vocal up/down. Tip: Small shifts (1-2 semitones) sound natural; large shifts sound robotic."},
    "reverse":      {"label": "Reverse",          "icon": "⟲", "group": "edit",
                     "tip": "Flip audio backwards. Use for reverse cymbals (classic intro effect), reverse reverb on vocals, or creative sound design."},

    # ═══ CLEANUP (do these BEFORE mixing) ═══
    "noise_gate":   {"label": "Noise Gate",       "icon": "🔇", "group": "cleanup",
                     "tip": "Silences audio below a threshold — kills bleed, hum, and room noise between notes. Chain: Noise Gate FIRST → then EQ → then Compressor. Use on drums, guitar amps, vocals."},
    "noise_reduce": {"label": "Noise Reduction",  "icon": "🔇", "group": "cleanup",
                     "tip": "Spectral denoising — removes steady-state noise (hiss, fan, room tone). Learns from quiet sections. Use before mixing. Chain: Noise Reduction → Noise Gate → EQ."},
    "click_removal":{"label": "Click Removal",   "icon": "🔕", "group": "cleanup",
                     "tip": "Removes pops and clicks from recordings (mouth clicks, vinyl crackle, digital errors). Use before EQ — EQ can amplify clicks. Chain: Click Removal → Noise Gate → EQ."},
    "bleed_remove": {"label": "Bleed Removal",   "icon": "🔕", "group": "cleanup",
                     "tip": "Removes instrument bleed from a mic using the clean DI signal. Recording guitar and vocals simultaneously? The mic picks up guitar — this removes it. Use before mixing."},
    "hum_remove":   {"label": "Hum Removal",      "icon": "〰", "group": "cleanup",
                     "tip": "Removes 50/60Hz electrical hum and its harmonics. Common with ungrounded amps, single-coil pickups, cheap cables. Use before EQ. Chain: Hum Removal → Noise Gate → EQ."},
    "de_ess":       {"label": "De-esser",         "icon": "💨", "group": "cleanup",
                     "tip": "Tames harsh 'S' and 'T' sounds in vocals. Use AFTER compression (compression makes sibilance worse). Chain: EQ → Compressor → De-esser → Reverb."},
    "de_clip":      {"label": "De-clip",          "icon": "📉", "group": "cleanup",
                     "tip": "Repairs digital clipping (flat-topped waveforms from recording too hot). Use first — before any other processing. Prevention: record at -12dB to -6dB peaks."},
    "normalize":    {"label": "Normalize",        "icon": "📊", "group": "cleanup",
                     "tip": "Brings the loudest peak to a target level. Use after recording if the level is too low. NOT a substitute for proper gain staging. After: Continue to EQ and mixing."},

    # ═══ MIX (the art — do these in order) ═══
    "eq":           {"label": "EQ",               "icon": "≋", "group": "mix",
                     "tip": "Shape the frequency balance of each track. Cut mud (200-400Hz), add presence (2-5kHz), roll off rumble (HPF below 80Hz). Chain: Noise Gate → EQ → Compressor → Reverb. The most important mixing tool."},
    "compressor":   {"label": "Compressor",       "icon": "⇕", "group": "mix",
                     "tip": "Reduces dynamic range — makes quiet parts louder and loud parts quieter. Essential for vocals, drums, bass. Chain: EQ → Compressor → De-esser (vocals) → Reverb. Fast attack = controlled; slow attack = punchy."},
    "reverb":       {"label": "Reverb",           "icon": "≈", "group": "mix",
                     "tip": "Adds room ambience and space. Use on vocals, snare, guitars — NOT on bass or kick. Chain: EQ → Compressor → Reverb. Use sends (not insert) so multiple tracks share one reverb. Less is more."},
    "delay":        {"label": "Delay",            "icon": "⋯", "group": "mix",
                     "tip": "Repeating echoes synced to BPM. Use on vocals (subtle) and guitars (rhythmic). Chain: After compressor, before or alongside reverb. Sync to tempo for musical results. Ping-pong delay adds width."},
    "quantize":     {"label": "Quantize",          "icon": "⊞", "group": "edit",
                     "tip": "Snap recorded MIDI notes to the nearest grid position. Tightens up timing that was played slightly off-beat. Set the grid resolution (1/4, 1/8, 1/16) and strength (100% = perfect grid, 50% = halfway)."},
    "punch":        {"label": "Punch In/Out",     "icon": "⏺", "group": "record",
                     "tip": "Record over just a section of a track without replacing the whole thing. Set punch-in point (where recording starts) and punch-out (where it stops). The rest of the track stays untouched."},
    "true_peak":    {"label": "True Peak Meter",  "icon": "📐", "group": "master",
                     "tip": "Intersample peak detection. Regular meters miss peaks between samples that can cause distortion on playback. Streaming platforms penalize true peaks above -1dBTP. Check BEFORE final export."},
    "bus":          {"label": "Bus/Group",         "icon": "⫛", "group": "mix",
                     "tip": "Route multiple tracks to a submix bus. Group all drums to a Drum Bus, apply compression to the group. This is how pros control sections of a mix together. Create bus AFTER individual track processing."},
    "sends":        {"label": "Sends",            "icon": "→", "group": "mix",
                     "tip": "Route audio from multiple tracks to a shared effect (bus). Use for reverb and delay — one reverb bus, many tracks feeding it at different levels. Saves CPU and creates cohesion. This is how pros mix."},

    # ═══ MASTER (final stage — do these last) ═══
    "limiter":      {"label": "Limiter",          "icon": "⊤", "group": "master",
                     "tip": "Brick-wall ceiling — prevents audio from exceeding 0dB. The LAST thing in the chain. Use on the master bus. Set ceiling to -1dB (streaming headroom). Push the input until loudness hits your LUFS target."},
    "lufs":         {"label": "Loudness",         "icon": "📏", "group": "master",
                     "tip": "Measures loudness in LUFS — the standard for streaming platforms. Targets: Spotify -14 LUFS, Apple Music -16 LUFS, YouTube -14 LUFS. Use alongside the Limiter. Check BEFORE exporting."},
    "stereo_width": {"label": "Stereo Width",     "icon": "↔", "group": "master",
                     "tip": "Controls how wide the stereo image is. Use on the master bus for final width adjustment. Tip: Check in mono — if it sounds thin in mono, you've gone too wide. Keep bass and kick centered."},
    "reference":    {"label": "Reference A/B",    "icon": "⟷", "group": "master",
                     "tip": "Compare your mix against a professional reference track. Load a song you want to sound like, switch between yours and theirs. Match loudness first (our ears prefer louder). The fastest way to improve."},
    "export":       {"label": "Export",           "icon": "↗", "group": "master",
                     "tip": "Render your mix to a file. WAV (lossless, for mastering), MP3 (streaming/sharing), FLAC (lossless + smaller). Always export WAV first, then convert. The final step."},
    "learn":        {"label": "Learn",            "icon": "📖", "group": "master",
                     "tip": "Built-in encyclopedia — from 'what is a note' to LUFS targets for Spotify. Search any topic. Use anytime you don't understand a term or technique."},
}


class ContextEngine:
    """Watches the session and determines what tools to show."""

    def __init__(self):
        self.state = ContextState()
        self._idle_threshold = 10.0  # seconds before suggesting

    def update(self, engine_state, action=None):
        """Update context from the audio engine state and user action."""
        self.state.track_count = len(engine_state.get("tracks", []))
        self.state.is_playing = engine_state.get("playing", False)
        self.state.is_recording = engine_state.get("recording", False)

        if action:
            try:
                self.state.last_action = Action(action)
            except ValueError:
                self.state.last_action = Action.NONE
            self.state.last_action_time = time.time()

        # Determine phase
        self.state.phase = self._determine_phase()

        # Calculate tool weights
        self.state.tool_weights = self._calculate_weights()

        return self.get_ui_state()

    def _determine_phase(self):
        """Figure out where the user is in their workflow."""
        s = self.state

        if s.is_recording:
            return Phase.RECORD

        if s.track_count == 0:
            return Phase.EMPTY

        if s.last_action in (Action.DROP_FILE, Action.OPEN_FILE, Action.RUN_SEPARATION):
            return Phase.IMPORT

        if s.last_action in (Action.SPLIT_CLIP, Action.SELECT_REGION):
            return Phase.EDIT

        if s.track_count >= 2 and s.last_action in (Action.ADJUST_VOLUME, Action.ADJUST_PAN,
                                                       Action.MUTE_TRACK, Action.SOLO_TRACK):
            return Phase.MIX

        if s.last_action == Action.SOLO_MASTER:
            return Phase.MASTER

        # Default: if 1 track, we're in import/edit. If 2+, we're mixing.
        if s.track_count == 1:
            return Phase.IMPORT
        return Phase.MIX

    def _calculate_weights(self):
        """Calculate visibility weight for each tool based on context."""
        weights = {}
        phase = self.state.phase

        # Base weights by phase
        phase_weights = {
            Phase.EMPTY: {
                "open_file": 1.0, "input_select": 0.8,
                "synth": 0.7, "drums": 0.7, "pad": 0.7,
                "piano_roll": 0.6, "learn": 0.5,
            },
            Phase.IMPORT: {
                "stem_split": 1.0, "lyrics": 0.9, "analyze": 0.9,
                "bandmate": 0.8,
                "noise_gate": 0.7, "hum_remove": 0.6, "normalize": 0.6,
                "de_ess": 0.5, "de_clip": 0.5,
                "open_file": 0.4,
            },
            Phase.RECORD: {
                "input_select": 1.0, "metronome": 0.9, "count_in": 0.8,
                "synth": 0.6, "drums": 0.6, "pad": 0.6,
            },
            Phase.EDIT: {
                "split": 1.0, "trim": 0.9, "crossfade": 0.8,
                "stretch": 0.7, "pitch": 0.7, "reverse": 0.5,
                "noise_gate": 0.4, "normalize": 0.4,
            },
            Phase.MIX: {
                "eq": 1.0, "compressor": 0.9, "reverb": 0.8, "delay": 0.7,
                "sends": 0.7, "bandmate": 0.6, "bleed_remove": 0.6, "normalize": 0.5,
                "lufs": 0.4,
            },
            Phase.MASTER: {
                "limiter": 1.0, "lufs": 1.0, "stereo_width": 0.8,
                "reference": 0.8, "export": 0.9,
                "eq": 0.5, "compressor": 0.5,
            },
            Phase.EXPORT: {
                "export": 1.0, "lufs": 0.8, "reference": 0.7,
            },
        }

        base = phase_weights.get(phase, {})

        # Start with base weights
        for tool_id in TOOLS:
            weights[tool_id] = base.get(tool_id, 0.1)  # everything at least 0.1 (accessible)

        # Boost based on detected issues
        for issue in self.state.audio_issues:
            if issue.type == "clipping" and issue.fix_available:
                weights["de_clip"] = max(weights.get("de_clip", 0), 0.9)
                weights["normalize"] = max(weights.get("normalize", 0), 0.7)
            elif issue.type == "hum":
                weights["hum_remove"] = max(weights.get("hum_remove", 0), 0.9)
            elif issue.type == "noise":
                weights["noise_gate"] = max(weights.get("noise_gate", 0), 0.9)
            elif issue.type == "low_volume":
                weights["normalize"] = max(weights.get("normalize", 0), 0.9)

        # Idle suggestions — after 10 seconds of no action
        idle_time = time.time() - self.state.last_action_time
        if idle_time > self._idle_threshold and self.state.track_count > 0:
            # Suggest next logical step
            if phase == Phase.IMPORT:
                weights["stem_split"] = 1.0
                weights["lyrics"] = 0.9
            elif phase == Phase.MIX:
                weights["lufs"] = 0.9
                weights["export"] = 0.8

        return weights

    def get_ui_state(self):
        """Return the context state for the frontend."""
        # Sort tools by weight, group into prominent vs available
        sorted_tools = sorted(
            [(tid, TOOLS[tid], w) for tid, w in self.state.tool_weights.items()],
            key=lambda x: -x[2]
        )

        prominent = []  # weight >= 0.5 — shown prominently
        available = []  # weight < 0.5 — in the drawer

        for tool_id, tool_info, weight in sorted_tools:
            entry = {
                "id": tool_id,
                "label": tool_info["label"],
                "icon": tool_info["icon"],
                "group": tool_info["group"],
                "weight": round(weight, 2),
                "tip": tool_info.get("tip", ""),
            }
            if weight >= 0.5:
                prominent.append(entry)
            else:
                available.append(entry)

        # Contextual message — what the program "sees"
        message = self._get_context_message()

        return {
            "phase": self.state.phase.value,
            "prominent_tools": prominent,
            "available_tools": available,
            "message": message,
            "issues": [{"type": i.type, "description": i.description,
                        "severity": i.severity} for i in self.state.audio_issues],
        }

    def _get_context_message(self):
        """A human-readable hint about what the program suggests."""
        phase = self.state.phase
        tc = self.state.track_count

        if phase == Phase.EMPTY:
            return "Drop a song or hit Record to start."
        elif phase == Phase.IMPORT and tc == 1:
            return "Track loaded. Try Stem Split to pull it apart, or Lyrics to transcribe."
        elif phase == Phase.RECORD:
            return "Recording. Focus on the performance — everything else can wait."
        elif phase == Phase.EDIT:
            return "Editing. Split, trim, or stretch to shape the arrangement."
        elif phase == Phase.MIX and tc >= 2:
            return f"{tc} tracks. Balance the levels, add space with EQ and reverb."
        elif phase == Phase.MASTER:
            return "Mastering. Check loudness, apply limiting, A/B against a reference."

        # Idle suggestions
        if self.state.audio_issues:
            issue = self.state.audio_issues[0]
            return f"I noticed: {issue.description}"

        return ""

    def report_issue(self, issue_type, severity, location, description):
        """Audio analysis found an issue — add it to context."""
        self.state.audio_issues.append(
            AudioIssue(type=issue_type, severity=severity,
                      location=location, description=description)
        )

    def clear_issues(self):
        self.state.audio_issues.clear()
