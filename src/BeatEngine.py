#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BeatEngine v2
Stable, FPS-independent beat / bar / phrase engine
"""

import math


class BeatEngine:
    def __init__(self):
        self.bpm = {
            1: 54,
            2: 126,
            3: 128
        }

        self.beats_per_bar = 4
        self.phrase_bars = 4   # 4 bars = 16 beats

    def update(self, t, track):
        if track not in self.bpm:
            return self._empty()

        bpm = self.bpm[track]
        sec_per_beat = 60.0 / bpm
        sec_per_bar = sec_per_beat * self.beats_per_bar

        beat_f = t / sec_per_beat
        beat_i = int(beat_f)
        beat_phase = beat_f % 1.0   # 0..1

        bar_i = int(t / sec_per_bar)
        bar_phase = (t / sec_per_bar) % 1.0

        phrase_i = bar_i // self.phrase_bars
        phrase_phase = (bar_i % self.phrase_bars) / self.phrase_bars

        # Beat window (stable across FPS)
        hit = beat_phase < 0.18

        return {
            # --- BEAT ---
            "beat_f": beat_f,
            "beat_i": beat_i,
            "beat_phase": beat_phase,
            "hit": hit,

            # --- BAR ---
            "bar_i": bar_i,
            "bar_phase": bar_phase,
            "downBeat": hit and (beat_i % self.beats_per_bar == 0),

            # --- PHRASE ---
            "phrase_i": phrase_i,
            "phrase_phase": phrase_phase,
            "phrase_start": hit and (bar_i % self.phrase_bars == 0),

            # --- MUSICAL PHASE ---
            "sin": math.sin(2 * math.pi * beat_phase),
            "cos": math.cos(2 * math.pi * beat_phase)
        }

    def _empty(self):
        return {
            "beat_f": 0.0,
            "beat_i": 0,
            "beat_phase": 0.0,
            "hit": False,
            "bar_i": 0,
            "bar_phase": 0.0,
            "downBeat": False,
            "phrase_i": 0,
            "phrase_phase": 0.0,
            "phrase_start": False,
            "sin": 0.0,
            "cos": 1.0
        }
