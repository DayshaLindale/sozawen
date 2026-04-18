# Gaming Accessibility Program — No Two Are The Same

## The Problem
Deaf and hard-of-hearing gamers miss audio cues. Existing solutions are binary (on/off)
or offer 2-3 presets that fit nobody perfectly. Partial hearing loss is a spectrum.
Gaming needs are a spectrum. No two people need the same thing.

## The Core Principle
**Not profiles. Not presets. A continuous spectrum where every element is independent.**
The user builds their own experience from individual components, each on its own dial.

## Name: TBD (needs the same naming process as Sozawen)

---

## Four Layers — All Independent, All Adjustable

### Layer 1: Sound Classification (< 10ms latency)
A tiny CNN that classifies game audio in real-time. Not transcription — classification.
"That sound was a footstep." "That was an ability." "That was an explosion."

Output: directional icon overlay on screen
- Arrow shows direction sound came from
- Icon shows what type of sound
- Size/opacity reflects volume/distance
- Color reflects urgency (environmental vs threat vs teammate)
- ALL of these: user-adjustable per category

Latency target: < 10ms. No speech-to-text involved. Pure signal classification.
Runs on GPU alongside the game (tiny model, <100MB VRAM).
CPU fallback with slightly higher latency (~20ms).

### Layer 2: Voice Chat Transcription (< 300ms)
Streaming Whisper on the voice chat audio channel.
Speaker-separated — each teammate gets their own caption line.

Output: subtitle-style overlay
- Position: user chooses (top, bottom, sides, floating near minimap)
- Size: continuous slider
- Opacity: continuous slider  
- Duration: how long text stays visible
- Color per speaker: auto-assigned or manual
- Partial results: show words as they form (less accurate but faster)
  vs wait for complete sentence (more accurate but delayed)
- User chooses their own latency/accuracy tradeoff on a slider

### Layer 3: Environmental Audio Translation
Music shifts, ambient changes, audio cues that aren't sounds but moods.
"The music got tense" = danger nearby. "Ambient went quiet" = something is about to happen.

Output: screen border effects
- Edge glow color shifts with mood (calm = blue, tension = amber, danger = red)
- Intensity on a slider — subtle tint to obvious pulse
- User chooses which environmental categories get visual treatment
- Can be turned off entirely without affecting other layers

### Layer 4: Tactical Overlay
Combines all layers into a unified HUD element.
Threat direction + sound type + voice callouts in one glanceable area.

Output: customizable HUD widget
- User places it wherever they want on screen
- Resize freely
- Transparency slider
- Information density slider (minimal → detailed)
- Which layers feed into it (any combination)

---

## The Customization Philosophy

**Everything is a slider, not a checkbox.**

Instead of:
  [x] Enable subtitles
  [ ] Show directional indicators

We offer:
  Subtitle visibility: [====|====] (0-100%)
  Subtitle size: [==|========] (small to large)
  Subtitle delay: [|==========] (instant/partial to accurate/delayed)
  Directional indicator size: [=====|====] (0-100%)
  Directional indicator opacity: [========|=] 
  Footstep sensitivity: [======|===]
  Ability cue sensitivity: [===|======]
  Voice chat position: [drag anywhere]
  Environmental mood intensity: [==|========]

**Every slider is independent.** Someone who has partial hearing in one ear
tunes differently than someone fully Deaf. Someone who plays Overwatch
tunes differently than someone who plays BG3. The program doesn't assume.

**Preset sharing, not preset enforcement.** Users CAN save their config
and share it with others. "Here's my Overwatch setup." But it's a starting
point they modify, not a box they fit into.

---

## Technical Architecture

### Audio Capture
- WASAPI loopback (same as Notare) for game audio
- Separate channel for voice chat (Discord, game voice, etc.)
- Split at capture time — game sounds vs voice go to different pipelines

### Sound Classifier
- Tiny CNN (~5MB) trained on game audio samples
- Categories: footstep, gunshot, ability, explosion, UI sound, voice, music, ambient
- Per-game profiles that improve classification accuracy
- < 10ms inference on GPU, < 20ms on CPU
- Directional detection via stereo/surround channel analysis

### Voice Transcriber
- Faster-whisper streaming mode
- Speaker diarization on voice chat
- Partial result display for low-latency needs
- Runs on CPU (game owns the GPU) or on E-cores if available

### Overlay Renderer
- Transparent overlay window (Win32 layered window or DirectComposition)
- Renders ABOVE the game without hooking into it (no anti-cheat conflicts)
- GPU-composited but separate from the game's rendering pipeline
- Works with any game — no per-game integration needed

### Anti-Cheat Compatibility
- CRITICAL: must not trigger anti-cheat (EAC, BattlEye, Vanguard)
- No process injection, no memory reading, no DLL hooking
- Audio capture via OS-level WASAPI (same as OBS — if OBS works, we work)
- Overlay via standard Windows compositor (same as Discord overlay)
- Document compatibility testing with every major anti-cheat

---

## Pricing
- Free tier: Layer 1 (sound classification) + Layer 3 (environmental)
- Full: $15 one-time — all 4 layers, unlimited customization
- Why not free entirely: sustainable development, continued game support
- Why one-time not subscription: accessibility shouldn't have a monthly gate

---

## Build Priority
1. Audio capture + sound classifier + directional overlay (MVP)
2. Voice chat transcription + subtitle overlay
3. Environmental mood detection
4. Tactical HUD + preset sharing
5. Per-game classifier training + community profiles

---

## What Makes This Different
Every other accessibility tool says "here's what we built for you."
This one says "here's what you need to build YOUR experience."
No two setups are the same because no two people are the same.
