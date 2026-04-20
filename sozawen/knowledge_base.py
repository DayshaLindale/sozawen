"""Sozawen Knowledge Base — everything a musician needs to know.

From music theory fundamentals to mastering for streaming platforms.
Written by musicians, not textbooks. Plain language, real examples.
"""

KNOWLEDGE_BASE = {
    # ═══════════════════════════════════════════════════════════════
    # MUSIC THEORY
    # ═══════════════════════════════════════════════════════════════

    "notes": {
        "title": "Notes & Pitch",
        "category": "Music Theory",
        "content": """Music uses 12 notes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B. Then it repeats an octave higher. The distance between any two adjacent notes is a **semitone** (or half step). Two semitones = one **whole step**.

**Middle C** is C4 (MIDI note 60, 261.6 Hz). Concert pitch A is A4 (MIDI 69, 440 Hz). Every octave up doubles the frequency.

**Sharps (#)** raise a note by one semitone. **Flats (b)** lower by one. C# and Db are the same pitch — different names depending on context (called enharmonic equivalents).

On a piano: white keys are the natural notes (C D E F G A B), black keys are the sharps/flats. On a guitar: each fret is one semitone."""
    },

    "intervals": {
        "title": "Intervals",
        "category": "Music Theory",
        "content": """An interval is the distance between two notes, measured in semitones:

| Semitones | Name | Sound | Example |
|-----------|------|-------|---------|
| 0 | Unison | Same note | C to C |
| 1 | Minor 2nd | Tense, dissonant | Jaws theme |
| 2 | Major 2nd | Stepping up | Happy Birthday (first two notes) |
| 3 | Minor 3rd | Sad, dark | Greensleeves |
| 4 | Major 3rd | Happy, bright | Oh When the Saints |
| 5 | Perfect 4th | Open, suspended | Here Comes the Bride |
| 6 | Tritone | Unstable, evil | The Simpsons theme |
| 7 | Perfect 5th | Strong, powerful | Star Wars theme |
| 8 | Minor 6th | Bittersweet | Love Story theme |
| 9 | Major 6th | Warm, sweet | My Bonnie |
| 10 | Minor 7th | Bluesy | Star Trek theme |
| 11 | Major 7th | Dreamy, jazzy | |
| 12 | Octave | Same note, higher | Somewhere Over the Rainbow |

Intervals are the building blocks of melody (horizontal) and chords (vertical)."""
    },

    "scales": {
        "title": "Scales",
        "category": "Music Theory",
        "content": """A scale is a set of notes that sound good together. The two most important:

**Major scale** — happy, bright, resolved. Intervals: W W H W W W H (W=whole step, H=half step). Example: C D E F G A B.

**Natural minor scale** — sad, dark, emotional. Intervals: W H W W H W W. Example: A B C D E F G.

**Pentatonic scales** — remove the "tension" notes from major/minor. Only 5 notes. Can't play a wrong note. Used in blues, rock, pop, folk, and most guitar solos.
- Major pentatonic: 1 2 3 5 6 (C D E G A)
- Minor pentatonic: 1 b3 4 5 b7 (A C D E G)

**Blues scale** — minor pentatonic plus the "blue note" (b5): 1 b3 4 b5 5 b7.

**Modes** — starting a major scale from a different note changes the mood:
- Dorian (from 2nd) — minor but brighter. Jazz, Santana.
- Phrygian (from 3rd) — dark, Spanish. Flamenco, metal.
- Lydian (from 4th) — dreamy, floating. Film scores.
- Mixolydian (from 5th) — major but bluesy. Rock, funk.

**The key of a song** = which scale its melody and chords are built from."""
    },

    "chords": {
        "title": "Chords & Harmony",
        "category": "Music Theory",
        "content": """A chord is three or more notes played together. Built by stacking intervals:

**Major chord** — root + major 3rd + perfect 5th (happy). C = C E G.
**Minor chord** — root + minor 3rd + perfect 5th (sad). Am = A C E.
**Diminished** — root + minor 3rd + diminished 5th (tense). Bdim = B D F.
**Augmented** — root + major 3rd + augmented 5th (unstable). Caug = C E G#.

**7th chords** add a 4th note:
- Major 7th (Cmaj7) — dreamy, jazz. C E G B.
- Minor 7th (Am7) — smooth, soulful. A C E G.
- Dominant 7th (G7) — bluesy, wants to resolve. G B D F.

**Diatonic chords** — chords built from a scale using only its notes:
- In C major: C Dm Em F G Am Bdim (I ii iii IV V vi vii°)
- In A minor: Am Bdim C Dm Em F G (i ii° III iv v VI VII)

**Roman numerals** describe chord function regardless of key:
- I = home (tonic)
- IV = departure (subdominant)
- V = tension that wants to go home (dominant)
- vi = emotional, reflective"""
    },

    "circle_of_fifths": {
        "title": "Circle of Fifths",
        "category": "Music Theory",
        "content": """The Circle of Fifths shows the relationship between all 12 keys:

Going clockwise adds one sharp: C → G → D → A → E → B → F#
Going counter-clockwise adds one flat: C → F → Bb → Eb → Ab → Db

**Why it matters:**
- Keys next to each other share 6 out of 7 notes — they blend well
- The key directly opposite is the most distant — maximum contrast
- V chord (dominant) is one step clockwise
- IV chord (subdominant) is one step counter-clockwise

**Each major key has a relative minor** (shares the same notes):
C/Am, G/Em, D/Bm, A/F#m, E/C#m, B/G#m, F#/D#m, F/Dm, Bb/Gm, Eb/Cm, Ab/Fm, Db/Bbm

**Common modulations:** Move one step on the circle for a smooth key change. Move to the relative minor/major for an emotional shift."""
    },

    "song_structure": {
        "title": "Song Structure",
        "category": "Music Theory",
        "content": """Most songs follow predictable structures. Knowing them helps you arrange:

**Verse-Chorus** (most pop/rock):
Intro → Verse → Chorus → Verse → Chorus → Bridge → Chorus → Outro

**AABA** (jazz standards, older pop):
A section → A section → B section (bridge) → A section

**Verse-Verse** (folk, storytelling):
Verse → Verse → Verse (each with different lyrics, same melody)

**Common section lengths:**
- Intro: 4-8 bars
- Verse: 8-16 bars
- Pre-chorus: 4-8 bars
- Chorus: 8-16 bars
- Bridge: 8 bars
- Outro: 4-8 bars

**Dynamics matter more than structure.** A song that's the same volume the whole way through is boring. Build up. Pull back. The chorus should feel bigger than the verse — not necessarily louder, but wider, fuller, more energy."""
    },

    "rhythm": {
        "title": "Rhythm & Time",
        "category": "Music Theory",
        "content": """**Time signature** tells you how beats are grouped:
- **4/4** — four beats per bar, quarter note gets one beat. Most music.
- **3/4** — three beats per bar. Waltz, some ballads.
- **6/8** — six eighth notes per bar, grouped in two. Compound feel. "Nothing Else Matters."
- **5/4** — five beats. "Take Five." Progressive rock.
- **7/8** — seven eighth notes. Tool, King Crimson.

**BPM (beats per minute)** = tempo:
- 60-80: Slow ballad, downtempo
- 80-100: Hip-hop, R&B
- 100-120: Pop, indie rock
- 120-140: Dance, EDM, punk
- 140-170: Drum and bass, fast metal
- 170-200: Thrash, speed metal

**Swing** — instead of straight eighth notes, the first is held longer. Makes it "groove." Jazz, blues, shuffle.

**Syncopation** — accenting the off-beats. Makes rhythm feel alive and human."""
    },

    # ═══════════════════════════════════════════════════════════════
    # RECORDING
    # ═══════════════════════════════════════════════════════════════

    "signal_chain": {
        "title": "The Signal Chain",
        "category": "Recording",
        "content": """The path your sound takes from source to recording:

**Instrument/Voice → Microphone → Cable → Preamp/Interface → DAW**

Each link matters:
1. **Source** — the performance. No amount of gear fixes a bad take.
2. **Microphone** — converts sound waves to electrical signal. Type matters:
   - **Dynamic** (SM57/SM58) — rugged, handles loud sources. Guitar amps, snare, vocals live.
   - **Condenser** (AT2020, Rode NT1) — detailed, sensitive. Vocals, acoustic guitar, overheads.
   - **Ribbon** — smooth, warm. Vintage sound. Fragile. Never use phantom power with ribbon mics.
3. **Preamp** — amplifies the tiny mic signal. Built into your audio interface.
4. **Interface** — converts analog to digital (A/D). Sample rate and bit depth set here.
5. **DAW** — records, edits, mixes. That's where you are now.

**Gain staging** — set each stage's level so nothing clips but the signal is strong:
- Interface preamp: peaks hitting about -12 to -6 dBFS
- Track fader: start at 0dB (unity)
- Master: peaks below -1 dBTP"""
    },

    "mic_placement": {
        "title": "Microphone Placement",
        "category": "Recording",
        "content": """Where you put the mic matters more than which mic you use:

**Vocals:** 6-10 inches from the mouth. Pop filter between singer and mic. Slightly off-axis (not pointed directly at mouth) reduces plosives. Height at mouth level or slightly above.

**Acoustic guitar:** Aim at the 12th fret from 6-12 inches away. NOT at the sound hole (too boomy). For more body, angle slightly toward the bridge.

**Electric guitar amp:** SM57 pointed at the speaker cone. On-axis (center) = brighter. Off-axis (edge) = warmer. 1-3 inches from the grille cloth.

**Multi-mic recording:** When using two mics on the same source, check phase (the phase invert button). If it sounds thin or hollow when both are on, flip the phase on one.

**Room sound:** Further from the source = more room. Closer = more direct. In an untreated room, get close to minimize room reflections.

**The 3:1 rule:** If using multiple mics, the distance between mics should be at least 3x the distance from each mic to its source. Prevents phase cancellation."""
    },

    "gain_staging": {
        "title": "Gain Staging",
        "category": "Recording",
        "content": """Gain staging means setting the right level at every point in the signal chain:

**During recording:**
- Set the interface preamp so peaks hit around **-12 to -6 dBFS**
- Leave headroom — you can always make it louder later, you can't un-clip
- 24-bit recording has so much dynamic range that recording "too quiet" is not a real problem

**During mixing:**
- Start every fader at 0dB (unity gain)
- Balance by bringing things DOWN, not up
- If everything is loud, nothing is loud
- Aim for the mix bus (master) peaking around **-6 to -3 dBFS** before mastering

**The golden rule:** If you need to turn something up, first try turning everything else down. Headroom is free. Distortion is permanent."""
    },

    # ═══════════════════════════════════════════════════════════════
    # MIXING
    # ═══════════════════════════════════════════════════════════════

    "eq_guide": {
        "title": "EQ Strategy",
        "category": "Mixing",
        "content": """EQ shapes the tone of each track so everything has its own space:

**The frequency spectrum — where instruments live:**
- **20-80 Hz** — Sub bass. Kick drum thump, bass guitar low end. Too much = muddy.
- **80-250 Hz** — Bass/warmth. Fullness of vocals, body of guitar. Too much = boomy.
- **250-500 Hz** — Low mids. Boxiness lives here. Often CUT in this range.
- **500Hz-2kHz** — Midrange. Body of most instruments. Nasal around 1kHz.
- **2-4 kHz** — Presence. Vocal clarity, guitar bite. Harsh if boosted too much.
- **4-8 kHz** — Clarity/sibilance. "S" and "T" sounds. De-esser territory.
- **8-20 kHz** — Air. Sparkle, shimmer, cymbal sizzle. Hiss also lives here.

**Rules of thumb:**
1. **Cut before you boost.** If something is muddy, cut the mud — don't boost the brightness to compensate.
2. **Boost wide, cut narrow.** Wide boosts sound natural. Narrow cuts are surgical.
3. **Use the HPF (high-pass filter)** on everything except kick and bass. Cuts low-end rumble that you can't hear but eats headroom.
4. **Solo is a lie.** A track that sounds great solo may not fit the mix. Always check in context.
5. **If two tracks fight for the same frequency, one should give way.** Cut 250Hz on the guitar so the vocal has room there."""
    },

    "compression_guide": {
        "title": "Compression Guide",
        "category": "Mixing",
        "content": """Compression reduces the dynamic range — makes quiet parts louder and loud parts quieter:

**When to use compression:**
- Vocals that vary too much in volume (whisper to shout)
- Drums that need more consistent punch
- Bass that disappears and reappears
- Mix bus to "glue" everything together

**Settings by source:**

| Source | Threshold | Ratio | Attack | Release |
|--------|-----------|-------|--------|---------|
| Vocals | -20 to -15dB | 2:1 to 4:1 | 5-15ms | 50-100ms |
| Drums (punch) | -15 to -10dB | 4:1 to 8:1 | 10-30ms (slow = more punch) | 50-100ms |
| Bass | -20 to -15dB | 3:1 to 6:1 | 5-10ms | 50-80ms |
| Mix bus | -3 to -6dB | 1.5:1 to 2:1 | 10-30ms | auto or 100-300ms |

**The attack trick:** Slow attack lets the initial transient through — more punch, more snap. Fast attack catches the transient — smoother, more controlled. For drums, try slow attack. For vocals, try medium.

**Parallel compression:** Mix the compressed signal with the uncompressed original. Gets the consistency of compression without killing the dynamics. Also called "New York compression." """
    },

    "reverb_guide": {
        "title": "Reverb & Space",
        "category": "Mixing",
        "content": """Reverb creates the sense of a physical space:

**Types:**
- **Room** — small, tight, natural. Good for drums, guitars.
- **Hall** — large, lush. Orchestral, cinematic, ballads.
- **Plate** — smooth, even. Classic vocal reverb.
- **Chamber** — warm, mid-sized. All-purpose.
- **Spring** — bouncy, vintage. Surf rock, lo-fi.

**Key parameters:**
- **Pre-delay** — gap before reverb starts. Creates depth without muddying the source. 20-60ms for vocals.
- **Decay** — how long the reverb lasts. Short (0.5-1s) for tight spaces. Long (2-4s) for halls.
- **Damping** — how quickly high frequencies die in the reverb tail. High damping = warmer, like a carpeted room.
- **Wet/dry** — how much reverb vs. original. Less is usually more. 10-25% for vocals.

**The send trick:** Instead of putting reverb directly on each track, create a bus track with reverb, then SEND audio to it. Multiple tracks share the same reverb space — sounds like they're in the same room.

**Dry in the center, wet on the sides.** Keep the dry vocal centered and pan the reverb returns wider. Creates width without losing clarity."""
    },

    "panning_guide": {
        "title": "Panning & Stereo Image",
        "category": "Mixing",
        "content": """Panning places instruments left, right, or center in the stereo field:

**The standard layout:**
- **Center:** Kick, snare, bass, lead vocal. The anchor.
- **Slight left/right (20-40%):** Rhythm guitars, keys, backing vocals.
- **Wide left/right (60-100%):** Stereo guitars, percussion, pads, double-tracked parts.
- **Overheads/room mics:** Hard left/right for width.

**Rules:**
1. **Low frequencies stay center.** Bass and kick below 200Hz should be mono. Low frequencies panned hard cause phase issues on mono systems.
2. **If it's on the left, balance it on the right.** Something similar in energy on the opposite side. Otherwise the mix feels lopsided.
3. **Automate panning for movement.** A background element that slowly pans creates interest.
4. **Check in mono.** Hit the mono button. If something disappears, there's a phase issue. Fix it before it goes to a phone speaker."""
    },

    # ═══════════════════════════════════════════════════════════════
    # MASTERING
    # ═══════════════════════════════════════════════════════════════

    "mastering_basics": {
        "title": "What Is Mastering?",
        "category": "Mastering",
        "content": """Mastering is the final step before release. It ensures your mix sounds good on every system — phone speakers, car stereo, club PA, earbuds, studio monitors.

**What mastering does:**
1. **Overall EQ** — subtle tonal adjustments across the whole mix
2. **Compression/limiting** — controls dynamics and maximizes loudness
3. **Stereo enhancement** — widens or focuses the stereo image
4. **Loudness matching** — meets platform standards (LUFS)
5. **Format conversion** — correct sample rate, bit depth, dithering

**What mastering does NOT do:**
- Fix a bad mix. If the vocals are buried, go back and fix the mix.
- Make everything louder. Louder ≠ better. Dynamics are what make music breathe.

**The order:**
1. EQ first (subtle — ±1-2dB max)
2. Compression (gentle — 1-2dB gain reduction)
3. Stereo width (if needed)
4. Limiter last (sets the ceiling)
5. Dithering (if converting bit depth)"""
    },

    "loudness_standards": {
        "title": "Loudness Standards (LUFS)",
        "category": "Mastering",
        "content": """Streaming platforms normalize your track's loudness. If your master is too loud or too quiet, they adjust it. Target the right LUFS to sound your best:

| Platform | Target LUFS | True Peak Ceiling |
|----------|-------------|-------------------|
| **Spotify** | -14 LUFS | -1 dBTP |
| **Apple Music** | -16 LUFS | -1 dBTP |
| **YouTube** | -14 LUFS | -1 dBTP |
| **Tidal** | -14 LUFS | -1 dBTP |
| **Amazon Music** | -14 LUFS | -2 dBTP |
| **CD** | -9 to -12 LUFS | -0.3 dBTP |
| **Podcast** | -16 to -18 LUFS | -1 dBTP |
| **Broadcast (EBU)** | -23 LUFS | -1 dBTP |

**Why -14 matters:** If your master is -8 LUFS (very loud), Spotify turns it DOWN 6dB — and your song sounds quieter relative to its compressed dynamics. A -14 LUFS master with good dynamics actually sounds LOUDER and better on Spotify than a brick-walled -8 LUFS master.

**The lesson:** Master for dynamics, not loudness. The platforms handle the rest."""
    },

    "export_formats": {
        "title": "Export Formats Guide",
        "category": "Mastering",
        "content": """Which format to use depends on where your music is going:

**WAV (Waveform Audio)**
- Uncompressed, full quality. Standard for mastering and delivery to platforms.
- 16-bit/44.1kHz = CD quality. 24-bit/48kHz = studio standard.
- Large files (~10MB per minute at 16/44.1).

**FLAC (Free Lossless Audio)**
- Compressed but no quality loss. 50-70% the size of WAV.
- Great for archiving and platforms that accept it (Tidal, Bandcamp).

**MP3**
- Lossy compression. Small files. 320kbps is the highest quality.
- Fine for demos, previews, sharing. Not for final delivery.

**OGG Vorbis**
- Open-source lossy. Slightly better than MP3 at the same bitrate.
- Used by Spotify internally.

**AIFF**
- Apple's uncompressed format. Same quality as WAV, different container.
- Use if delivering to Apple-centric workflows.

**Dithering:** When converting from 24-bit to 16-bit (e.g., for CD), add dither. It's a very quiet noise that prevents audible distortion from bit-depth truncation. TPDF (triangular) is standard. Apply ONCE, at the very last step."""
    },

    "reference_mixing": {
        "title": "Using Reference Tracks",
        "category": "Mastering",
        "content": """A reference track is a professionally mixed/mastered song you compare your mix against:

**Why:** Your ears adapt. After hours of mixing, you lose perspective. A reference snaps you back to reality.

**How:**
1. Choose a song in a similar genre that sounds great on every system
2. Load it into Sozawen (use Reference A/B or just add it as a track)
3. Match the loudness (turn the reference down to match your mix level)
4. A/B between your mix and the reference
5. Listen for: bass balance, vocal level, high-end brightness, stereo width, dynamics

**What to compare:**
- Is your low end as tight?
- Are your vocals as clear and present?
- Is the stereo image as wide?
- Does your mix breathe (dynamic range)?
- Does your mix translate to different speakers?

**Don't copy — calibrate.** The goal isn't to sound identical. It's to make sure your mix is in the same ballpark. Your song has its own identity. The reference just keeps you honest."""
    },

    "modulation": {
        "title": "Key Changes & Modulation",
        "category": "Music Theory",
        "content": """A modulation (key change) shifts the entire harmonic center of a song to a new key. It's one of the most powerful emotional tools in music — when a chorus lifts a half step, you FEEL it before you understand it.

**Types of Modulation:**

**1. Direct / Abrupt (Truck Driver's Modulation)**
- Simply jump to the new key with no preparation.
- Most common: shift UP a half step or whole step for the final chorus.
- Effect: instant energy lift. The audience feels it physically.
- Examples: "I Will Always Love You" (Whitney Houston) — E to F to F#. "She Used to Love Me a Lot" (Johnny Cash) — steps up mid-song. "Man in the Mirror" (Michael Jackson) — steps up at the climax. "Livin' on a Prayer" (Bon Jovi) — Em to Gm, up a minor 3rd.

**2. Pivot Chord Modulation**
- Uses a chord that exists in BOTH the old key and the new key as a bridge.
- Example: In C major, the Am chord is vi. In G major, Am is ii. Use Am as the pivot.
- Effect: smooth, natural. The listener barely notices the key changed.
- Classical and jazz use this extensively.

**3. Relative Major/Minor**
- Shift between a major key and its relative minor (or vice versa). They share all the same notes.
- C major → A minor. The mood changes but the notes don't.
- Effect: emotional shift without harmonic disruption. Verse in minor, chorus in relative major.
- Example: "Stairway to Heaven" (Led Zeppelin) — moves between Am and C.

**4. Parallel Major/Minor**
- Same root, different mode. C major → C minor.
- Only 3 notes change (3rd, 6th, 7th are lowered).
- Effect: dramatic mood shift. Bright to dark on the same root.
- Example: "Creep" (Radiohead) — borrows from parallel minor in the pre-chorus.

**5. Chromatic Modulation**
- Uses a chromatic line (notes moving by half step) to slide into the new key.
- The bass or an inner voice walks chromatically until it lands in the new key.
- Effect: cinematic, sophisticated. Film scores use this constantly.

**6. Circle of Fifths Modulation**
- Move through the circle of fifths: each step is a V→I resolution.
- C → G → D → A. Each step feels natural because V resolves to I.
- Effect: purposeful journey. The listener feels momentum.

**How to transpose in Sozawen:**
1. Detect the key (Key & BPM detection)
2. Use Pitch Shift to move the audio up/down by the desired interval
3. For a half-step up: +1 semitone. Whole step: +2 semitones.
4. For the "truck driver" modulation: split the track at the modulation point, pitch shift the second half.

**How to detect modulation in a song:**
- If the key detection gives you one key but parts of the song sound "off" — the song modulates.
- Separate into stems. Analyze each section independently.
- The Bandmate can help identify where modulations happen.

**Nashville Number System:**
Professional session musicians use numbers instead of note names:
- 1 = root, 2 = second scale degree, etc.
- A "1-4-5" in ANY key means the same progression.
- When a song modulates, you just change the reference note — the numbers stay the same.
- This is why Nashville players can transpose on the fly. They think in relationships, not absolute notes."""
    },

    "transposition": {
        "title": "Transposition",
        "category": "Music Theory",
        "content": """Transposition means moving music to a different key — same intervals, same relationships, different pitch level.

**Why transpose:**
- A vocalist's range doesn't fit the original key
- Matching keys between two songs for a medley
- A guitar capo changes the sounding key
- Moving from guitar-friendly keys (E, A, G) to horn-friendly keys (Bb, Eb, F)

**How to transpose intervals:**

| From → To | Semitones | Direction | Example |
|-----------|-----------|-----------|---------|
| C → C# / Db | +1 | Up half step | Everything shifts up one fret |
| C → D | +2 | Up whole step | Common "energy lift" modulation |
| C → Eb | +3 | Up minor 3rd | Dramatic shift |
| C → E | +4 | Up major 3rd | Distant but powerful |
| C → F | +5 | Up perfect 4th | Subdominant shift |
| C → G | +7 | Up perfect 5th | Dominant shift |
| C → A | -3 or +9 | To relative minor | Same notes, different mood |

**The Capo shortcut (guitar):**
A capo on fret N transposes everything up N semitones while you play the same chord shapes:
- Capo 1 = half step up
- Capo 2 = whole step up
- Capo 3 = minor 3rd up
- Capo 5 = 4th up (play G shapes, get C)
- Capo 7 = 5th up (play C shapes, get G)

**In Sozawen:**
- Use Pitch Shift (semitones) to transpose recorded audio
- Formant preservation keeps vocals sounding natural
- The synth patterns auto-match the detected key
- Export at the new pitch — the original file is never modified

**Transposing instruments:**
Some instruments are "transposing" — they sound a different pitch than written:
- Bb Trumpet: written C sounds as Bb. Transpose UP a whole step for concert pitch.
- Eb Alto Sax: written C sounds as Eb. Transpose DOWN a minor 3rd.
- F Horn: written C sounds as F. Transpose DOWN a 5th.
- Guitar: sounds one octave lower than written in standard notation.
- Bass: sounds two octaves lower than written."""
    },

    # ═══════════════════════════════════════════════════════════════
    # INSTRUMENTS & GEAR
    # ═══════════════════════════════════════════════════════════════

    "guitar_types": {
        "title": "Guitar Types & When to Use Them",
        "category": "Instruments",
        "content": """**Classical / Nylon String**
- Nylon strings, wider neck, softer tone. Fingerpicking, classical, flamenco, bossa nova.
- Use when: you want warmth without volume. Intimate recordings. The nylon softness sits beautifully in a mix without competing with other instruments.
- Recording: condenser mic, 12-16 inches, pointed at 12th fret.

**Steel-String Acoustic (Dreadnought / Full Body)**
- Bright, loud, powerful projection. Strumming, singer-songwriter, folk, country, rock.
- The dreadnought shape projects more low end — fills a room.
- Use when: you need the guitar to cut through or be the primary instrument. Strumming chords. Campfire energy.
- Recording: condenser at 12th fret, 8-12 inches. Add a second mic at the bridge for body.

**Parlor / Small Body Acoustic**
- Quieter, more focused, midrange-forward. Fingerpicking, blues, intimate settings.
- Use when: the guitar needs to sit in a mix without dominating. Pairs well with vocals because it doesn't compete in the low end.

**Acoustic-Electric**
- Same as acoustic but with a built-in pickup. Can go direct into your interface.
- DI (direct input) sounds thinner than a mic'd acoustic. Use both: DI for clarity, mic for warmth. Blend to taste.

**Electric Guitar**
- Solid body, needs an amplifier. Clean, overdrive, distortion. Infinite tonal range.
- Recording options: mic the amp (SM57, 1-3 inches from speaker), use an amp sim plugin, or DI with cabinet impulse responses.

**Bass Guitar**
- Standard: 4 strings (E A D G). Extended range: 5-string adds low B, 6-string adds high C.
- **4-string** — standard for most genres. Covers 90% of music.
- **5-string** — the low B (30.87 Hz) gives sub-bass that 4-string can't reach. Metal, modern worship, hip-hop, R&B.
- **6-string** — adds high C for chordal and solo work. Jazz, progressive, fusion.
- Recording: DI is standard for bass. Mic the amp too for grit and blend.

**7 and 8 String Guitars**
- Extended range guitars. 7-string adds low B (like a bass). 8-string adds low F#.
- Used in djent, progressive metal, ambient, modern heavy music.
- Tuning is critical — heavier strings needed. Standard gauge won't intonate properly on extended range."""
    },

    "tuning_reference": {
        "title": "Tunings & Alternative Tunings",
        "category": "Instruments",
        "content": """**Standard Guitar Tuning (6-string):** E A D G B E (low to high)
- MIDI notes: E2(40) A2(45) D3(50) G3(55) B3(59) E4(64)

**Standard Bass Tuning (4-string):** E A D G
- MIDI notes: E1(28) A1(33) D2(38) G2(43)

**5-String Bass:** B E A D G — adds B0 (23.12 Hz, MIDI 23)
**6-String Bass:** B E A D G C — adds high C3 (MIDI 48)

**7-String Guitar:** B E A D G B E — adds low B1 (MIDI 35)
**8-String Guitar:** F# B E A D G B E — adds low F#1 (MIDI 30)

**Common Alternative Tunings:**
- **Drop D:** D A D G B E — low E dropped to D. Power chords with one finger. Rock, metal, grunge.
- **Drop C:** C G C F A D — everything down a whole step, then drop. Heavy metal.
- **Open G:** D G D G B D — slide guitar, Keith Richards (Rolling Stones).
- **Open D:** D A D F# A D — blues slide, folk.
- **Open E:** E B E G# B E — slide, Duane Allman.
- **DADGAD:** D A D G A D — Celtic, folk, ambient. Jimmy Page.
- **Half Step Down:** Eb Ab Db Gb Bb Eb — Hendrix, Stevie Ray Vaughan. Slightly darker, easier string bending.
- **Whole Step Down:** D G C F A D — heavier feel. Alice in Chains.
- **Nashville Tuning:** Replace low E A D G with their octave-up equivalents. Bright, chimey, doubles beautifully with standard tuning.

**Equal Temperament vs Just Intonation:**
- **Equal temperament** — standard modern tuning. Divides the octave into 12 equal semitones. Every key sounds equally "in tune" (and equally slightly out). What your tuner uses.
- **Just intonation** — intervals based on pure frequency ratios. Sounds more consonant in one key but goes out of tune in others. Used in a cappella, barbershop, some world music.
- **Pythagorean tuning** — based on stacking perfect fifths. Very pure fifths but harsh thirds.
- **Meantone temperament** — compromise between just and equal. Renaissance and Baroque keyboard music.

For recording: use equal temperament (your tuner) unless you're specifically going for a historical or microtonal sound."""
    },

    "vocal_recording": {
        "title": "Recording Vocals",
        "category": "Recording",
        "content": """**The chain:** Singer → Pop filter (2-4 inches from mic) → Condenser mic → Preamp → Interface → DAW

**Mic choice:**
- Large-diaphragm condenser (Rode NT1, AT2020, U87) for studio vocals
- Dynamic (SM7B, SM58) for loud singers or untreated rooms — less room pickup
- Ribbon (Royer 121) for warm, vintage vocal tone — never use phantom power

**Room matters more than the mic.** An untreated room with reflections will make any expensive mic sound bad. Quick fixes:
- Hang blankets behind and to the sides of the singer
- Record in a closet full of clothes (natural absorption)
- Use a reflection filter behind the mic

**Performance tips:**
- Record multiple takes (3-5) and "comp" the best phrases from each
- Keep the energy consistent between takes
- Warm up the voice before recording
- Keep water nearby — room temperature, not cold

**Levels:** Peaks at -12 to -6 dBFS. Leave headroom. Louder is NOT better.

**Double tracking:** Record the same part twice. Pan one left, one right. Instant width. Works for vocals, guitars, anything. The slight natural timing differences create thickness that plugins can't replicate."""
    },

    "drum_recording": {
        "title": "Recording Drums",
        "category": "Recording",
        "content": """**Minimal setup (2 mics):**
- Overhead: condenser above the kit, captures everything
- Kick: dynamic (SM57, Beta 52) inside or just outside the kick drum port
- This covers 80% of what you need. Pan overhead slightly for stereo.

**Standard setup (4 mics):**
- Kick (inside), Snare (SM57 on top), Overheads (matched pair, spaced or X-Y)

**Full setup (8+ mics):**
- Kick in, kick out, snare top, snare bottom (phase inverted), hi-hat, 2 overheads, room mic
- Each tom gets its own mic
- The room mic (3-6 feet away) captures the natural ambience

**Phase is critical.** Multiple mics on the same kit create phase cancellation if the distances aren't right. Use the 3:1 rule. Check phase: mute the overhead, listen to snare close. Unmute overhead — if the snare gets thinner, flip the phase on the overhead.

**Tuning drums:** Tune before recording, not after. A poorly tuned kit wastes everyone's time. Kick: tight batter head, loose resonant. Snare: medium tension, snare wires snug but not choked. Toms: even tension around each head.

**If you don't have a drummer:** Use the built-in drum machine. Program a pattern, render it, record your instruments on top. Then replace the programmed drums with a real drummer later if you want."""
    },

    "mixing_order": {
        "title": "Mixing Order & Workflow",
        "category": "Mixing",
        "content": """There's no single right order, but here's a workflow that works:

**1. Organization (before you touch a fader)**
- Name every track
- Color-code by group (drums = blue, guitars = green, vocals = purple)
- Delete unused tracks and empty regions
- Set up groups/buses (drum bus, guitar bus, vocal bus)

**2. Static balance**
- All faders at 0dB, pan centered
- Solo nothing — listen to everything together
- Set rough volume balance by pulling faders DOWN to taste
- Get the lead vocal at the right level first — everything else serves it

**3. Panning**
- Center: kick, snare, bass, lead vocal
- Slight L/R: rhythm guitars, keys, background vocals
- Wide: stereo guitars, percussion, pads, reverb returns

**4. EQ (subtractive first)**
- HPF on everything except kick and bass
- Cut mud (200-400Hz) on guitars and keys
- Clear space for the vocal (2-4kHz) by cutting other instruments there

**5. Compression**
- Vocals: even out the performance
- Drums: control dynamics, add punch
- Bass: consistent low end
- Mix bus: gentle glue (1-2dB reduction)

**6. Space (reverb, delay)**
- Send-based: one reverb bus, multiple tracks feeding it
- Less is more — you can always add, hard to remove

**7. Automation**
- Ride the vocal fader — every phrase at the right level
- Automate panning for movement
- Push the chorus slightly louder than the verse

**8. Reference check**
- Compare to a professional mix in the same genre
- Check on multiple speakers (monitors, headphones, phone, car)
- Take breaks — fresh ears catch problems"""
    },

    "frequency_chart": {
        "title": "Instrument Frequency Chart",
        "category": "Mixing",
        "content": """Where each instrument lives in the frequency spectrum:

| Instrument | Fundamental Range | Key Frequencies |
|------------|------------------|-----------------|
| **Kick drum** | 40-100 Hz | Thump: 60-80Hz. Click/attack: 2-5kHz |
| **Snare** | 150-250 Hz | Body: 200Hz. Crack: 2-4kHz. Wires: 8-12kHz |
| **Hi-hat** | 300Hz-15kHz | Stick: 8-10kHz. Shimmer: 12-16kHz |
| **Bass guitar** | 40-400 Hz | Fundamental: 40-200Hz. Growl: 700Hz-1kHz. String noise: 2-4kHz |
| **Electric guitar** | 80-5kHz | Body: 200-500Hz. Bite: 2-4kHz. Presence: 4-6kHz |
| **Acoustic guitar** | 80-12kHz | Body: 100-250Hz. String: 2-5kHz. Air: 8-12kHz |
| **Piano** | 27-4200 Hz | Warmth: 100-300Hz. Presence: 2-5kHz. Sparkle: 8-12kHz |
| **Vocals (male)** | 80-500 Hz | Chest: 100-250Hz. Clarity: 2-4kHz. Air: 8-12kHz |
| **Vocals (female)** | 150-1kHz | Body: 200-400Hz. Clarity: 3-5kHz. Air: 10-14kHz |
| **Strings** | 200-8kHz | Warmth: 200-500Hz. Rosin: 7-10kHz |
| **Brass** | 80-6kHz | Honk: 500Hz-1kHz. Brilliance: 3-6kHz |

**The rule:** If two instruments share the same fundamental range, one needs to give way. Cut, don't boost. Make space, don't fight for it."""
    },

    "common_mistakes": {
        "title": "Common Mixing Mistakes",
        "category": "Mixing",
        "content": """**1. Mixing too loud.** Turn your monitors down. If it sounds good quiet, it'll sound great loud. If it only sounds good loud, the mix has problems.

**2. Too much low end.** Untreated rooms exaggerate bass. Use a spectrum analyzer. Compare to a reference. HPF everything that isn't kick or bass.

**3. Solo-button syndrome.** A track that sounds amazing solo may not fit the mix. Always check in context. The mix is what the listener hears.

**4. Over-processing.** Not every track needs EQ, compression, reverb, and saturation. If it sounds good raw, leave it alone. The best processing is the processing you don't do.

**5. No breaks.** Your ears fatigue after 30-60 minutes. Take a 10-minute break every hour. Walk outside. Reset your hearing.

**6. Not checking in mono.** 25% of listening happens on mono speakers (phones, smart speakers). Hit the mono button. If something disappears, there's a phase issue.

**7. Mixing on headphones only.** Headphones exaggerate stereo width and detail. Check on speakers too. The truth is usually between both.

**8. Not using a reference.** Without a reference track, you're mixing in the dark. Load one. Level-match it. Compare frequently.

**9. Too much reverb.** Reverb hides problems. A dry, well-balanced mix sounds better than a washed-out one. Use just enough to create space. You should barely notice it's there.

**10. Mastering in the mixing session.** Finish the mix. Export. Open a new session. THEN master. Fresh ears, fresh perspective."""
    },

    "bass_guitar": {
        "title": "Bass Guitar — The Foundation",
        "category": "Instruments",
        "content": """Bass bridges rhythm and harmony. It locks with the kick drum and outlines the chord progression.

**4-String (Standard):** E A D G. Covers 90% of all music. **5-String:** Adds low B (30.87 Hz) — modern metal, worship, R&B. **6-String:** Adds high C — jazz, progressive, chordal playing. **Fretless:** No frets, singing tone with natural slides. Jaco Pastorius.

**P-Bass vs J-Bass:** Precision = fat, punchy, sits in a mix (Motown, punk, rock). Jazz = brighter, growlier (slap, funk, fusion). **Active vs Passive:** Passive = warm, organic. Active = hotter, more clarity, extended low end.

**Recording:** DI is standard. Mic the amp for grit, blend both. Keep bass below 200Hz mostly mono in the mix."""
    },

    "drums_detailed": {
        "title": "Drums & Percussion — Complete Guide",
        "category": "Instruments",
        "content": """**Kick:** 20-24 inches. Muffle with a pillow inside for punch. **Snare:** 14 inches. Wood = warm, metal = bright. **Hi-Hat:** 13-15 inches. Foot pressure controls open/closed. **Toms:** Tune high to low, left to right. **Ride:** 20-22 inches, bell for accents. **Crash:** 16-18 inches, accents and transitions.

**Percussion beyond the kit:** Congas/bongos (Latin), djembe (West African), cajon (acoustic), tambourine (shimmer), shaker (fills gaps), cowbell (funk/Latin).

**Tuning matters more than the drum.** Even tension around each head. Snare wires tight enough to respond, loose enough to breathe."""
    },

    "keyboards_piano": {
        "title": "Keyboards, Piano & Synths",
        "category": "Instruments",
        "content": """**Acoustic Piano:** 88 keys, A0-C8. Grand projects more, upright fits rooms. **Rhodes:** Warm, bell-like soul/jazz. **Wurlitzer:** Brighter, edgier. **Clavinet:** Funky, percussive (Stevie Wonder).

**Synth types:** Subtractive (filter a rich waveform — Moog, Juno), FM (modulating oscillators — DX7 bells), Wavetable (morphing shapes — Serum), Granular (audio into textures).

**Hammond B3:** THE organ sound. Leslie speaker adds rotating effect. **MIDI Controllers:** Send note data to synths like Sozawen's. Weighted keys = piano feel, synth-action = lighter.

**In the mix:** Piano is wide-range — HPF at 100Hz, presence at 3-5kHz. Carve space so it doesn't step on vocals."""
    },

    "vocals_instrument": {
        "title": "The Voice as an Instrument",
        "category": "Instruments",
        "content": """The most expressive instrument and the hardest to record well.

**Ranges:** Bass (E2-E4, Johnny Cash), Baritone (A2-A4, Eddie Vedder), Tenor (C3-C5, Freddie Mercury), Alto (F3-F5, Amy Winehouse), Mezzo-Soprano (A3-A5, Adele), Soprano (C4-C6, Mariah Carey).

**Layering:** Double track (sing it twice, pan L/R). Harmonies (3rds and 5ths). Ad-libs between phrases. Whisper track underneath for intimacy.

**Processing chain:** HPF at 80Hz → cut mud 200-300Hz → presence 3-5kHz → compression 3:1 → de-esser 6-8kHz → reverb on a send.

**The rule:** If it doesn't sound good raw, no processing will save it. Get the performance right first."""
    },

    "strings_brass_woodwinds": {
        "title": "Strings, Brass & Woodwinds",
        "category": "Instruments",
        "content": """**Strings:** Violin (G3-E5, melody), Viola (C3-A4, inner voice), Cello (C2-A3, the most vocal), Double Bass (E1-G2, orchestral foundation). Record solo strings with a condenser 2-3 feet away aimed at the f-holes.

**Brass:** Trumpet (Bb, bright/cutting), Trombone (Bb, warm/powerful), French Horn (F, rich/noble), Tuba (BBb, deep foundation). Brass cuts through any mix — use sparingly and it's devastating.

**Woodwinds:** Flute (C, airy), Clarinet (Bb, woody), Saxophone (Bb/Eb, jazz/R&B/rock), Oboe (C, nasal/penetrating — the orchestra tunes to it).

**In modern production:** Even one real string or brass track transforms a pop song. Layer real and sampled together — the real performance adds life."""
    },

    "electronic_production": {
        "title": "Electronic Music Production",
        "category": "Instruments",
        "content": """Sound design IS the instrument. The synth patch, drum selection, and effect chain IS the performance.

**Essential concepts:** Oscillator (raw tone) → Filter (shape it) → Envelope ADSR (evolve over time) → LFO (modulate parameters). **808 kick:** Pitch-swept sine wave — foundation of hip-hop, trap, modern pop.

**Layering:** Stack sounds for thickness. Sub sine under saw bass. Clap with snare. Pluck with pad. Each layer covers a frequency range the others don't.

**Genres:** House (120-130 BPM, four-on-the-floor), Techno (125-150, hypnotic), D&B (160-180, breakbeats), Dubstep (140 half-time, wobble bass), Ambient (no fixed BPM, texture), Lo-fi (deliberate imperfection)."""
    },

    "world_instruments": {
        "title": "World & Folk Instruments",
        "category": "Instruments",
        "content": """**Stringed:** Sitar (India, buzzing resonance), Oud (Middle East, fretless/microtonal), Kora (West Africa, cascading arpeggios), Erhu (China, haunting two-string), Banjo (American/African origin, bright/percussive), Ukulele (Hawaiian, warm/intimate), Mandolin (Italian/bluegrass, paired strings).

**Percussion:** Tabla (India, complex rhythmic patterns), Djembe (West Africa, three voices: bass/tone/slap), Bodhrán (Ireland, frame drum), Steel Pan (Trinidad, tuned metal from oil barrels).

**Wind:** Didgeridoo (Australia, circular breathing drone), Shakuhachi (Japan, zen bamboo flute), Pan Flute (Andes, ethereal), Bagpipes (Scotland, continuous drone with melody).

**Recording world instruments:** Respect the room. Many were designed for specific acoustic spaces. Use room mics. Don't over-process — the beauty is in the human touch."""
    },

    "microphone_guide": {
        "title": "Microphone Types & Selection",
        "category": "Instruments",
        "content": """**Dynamic:** Rugged, handles loud sources. SM57 (amps, snare, everything — the Swiss army knife), SM58 (live vocals standard), SM7B (broadcast/studio vocals, smooth and warm). Use in untreated rooms and loud environments.

**Condenser:** Sensitive, detailed, full frequency response. AT2020 (honest entry-level), Rode NT1 (ultra-quiet, great first studio mic), AKG C414 (multi-pattern workhorse), Neumann U87 (the professional standard). Requires 48V phantom power. More sensitive to room acoustics — treat your space.

**Ribbon:** Smooth, warm, vintage character. Royer R-121 (amps, brass, vocals). Figure-8 polar pattern. NEVER use phantom power with passive ribbons — it can destroy the element.

**Polar Patterns:** Cardioid (front only, most common, good isolation), Figure-8 (front+back, rejects sides), Omnidirectional (everything equally, most natural), Supercardioid (tighter than cardioid, more rejection).

**Buy order:** Start with a dynamic all-rounder (SM57) → add a large-diaphragm condenser for vocals → add a matched pair of pencil condensers for stereo recording. Everything after that is refinement, not necessity."""
    },
    # ═══════════════════════════════════════════════════════════════
    # HARDWARE & STUDIO
    # ═══════════════════════════════════════════════════════════════

    "audio_interfaces": {
        "title": "Audio Interfaces — Choosing & Using",
        "category": "Hardware",
        "content": """The interface converts analog to digital and back. The most important piece of gear you'll buy.

**Entry level (1 input):** Focusrite Scarlett Solo, M-Audio M-Track Solo. One mic or instrument at a time. Good preamps for the price.

**Mid range (2 inputs):** Focusrite Scarlett 2i2, M-Audio M-Track Duo, PreSonus AudioBox. Record guitar and vocals simultaneously. The sweet spot for most home studios.

**Professional (2-4 inputs, better converters):** Universal Audio Volt, Audient iD14, SSL 2+. Cleaner preamps, lower noise floor, more routing options.

**High end (4+ inputs, DSP):** Universal Audio Apollo, RME Babyface Pro, Audient iD44. Multiple simultaneous inputs for full band or drum recording.

**Inputs needed:** 1-2 for singer-songwriter. 4 for a band rehearsal. 8+ for drums with multiple mics. Sozawen maps each input to its own track.

**Sample rate:** 44.1kHz is fine for music. 48kHz for video sync. Higher rates double file size with marginal audible difference. **Latency:** Buffer 128 samples = ~3ms (monitoring). 256 = ~6ms (safe default). 512+ = mixing only."""
    },

    "monitors_headphones": {
        "title": "Studio Monitors & Headphones",
        "category": "Hardware",
        "content": """Studio monitors are flat — they show what your mix actually sounds like, not what sounds fun.

**Monitors to research:** Yamaha HS5 (industry standard flat response), JBL 305P (wider sweet spot), KRK Rokit 5 (slightly enhanced low end), Adam Audio T7V (detailed highs). Place in equilateral triangle with your head, tweeters at ear height, 6+ inches from walls.

**Headphones — Open-back (mixing):** AKG K240, Beyerdynamic DT 990, Sennheiser HD 600. Natural imaging but sound leaks out. **Closed-back (tracking):** Audio-Technica ATH-M50x, Beyerdynamic DT 770, Sony MDR-7506. No bleed into the mic during recording.

**The truth is between both.** Mix on monitors, check on headphones, check on earbuds, check in the car. Every system reveals different problems. Never mix on headphones alone — they exaggerate stereo width and bass detail."""
    },

    "cables_connections": {
        "title": "Cables & Connections",
        "category": "Hardware",
        "content": """**XLR:** 3-pin balanced. Mics, monitors. Noise rejection over long runs — always use for mics. **TRS:** 1/4 inch balanced (two rings). Monitor connections, balanced lines. **TS:** 1/4 inch unbalanced (one ring). Guitar cables. Keep under 20 feet.

**Balanced vs Unbalanced:** Balanced carries the signal twice (normal + inverted). Noise picked up cancels out at the receiving end. XLR can run 100+ feet clean. TS picks up hum after 15-20 feet.

**USB:** Interface to computer. USB-C current. Thunderbolt for lowest latency. **MIDI:** Note data, no audio. 5-pin DIN (classic) or USB (modern).

**The rule:** Shortest cable that reaches. Don't run audio parallel to power cables. Coil in figure-8, not circles."""
    },

    "acoustic_treatment": {
        "title": "Room Treatment & Acoustics",
        "category": "Hardware",
        "content": """The room is the most important gear. A $3,000 mic in an untreated room sounds worse than a $100 mic in a treated one.

**Priority order:** 1. Bass traps in corners (4+ inch rigid fiberglass). Single biggest improvement. 2. First reflection panels (side walls, ceiling — use mirror trick to find the spots). 3. Rear wall diffusion or absorption.

**Budget treatment:** Moving blankets behind the vocalist. Bookshelves as diffusers. Couch and carpet for absorption. Closet full of clothes = natural vocal booth.

**Don't:** Cover everything in foam (only absorbs highs, makes room boomy). Make the room completely dead (unnatural, fatiguing). **Do:** Treat about 30% of wall area. Balance absorption and diffusion."""
    },

    "acoustic_guitar_tones": {
        "title": "Acoustic Guitar Brands & Their Sound",
        "category": "Instruments",
        "content": """Every acoustic guitar brand has a sonic signature shaped by their bracing, tonewoods, and body shape. Knowing the differences helps you pick the right one for a recording.

**Taylor** — Bright, clear, articulate. Their V-Class and X-bracing emphasizes note separation and high-end sparkle. Sits beautifully in a mix without fighting other instruments. Grand Auditorium (GA) is their most versatile shape. Best for: recording (mics love Taylors), fingerpicking, modern pop/folk.

**Martin** — Warm, thick, woody. Scalloped X-bracing gives deep bass response and rich midrange. The dreadnought shape (D-28, D-18) defines what "acoustic guitar" sounds like. Decades of strumming songs were recorded on Martins. Best for: singer-songwriter strumming, country, folk, Americana. The warmth fills a room.

**Gibson** — Punchy, midrange-forward, gutsy. Shorter scale length (24.75" vs 25.5") means looser string tension — warmer, easier bends. The J-45 is the workhorse. Thicker neck. Best for: blues, rock, aggressive strumming, singer-songwriters who want body without sparkle.

**Yamaha** — Honest, balanced, reliable. The FG/FS series punches above its price at every level. No extreme personality — records clean and sits where you put it in a mix. Best for: beginners, budget-conscious recording, versatile studio use.

**Takamine** — Clear with a strong midrange. Known for excellent built-in electronics (live performance). Their NEX body shape is comfortable. Best for: live performance with plugged-in sound, country, pop.

**Seagull** — Warm, cedar-topped. Canadian-made, cedar top instead of spruce gives an immediate warmth and faster break-in. Best for: fingerpicking, folk, intimate recording.

**Collings** — Boutique perfection. Every note rings clearly. Unforgiving of sloppy playing (which means it rewards good technique). Best for: studio work where every detail matters.

**Recording tip:** A bright guitar (Taylor) works when the vocal is warm. A warm guitar (Martin) works when the vocal is bright. Contrast creates clarity — two warm sources fight for the same space."""
    },

    "electric_guitar_tones": {
        "title": "Electric Guitars & Their Sound",
        "category": "Instruments",
        "content": """**Fender Stratocaster** — Three single-coil pickups. Bright, glassy, chimey. The "quack" in positions 2 and 4 (between pickups) is unmistakable. Clean tones sparkle. Overdriven tones have bite without mud. Hendrix, Mayer, Gilmour, Knopfler. Best for: blues, funk, clean pop, anything that needs clarity and expression.

**Fender Telecaster** — Two single-coils. Brighter and more aggressive than a Strat. The bridge pickup has twang and snap that defined country and indie rock. Simpler circuit = more direct signal. Keith Richards, Bruce Springsteen, Radiohead. Best for: country, indie, punk, anything raw and honest.

**Gibson Les Paul** — Two humbuckers. Fat, thick, warm sustain. The mahogany body and set neck give weight that single-coils can't match. The PAF humbucker tone is the sound of classic rock. Slash, Jimmy Page, Duane Allman. Best for: rock, blues, jazz, anything that needs power and sustain.

**Gibson SG** — Lighter than a Les Paul, slightly brighter, faster neck. Same humbuckers but the thinner body reduces low-end weight. Angus Young. Best for: hard rock, punk, aggressive playing.

**PRS (Paul Reed Smith)** — The middle ground. Warm like a Gibson but with Fender-like clarity. Versatile — coil-split humbuckers switch between single-coil and humbucker voicings. Santana, Mark Tremonti. Best for: everything. The most versatile electric guitar.

**Ibanez** — Thin, fast necks. Extended range (7/8 string). HSH pickup configurations. Built for speed and precision. Steve Vai, Joe Satriani, djent. Best for: metal, shred, progressive, fusion.

**Gretsch** — Hollow/semi-hollow. Twangy, jangly, with natural feedback at volume. Filter'Tron pickups are brighter than PAFs. Brian Setzer, Malcolm Young, George Harrison. Best for: rockabilly, country, jangly indie, classic rock rhythm.

**Rickenbacker** — Jangly, bright, cutting. The 12-string Rickenbacker defined the 60s. The Beatles, The Byrds, R.E.M. Best for: jangle pop, alternative, anything that needs shimmer.

**Recording tip:** Single-coils hum under fluorescent lights and near monitors. Humbuckers are quiet. If your single-coil guitar hums during recording, face away from the monitor or use Sozawen's hum removal."""
    },

    "amp_tones": {
        "title": "Guitar Amplifiers & Their Character",
        "category": "Instruments",
        "content": """Every amp has a voice. Knowing what each one does helps you choose the right tone before you record.

**Fender** — Clean, headroom, sparkle. The Twin Reverb is the definition of clean guitar tone. The Deluxe Reverb breaks up beautifully at lower volumes. Fender cleans are the benchmark everything else is measured against. Best for: clean tones, blues breakup, country, jazz.

**Marshall** — Midrange crunch, aggressive, British. The Plexi (JTM45/JMP) is the sound of 70s rock. The JCM800 is the sound of 80s metal. Marshalls push midrange — they cut through a band mix like nothing else. Best for: rock, hard rock, classic metal.

**Vox** — Chimey, jangly, mid-focused but brighter than Marshall. The AC30 has a Class A circuit that compresses naturally as you push it. The Beatles, The Edge, Brian May. Top Boost channel is iconic. Best for: British invasion, indie, jangle, chimey clean-to-crunch.

**Mesa/Boogie** — High gain, tight, precise. The Dual Rectifier defined modern metal tone. The Mark series (Mark V) is the most versatile amp ever made — Petrucci, Metallica. Tight low end that stays defined even with extreme distortion. Best for: metal, progressive, high-gain.

**Orange** — Thick, fuzzy, woolly midrange. The Rockerverb and Thunderverb have a distinctive "chewiness" that no other amp has. Brent Hinds, Jim Root. Best for: stoner rock, doom, sludge, alternative.

**Peavey 5150/6505** — The budget metal standard. Tight, aggressive, scooped. Designed with Eddie Van Halen. Best for: metal on a budget. Sounds huge recorded.

**Amp sims vs real amps:** Modern amp simulation (Neural DSP, Line 6 Helix, amp plugins) has reached the point where blind tests fool professionals. If you're recording at home, a good amp sim through your interface is often better than a real amp in an untreated room — no mic bleed, no volume complaints, consistent tone. Record with the sim, reamp later if you want."""
    },

    "bass_amp_tones": {
        "title": "Bass Amps & Their Character",
        "category": "Instruments",
        "content": """**Ampeg SVT** — THE bass amp. Tube-driven, massive, authoritative. The 8x10 cab moves air like nothing else. Warm, gritty when pushed, enormous low end with midrange presence that cuts through any band. Used on more hit records than every other bass amp combined. Geddy Lee, Flea, Chris Squire. Best for: rock, punk, metal, anything that needs bass you can feel in your chest.

**Ampeg B-15 (Portaflex)** — The studio classic. Smaller, warmer, rounder than the SVT. James Jamerson recorded Motown through a B-15. Smoother breakup, more controlled low end. Best for: studio recording, Motown, R&B, jazz, anything that needs warmth without overwhelming the room.

**Fender Bassman** — Originally a bass amp, became a legendary guitar amp too. Clean, bright, punchy. Less low-end weight than Ampeg but more clarity and note definition. Best for: country, classic rock, clean tones, sessions where bass needs to stay tight and defined.

**Darkglass** — Modern, aggressive, defined. Their Microtubes preamps (B7K, Alpha Omega) add harmonic distortion that stays tight even with drop tunings. The sound of modern metal bass. Best for: djent, progressive metal, modern rock. Surgical distortion without mud.

**Gallien-Krueger (GK)** — Clean, hi-fi, articulate. The 800RB powered 80s and 90s bass tone. Bright, punchy, cuts through without grit. Flea's Red Hot Chili Peppers slap tone. Best for: slap, funk, pop, anything that needs clarity and snap.

**Orange** — Warm, woolly, thick. Same midrange chewiness as their guitar amps. The AD200B is all-tube warmth. Best for: stoner, doom, sludge, psychedelic — when you want bass that feels like a blanket of sound.

**Hartke** — Aluminum cone speakers give a distinctive bright, punchy attack. Larry Graham. Best for: slap, gospel, R&B where bass needs to pop.

**Recording bass amps:** Close mic (SM57 or RE20) 1-3 inches from the speaker for grit and character. Blend with the DI signal for clarity. The DI gives you the clean low end, the mic gives you the personality. In Sozawen, these are two tracks — mix to taste."""
    },

    "drum_brands": {
        "title": "Drum Brands & Their Sound",
        "category": "Instruments",
        "content": """**DW (Drum Workshop)** — Premium American-made. Known for their VLT (Vertical Low Timbre) shell construction. Warm, controlled, focused. Studio drums — they record beautifully because DW tunes the shell resonance to specific notes. Best for: studio recording, any genre where drum tone matters.

**Pearl** — Versatile, reliable, wide range from student to professional. The Reference series is world-class. The Export series is the best-selling kit in history for a reason — it sounds good out of the box at every price point. Best for: everything. A Pearl kit serves any genre.

**Tama** — Punchy, bright, articulate. The Starclassic series (birch/walnut) has a focused attack that engineers love. The Iron Cobra pedals are legendary. Best for: rock, metal, fusion — anything that needs drums with presence and cut.

**Yamaha** — Balanced, honest, consistent. Like their monitors and pianos, Yamaha drums are designed to be accurate rather than colored. The Recording Custom series is a studio standard. Steve Gadd, Dave Weckl. Best for: studio, jazz, session work, education.

**Ludwig** — The sound of classic rock. John Bonham's kit was Ludwig. The Vistalite (acrylic shells) is iconic. Warm, open, big. Best for: classic rock, blues, anything that needs drums to breathe and ring.

**Gretsch** — Warm, round, vintage. The Broadkaster series has a natural warmth that records beautifully without heavy dampening. Best for: jazz, blues, Americana, anything that needs organic drum tone.

**Mapex** — Modern, versatile, aggressive. The Saturn series (hybrid walnut/maple) balances warmth with attack. Strong fundamental without excessive overtones. Best for: modern rock, metal, pop — focused sound at every volume.

**Cymbals — the other half:**
- **Zildjian:** Bright, traditional. A Custom (bright, cutting), K series (dark, complex, jazz).
- **Sabian:** Versatile range. AAX (bright, modern), HHX (dark, washy, expressive).
- **Meinl:** Dark, dry, complex. Byzance series is the standard for jazz and modern worship. Extra Dry for hip-hop and R&B ghost notes.
- **Paiste:** Bright, clean, defined. The 2002 series is the brightest major cymbal. Formula 602 is warm and vintage.

**The cymbal matters as much as the drum.** A cheap kit with great cymbals sounds better than an expensive kit with cheap cymbals. Upgrade cymbals first."""
    },

    "studio_budget_guide": {
        "title": "Building a Studio on Any Budget",
        "category": "Hardware",
        "content": """Everything here works with Sozawen. Build what you can afford — upgrade when you outgrow it. Prices change, so research current pricing before buying.

**Tier 1 — The Essentials:**
- Entry-level audio interface (1 input — Scarlett Solo, M-Track Solo)
- One microphone (AT2020 condenser or SM57 dynamic)
- Headphones you already own
- Sozawen
- This is enough to record, edit, mix, master, and export a finished song.

**Tier 2 — The Bedroom Studio:**
- 2-input interface (Scarlett 2i2, M-Track Duo)
- Quality condenser mic (Rode NT1 or similar)
- Closed-back headphones (ATH-M50x, DT 770)
- Pop filter, mic stand, XLR cable
- Sozawen
- Record vocals and guitar simultaneously. Monitor properly.

**Tier 3 — The Serious Setup:**
- Mid-range interface (Audient iD14, SSL 2+)
- Condenser mic + dynamic mic (covers most sources)
- Studio monitors (Yamaha HS5, JBL 305P)
- Quality headphones for reference
- Basic acoustic treatment (DIY corner traps and first reflections)
- Sozawen
- Professional monitoring. Treated room. Real results.

**Tier 4 — The Home Studio:**
- Professional interface (Universal Audio Volt, Apollo Solo)
- Multiple mics (condenser + dynamic + maybe a ribbon)
- Accurate monitors (Adam Audio T7V, Focal Alpha)
- Reference headphones (Sennheiser HD 600)
- Full room treatment
- MIDI controller
- Sozawen
- Everything you need to make records that compete with professional studios.

**The truth:** The gear ceiling stopped mattering years ago. An entry-level interface and a decent mic with Sozawen can make a record that sounds as good as what came out of Abbey Road in the 1960s. The difference is the performance, the songs, and the time you put in. Not the price tag."""
    },

    # ═══════════════════════════════════════════════════════════════
    # RELEASING YOUR MUSIC
    # ═══════════════════════════════════════════════════════════════

    "release_guide": {
        "title": "How to Release on Spotify, Apple Music & More",
        "category": "Releasing",
        "content": """Your song is done. Now what? Here's the complete step-by-step to get your music on every streaming platform.

**Step 1: Master your track**
- Target **-14 LUFS integrated** for Spotify (they normalize to this)
- Target **-16 LUFS** for Apple Music
- True peak must be below **-1 dBTP** (prevents distortion on playback)
- Export as **WAV, 44.1kHz, 16-bit** (the universal standard)
- Use Sozawen's Loudness meter and Limiter to hit these targets

**Step 2: Choose a distributor**
Distributors get your music onto streaming platforms. You keep your rights.

| Service | Cost | Keeps royalties? | Best for |
|---------|------|-----------------|----------|
| **DistroKid** | $22.99/year | 100% to you | Most indie artists |
| **TuneCore** | $9.99/single | 100% to you | Single releases |
| **CD Baby** | $9.95/single (one-time) | 91% to you | Set-and-forget |
| **Amuse** | Free tier available | 100% on free | Budget-conscious |
| **LANDR** | $9.99/year | 100% to you | Also offers mastering |

**Step 3: Prepare your metadata**
- **Song title** — exactly as you want it displayed
- **Artist name** — consistent across all releases
- **Genre** — pick primary and secondary
- **Release date** — set 2-4 weeks out (gives time for playlist consideration)
- **ISRC code** — your distributor usually generates this (unique identifier per track)
- **UPC/EAN** — for albums/EPs (distributor provides)

**Step 4: Cover art**
- **Minimum 3000x3000 pixels**, square, RGB, JPG or PNG
- No blurry images, no screenshots, no copyrighted images
- Simple is better — look at how your favorite artists do it
- Canva.com (free) or hire someone on Fiverr ($5-25)

**Step 5: Register for royalties**
- **ASCAP** or **BMI** (US) — collects performance royalties when your song plays on radio, TV, or in venues. Free to join.
- **SoundExchange** — collects digital performance royalties (streaming). Free.
- **Your distributor** handles mechanical royalties from streams.

**Step 6: Upload and release**
- Upload your WAV to your distributor
- Fill in metadata, upload cover art
- Set release date (Friday is industry standard)
- Submit to Spotify for playlist consideration (through Spotify for Artists — do this AT LEAST 7 days before release)

**Step 7: Promote**
- Share on every platform you're on
- Send to friends, family, local music communities
- Submit to independent playlist curators (SubmitHub, PlaylistPush)
- Post a behind-the-scenes story about making the song — people connect with the process

**You own everything.** Your song is automatically copyrighted the moment you create it. Registration with the US Copyright Office ($65) provides additional legal protection but isn't required."""
    },

    "copyright": {
        "title": "Copyright, Publishing & Protecting Your Music",
        "category": "Releasing",
        "content": """Your music is yours. Here's what you need to know to protect it.

**Automatic copyright:** The moment you record or write down your song, it's copyrighted. You don't need to register, file paperwork, or pay anyone. It's yours by law.

**BUT registration helps:** Registering with the U.S. Copyright Office ($65 per work at copyright.gov) gives you:
- Legal proof of ownership with a specific date
- The ability to sue for statutory damages (up to $150,000 per infringement)
- Without registration, you can only sue for actual damages (what you lost)

**The two copyrights in every song:**
1. **Composition copyright** — the melody and lyrics (the SONG itself). This is yours as the songwriter.
2. **Sound recording copyright** — the specific recording (the MASTER). This is yours as the artist/producer.

If you wrote it AND recorded it in Sozawen, you own BOTH. That's 100% ownership.

**Publishing:**
- Publishing = the business of your compositions
- A publisher shops your songs for sync licensing (TV, film, ads, games)
- You can self-publish (keep 100%) or sign with a publisher (they take 15-50% but open doors)
- Register with ASCAP or BMI as both a **writer** AND a **publisher** to collect all royalties

**Performance Rights Organizations (PROs):**
- **ASCAP** — free to join, collects when your music is played publicly
- **BMI** — free to join, same function
- **SESAC** — invitation only
- You only join ONE. They don't compete — they all collect from the same places.
- International: PRS (UK), GEMA (Germany), SACEM (France), JASRAC (Japan)

**Sync licensing** (TV, film, games, ads):
- This is where real money is for indie artists
- A 30-second placement in a TV show can pay $1,000-50,000+
- Submit to sync libraries: Musicbed, Artlist, Epidemic Sound, or hire a sync agent
- Having clean, well-mastered tracks with clear ownership makes you attractive

**Sozawen instruments are copyright-free:**
All 62 instruments in Sozawen are synthesized from math. No samples, no licensed content, no royalty obligations. The sounds you create are 100% yours. This is by design — we built it this way so nothing stands between you and ownership.

**Protect your lyrics:**
Save your lyrics with a date. Email them to yourself (creates a timestamp). Better yet, register the full song with the Copyright Office. The $65 is worth the peace of mind."""
    },

    "export_platforms": {
        "title": "Export Settings for Every Platform",
        "category": "Releasing",
        "content": """Different platforms have different requirements. Here are the exact settings for each:

**Spotify:**
- Format: WAV or FLAC
- Sample rate: 44.1 kHz
- Bit depth: 16-bit or 24-bit
- Loudness target: **-14 LUFS integrated**
- True peak: **-1 dBTP** maximum
- Spotify normalizes everything to -14 LUFS — if yours is louder, they turn it down. If quieter, they leave it (won't turn up).

**Apple Music:**
- Format: WAV or AIFF
- Sample rate: 44.1 kHz (or up to 192 kHz for spatial audio)
- Loudness target: **-16 LUFS integrated**
- True peak: **-1 dBTP**
- Apple Music also supports Dolby Atmos and lossless

**YouTube:**
- Format: WAV or FLAC (YouTube re-encodes anyway)
- Loudness target: **-14 LUFS**
- True peak: **-1 dBTP**

**SoundCloud:**
- Format: WAV or FLAC (for best quality; they transcode to 128kbps for free, 256kbps for Go+)
- Loudness: no normalization — louder = louder

**CD/Physical:**
- Format: WAV
- Sample rate: 44.1 kHz
- Bit depth: 16-bit
- Loudness: **-9 to -12 LUFS** (CDs don't normalize)
- True peak: **-0.3 dBTP**

**In Sozawen:** Use the Export tool. Set the format, sample rate, and bit depth. Check LUFS with the Loudness meter. Adjust the Limiter until you hit the target. Export. Done.

**Pro tip:** Always master at **-14 LUFS** first. This works for Spotify, YouTube, and most platforms. If you need a louder version for CD or SoundCloud, make a separate master."""
    },

    "collaboration": {
        "title": "Collaborating with Other Musicians",
        "category": "Releasing",
        "content": """Music is better together. Here's how to collaborate using Sozawen.

**Sharing your project:**
1. Use **Export → Project File (.sozawen)** to save your entire session
2. The project file includes all track references, effects settings, markers, and arrangement
3. Send it to your collaborator — they open it in Sozawen and pick up where you left off

**Sharing stems:**
1. Use **Export → All Stems (ZIP)** to export each track as a separate WAV
2. Your collaborator can import these into ANY DAW — not just Sozawen
3. Label your stems clearly: "Vocals_Lead.wav", "Guitar_Rhythm.wav", "Drums_Full.wav"

**Remote collaboration workflow:**
1. You record guitar and vocals, export stems
2. Send to your bassist — they import your stems, record bass, export their stem back
3. You import their bass stem into your project
4. Repeat with drummer, keys player, etc.
5. Final mix happens in one session with all stems

**Splits and credits:**
- Agree on songwriting splits BEFORE the song is finished
- Standard: lyrics writer gets 50%, music writer gets 50%
- If you co-write both: split evenly or by contribution
- Put it in writing — even a text message is better than nothing
- Register all writers with your PRO (ASCAP/BMI)

**Finding collaborators:**
- Join the Sozawen Discord — musicians looking to collaborate
- BandLab, Kompoz, SoundBetter — online collaboration platforms
- Local open mics, music schools, church worship teams
- Reddit: r/MusicInTheMaking, r/BedroomBands

**The golden rule:** Communicate early, communicate often. Disagreements about credits after a song blows up are how friendships end. Agree on everything upfront."""
    },

    "lyrics_protection": {
        "title": "Protecting Your Lyrics & Songwriting",
        "category": "Releasing",
        "content": """Your words are yours the moment you write them. Here's how to make sure they stay that way.

**Automatic protection:**
Under US copyright law (and most international law via the Berne Convention), your lyrics are copyrighted the instant you write them down or record them. No registration required. No © symbol needed. It's automatic.

**But proof matters:**
If someone steals your lyrics, you need to PROVE you wrote them first. Here's how:

**Method 1: Poor man's copyright (free)**
- Email your lyrics to yourself. The email timestamp proves you had them on that date.
- Save the email. Don't delete it.
- This isn't as strong as registration but it's better than nothing.

**Method 2: Copyright registration ($65)**
- Go to copyright.gov → Register → Literary Work (for lyrics) or Sound Recording (for the full song)
- Upload your lyrics document or audio file
- Takes 2-6 months to process but your protection backdates to the filing date
- This gives you the legal standing to sue for statutory damages

**Method 3: Sozawen's Lyrics Editor**
- Write your lyrics in the Lyrics Editor tool
- Export as .txt — the file's creation date is your timestamp
- Save it somewhere safe (cloud backup, email to yourself)

**What copyright DOESN'T protect:**
- A chord progression (you can't copyright I-V-vi-IV)
- A song title (titles can't be copyrighted)
- A general idea or theme ("a song about heartbreak")
- A groove or rhythm
- What IS protected: your specific melody, your specific lyrics, your specific arrangement

**If someone steals your song:**
1. Document the infringement (screenshots, links)
2. File a DMCA takedown with the platform (Spotify, YouTube, etc.)
3. Contact a music attorney if the infringement is significant
4. Having a copyright registration makes this process much stronger

**Best practice:**
Every time you write a song, save the lyrics with a date. Keep a running document. Back it up. Your words are worth protecting — they're the most personal thing you'll ever create."""
    },
}


def search_knowledge(query):
    """Search the knowledge base. Returns matching articles."""
    query_lower = query.lower()
    results = []
    for key, article in KNOWLEDGE_BASE.items():
        score = 0
        if query_lower in article['title'].lower(): score += 10
        if query_lower in article['category'].lower(): score += 5
        if query_lower in article['content'].lower(): score += 1
        # Check for word matches
        for word in query_lower.split():
            if word in article['title'].lower(): score += 3
            if word in article['content'].lower(): score += 1
        if score > 0:
            results.append({**article, 'id': key, 'score': score})

    results.sort(key=lambda x: -x['score'])
    return results[:10]


def get_article(article_id):
    """Get a specific article by ID."""
    return KNOWLEDGE_BASE.get(article_id)


def get_categories():
    """Get all categories with their article counts."""
    cats = {}
    for key, article in KNOWLEDGE_BASE.items():
        cat = article['category']
        if cat not in cats: cats[cat] = []
        cats[cat].append({'id': key, 'title': article['title']})
    return cats
