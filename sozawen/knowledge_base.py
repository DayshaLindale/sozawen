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
        "content": """Every song you've ever heard — every melody, every guitar riff, every vocal line — is built out of the same small alphabet of sounds. Music theory calls them **notes**, and there are only twelve of them before they start over. That's the whole language. Learn the alphabet once, and you can read any page of it.

Here's the full list, in order from low to high: `C`, `C#`, `D`, `D#`, `E`, `F`, `F#`, `G`, `G#`, `A`, `A#`, `B` — and then it starts again at `C`, one octave higher. On a piano, that's one full trip from any key to the next key with the same name. On a guitar, that's twelve frets up the same string.

**Try this:** Hum the first two notes of "Happy Birthday." The jump from the first note to the second is called a **whole step** (two notes apart). Now hum the "mi-fa" part of "Do-Re-Mi" — that smaller, tighter jump is a **half step** (one note apart, also called a **semitone**). Every melody in every genre is stitched together from these two distances. That's it. That's the raw material.

**The three terms you'll see everywhere:**
- A **semitone** (or **half step**) is the smallest jump in Western music — `C` to `C#`, or `E` to `F`.
- A **whole step** is two semitones — `C` to `D`, or `G` to `A`.
- An **octave** is twelve semitones — the same note name, higher or lower. Your voice singing "Somewhere" at the start of *Over the Rainbow* jumps exactly one octave.

**Why are there no E# or B#?** This is the question everyone asks, and it throws people off for weeks if no one answers it. The twelve-note system isn't evenly spaced in our hearing — it grew out of physics and centuries of tuning compromise. Between `E` and `F`, and between `B` and `C`, the jump is already only a semitone. There's no black key between them on a piano because there's no room for one. So the natural notes `C D E F G A B` alternate between whole steps and half steps in a specific pattern — and that pattern is what makes the **major scale** sound the way it does. (See the `scales` article for why that matters.)

**Sharps and flats.** A sharp (`#`) raises a note by a semitone. A flat (`b`) lowers it by one. So `C#` and `Db` are literally the same pitch on a keyboard — they just get different names depending on musical context. Musicians call these **enharmonic equivalents**. When you're writing in a sharp key, you'll see `F#`. When you're in a flat key, the same pitch might be called `Gb`. Don't let it confuse you — it's the same sound.

**In Sozawen.** The Piano Roll shows every note in the 12-note system laid out vertically — white rows for naturals, darker rows for sharps/flats. Middle C (`C4`, MIDI note 60) is labeled. Hover any note to see its name, octave, and frequency in Hz. When you hit the Scale Reference, the notes that belong to your chosen key highlight green on both the Piano Roll and the Score editor, so you can see the alphabet of your song at a glance.

**Going deeper.** Every doubling of frequency is one octave. `A4` = 440 Hz, `A5` = 880 Hz, `A3` = 220 Hz. This is why octaves sound like "the same note" — the ear recognizes the 2:1 ratio. The twelve-note **equal temperament** system we use today divides that octave into twelve mathematically equal steps (each semitone is a factor of 2^(1/12) ≈ 1.0595 in frequency). Older music used **just intonation** and other tuning systems where intervals were built from simple ratios — purer-sounding but limited to one key at a time. Equal temperament is a compromise: slightly out of tune everywhere, but usable everywhere. That trade is why a modern piano can play in all 12 keys without retuning."""
    },

    "intervals": {
        "title": "Intervals",
        "category": "Music Theory",
        "content": """Intervals are just the distance between two notes. That's it. That's the whole concept. If you can tell that "Happy Birthday" starts with a small jump up and "Somewhere Over the Rainbow" starts with a big jump up, you already understand intervals — you just don't have names for them yet. This article gives you the names.

**Why bother naming them?** Because every emotion in music comes from intervals. A major third sounds happy. A minor third sounds sad. A tritone sounds unsettling. These aren't cultural — they're built into how the ear processes frequency ratios. Once you can hear and name intervals, you can write melodies on purpose instead of by accident, and you can hear a song once and know roughly how to play it.

**The unit is the semitone.** Count the half-steps between two notes and you have the interval. `C` to `D` is 2 semitones. `C` to `G` is 7. Here's the full map, with a famous tune for each so you can hear them in your head:

| Semitones | Name | Feel | Famous example (first two notes) |
|-----------|------|------|----------------------------------|
| 0 | Unison | Same note | any note doubled |
| 1 | Minor 2nd | Tense, creeping | *Jaws* theme |
| 2 | Major 2nd | Gentle step | *Happy Birthday* ("Hap-py") |
| 3 | Minor 3rd | Sad, wistful | *Greensleeves* |
| 4 | Major 3rd | Bright, sunny | *When the Saints Go Marching In* |
| 5 | Perfect 4th | Heroic, open | *Here Comes the Bride* |
| 6 | Tritone | Unstable, evil | *The Simpsons* theme ("The Simp-") |
| 7 | Perfect 5th | Strong, powerful | *Star Wars* main theme |
| 8 | Minor 6th | Bittersweet, longing | *Love Story* theme |
| 9 | Major 6th | Warm, hopeful | *My Bonnie Lies Over the Ocean* |
| 10 | Minor 7th | Bluesy, questioning | *Star Trek: TOS* theme |
| 11 | Major 7th | Dreamy, jazzy | *Take On Me* (the chorus leap) |
| 12 | Octave | Same note, higher | *Somewhere Over the Rainbow* ("Some-where") |

**Why do intervals have weird name pairs like "major" and "minor"?** Every interval size (2nd, 3rd, 6th, 7th) comes in a major and minor version — one semitone apart. A **major 3rd** is 4 semitones and sounds happy; a **minor 3rd** is 3 semitones and sounds sad. The 4th, 5th, and octave are called **perfect** — they're so stable they don't have a major/minor version. Mess with them and you get **augmented** (one higher) or **diminished** (one lower) instead.

**The tritone** deserves a special mention. It's the 6-semitone interval, right in the middle of the octave, and it sounds genuinely wrong to most ears. Medieval composers called it *diabolus in musica* — "the devil in music" — and church music actually banned it for centuries. Today it's the whole engine of jazz harmony and the reason dominant 7 chords pull so hard toward home.

**In Sozawen.** Select any two notes in the Piano Roll and the bottom strip shows the interval name and semitone count. The Chord Builder lists every chord as a stack of intervals, so you can see exactly what makes a `Cmaj7` different from a `C7` — it's just the top note moving by one semitone.

**Going deeper.** Intervals work in two directions. **Melodic intervals** are notes played one after the other (that's melody). **Harmonic intervals** are notes played at the same time (that's the foundation of every chord). Stack a root, a major 3rd, and a perfect 5th and you get a major chord — covered in the `chords` article. Intervals larger than an octave get special names too: a 9th is a 2nd plus an octave, an 11th is a 4th plus an octave, a 13th is a 6th plus an octave. Jazz is mostly arguments about which of those to stack on top of a 7th chord."""
    },

    "scales": {
        "title": "Scales",
        "category": "Music Theory",
        "content": """A **scale** is just a specific selection of notes — out of the twelve available — that have been chosen to sound good together. Pick a scale, stay inside it, and your melody will sound "in tune" with your chords automatically. Step outside it and you get tension, surprise, or a wrong note, depending on how careful you are. Scales are the rails the song rides on.

**The easiest way to understand this:** the white keys of a piano, played from `C` to the next `C`, give you the **C major scale**: `C D E F G A B C`. That's the "Do Re Mi Fa Sol La Ti Do" from *The Sound of Music*. Play only those notes over a C major chord progression and everything will sound fine. Congratulations — you just used a scale.

**The two scales that run 90% of Western music:**

**Major scale** — happy, resolved, triumphant. The pattern of steps is **W W H W W W H** (W = whole step, H = half step). Starting from `C`, that gives you `C D E F G A B`. Think Christmas carols, national anthems, most pop choruses. *Twinkle Twinkle Little Star* is pure major scale.

**Natural minor scale** — sad, moody, serious. The pattern is **W H W W H W W**. Starting from `A`, that gives you `A B C D E F G` — the same notes as C major, just starting in a different place. This is why A minor is called the **relative minor** of C major. Think *Stairway to Heaven*, *House of the Rising Sun*, most film scores for sad scenes.

**Here's the pattern trick:** you can build a major scale from any starting note by using **W W H W W W H**. Start on `G`, follow the pattern, and you'll need one sharp (`F#`) to make it work. Start on `F` and you'll need one flat (`Bb`). The `circle_of_fifths` article explains why keys accumulate sharps and flats in such a predictable order.

**Pentatonic scales** — five-note scales that have the "tense" notes removed. You literally cannot play a wrong note if you stay in them, which is why every beginner guitarist learns these first.
- **Major pentatonic** — degrees 1 2 3 5 6 of the major scale. In C: `C D E G A`. Bright and folky.
- **Minor pentatonic** — degrees 1 b3 4 5 b7. In A: `A C D E G`. The entire vocabulary of blues and rock guitar.

**Blues scale** — minor pentatonic with one extra note added, the **blue note** (`b5`). In A: `A C D Eb E G`. That added note is where the "cry" comes from.

**Modes** — what happens when you start a major scale from a different note and treat that note as home. The intervals shift, and the mood shifts with them. You get seven modes from the major scale:
- **Ionian** — the major scale itself. Happy, stable.
- **Dorian** — minor with a lifted 6th. Smoother than natural minor. Santana, jazz, sea shanties.
- **Phrygian** — minor with a lowered 2nd. Dark, Spanish, menacing. Flamenco, metal.
- **Lydian** — major with a raised 4th. Dreamy, floating, otherworldly. Film scores, dream sequences.
- **Mixolydian** — major with a lowered 7th. Bluesy, rock-and-roll. *Sweet Child o' Mine* solo, Celtic jigs.
- **Aeolian** — natural minor. Sad, grounded.
- **Locrian** — the weird one. Almost never used as a home base because it has no stable tonic chord.

**The key of a song** is just shorthand for "which scale is this song built from." When someone says "it's in G major," they mean the melody and chords all come from the G major scale. Knowing the key tells you which notes are safe to play.

**Common confusion: why do minor keys and major keys share notes?** Because the minor scale is just the major scale starting from a different point. C major and A minor use the exact same seven notes. What makes one *feel* major and the other *feel* minor is which note the song treats as home — the one it keeps returning to and ends on. Same ingredients, different center of gravity.

**In Sozawen.** The Scale Reference panel lights up the notes of your current key across the Piano Roll and Score editor — anything outside the scale shows in gray. The Chord Builder can be set to "in-key only," which filters suggestions so every chord it proposes fits the scale. And the Genre Presets pre-select a scale and mode appropriate to the style (blues → minor pentatonic, film score → Lydian or Dorian), so you can jump in without picking one yourself.

**Going deeper.** There are three minor scales, not one. **Natural minor** is the default. **Harmonic minor** raises the 7th to create a stronger pull back to the root — that Middle-Eastern-sounding interval between the 6th and raised 7th is its signature. **Melodic minor** raises both the 6th and 7th on the way up, then reverts to natural minor on the way down — it was designed to make singing melodies smoother. Once you're past those, there's a whole universe of synthetic and exotic scales: whole-tone, diminished, double-harmonic, Hungarian minor. Every one of them is just a different selection of notes from the twelve — a different set of rails."""
    },

    "chords": {
        "title": "Chords & Harmony",
        "category": "Music Theory",
        "content": """A **chord** is what happens when you play three or more notes at the same time and they sound like *one thing* instead of three separate things. When a guitarist strums once and you hear a single wash of sound with a clear mood — happy, sad, tense, resolved — that's a chord. Chords are the emotional backbone of a song. The melody sings over them; the rhythm pushes them; but the chords tell you how to *feel*.

**The smallest chord you'll use is a triad** — three notes, stacked in thirds. Take any note, skip a note, add one, skip a note, add one. On `C`: root `C`, skip `D`, add `E`, skip `F`, add `G`. That's a `C` major chord: `C E G`. Every triad you'll ever play is built this exact way — you just vary the *size* of the thirds you stack.

**The four basic triad types:**

- **Major** — root + major 3rd + perfect 5th. Happy, resolved. `C` = `C E G`.
- **Minor** — root + minor 3rd + perfect 5th. Sad, introspective. `Am` = `A C E`.
- **Diminished** — root + minor 3rd + diminished 5th. Tense, unstable, wants to move. `Bdim` = `B D F`.
- **Augmented** — root + major 3rd + augmented 5th. Strange, dreamlike, suspended in air. `Caug` = `C E G#`.

The difference between happy and sad is *one semitone*. Lower the 3rd of a major chord by a half step and you've got a minor chord. That's the entire difference between *Here Comes the Sun* and a funeral dirge. One note.

**7th chords** add a fourth note on top of the triad, a seventh above the root. This is where music starts to get richer and more grown-up.

- **Major 7th** (`Cmaj7`) = `C E G B`. Dreamy, lush, sophisticated. The sound of a jazz ballad or a bossa nova.
- **Minor 7th** (`Am7`) = `A C E G`. Smooth, soulful, mellow. The sound of every R&B verse ever written.
- **Dominant 7th** (`G7`) = `G B D F`. Bluesy, restless. This chord has the tritone baked into it (between `B` and `F`), which is why it *always* sounds like it wants to go somewhere — usually back to the root chord (`C` in this case).

That last point is the whole engine of Western harmony. A `G7` wants to resolve to `C`. The tension resolves. The ear relaxes. That's a **V-I cadence**, and it's the ending of about a billion songs.

**Diatonic chords** — the chords you get by stacking thirds on each note of a scale, using only notes from that scale. Every key has exactly seven of them, and they come in a predictable pattern:

In **C major**: `C` `Dm` `Em` `F` `G` `Am` `Bdim`
- Major, minor, minor, major, major, minor, diminished.

In **A minor**: `Am` `Bdim` `C` `Dm` `Em` `F` `G`
- Same chords, different starting point.

**Roman numerals** are the universal language of chord function — they describe a chord's role regardless of key. Capital = major, lowercase = minor, ° = diminished:

- **I** — home (tonic). Where the song lives.
- **ii** — a softer departure. Often leads to V.
- **iii** — moody middle ground.
- **IV** — uplift, openness. The "pre-chorus" chord.
- **V** — maximum tension, pointed at home. Wants to become I.
- **vi** — the emotional one. The relative minor. Where sad choruses live.
- **vii°** — rare, tense, mostly used as a passing chord.

Once you know these, you can read a progression like **I-V-vi-IV** and know it's the sound of half the pop songs of the last 30 years — *Let It Be*, *Someone Like You*, *No Woman No Cry*, and on and on. The actual letters change with the key; the Roman numerals don't.

**In Sozawen.** The Chord Builder lets you click any note as a root and instantly see every common chord you can build from it — triads, 7ths, extensions, slash chords. It shows the notes, the intervals, and plays the sound. Drop a chord onto the Piano Roll and it writes in every note at the right octave. The Score editor displays chord symbols above the staff automatically.

**Going deeper.** Beyond 7ths, chords can stack all the way to 13ths — a `Cmaj13` is `C E G B D F A`, which is basically the entire C major scale played at once. Jazz lives in these extensions. **Inversions** flip a chord so a different note is on the bottom — `C/E` means a C chord with E in the bass. **Suspended chords** (`sus2`, `sus4`) replace the 3rd with a 2nd or 4th, creating a floating, unresolved sound. **Slash chords** (`G/B`) put a specific bass note under a chord to smooth out the bassline between two other chords. All of these are built from the same core idea — stack intervals, pick which ones, decide what's on the bottom. Everything else is decoration."""
    },

    "circle_of_fifths": {
        "title": "Circle of Fifths",
        "category": "Music Theory",
        "content": """The **Circle of Fifths** is the single most useful diagram in all of music theory. It looks like a clock face with the twelve keys arranged around it, and once you understand what it's showing, you can see — at a glance — which keys are related, which chords belong together, how to modulate between keys smoothly, and why some chord progressions feel inevitable while others feel jarring.

**Here's what the circle actually is.** Start on `C`. Go up a perfect 5th (seven semitones) and you land on `G`. Go up another 5th and you land on `D`. Keep going — `A`, `E`, `B`, `F#`, `C#`, `G#`, `D#`, `A#`, `F`, back to `C`. You just visited all twelve notes in a specific order, and that order is the circle. It's not arbitrary; it's what happens when you apply the same interval (a 5th) over and over.

**Why does it matter?** Because keys that are neighbors on the circle share almost all their notes. `C` major and `G` major are right next to each other, and they differ by exactly one note — `F` in C major becomes `F#` in G major. Six of their seven notes are identical. That's why a song can slide from C to G and barely feel it. Keys that are *opposite* each other on the circle (`C` and `F#`, say) share almost nothing, and moving between them feels dramatic and far.

**The sharp-flat pattern is hiding in plain sight:**

- Going **clockwise** from `C`, each key adds one sharp. `C` has zero. `G` has one (`F#`). `D` has two (`F#`, `C#`). `A` has three. The new sharp is always the 7th degree of the new key.
- Going **counter-clockwise** from `C`, each key adds one flat. `F` has one (`Bb`). `Bb` has two (`Bb`, `Eb`). `Eb` has three. The new flat is always the 4th degree.

This is why some key signatures have a lot of sharps and others have a lot of flats — you're just seeing how far around the circle you've walked from `C`.

**The chord shortcut.** For any key on the circle, the three most important chords in that key — the **I, IV, and V** — are always the current position, one step counter-clockwise (the `IV`), and one step clockwise (the `V`). In C major, that's `F` (IV) `C` (I) `G` (V). In G major, it's `C` (IV) `G` (I) `D` (V). The circle is literally a map of chord relationships. This is why so many songs cycle through chords by moving around the circle — it's the path of least resistance for the ear.

**Relative majors and minors.** Every major key has a **relative minor** that shares all the same notes but treats a different note as home. On the circle, the relative minor of each major key sits inside that slot:

`C`/`Am`, `G`/`Em`, `D`/`Bm`, `A`/`F#m`, `E`/`C#m`, `B`/`G#m`, `F#`/`D#m`, `F`/`Dm`, `Bb`/`Gm`, `Eb`/`Cm`, `Ab`/`Fm`, `Db`/`Bbm`

Switching from a major key to its relative minor (or vice versa) is the smoothest possible key change — no notes change, just which one feels like home. That's how a song modulates from a sunny verse to a melancholy bridge without sounding like it jumped off a cliff.

**Modulation cheatsheet.**
- Move **one step clockwise** — the "key up a fifth" move. Brightens the mood, raises tension. Very common in hymns and second verses.
- Move **one step counter-clockwise** — the "key down a fifth" move. Relaxes, deepens.
- Move to the **relative minor/major** — emotional shift without disturbing the notes.
- Move **directly across the circle** — maximum contrast. Rare but dramatic. Key change as plot twist.

**Common confusion: are C# and Db really the same?** On a modern instrument, yes — they're the same pitch. But on the circle, they're listed separately because the key of `C#` major and the key of `Db` major have different key signatures (`C#` has seven sharps; `Db` has five flats). Same sound, different spelling. Composers pick whichever has fewer accidentals to read.

**In Sozawen.** The built-in Circle of Fifths panel is interactive — click any slot and Sozawen sets the project key to that, highlights the relative minor, and lists the diatonic chords for both. It also draws arrows showing the `I-IV-V` and the four closest related keys, so you can plan modulations visually. The Chord Builder uses circle-distance to suggest "close" or "distant" substitutions when you're stuck on a progression.

**Going deeper.** The circle is really a loop through the 12-tone chromatic scale traversed by the interval of a 5th — which, because 12 and 7 (semitones in a 5th) share no common factors, visits every note exactly once before returning home. This is why fifths dominate Western music: they're the strongest consonance after the octave, and they generate all twelve notes. The same logic produces the **Circle of Fourths** (going the other direction), which is the same circle read backwards — and which, not coincidentally, describes the root motion of most jazz `ii-V-I` progressions. Once you see the circle in a `ii-V-I`, you start seeing it everywhere. See the `chords` article for how these progressions are built, and the `scales` article for how keys are defined in the first place."""
    },

    "song_structure": {
        "title": "Song Structure",
        "category": "Music Theory",
        "content": """A **song structure** is just the architecture of a song — the map of when the verse happens, when the chorus hits, when the bridge shows up, and how the whole thing starts and ends. It's not a creative limitation; it's how listeners keep their bearings. When a song feels satisfying, you can almost always find a structure under it doing the quiet work. When a song feels like it's meandering or overstays its welcome, usually the structure is wrong.

**Think about it this way:** every good story has a setup, a middle, a turn, and a resolution. Songs are the same. The verse sets the scene. The chorus is the point. The bridge is the twist. The outro is the landing. Give the listener those signposts and they'll follow you anywhere. Leave them out and even a beautiful melody can feel formless.

**The most common structure — Verse/Chorus** (pop, rock, indie, country, most of what's on the radio):

`Intro -> Verse 1 -> Chorus -> Verse 2 -> Chorus -> Bridge -> Chorus -> Outro`

The verses carry the story and tend to stay lower-energy. The chorus is the emotional hook — louder, fuller, repeated word-for-word each time. The bridge breaks the pattern, offers a new angle, and sets up the final chorus to hit harder than the ones before it. This is the shape of *Someone Like You*, *Mr. Brightside*, *Shallow*, and thousands more.

**Pre-chorus addition** — many modern pop songs add a **pre-chorus** between verse and chorus: a short section that builds tension so the chorus feels like a release. Often the chords climb, the drums half-time, or the vocal opens up. *Livin' on a Prayer* is the textbook example — "whoa, we're halfway there" is the pre-chorus ramp into "livin' on a prayer!"

**AABA** (jazz standards, Broadway, older pop):

`A -> A -> B -> A`

Two verses of the main melody (A), then a contrasting bridge (B), then the main melody returns one more time. *Somewhere Over the Rainbow*, *Blue Moon*, and most Great American Songbook tunes use this. 32 bars total — 8 per section — which is why jazz musicians talk about "playing the form" in 32-bar cycles.

**Verse/Verse** (folk, ballads, storytelling):

`Verse 1 -> Verse 2 -> Verse 3 -> ...`

Same melody, different lyrics each time. The song is carried by the story, not a repeated hook. *The Times They Are A-Changin'*, *Tom Dooley*, most Irish and Appalachian ballads.

**Through-composed** — no repeating sections at all. Each part is new. Common in progressive rock, classical, film scores. *Bohemian Rhapsody* is partly through-composed, which is why it feels like five songs glued together.

**Typical section lengths:**

- **Intro** — 4 to 8 bars. Sets the key and the mood. Sometimes instrumental, sometimes a taste of the chorus.
- **Verse** — 8 to 16 bars. The story.
- **Pre-chorus** — 4 to 8 bars. The climb.
- **Chorus** — 8 to 16 bars. The payoff.
- **Bridge** — usually 8 bars. The detour.
- **Outro** — 4 to 8 bars. The landing, or a long fade.

These are starting points, not rules. A song can have a 4-bar verse and a 32-bar chorus if that's what the song wants.

**The secret most beginners miss: dynamics matter more than structure.** You can write a textbook verse-chorus song and have it feel dead if every section is the same energy. The verse should feel *smaller* than the chorus — fewer instruments, quieter, more intimate. The chorus should feel *wider* — more harmony, bigger drums, doubled vocals. The bridge should feel *different* — a key change, a drop, a sudden sparse moment. Listeners don't consciously notice these shifts, but they feel them. When a chorus "hits," what they're feeling is the contrast with the verse that came before.

**Common confusion: what's the difference between a pre-chorus and a bridge?** A pre-chorus happens *every time* before the chorus — it's part of the repeating pattern. A bridge happens *once*, usually in the last third of the song, and it introduces new material (new chords, new lyrics, sometimes a new key). Pre-chorus = ramp. Bridge = detour.

**In Sozawen.** The Arrangement view lets you label sections (Intro, Verse, Chorus, Bridge, etc.) as colored blocks, and the Structure Templates menu can scaffold any of the common forms above with empty sections ready for you to fill in. When you're writing, the Section Energy meter shows the relative density of each section — number of tracks active, dynamic level, harmonic fullness — so you can see at a glance whether your chorus is actually bigger than your verse.

**Going deeper.** Beyond the standard forms, there are **post-choruses** (a short tag after the chorus — the "oh-oh-oh" in a lot of 2010s pop), **drops** (the EDM version of a chorus, where the "hook" is instrumental), **breakdowns** (strip everything back, often right before the last chorus), and **codas** (extended outros that develop new material, borrowed from classical). The structure you pick shapes the listener's expectations; breaking it at the right moment is where the memorable songs live. See the `rhythm` article for how tempo and feel reinforce structural boundaries — a half-time feel in the bridge is one of the most reliable tricks in pop production."""
    },

    "rhythm": {
        "title": "Rhythm & Time",
        "category": "Music Theory",
        "content": """**Rhythm** is how music moves through time. Melody tells you *what* to play; rhythm tells you *when*. And "when" is doing more heavy lifting than people realize — you can take the exact same notes, re-time them, and end up with a lullaby, a march, or a dance floor banger. Rhythm is the difference between a song you tap your foot to and one that just sits there.

**Start with the pulse.** Every song has a **beat** — the steady, repeating pulse you'd clap along to. That's the tempo. Now count those beats in groups: "ONE two three four, ONE two three four." That grouping — where the ONE lands, and how many beats before it comes around again — is the **time signature**. Once you've got pulse and grouping, you've got the skeleton of rhythm. Everything else is decoration.

**Time signatures** look like a fraction: `4/4`, `3/4`, `6/8`. The top number is **how many beats per bar**. The bottom number is **which note value gets the beat** (4 = quarter note, 8 = eighth note). The common ones and how they feel:

- **`4/4`** — four beats per bar, quarter note gets the beat. The default for just about everything — pop, rock, hip-hop, EDM, country, metal. If a song isn't telling you otherwise, assume `4/4`.
- **`3/4`** — three beats per bar. Waltz time. *My Favorite Things*, *Piano Man*, *Manic Depression*. Feels like it's spinning or swaying.
- **`6/8`** — six eighth notes per bar, grouped as **two** beats of three. Compound feel — lilting, rolling, often used for ballads. *Nothing Else Matters*, *We Are the Champions* chorus, most Irish jigs.
- **`5/4`** — five beats per bar. Asymmetric, distinctive. *Take Five*, the *Mission: Impossible* theme.
- **`7/8`** — seven eighth notes per bar, usually grouped as 3+2+2 or 2+2+3. Lopsided, propulsive. Tool, Radiohead, King Crimson, a lot of Balkan folk music.

**BPM (beats per minute) is tempo.** It's just how fast the beats are coming. Rough genre ranges (these are starting points, not strict rules):

- **60-80 BPM** — slow ballad, downtempo, ambient
- **80-100 BPM** — hip-hop, R&B, trip-hop
- **100-120 BPM** — pop, indie rock, reggae
- **120-140 BPM** — dance, house, punk, most EDM
- **140-170 BPM** — drum and bass, fast metal, some techno
- **170-200 BPM** — thrash metal, speedcore, fast bluegrass

A song at 75 BPM doesn't automatically *feel* slow, though — this is where subdivision comes in. A ballad at 75 BPM that plays a ton of 16th notes on the hi-hat can feel just as busy as a rock song at 140. **The surface rhythm** — how many notes are actually hitting per second — often matters more than the underlying BPM.

**Straight vs. swing.** In **straight** time, each beat is divided evenly — if you subdivide into eighth notes, every eighth is exactly half a beat. In **swing** (or **shuffle**), the first eighth of each pair is held longer and the second is shorter, usually in roughly a 2:1 ratio. That lopsided bounce is the entire reason jazz feels like jazz, blues feels like blues, and hip-hop from the early 90s feels different from hip-hop from the 2010s. Swing takes the same notes and makes them *groove*.

**Syncopation** is when accents land on the "wrong" beats — the off-beats, the upbeats, the spaces between the main pulses. If `4/4` counts as "1 and 2 and 3 and 4 and," straight rock puts the weight on 1 and 3, or 2 and 4. Syncopation puts the weight on the "ands." Every funk song, every reggae song, every rhythmically interesting pop song lives in syncopation. Without it, music feels stiff. Too much of it and you lose the pulse entirely. The art is finding the balance.

**Common confusion: what makes 6/8 different from 3/4?** Both have six eighth notes per bar, so on paper they look similar. The difference is where the accents fall. `3/4` groups as **three** beats of two (ONE-two, ONE-two, ONE-two — a waltz). `6/8` groups as **two** beats of three (ONE-two-three, ONE-two-three — a lilt). Same notes, completely different feel. Count to yourself out loud and you'll hear the difference immediately.

**Another confusion: half-time and double-time.** These aren't new time signatures — they're perceived shifts. **Half-time** is when the snare moves from beat 2 and 4 to just beat 3, making the groove feel like it dropped to half speed without changing the BPM. It's the "big" feeling in a bridge or chorus drop. **Double-time** is the opposite — the drums double up, making the song feel twice as fast. Drum and bass is essentially rock music drummed in double-time.

**In Sozawen.** The Tempo and Time Signature are set at the top of every project and drive the grid in the Piano Roll, the Score editor, and the Drum Grid. You can change either mid-project — the Tempo Track lets you automate BPM changes across the song (slow intros, half-time bridges, accelerandos). The Swing slider in each MIDI clip lets you slide between perfectly straight and full shuffle. And the Groove Templates library has swing and humanization profiles extracted from famous grooves (Motown, Dilla, New Orleans second-line) that you can drag onto any clip to borrow its feel.

**Going deeper.** Rhythm can be polyrhythmic — two different pulses running at once, like `3` against `4` (the backbone of a lot of African music and modern prog). **Polymeter** is when two instruments play in different time signatures simultaneously but share the same pulse. **Odd groupings** within a bar — a `4/4` where the hi-hat plays groups of 3 over the steady quarter-note kick — create rhythmic tension that resolves every few bars when the patterns line up again. Once pulse and grouping become second nature, time signature stops being a constraint and starts being a tool. See the `song_structure` article for how rhythmic shifts (half-time bridges, double-time outros) reinforce a song's architecture."""
    },

    # ═══════════════════════════════════════════════════════════════
    # RECORDING
    # ═══════════════════════════════════════════════════════════════

    "signal_chain": {
        "title": "The Signal Chain",
        "category": "Recording",
        "content": """Your signal chain is every piece of gear sound passes through between the source and the recording. Get it wrong and your recording is broken before you even hit record. Get it right once and you stop thinking about it forever.

**The concrete version:** You plug a mic into an audio interface. The interface connects to your computer by USB. Sozawen sees it in the **Input Device** panel. You pick that input on a track, arm the track, hit **Record**. That's a signal chain — five stages, one path, sound moving left to right.

## The Five Stages

**Source -> Microphone -> Cable -> Interface (preamp + converter) -> Sozawen**

1. **Source** — the actual performance. A singer, an amp, an acoustic guitar in a room. This is the one link no plugin can fix. A great mic on a bad take still sounds like a bad take. Spend time here first.
2. **Microphone** — converts air pressure into a tiny electrical signal. Three common types:
   - **Dynamic** (SM57, SM58, SM7B) — tough, handles loud sources, rejects room noise. Good for guitar amps, snare, live vocals, untreated rooms.
   - **Condenser** (AT2020, Rode NT1, U87) — detailed and sensitive, needs `+48V` phantom power. Good for studio vocals, acoustic guitar, drum overheads.
   - **Ribbon** (Royer 121) — warm and smooth, vintage character. **Never send phantom power to a ribbon** unless the manual explicitly says it's safe — you can destroy the element.
3. **Cable** — XLR for mics, 1/4" TS for instruments, 1/4" TRS for balanced line-level. A cheap cable with a bad connection will ruin a `$2000` mic. Wiggle-test your cables before a session.
4. **Interface** — your preamp lives here (it boosts the mic's whisper-quiet signal up to line level), and so does the **A/D converter** (analog to digital). This is where you choose sample rate (`44.1 kHz` or `48 kHz` for most work) and bit depth (`24-bit`, always).
5. **Sozawen** — the track receives that digital audio. You select the input channel from the track's input dropdown, arm the track, and the level meter lights up with the signal.

## How It Shows Up in Sozawen

Open the **Input Device** panel and pick your interface. Each track has a per-track **input channel selector** — point track 1 at input 1, track 2 at input 2, and so on. Arm the track and watch the track's level meter. If the meter is dead, your chain is broken somewhere. Work backward: cable in? Phantom power on (for condensers)? Correct input channel selected? Interface showing up in Sozawen's device list?

The **input monitoring** toggle lets you hear yourself through your speakers/headphones while recording. Turn it on for vocals and re-amped guitar. Turn it off (and monitor through the interface's direct monitor instead) if you're hearing annoying latency.

## Common Beginner Mistakes

- **Plugged into line input instead of mic input.** Mic-level is tiny; line-level is ~1000x bigger. Wrong jack = no signal or a weak, crunchy one.
- **Forgot phantom power on a condenser.** No signal at all, or barely anything. Flip `+48V` on.
- **Left phantom power ON when plugging in a ribbon.** Rest in peace, ribbon.
- **Monitoring through speakers with an open mic.** Feedback loop. Use headphones when tracking.
- **Blaming the DAW for a silent track.** It's almost never Sozawen. It's the chain upstream.

## Going Deeper

Every stage adds a little noise and a little color. The pros of a nice preamp, a good mic, and a well-treated room are cumulative — each stage contributes. But the single biggest improvement for a beginner is almost always the **source** and the **room**, not the gear. A `$100` mic in a good-sounding room beats a `$2000` mic in a bathroom every time.

See also: `audio_interfaces`, `microphone_guide`, `gain_staging`, `mic_placement`."""
    },

    "mic_placement": {
        "title": "Microphone Placement",
        "category": "Recording",
        "content": """Where you put the mic matters more than which mic you buy. A `$100` SM57 placed well beats a `$3000` condenser placed badly — every single time. Moving a mic two inches can change the sound more than any EQ plugin you'll ever use. Learn this skill and your recordings will jump a level overnight.

**The concrete version:** You're recording an acoustic guitar. You park the mic right in front of the sound hole because that's where the sound "comes from," right? You hit record. Playback is a boomy, bass-heavy mess. You move the mic to point at the 12th fret instead, eight inches away. Playback is suddenly balanced, detailed, real. Same guitar, same mic, same room, same performance. That's mic placement.

## Starting Points (Not Rules)

**Vocals** — `6 to 10 inches` from the mouth. Pop filter halfway between singer and mic. Aim slightly off-axis (mic pointed at the chin or the top of the nose rather than straight at the lips) to tame plosives and sibilance. Mic height at mouth level or slightly above, tilted down.

**Acoustic guitar** — Aim at the **12th fret**, `6 to 12 inches` away. Do **not** mic the sound hole — it's all low-end boom. Want more body? Angle the mic slightly toward the bridge. Want more attack and pick detail? Move it toward the headstock.

**Electric guitar amp** — SM57, `1 to 3 inches` from the grille cloth, pointed at the speaker cone. **On-axis** (aimed at the center of the cone) = brighter, more presence. **Off-axis** (aimed at the edge) = warmer, darker. Split the difference for most rock tones.

**Drum overheads** — Matched pair of condensers, `3 to 4 feet` above the kit. Equidistant from the snare to keep the snare centered in the stereo image. See `drum_recording` for the full setup.

**Bass amp** — Large dynamic like a RE20 close to the speaker, plus a DI (direct) signal into the interface for the clean low end. Blend both in the mix.

## Proximity Effect

Directional mics (cardioid, most of what you own) boost low frequencies as you get closer to the source. Move a vocal mic from `12 inches` to `3 inches` away and the voice gets noticeably bassier and more intimate. Radio DJs and rap vocals exploit this. For balanced tone, back off. For warmth and size, get close — but manage the plosives.

## Multiple Mics and the 3:1 Rule

If you use two mics on one source (snare top + bottom, guitar amp + room), they can cancel each other in the frequencies where their distances differ by half a wavelength. The result: thin, hollow, weird-sounding playback.

**The 3:1 rule:** the distance between two mics should be at least **three times** the distance from each mic to its source. Mic A is `6 inches` from the snare? Mic B should be at least `18 inches` from Mic A. This minimizes phase cancellation between them.

Always check phase when using multiple mics. In Sozawen, you can flip a track's polarity — if combining two mics sounds thinner than either alone, flip one and listen again. Pick whichever version sounds fuller.

## Room Matters

**Closer to source = more direct sound, less room.** **Further = more room reflections mixed in.** In an untreated bedroom, get close and keep it tight. In a great-sounding room, back off and let the space become part of the recording. Blankets, rugs, and bookcases kill reflections. Bathrooms are reverb chambers — sometimes useful, usually not.

## Common Beginner Mistakes

- **Miking the sound hole of an acoustic guitar.** All boom, no definition.
- **Mic pointed straight at the singer's mouth.** Maximum plosives, maximum sibilance.
- **Two mics too close together.** Phase cancellation eats the tone.
- **Not moving the mic.** Place, record a test, listen, move, repeat. Two minutes of experimentation beats two hours of EQ.

## Going Deeper

Every mic has a **polar pattern** (the shape of what it picks up). Cardioid rejects sound from the rear; figure-8 picks up front and back equally; omni picks up everything. Use a figure-8 when you want to reject sound from the sides (a noisy drummer next to a vocalist). Use omni in a great room when you want the space in the recording.

See also: `microphone_guide`, `vocal_recording`, `drum_recording`, `signal_chain`."""
    },

    "gain_staging": {
        "title": "Gain Staging",
        "category": "Recording",
        "content": """Gain staging is the boring skill that separates recordings that sound professional from recordings that sound amateur. It's just setting the right level at every stage — mic preamp, track, bus, master. No single stage clips, no single stage is buried in the noise floor. Get this right and your mixes will sound cleaner without you touching an EQ.

**The concrete version:** You're tracking a vocal. You plug in the mic, turn up the interface preamp knob until the singer's loudest note peaks around `-12 dBFS` on Sozawen's input meter. Not the top. Not near the top. Well below the top. You hit record. That's gain staging.

## The Most Common Mistake

The most common gain-staging mistake is cranking the input knob so the meter slams the top of the scale — thinking louder equals better. Here's why that's wrong:

- **Digital audio has a ceiling at `0 dBFS`.** Go over it and the waveform clips. Clipping in digital is ugly, crunchy distortion that you cannot remove later. It's permanent damage.
- **24-bit audio has a noise floor around `-144 dBFS`.** That's so quiet you will never hear it. Recording a peak at `-12 dBFS` still gives you roughly 132 dB of usable range above the noise. You do not need to "use all the meter." That thinking is left over from tape and 16-bit days.
- **Headroom is free. Distortion is permanent.** Write that on a sticky note.

## Target Levels

| Stage | Target peaks | Why |
|-------|-------------|-----|
| Interface preamp (tracking) | `-18 to -12 dBFS` | Safe headroom for surprise louds |
| Vocal peaks (tracking) | `-12 to -6 dBFS` | Singers are unpredictable |
| Loud sources (drums, amps) | `-18 to -10 dBFS` | Transients spike higher than you think |
| Track fader (mixing) | Start at `0 dB` (unity) | Fader moves balance, gain sets base level |
| Mix bus before mastering | `-6 to -3 dBFS` peaks | Leaves room for limiter/final stage |
| Master bus true-peak | Below `-1 dBTP` | Prevents inter-sample clipping on streaming |

`-18 dBFS` is a rough target for clean headroom because it roughly lines up with `0 VU` on analog gear — where most analog processors were designed to sound their best. Plugins modeled after that gear behave the same way. Feed them signal that's too hot and they overdrive in ways the designers never intended.

## How It Shows Up in Sozawen

Watch the **input level meter** on each armed track while tracking. Sozawen shows a peak indicator — if it turns red, you clipped. Back off the interface's input gain knob (not a fader inside the DAW — the physical knob on the interface). Ask the singer for their loudest note and set the level on that, not on their speaking voice.

While mixing, check the per-track meters with everything playing. If individual track peaks are hitting `0 dBFS` and the master is clipping, pull those tracks down. **If everything is loud, nothing is loud** — the mix has no contrast and no impact.

## The Golden Rule

If something isn't loud enough in the mix, first try turning everything else down. The master has a fixed ceiling; the only way to make something stand out is contrast. Beginners push everything up and run out of headroom. Pros pull things down and keep headroom for the elements that matter.

## Going Deeper

Once you're comfortable with tracking levels, start thinking about gain staging **inside** plugin chains. Many compressors, saturators, and emulations have a "sweet spot" around `-18 dBFS` input. A trim plugin at the top of the chain that drops hot tracks down to that range will make every plugin downstream sound like it's working properly, not being overdriven.

See also: `signal_chain`, `audio_interfaces`, `compression_guide`, `eq_guide`."""
    },

    # ═══════════════════════════════════════════════════════════════
    # MIXING
    # ═══════════════════════════════════════════════════════════════

    "eq_guide": {
        "title": "EQ Strategy",
        "category": "Mixing",
        "content": """EQ is how you carve space in a mix. Every instrument wants to live in the same frequency range — vocals, guitars, piano, synths, they all crowd the middle. EQ is how you give each one its own seat at the table. When you hear a mix where you can pick out every part clearly, that's EQ doing its job. When you hear a mix that's muddy, honky, or harsh — that's EQ *not* doing its job.

**Start with one move you can hear.** Pull up a vocal that sounds muddy. Open Sozawen's EQ panel, grab a **peaking** band, sweep it to around `300 Hz`, and cut about `-4 dB` with a moderate Q. Listen. The clarity comes back. You didn't boost anything — you just removed what was in the way. That's the whole job, most of the time.

**Why `300 Hz` is the usual suspect:** the low-mids are where body lives, but also where every instrument piles on top of every other instrument. Cutting a little mud from the guitar, the keys, and the pad (each in a slightly different spot) opens up the whole mix.

**How EQ shows up in Sozawen**

The EQ panel has five band types, and each has a job:

- **Hi-pass (HPF)** — removes everything below a chosen frequency. Use it on almost every track except kick and bass. Set around `80-100 Hz` on vocals, `120 Hz` on guitars, `200 Hz` on hi-hats and overheads. You can't hear the rumble it removes, but your headroom will thank you.
- **Low-shelf** — boost or cut everything below a point. Gentle `+2 dB` at `100 Hz` adds warmth to a thin acoustic guitar. Gentle cut tames a boomy room.
- **Peaking** — a bell curve at any frequency. Your main surgical tool. Narrow Q for cuts, wide Q for boosts.
- **High-shelf** — boost or cut everything above a point. `+2 dB` at `10 kHz` adds "air" to vocals. Cut to tame harshness.
- **Low-pass (LPF)** — removes everything above a point. Useful on background elements to push them behind the lead.

If you need more than four or five bands, reach for the **Multi-band EQ** — it gives you up to eight bands with spectrum visualization so you can see what you're cutting.

**The frequency map (memorize this)**

- `20-80 Hz` — sub-bass. Kick thump, bass fundamental. Too much = muddy, speaker-flapping.
- `80-250 Hz` — warmth, body. Where chests and bodies live. Too much = boomy.
- `250-500 Hz` — low-mids. Boxiness, mud. Usually a **cut** zone.
- `500 Hz-2 kHz` — midrange. Body of most instruments. `1 kHz` gets nasal fast.
- `2-4 kHz` — presence. Vocal intelligibility, guitar bite. Harsh if overdone.
- `4-8 kHz` — clarity, sibilance. "S" and "T" sounds.
- `8-20 kHz` — air, sparkle. Cymbals, breath, shimmer.

See `frequency_chart` for instrument-by-instrument placement.

**The five rules that separate amateur from pro mixes**

1. **Cut before you boost.** If the vocal is muddy, cut the mud. Don't boost `5 kHz` to compensate — that just makes it muddy *and* harsh.
2. **Boost wide, cut narrow.** Wide Q boosts (Q of 0.7-1.0) sound musical. Narrow Q cuts (Q of 4-8) are surgical and don't color the rest.
3. **HPF almost everything.** The stuff below `80 Hz` on a guitar isn't doing anything but stealing headroom from the kick and bass.
4. **Never EQ in solo.** A track that sounds perfect alone might disappear in the mix, or stick out like a sore thumb. EQ in context.
5. **If two tracks fight, one gives way.** Don't boost both — pick a winner. Vocal needs `3 kHz`? Cut `3 kHz` on the guitar with a gentle dip.

**Advanced notes**

- **Dynamic EQ** acts only when a frequency gets loud. Great for de-essing vocals without dulling them, or taming a resonant note on a bass that only rings out on certain pitches.
- **Linear-phase EQ** preserves transient timing — useful on drum bus and mastering. Costs more CPU and adds latency. Not needed on most tracks.
- Use the **Spectrum Analyzer** to confirm what your ears suspect. It's a check, not a replacement for listening.

See also: `compression_guide`, `frequency_chart`, `mixing_order`, `common_mistakes`, `gain_staging`."""
    },

    "compression_guide": {
        "title": "Compression Guide",
        "category": "Mixing",
        "content": """Compression is a volume knob that moves by itself. When the signal gets too loud, it turns down. When the signal gets quiet, it leaves it alone. The result: quiet parts come forward, loud parts sit back, and the whole track feels steadier and more *present* — like it's sitting right in front of you instead of drifting in and out.

**Hear it first.** Put a vocal on a track in Sozawen. Listen to the verse where they whisper, then the chorus where they belt. The whisper is buried, the belt is slapping your face. Now add the **Compressor**: threshold `-18 dB`, ratio `3:1`, attack `10 ms`, release `80 ms`, makeup gain `+4 dB`. Play it back. The whisper is now audible, the belt isn't shredding your ears, and the whole vocal feels *closer*. That's what compression does.

**The five controls, in plain English**

- **Threshold** — the volume at which the compressor starts working. Signal above threshold gets squeezed; below, it passes through untouched. Lower threshold = more compression.
- **Ratio** — how hard it squeezes. `2:1` means for every 2 dB the signal goes over threshold, only 1 dB comes out. `4:1` is firmer. `10:1` and above is limiting.
- **Attack** — how fast the compressor clamps down after the signal crosses threshold. Fast attack (`1-5 ms`) catches transients and smooths peaks. Slow attack (`20-50 ms`) lets the initial snap through for punch.
- **Release** — how fast it lets go. Fast release (`30-50 ms`) feels lively, can pump on sustained sounds. Slow release (`200+ ms`) feels smooth and glued.
- **Makeup gain** — compression turns things down, so you turn them back up. Match the output level to the input level, then decide if the track needs to sit louder or quieter in the mix.

**Starting points by source**

| Source | Threshold | Ratio | Attack | Release |
|--------|-----------|-------|--------|---------|
| Vocals | `-20` to `-15 dB` | `2:1` to `4:1` | `5-15 ms` | `50-100 ms` |
| Drums (punch) | `-15` to `-10 dB` | `4:1` to `8:1` | `20-40 ms` (slow = punch) | `50-100 ms` |
| Bass | `-20` to `-15 dB` | `3:1` to `6:1` | `5-10 ms` | `50-80 ms` |
| Acoustic guitar | `-18` to `-12 dB` | `2:1` to `3:1` | `10-20 ms` | `80-150 ms` |
| Mix bus (glue) | `-3` to `-6 dB` | `1.5:1` to `2:1` | `10-30 ms` | auto or `100-300 ms` |

Aim for **2-6 dB of gain reduction** on individual tracks, and **1-2 dB** on the mix bus. If the meter is slamming down `10+ dB`, back off — you're crushing the life out of it.

**The attack trick (this is the one that clicks)**

Slow attack = more punch. It sounds backwards, but it's true. When attack is slow, the initial transient (the drum stick hitting, the consonant of a word) passes through untouched. Then compression clamps down on the sustain. The ear hears the transient as *extra* loud relative to the tamed body — and "extra loud transients" is exactly what "punchy" means.

Fast attack = smoother, more controlled, less snap. Great for taming harsh vocals or stray peaks. Bad for making drums feel big.

**How compression shows up in Sozawen**

- **Compressor** — the standard plugin. Threshold, ratio, attack, release, makeup, plus a gain-reduction meter so you can *see* it working.
- **Multi-band Compressor** — splits the signal into frequency bands and compresses each separately. Perfect for a vocal that only gets harsh on high notes, or a bass that booms only on low ones. Compress what needs it, leave the rest alone.
- **Parallel Compression** — mix the crushed signal back under the dry original. You get the density and power of heavy compression *plus* the dynamics of the raw track. Try it on drum bus with ratio `10:1`, threshold low enough for `8-10 dB` of reduction, then blend in to taste. Also called "New York compression."

**Beginner mistakes**

- **Over-compressing.** If you can *hear* the pumping, you've gone too far. Back off until it's subtle — you should feel the consistency, not notice the effect.
- **Not matching output gain.** Louder always sounds better to untrained ears. If you don't match levels before and after, you can't tell if compression actually helped.
- **Compressing before fixing the performance.** A compressor can't fix a bad take. Edit the volume peaks manually first (clip gain), then compress.
- **Reaching for reverb before compression.** Compression makes space; reverb fills it. In that order.

See also: `eq_guide`, `reverb_guide`, `mixing_order`, `gain_staging`, `common_mistakes`."""
    },

    "reverb_guide": {
        "title": "Reverb & Space",
        "category": "Mixing",
        "content": """Reverb is a time machine. It puts a sound in a room that doesn't exist. A dry vocal sounds like someone whispered into a microphone in a closet. Add the right reverb and suddenly that same vocal is standing in a cathedral, or a small club, or a bedroom at 2 AM. Reverb is how you tell the listener *where* they are.

**One move, right now.** Load a dry vocal in Sozawen. Open the **Reverb** plugin. Pick a medium **Room**, set decay to `1.2 seconds`, pre-delay to `30 ms`, wet/dry to `18%`. Play it. The voice is no longer glued to the speaker — it's sitting slightly behind it, in a real-feeling space. That's it. That's reverb. Everything else is variations on that idea.

**The five reverb types, and when to use each**

- **Room** — small, tight, natural. `0.3-1.0 s` decay. Think: a living room, a small studio. Default choice for drums, electric guitars, and anything that should feel *close*.
- **Hall** — big, lush, long. `1.8-4.0 s` decay. Think: symphony hall, cathedral. Ballads, strings, cinematic vocals. Use pre-delay to keep it from swallowing the dry signal.
- **Plate** — metal-plate reverb. Smooth, dense, bright. Classic vocal sheen. `1.2-2.5 s`. The sound of almost every famous rock and pop vocal from the 60s-90s.
- **Chamber** — warm, mid-sized. All-purpose. Between room and hall. Good when you're not sure what you want.
- **Spring** — bouncy, twangy, vintage. Surf rock guitar, dub, lo-fi. Character more than realism.

**The parameters that matter**

- **Pre-delay** — the gap between the dry sound and the start of the reverb. This is the single most important control for clarity. `20-60 ms` on vocals gives the word time to be heard before the tail blurs in. Without pre-delay, reverb smears everything into mush.
- **Decay (RT60)** — how long the tail lasts. Short decays make the space feel small and intimate. Long decays feel grand but eat clarity. Match decay to tempo — on a `120 BPM` song, a decay around `1.5 s` aligns with a half-note and feels musical.
- **Damping (or HF decay)** — how fast the high frequencies die off in the tail. High damping = warmer, carpeted-room feel. Low damping = brighter, tile-bathroom feel. For most vocals, roll off the highs in the tail so it doesn't get hissy.
- **Wet/dry** — how much reverb vs. original. `10-25%` for lead vocals, `15-30%` for backing vocals, `5-15%` for drums, `20-40%` for pads. Less is almost always more.

**The send trick (non-negotiable, learn this)**

Don't put reverb directly on each track. Instead, create a **bus track** in Sozawen with one reverb plugin on it, then **send** audio from multiple tracks into that bus. Why:

1. **Cohesion.** Multiple instruments share the same space. The mix feels like one room instead of ten.
2. **Control.** One knob (the bus fader) adjusts the whole reverb level at once.
3. **CPU.** One reverb plugin instead of ten.

You can still have a second reverb bus with different settings (short room for drums, long hall for vocals), but even two well-chosen sends beat ten individual plugins.

**Tricks that separate pros from beginners**

- **Dry in the center, wet on the sides.** Keep the dry signal mono and centered. Pan the reverb returns hard left/right. Creates width without losing focus. See `panning_guide` for more on this.
- **EQ the reverb.** Put an EQ *after* the reverb on the bus. High-pass at `200-300 Hz` (no low-end mud in the tail). Sometimes low-pass at `8 kHz` (no hissy tail). The reverb stays big without fogging the mix.
- **Duck the reverb under the vocal.** Use a compressor on the reverb bus side-chained to the dry vocal. When the vocal sings, the reverb ducks. When the vocal stops, the reverb blooms. You get clarity *and* space.
- **Pre-delay sync.** Set pre-delay to match an eighth or sixteenth note at your tempo (at `120 BPM`, a sixteenth is `125 ms`). Rhythmic, not smeary.

**Beginner mistakes**

- **Too much reverb.** The #1 amateur giveaway. If you can clearly hear the reverb on a mix, it's probably too much. Pull it back 30%.
- **Reverb on everything.** The kick drum does not need reverb. The bass does not need reverb. Those tracks are your foundation — keep them dry and tight.
- **Reverb before compression.** Compression should come first in the chain. Otherwise you're compressing the tail along with the source, which makes the space pump unnaturally.
- **Using reverb to hide problems.** If the vocal is out of tune or the take is bad, reverb won't save it. Fix the source.

See also: `eq_guide`, `compression_guide`, `panning_guide`, `signal_chain`, `mixing_order`."""
    },

    "panning_guide": {
        "title": "Panning & Stereo Image",
        "category": "Mixing",
        "content": """Panning is where things *are*. Close your eyes in a good mix and you can point to each instrument — the hi-hat is up and to the right, the rhythm guitar is over there on the left, the vocal is dead center with their mouth right in front of you. That spatial picture is panning. Done well, the mix feels three-dimensional. Done badly, everything piles up in the middle and your ears get tired in thirty seconds.

**One move, right now.** You've got a rock mix. Kick, snare, bass, vocal are all centered (good). Now grab the rhythm guitar and pan it `40%` left. Grab the keys and pan them `35%` right. Grab the hi-hat and nudge it `20%` right (to match where it would be on a drum kit). Hit play. The mix just *breathed*. Suddenly there's room between the instruments. Nothing got EQ'd, nothing got compressed — you just gave things places to sit.

**The standard layout (memorize this)**

- **Center** (12 o'clock): kick, snare, bass, lead vocal. These are the **anchor** — the spine of the mix. Everything else hangs off them.
- **Slight off-center** (`20-40%` L/R): rhythm guitars, keys, backing vocals, secondary percussion. These fill the near-field.
- **Wide** (`60-100%` L/R): doubled guitars (one hard left, its double hard right), stereo pads, room mics, reverb returns, shaker, tambourine.
- **Moving/automated:** background elements that sweep, whooshes, arpeggios. Great for transitions.

**The LCR approach (pro shortcut)**

Some engineers only use three pan positions: **Left**, **Center**, **Right**. Nothing in between. It's a discipline that forces decisions — every sound picks a lane. Mixes made this way feel clean and bold because nothing is wishy-washy at `18%` left.

Try it on a busy mix that feels cluttered. Push everything to hard L, hard R, or dead center. You'll be shocked how much clarity you get.

**How panning shows up in Sozawen**

- Every track has a **pan knob** in the mixer strip. Drag left or right, or type an exact value.
- **Stereo Width** plugin — adjust how wide a stereo source is without changing its center. Great for making a doubled guitar feel huge, or pulling in an overly-wide synth that's causing phase problems.
- **Mono button** on the master bus — collapse the entire mix to mono instantly. Use it constantly (see below).

**The four rules**

1. **Low frequencies stay center.** Anything below `150 Hz` should be mono. Bass and kick panned off-center cause phase problems on mono systems (phones, Bluetooth speakers, club PAs summed to mono). Use the Stereo Width plugin with a "mono below `120 Hz`" setting if your synth or doubled bass is drifting.
2. **Balance the sides.** If the rhythm guitar is `40%` left, put something of similar energy `40%` right — keys, a double, a shaker, anything. Lopsided mixes feel *wrong* even when you can't say why.
3. **Pan where the sound would actually be.** Hi-hat on a drum kit is to the drummer's right, so pan it right (or left, if you want the audience's perspective — pick one convention and stick to it across the whole mix).
4. **Check in mono.** Hit the mono button. If something *disappears* when you collapse to mono, you have a phase problem — usually a stereo plugin or doubled track with inverted polarity. Fix it now, before it ships to a phone speaker.

**Width tricks**

- **Haas effect.** Duplicate a mono track, pan the copy hard opposite, delay it `10-25 ms`. Your ear hears it as wide stereo. Watch mono compatibility — too much delay and it phases out.
- **Pan automation.** A clean guitar arpeggio that slowly pans from `30%` left to `30%` right over eight bars adds motion without cluttering the mix.
- **Double-tracking.** Record two takes of the same guitar part, pan them hard L/R. Huge, wide, and rock-solid in mono because the performances are *different* (not phase-correlated).
- **Narrow the chorus, widen the verse.** Or vice versa. Changing stereo width between sections makes the arrangement feel bigger at the payoff.

**Beginner mistakes**

- **Everything hard-panned.** Sounds impressive for ten seconds, then exhausting. You need a center.
- **Nothing panned.** Everything up the middle = a wall of mono mud. Use the stereo field.
- **Panned bass.** Kills mono compatibility. Keep bass centered, always.
- **Ignoring mono check.** If half your listeners hear the mix on a single speaker and something goes missing, that's on you.

See also: `eq_guide`, `reverb_guide`, `mixing_order`, `common_mistakes`, `signal_chain`."""
    },

    # ═══════════════════════════════════════════════════════════════
    # MASTERING
    # ═══════════════════════════════════════════════════════════════

    "mastering_basics": {
        "title": "What Is Mastering?",
        "category": "Mastering",
        "content": """Mastering sounds like dark magic. It's not. Mastering is the final polish — the step that takes a finished mix and prepares it for everywhere it's going to be heard. Phone speakers. Car stereos. Club PAs. Earbuds on a bus. A laptop in a coffee shop. Your job in mastering is not to make your song better. Your job is to make your song translate.

**The one-sentence version:** Mixing is about balancing the parts inside your song. Mastering is about making the whole song sit correctly in the world.

**What mastering actually does**

1. **Gentle overall EQ** — small tonal tilts across the whole mix (think `+0.5 dB` at 10 kHz for air, `-1 dB` at 250 Hz if it's muddy). Never surgical. If you need surgical EQ, you need to go back to the mix.
2. **Glue compression** — `1-2 dB` of gain reduction with a slow attack and auto-release. Just enough to make the song feel like one object, not a stack of tracks.
3. **Stereo shaping** — widen the highs, keep the bass mono below `120 Hz`. Optional.
4. **Loudness** — hit the target LUFS for your platform (see `loudness_standards`).
5. **Format conversion** — correct sample rate, bit depth, and dithering for delivery (see `export_formats`).

**The honest truth about mastering**

Louder is not mastered. Many beginners slap a limiter on the master bus, crush the song to `-6 LUFS`, and call it done. That is not mastering. That is destroying your dynamics and hoping nobody notices. Spotify will turn it down anyway. It will sound SMALLER than a properly mastered `-14 LUFS` track. Every time.

Mastering also cannot fix a bad mix. If your vocal is buried, go back to the mix. If your kick and bass are fighting, go back to the mix. If the low end is muddy, go back to the mix. Mastering is a polish on a finished piece of furniture — it cannot rebuild the chair.

**The order that works**

1. **EQ first** — subtle tonal moves, `±1-2 dB` maximum
2. **Compression second** — slow, gentle glue (`2:1` ratio, `1-2 dB` GR)
3. **Saturation** (optional) — a whisper of tape or tube warmth
4. **Stereo width** (optional) — widen above `2 kHz`, collapse bass under `120 Hz`
5. **Limiter last** — sets the ceiling, brings up loudness
6. **Dithering** — only when reducing bit depth, applied ONCE at the very end

**How this shows up in Sozawen**

Open the Export panel. You'll see platform presets — Spotify, Apple Music, YouTube, SoundCloud, CD, and a generic Mastering preset. Each one pre-configures your LUFS target, true peak ceiling, sample rate, bit depth, and dithering mode. Alongside the export, Sozawen gives you an integrated **LUFS meter**, a **True Peak meter**, a mastering **Limiter**, and **Reference A/B** for comparing against commercial tracks.

**Common beginner mistakes**

- Mastering before the mix is done. Finish the mix first. Bounce it. Import the stereo file. THEN master.
- Reaching for a limiter to "fix" a weak mix. A limiter amplifies whatever is underneath it — good and bad.
- Mastering while tired. Your ears lie to you after three hours. Sleep on it. Listen fresh.
- Mastering in headphones only. Check on speakers, check in the car, check on a phone.

**One advanced note**

"Mastering" used to mean cutting a physical lacquer for vinyl. That job still exists, and the engineer who does it is called a mastering engineer for a reason — they are the last pair of ears before the world. If you master your own song, you become that last pair of ears. Take breaks. Trust references. Don't fall in love with loudness.

**Related reading:** `loudness_standards`, `reference_mixing`, `export_formats`, `release_guide`, `compression_guide`, `eq_guide`, `common_mistakes`."""
    },

    "loudness_standards": {
        "title": "Loudness Standards (LUFS)",
        "category": "Mastering",
        "content": """LUFS looks like jargon. It isn't. LUFS (Loudness Units relative to Full Scale) is simply how loud your song sounds to a human ear, averaged over time. Unlike peak meters, which only see spikes, LUFS measures the felt loudness the way your ears actually perceive it.

**Why you care:** every major streaming platform now normalizes loudness. If you deliver a track at `-8 LUFS`, Spotify will turn it DOWN `6 dB` to reach their `-14 LUFS` target. Your listener hears a quieter, more squashed version of your song than they would have heard if you'd just mastered to `-14 LUFS` in the first place. Mastering at the target means what you hear is what your listener hears.

**Platform targets**

| Platform | Integrated LUFS | True Peak Ceiling | Notes |
|----------|-----------------|-------------------|-------|
| **Spotify** | `-14 LUFS` | `-1 dBTP` | Normalizes by default; turn off in settings for loud masters |
| **Apple Music** | `-16 LUFS` | `-1 dBTP` | Sound Check is always on |
| **YouTube** | `-14 LUFS` | `-1 dBTP` | Only turns loud tracks down, never up |
| **YouTube Music** | `-14 LUFS` | `-1 dBTP` | Same as YouTube |
| **Tidal** | `-14 LUFS` | `-1 dBTP` | Lossless delivery still normalized |
| **Amazon Music** | `-14 LUFS` | `-2 dBTP` | Stricter true peak |
| **SoundCloud** | `-14 LUFS` | `-1 dBTP` | Normalization is newer, inconsistent |
| **Deezer** | `-15 LUFS` | `-1 dBTP` | |
| **CD / Bandcamp** | `-9 to -12 LUFS` | `-0.3 dBTP` | No normalization; loud masters OK |
| **Podcast** | `-16 to -18 LUFS` | `-1 dBTP` | Mono check required |
| **Broadcast (EBU R128)** | `-23 LUFS` | `-1 dBTP` | Law in Europe |
| **Broadcast (ATSC A/85)** | `-24 LUFS` | `-2 dBTP` | US TV standard |

**The honest takeaway**

For most streaming delivery, target `-14 LUFS integrated` with a `-1 dBTP` ceiling. That single master will behave well on Spotify, YouTube, Tidal, Amazon, SoundCloud, and Deezer. Apple Music prefers `-16 LUFS`, but a `-14 LUFS` master will simply be turned down slightly — it won't sound bad.

**How this shows up in Sozawen**

The Export panel has one-click presets for Spotify `-14`, Apple Music `-16`, YouTube `-14`, SoundCloud, CD, and a generic Mastering preset. The built-in **LUFS meter** shows Integrated, Short-term, and Momentary readings live. The **True Peak meter** shows inter-sample peaks so you know if your limiter ceiling is really safe. The mastering **Limiter** has a true-peak mode — turn it on for streaming delivery.

**Common beginner mistakes**

- **Matching LUFS is not mastering.** Turning a squashed `-8` master down to `-14` does NOT make it a `-14 LUFS` master. The dynamics are still gone. The loudness war already happened inside the file.
- **Ignoring true peak.** Your sample-peak meter can read `-1.0 dB` while your true peak is `+0.4 dB` and clipping on lossy encoders. Always use a true-peak meter.
- **Mastering to Spotify's reported LUFS instead of your meter.** Spotify's analyzer lags and uses slightly different gating. Trust a calibrated ITU-R BS.1770 meter (like the one Sozawen uses).
- **Chasing `-8 LUFS` like it's 2005.** That's a mastered-for-CD loudness. Modern streaming punishes it.

**One advanced note**

There are three LUFS readings: **Integrated** (whole-track average), **Short-term** (3-second window), and **Momentary** (400 ms window). Platforms normalize on Integrated. But your chorus should probably read `-12 to -10` Short-term even if Integrated is `-14`, because quiet verses pull the integrated number down. A "dynamic" master isn't quiet — it's a master where the loud parts are actually louder than the quiet parts.

**Related reading:** `mastering_basics`, `export_formats`, `export_platforms`, `reference_mixing`, `compression_guide`, `release_guide`, `common_mistakes`."""
    },

    "export_formats": {
        "title": "Export Formats Guide",
        "category": "Mastering",
        "content": """The export dialog looks intimidating — WAV vs FLAC vs MP3, `16-bit` vs `24-bit` vs `32-bit float`, `44.1` vs `48` vs `96 kHz`, dithering modes. In practice there are only a few combinations you'll ever use, and the right one depends entirely on where the file is going.

**Format comparison**

| Format | Compression | Quality | Typical Size (3 min) | Best For |
|--------|-------------|---------|----------------------|----------|
| **WAV** | None | Perfect | ~`30 MB` at `16/44.1` | Platform delivery, mastering, archive |
| **AIFF** | None | Perfect (same as WAV) | ~`30 MB` at `16/44.1` | Apple-centric workflows |
| **FLAC** | Lossless | Perfect | ~`18 MB` | Bandcamp, Tidal, archive, sharing |
| **ALAC** | Lossless | Perfect | ~`18 MB` | Apple ecosystem archive |
| **MP3 320** | Lossy | Very good | ~`7 MB` | Demos, email, previews |
| **MP3 192** | Lossy | Good | ~`4 MB` | Streaming demos |
| **OGG Vorbis** | Lossy | Slightly better than MP3 | ~`4-7 MB` | Web, games, Spotify internal |
| **AAC 256** | Lossy | Very good | ~`6 MB` | Apple Music internal, iTunes |
| **Opus** | Lossy | Best modern lossy | ~`3-5 MB` | YouTube internal, modern web |

**Sample rate**

- **`44.1 kHz`** — CD standard. What you should deliver for music in almost every case.
- **`48 kHz`** — video/film standard. Use this for anything going to YouTube, TV, or video.
- **`88.2 / 96 kHz`** — high-res. Useful for tracking and mixing headroom. Almost always a waste for final delivery — streaming platforms downsample anyway.
- **`192 kHz`** — almost never needed. Big files, no audible benefit.

**Bit depth**

- **`16-bit`** — CD quality. `~96 dB` dynamic range. Required for CDs, fine for most streaming.
- **`24-bit`** — studio standard for delivery. `~144 dB` dynamic range. Use for any high-quality master.
- **`32-bit float`** — the "can't clip" format. Use for internal project rendering and stem exports, NOT for platform delivery.

**Dithering**

When you reduce bit depth (e.g. `24-bit` mix → `16-bit` master for CD), the last few bits get truncated. Truncation sounds like quiet crunchy distortion on fadeouts and reverb tails. **Dither** is a tiny amount of shaped noise added during the conversion — it masks the truncation and restores smooth low-level detail.

- **TPDF (Triangular PDF)** — standard, transparent, safe default for everything.
- **Rectangular** — older, slightly noisier, rarely used today.
- **Noise-shaped / highpass TPDF** — pushes dither noise into the `>16 kHz` region where it's less audible. Good for critical listening masters.

**Apply dither ONCE, at the very last step of your export chain.** Never dither twice.

**Recommended exports by destination**

| Destination | Format | Sample Rate | Bit Depth | Dither |
|-------------|--------|-------------|-----------|--------|
| Spotify / Tidal / Apple / Amazon | `WAV` | `44.1 kHz` | `24-bit` | No |
| YouTube / video | `WAV` | `48 kHz` | `24-bit` | No |
| CD / DDP | `WAV` | `44.1 kHz` | `16-bit` | TPDF |
| Bandcamp | `WAV` or `FLAC` | `44.1 kHz` | `24-bit` | No |
| Demo / email | `MP3 320` | `44.1 kHz` | — | — |
| Archive / stems | `WAV` or `FLAC` | session rate | `24-bit` or `32f` | No |

**How this shows up in Sozawen**

The Export panel has platform presets that configure format, sample rate, bit depth, and dither for you — Spotify, Apple Music, YouTube, SoundCloud, CD, Bandcamp, and a generic Mastering preset. You can also export custom. Dithering options include **TPDF**, **rectangular**, and **highpass-shaped**. Bit-depth options are `16`, `24`, and `32-bit float`. Sample rates run from `44.1 kHz` to `192 kHz`.

**Common beginner mistakes**

- **Exporting `24-bit / 48 kHz` to Spotify thinking it sounds better.** Spotify re-encodes to lossy Ogg Vorbis / AAC at `~160-320 kbps` regardless. Deliver the format that matches the platform's spec, not the fanciest file you can generate.
- **Exporting MP3 as your master.** MP3 is for demos. Master to WAV, convert to MP3 separately for previews.
- **Dithering twice.** Once per bit-depth reduction, at the very last step. Never again.
- **Exporting `96 kHz` "for quality."** Listeners won't hear the difference; platforms downsample; file size explodes. `44.1` or `48` is correct.
- **Forgetting true-peak ceiling.** Lossy codecs add peaks. Leave `-1 dBTP` of headroom.

**One advanced note**

The `96 kHz` myth is real and stubborn. Higher sample rates are useful for recording and certain processing (pitch shifting, nonlinear saturation) where aliasing matters. They are not useful for delivery — almost no playback chain resolves above `22 kHz`, and every streaming platform downsamples. Work high, deliver at `44.1 kHz / 24-bit` for streaming or `44.1 / 16-bit TPDF` for CD.

**Related reading:** `mastering_basics`, `loudness_standards`, `export_platforms`, `release_guide`, `reference_mixing`, `common_mistakes`."""
    },

    "reference_mixing": {
        "title": "Using Reference Tracks",
        "category": "Mastering",
        "content": """Your ears lie to you. Not because they're broken, but because they're brilliant — they adapt. After an hour on a mix, your brain tunes itself to the song you're working on and quietly tells you it sounds great. Two days later you listen in the car and everything is wrong. A **reference track** — a commercially released song you trust — is the cheapest, fastest way to beat this.

**What a reference track is**

A reference is a professionally mixed and mastered song in a similar genre, tempo, and vibe to the one you're making. Not your favorite song of all time. Not something aspirational you could never reach. A song that sounds right on every system and lives in the same neighborhood as what you're building.

**Why it works**

Your reference is the ground truth. When you flip between your mix and the reference, all the things your tired ears stopped hearing come flooding back: the kick punches harder on the reference, the vocal sits a little more forward, the high end is airier, the stereo image is wider at the top and tighter at the bottom. You stop arguing with yourself and start hearing again.

**How to use references in Sozawen**

1. Pick two or three references, not just one. Different songs expose different problems.
2. Drop them into Sozawen's **Reference A/B** panel (or add them as a muted stereo track).
3. **Match loudness.** This is the step most beginners skip. The reference is `-9 LUFS` mastered, your mix is `-18 LUFS` unmastered — of course the reference sounds better. Pull the reference down with the Reference A/B gain control until its short-term LUFS matches yours. Now the comparison is honest.
4. A/B in short bursts. Don't listen to `30 seconds` of your mix vs `30 seconds` of the reference. Flip every `5-10 seconds`. Your ear memory is about that long.
5. Compare specific things in specific passes: first pass bass, then vocals, then highs, then stereo width, then dynamics.

**What to listen for**

- **Low end:** is your kick and bass as tight, as defined, as controlled?
- **Midrange:** does your vocal sit with the same presence? Or is it buried/harsh?
- **High end:** does your mix have air at `10-15 kHz`, or is it dull? Or harsh?
- **Stereo image:** is the reference wider on top, tighter on bottom? Yours too?
- **Dynamics:** does the chorus lift? Or is everything the same volume?
- **Translation:** check both on headphones AND speakers, both at low AND normal volume.

**Common beginner mistakes**

- **Comparing loudness instead of sound.** Louder always wins a blind A/B. Loudness-match or you're fooling yourself.
- **One reference.** Different mixes solve different problems. Use a few.
- **Wrong-genre references.** A folk song is not a useful reference for a dubstep track. Genre sets the rules.
- **Copying the reference instead of calibrating against it.** The reference tells you where the goalposts are. Your song still has to be your song.
- **Only referencing at mix time.** Reference during tracking too. If your raw recordings can't hang with commercial raw recordings, no amount of mixing saves them.

**One advanced note**

Reference matching is a compass, not a map. Even great mastering engineers reference constantly — not to copy tonality, but to stay honest. Sozawen's Reference A/B can match the reference's LUFS to your mix automatically, but you can also invert and null-test in certain cases to hear EQ differences directly. Don't over-use it. The goal is a song that sounds like itself, not a clone.

**Related reading:** `mastering_basics`, `loudness_standards`, `export_formats`, `eq_guide`, `compression_guide`, `common_mistakes`, `release_guide`."""
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
        "content": """Sing a song in C major and it feels too low. Slide every note up three frets — suddenly it fits your voice. That's transposition: shifting **every note by the same interval**, so the song stays recognizable but sits in a new key.

**The core idea.** Transposition doesn't change the *song* — it changes the *pitch* the song lives at. The shape between notes stays identical. If the melody went up a fourth and down a step in C, it goes up a fourth and down a step in E too. Only the starting pitch moved.

Think of it like sliding a shape along a ruler. The shape is the song. The ruler is pitch.

**Vocabulary.**
- **Interval** — the distance between two notes (minor third, perfect fifth, octave). Transposition is defined by an interval.
- **Key** — the tonal home base of a song. "Transposing from C to E" means shifting up a major third.
- **Semitone / half-step** — smallest standard Western interval. One fret. One piano key (black or white, whichever's next).
- **Nashville Numbers** — chords written as scale degrees (1, 4, 5, 6m) instead of letters. Key-independent notation — transposing becomes trivial.
- **Capo** — a clamp that shortens guitar strings, transposing the whole instrument up without changing your hand shapes.

**Why musicians transpose.**
- **Vocal range.** The #1 reason. A song written for a tenor buries an alto. Drop it a fourth.
- **Modulation.** Shifting keys mid-song for lift (think the last chorus going up a whole step).
- **Capo substitution.** You want the ringing open chords of G, but the singer needs B♭. Capo 3, play in G shapes.
- **Transposing instruments.** Some instruments are written in one key and sound in another (see below).

**In Sozawen.** Right-click any clip or selection and choose **Transpose**. Enter an interval in semitones (±12 per octave) or pick a target key — Sozawen shifts MIDI notes, updates chord symbols, and re-notates the sheet music simultaneously. The **Key Lock** toggle keeps the transposition diatonic (snaps to the new key's scale) instead of literal chromatic shifting. Chord charts switch between letter names and Nashville numbers in the **Composition** panel — one click flips the whole score.

**Common mistakes:**
- **Transposing audio like it's MIDI.** Pitch-shifting recorded audio more than ~3 semitones starts sounding artificial. For big shifts, re-record.
- **Forgetting the capo math.** Capo 3 means your G shape sounds as B♭. Players often hand charts to bandmates in "shape key" when the band needs "sounding key."
- **Transposing the melody but not the chords.** Easy to do when working by ear. Lock them together.
- **Transposing past the instrument's range.** A bass line shifted up an octave may leave the instrument's lowest string unused, or push it past the highest fret.
- **Ignoring the feel change.** A song in E is bright and ringing on guitar; the same song in F is fretted and closed. Same notes, different vibe.

**Going deeper — transposing instruments.** Some instruments are **notated in a different key than they sound**, a convention inherited from the mechanics of brass and woodwinds.

- **B♭ trumpet / B♭ clarinet / tenor sax** — written a whole step above sounding pitch. When the page says C, the audience hears B♭.
- **E♭ alto sax / baritone sax** — written a major sixth (alto) or an octave + major sixth (bari) above sounding pitch.
- **F horn** — written a perfect fifth above sounding pitch.

Why? Historically, each horn came in multiple keys (trumpet in C, in B♭, in D…), and fingering stayed the same across them. Writing in the instrument's "home" key meant a player could switch horns without relearning fingerings. That convention survived even as horns standardized.

**For the composer:** if you're arranging for a B♭ trumpet to play a concert-pitch melody, transpose *up a whole step* on the page for that player. Sozawen's per-track **Transpose Display** setting does this automatically — the score shows the trumpet its part, the playback sounds at concert pitch.

**Nashville numbers** are the pro's shortcut. A chart written `1 - 5/7 - 6m - 4` works in every key. Change the key letter at the top, and the whole band transposes in their heads. No re-writing needed."""
    },

    # ═══════════════════════════════════════════════════════════════
    # INSTRUMENTS & GEAR
    # ═══════════════════════════════════════════════════════════════

    "guitar_types": {
        "title": "Guitar Types & When to Use Them",
        "category": "Instruments",
        "content": """Listen to the opening of "Wish You Were Here" and you hear a **dreadnought acoustic** — big, warm, forgiving. Switch to "Blackbird" and that's a smaller-bodied **OM** — balanced, fingerstyle-friendly. Now put on "Smoke on the Water" and you're hearing a **solidbody electric** pushing a cranked amp. Same six strings, three different worlds.

The guitar's shape, wood, and construction decide **which frequencies sing and which get tamed**. A big box moves more air (loud, bass-heavy); a small box controls overtones (tight, articulate); a hollow electric feeds back easily but swings like nothing else.

**Acoustic guitars:**
- **Dreadnought** — The Martin D-28 shape. Big low end, strong projection. The country, bluegrass, and singer-songwriter default. Johnny Cash, Neil Young, Jason Isbell.
- **Orchestra Model (OM) / 000** — Smaller waist, balanced EQ, responsive to a light touch. The fingerstyle king. James Taylor, Paul Simon, John Mayer's "Stop This Train."
- **Parlor** — Tiny body, midrange-forward, almost banjo-like snap. Blues and porch music. Early Robert Johnson recordings.
- **Jumbo** — Even bigger than a dread, scooped mids, booming lows. Gibson J-200. Elvis, Emmylou Harris.
- **Classical (nylon)** — Wide neck, no truss rod tension, mellow and warm. Flamenco, bossa nova, classical. Willie Nelson's "Trigger" is an outlier Martin N-20.

**Electric guitars:**
- **Solidbody** — Strat, Tele, Les Paul. No feedback, infinite sustain with gain. Rock, metal, funk, country lead.
- **Semi-hollow** — ES-335. Warmth of hollow, control of solid. Blues, jazz-rock, indie. Dave Grohl's Pelham Blue, B.B. King's Lucille.
- **Hollowbody / Archtop** — Gretsch, L-5. Jazz comping, rockabilly. Brian Setzer, Wes Montgomery.

**12-string** — Every string paired (low four in octaves, high two in unison). Chimes like a harp. "Hotel California" intro, Byrds' "Mr. Tambourine Man."

**Resonator** — Metal cone instead of wooden top. Slide blues and bluegrass dobro. "Come On In My Kitchen."

**In Sozawen.** The Instruments Panel ships physical models for the **Martin D-28**, **Taylor Dreadnought**, **Gibson J-45**, **Fender Stratocaster**, **Gibson Les Paul**, and **Classical nylon**. Each uses Karplus-Strong waveguide synthesis tuned to the real instrument's modal spectrum — pick position, body resonance, and string material are all exposed. Switch body type and the Score overlay auto-adjusts capo suggestions; the Composition Editor knows a parlor doesn't want a low-E drone and will flag it.

**Common mistakes:**
- Using a dreadnought for delicate fingerstyle. The bass bloom drowns inner voices. Reach for an OM or 000.
- Tracking a jumbo and an electric bass together without EQ. Both live at 80-120 Hz. Carve one.
- Choosing a 12-string for busy strumming. It smears. 12s shine on slow arpeggios and single chord stabs.
- Recording an archtop close-mic'd at the soundhole. Boomy and boxy. Mic the 12th fret at 8-12 inches.
- Assuming nylon and steel-string are interchangeable. Fingerboard widths differ by ~6mm; your chord shapes won't feel the same.

**Going deeper.** Top wood sets the attack transient — **spruce** is bright and percussive, **cedar** is warm and compressed, **mahogany** is mid-focused. Back and sides shape sustain and overtone spread — **rosewood** gives that deep piano-like bloom, **maple** is dry and fast, **koa** sits between. Electric pickups split into **single-coil** (Strat/Tele — bright, noisy, articulate), **humbucker** (Les Paul — thick, quiet, compressed), and **P-90** (between both — bark plus bite). Scale length matters too: a 25.5" Fender scale has more string tension and snap than a 24.75" Gibson scale, which is why Strats feel tight and Les Pauls feel loose under the same gauge."""
    },

    "tuning_reference": {
        "title": "Tunings & Alternative Tunings",
        "category": "Instruments",
        "content": """Joni Mitchell didn't write in standard tuning. Neither did half of Led Zeppelin's acoustic catalog. Retune two strings and the guitar **becomes a different instrument** — new chord shapes, new open-string drones, new mistakes that suddenly sound like discoveries.

**Standard tuning** is `E-A-D-G-B-E` low to high. It's a compromise designed to make common chord shapes reachable with four fingers. Every other tuning trades that convenience for something else — usually **resonance**, **voicing**, or **ease of a specific technique**.

**The common alternates:**
- **Drop D** (`D-A-D-G-B-E`) — Just the low E down a whole step. Power chords become one-finger barres. Huge low end. Soundgarden ("Spoonman"), Foo Fighters ("Everlong" uses Drop D with the rest down a half step), Rage Against the Machine.
- **DADGAD** — Drop D plus the G and high E also dropped a whole step, leaving a suspended D voicing across open strings. Celtic, modal folk, raga-adjacent. Jimmy Page ("Kashmir," "Black Mountain Side"), Pierre Bensusan's entire career.
- **Open G** (`D-G-D-G-B-D`) — Strum all strings open and you get a G major chord. Slide blues and Keith Richards' whole Stones rhythm style ("Start Me Up," "Brown Sugar" — Keith famously removes the low E and plays five-string Open G).
- **Open D** (`D-A-D-F#-A-D`) — Open chord is D major. Slide resonator territory. "She Talks to Angels" by Black Crowes. Joni Mitchell lived here too.
- **Open E** (`E-B-E-G#-B-E`) — Same intervals as Open D but up a whole step. **Higher string tension — not safe on every guitar.** Duane Allman slide work, "Jumpin' Jack Flash."
- **Double Drop D** (`D-A-D-G-B-D`) — Both E strings to D. Neil Young's "Cinnamon Girl" and "The Loner." Modal droning top and bottom.
- **Nashville tuning** — Take a 12-string set and use only the high octave strings. Turns a 6-string into a shimmering octave-up instrument. Layered under regular guitars for sparkle. "Wild Horses" studio recording.

**How to retune safely:** Always detune **down** to target pitch, not up (catches any slack, keeps intonation stable). Retune in small increments across all strings, then pass again — guitars settle, and the first pass will drift as neck tension rebalances. Stretch each string gently after tuning. For Open E specifically, consider using lighter gauge strings since you're raising three strings in pitch.

**In Sozawen.** The Composition Editor has a **Tuning dropdown** in the guitar instrument panel — pick Standard, Drop D, DADGAD, Open G, Open D, Open E, Double Drop D, or Nashville, and the Score overlay re-draws the fretboard with new open-string labels. **Chord suggestions reroute automatically**: in DADGAD, the editor won't suggest a barred F — it'll suggest the two-finger modal voicing that tuning invites. The Tab view shows fret numbers based on the active tuning, so imported MIDI translates correctly. Physical models reflect the actual string tension — a Drop D low string has measurable floppier attack in the sound, not just a pitch shift.

**Common mistakes:**
- Tuning up to Open E on a vintage or thin-top acoustic. The added tension can bow the neck or pull the bridge. Use Open D and capo at fret 2 instead.
- Forgetting capo math. A capo at fret 5 in Drop D gives you `G-D-G-C-E-G` — not standard transposed. The Score overlay handles this; your brain often doesn't.
- Using a clip-on tuner's default mode. Most expect standard. Switch to chromatic when working alternate tunings.
- Writing a DADGAD song and trying to perform it in standard. The voicings don't translate. Commit to the tuning on stage.
- Retuning without stretching. New pitch + unstretched string = 30 seconds of slow drift mid-take.

**Going deeper.** Alternate tunings are really about **which notes ring out when you don't fret them**. Standard tuning's open strings spell `E-A-D-G-B-E` — an Em11 with no clear tonal center, which is why we barre and fret so much. Open tunings preload a chord; modal tunings (DADGAD, CGDGCD) preload ambiguity — they're neither major nor minor until you define it. This is why DADGAD feels so "Celtic": Celtic music leans modal, and the tuning already agrees. Mathematically, each tuning creates a different **fret-distance-to-interval map**. The blues box shape you memorized in standard is geometrically different in Open G — and that's exactly why Keith Richards sounds like Keith Richards."""
    },

    "vocal_recording": {
        "title": "Recording Vocals",
        "category": "Recording",
        "content": """The vocal is usually the loudest, most exposed element in your song. Every flaw you record — room noise, plosives, weak takes, clipping — shows up louder than the rest of the mix. Treat vocal tracking like the main event, because it is.

**The concrete version:** Singer in front of a large-diaphragm condenser, pop filter two inches from the mic. You hit the **count-in** button in Sozawen's transport so the singer gets a `1 bar` click before recording starts. Headphones on, input monitoring on, backing track playing. Record arm the vocal track, press **Record**, and capture takes one through five back-to-back. That's a vocal session.

## The Chain

`Singer -> Pop filter -> Mic -> Interface preamp -> Sozawen`

Keep it short. Every stage adds a little noise. For vocals especially, you want a clean chain and then add character in the mix, not at the source.

## Mic Choice

- **Large-diaphragm condenser** (Rode NT1, AT2020, U87 if you're rich) — the default for studio vocals. Detailed, full-bodied, picks up everything including the room.
- **Dynamic** (SM7B, SM58) — best for loud singers, screamers, rappers, and anyone working in an untreated room. Rejects room sound, forgives bad acoustics.
- **Ribbon** — silky, vintage tone. Fragile. **Never send phantom power.**

If your room sounds bad and you only have one mic, a dynamic will almost always sound more professional than a condenser, because it isn't picking up your refrigerator in the next room.

## The Room Matters More Than the Mic

An untreated room with bare walls and hard floors creates slapback reflections that a condenser captures along with the voice. You cannot EQ this out later. Quick fixes that actually work:

- Hang heavy blankets behind and to the sides of the singer
- Record inside a closet full of hanging clothes
- Set up a reflection filter behind the mic
- Face the singer away from parallel hard walls

## Setup in Sozawen

1. In the **Input Device** panel, pick your interface.
2. Create a mono track. Set its **input channel** to wherever the mic is plugged in (channel 1 is typical).
3. **Arm** the track (the record-enable button on the track).
4. Turn on **input monitoring** so the singer hears themselves in headphones with the rest of the mix.
5. Enable **count-in** in the transport (one or two bars of click) so the singer has time to breathe and come in.
6. Set the interface's input gain so the loudest note peaks around `-12 to -6 dBFS`.
7. If you're fixing a single line or section, set **punch in/out** points so recording only happens within that region — the singer can sing over the rest safely.
8. Hit **Record**. Capture 3 to 5 full takes.

## Comping

After you've got several takes, cut them into phrases and keep the best phrase from each take. This is called **comping** (short for composite). It's how every professional vocal you've ever loved was assembled. Nobody nails a whole song in one pass. Chasing "the perfect take" in one shot will wear out the singer and cost you the magic.

## Performance Tips

- Warm up the voice for `5 to 10 minutes` before recording. Cold vocals sound cold.
- Keep room-temperature water nearby. Never ice water — it tightens the throat.
- Record the chorus last if the singer is getting tired; the high-energy sections need the freshest voice.
- Encourage multiple expressive takes, not one cautious one. You can't comp emotion you didn't capture.

## Common Beginner Mistakes

- **Singer too close to the mic** — plosives explode, breathing is deafening. `6 to 10 inches` is the zone.
- **Gain too hot** — a surprise loud note clips and the take is unusable. Back off.
- **Monitoring through speakers** — the mic picks up the backing track and you can never separate them. Headphones only.
- **No pop filter** — every "p" and "b" sounds like a bomb. `$10` pop filter fixes this forever.

## Double Tracking

Record the same lead vocal line twice. Pan one hard left, one hard right. The tiny natural timing and pitch differences between takes create a thickness and width no plugin can replicate. Works for harmonies, ad-libs, backgrounds. Use sparingly on the main lead — sometimes a single, dry lead is more powerful.

## Going Deeper

Mouth-on-diaphragm distance changes tone through **proximity effect** — closer equals bassier. Intimate ballad: `3 to 4 inches`. Pop lead: `6 inches`. Rock belting: `8 to 12 inches`. Move the singer, not the EQ.

See also: `mic_placement`, `signal_chain`, `gain_staging`, `compression_guide`, `eq_guide`."""
    },

    "drum_recording": {
        "title": "Recording Drums",
        "category": "Recording",
        "content": """Drums are the loudest, most dynamic, most unforgiving thing you will ever record. Everything is transient, everything is a peak, and every mic picks up every other drum. Miked well, a real kit in a real room sounds alive in a way samples almost never do. Miked badly, it sounds like cardboard boxes in a hallway.

**The concrete version:** Two mics — one condenser hanging over the kit, one dynamic inside the kick drum. Pan the overhead to taste. Set both inputs so the loudest hits peak at `-10 to -6 dBFS` on Sozawen's input meters. Drummer plays, Sozawen records two tracks in sync. That's a usable drum recording with the absolute minimum gear.

## Tune Before You Record

A poorly tuned kit wastes everyone's time. No amount of mixing saves a ringing, flabby drum kit. Tune first:

- **Kick** — batter head fairly tight, resonant head looser. Muffle with a small pillow or folded towel if it rings too long.
- **Snare** — medium-tight head, snare wires snug but not choked flat against the bottom head. Tap and listen for clear pitch, not wobble.
- **Toms** — even tension around each lug. Tap 1 inch in from every lug and match pitches.
- **Cymbals** — clean them, check for cracks, make sure they're not hitting each other.

## Mic Setups — Build Up, Don't Jump In

**Two-mic (minimum viable):**
- 1 condenser overhead, dead center above the kit, `3 to 4 feet` up
- 1 dynamic (SM57, Beta 52, D6) inside the kick port

This captures `80%` of what most pop/rock needs. The overhead gives you snare, hats, cymbals, and toms as a natural blend; the kick mic gives you thump.

**Four-mic (standard):**
- Kick (inside the drum)
- Snare top (SM57, `1 inch` above the head, pointed at center, angled slightly away from the hat)
- Matched pair of overheads in **X-Y** (two cardioids meeting at 90 degrees, one point) or **spaced pair** (two mics `3 feet` apart, equidistant from snare)

**Eight-plus mic (full):**
- Kick in, kick out (outside the resonant head for weight), snare top, snare bottom (polarity-flipped to combine cleanly with top), hi-hat, two overheads, room mic `6 to 10 feet` back

The room mic, crushed with a compressor later, is often the secret behind records that sound huge.

## Phase Is Everything

With multiple mics, every drum hits every mic — just at slightly different times. If two mics capture the same hit out of phase with each other, frequencies cancel and the drum sounds thin and weird. Fix it:

1. Apply the **3:1 rule** — distance between any two mics should be at least 3x the distance from each mic to its source.
2. After setup, solo the overheads. Add the close mics one at a time. If the snare gets **thinner** when you unmute the overheads, flip the polarity on that overhead or that close mic and listen again. Keep whichever version sounds fuller.
3. In Sozawen, each track has a polarity/phase invert control — flip it, compare, keep the better one.

## Setup in Sozawen

1. Open the **Input Device** panel and confirm your multi-input interface is selected.
2. Create one track per mic. Name them immediately: `Kick In`, `Snare Top`, `OH L`, `OH R`, etc. Color-code them.
3. Assign each track's **input channel** to the matching physical input on the interface.
4. Arm all drum tracks.
5. Have the drummer play their loudest section. Set input gains so each track peaks around `-10 to -6 dBFS`. Toms almost always spike higher than you expect — leave headroom.
6. Enable **count-in** so the drummer knows exactly where to come in.
7. Turn off **input monitoring** on the drum tracks — the drummer should hear the click and backing track in headphones, not a delayed version of themselves.
8. Use **punch in/out** to redo sections without recording over the whole take.

## Common Beginner Mistakes

- **Gain too hot on toms.** Quiet during the verse, explosive during the fill. Set the level on the fills.
- **Overheads not equidistant from the snare.** The snare drifts off-center in the stereo field and sounds weird.
- **Ignoring phase.** Half the reason beginner drum recordings sound small is uncorrected phase cancellation between the close mics and the overheads.
- **Miking a bad-sounding room.** Drums are huge sound sources. If the room is bad, close-mic everything and avoid ambient mics entirely.

## No Drummer? No Problem.

Use Sozawen's built-in drum machine. Program a pattern, lay down the rest of the song on top, replace with a real drummer later if you want. Plenty of hits were built this way.

## Going Deeper

Compressing the room mic heavily and blending it under the close mics is one of the oldest tricks for making drums sound massive. Parallel compression (a duplicated drum bus crushed with a compressor and blended underneath the clean bus) is another. Both work because the human ear reads "loud sustained drum tail" as "powerful drum." See the `compression_guide` for how to dial that in.

See also: `mic_placement`, `signal_chain`, `gain_staging`, `compression_guide`, `eq_guide`."""
    },

    "mixing_order": {
        "title": "Mixing Order & Workflow",
        "category": "Mixing",
        "content": """A great mix isn't one magic move — it's a hundred small decisions made in the right order. Start with the wrong thing and every later step fights you. Start with the right thing and everything falls into place. This is a workflow that works whether you're mixing a folk duet or a metal record.

**The golden rule:** balance, space, dynamics, tone, motion — in that order. Faders first. EQ and compression later. Effects last. Do it backwards and you'll end up chasing problems you created yourself.

**Step 0 — Don't start mixing yet**

Before you touch a fader, listen through the song three times. Take notes. What's the moment? Where should the listener's attention go in the verse, the chorus, the bridge? Mixing without a target is how you end up with a technically clean mix that feels like nothing.

**Step 1 — Organization (10 minutes that save 10 hours)**

- Name every track. "Audio 14" is not a name.
- Color-code by group: drums blue, bass yellow, guitars green, keys orange, vocals purple.
- Delete unused tracks and empty regions.
- Set up group buses in Sozawen: drum bus, guitar bus, vocal bus, FX bus (for reverbs and delays).
- Route related tracks to their group. Now one fader controls all the drums, all the vocals, etc.

**Step 2 — Gain staging**

Before any processing, set the input level of every track so peaks hit around `-12 to -6 dBFS`. Not `0 dB`, not `-3 dB` — leave headroom. Plugins and analog-modeled gear sound best in this range. If tracks are slamming the red, your compressors and saturators will sound ugly and nothing will fix it later. See `gain_staging` for details.

**Step 3 — Static balance (faders only)**

All faders down. Plugins off. Pan centered. Bring up the lead vocal first — set it to a comfortable level (peak around `-8 dBFS`). Now bring up the rest *underneath* it, in this order:

1. Kick and bass (the foundation)
2. Snare and rest of the drums
3. Rhythm guitars and keys
4. Background vocals, pads, ear candy

Pull faders *down* to taste rather than *up*. It forces you to make real decisions about what matters. The mix should already sound like a *mix* before you add a single plugin. If it doesn't, fix the balance before you touch EQ.

**Step 4 — Panning**

See `panning_guide` for the full rundown. Quick version:

- Center: kick, snare, bass, lead vocal.
- Slight L/R (`20-40%`): rhythm guitars, keys, background vocals.
- Wide (`60-100%`): stereo doubles, overheads, pads, FX returns.
- Keep everything below `150 Hz` mono.

**Step 5 — EQ (subtractive first)**

Cut before you boost. For every track:

1. **HPF** everything except kick and bass (`80-200 Hz` depending on source).
2. Cut the **mud** (`200-400 Hz`) on guitars, keys, and backing vocals that don't need it.
3. Carve **space for the vocal** (`2-4 kHz`) by cutting a small dip there on the guitars and keys.
4. *Then* — and only then — reach for subtle boosts where an instrument needs to shine.

See `eq_guide` and `frequency_chart`.

**Step 6 — Compression**

Once EQ has opened up space, compression tightens the dynamics.

- **Vocals:** `3:1` ratio, `4-6 dB` gain reduction. Even out the performance so every word sits at the right level.
- **Drums:** slow attack (`20-40 ms`) for punch on the kick and snare. Parallel compression on the drum bus for density.
- **Bass:** `4:1` ratio, `5-8 ms` attack, consistent low end.
- **Mix bus (glue):** `1.5:1` to `2:1`, only `1-2 dB` of reduction. Makes everything feel like one thing.

See `compression_guide`.

**Step 7 — Space (reverb & delay)**

Now that the mix is tight and clear, add the *room*. Send-based, always:

- One short room reverb bus for drums (`0.6 s`).
- One medium plate reverb bus for vocals (`1.5 s`, pre-delay `30 ms`).
- One tempo-synced delay bus for vocals or lead instrument.

Less is more. You should barely notice the reverb is there. If you can clearly hear it, pull it back `30%`. See `reverb_guide`.

**Step 8 — Automation (this is where mixes become records)**

A static mix is a demo. An automated mix is a record.

- **Ride the vocal fader.** Every phrase, every word. Quiet parts up, loud parts down. Vocal rides are the single biggest difference between amateur and pro mixes.
- **Push the chorus.** Nudge the whole mix bus (or specific chorus elements) up `0.5-1 dB` at the chorus. Lift lands harder.
- **Automate FX sends.** More reverb on the last word of a line. Delay throw on the ad-lib. Motion.
- **Pull things down in the verses.** Give the chorus somewhere to go.

**Step 9 — Reference check**

Load a professional mix in the same genre. **Level-match it** (the reference will be mastered, so it's louder — pull it down so perceived loudness matches yours). Compare:

- How's the low end? Is mine thinner? Boomier?
- Where does the vocal sit? Louder or quieter than mine?
- How wide is the stereo image?
- How bright is the top end?

Use a **Spectrum Analyzer** for objective comparison. Use your ears for everything else.

**Step 10 — Check on multiple systems**

- Studio monitors (truth)
- Headphones (detail)
- Phone speaker (reality check for 25% of your listeners)
- Car stereo (reality check for the other 50%)
- Bluetooth speaker (mono summing, low-end truth)

If it sounds good on all five, you're done. If one of them is bad, that's a real problem — not that system's fault.

**Step 11 — Take a break, then final pass**

Walk away for at least an hour. Come back with fresh ears. Listen top to bottom once without touching anything. Make a short list of the two or three things that still bother you. Fix *only* those. Stop.

**Beginner mistakes about order**

- **Effects before balance.** Reverb on a track that's at the wrong volume is a waste of time.
- **EQ before gain staging.** If the track is clipping the plugin, EQ won't fix it — it'll just make the clipping sound different.
- **Compression before EQ.** Sometimes fine, but usually you want to remove mud *first* so the compressor isn't reacting to frequencies you don't want anyway.
- **Mastering the mix.** Don't slam a limiter on the master while mixing. Leave `-6 dB` of headroom. Mastering is a separate stage (see `mastering_basics`).
- **Never stopping.** A mix that's done is better than a mix that's perfect. Commit. Move on.

See also: `eq_guide`, `compression_guide`, `reverb_guide`, `panning_guide`, `frequency_chart`, `gain_staging`, `signal_chain`, `common_mistakes`."""
    },

    "frequency_chart": {
        "title": "Instrument Frequency Chart",
        "category": "Mixing",
        "content": """Every instrument has a home in the frequency spectrum. Learn where each one lives and mixing stops being guesswork — you'll know *where* to look the moment something sounds wrong. "The kick feels weak" becomes "boost `60 Hz` a little." "The vocal is harsh" becomes "cut `3 kHz` with a narrow Q." This chart is the map. Keep it open while you mix.

**How to read this chart**

- **Fundamental range** — where the lowest-to-highest pitches of the instrument sit. The *body* of the sound.
- **Key frequencies** — specific spots where important things happen: thump, click, body, bite, air. These are where you reach for EQ moves.
- **Mud zone** — the `200-500 Hz` range where everything competes. If a track sounds boxy or cluttered, check here first.

**The chart**

| Instrument | Fundamental Range | Key Frequencies | Common Moves |
|------------|-------------------|-----------------|--------------|
| **Kick drum** | `40-100 Hz` | Thump: `60-80 Hz`. Body: `100-200 Hz`. Click/beater: `2-5 kHz` | Boost `60 Hz` for power, cut `300 Hz` for mud, boost `3 kHz` for attack |
| **Snare** | `150-250 Hz` | Body: `200 Hz`. Crack: `2-4 kHz`. Wires/air: `8-12 kHz` | Boost `200 Hz` for fatness, `4 kHz` for crack, high-shelf at `10 kHz` for air |
| **Hi-hat** | `300 Hz-15 kHz` | Stick click: `8-10 kHz`. Shimmer: `12-16 kHz` | HPF at `300 Hz`, gentle boost at `10 kHz` |
| **Crash/ride** | `200 Hz-18 kHz` | Ping (ride): `3-4 kHz`. Wash: `8-15 kHz` | HPF at `300 Hz`, tame `5-7 kHz` if harsh |
| **Toms** | `80-300 Hz` | Low tom: `80-120 Hz`. High tom: `200-300 Hz`. Attack: `3-5 kHz` | Boost fundamental, cut `400-600 Hz` for mud |
| **Bass guitar** | `40-400 Hz` | Fundamental: `40-200 Hz`. Growl: `700 Hz-1 kHz`. String/pick: `2-4 kHz` | Boost `80 Hz` for low end, `800 Hz` for presence, `2.5 kHz` for definition |
| **Sub-bass / 808** | `30-80 Hz` | Fundamental: `30-60 Hz` | HPF everything else *below* it, keep mono |
| **Electric guitar (rhythm)** | `80-5 kHz` | Body: `200-500 Hz`. Bite: `2-4 kHz`. Presence: `4-6 kHz` | HPF at `100 Hz`, cut `300 Hz` mud, boost `3 kHz` for bite |
| **Electric guitar (lead)** | `100 Hz-6 kHz` | Sustain: `500 Hz-1 kHz`. Sing: `2-3 kHz` | HPF at `150 Hz`, boost `2.5 kHz` for cut-through |
| **Acoustic guitar** | `80-12 kHz` | Body: `100-250 Hz`. Boxy: `300-500 Hz`. String: `2-5 kHz`. Air: `8-12 kHz` | HPF at `100 Hz`, cut `300 Hz` boxiness, boost `10 kHz` for sparkle |
| **Piano** | `27-4200 Hz` (+ harmonics to `20 kHz`) | Warmth: `100-300 Hz`. Presence: `2-5 kHz`. Sparkle: `8-12 kHz` | Depends on role — rhythm piano: cut `300 Hz`; lead piano: boost `4 kHz` |
| **Rhodes / electric piano** | `80 Hz-8 kHz` | Body: `200 Hz`. Bark: `1-2 kHz`. Bell: `5-8 kHz` | Boost `200 Hz` for warmth, `5 kHz` for bell |
| **Organ (Hammond)** | `60 Hz-8 kHz` | Body: `200-500 Hz`. Click: `3-5 kHz` | HPF at `100 Hz`, cut `400 Hz` if muddy |
| **Vocals (male)** | `80-500 Hz` (fundamental) | Chest: `100-250 Hz`. Mud: `300 Hz`. Nasal: `1 kHz`. Clarity: `2-4 kHz`. Sibilance: `5-8 kHz`. Air: `8-14 kHz` | HPF at `80 Hz`, cut `300 Hz` mud, gentle boost `3 kHz` and `10 kHz` |
| **Vocals (female)** | `150-1 kHz` (fundamental) | Body: `200-400 Hz`. Clarity: `3-5 kHz`. Sibilance: `6-9 kHz`. Air: `10-14 kHz` | HPF at `100 Hz`, cut `400 Hz` if boxy, de-ess `7 kHz` |
| **Backing vocals** | Same as lead | Same | HPF higher (`150-200 Hz`) to clear space for lead, cut `3 kHz` so lead shines |
| **Strings (violin)** | `200 Hz-3 kHz` | Warmth: `200-500 Hz`. Presence: `1-3 kHz`. Rosin: `7-10 kHz` | Cut `400 Hz` if boxy, tame `3 kHz` if screechy |
| **Strings (cello)** | `65 Hz-1 kHz` | Body: `200-400 Hz`. Bow: `1-3 kHz` | Boost `200 Hz` for warmth |
| **Strings (ensemble)** | `60 Hz-8 kHz` | Warmth: `200 Hz`. Air: `8-10 kHz` | High-shelf boost for lushness |
| **Brass (trumpet)** | `160 Hz-1 kHz` | Honk: `500 Hz-1 kHz`. Brilliance: `3-6 kHz` | Tame `1 kHz` honk, boost `4 kHz` for edge |
| **Brass (sax)** | `100 Hz-8 kHz` | Body: `300-500 Hz`. Breath: `5-8 kHz` | Cut `500 Hz` if honky |
| **Woodwinds (flute)** | `260 Hz-2 kHz` | Breath: `2-5 kHz`. Air: `8-12 kHz` | HPF at `200 Hz`, boost `8 kHz` for air |
| **Synth pads** | varies widely | Fills whatever space you give it | HPF at `200 Hz`, sit *behind* other elements |
| **Synth lead** | `200 Hz-6 kHz` | Presence: `2-4 kHz` | Treat like a lead vocal — carve a pocket |

**The rule that makes this chart useful**

If two instruments share the same fundamental range, one has to give way. The vocal and the lead guitar both want `2-4 kHz`. The kick and the bass both want `60-100 Hz`. You can't boost both — they'll fight, and the fight sounds like mud.

**Cut, don't boost.** If the vocal needs `3 kHz`, cut a small dip at `3 kHz` on the guitar. If the kick needs `60 Hz`, cut a small dip at `60 Hz` on the bass (and maybe give the bass a boost at `80 Hz` instead, where the kick isn't). Make *space*, don't fight for it.

**Use the Spectrum Analyzer.** Sozawen's Spectrum Analyzer shows you exactly what frequencies are busy in real time. Solo two instruments that feel like they're clashing — look at the overlap. Wherever they stack on the analyzer is exactly where you need to carve.

See also: `eq_guide`, `compression_guide`, `panning_guide`, `mixing_order`, `common_mistakes`."""
    },

    "common_mistakes": {
        "title": "Common Mixing Mistakes",
        "category": "Mixing",
        "content": """Every mixer — bedroom or Grammy — has made these. The difference is that pros learned to catch them fast. This is the checklist.

**The core idea.** Mixing is about **relationships between sounds**, not the sound of any one track. A kick that's perfect in solo can vanish in the mix. A vocal that sounds gorgeous alone can sit on top of the song like it's floating above it. Every mistake below comes from mistaking *isolated perfection* for *contextual balance*.

**Vocabulary.**
- **In context** — how a track sounds with everything else playing.
- **Reference track** — a commercial song in the same genre, loaded into your session, that you A/B against.
- **LUFS** — loudness unit, how streaming platforms measure perceived volume.
- **Mono compatibility** — whether your mix survives being summed to one speaker.
- **Headroom** — dB of space between your loudest peak and 0dBFS.

**The 12 mistakes.**

**1. Mixing too loud.** Symptom: mixes sound great in the studio, thin and harsh everywhere else. *Why:* Fletcher-Munson — loud listening flatters bass and treble. *Fix:* mix at conversation level (~70-80 dB SPL). Reference at loud volume briefly, then turn down.

**2. Soloing instead of mixing in context.** Symptom: every track sounds polished, the mix sounds cluttered. *Why:* you EQ'd each track to sound full on its own. *Fix:* make EQ and level decisions with the whole mix playing.

**3. Too much reverb.** Symptom: mix sounds distant, washy, amateur. *Why:* reverb feels luxurious in solo and buries everything in context. *Fix:* pull reverb sends down until you *barely* hear them, then raise 1dB.

**4. Over-compressing.** Symptom: mix feels flat, lifeless, fatiguing. *Why:* stacking compressors without purpose. *Fix:* each compressor should have a job — glue, level control, tone. If you can't state the job, bypass it.

**5. Cutting when you should boost (and vice versa).** Symptom: thin mixes that never feel "there." *Why:* rule of thumb said "always cut" but cutting endlessly leaves nothing. *Fix:* cut to remove problems, boost to add character. Both are tools.

**6. Mixing only on one pair of speakers.** Symptom: bass-heavy on laptops, thin in cars. *Why:* your monitors have a coloration. *Fix:* check on headphones, phone speaker, car, and a Bluetooth speaker before calling it done.

**7. No reference tracks.** Symptom: you don't know if the mix is "right." *Why:* your ears drift over hours. *Fix:* load 2-3 commercial songs in the same genre. A/B every 20 minutes. Level-match them to your mix.

**8. Burying the vocal.** Symptom: you can't understand the words. *Why:* guitars and synths fought the vocal and won. *Fix:* pull the vocal up until it's too loud, back it off 0.5dB. Carve EQ space in competing instruments around 2-4 kHz.

**9. Low-cutting everything reflexively.** Symptom: mix feels small, no body. *Why:* "always high-pass below 100Hz" taken as gospel. *Fix:* low-cut only when a track has mud that isn't serving the song. Bass, kick, and often toms need their lows.

**10. Phase issues.** Symptom: mix sounds thin when summed to mono, snare loses punch. *Why:* two mics on one source (kick in/out, overheads, DI + amp) are out of phase. *Fix:* flip phase on one mic. Listen for which sounds fuller. Nudge mic tracks in ms if needed.

**11. Ignoring mono compatibility.** Symptom: mix collapses on phones, Bluetooth speakers, clubs. *Why:* heavy stereo widening and uncorrelated reverb. *Fix:* sum to mono occasionally while mixing. Anything that vanishes is a warning.

**12. Mastering-in-the-mix.** Symptom: you slap a limiter on the master and squash to match commercial loudness, mix becomes lifeless. *Why:* hearing the "finished" loudness feels satisfying. *Fix:* mix with headroom (-6 to -10 dB peak, no limiter). Let mastering be mastering.

**In Sozawen.** The **Master panel** has a **Reference Loader** — drag in up to 3 commercial tracks, level-matched automatically. The **Mono Check** button (next to the master fader) sums everything to one speaker so you can hear phase issues immediately. The **Mix Meter** shows current LUFS, peak, and correlation so you know when stereo width has become a problem. Platform LUFS targets (Spotify, Apple, YouTube, SoundCloud, CD) live in the Master panel's preset dropdown — pick the destination, Sozawen calibrates the ceiling.

**Going deeper.** Mixing is a habit loop: **listen → decide → act → reference → rest**. The "rest" is non-negotiable — ear fatigue after 90 minutes makes every decision worse. Walk away. Come back. The mistake that was invisible before the break will be obvious after it."""
    },

    "bass_guitar": {
        "title": "Bass Guitar — The Foundation",
        "category": "Instruments",
        "content": """Pull the bass out of your favorite song and it collapses. The groove goes flat, the kick drum loses its punch, the chord progression stops **meaning anything**. Listen to "Another One Bites the Dust," "Good Times," or anything Motown — the bass is the song. Everything else is decoration.

Bass players hold **two jobs at once**: lock with the kick drum (rhythm) and outline the chord changes (harmony). The instrument sits between drums and guitars both sonically (40-250 Hz is its home) and structurally.

**The iconic basses:**
- **Fender Precision (P-bass)** — Split-coil pickup, fat and thumpy, the sound of 60% of records ever made. Motown, punk, country. James Jamerson, Steve Harris, Sting's early work.
- **Fender Jazz (J-bass)** — Two single-coil pickups, scooped mids, growly and articulate. Funk, fusion, modern rock. Jaco Pastorius, Marcus Miller, Geddy Lee (partly).
- **Music Man StingRay** — Big humbucker, active 3-band EQ, aggressive and punchy. Funk slap and modern rock. Flea (early Chili Peppers), Louis Johnson, Tony Levin.
- **Rickenbacker 4001/4003** — Through-body neck, trebly bite, piano-like clarity. Chris Squire (Yes), Geddy Lee (Rush), Paul McCartney after the Hofner.
- **5-string** — Adds a low `B` (sometimes a high `C`). Metal, modern worship, gospel, film scoring. The low B needs a longer scale to stay tight.

**Scale length** matters more than most players realize. **34"** is standard long-scale — the tight, articulate Fender sound. **30-32"** short-scale (Hofner, Mustang) feels looser with a rounder, thumpier tone — McCartney's "Michelle" sound. **35"+** extended-scale is common on 5 and 6-string to keep the low B from flopping.

**Pick vs fingers vs slap:**
- **Fingers** (index and middle alternating) — Round, warm, dynamic. The default. Jamerson did everything with one finger.
- **Pick** — Bright, aggressive, consistent attack. Punk (Steve Harris actually plays fingers — the exception), Anthony Jackson, most modern rock.
- **Slap and pop** — Thumb slaps low strings, fingers pop highs. Percussive and funky. Larry Graham invented it; Flea and Marcus Miller built cathedrals on it.

**Active vs passive electronics:** **Passive** (P, J, most vintage) has volume and tone knobs; the signal goes straight from pickup to jack. Warm, slightly dark, dynamic. **Active** (StingRay, most modern 5-strings) uses an onboard preamp and battery to boost signal and add EQ (usually bass/mid/treble knobs). Cleaner, hotter, more surgical — and dead when the 9V dies mid-gig.

**In Sozawen.** The Instruments Panel has physical models for **Fender Precision**, **Fender Jazz**, **Music Man StingRay**, and **Rickenbacker 4003**. Pick-vs-finger-vs-slap is a dropdown that changes the attack transient model — it's not just EQ, it's the actual excitation waveform into the string. The Piano Roll has a **bass-focused velocity curve** that emphasizes 1-and-3 with ghost-note-friendly low velocities, and the Composition Editor's bass lane snaps to root-fifth-octave patterns while allowing full chromatic movement. Amp models (`ampeg_svt`, `darkglass`, `orange`, `fender`, `mesa`) complete the chain; the `clean_di` path gives you a pure DI for re-amping. The `acoustic_bass` body profile covers upright/fretless territory.

**Common mistakes:**
- Tracking bass DI only, no amp or amp sim. The DI is clean but lifeless. Blend with a cabinet simulation for weight.
- Doubling the kick drum on every note. Space matters. The bass should **converse** with the kick, not mirror it.
- Playing too high on the neck all the time. Low-position playing uses open strings and richer fundamentals. Bass lives in the bottom third of the fretboard more than guitar does.
- EQing bass with too much 100 Hz. That's where it clashes with kick. Carve bass around 80 or 120 depending on the drum's tuning.
- Using a pick because you're sloppy with fingers. Learn fingers first; pick is a tool, not a crutch.

**Going deeper.** Bass frequencies are **omnidirectional** below roughly 120 Hz, which is why subs don't need precise placement but mids and highs do. This is also why bass and kick fighting for the same fundamental creates mud — our ears can't separate them spatially. Mixing engineers solve this with **sidechain compression** (bass ducks when kick hits) or **complementary EQ** (kick owns 60 Hz, bass owns 100 Hz, or vice versa). Historically, the bass guitar was invented by Leo Fender in 1951 specifically to replace the upright — louder, fretted, portable. Within a decade it had rewritten what popular music could sound like, because suddenly the low end had **pitch articulation fast enough for a backbeat**. That's the whole story of R&B, soul, funk, and rock in one sentence."""
    },

    "drums_detailed": {
        "title": "Drums & Percussion — Complete Guide",
        "category": "Instruments",
        "content": """The drums are the **pulse**. Not the beat — the pulse. Take the drums out of "When the Levee Breaks" and you still have a great song; take them out of "Rosanna" and the floor drops out. Drums decide how a track **feels in the body** before the listener hears a single note.

A modern drum kit isn't one instrument — it's a **small orchestra played by one person** with four limbs.

**Kit anatomy:**
- **Kick (bass drum)** — The low thump. Foot pedal. 20-24" typical. Tuned low and muffled for rock, open and boomy for jazz.
- **Snare** — The backbeat. Wires underneath vibrate when the top head is struck. Wood (warm) or metal (crisp) shell. Every drummer's fingerprint.
- **Hi-hats** — Two cymbals on a stand, opened and closed with a foot pedal. 14" is standard. The clock of the kit.
- **Toms** — Rack toms (mounted above the kick) and floor toms (on legs). Fills, tension, atmosphere. Typical set: 10"/12" rack, 14"/16" floor.
- **Crash** — Explosive accent cymbal. 16-18". Hits on transitions.
- **Ride** — Timekeeping cymbal with a defined "ping." 20-22". Jazz lives on the ride.
- **Splash** — Tiny crash, 8-12". Quick accents.
- **China** — Inverted edge, trashy and aggressive. Metal and punk love them.

**Sticks vs brushes vs mallets:**
- **Sticks** — Standard wood (hickory, maple, oak). 5A is the default. Gives attack and definition.
- **Brushes** — Wire or plastic fibers fanned out. Sweeping on the snare creates that **sshhh** jazz sound. Philly Joe Jones, Ed Thigpen.
- **Mallets** — Felt heads. Soft swells on cymbals, orchestral tom rolls, ballads. "In the Air Tonight" fills.
- **Rods (Blastix/Hot Rods)** — Bundled dowels. Between brushes and sticks. Unplugged gigs.

**Tuning basics:** Tighter heads = higher pitch and faster decay. Looser heads = lower pitch and longer sustain. Every drum has two heads (batter on top, resonant on bottom) and both matter. Equal tension across all lugs or the drum rings ugly. Muffling (gels, tape, internal pillows for kicks) kills overtones — good for tight rock, bad for open jazz.

**Genre setups:**
- **Jazz kit** — Small kick (18"), 14" snare, one rack tom, one floor, ride-forward cymbals, open tuning. Entire kit may be quieter than a rock snare.
- **Rock kit** — 22" kick, 14" snare, 2 rack + 1-2 floor, crash-heavy. Tuned medium, moderately muffled.
- **Metal kit** — Double kick pedals or 2 kicks, triggered heads, China cymbals, tight tuning, gate compression on everything.
- **Studio session kit** — Versatile. Medium everything. Replaceable heads, multiple snares on a rack, tuned fresh for each song.

**Auxiliary percussion:**
- **Shaker** — Eggs or tubes. Adds a sixteenth-note layer. In your top 10 favorite pop songs, probably 7.
- **Tambourine** — Jingles on a frame. Strong on 2 and 4 to lift choruses.
- **Congas** — Tall Afro-Cuban hand drums, tuned in pairs (tumba/conga/quinto).
- **Bongos** — Smaller, higher hand drums. Latin jazz, Santana.
- **Timbales** — Shallow metal drums with cowbell. Salsa and Latin rock.
- **Cowbell** — Yes, more cowbell. Mambo bell patterns, Grand Funk Railroad.

**In Sozawen.** The drum engine ships **18 physically-modeled drum sounds** across kick, snare, hats, toms, crashes, rides, splashes, and chinas — including velocity nonlinearity and B20/B8 cymbal alloy differentiation documented in our cymbal acoustics research. The **Drum Pattern Generator** has presets for jazz, rock, metal, funk, Latin, hip-hop, country, and more genres with verse/chorus/bridge section variations. You can select **Zildjian K vs A**, wood vs metal snares, and different kick characters in the Instruments Panel, and each uses its measured modal signature. Auxiliary percussion is its own lane — shaker, tambourine, and conga patterns auto-lock to the main kit's swing value.

**Common mistakes:**
- Overmuffling the kick. A little ring is a feature, not a bug. Dead kicks sound like cardboard boxes.
- Hi-hats too loud in the mix. They'll shred ears on headphones. Pull them down 3-6 dB below where instinct says.
- Programming every hi-hat at identical velocity. Real drummers accent beats. Vary velocity or the loop sounds machine-sequenced.
- Using one snare for every song. The snare changes the genre. Swap it.
- Ignoring the room. A great drum take is half the room it was recorded in. Room mics matter.

**Going deeper.** Cymbals are **nonlinear oscillators** — strike harder and new modal frequencies appear, not just more of the same. This is why a velocity layer sampler always sounds slightly fake: it's switching between snapshots, not evolving continuously. Our cymbal model solves this with physical modal synthesis. Snare wires are a **coupled resonator** — the bottom head vibrates, the wires vibrate against it, and the top head's strike energy feeds back into the whole system. Loosen the wires and the drum becomes a tom; tighten them fully and you get that tight crack. Historical note: the modern drum kit was assembled in the 1920s so one player could replace the three-person rhythm section of a marching band — which is why it's called a **trap set** (from "contraption"). Every innovation since has been adding colors to that original idea."""
    },

    "keyboards_piano": {
        "title": "Keyboards, Piano & Synths",
        "category": "Instruments",
        "content": """Play a `C` major chord on a grand piano, a Rhodes, a Hammond B3, and a Moog, and you've played **four completely different instruments**. Same three notes, four different songs. Keyboards are the Swiss Army knife of music — each type was designed for a specific sonic job.

**Acoustic pianos:**
- **Grand piano** — Horizontal frame, strings run away from the player, hammers fall by gravity. 9' concert grands for halls, 5-7' baby/parlor grands for studios. Full dynamic range, long sustain, the reference instrument for everything. Steinway D, Bösendorfer 290, Yamaha C7.
- **Upright** — Vertical frame, springs return hammers. Compact, slightly compressed tone, warmer top end. Living room piano. Honky-tonk uprights have a loose tack sound by design.

**Digital pianos** sample or model real pianos. Weighted hammer-action keys matter more than sample quality for feel. Best ones feel indistinguishable from uprights to anyone but pros.

**Electric pianos (EPs):**
- **Rhodes Mark 1 and Mark 2** — Metal tines struck by hammers, amplified electromagnetically. Bell-like, warm, chorus-y through a vibrato. "Riders on the Storm," Herbie Hancock's "Chameleon," half of all '70s soul ballads.
- **Wurlitzer 200A** — Metal reeds (not tines), reedier and barkier than Rhodes. "What'd I Say," Supertramp "Logical Song," Ray Charles' whole right hand.
- **Clavinet (Hohner D6)** — Strings plucked like a tiny guitar, very percussive. "Superstition" is a Clav through a wah.

**Hammond B3 organ + Leslie speaker** — Nine drawbars that add harmonic partials by the sinewave. Fed through a **rotating Leslie cabinet** (spinning drum for lows, rotating horn for highs) that creates the iconic Doppler swirl. Jazz (Jimmy Smith), gospel, rock (Deep Purple "Highway Star," Procol Harum "Whiter Shade of Pale"). The Leslie has two speeds: slow (chorale) and fast (tremolo). Switching between them mid-song is half the expression.

**Synthesizers (synths):**
- **Analog subtractive** — Oscillators (saw, square, triangle) fed through a resonant low-pass filter. Fat, warm, slightly unstable. Moog, Prophet-5, Juno-106. Bass lines, leads, classic pads.
- **Digital** — All-digital oscillators and filters. Cleaner, more predictable, more extreme. D-50, M1, modern softsynths.
- **FM (frequency modulation)** — One oscillator modulates another's frequency. Glassy, metallic, bell-like. Yamaha DX7. "Take On Me" lead, every '80s electric piano patch that wasn't a real Rhodes.
- **Wavetable** — Cycles through a bank of single-cycle waveforms over time. Evolving, morphing, modern. PPG, Waldorf, Serum. Skrillex's whole catalog.

**Roles in the mix:**
- **Pads** — Sustained chords filling the harmonic bed. Soft attack, long release. String synths, Juno pads.
- **Leads** — Single-note melodic voice, usually monophonic, usually on top. Moog lead, sawtooth-and-filter.
- **Basses** — Monophonic low-end. Squares and saws through a resonant filter. TB-303, Minimoog bass.
- **Keys (comping)** — Chordal rhythm instrument. Rhodes, piano, Wurli.

**In Sozawen.** The Instruments Panel has physically-modeled **Steinway D**, **Yamaha CFX**, **Bösendorfer Imperial**, **Rhodes Mark 1**, **Wurlitzer 200A**, **Hammond B3 with virtual Leslie** (adjustable slow/fast speed and ramp time), and a growing synth section. The Piano Roll has a dedicated **sustain pedal lane** that physical models respect — pedaled notes engage sympathetic resonance across other strings, not just a release extension. The Composition Editor's Score view can render keyboard parts as grand staff with proper left/right hand splits.

**Common mistakes:**
- Tracking piano with one mic. Stereo matters — piano is wide. X/Y or spaced pair over the hammers.
- Using an unweighted MIDI controller for piano parts. Your phrasing dies. Velocity curves can't fix it.
- Running a Rhodes dry. A touch of chorus, tremolo, and tube warmth is the sound. Pure clean Rhodes sounds thin.
- Stacking a pad, a Rhodes, and a string synth all at once. Pick two. Otherwise the midrange turns to soup.
- Programming organ with no Leslie movement. Static B3 isn't B3. Automate the speed switch on phrase endings.

**Going deeper.** Piano strings are **inharmonic** — the overtones aren't perfect integer multiples of the fundamental because real strings have stiffness. This is why pianos are tuned with **stretched octaves** (high notes tuned slightly sharp, low notes slightly flat) to match the ear's perception, not math. Electric pianos like the Rhodes are nearly sinewave at low velocity and gain complex metallic overtones at high velocity — which is why **velocity sensitivity isn't optional** in a good Rhodes model; it's the whole instrument. The Hammond B3's tonewheels are physical spinning gears with sine-shaped teeth generating each harmonic — 91 tonewheels for the whole organ — and the small mechanical imperfections are exactly what makes the sound feel alive versus a perfect digital sine bank."""
    },

    "vocals_instrument": {
        "title": "The Voice as an Instrument",
        "category": "Instruments",
        "content": """A great vocal take outranks every production decision on the record. Listen to Whitney Houston's "I Have Nothing," Freddie Mercury's "Somebody to Love," or Jeff Buckley's "Hallelujah" — **the voice is the song**. Everything else is scaffolding.

Your voice is an acoustic instrument made of muscle, cartilage, and resonant cavities. Unlike guitar strings, it **gets better with use and rest, and worse with abuse**.

**Registers (where the sound resonates):**
- **Chest voice** — Full, rich, felt in the chest. Speaking range and low singing. Adele's verses, Johnny Cash.
- **Head voice** — Lighter, resonates behind the eyes and top of skull. Higher notes without strain. Pavarotti on a high `C`.
- **Mixed voice (middle voice)** — Blends both. Sounds like chest but reaches head territory. The secret of pros — Bruno Mars, Ariana Grande, Sam Smith all live here on big notes.
- **Falsetto** — Airy, hollow, disconnected from chest. Only the vocal fold edges vibrate. Prince, Bee Gees, The Weeknd choruses.
- **Whistle register** — Above soprano range, flute-like. Mariah Carey, Ariana Grande outros.

**Vibrato** — The periodic pitch oscillation (usually 5-7 Hz) that gives notes warmth. **Natural vibrato** comes from relaxation of the throat; **forced vibrato** from jaw or diaphragm sounds mechanical. Straight tone (no vibrato) is a choice — indie, Gregorian, some folk.

**Vocal ranges:**
- **Soprano** (`C4-C6`) — Highest female. Mariah Carey, Ariana Grande, Freddie Mercury (yes, his tenor could hit soprano notes).
- **Alto / Mezzo** (`F3-F5`) — Rich female middle. Adele, Amy Winehouse, Lana Del Rey.
- **Tenor** (`C3-C5`) — Highest standard male. Freddie Mercury, Jeff Buckley, Anthony Kiedis.
- **Baritone** (`G2-G4`) — Male middle. Frank Sinatra, Elvis, Eddie Vedder.
- **Bass** (`E2-E4`) — Lowest. Johnny Cash, Barry White, Leonard Cohen (late-career).

**Diction** — The clarity of consonants and vowels. Pop and rock lean on vowels (which carry pitch). Hip-hop and folk demand crisp consonants. **Over-enunciating** sounds robotic; **underenunciating** loses lyrics.

**Breath control** — Singing from the **diaphragm** (belly rising, not shoulders) gives sustained phrases. Poor breath = rushed phrasing, pitch sag at phrase ends, vocal fatigue.

**Harmonies:**
- **Thirds** — Sweet, pop-friendly. Above or below the melody. Beach Boys, Fleet Foxes.
- **Fifths** — Open, powerful, slightly medieval. Queen, Simon & Garfunkel.
- **Octaves** — Thickening without harmonic change. Simon & Garfunkel "The Sound of Silence" intro.
- **Sixths** — Rich, sophisticated. Jazz and soul. Stevie Wonder.

**Doubling and stacking** — **Doubling** is recording the same part twice and panning slightly; it thickens without sounding like harmony. **Stacking** is layering multiple harmony parts — Queen did 180+ vocal overdubs on "Bohemian Rhapsody."

**Health:**
- **Hydration** — Water reaches vocal folds via systemic hydration, not by drinking during a take. Hydrate hours before.
- **Warmups** — Lip trills, sirens, and gentle scales before any heavy singing. 10 minutes is plenty.
- **Rest** — Voices recover during sleep. Back-to-back gigs without rest guarantees nodules eventually.
- **Avoid** — Whispering strains more than talking. Clearing your throat is micro-trauma. Alcohol and caffeine dehydrate.

**In Sozawen.** The Composition Editor has **vocal range indicators** per track — set singer range (soprano/alto/tenor/bass) and the Score overlay flags notes above or below safely sustainable range. The **Harmony Generator** builds thirds, fifths, sixths, and octaves under or over a lead melody with voice-leading rules. Stacked harmonies route to dedicated lanes in the Piano Roll for independent editing. The Mixer has a **vocal chain preset** (de-esser, compressor, subtle reverb, tape-style saturation) tuned per range. MIDI-driven vocal synthesis isn't the goal — Sozawen is for capturing real vocals — but pitch correction and formant-preserving transposition are first-class tools.

**Common mistakes:**
- Mic too close without a pop filter. Plosives spike the low end. 4-6 inches with a pop filter is the rule.
- Singing a song out of your range. Transpose. Key isn't sacred; your voice is.
- Doubling harmonies instead of the lead. Harmonies panned wide and dry, lead centered with reverb. Don't double backups louder than the melody.
- Tracking a cold voice. The first take after warmup sounds tired because you weren't warm. Warm up fully.
- Comping from takes where pitch is the only consideration. Breath, word shape, and emotion beat pitch-perfect. A great imperfect take beats a flawless tired one.

**Going deeper.** The vocal folds vibrate 100-1000+ times per second depending on pitch — a soprano high `C` is around 1046 Hz, meaning the folds slap together a thousand times every second. That's why hydration, rest, and technique matter: you're running a muscle at speeds no other muscle in your body operates at. **Formants** — the resonance peaks of your vocal tract — are what make a vowel a vowel regardless of pitch. This is why autotune can correct pitch without turning you into a chipmunk: it preserves formants while shifting the fundamental. The oldest instrument in music is the voice, and every other instrument we've ever built is, at some level, an imitation of it."""
    },

    "strings_brass_woodwinds": {
        "title": "Strings, Brass & Woodwinds",
        "category": "Instruments",
        "content": """The orchestral families are the **color palette** of arrangement. A song with just drums, bass, and guitar is a photograph; add a string pad and it's in color; add a horn stab and it's in motion. The Beatles understood this — "Eleanor Rigby" is all strings, "Got to Get You into My Life" is horns, and both are Beatles at their best.

Each family has a **physical principle** that defines its sound.

**Strings (bowed):**
- **Violin** — Highest, brightest. Soloist voice of the orchestra. Range: `G3-E7+`. Vivaldi "Four Seasons," every film score love theme.
- **Viola** — A fifth lower than violin. Warmer, darker, less projection. Range: `C3-E6`. The inner harmony voice. Bartók concerto.
- **Cello** — An octave below viola. Human-voice range, lyrical and powerful. Range: `C2-C6`. Yo-Yo Ma, Bach Cello Suites, "Unfinished Sympathy."
- **Contrabass (double bass)** — Lowest. Orchestral foundation. Range: `E1-C5`. Written an octave above sounding pitch.

Strings can be played **arco** (bowed), **pizzicato** (plucked), **col legno** (wood of bow struck), **sul ponticello** (near the bridge, glassy), **tremolo** (rapid bowing). A string section = multiple players per part, which creates natural chorusing; one player per part sounds like a soloist.

**Brass (buzzed lip vibration into a cup mouthpiece):**
- **Trumpet** — Highest brass. Bright, heroic, cutting. Range: `F#3-D6`. Miles Davis "Kind of Blue," Herb Alpert, mariachi.
- **French horn** — Coiled tubing, mellower and rounder than trumpet. Range: `B1-F5`. Film scores ("Jurassic Park"), Mahler.
- **Trombone** — Slide instead of valves. Warm, expressive, can glide between pitches. Range: `E2-F5`. J.J. Johnson jazz, big band sections, ska.
- **Tuba** — Lowest. Foundation. Range: `D1-F4`. Marching bands, orchestral low brass.

Brass tone comes from **bore taper** and **mouthpiece depth**. Wider bore = warmer (horn, flugelhorn); narrower = brighter (trumpet, trombone). Deep mouthpiece cup = round (horn); shallow = bright (lead trumpet). Mutes (straight, cup, harmon, plunger) reshape the tone — Miles Davis lived on a Harmon mute.

**Woodwinds (reeds or air-across-edge):**
- **Flute** — No reed; air blown across a hole. Bright, airy. Range: `C4-C7`. "Prelude to the Afternoon of a Faun," Jethro Tull.
- **Clarinet** — Single reed, cylindrical bore. Woody, flexible across registers. Range: `D3-C7`. Benny Goodman, klezmer, Mozart concerto.
- **Oboe** — Double reed, conical bore. Nasal, piercing, soulful. Range: `Bb3-G6`. Orchestra tunes to the oboe's `A4`. "Gabriel's Oboe."
- **Bassoon** — Large double reed. Woody, reedy bass. Range: `Bb1-Eb5`. "Rite of Spring" opening, Peter in "Peter and the Wolf" grandpa.
- **Saxophone family** — Single reed, conical bore, metal body. Technically woodwind despite material. **Soprano** (curved or straight, highest), **alto** (the jazz solo voice — Charlie Parker), **tenor** (warmer, Coltrane, Stan Getz), **baritone** (low, punchy, Motown section sound).

**Section vs solo:**
- **Section** writing — Multiple players in close harmony (thirds/sixths, block voicings). Motown horn sections, Gordon Goodwin big band.
- **Solo** writing — One instrument with backing. Every ballad saxophone feature.

**Mic techniques:**
- **Strings** — Mic 2-4 feet above and slightly in front; room mics for section depth. Ribbon mics flatter violins.
- **Brass** — Off-axis at 1-3 feet; directly on-axis is harsh. Ribbon or large-diaphragm condenser.
- **Woodwinds** — Flute at the embouchure hole (not the tip); clarinet and sax at the body, not the bell.

**In Sozawen.** The Instruments Panel includes physically-modeled **violin**, **viola**, **cello**, **contrabass** (with arco/pizz articulations), **trumpet**, **French horn**, **trombone**, **tuba**, **flute**, **clarinet**, **oboe**, **alto sax**, and **tenor sax** models — all using modal synthesis with proper formant behavior per register. The Composition Editor recognizes **divisi** writing (section splits) and the Score overlay renders proper orchestral notation with dynamics, slurs, and articulations (arco, pizz, con sordino).

**Common mistakes:**
- Writing strings in the violin's top octave for a whole arrangement. Ear fatigue. Let the mid-range breathe.
- Doubling strings with a pad synth on the same notes. Washes both out. Pick one or arrange them in different octaves.
- Writing brass parts that never rest. Real players need breath. Leave space.
- Picking the wrong sax. Alto sits above the vocal; tenor sits with the vocal; bari sits under. Choose by register.
- Quantizing orchestral parts to a grid. Kills the phrasing that makes them feel alive. Humanize or play live.

**Going deeper.** The three families differ in **how they excite the air column**: strings have a continuously-excited oscillator (bow friction), brass has a lip-valve generating a buzz that the tube filters, and woodwinds have either a reed (single or double) or a turbulent air jet (flute). This is why brass can play loud cleanly, woodwinds have complex formant colors, and strings have the widest dynamic range of any acoustic instrument. **Stradivarius violins sound unique** not because of a secret varnish (myth) but because of **300-year-old spruce that has micro-crystallized**, combined with carved thickness graduations refined over decades of play. We can model the spectrum; we cannot age the wood. In arrangement terms, remember that the orchestra was built over **four centuries** specifically to cover every pitch, every dynamic, and every timbre a composer could want — which is why adding one well-chosen orchestral element can transform a pop song more than adding ten synths."""
    },

    "electronic_production": {
        "title": "Electronic Music Production",
        "category": "Instruments",
        "content": """You hear that pulsing, hypnotic bass in a house track — the one that breathes in and out like the song itself is alive. That breathing isn't magic. It's a bunch of producers building the same handful of tricks on top of each other for forty years, and once you see the pieces, you can build them too.

**Electronic music** is music made primarily from synthesized or sampled sounds, usually built around a drum machine pulse rather than a live drummer. The foundation of most dance music is the **four-on-the-floor** — a kick drum hitting every beat (1, 2, 3, 4) like a heartbeat you can dance to. House, techno, and trance all live on this pulse. Drum and bass and dubstep break the pulse instead, putting the kick and snare in unexpected places.

Around that pulse you layer a few archetypal elements. A **bassline** locks to the kick — in house it "rolls" in eighth or sixteenth notes; in dubstep it moves like a wounded animal. **Stabs** are short, chord-shaped hits (usually a synth brass or piano) that punch on the offbeat. **Pads** are long, slow chord washes that fill the background. And the **drop** is the moment everything crashes back in after a buildup — the payoff the whole track is arranged around.

The famous "pumping" sound comes from **sidechain compression** — the kick drum ducks the bass and pads every time it hits, so the track breathes. Daft Punk's *One More Time*, Eric Prydz's *Opus*, pretty much any modern house track — that pump is sidechain.

The core vocabulary: **BPM** (tempo — house sits around 122-128, techno 125-135, DnB 170-180, trap 140 half-time, lofi 70-90), **arpeggiator** (turns a held chord into a rolling pattern), **LFO** (a slow wave that wobbles a parameter — the "wub" of dubstep is LFO on a filter), **filter sweep** (opening a lowpass filter during a buildup), **risers** and **downlifters** (transition FX), **FX sends** (reverb and delay on separate buses).

Genres in one line each. **House** — 4-on-floor, soulful, 122-128 BPM, warm. **Techno** — darker, more machine-like, minimal. **Trance** — euphoric, long breakdowns, supersaw leads (think Above & Beyond). **Drum & Bass** — 170+ BPM, breakbeat drums, rolling reese bass. **Dubstep** — 140 half-time, wobble bass, Skrillex/Rusko. **Trap** — 808 sub-bass, triplet hi-hats, half-time feel. **Lofi** — slow, warm, tape-saturated, jazz chords over boom-bap drums.

**Synthesis basics.** There are four main flavors. **Subtractive** (start with a rich waveform, carve it with filters — the classic Moog/analog sound, used in almost everything). **FM** (frequencies modulating each other — bell-like, metallic, the DX7 electric piano sound). **Wavetable** (scan through a library of waveshapes — the modern Serum/Vital sound, every pop song since 2015). **Additive** (build tones by stacking pure sine waves — rare but precise).

**In Sozawen.** The drum generator is your rhythmic engine — every genre preset (house, techno, DnB, dubstep, trap, lofi) pre-configures the kick pattern, hat density, and section flow so you're not starting from a blank grid. The physical modeling synths cover the acoustic layer when you want a real `Taylor Dreadnought` or `Les Paul` under your synth stack — Odesza, Bonobo, and ODESZA-style hybrid electronic is exactly this blend. For pure-synth work, the synthesis engine handles subtractive and wavetable patches; route a kick bus to trigger sidechain on your `bass` and `pad` buses to get the pump. Sample-based hip-hop and lofi producers chop drum breaks in the composition editor and layer the `acoustic_bass` body profile for the upright-bass feel Dilla and Nujabes built their sound on.

**Common mistakes:**
- Using the same kick drum as everyone else — your kick is the signature, sculpt it
- No low-end discipline — muddy mixes come from bass and kick fighting for the same 60-100Hz space
- Overusing sidechain on everything — it loses meaning when nothing is stable
- Ignoring automation — a static synth for 4 minutes is why your tracks feel flat
- Building drops before you have a groove — the drop only hits if the verse breathes

**Going deeper.** Pros think in **frequency zones** — kick at 60Hz, sub-bass at 40-80Hz, mid-bass at 100-300Hz, each occupying its own shelf. Parallel compression on drums glues them. **OTT** (an upward/downward multiband compressor) is the "modern" sound on leads and bass. For trance and big-room, **supersaw** stacks (7 detuned saws) are the lead signature. **Granular synthesis** — chopping samples into tiny grains — is how ambient producers like Jon Hopkins build texture. Mixing references: A/B against Deadmau5 for techno, Disclosure for house, Noisia for DnB."""
    },

    "world_instruments": {
        "title": "World & Folk Instruments",
        "category": "Instruments",
        "content": """When George Harrison put a sitar on *Norwegian Wood* in 1965, Western pop music split in two — before and after. World and folk instruments carry thousands of years of tuning, technique, and feeling, and you can hear a culture in a single note if you listen.

These instruments come from specific places and specific musical traditions. You don't need to become an expert to use them, but you do need to understand what they're **for** — because using a sitar as background texture when the scale underneath is a major triad is the sonic equivalent of a tourist taking a selfie at a funeral.

**The plucked strings.** The **sitar** (North India) has sympathetic strings that ring in drone behind the melody — used in Indian classical to play **ragas** (scale-mood combinations, each tied to a time of day and emotion). The **oud** (Middle East, North Africa) is fretless, warm, and plays **maqams** (modes built around microtonal intervals — the quarter-tones between our piano notes). The **bouzouki** (Greece, Ireland) is bright and trebly — Greek rembetiko and Irish folk both claim it. The **mandolin** (Italy → American bluegrass) is tuned in fifths like a violin and tremolo-picked for that shimmering Chris Thile sound. The **banjo** (West Africa → Appalachia) is rhythmic and percussive — Earl Scruggs three-finger rolls vs. clawhammer old-time are two different instruments that happen to share a body. The **ukulele** (Hawaii, via Portugal) is four nylon strings, cheerful by default. The **dulcimer** (Appalachia) sits on your lap, tuned to a drone — modal, trance-like. The **kora** (West Africa, Mali/Senegal) is a 21-string harp-lute — Toumani Diabaté plays patterns that feel both ancient and mathematical.

**The winds.** The **didgeridoo** (Aboriginal Australia) is a drone instrument played with circular breathing — one sustained note with shifting overtones and rhythmic tonguing. The **shakuhachi** (Japan) is an end-blown bamboo flute used in Zen meditation — breathy, pitch-bending, spacious. The **erhu** (China) is a two-string bowed instrument — vocal, mournful, the sound of Chinese cinema.

**The drums.** The **tabla** (North India) is a pair of hand drums — a metal-paste spot on the head gives it that talking, melodic quality. Tabla players speak syllables (**bols** — "dha", "tin", "na") that map to specific strokes. The **djembe** (West Africa) is a goblet-shaped hand drum with three core tones — bass, tone, slap.

**Scale systems they imply.** Ragas are more than scales — they're melodic grammars with required phrases. Maqams use microtones your guitar can't play without bending. Celtic tunes live in **Mixolydian** and **Dorian** modes. Appalachian music often sits in modal tunings where major/minor blur.

**In Sozawen.** The physical modeling engine focuses on Western string instruments (`Taylor Dreadnought`, `Martin D-28`, `Gibson J-45`, `Classical`, `Strat`, `Les Paul`, `Acoustic Bass`). For world and folk tones, the `Classical` nylon body gets you close to oud and bouzouki territory — both are nylon/gut-strung with warm bodies. The drum generator's percussion voices can cover djembe-style hand drums; lay them under a groove instead of a kit. For raga and maqam work, use Sozawen's composition editor scale settings — modal scales (Dorian, Phrygian, Mixolydian) approximate many ragas, and the tuning tools let you bend individual notes for maqam microtones. Layer these with the `mic` selection in the Instruments Panel for recorded performances, and keep the mix spacious — world instruments need reverb and breath, not dense pop production.

**Common mistakes:**
- Using a sitar drone over a major key chord progression — the raga doesn't work that way, and it sounds tourist
- Treating the djembe like a Western kit — it's tonal, not just rhythmic
- Quantizing hand percussion to a grid — tabla and djembe live in the micro-timing between beats
- Putting world instruments on every track for "vibe" — less is infinitely more
- Ignoring the tuning — an oud sample pitched to 440Hz equal temperament has been stripped of what makes it an oud

**Going deeper.** If you're serious about using these sounds, learn the parent tradition — even just listening. Ravi Shankar for sitar. Toumani Diabaté for kora. Anouar Brahem for oud. Zakir Hussain for tabla. Watch Rhiannon Giddens show you what the banjo was before minstrelsy. Producers who do this well: Nitin Sawhney, Four Tet, Shpongle, Bonobo on *Black Sands*, Peter Gabriel's *Passion*. The opposite — Enigma — turned sampled Gregorian chant into wallpaper, and that's the trap to avoid. Record live players when you can; sample libraries are a starting point, not a finish line."""
    },

    "microphone_guide": {
        "title": "Microphone Types & Selection",
        "category": "Instruments",
        "content": """Hand a singer three microphones and you'll get three different singers. A **mic** doesn't just record sound — it chooses which parts of the sound to hear and which to ignore. That choice is the first creative decision in every recording, and it matters more than the preamp, the room, or the plugin you put on it later.

There are three main families of microphones, distinguished by how they convert sound into electricity.

**Dynamic mics** use a moving coil in a magnetic field — like a tiny speaker in reverse. They're tough, cheap, handle loud sources without distorting, and reject room sound. The **Shure SM57** is on every snare drum and guitar cab in recorded music history. The **SM58** is its vocal sibling — the same capsule with a ball windscreen, used by everyone from Bono to your local karaoke bar. The **Electro-Voice RE20** is the broadcast standard — deep male voices, kick drum, bass cabs. Dynamics are **less sensitive**, which is a feature, not a bug, in loud environments.

**Condenser mics** use a charged diaphragm and need external power (**phantom power**, +48V). They're far more sensitive and capture detail dynamics miss. **Large-diaphragm condensers** (LDCs) — Neumann U87, AKG C414, Audio-Technica AT4040 — are your lead vocal and acoustic room mics. They sound "bigger" and flatter the voice. **Small-diaphragm condensers** (SDCs, "pencils") — Neumann KM184, Shure SM81, Rode NT5 — are for accuracy: overheads, acoustic guitar, orchestral work, hi-hats. SDCs tell the truth. LDCs tell a flattering version of the truth.

**Ribbon mics** use a thin aluminum ribbon in a magnetic field. They're fragile, warm, and dark — they roll off high frequencies naturally. The **Royer R-121** is the modern standard on guitar cabs — it tames harsh amp fizz. The **Coles 4038** is the BBC classic — on drum overheads it sounds like 1968 in a box. **Never put phantom power on a vintage ribbon** without checking — it can destroy the ribbon element.

**Polar patterns** — where a mic listens from. **Cardioid** hears the front, rejects the back (most vocal mics). **Omnidirectional** hears everything equally — great for room tone and realism, useless for isolation. **Figure-8** hears front and back, rejects sides — the basis of Blumlein stereo recording and essential for mid-side techniques. **Supercardioid** is a tighter cardioid with slight rear pickup (Beyer M88 on drums). **Shotgun** is hyper-directional — film and TV dialogue.

**What each excels at.** **Vocals** — LDC condenser (studio) or SM7B/SM58 (live, loud, untreated rooms). **Acoustic guitar** — SDC condenser aimed at the 12th fret, plus LDC on the body. **Electric guitar cab** — SM57 on the grille, R-121 a few inches back for warmth. **Kick drum** — RE20 or dedicated kick mic (Shure Beta 52) inside, D6 for click. **Snare** — SM57 on top, smaller condenser or another 57 underneath. **Overheads** — matched pair of SDCs (pencils) or LDCs for wider character. **Bass amp** — RE20 or a large dynamic. **Piano** — two SDCs inside, or LDCs further back for room.

**Price tiers.** Entry ($100-300) — SM57, SM58, SM7B (yes, really), AT2020, Rode NT1. Mid ($500-1200) — AKG C414, Rode NT2-A, Shure KSM series. Pro ($1500+) — Neumann U87, Sony C-800G, vintage tube mics. Spending more above the mid tier is taste, not improvement.

**In Sozawen.** The Instruments Panel mic selection lets you pick the capture character for each body profile — pair a `Taylor Dreadnought` with a small-diaphragm condenser for that sparkling Nick Drake fingerpicked clarity, or run the same guitar through a ribbon emulation for Norah Jones warmth. A `Martin D-28` through a condenser in front of the sound hole is the classic bluegrass/singer-songwriter capture. For the `Les Paul` and `Strat` body profiles, the `SM57 on grille + R-121 back` combo is baked into the amp chain presets (`marshall`, `fender`, `mesa`). Bass bodies (`Precision`, `Jazz`, `StingRay`, `Rickenbacker`) default to a DI + dynamic blend feeding `ampeg_svt` or `darkglass`. In the drum generator, overhead pairs are modeled as SDCs by default — switch to LDC character for a John Bonham room-sound vibe.

**Common mistakes:**
- Using a condenser on a loud guitar amp up close — it'll distort or sound harsh
- Singing off-axis from a cardioid — every angle away from the capsule loses top end
- Ignoring the room — a $3000 mic in a bad room sounds worse than a $100 mic in a good one
- Matching the wrong mic to the source — SDC on a screaming rock vocal will shred your ears
- Forgetting phantom power kills ribbons — check before you hit +48V

**Going deeper.** Proximity effect — cardioids boost bass when you get close to them. Radio DJs use it intentionally. Pop filters kill plosives ("p" and "b" bursts). For acoustic guitar, try **X/Y** (two SDCs at 90 degrees, capsules touching) for mono-compatible stereo. **Blumlein pair** (two figure-8s at 90 degrees) is the most realistic stereo image humans have discovered. **Mid-side** (cardioid + figure-8, decoded later) gives you adjustable stereo width after the fact. On vocals, **distance is tone** — 2 inches is intimate and bass-heavy, 12 inches is neutral, 3 feet is the room."""
    },
    # ═══════════════════════════════════════════════════════════════
    # HARDWARE & STUDIO
    # ═══════════════════════════════════════════════════════════════

    "audio_interfaces": {
        "title": "Audio Interfaces — Choosing & Using",
        "category": "Hardware",
        "content": """Your computer's built-in audio jack was never meant for music. An **audio interface** is a small box that sits between your microphones, instruments, and the computer — converting the analog world into digital samples the DAW can actually work with, then converting back out so you can hear what you did.

At the heart of every interface are two converters: the **A/D** (analog-to-digital) that captures your sound, and the **D/A** (digital-to-analog) that plays it back. Everything else — preamps, headphone amps, MIDI jacks — is stuff bolted around those two chips. The quality of those converters, and the cleanliness of the preamps feeding them, is most of what you're paying for.

**Key vocabulary:** **Sample rate** (how many times per second the signal is measured — `44.1 kHz` for CD, `48 kHz` for video, `96 kHz` for fussy purists). **Bit depth** (how precisely each sample is measured — `24-bit` is the tracking standard, `32-bit float` on newer interfaces is effectively clip-proof). **Preamp** (the gain stage that brings a quiet mic up to line level). **Phantom power / +48V** (the DC voltage condenser mics need — a switch on the interface). **Latency** (the round-trip delay between you playing and hearing it — anything over ~10ms feels weird). **Direct monitoring** (routing input straight to the headphone jack before the computer, so you hear yourself with zero delay). **Driver** (the software layer the DAW talks to — `Core Audio` on Mac is native; on Windows you want `ASIO`, avoid `DirectSound` and `MME` for tracking).

**In Sozawen.** Any interface with a working Core Audio, ASIO, or DirectSound driver will show up automatically — pick it in the audio settings panel and set your buffer size. Smaller buffers (`64`, `128` samples) mean lower latency for tracking; larger buffers (`512`, `1024`) let you run more plugins while mixing. Sozawen's built-in physical instrument models don't care about sample rate the way sample libraries do, so `48 kHz` is fine forever.

**Common mistakes:**
- Buying more inputs than you'll ever use — a solo songwriter rarely needs more than two.
- Leaving `+48V` on when plugging in a ribbon mic. It can kill it. Always turn phantom off before swapping mics.
- Using the cheapest USB cable you can find on a `USB 2.0` interface, then blaming the interface for dropouts.
- Monitoring through the DAW at a high buffer while tracking — use direct monitoring or drop the buffer to `128`.
- Running the interface through a USB hub. Always plug directly into the computer.

**Going deeper.** Tier one (under $150): **Focusrite Scarlett Solo / 2i2**, **PreSonus AudioBox**. Two clean inputs, fine preamps, you will not outgrow these for years. Tier two ($200-400): **Audient iD14**, **MOTU M4**, **SSL 2+** — noticeably better converters and preamps, often with genuine console-grade circuits at this price. Tier three ($500-1500): **Universal Audio Apollo Twin X**, **RME Babyface Pro FS**, **MOTU UltraLite** — the Apollo adds onboard DSP for Unison preamp modeling; the RME has driver stability that's basically legendary. Tier four ($2000+): **Apogee Symphony**, **Universal Audio Apollo x8p**, **RME UFX** — multi-channel rigs for tracking full bands.

USB-C is fine for up to around 8 inputs at `96 kHz`. Thunderbolt matters when you're tracking a drum kit with 16 mics or running heavy DSP. For a bedroom setup, USB is perfect — spend the Thunderbolt difference on a better microphone or room treatment."""
    },

    "monitors_headphones": {
        "title": "Studio Monitors & Headphones",
        "category": "Hardware",
        "content": """Your mixes only sound as good as the thing you're listening on. **Studio monitors** are speakers designed to be boring — flat, honest, unflattering — so the decisions you make on them translate to other systems. Consumer speakers hype the bass and smooth the highs; if you mix on those, your track will sound thin and harsh everywhere else.

Monitors come in two families. **Nearfield monitors** sit 3-5 feet from your head and are what you want in a bedroom or small room — the direct sound from the speaker reaches you before the room's reflections do, so you're hearing the speaker, not the room. **Midfield monitors** live 6-10 feet out in larger, treated rooms. For 95% of indie musicians, nearfields are the answer.

**Key vocabulary:** **Active** (amplifier built in — what nearly everyone buys now). **Passive** (needs a separate amp). **Ported** (has a hole that extends bass response — louder, boomier). **Sealed** (no port — tighter, less deep). **Open-back** vs **closed-back** headphones (open sound bigger and more natural but leak sound everywhere; closed isolate but can feel claustrophobic and hype the bass). **Sweet spot** (the tight triangle where the speakers and your head form an equilateral triangle — this is where the stereo image actually works).

**In Sozawen.** Sozawen's built-in metering and reference track A/B feature will reveal when your room is lying to you — if your mix sounds great on monitors and awful on headphones, it's almost always the room, not the mix. Load a commercial reference in the same genre, flip back and forth, and trust the headphones when the low end disagrees.

**Common mistakes:**
- Buying big 8-inch monitors for a tiny bedroom. The room can't handle the bass and you'll mix with phantom problems that aren't in the recording.
- Mixing only on headphones, or only on monitors. You need both.
- Setting monitor levels too loud. Around `75-85 dB SPL` at the listening position is the honest zone — louder than that and the Fletcher-Munson curve flatters everything.
- Pointing the tweeters at your belly button instead of your ears.
- Putting monitors on the desk with no isolation pads — the desk resonates and smears the low-mids.

**Going deeper.** Entry nearfields ($300-500/pair): **Yamaha HS5**, **Kali LP-6 V2**, **JBL 305P MkII**, **PreSonus Eris E5**. Kali punches way above its price. Mid tier ($700-1200/pair): **Yamaha HS8**, **KRK Rokit 8 G5**, **Adam T7V**, **Focal Alpha 65 Evo**. Pro ($1500-3000/pair): **Adam A7X / A77H**, **Focal Shape 65**, **Neumann KH 120**. Reference ($3000+/pair): **Genelec 8040 / 8050**, **Dynaudio Core 7**, **Barefoot MM27**.

Headphones split by job. For **mixing**: **Sennheiser HD600 / HD650** (open-back, the honest standard, $350-450), **Beyerdynamic DT880 / DT990** ($200-350), **AKG K240** ($80 — cheap and trustworthy for the price), **Audeze LCD-X** ($1200+ if you have it). For **tracking**: closed-back only, so the click track doesn't bleed into the mic. **Sony MDR-7506** ($100, industry standard for a reason), **Beyerdynamic DT770** ($180), **Sennheiser HD280 Pro** ($100).

The room is half your monitor. A $300 pair in a treated room will out-mix a $3000 pair in a bare bedroom. Budget accordingly — when in doubt, treat the room before upgrading the speakers."""
    },

    "cables_connections": {
        "title": "Cables & Connections",
        "category": "Hardware",
        "content": """Cables are the plumbing of a studio. They're invisible until one fails at 2am, and then they're the only thing in the room. Understanding the three or four connector types you'll actually encounter saves hours of troubleshooting and prevents the mystery hum that ruins otherwise perfect takes.

The big split is **balanced vs unbalanced**. A balanced cable carries the signal on two wires — one in phase, one flipped — and the gear at the end subtracts them. Any noise picked up along the way appears on both wires and cancels out. Unbalanced cables have one signal wire plus a shield; the shield picks up hum from everything nearby, and you just have to hope the run is short.

**Key vocabulary:** **TS** (tip-sleeve, two contacts, unbalanced `1/4"` — guitar cables). **TRS** (tip-ring-sleeve, three contacts, balanced `1/4"` OR stereo — looks identical to TS, but the extra ring is the giveaway). **XLR** (three-pin round connector, balanced, the standard for microphones and pro line gear). **RCA** (the red/white consumer jacks — unbalanced, `-10 dBV` level, for turntables and home stereo). **SpeakON** (twist-lock connector for passive speaker cables — fat wire, high current, never for line signals). **DIN / 5-pin MIDI** (the old hardware MIDI port, still on synths). **Signal levels:** mic level (~`-50 dBu`, tiny), instrument level (~`-20 dBu`, medium, high-impedance), line level (`+4 dBu` pro or `-10 dBV` consumer, hot).

**In Sozawen.** Sozawen doesn't care what cable you used — but if your recording has a steady `60 Hz` hum (in the US) or `50 Hz` (Europe) visible in Sozawen's spectrum analyzer as a spike at the wall frequency, it's almost always a cable, a ground loop, or an unbalanced run too close to a power supply.

**Common mistakes:**
- Plugging a guitar into a line-level input. The impedance mismatch kills your tone — use a DI box or the interface's `Hi-Z` / instrument input.
- Using a speaker cable as an instrument cable (or vice versa). Speaker cables have no shield; instrument cables can't handle amp current. Both sound bad, one can fry gear.
- Long unbalanced runs. Past about 20 feet, unbalanced TS picks up every fluorescent light in the building.
- Daisy-chaining power strips and wall-warts until you've got a ground loop hum. Plug all audio gear into the same outlet or power conditioner.
- Buying `$200` cables for a bedroom studio. The law of diminishing returns hits hard past `$20-30` per cable for normal lengths.

**Going deeper.** Cable quality matters most at the **endpoints** — the connector and the solder joint are where cables die. **Mogami**, **Canare**, **Gotham**, and **Van Damme** are the boring pro standards; ready-made **Hosa** cables are fine for practice, iffy for permanent installs. Beware of cables with molded strain reliefs you can't repair — when they fail, the whole cable is trash.

Length limits: balanced XLR is happy at `100+ feet`; balanced TRS to `50+ feet`; unbalanced TS should stay under `20 feet`; USB `2.0` dies past `15 feet` without a powered hub; HDMI gets unreliable past `25 feet`.

Ground loops — the symptom is a constant hum that gets louder when you touch the guitar strings. Fixes, in order: (1) plug all audio gear into one outlet, (2) lift the ground on one piece of gear with a Hum X or ground-lift adapter (never on a 3-prong safety ground of something with tubes inside), (3) add a **Jensen Iso-Max** or **Radial J-Iso** isolation transformer on the offending line. Don't cut ground pins off plugs. That's how people die."""
    },

    "acoustic_treatment": {
        "title": "Room Treatment & Acoustics",
        "category": "Hardware",
        "content": """The room you're mixing in is part of your monitor chain whether you treated it or not. Untreated rooms lie — they boost certain frequencies where the walls pile up standing waves, cut others where they cancel, and smear transients with early reflections. You mix to compensate, and the mix falls apart the moment it leaves your room.

Good news: you don't need a professional studio to make honest decisions. You need to kill the **early reflections** off the walls near your speakers, tame the **bass modes** in the corners, and stop the **flutter echo** pinging between parallel surfaces. That's it. That's 80% of the job, and it can be done for a few hundred dollars in a bedroom.

**Key vocabulary:** **Early reflections** (sound from the monitors bouncing off the nearest walls and hitting your ears 1-15ms after the direct sound — the brain can't separate them, so the stereo image smears). **First-reflection points** (the spots on each wall where a reflection would bounce directly into your listening position). **Standing waves / room modes** (bass frequencies where the wavelength matches a room dimension and piles up — a `10-foot` wide room has a big bump around `56 Hz`). **Broadband absorption** (panels that soak up everything above ~`250 Hz` — what 2-4" of Rockwool does). **Bass trap** (a thicker or tuned absorber for low frequencies, usually in corners). **Diffusion** (scattering the sound instead of killing it — keeps the room feeling alive).

**In Sozawen.** Sozawen's frequency analyzer and reference-track A/B tool are the fastest way to diagnose a bad room. Play a commercial track in your genre through your monitors, then on headphones. If the low end disappears or doubles on monitors, you have bass problems. If the stereo image is narrower on monitors, you need first-reflection treatment.

**Common mistakes:**
- Putting foam squares everywhere and thinking the room is "treated." Thin foam only absorbs above ~`1 kHz` — the room still lies in the low-mids where mixes actually live.
- Treating the wall behind the listening position before the walls beside the monitors. First reflections come from the sides first.
- Ignoring the corners. Bass traps in corners do more than any other single treatment.
- Over-deadening the room. Zero reflections feels suffocating and kills the musicality. Leave some life.
- Mixing near a window. Glass reflects everything above `500 Hz` like a mirror.

**Going deeper.** **The mirror trick** for finding first-reflection points: sit in your mixing position, have a friend slide a small mirror along each side wall. Any spot where you can see a monitor tweeter in the mirror is a first-reflection point. That's where a `2'x4'` broadband panel goes.

**Broadband panels.** DIY with **Rockwool Rockboard 60** or **Owens Corning 703** (rigid mineral wool, 2-4" thick), wrap in breathable fabric, hang on walls. A 2'x4' panel costs about `$40` in materials. Prebuilt from **GIK Acoustics** (the pro favorite, $100-150/panel), **Primacoustic Broadway** (easy mount, $80-120), or **Auralex** (fine for the price but avoid their thin foam).

**Bass traps** go in the corners — floor-to-ceiling if you can. Two 4-foot **GIK Soffit Traps** per corner will transform a small room. Tighter rooms benefit more from **membrane / tuned traps** that target specific mode frequencies.

**Diffusion** is for the back wall, behind the listening position. **RPG Skyline**, **GIK Gridfusor**, or a bookshelf full of mismatched books genuinely works.

When you can't treat the room — rental, landlord, toddler — the headphone fallback is real. A pair of **Sennheiser HD600** and Sozawen's reference-track workflow will get you 90% there while you save for the panels."""
    },

    "acoustic_guitar_tones": {
        "title": "Acoustic Guitar Brands & Their Sound",
        "category": "Instruments",
        "content": """You can close your eyes during James Taylor's *Fire and Rain* and know it's a Martin. You can hear Taylor Swift's first record and know it's a Taylor. That's not marketing — it's wood, bracing, and a hundred-year argument between two companies in Pennsylvania and California about what an **acoustic guitar** should sound like.

An acoustic guitar's sound comes from three things: the **wood** (what kind, how old, how dry), the **bracing** (the internal skeleton that shapes how the top vibrates), and the **body shape** (how much air is inside and where it moves). Brand character is the sum of those choices, refined for decades.

**Martin** invented the modern steel-string acoustic in the 1800s. The sound is **warm, thick, and woody** — mids that sit under a vocal, a low end you feel in your chest. The **D-28** (dreadnought, East Indian rosewood back/sides, Sitka spruce top) is the bluegrass and folk standard — Hank Williams, Johnny Cash, Dylan. The **D-18** swaps rosewood for mahogany — drier, punchier, less piano-like sustain (think early Beatles acoustic tracks, Tony Rice). The **OM-28** (Orchestra Model) is smaller, balanced, perfect for fingerpicking (James Taylor's entire career).

**Taylor** (founded 1974 in California) is the modern counterpart — **bright, clear, articulate**, with a clean piano-like top end. Taylors record easily and cut through a mix. The 814ce is the flagship — rosewood/spruce dreadnought with Taylor's V-Class bracing. Pop and country rhythm players live on Taylors — Taylor Swift's early stuff, Jason Mraz, John Mayer's *Continuum* rhythm parts. Some old-school players find them "too clean" — that's the point.

**Gibson** acoustics are the third voice — **punchy, midrange-forward, woody with a vocal quality**. The **J-45** (round-shouldered dreadnought, mahogany back/sides) is the singer-songwriter's guitar — Bob Dylan, Noel Gallagher, Sheryl Crow. It doesn't have the piano sustain of a Martin or the shimmer of a Taylor — it has **grunt**. The **Hummingbird** is the flashier cousin (maple or mahogany, decorated). The **Dove** is even flashier, with more bass.

**The other voices.** **Takamine** (Japan) built its name as a stage guitar — bright, well-amplified, reliable pickup systems. **Yamaha** makes possibly the best value in acoustics — the FG800 under $300 punches way above its price, and high-end LLs/LSs compete with Martins at half the cost. **Breedlove** (Oregon) has a distinct modern sound — asymmetric bracing, bright and open. **Seagull** (Canada) builds solid-top guitars at budget prices — cedar tops, warmer than spruce.

**Body shape matters as much as brand.** **Dreadnought** (big, square-shouldered) — loud, bass-heavy, the strum guitar. **Orchestra Model / OM / 000** — smaller, balanced, fingerpicker's choice. **Parlor** — small, midrange-focused, old-timey and blues. **Jumbo** — huge and bassy (Gibson J-200, Elvis's guitar). The same Taylor in an OM vs. a dreadnought sounds like two different instruments.

**In Sozawen.** The physical modeling engine has three acoustic body profiles that cover the core voicings: `Taylor Dreadnought` (bright, clear, modern — your pop and indie rhythm voice), `Martin D-28` (warm, rosewood-piano sustain — for folk, bluegrass, singer-songwriter), and `Gibson J-45` (round-shoulder punch, midrange grit — for rock-leaning acoustic and Americana). The `Classical` body covers nylon-string repertoire entirely separately. Brand character in Sozawen isn't a sticker — the BODY_PROFILES model different bracing response, body resonance frequencies, and top-wood stiffness, so a `Martin D-28` strum genuinely decays differently than a `Taylor Dreadnought` strum. Pair with the Instruments Panel mic selection — a condenser on the 12th fret captures `Taylor` clarity; an LDC back from the body captures `Martin` room-warmth.

**Common mistakes:**
- Buying based on brand rather than what you play — a dreadnought for quiet fingerstyle will fight you
- Ignoring string choice — phosphor bronze vs. 80/20 bronze changes the guitar more than most pedals
- Thinking expensive = better for you — a $3000 Martin isn't right if you play rhythm in open tunings
- Forgetting humidity — acoustics crack in dry winters; keep a humidifier in the case
- Mic'ing a dreadnought at the sound hole — it sounds boomy; aim at the 12th fret

**Price tiers.** Beginner ($150-400) — Yamaha FG, Seagull S6, Epiphone DR-100. Intermediate ($500-1200) — Taylor 100/200 series, Martin X/Road series, Gibson G-45. Pro ($1500-3500) — Taylor 300-800 series, Martin HD-28/D-18, Gibson J-45 Standard. Vintage/boutique ($4000+) — 1940s-60s Martins, Collings, Santa Cruz, Bourgeois.

**Going deeper.** Solid vs laminate tops — solid wood opens up over decades; laminate stays where it is. **Scalloped bracing** (carved out) is lighter and more responsive, **non-scalloped** is stiffer and punchier. Rosewood (Brazilian > East Indian > Madagascar) vs. mahogany vs. maple back/sides shape the overtones. Record two mics if you can — SDC on the neck, LDC at the body — and blend to taste."""
    },

    "electric_guitar_tones": {
        "title": "Electric Guitars & Their Sound",
        "category": "Instruments",
        "content": """Put six electric guitars in a room and play the same riff on each one. You won't hear "guitar" six times — you'll hear six different instruments having a conversation. A Stratocaster will sparkle, a Les Paul will growl, a Tele will bark, and a Rickenbacker will chime like a bell. Every rock song you love was shaped by the specific guitar that made it.

An **electric guitar** is mostly defined by three things: **pickups** (magnets that translate string vibration into signal), **wood** (body and neck, affecting resonance and sustain), and **scale length** (distance from nut to bridge, affecting string tension and tone). Brand character is the decades-long interaction of those choices.

**Fender Stratocaster** — three **single-coil** pickups, alder or ash body, maple or rosewood neck, 25.5" scale. **Bright, glassy, quacky** (especially positions 2 and 4, the "in-between" tones). Used by everyone from Jimi Hendrix to David Gilmour to John Mayer to Eric Johnson. The 5-way switch and tremolo arm are signatures. Cleans sing, overdrive stays articulate. Downside — can sound thin through heavy gain.

**Fender Telecaster** — two single-coils, slab body, 25.5" scale, bolt-on maple neck. **Twangy, cutting, percussive** — the bridge pickup is the most aggressive-sounding single-coil ever made. Country (Brad Paisley, Keith Urban), rockabilly, indie (Johnny Marr, Graham Coxon), Bruce Springsteen's entire catalog. The Tele is working-class — simple, loud, reliable.

**Gibson Les Paul** — two **humbucker** pickups, mahogany body with maple top, 24.75" scale. **Warm, thick, sustained** — humbuckers cancel noise and push twice the signal of single-coils. Slash, Jimmy Page, Billy Gibbons, Joe Bonamassa. The shorter scale gives strings a slinkier feel and fatter midrange. Heavy (literally — often 9+ pounds).

**Gibson SG** — humbuckers in a thinner, double-cut mahogany body. **Biting, aggressive, fast** — less sustain than a Les Paul, more cutting midrange. Tony Iommi (the entire sound of Black Sabbath), Angus Young, Derek Trucks.

**Gibson ES-335** — **semi-hollow** with a solid center block, humbuckers. Warmth of a hollow body, feedback control of a solid. B.B. King (his "Lucille"), Chuck Berry, Larry Carlton, Dave Grohl. Jazz, blues, and anywhere you want warmth without mud.

**PRS (Paul Reed Smith)** — humbuckers with coil-split, mahogany/maple, 25" scale (splitting the difference between Fender and Gibson). **Refined, even, versatile** — Carlos Santana (his signature), John Mayer (on his PRS Silver Sky, which is actually Strat-voiced). PRS guitars sound expensive because they are.

**Gretsch** — **hollow-body**, Filter'Tron pickups (lower-output humbuckers). **Jangly, twangy, airy**. Chet Atkins, Brian Setzer, George Harrison's early Beatles tone, Malcolm Young's rhythm on AC/DC records (a Gretsch Jet through Marshalls is that sound).

**Rickenbacker** — unique pickups, through-neck construction, jangly 12-string variants. **Chiming, glassy, harmonically rich**. The Beatles (*A Hard Day's Night* opening chord is a Rick 12-string), Tom Petty, Peter Buck of R.E.M., The Jam.

**In Sozawen.** The physical modeling engine covers the two archetypal electric voices through body profiles: `Strat` (bright, glassy, single-coil articulation — clean chords bloom, blues leads sing) and `Les Paul` (thick, humbucker-driven, midrange push — for rock rhythm and sustained lead). These body profiles feed into the amp models to complete the chain — a `Strat` into `fender` is the Mayer/SRV blueprint, a `Les Paul` into `marshall` is Jimmy Page, a `Les Paul` into `mesa_boogie` covers heavier territory. For Tele-style twang, run `Strat` with the bridge pickup character and roll off some mids; for SG aggression, `Les Paul` into `marshall` with more gain captures the bite. The `clean_di` path is useful for re-amping and pedal chains.

**Common mistakes:**
- Buying the "rock" guitar for jazz, or vice versa — fit the tool to the job
- Ignoring scale length — 24.75" vs 25.5" changes how bends feel
- Assuming humbuckers are "better" than single-coils — they're just different
- Same strings on every guitar — a Les Paul likes 10s, a Tele can take 11s, a Strat is happy with 9s
- Chasing tone through pedals when the guitar-to-amp pairing is wrong — start at the source

**Going deeper.** Pickup position matters — neck pickups are warm and vocal, bridge pickups are bright and aggressive, middle (Strat) is balanced. **Wood**: alder is balanced, ash is bright with scoop, mahogany is warm, basswood is neutral. **Tone wood debate** — on solid bodies, body wood matters less than most players claim; on hollow/semi-hollow, it matters enormously. **Coil-splitting** turns a humbucker into a single-coil — huge versatility. Active pickups (EMG, Fishman Fluence) are consistent and noiseless — metal players' default. Know that tone is 70% fingers, 20% gear, 10% luck."""
    },

    "amp_tones": {
        "title": "Guitar Amplifiers & Their Character",
        "category": "Instruments",
        "content": """Change the amp, change the song. The same Les Paul through a Fender Twin is surf music. Through a Marshall Plexi it's Zeppelin. Through a Mesa Rectifier it's Tool. The **amp** is half the voice of an electric guitar, and every amp brand has a dialect of its own.

A guitar amp has three jobs: amplify the signal, shape its tone, and (crucially) add its own distortion and saturation character when pushed. That last job — how the amp *breaks up* — is where personality lives.

**Fender** is the **clean American sound** — scooped mids, sparkling highs, firm but not thunderous lows. The **Twin Reverb** is the benchmark clean amp — 85 watts, 2x12" speakers, the most famous clean platform in jazz, country, and anywhere cleans matter. The **Deluxe Reverb** is the smaller-room version — 22 watts, breaks up beautifully at gig volume (Mayer's live tone, SRV's studio secret). The **Princeton** is the small-combo classic — 12 watts, breaks up early, the recording engineer's favorite. Fender = clean headroom + spring reverb + tremolo.

**Marshall** is the **British crunch**. Where Fender scoops mids, Marshall pushes them forward. The **Plexi** (1959 Super Lead, from 1965-69) is the sound of classic rock — Hendrix, Cream-era Clapton, Van Halen's brown sound (modded). The **JCM800** is the 80s rock template — Slash, Zakk Wylde, Kerry King. Marshall amps love to be pushed — at low volume they sound polite, cranked they sound mythological.

**Vox AC30** is the **British chime**. EL84 power tubes (vs Marshall's EL34) give a more chimey, jangly character with rich top-end harmonics. The Beatles ran through AC30s. The Edge's entire U2 sound is an AC30 with delay. Brian May built the Queen guitar tone on six AC30s in a chain. The AC30 clean is shimmery; pushed, it's a different kind of distortion than a Marshall — more compressed, more treble-forward.

**Mesa Boogie** is **high-gain American**. Randall Smith modded a Fender Princeton in the 70s to have way more gain stages, and the modern high-gain amp was born. The **Dual Rectifier** is nu-metal's voice (Metallica *Black Album*, Tool, Deftones) — thick, scooped, aggressive. The **Mark series** (Mark IV, Mark V) is John Petrucci / Santana / Metallica lead territory — complex EQ (graphic EQ in the loop), unmistakable midrange.

**Orange** is **midrangey British**. Less scoop than Fender, more midrange than Marshall — a chunky, woody distortion. Used on a ton of stoner and doom (Sleep, Kyuss), plus mainstream rock (Jimmy Page on *Physical Graffiti*, recent Mastodon).

**Hiwatt** is **loud clean British**. Headroom for days, crystalline cleans that stay clean at volume where Marshalls would dirt up. Pete Townshend's wall of Hiwatts is the sound of *Live at Leeds*. David Gilmour's Pink Floyd tones. Hiwatts are for when you need clean at stadium volume.

**Peavey 5150** (now EVH 5150) — designed with Eddie Van Halen. The **metal amp** of the 90s and 2000s — tight, gainy, aggressive. Bullet For My Valentine, Machine Head, most modern metal. Four gain stages, aggressive attack.

**Tube vs solid state vs modeling.** **Tube amps** distort gradually as you push them — the saturation feels alive and responsive to your pick attack. **Solid state** distorts abruptly and the same way every time — cheaper, lighter, harder edges (jazz players like the Roland JC-120, a solid-state clean machine). **Modeling amps** (Fractal, Kemper, Helix, Quad Cortex) digitally emulate real amps — now good enough that pros tour with them exclusively. Modeling trades some feel for convenience and consistency.

**In Sozawen.** The amp model library covers the archetypal voices: `fender` (clean American, for jazz/country/clean-tone indie), `marshall` (British crunch, for classic rock rhythm and lead), `vox` (chime, for indie and Brit-pop territory), `mesa` / `mesa_boogie` (high-gain, for modern rock and metal), `orange` (midrangey, for stoner and doom). Pair with body profiles strategically — `Strat` into `fender` is the Mayer/Clapton clean blueprint, `Les Paul` into `marshall` is hard rock's default, `Les Paul` into `mesa_boogie` is modern metal. The `clean_di` amp is your re-amping and pedal-testing bed — no amp coloration, just the raw pickup signal. Cabinet impulse responses inside each amp model handle the speaker character; swap them for tone exploration without changing amps.

**Common mistakes:**
- Buying a 100-watt amp for bedroom use — tube amps need volume to sound right, a 5-watt does more for you at home
- Boosting bass on a Marshall — they're already mid/low-rich, cut instead of boost
- Ignoring the cabinet — a Twin head through a 4x12 is a different animal than through the Twin's open-back 2x12
- Cranking the gain — 90% of "heavy" tone comes from tight low-end and mid EQ, not gain
- Forgetting the room — amp-mic'ing captures the room as much as the amp; treat it or close-mic

**Going deeper.** Power tubes define the voice as much as the amp circuit. **6L6** (Fender, Mesa) — warm, firm, American. **EL34** (Marshall) — aggressive midrange, British rock. **EL84** (Vox) — chimey, compressed, Brit-pop. **6V6** (small Fenders) — sweet breakup at low volume. **Class A** vs **Class AB** — Class A (Vox) stays saturated; Class AB (most others) has more headroom. **Bright cap**, **presence** knob, **resonance** — these shape the top and bottom in ways the main EQ doesn't. And speakers matter as much as amps — a Celestion Greenback vs. a V30 vs. a Blue Alnico is the difference between eras."""
    },

    "bass_amp_tones": {
        "title": "Bass Amps & Their Character",
        "category": "Instruments",
        "content": """Bass amps aren't just "like guitar amps, but lower." They're a completely different philosophy — because bass is felt in the chest as much as heard in the ear, and the job of a bass rig is to move air while staying out of the kick drum's way. Get the amp right and the band sounds huge. Get it wrong and everything turns to mud.

A **bass amp** needs three things a guitar amp doesn't: massive clean headroom at low frequencies, speakers that can handle sustained low-end energy without flapping, and an EQ curve that lets the bass occupy its own frequency zone. That's why bass amps look like refrigerators and why their cabinets are built like tanks.

**Ampeg SVT** — the 300-watt all-tube heavyweight, born in 1969. **Thick, round, warm, growling when pushed**. The SVT-8x10 (eight 10" speakers, "fridge cab") is the rock bass sound — John Paul Jones, Geddy Lee, Jack Bruce, Cliff Burton, every 70s-80s rock record. At low volume it's round and punchy; pushed into saturation it has a beautiful harmonic grit that sits a guitar mix perfectly.

**Fender Bassman** — the original bass amp from 1952, so beloved that guitar players stole it (the tweed Bassman became Marshall's blueprint). Modern Bassman amps are clean, warm, and vintage-voiced. Blues, country, and indie bass live here.

**Mesa Bass** (Mesa Boogie's bass line — D-800, Subway, Bass Strategy) — **articulate, modern, punchy** with flexible EQ. Mesa bass amps handle modern extended-range basses and slap styles well, with enough headroom for 5-string low B.

**Darkglass** — the **modern metal/progressive bass sound**. Finnish company that built its reputation on the B7K overdrive pedal, now full amps (Microtubes 900, Alpha Omega). **Aggressive, mid-scooped, saturated** — the clanky, gritty bass tone on every modern metal record since 2010 (Periphery, Animals as Leaders, Polyphia). Built-in distortion circuits that stay tight in the low end.

**Orange** bass amps (Terror Bass, AD200B) — **warm, British, midrangey**. The bass equivalent of their guitar amps. Stoner rock, doom, and heavy fuzz bass (Matt Pike, Geezer Butler's modern tone).

**Aguilar** (Tone Hammer, DB751) — **clean, hi-fi, studio-refined**. Aguilar amps and preamps are the modern session standard — neutral, detailed, and they sit in a mix without coloring it. Session players on jazz, fusion, and pop.

**Gallien-Krueger (GK)** — **clean punch, solid-state**. The 800RB defined "clean bass" in the 80s — Flea's early Red Hot Chili Peppers tone, tons of rock and pop. GK amps are bright, snappy, and punch through dense mixes.

**Markbass** — **modern Italian, lightweight, mid-forward**. Markbass amps and 1x12 combos are the session and jazz player's gig bag — loud, clean, and 15 pounds instead of 80. Marcus Miller uses them.

**Trace Elliot** — British, known for their graphic EQ and green aesthetic. The 80s-90s rock and pop bass sound — Mark King (Level 42), Pino Palladino's early work.

**Cabinets and what they do.** Cabs move air, and size + driver count define the character. **1x15** — big, round, warm, classic vintage sound (Motown, old-school rock). **2x10** — punchy, articulate, great for modern styles. **4x10** — the most versatile — punch of 10s with enough air movement for rock. **8x10** ("fridge") — the Ampeg classic, thunderous and immense, rock and metal stage rig. **1x12** — modern, detailed, often paired with tweeter for top-end clarity. Multiple drivers in smaller sizes (4x10) give tighter low end than one big driver (1x15); one big driver gives warmer, rounder low end.

**In Sozawen.** The bass amp model library covers the core voices: `ampeg_svt` (thick tube warmth — rock and classic), `darkglass` (modern overdriven — progressive, metal, clanky/gritty), `orange` (warm British — stoner, fuzz), `fender` (clean vintage — blues, country), `mesa` (articulate modern). Pair with the bass body profiles strategically — `Precision` into `ampeg_svt` is the Motown/rock blueprint (McCartney, JPJ, Dee Dee Ramone), `Jazz` into `fender` is the fingerstyle-funk standard (Jaco, Marcus Miller clean), `StingRay` into `ampeg_svt` or `mesa` is Flea/Louis Johnson slap territory, `Rickenbacker` into `orange` is Lemmy's unmistakable snarl. The `clean_di` path is your direct-injected studio signal — essential for pop, where a blended DI + amp-mic gives you clarity and warmth at once. For the `acoustic_bass` body profile, skip the amp chain entirely and mic/DI the modeled instrument.

**Common mistakes:**
- Boosting low end until the speakers fart — low-end comes from the cabinet, not the EQ knob
- Ignoring the crossover with the kick — carve 60-100Hz in one or the other, not both
- Using a guitar amp for bass — you'll blow the speaker and the low end is undersized
- Running full-range direct and full-range through the amp — phase cancellation will hollow out your tone
- Forgetting the high end — bass has top-end attack too; don't shelve it off

**Going deeper.** **Tube vs. solid state** — tube amps compress gracefully and saturate musically (Ampeg SVT is the holy grail here); solid state is clean, consistent, and lighter. **Class D** (modern Markbass, Aguilar Tone Hammer) is the new standard — huge power in tiny boxes. **DI (direct injection)** bypasses the amp/cab entirely — essential for recording in rooms that can't handle bass volume, and for re-amping later. **Blend DI + mic** is the studio standard — DI for clarity, mic for body and amp character. Bass preamp pedals (SansAmp, Darkglass, Tech 21) are the poor man's amp — many pros use the pedal and skip the head entirely. EQ philosophy: **cut more than you boost**, and remember — bass sits in the mix by what it *doesn't* do as much as what it does."""
    },

    "drum_brands": {
        "title": "Drum Brands & Their Sound",
        "category": "Instruments",
        "content": """Drum sets sound like the brand printed on the bass drum head. That isn't marketing — it's shell wood, bearing edges, hardware weight, and a century of each company making specific decisions. Put John Bonham's Ludwig in a room, hit it, and you've already got half the sound of *Moby Dick*. Switch to a DW kit and you're in a 2010 pop record before the first fill.

A **drum kit** has two sonic families — **shells** (the drums themselves) and **cymbals**. Each has its own brand character, and the combination is your sonic fingerprint.

**Ludwig** — American, founded 1909. **Open, warm, resonant, slightly unruly**. The Ludwig sound is loose and three-dimensional — drums that breathe. The **Black Oyster Pearl** Ludwig kit is Ringo Starr's (every Beatles record). The **Amber Vistalite** (clear acrylic) is John Bonham's Led Zeppelin sound — enormous, open, with a kick that's as much chest as ear. Ludwig snares — the **Supraphonic 400** (chrome-over-aluminum) and the **Black Beauty** (brass) — are on more hit records than any other snares in history.

**DW (Drum Workshop)** — American, founded 1972. **Articulate, modern, controlled, pristine**. Where Ludwig is wild, DW is precise. Maple shells with VLT (vertical low timbre) construction, heavy hardware, tight bearing edges. Modern pop, country, contemporary Christian, session work — if you hear a drum kit that sounds like every drum is exactly where it's supposed to be, it's probably a DW.

**Gretsch** — American, founded 1883. **Broken-in, round, dry, vintage-voiced**. Gretsch shells use a unique 6-ply maple/gum combination with "silver sealer" interior. The sound is warm and pre-aged — jazz (Tony Williams, Elvin Jones, Mel Lewis), Americana (Levon Helm of The Band), indie rock. "That Great Gretsch Sound" is their old slogan and it's accurate.

**Yamaha** — Japanese, drum division since 1967. **Consistent, studio-friendly, balanced, even**. Yamaha Recording Customs are literally designed for the studio — they tune easily, sound great at any volume, record cleanly. Steve Gadd, Dave Weckl, a massive share of session drummers worldwide. The Tour Custom and Stage Custom cover mid-range; the Absolute Hybrid Maple is the modern flagship.

**Pearl** — Japanese, founded 1946. **Versatile, workhorse, genre-flexible**. Pearl makes drums across every price point and every style. The Masters Maple Complete is pro session territory; the Export is the most-sold intermediate kit in the world. Pearl kits show up everywhere because they do everything competently.

**Tama** — Japanese, founded 1974. **Dark, cutting, modern, metal-friendly**. Tama Starclassic (maple, birch/bubinga) and Superstar lines are metal and rock standards — Lars Ulrich, Mike Portnoy, Stewart Copeland (on his iconic Police kit). Birch shells are brighter and more cutting than maple.

**Sonor** — German, founded 1875. **Classic, full, precise, heavy-duty**. German engineering applied to drums — thick shells, beaded bearing edges, premium fittings. The SQ2 custom series is one of the finest kits money can buy. Phil Collins, Steve Smith, Benny Greb. Sonor kits sound big and expensive because they are.

**Cymbals.** **Zildjian** — Turkish/Armenian, founded 1623 (yes, really). The **A series** is bright, cutting, loud — classic rock and pop. The **K series** is darker, drier, more complex — jazz and studio. The **A Custom** is hybrid brightness. **Sabian** — Canadian, founded by a Zildjian family member. Parallel range — AA (bright), AAX (modern bright), HH (dark, hand-hammered). **Paiste** — Swiss. **Clear, cutting, complex, shimmering**. Paiste 2002 is the classic rock cymbal (Bonham, Nicko McBrain). **Meinl** — German. Modern, complex. Byzance and Byzance Vintage are jazz and studio favorites; Classics Custom is rock.

**Shell woods.** **Maple** — balanced, warm, the default. **Birch** — brighter, more cutting, studio-favored for its pre-EQ'd top end. **Mahogany** — warmer than maple, vintage voice (Ludwig's classic Keller shells). **Bubinga** — dense, loud, aggressive. **Beech** — between maple and birch. **Oak** (Yamaha) — punchy, modern. Ply count matters — **6-ply** (most common) balances resonance and durability; **thin 4-ply** is more resonant; **thick 10-ply** is more projection, less resonance.

**In Sozawen.** The drum generator models kit character at the shell and head level — each kit preset reflects a specific brand voicing and tuning philosophy. The 18-voice drum engine covers the core kicks, snares, toms, hats, and cymbals across brand archetypes (Ludwig-style open/warm, DW-style articulate, Tama-style dark metal, Gretsch-style broken-in). Cymbal voices are modeled from the peer-reviewed cymbal physics research — distinct modal frequencies, B20 vs B8 alloy decay curves, and brand signatures (Zildjian K vs A character). The 20 genre presets (rock, pop, metal, jazz, funk, etc.) pre-configure not just the pattern but the kit character and mic setup appropriate for the style — a metal preset leans Tama shells + Zildjian A Custom crashes through a close-mic'd setup, while a jazz preset uses Gretsch-voiced shells + Zildjian K ride with more room mic blend.

**Common mistakes:**
- Buying the "pro" kit for a bedroom — smaller shells, thinner heads, and good tuning beat expensive kits played wrong
- Ignoring heads — head choice (Remo Ambassador vs Emperor vs coated vs clear) changes the kit more than the shells
- Tuning to one "right" pitch — drums sound best tuned to resonate freely; pitch is secondary to resonance
- Over-dampening — moongels and pillows everywhere kill the kit's voice; let drums ring
- Matching brand loyalty over sound — a Pearl kit might be right for you even if your hero plays Tama

**Going deeper.** **Bearing edges** — sharper edges (45°) = more attack, brighter; rounder edges = warmer, rounder. **Shell thickness** — thinner = more resonance; thicker = more projection, less tone. **Snare wires** — 20-strand is the default; 30-strand is crisper; 16-strand is looser and jazzier. **Snare bed** — a carved dip in the shell where the wires contact, critical to snare sensitivity. **Calf heads** (traditional) vs plastic (Remo/Evans) — calf is warmer and weather-sensitive, plastic is consistent. Tuning top and bottom heads to different pitches opens up the drum's voice — bottom slightly higher than top gives a fatter rebound. Listen to the space between the drums — ghost notes, hi-hat openings, subtle ride dynamics are what separate a great drummer from a competent one."""
    },

    "studio_budget_guide": {
        "title": "Building a Studio on Any Budget",
        "category": "Hardware",
        "content": """You don't build a studio all at once. You build the piece you need right now, live with it long enough to know what's actually limiting you, and then upgrade the specific thing. Every budget below assumes you're starting from nothing and want to make finished music — not demos, finished music — at that price point.

The ugly truth: past about `$500`, the biggest single upgrade is almost always **room treatment**, not more gear. A `$300` pair of monitors in a treated room beats a `$3000` pair in a bare bedroom, every time. Plan accordingly.

**Key vocabulary:** **Signal chain** (the path from source to recording — instrument → cable → interface → computer → DAW). **Tracking** (recording a performance). **Mixing** (balancing and processing the tracks). **Reference track** (a commercial song in your genre you A/B against while mixing). **Cans** (headphones — studio slang).

**In Sozawen.** Sozawen's built-in physical instrument models mean you don't need expensive sample libraries to get convincing guitar, piano, drums, or strings out of a bedroom rig. A `$200` interface and a laptop running Sozawen will put real instrument sounds on your tracks — which shifts the budget toward the one or two things that actually have to be physical: a mic, a pair of headphones, and eventually a room.

**Common mistakes:**
- Buying gear in the wrong order. Monitors before treatment. A fancy mic before a quiet room. A high-end interface before you've outgrown a Scarlett.
- Spending the whole budget on one piece. A `$1500` mic into a laptop's built-in input sounds worse than an `$80` **SM58** into a **2i2**.
- Skipping the chair. You'll spend 1000+ hours in it. A `$150` office chair matters more than a `$150` plugin.
- Ignoring the computer. An underpowered laptop will bottleneck everything. `16 GB RAM`, SSD, and a modern CPU is the floor.
- Upgrading for upgrade's sake. Finish 10 songs on the rig you have before changing anything.

**Going deeper.**

**$200 — bedroom starter.** Laptop you already own, **Focusrite Scarlett Solo** ($110) or used **2i2** ($80), **Shure SM58** ($100 — handles vocals, amps, anything loud) OR **Audio-Technica AT2020** ($100 — condenser for softer vocals and acoustic guitar, but you need a quiet room), **Sennheiser HD280 Pro** or **Sony MDR-7506** ($100). Sozawen handles the rest. You can make a full album with this.

**$1000 — serious home setup.** **Audient iD14** ($300), **Shure SM7B** OR **AT2020** plus an **SM57** ($100-400 mic budget), **Kali LP-6 V2** monitors ($450/pair), **Sennheiser HD600** headphones ($350 — worth the splurge, lasts a lifetime), basic treatment: two DIY Rockwool panels at first reflection points, two corner bass traps ($150 in materials). Isolation pads under the monitors ($40). Boom arm for the mic ($30). This rig finishes professional-sounding indie records.

**$5000 — pro home studio.** **Universal Audio Apollo Twin X** or **RME Babyface Pro FS** ($900-1400), **Adam T7V** or **Focal Alpha 65 Evo** monitors ($900/pair), proper treatment — four **GIK 242 panels** plus two **Soffit bass traps** ($1200), multiple mics: **SM7B** + **AT4040** + stereo pair of **sE7** pencils ($1000), **HD600** plus **Beyerdynamic DT770** for tracking ($500), decent MIDI controller like a **Native Instruments Komplete Kontrol** ($400). Upgrade the chair and the desk. You're now limited by skill, not gear.

**$20k+ — mix room.** Dedicated room with floated floor or at minimum isolated walls, **Genelec 8040** or **Adam A7X** with sub ($4-6k), **RME UFX** or **Apollo x8p** ($3-4k), proper treatment designed by someone who's done it before (`$3-5k` including the work), a small locker of character mics (**Neumann U87** or **TLM 103**, **Royer R-121**, multiple dynamics), outboard preamp pair (**Warm Audio WA-73**, **BAE 1073**), isolated tracking room or vocal booth. At this tier, you're running a small business or getting paid for other people's records — otherwise the money is better spent on time.

The single cheapest upgrade at every tier: finishing more songs on what you already own. Gear doesn't write the record."""
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
        "content": """The moment you record a song idea on your phone, you own the copyright. Nobody had to approve it. The law already says it's yours. What registration, publishing, and PROs give you is **enforcement power** — the paperwork to actually get paid when your song makes money.

**The core idea.** Every song has **two copyrights**, not one:
- **The composition** — melody, lyrics, chords. The song itself.
- **The master** — a specific recording of that song.

Cover a song, and you're using someone else's composition but making your own master. That's why cover artists pay mechanical royalties to the composer and keep their own recording royalties. Keep this two-copyright split in your head — every deal, split, and royalty flows from it.

**Vocabulary.**
- **PRO (Performance Rights Organization)** — ASCAP, BMI, SESAC (US), SOCAN (Canada), PRS (UK), GEMA (Germany). Collect performance royalties when your song plays on radio, streaming, venues, TV.
- **Mechanical royalties** — paid when a recording is reproduced (CD, download, interactive stream). Collected by HFA or **MLC** (Mechanical Licensing Collective) in the US.
- **Sync licensing** — a TV show or film using your song. One-time fees + backend royalties.
- **Publisher share / Writer share** — a song's publishing income is split 50/50 between "writer" and "publisher." If you self-publish, you get both halves.
- **Split sheet** — written agreement listing all co-writers and their ownership percentages.

**What exists automatically vs what you have to do.**

Automatic the moment the song is "fixed" (recorded, written down):
- Copyright ownership in US, EU, most of the world (Berne Convention).
- The right to control who uses it.

You have to actively do:
- **Register with a PRO.** Free or cheap. Without this, performance royalties go uncollected. Pick *one* PRO per writer — you can't join both ASCAP and BMI.
- **Register with the MLC** (US mechanical royalties for streaming). Free.
- **Register with the US Copyright Office** (Form PA, $45). Not required to own it, but **required to sue for infringement** in US federal court with statutory damages.
- **Distribute masters** through DistroKid / TuneCore / CD Baby to get on streaming platforms.

**In Sozawen.** Sozawen's **Project Metadata** panel stores writer splits, ISRC, ISWC, and PRO affiliations per project. When you export, the metadata is embedded in the file so distributors can read it. The **Collaboration Export** bundles a split sheet PDF with every multitrack delivery — dated, listed by contributor, ready to sign. Lyrics entered in the **Lyrics Editor** export as PDF for Copyright Office submissions or as LRC files for streaming sync.

**Common mistakes:**
- **Poor-man's copyright.** Mailing yourself a CD in a sealed envelope. **This is a myth.** It has no legal standing under the 1976 Copyright Act. Use the Copyright Office.
- **Not joining a PRO.** Your song plays on Spotify, radio, a coffee shop — you're owed money. Without a PRO, it sits in "unclaimed" pools forever.
- **Verbal splits.** You and your co-writer agree 50/50 in the room, never write it down. Two years later the song blows up and memories differ. **Always split-sheet before recording.**
- **Confusing master with composition.** Selling your master to a label doesn't give them your composition rights. Selling your publishing doesn't give them your master. They're separate assets, negotiated separately.
- **Skipping the MLC.** Mechanical streaming royalties in the US now flow through the MLC. Register for free or leave money on the table.

**Going deeper.**

**When to incorporate.** Once you're earning consistent publishing income, an LLC (or S-corp once profits cross roughly $40-80k) protects personal assets and can save on self-employment tax. Talk to an entertainment accountant, not a general one. The LLC becomes the publisher — you, the writer, license your work to your own publisher, and both halves of income flow through it.

**Self-publishing vs signing a publisher.** A publisher (Sony/ATV, Warner Chappell, indie) takes 25-50% of publishing in exchange for pitching your songs for sync, cuts, co-writes. Worth it if you want placements; not worth it if you're primarily a recording artist.

**Sync is where indie money lives.** A single TV placement can pay $500-$50,000. Companies like Musicbed, Artlist, and direct pitches to music supervisors are realistic paths. Keep instrumental stems — most syncs need an instrumental version.

The paperwork is unglamorous. Do it once, then make music."""
    },

    "export_platforms": {
        "title": "Export Settings for Every Platform",
        "category": "Releasing",
        "content": """Each streaming platform normalizes loudness differently. Master too loud for Spotify and it sounds *quieter* than a track mastered properly — because Spotify turns you down and strips your dynamics in the process. Master right for the destination, and your song lands with impact everywhere.

**The core idea.** **LUFS** (Loudness Units Full Scale) is how platforms measure perceived loudness. Every major streamer has a target; anything louder gets turned down. Anything quieter *may* get turned up (Spotify), or left alone (Apple). The game isn't "be the loudest" — it's "hit the target with the best dynamics."

**Vocabulary.**
- **Integrated LUFS** — average loudness across the whole song.
- **True Peak (dBTP)** — the actual peak after digital-to-analog conversion. Inter-sample peaks can exceed 0dBFS even if your DAW meter doesn't show it.
- **Normalization** — the platform's automatic volume adjustment. On by default on most streamers.
- **Sample rate / bit depth** — 44.1 kHz / 16-bit is the consumer standard; 48 kHz / 24-bit is the production standard.

**Platform-by-platform.**

| Platform | LUFS Target | True Peak | Format |
|---|---|---|---|
| Spotify | -14 LUFS | -1 dBTP | OGG Vorbis 320kbps |
| Apple Music | -16 LUFS (Sound Check) | -1 dBTP | AAC 256kbps / ALAC lossless |
| YouTube / YouTube Music | -14 LUFS | -1 dBTP | AAC 128-384kbps |
| Tidal | -14 LUFS | -1 dBTP | FLAC lossless (up to 24/192 MQA) |
| Amazon Music | -14 LUFS | -2 dBTP | FLAC lossless |
| SoundCloud | -8 to -13 LUFS tolerated | -1 dBTP | MP3 128kbps (free) / Opus 256kbps (Go+) |
| Bandcamp | No normalization | -0.3 dBTP | WAV/FLAC source, all formats offered |
| CD mastering | -9 to -11 LUFS (no cap) | -0.1 dBTP | 16-bit / 44.1 kHz WAV |
| Vinyl mastering | -14 to -16 LUFS | -1 dBTP | 24-bit / 96 kHz, limited sub + tamed highs |

**In Sozawen.** The **Master panel**'s platform dropdown contains every target above. Pick "Spotify," and Sozawen shows a live **LUFS/True-Peak meter** with green/red indicators and sets the export encoder automatically. The **Export Settings** dialog remembers your destination per project — a song destined for Spotify + Apple + vinyl exports as three files, each correctly mastered, in one click. The **Master panel** also has a **Normalization Preview** that simulates what each platform will do to your track *before* you upload, so you can hear Spotify's -14 LUFS target on your own speakers.

**Common mistakes:**
- **Mastering at -7 LUFS for Spotify.** Spotify turns you down 7 dB. Your dynamics get crushed for no gain — you sound quieter and flatter than properly mastered competitors.
- **Ignoring true peak.** Peaks at -0.1 dBFS in your DAW can hit +0.5 dBTP after encoding, causing audible clicks on Spotify's OGG stream. Leave -1 dBTP.
- **One master for every platform.** Vinyl and Spotify want different things. So do CD and YouTube. Export variants.
- **Exporting MP3 from your DAW for streamers.** Let the platform encode from your WAV. Their encoders are updated; yours may not be.
- **Forgetting to disable normalization when referencing.** If you're A/B'ing your mix against a Spotify track *inside Spotify*, both are level-matched. Toggle Spotify's normalization *off* when referencing absolute loudness.

**Going deeper.**

**Bandcamp is special.** No normalization means the loudest master wins — briefly. But Bandcamp's audience cares about quality; a dynamic, -12 LUFS master with punch often outperforms a squashed -7 LUFS wall-of-sound one. Upload 24-bit WAV for best quality.

**Vinyl is physics, not loudness.** A lathe cuts a groove. Harsh sibilance and heavy sub-bass below 80 Hz crossed with stereo width cause skipping. Your vinyl master wants: mono-summed sub, de-essed highs, -14 LUFS, careful phase work. Most vinyl mastering engineers want your *pre-limiter* mix, not your Spotify master.

**CD mastering** can be louder (no platform normalization), but listener fatigue sets in. -9 to -11 LUFS gives impact without pain.

**YouTube content ID** cares about your master rights, not loudness — register with a PRO and a distributor or third parties will claim your audio.

The LUFS target is a guideline for the destination, not a target for every mix."""
    },

    "collaboration": {
        "title": "Collaborating with Other Musicians",
        "category": "Releasing",
        "content": """The best collaboration is the one nobody fights about six months later. That means: **split ownership before you hit record**, send files people can actually use, and speak the same language about what you want.

**The core idea.** Collaboration produces two outputs: **a song** and **a relationship**. Both need maintenance. The song needs technical standards (sample rates, stem alignment, loudness). The relationship needs written agreements (who wrote what, who owns what, who gets paid what). Skipping either side — "we'll figure out splits later," "I'll just send them my session" — is where collaborations break.

**Vocabulary.**
- **Stems** — grouped mixes (all drums on one file, all vocals on another). Typically 4-8 files.
- **Multitracks** — every individual track exported separately. Dozens of files.
- **Split sheet** — written doc listing every contributor, their role, and ownership %.
- **Work-for-hire** — contributor gets paid once, gets no ongoing royalties, claims no ownership.
- **Profit share / Points** — contributor gets a % of income (typically 1-5 "points" for producers).
- **Reference track** — a commercial song you send to communicate direction ("make it feel like this").

**Splitting ownership — get it in writing.** Before recording starts, agree:
1. **Who's a writer** (melody, lyrics, chord progression — not everyone who plays on it)
2. **What percentage each writer owns** (doesn't have to be equal)
3. **Master ownership** separately from publishing
4. **Producer points** separately from writer splits

A basic split sheet: names, contact, PRO affiliation, contribution description, % publishing, % master, signature, date. One page. Free templates exist — use one.

**Technical standards for sending files.** When sending stems to a mixer or collaborator:
- **Sample rate & bit depth:** match the session (usually 48 kHz / 24-bit).
- **Start point:** every stem starts at **bar 1, beat 1**, even if silent there. This lets the receiver drag all files to bar 1 and they align perfectly.
- **No master bus processing.** No limiter, no master compression, no master EQ. Export each stem with inserts and sends *intact* on the track itself.
- **Headroom:** peak around **-6 dBFS**, integrated around **-18 LUFS**. Don't send clipping files.
- **Naming:** `01_Kick.wav`, `02_Snare.wav`, `VOX_Lead.wav`. The mixer will love you.
- **Include a reference mix** (a rough stereo bounce) so the collaborator hears how it's supposed to feel.

**In Sozawen.** The **Collaboration Export** dialog bundles all of the above automatically. Pick "Stems" or "Multitracks," and Sozawen exports with bar-1 alignment, consistent sample rate, -18 LUFS calibration, clean naming, a reference stereo bounce, a tempo map, a MIDI-guide track, and an editable split sheet PDF — all zipped. Drop the zip in Dropbox, Drive, or Splice; the receiver imports the whole session in one click. Sheet music exports as **MusicXML** or **PDF** for players who can't open DAW sessions.

**Common mistakes:**
- **"We'll do splits later."** Later is never. Do it before the session ends.
- **Sending a stereo bounce instead of stems.** Mixer can't fix what's baked in.
- **Master bus processing left on stems.** Limiter on the master squashes every stem. Remove it before exporting.
- **Misaligned stems.** Each stem starting where its content starts, not bar 1. Dragging them in requires manual time-alignment per file.
- **Different sample rates.** 48 kHz stem into a 44.1 kHz session resamples badly if the DAW doesn't catch it.
- **"It sounds weird."** Useless feedback. Replace with: *"the vocal feels buried in the second chorus"* or *"the snare is thin compared to the reference."*

**Going deeper — feedback language.** Bad feedback kills collaborations. Good feedback has three parts: **where, what, how**.
- **Where** — timestamp or section. "2:14" or "second chorus."
- **What** — the symptom. "Vocal is distant." "Kick is woofy." "Snare disappears."
- **How** — desired direction, not a prescription. "More presence" beats "boost 3 kHz +2 dB." Let the mixer decide the tool.

**Reference tracks** communicate in 10 seconds what words take paragraphs. "Make the vocal ride the mix like *this* song at 0:45." Send the link.

**Credit listings** matter. A producer who got 2 points and is credited as "Produced by X" on the release has a career-building artifact. A producer who got paid cash and isn't listed has nothing to point to. Credit is usually cheaper than money — give it freely when earned.

**Work-for-hire vs profit share.** A session musician who tracked guitar for $300 with a work-for-hire agreement is done — no ongoing obligations either way. A co-producer with 3 points gets paid forever. Know which you're offering before the conversation.

Good collaboration means everyone wants to work together again."""
    },

    "lyrics_protection": {
        "title": "Protecting Your Lyrics & Songwriting",
        "category": "Releasing",
        "content": """Lyrics are copyrighted the instant you write them down or record them — no filing, no fee. What protection gives you is **provable ownership** when someone else claims the song is theirs. Your job isn't to *create* ownership; it's to build a trail of evidence you can point to.

**The core idea.** Proving you wrote something first requires two ingredients: **a dated record of the work** and **a verifiable third party** holding that record. A voice memo on your phone has a date but it's on a device you control — easy to dispute. A cloud upload to Dropbox is date-stamped by Dropbox's servers — much harder to dispute. A US Copyright Office registration is **legally definitive**.

Stack the layers. Each one is cheap. Together they're airtight.

**Vocabulary.**
- **Copyright Office registration (Form PA)** — $45, US. Definitive legal record. Required to sue for statutory damages in federal court.
- **Poor-man's copyright** — mailing yourself a sealed envelope. **Myth — no legal standing.**
- **Metadata** — data embedded in a file (creation date, author, GPS). Can be evidence.
- **Provenance** — documented chain of custody: who had it, when.
- **NDA (Non-Disclosure Agreement)** — signed contract requiring the receiver to keep material confidential.

**The protection stack.**

**Layer 1 — habit.** Journal every lyric and melody idea with a date. Voice memos with the date spoken aloud. One notebook, one folder, one cloud drive.

**Layer 2 — cloud upload.** Drop lyric drafts and demos into Dropbox, Google Drive, or iCloud. The server timestamps the upload. If someone disputes authorship in 2029, the 2026-04-20 cloud timestamp stands up.

**Layer 3 — PRO registration.** ASCAP/BMI/SESAC register your song with a date and your ownership claim. Free.

**Layer 4 — Copyright Office registration.** $45, Form PA, done online. Takes months to process but the effective date is the *filing* date. This is the one that gives you real legal teeth — without it, statutory damages ($750-$150,000 per infringement) aren't available in US court.

**Layer 5 — watermarked demos when pitching.** Don't send naked MP3s to strangers. Embed a watermark (audible or metadata) identifying the recipient — "Demo for [Label] — [Date]." If the file leaks, you can trace the source.

**In Sozawen.** The **Lyrics Editor** timestamps every edit and stores a version history — every revision is saved with date, time, and a text diff. The **Source Bank** is Sozawen's idea journal: every voice memo, lyric fragment, or melodic sketch you drop in gets timestamped and cloud-synced. Export the Source Bank as a dated PDF bundle for Copyright Office submission — Sozawen generates a properly formatted Form PA lyric sheet ready to attach. The **Collaboration Export** bundles a signable NDA template alongside demo files when sending to labels or co-writers.

**Common mistakes:**
- **Relying on the mail-yourself-a-CD myth.** No US case law supports it. Don't bet a song on it.
- **Not registering demos at all.** "It's just a demo" — until it gets leaked, covered, or sampled without credit.
- **Sending unwatermarked material to labels.** Cold-pitched songs have been allegedly cut by label-adjacent writers before the artist heard back. Watermark or NDA.
- **Trusting metadata alone.** Phone metadata can be edited. Use cloud timestamps.
- **Collaborating without work-for-hire language.** A session writer who helped with one line might later claim co-authorship if nothing's signed. Get a one-page work-for-hire or split sheet before the session.
- **Posting lyric videos before registration.** Once it's on YouTube it's in the wild. Register first.

**Going deeper.**

**Lyric services** — MusixMatch and Genius display lyrics on streaming platforms and search. They are **metadata distribution**, not protection. You retain copyright; they retain no ownership. But submitting to them does create another third-party dated record, which doesn't hurt.

**Anti-plagiarism habits.** Keep *everything* dated: voice memos, written drafts, co-writer texts discussing the idea. A paper trail of the song's development is the best defense against a "you stole this from me" claim. It also protects you from *accidentally* copying someone else — if you can show a timeline of independent creation, even similar-sounding songs can be defended.

**NDAs when pitching.** A simple mutual NDA before sending unreleased material to labels, sync houses, or co-writers is reasonable and professional. One page. Free templates exist. Most pros sign without blinking; the ones who refuse are telling you something.

**When something does get stolen.** Don't post on social media first — you'll hurt your case. Talk to an entertainment lawyer before making public accusations. With Copyright Office registration, PRO registration, dated cloud uploads, and development artifacts, you walk in with ammunition.

Protection isn't paranoia — it's the paperwork equivalent of saving your work."""
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
