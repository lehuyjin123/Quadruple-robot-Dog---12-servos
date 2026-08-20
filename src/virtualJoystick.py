#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
virtualJoystick.py
Dance signal generator (no physical joystick)
Phrase-based, beat-aware
Compatible with Miguel Hackaday quadruped
"""


import numpy as np
import math


TAU = 2.0 * math.pi




class VirtualJoystick:
    def __init__(self):
        # Output states (Miguel-compatible)
        self.commandPose = np.zeros(3)  # [x, y, z]
        self.commandOrn = np.zeros(3)   # [roll, pitch, yaw]


        self.V = 0.0
        self.angle = 0.0
        self.Wrot = 0.0
        self.T = 0.4
        self.compliantMode = False


    # ==================================================
    # PUBLIC API
    # ==================================================
    def read(self, t, track):
        """
        Called every control loop
        """
        self._reset()


        if track == 1:
            self._track1_intro()


        elif track == 2:
            self._track2_groove(t)


        elif track == 3:
            self._track3_climax(t)


        return (
            self.commandPose.copy(),
            self.commandOrn.copy(),
            self.V,
            self.angle,
            self.Wrot,
            self.T,
            self.compliantMode
        )


    # ==================================================
    # CORE HELPERS
    # ==================================================
    def _reset(self):
        self.commandPose[:] = 0.0
        self.commandOrn[:] = 0.0
        self.V = 0.0
        self.angle = 0.0
        self.Wrot = 0.0
        self.T = 0.4
        self.compliantMode = False


    def _beat(self, t, bpm):
        return TAU * (bpm / 60.0) * t


    # ==================================================
    # TRACK 1 INTRO (NO MOTION)
    # ==================================================
    def _track1_intro(self):
        """
        Robot stays perfectly still
        LEDs tell the story
        """
        pass


    # ==================================================
    # TRACK 2 GROOVE / BODY DANCE
    # ==================================================
    def _track2_groove(self, t):
        """
        Avicii  The Nights
        Smooth body groove, no gait
        """


        bpm = 126
        beat = self._beat(t, bpm)
        phrase = int(t // 4) % 4   # change move every 4 seconds


        # --- MOTION VARIANTS ---
        if phrase == 0:
            # Side sway (pitch)
            self.commandOrn[1] = math.radians(6.0) * math.sin(beat)


        elif phrase == 1:
            # Yaw twist
            self.commandOrn[2] = math.radians(10.0) * math.sin(0.5 * beat)


        elif phrase == 2:
            # Roll groove
            self.commandOrn[0] = math.radians(8.0) * math.sin(beat)


        else:
            # Body wave
            self.commandOrn[0] = math.radians(6.0) * math.sin(beat)
            self.commandOrn[1] = math.radians(4.0) * math.sin(beat + math.pi / 2.0)


        # --- SOFT BOUNCE ---
        self.commandPose[2] = 0.015 * (1.0 - math.cos(beat)) * 0.5


        # Relaxed timing
        self.T = 0.45


    # ==================================================
    # TRACK 3 CLIMAX / ACCENT DANCE
    # ==================================================
    def _track3_climax(self, t):
        """
        Avicii Broken Arrows (climax)
        Accent-based movement (NOT continuous sin)
        """


        bpm = 128
        beat = self._beat(t, bpm)


        # Beat phase [0, 1)
        beat_phase = (beat / TAU) % 1.0


        # Phrase changes every 4 beats
        phrase = int(t // (60.0 / bpm * 4.0)) % 3


        # Beat hit window
        hit = beat_phase < 0.15


        # -------------------------
        # PHRASE LOGIC
        # -------------------------
        if phrase == 0:
            # POWER STEP FORWARD
            self.V = 0.08 if hit else 0.0
            self.commandOrn[1] = math.radians(8.0) if hit else 0.0
            self.Wrot = 0.0


        elif phrase == 1:
            # TURN + STOMP
            self.V = 0.0
            self.Wrot = 1.0 if hit else 0.0
            self.commandOrn[0] = math.radians(10.0) if hit else 0.0


        else:
            # JUMP ILLUSION (Z accent)
            self.V = 0.0
            self.Wrot = 0.0


            if hit:
                self.commandPose[2] = 0.045
                self.commandOrn[1] = math.radians(-6.0)


        # -------------------------
        # TIMING & SAFETY
        # -------------------------
        self.angle = 0.0
        self.T = 0.80
        self.compliantMode = True





