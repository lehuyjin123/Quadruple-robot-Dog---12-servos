#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DanceDirectory v2
Phrase-aware, weight-shifted dance choreography
Compatible with BeatEngine v2 + Miguel gait
"""

import math
import numpy as np


class DanceDirectory:
    def __init__(self):
        self.mode = 0          # motion style
        self.last_phrase = -1  # phrase memory

    def generate(self, beat, track):
        # =========================
        # DEFAULT OUTPUT
        # =========================
        pose = np.zeros(3)   # body position offset
        orn  = np.zeros(3)   # body orientation

        V = 0.0
        angle = 0.0
        Wrot = 0.0
        T = 0.45

        phase = 2 * math.pi * beat["beat_phase"]

        # =========================
        # PHRASE CHANGE ? SWITCH STYLE
        # =========================
        if beat["phrase_i"] != self.last_phrase:
            self.mode = (self.mode + 1) % 3
            self.last_phrase = beat["phrase_i"]

        # =====================================================
        # TRACK 2 GROOVE / BODY DANCE (NO TRAVEL)
        # =====================================================
        if track == 2:
            sway = math.sin(phase)
            slow = math.sin(phase * 0.5)

            # ---------- WEIGHT SHIFT ----------
            pose[1] = 0.025 * sway        # left-right CoM shift
            pose[0] = 0.010 * slow        # subtle forward/back

            # ---------- BODY ORIENTATION ----------
            if self.mode == 0:
                # Chill sway
                orn[0] = math.radians(6) * sway
                orn[1] = math.radians(4) * slow

            elif self.mode == 1:
                # Hip twist
                orn[2] = math.radians(12) * sway
                orn[1] = math.radians(3) * slow

            else:
                # Body wave
                orn[0] = math.radians(8) * sway
                orn[1] = math.radians(6) * math.sin(phase + math.pi / 2)

            # ---------- BEAT ACCENT ----------
            if beat["downBeat"]:
                pose[2] = 0.035   # stomp squat
            else:
                pose[2] = 0.015 * (1 - math.cos(phase))

            # keep gait alive but subtle
            V = 0.01
            Wrot = 0.0
            T = 0.8

        # =====================================================
        # TRACK 3  DROP / ENERGY / POWER
        # =====================================================
        elif track == 3:
            drive = max(0.0, math.sin(phase))
            twist = math.sin(phase * 0.5)

            # ---------- MOVEMENT ----------
            V = 0.05 * drive
            Wrot = 0.6 * twist

            # ---------- WEIGHT SHIFT ----------
            pose[1] = 0.03 * math.sin(phase)
            pose[0] = 0.015 * drive

            # ---------- BODY ORIENTATION ----------
            orn[0] = math.radians(12) * drive
            orn[1] = math.radians(8) * math.sin(phase * 2)

            # ---------- STRONG DOWNBEAT ----------
            if beat["downBeat"]:
                pose[2] = 0.05    # deep punch squat
            else:
                pose[2] = 0.025 * drive

            T = 0.32

        # =====================================================
        # TRACK 1  INTRO / IDLE
        # =====================================================
        else:
            orn[1] = math.radians(4) * math.sin(phase * 0.5)
            pose[2] = 0.01 * (1 - math.cos(phase))

            V = 0.0
            Wrot = 0.0
            T = 0.6

        return pose, orn, V, angle, Wrot, T
