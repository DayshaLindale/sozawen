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
    "open_file":    {"label": "Open File",        "icon": "📂", "group": "import"},
    "stem_split":   {"label": "Stem Separation",  "icon": "✂", "group": "import"},
    "lyrics":       {"label": "Lyrics",           "icon": "♪", "group": "import"},
    "analyze":      {"label": "Analyze",          "icon": "≈", "group": "import"},
    "bandmate":     {"label": "Bandmate",         "icon": "💬", "group": "import"},

    # Recording
    "input_select": {"label": "Input Device",     "icon": "🎤", "group": "record"},
    "metronome":    {"label": "Metronome",        "icon": "⏱", "group": "record"},
    "count_in":     {"label": "Count-in",         "icon": "⏳", "group": "record"},

    # Editing
    "split":        {"label": "Split",            "icon": "✂", "group": "edit"},
    "trim":         {"label": "Trim",             "icon": "↔", "group": "edit"},
    "crossfade":    {"label": "Crossfade",        "icon": "╳", "group": "edit"},
    "stretch":      {"label": "Time Stretch",     "icon": "↕", "group": "edit"},
    "pitch":        {"label": "Pitch Shift",      "icon": "♯", "group": "edit"},
    "reverse":      {"label": "Reverse",          "icon": "⟲", "group": "edit"},

    # Cleanup
    "noise_gate":   {"label": "Noise Gate",       "icon": "🔇", "group": "cleanup"},
    "hum_remove":   {"label": "Hum Removal",      "icon": "〰", "group": "cleanup"},
    "de_ess":       {"label": "De-esser",         "icon": "💨", "group": "cleanup"},
    "de_clip":      {"label": "De-clip",          "icon": "📉", "group": "cleanup"},
    "normalize":    {"label": "Normalize",        "icon": "📊", "group": "cleanup"},

    # Mix
    "eq":           {"label": "EQ",               "icon": "≋", "group": "mix"},
    "compressor":   {"label": "Compressor",       "icon": "⇕", "group": "mix"},
    "reverb":       {"label": "Reverb",           "icon": "≈", "group": "mix"},
    "delay":        {"label": "Delay",            "icon": "⋯", "group": "mix"},
    "sends":        {"label": "Sends",            "icon": "→", "group": "mix"},

    # Master
    "limiter":      {"label": "Limiter",          "icon": "⊤", "group": "master"},
    "lufs":         {"label": "Loudness",         "icon": "📏", "group": "master"},
    "stereo_width": {"label": "Stereo Width",     "icon": "↔", "group": "master"},
    "reference":    {"label": "Reference A/B",    "icon": "⟷", "group": "master"},
    "export":       {"label": "Export",           "icon": "↗", "group": "master"},
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
            },
            Phase.EDIT: {
                "split": 1.0, "trim": 0.9, "crossfade": 0.8,
                "stretch": 0.7, "pitch": 0.7, "reverse": 0.5,
                "noise_gate": 0.4, "normalize": 0.4,
            },
            Phase.MIX: {
                "eq": 1.0, "compressor": 0.9, "reverb": 0.8, "delay": 0.7,
                "sends": 0.7, "bandmate": 0.6, "normalize": 0.5,
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
