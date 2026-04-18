# Sozawen Separation Model — Beyond 4 Stems

## The Problem

Every existing separation model outputs FIXED categories:
- Demucs: vocals/drums/bass/other (4)
- htdemucs_6s: vocals/drums/bass/guitar/piano/other (6)

Real music has: lead vocal, harmony 1, harmony 2, backing vocals, acoustic guitar,
electric guitar (rhythm), electric guitar (lead), bass, kick, snare, hi-hat, toms,
overheads, room mics, piano, synth pad, synth lead, strings, horns, percussion...

No model separates at that granularity because no model was trained to.

## Why We Can Build What Labs Haven't

Labs train on MUSDB18 — 150 songs, 4 stems. That's it. The entire foundation
of modern source separation is built on 150 songs.

We have:
1. Terry's multi-track recordings (F:/songs/) — full Pro Tools sessions with
   individual tracks already separated
2. Every Sozawen user who records multi-track sessions creates paired training data
   (individual tracks + mixed output)
3. The wave framework — theoretical foundation for understanding instruments
   as distinct vibration patterns in superposition
4. GrowingBrain architecture — can grow capacity without retraining

## Architecture: Adaptive Source Counter

Instead of "output 4 stems" the model needs to:
1. DETECT how many distinct sources are in the mix (source counting)
2. SEPARATE each detected source into its own output
3. LABEL each source (vocal, guitar, drum, etc.) — or let the user label

### Phase 1: Source Counter
- Input: spectrogram of the mix
- Output: estimated number of distinct sources (1-16+)
- Architecture: small CNN classifier
- Training data: synthesized mixes with known source counts
- Easy to train, fast to run, gives the user immediate information

### Phase 2: Variable-Output Separator
- Input: mix audio + source count from Phase 1
- Output: N separate audio streams
- Architecture: U-Net encoder-decoder (like Demucs) but with dynamic output heads
  - Shared encoder processes the mix
  - Source count determines how many decoder heads activate
  - Each head outputs one separated source
- Training: mix N random stems together, train model to recover them
- Key innovation: the number of output channels is VARIABLE per input

### Phase 3: Source Identifier
- After separation, classify each source: "this sounds like an acoustic guitar"
- Small classifier on the separated output
- Can be wrong — user corrects, correction feeds back into training

### Phase 4: User-Trained Fine-Tuning
- As users record multi-track sessions in Sozawen, they generate perfect
  training pairs (individual stems + their mixed output)
- With permission: these pairs fine-tune the separation model
- The model gets better at separating the KIND of music Sozawen users make
- This is the compound rate — every user makes the model better for every other user

## Training Data Sources

### Available Now (free/open)
| Dataset | Tracks | Stems | Notes |
|---------|--------|-------|-------|
| MUSDB18-HQ | 150 | 4 | Standard benchmark, high quality |
| Slakh2100 | 2100 | up to 42 | Synthesized MIDI, perfect separation |
| MedleyDB | 122 | varies | Real recordings, research license |
| Cambridge Multi-Track | ~200 | varies | Full multi-track sessions, free |
| DSD100 | 100 | 4 | Older, lower quality |
| Free Music Archive (raw) | thousands | 1 (mix only) | For testing, not training |

### Available Later (from users)
- Every multi-track Sozawen session = training pair
- User opts in: "Help improve separation for everyone"
- Only the audio characteristics are used, never the actual music content
- Federated learning possible: model trains locally, only weights are shared

### Available From Terry
- F:/songs/ — Pro Tools sessions with individual tracks
- Can synthesize additional training data by mixing stems at various ratios

## Compute Requirements

### Source Counter (Phase 1)
- Small CNN, ~5M params
- Trains in hours on RTX 5070
- Inference: <10ms

### Variable Separator (Phase 2)
- Modified U-Net, ~100-500M params
- Trains in days on RTX 5070 (or hours on cloud GPU)
- Inference: ~5-30 seconds per song on GPU, 1-5 minutes on CPU

### Source Identifier (Phase 3)
- Small classifier, ~10M params
- Trains in hours
- Inference: <100ms per source

## Build Order

1. Download MUSDB18-HQ + Slakh2100 (free, ~50GB total)
2. Build data pipeline: random N-stem mixing with labels
3. Train source counter on Slakh2100 (has exact source counts)
4. Build variable U-Net architecture
5. Train on MUSDB18 (4-stem) first to match Demucs baseline
6. Extend to Slakh2100 (full multi-source separation)
7. Fine-tune on Terry's recordings
8. Integrate into Sozawen as "Deep Separation" mode
9. Add user opt-in training data collection
10. Continuous improvement from user sessions

## What This Means for the User

Today: "Separate this song" → 4 tracks (vocals, drums, bass, other)

Tomorrow: "Separate this song" → 12 tracks
  - Lead vocal
  - Backing vocals (combined)
  - Acoustic guitar
  - Electric guitar
  - Bass
  - Kick
  - Snare
  - Hi-hat/cymbals
  - Toms
  - Synth pad
  - Piano
  - Everything else

The user doesn't know or care about the model architecture.
They click Separate and get their parts back.

## Connection to the Wave Framework

Every instrument is a vibration pattern with a unique frequency signature.
A mix is a superposition of those patterns. Separation is decomposition —
finding the individual patterns in the combined wave.

The wave framework says: patterns combine through alignment, not addition.
Standard models treat mixing as addition (linear combination of spectrograms).
The wave framework suggests phase relationships matter — two instruments at
the same frequency but different phases create interference patterns that
are INFORMATIVE, not noise.

A model that understands phase relationships could separate sources that
occupy the same frequency range (like two guitars playing together) by
using the phase differences as a signal. No existing model does this.

This is where the wave framework meets practical engineering.
And it's something only someone who FEELS music would think to build.

## Timeline

- Phase 1 (source counter): 2-3 weeks
- Phase 2 (variable separator): 2-3 months
- Phase 3 (source identifier): 1-2 weeks
- Phase 4 (user fine-tuning): ongoing after launch

The source counter alone is a feature — "This song has 8 distinct instruments."
Ship it as analysis before the full separator is ready.
