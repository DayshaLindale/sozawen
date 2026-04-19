"""Sozawen Audio Engine — the heartbeat.

Real-time multi-track playback, recording, and mixing.
Callback-based pipeline: tracks → mix → effects → master → output.

64-bit float internal. Sample-accurate. Low-latency.
This is what makes it a DAW instead of a file processor.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import logging
import time
from pathlib import Path
from collections import OrderedDict

logger = logging.getLogger("sozawen.engine")


class Region:
    """A clip of audio on a track — references a source file without copying it."""

    def __init__(self, source_path, start_sample=0, track_offset=0,
                 length=None, gain=1.0, name="", source_type="imported"):
        self.source_path = str(source_path)
        self.start_sample = start_sample      # where in the source file to start reading
        self.track_offset = track_offset       # where on the timeline this region sits (in samples)
        self.gain = gain
        self.name = name or Path(source_path).stem
        self.source_type = source_type         # "recorded", "imported", "generated"
        self.reversed = False
        self.muted = False

        # Load source info (but NOT the full audio — lazy load for playback)
        try:
            info = sf.info(self.source_path)
            self.sample_rate = info.samplerate
            self.channels = info.channels
            self.total_source_samples = info.frames
            self.length = length or self.total_source_samples
        except Exception as e:
            logger.warning("Could not read source info for %s: %s", source_path, e)
            self.sample_rate = 44100
            self.channels = 2
            self.total_source_samples = 0
            self.length = 0

        # Cached audio data (loaded on first read)
        self._cache = None
        self._cache_lock = threading.Lock()

    @property
    def end_sample(self):
        return self.track_offset + self.length

    def read(self, start, count):
        """Read samples from this region. Returns numpy array (count, channels) or None."""
        # Is the requested range within this region?
        region_start = self.track_offset
        region_end = self.end_sample

        if start >= region_end or start + count <= region_start or self.muted:
            return None

        # How much of the request overlaps with this region
        read_start = max(0, start - region_start)
        read_end = min(self.length, start + count - region_start)
        out_start = max(0, region_start - start)
        out_count = read_end - read_start

        if out_count <= 0:
            return None

        # Lazy load source audio
        self._ensure_cached()
        if self._cache is None:
            return None

        # Read from cache
        src_start = self.start_sample + read_start
        src_end = src_start + out_count

        if src_end > len(self._cache):
            src_end = len(self._cache)
            out_count = src_end - src_start

        if out_count <= 0:
            return None

        data = self._cache[src_start:src_end].copy()

        if self.reversed:
            data = data[::-1].copy()

        data *= self.gain

        # Place in output buffer at correct offset
        output = np.zeros((count, data.shape[1] if data.ndim > 1 else 1), dtype=np.float64)
        actual_count = min(out_count, count - out_start)
        if data.ndim == 1:
            output[out_start:out_start + actual_count, 0] = data[:actual_count]
        else:
            output[out_start:out_start + actual_count, :data.shape[1]] = data[:actual_count]

        return output

    def _ensure_cached(self):
        if self._cache is not None:
            return
        with self._cache_lock:
            if self._cache is not None:
                return
            try:
                data, sr = sf.read(self.source_path, dtype='float64')
                if data.ndim == 1:
                    data = data.reshape(-1, 1)
                # Ensure stereo
                if data.shape[1] == 1:
                    data = np.column_stack([data, data])
                self._cache = data
                logger.info("Cached: %s (%d samples, %d ch)", self.name, len(data), data.shape[1])
            except Exception as e:
                logger.error("Failed to load %s: %s", self.source_path, e)


class Track:
    """A single track in the session — holds regions and mix state."""

    _next_id = 0

    def __init__(self, name="", track_type="audio", color="#9b59b6"):
        self.id = Track._next_id
        Track._next_id += 1
        self.name = name or f"Track {self.id + 1}"
        self.track_type = track_type  # "audio", "bus", "master", "folder"
        self.color = color
        self.regions = []
        self.volume = 1.0         # linear gain (0.0 - 2.0)
        self.pan = 0.0            # -1.0 (left) to 1.0 (right)
        self.muted = False
        self.solo = False
        self.record_armed = False
        self.input_device = None
        self.input_channel = 0    # which input channel this track records from (0-based)
        self.phase_invert = False  # flip phase (polarity) — for multi-mic
        self.fx_chain = []        # list of effect instances
        self.automation = {}      # param_name -> list of (sample, value) breakpoints
        self.parent_id = None     # for folder grouping
        self.sends = []           # list of (bus_track_id, send_gain)

    def read_at(self, position, count):
        """Mix all regions at the given position. Returns (count, 2) float64 array."""
        output = np.zeros((count, 2), dtype=np.float64)

        for region in self.regions:
            data = region.read(position, count)
            if data is not None:
                # Ensure stereo
                if data.shape[1] == 1:
                    data = np.column_stack([data, data])
                elif data.shape[1] > 2:
                    data = data[:, :2]
                output[:data.shape[0], :] += data[:output.shape[0], :]

        # Apply track gain
        output *= self.volume

        # Apply pan (constant power panning)
        if self.pan != 0.0:
            angle = (self.pan + 1.0) * np.pi / 4.0  # 0 to pi/2
            output[:, 0] *= np.cos(angle)
            output[:, 1] *= np.sin(angle)

        return output

    def add_region(self, source_path, track_offset=0, **kwargs):
        region = Region(source_path, track_offset=track_offset, **kwargs)
        self.regions.append(region)
        return region

    @property
    def duration_samples(self):
        if not self.regions:
            return 0
        return max(r.end_sample for r in self.regions)


class AudioEngine:
    """The real-time audio pipeline.

    Runs in a sounddevice callback. Reads from tracks, mixes,
    applies master effects, outputs to speakers. Sample-accurate.
    """

    def __init__(self, sample_rate=44100, buffer_size=1024, channels=2):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.tracks = OrderedDict()  # id -> Track
        self.master = Track(name="Master", track_type="master")

        # Transport state
        self.position = 0          # current playback position in samples
        self.playing = False
        self.recording = False
        self.looping = False
        self.loop_start = 0
        self.loop_end = 0

        # Metronome
        self.metronome_on = False
        self.bpm = 120.0
        self.time_sig_num = 4
        self.time_sig_den = 4

        # Output stream
        self._stream = None
        self._input_stream = None
        self._record_buffers = {}  # track_id -> list of numpy arrays
        self.input_monitoring = False
        self._monitor_buffer = None  # latest input audio for monitoring
        self._input_levels = {}     # per-channel peak levels for live metering

        # Metronome click during playback
        self._metronome_click = None
        self._metronome_click_samples = 0
        self._lock = threading.Lock()

        # Metering
        self.master_peak = [0.0, 0.0]
        self.track_peaks = {}

        logger.info("AudioEngine: %dHz, buffer %d, %dch", sample_rate, buffer_size, channels)

    def start(self):
        """Start the audio output stream."""
        if self._stream is not None:
            return

        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=self.channels,
            dtype='float32',
            callback=self._output_callback,
            latency='low',
        )
        self._stream.start()
        logger.info("Audio output started")

    def stop(self):
        """Stop audio output."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self.playing = False
        self.recording = False

    def play(self):
        self.playing = True
        if not self._stream:
            self.start()

    def pause(self):
        self.playing = False

    def stop_transport(self):
        self.playing = False
        self.recording = False
        self.position = 0

    def seek(self, sample_position):
        self.position = max(0, sample_position)

    def seek_seconds(self, seconds):
        self.seek(int(seconds * self.sample_rate))

    def record(self, track_id=None):
        """Start recording on armed tracks."""
        self.recording = True
        self.playing = True
        if not self._stream:
            self.start()

        # Start input capture for armed tracks
        armed = [t for t in self.tracks.values() if t.record_armed]
        if not armed and track_id is not None:
            track = self.tracks.get(track_id)
            if track:
                track.record_armed = True
                armed = [track]

        for track in armed:
            self._record_buffers[track.id] = []

        # Start input stream if not running — open all available channels
        if armed and self._input_stream is None:
            try:
                # Query how many channels the selected device supports
                device_info = sd.query_devices(sd.default.device[0], 'input')
                max_channels = device_info['max_input_channels']
                self._input_channels = max_channels
                logger.info("Input device: %s (%d channels)",
                            device_info['name'], max_channels)

                self._input_stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.buffer_size,
                    channels=max_channels,
                    dtype='float32',
                    callback=self._input_callback,
                    latency='low',
                )
                self._input_stream.start()
                logger.info("Recording started on %d tracks, %d input channels",
                            len(armed), max_channels)
            except Exception as e:
                logger.error("Failed to start recording: %s", e)

    def stop_recording(self):
        """Stop recording and finalize captured audio."""
        self.recording = False

        if self._input_stream:
            self._input_stream.stop()
            self._input_stream.close()
            self._input_stream = None

        # Save recorded audio to files and create regions
        for track_id, buffers in self._record_buffers.items():
            if not buffers:
                continue
            track = self.tracks.get(track_id)
            if not track:
                continue

            audio = np.concatenate(buffers, axis=0)
            # Save to project directory
            from datetime import datetime
            filename = f"recording_{track.name}_{datetime.now().strftime('%H%M%S')}.wav"
            filepath = Path("recordings") / filename
            filepath.parent.mkdir(exist_ok=True)
            sf.write(str(filepath), audio, self.sample_rate)

            # Add as region on the track
            track.add_region(str(filepath), track_offset=self.position - len(audio),
                           source_type="recorded", name=filename)
            logger.info("Saved recording: %s (%d samples)", filename, len(audio))

        self._record_buffers.clear()
        for track in self.tracks.values():
            track.record_armed = False

    def _output_callback(self, outdata, frames, time_info, status):
        """Real-time audio output callback — called by sounddevice."""
        if not self.playing:
            outdata[:] = 0
            return

        with self._lock:
            mix = np.zeros((frames, 2), dtype=np.float64)

            # Check solo state
            any_solo = any(t.solo for t in self.tracks.values())

            # Read and mix all tracks
            for track_id, track in self.tracks.items():
                if track.muted:
                    continue
                if any_solo and not track.solo:
                    continue
                if track.track_type in ("bus", "master"):
                    continue

                track_audio = track.read_at(self.position, frames)
                if track.phase_invert:
                    track_audio = -track_audio
                mix += track_audio

                # Track metering
                peak_l = float(np.max(np.abs(track_audio[:, 0])))
                peak_r = float(np.max(np.abs(track_audio[:, 1])))
                self.track_peaks[track_id] = [peak_l, peak_r]

            # Metronome — click on each beat during playback
            if self.metronome_on and self.playing:
                beat_samples = int(60.0 / self.bpm * self.sample_rate)
                pos_in_beat = self.position % beat_samples
                if pos_in_beat < 600:  # short click at start of beat
                    is_downbeat = (self.position // beat_samples) % self.time_sig_num == 0
                    click_freq = 1500 if is_downbeat else 1000
                    click_vol = 0.4 if is_downbeat else 0.25
                    t = np.arange(min(frames, 600 - pos_in_beat)) / self.sample_rate
                    click = np.sin(2 * np.pi * click_freq * t) * click_vol * np.exp(-t * 200)
                    mix[:len(click), 0] += click
                    mix[:len(click), 1] += click

            # Input monitoring — mix live input into output
            if self.input_monitoring and self._monitor_buffer is not None:
                mon = self._monitor_buffer
                mon_frames = min(len(mon), frames)
                if mon.ndim == 1:
                    mix[:mon_frames, 0] += mon[:mon_frames] * 0.8
                    mix[:mon_frames, 1] += mon[:mon_frames] * 0.8
                else:
                    mix[:mon_frames] += mon[:mon_frames, :2] * 0.8

            # Master volume
            mix *= self.master.volume

            # Master metering
            self.master_peak[0] = float(np.max(np.abs(mix[:, 0])))
            self.master_peak[1] = float(np.max(np.abs(mix[:, 1])))

            # Clip protection
            mix = np.clip(mix, -1.0, 1.0)

            # Output (convert to float32 for sounddevice)
            outdata[:] = mix[:frames].astype(np.float32)

            # Advance position
            self.position += frames

            # Loop control
            if self.looping:
                loop_end = self.loop_end if self.loop_end > 0 else self.duration_samples
                if loop_end > 0 and self.position >= loop_end:
                    self.position = self.loop_start

            # Loop handling
            if self.looping and self.position >= self.loop_end:
                self.position = self.loop_start

    def _input_callback(self, indata, frames, time_info, status):
        """Record input audio to armed track buffers + monitoring.

        Multi-channel: each track gets only its assigned input channel.
        """
        audio = indata.copy().astype(np.float64)
        n_channels = audio.shape[1] if audio.ndim > 1 else 1

        # Store for input monitoring (even when not recording)
        if self.input_monitoring:
            self._monitor_buffer = audio

        # Compute per-channel peak levels for live metering
        n_ch = audio.shape[1] if audio.ndim > 1 else 1
        for ch in range(n_ch):
            ch_data = audio[:, ch] if audio.ndim > 1 else audio
            peak = float(np.max(np.abs(ch_data)))
            self._input_levels[ch] = peak

        if not self.recording:
            return

        for track_id in self._record_buffers:
            track = self.tracks.get(track_id)
            if not track:
                continue
            # Get the assigned channel for this track
            ch = track.input_channel if hasattr(track, 'input_channel') else 0
            ch = min(ch, n_channels - 1)  # clamp to available channels

            if n_channels == 1 or audio.ndim == 1:
                # Mono input — all tracks get the same signal
                self._record_buffers[track_id].append(audio.reshape(-1, 1) if audio.ndim == 1 else audio)
            else:
                # Multi-channel — extract assigned channel as mono
                channel_audio = audio[:, ch:ch+1]
                self._record_buffers[track_id].append(channel_audio)

    # ═══════════════════════════════════════════════════════════════
    # Track management
    # ═══════════════════════════════════════════════════════════════

    def add_track(self, name="", track_type="audio", color=None):
        track = Track(name=name, track_type=track_type,
                     color=color or "#9b59b6")
        self.tracks[track.id] = track
        logger.info("Track added: %s (id=%d, type=%s)", track.name, track.id, track_type)
        return track

    def remove_track(self, track_id):
        if track_id in self.tracks:
            del self.tracks[track_id]

    def get_duration_seconds(self):
        if not self.tracks:
            return 0
        max_samples = max((t.duration_samples for t in self.tracks.values()), default=0)
        return max_samples / self.sample_rate

    def get_position_seconds(self):
        return self.position / self.sample_rate

    def get_state(self):
        """Serializable state for the UI."""
        return {
            "playing": self.playing,
            "recording": self.recording,
            "position": self.position,
            "position_seconds": self.get_position_seconds(),
            "duration_seconds": self.get_duration_seconds(),
            "bpm": self.bpm,
            "sample_rate": self.sample_rate,
            "master_peak": self.master_peak,
            "track_peaks": self.track_peaks,
            "tracks": [{
                "id": t.id,
                "name": t.name,
                "type": t.track_type,
                "color": t.color,
                "muted": t.muted,
                "solo": t.solo,
                "armed": t.record_armed,
                "volume": t.volume,
                "pan": t.pan,
                "regions": [{
                    "name": r.name,
                    "source_type": r.source_type,
                    "offset": r.track_offset,
                    "length": r.length,
                    "gain": r.gain,
                } for r in t.regions],
            } for t in self.tracks.values()],
        }


# ═══════════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Sozawen Audio Engine — test")

    engine = AudioEngine(sample_rate=44100, buffer_size=1024)

    # Add a track
    track = engine.add_track("Test Track")

    # Check if there's a test file
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        track.add_region(path, source_type="imported")
        print(f"Loaded: {path}")
        print(f"Duration: {engine.get_duration_seconds():.1f}s")

        engine.play()
        print("Playing... (Ctrl+C to stop)")
        try:
            while engine.playing and engine.position < track.duration_samples:
                time.sleep(0.1)
                pos = engine.get_position_seconds()
                peak = max(engine.master_peak)
                bar = '#' * int(peak * 40)
                print(f"\r  {pos:6.1f}s  [{bar:<40}]", end='', flush=True)
        except KeyboardInterrupt:
            pass
        engine.stop()
        print("\nDone.")
    else:
        print("Usage: python audio_engine.py <audio_file>")
        print("Engine initialized successfully.")
