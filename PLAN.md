# Sozawen — Born from the burn. Built by feeling.
## Complete DAW Build Plan

**What:** Full DAW + AI music production suite for indie musicians.
**Price:** $49 one-time. No subscription. No account. No cloud.
**Tagline:** "Born from the burn. Built by feeling."
**Secondary:** "A bandmate who listens."

---

## Tech Stack
- Python 3.12 + PyInstaller (frozen exe)
- pywebview (native desktop window)
- sounddevice + PortAudio/ASIO (real-time audio I/O)
- PyTorch + CUDA (GPU acceleration)
- Demucs (stem separation)
- Whisper (lyric transcription)
- librosa (audio analysis)
- pedalboard (effects: EQ, comp, reverb, delay, gate, limiter)
- pyloudnorm (LUFS metering)
- soundfile (fast WAV I/O)
- rubberband-py (time stretch / pitch shift)
- pretty_midi (MIDI generation)
- HTML/CSS/JS frontend (Canvas for waveforms)

---

## Phase 1 — Full DAW (63 features + 20 foundations)

### FOUNDATIONS (build first, everything depends on these)

#### Audio Engine
- Callback-based real-time pipeline: tracks → mix → effects → master → output
- sounddevice output callback at buffer level (256-2048 samples)
- Per-track: read from source file at playhead position, apply gain/pan/mute/solo
- Mix bus: sum all unmuted tracks with gain/pan applied
- Master bus: effects chain → limiter → output
- 64-bit float internal processing
- Sample-accurate playback position tracking
- Transport state machine: stopped / playing / recording / paused

#### Recording Engine
- sounddevice input stream → WAV writer per armed track
- Input device enumeration (WASAPI/ASIO via PortAudio)
- Input monitoring: low-latency passthrough to output
- Latency compensation: measure roundtrip, offset playback
- Record to new region on armed track
- Loop record: create take per loop iteration

#### Undo/Redo System
- Command pattern: every operation is an undoable command
- Unlimited history (memory-bounded, configurable)
- Commands: add/remove track, add/remove region, move region, split, trim,
  gain change, pan change, mute/solo toggle, effect add/remove, etc.
- Group commands (one undo for multi-operation edits)
- Human-readable undo descriptions ("Undo: Split Track 1 at 0:42")

#### Waveform Rendering
- Pre-compute peak arrays at multiple zoom levels (overview → sample level)
- Canvas rendering with efficient redraw (only visible portion)
- Color: recorded = teal, imported = violet, generated = amber
- "Recorded" / "Imported" / "Generated" badge on each clip
- Responsive to zoom and scroll

#### Playhead + Cursor
- Visual playhead line moving across timeline during playback
- Click-to-seek anywhere on timeline
- Playhead position drives audio engine read position
- Time display updates in transport bar

#### Zoom / Scroll
- Horizontal zoom: mouse wheel = time zoom
- Vertical zoom: track height adjustment
- Scroll: horizontal scrollbar + shift-wheel
- Zoom to selection
- Zoom to fit all

#### Selection / Range
- Click-drag on timeline for time range selection
- Click on track header for track selection
- Shift-click for multi-track selection
- Selected range highlighted visually
- Operations apply to selection (cut, copy, delete, process)

#### Track System
- Track types: Audio, Bus, Master, Folder
- Track header: name, color, mute, solo, record arm, volume, pan
- Drag to reorder
- Folder tracks: collapse/expand children
- Master track: always at bottom, receives all output

#### Monitoring / Meters
- Per-track level meter (peak + RMS, stereo)
- Master meter
- Real-time update during playback and recording
- Clip indicator (red when clipping)

#### Markers / Regions
- Click timeline ruler to place marker
- Named markers with color
- Named regions (start-end spans)
- Navigate: jump to next/previous marker
- Loop between markers
- Tab to transient (next attack in waveform)

#### Crash Recovery
- Auto-save every 60 seconds to numbered backup
- On launch: detect if last session crashed, offer recovery
- Recovery loads last auto-save

### RECORDING (9)
- Multi-track simultaneous record
- Punch-in/out (auto)
- Loop record with takes
- Input monitoring
- Latency compensation
- Click/metronome with subdivisions
- Count-in bars
- ASIO support
- Input device selection UI

### EDITING (12)
- Non-destructive (regions reference source)
- Crossfade editor
- Grid modes (bar/beat/sample)
- Time stretch
- Pitch shift
- Take lanes / comping
- Trim / split / join
- Ripple edit
- Zero-crossing snap
- Clip gain
- Reverse
- Transient split

### MIXING (6)
- Volume / pan per track
- Mute / solo (exclusive + additive)
- Sends / returns
- Bus routing
- Folder tracks
- Track colors / labels

### EFFECTS (9)
- EQ (parametric)
- Compressor
- Reverb
- Delay
- Gate
- Limiter
- Chorus / flanger
- Plugin delay compensation
- Wet/dry per plugin

### AUTOMATION (2)
- Volume / pan envelopes
- Drawable automation lanes

### MASTERING (7)
- LUFS metering
- True peak limiting
- Dithering
- M/S widening
- Reference A/B
- Master FX chain
- Spectrum analyzer

### FILES (6)
- Project save/load (JSON + media refs)
- Auto-save with versions
- Multi-format export (WAV/MP3/FLAC/OGG)
- Stem export
- Templates
- Collect to folder

### SOZAWEN ONLY (5)
- Stem separation (Demucs)
- Lyric transcription (Whisper)
- Key / BPM / loudness analysis
- Self-healing engine
- No subscription ever

### ACCESSIBILITY (8)
- "Recorded" / "Imported" / "Generated" badges on every clip
- Tooltip on every control
- "What does this do?" mode with audio demos
- Color coding by source type
- Beginner mode (hide advanced)
- Built-in glossary with audio examples
- Undo explains itself in plain English
- Progress breadcrumbs (Record → Edit → Mix → Master → Export)

---

## Phase 2 — MIDI + Advanced (12)
- Piano roll editor
- Drum grid editor
- Step sequencer
- Quantize / humanize
- Velocity / CC lanes
- MIDI + audio simultaneous record
- Sidechain routing
- VCA faders
- Plugin parameter automation
- Touch / latch modes
- Tempo automation
- Batch export by markers

## Phase 3 — AI + Extensions (5)
- Session collaborator (AI bandmate)
- Hum-to-instrument
- AI drum / bass / pad generation
- VST3 plugin hosting
- MIDI learn

---

## Build Order
1. Audio engine (real-time playback pipeline)
2. Undo system (command pattern)
3. Waveform rendering (peak computation + canvas)
4. Playhead + transport
5. Track system (types, reorder, header controls)
6. Recording engine (input capture + monitoring)
7. Zoom / scroll / selection
8. Editing operations (split, trim, crossfade, stretch)
9. Effects chain (pedalboard integration)
10. Mixing (sends, buses, solo/mute logic, pan law)
11. Meters + monitoring
12. Markers + regions
13. Mastering chain
14. Stem separation + lyrics + analysis (already working)
15. File management (save/load/export)
16. Accessibility layer (tooltips, badges, beginner mode)
17. Self-healing + crash recovery
18. Installer + packaging

---

## Palette
- Deep background: #0a0a14
- Violet (the burn): #9b59b6
- Blue-green/teal (the flow): #2dd4a8
- Recorded audio: teal border
- Imported audio: violet border
- Generated audio: amber border
