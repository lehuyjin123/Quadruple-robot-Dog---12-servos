#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
gaitPlanner.py
Crawl gait version – fixed stance leg-length issue
Based on Miguel's quadruped gait structure


Author: adapted & fixed for UEH Dancing Robot
"""


import time
import math
import numpy as np




# =========================
# Bezier helper functions
# =========================


def comb(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))




def bernstein(t, k, p):
    t = max(0.0, min(1.0, float(t)))
    n = 9
    return p * comb(n, k) * (t ** k) * ((1.0 - t) ** (n - k))




# =========================
# Gait Planner (CRAWL)
# =========================


class trotGait:   # giữ tên class để không phải sửa file khác
    def __init__(self):


        self.bodytoFeet = np.zeros((4, 3), dtype=float)


        # phase
        self.phi = 0.0
        self.lastTime = 0.0
        self.alpha = 0.0


        # CRAWL OFFSETS (FR → FL → BR → BL)
        # order: [FR, FL, BR, BL]
        self.crawl_offsets = np.array([0.0, 0.25, 0.5, 0.75], dtype=float)


        # stance ratio (crawl = long stance)
        self.step_offset = 0.85


        self.min_step_T = 0.01




    # =========================
    # STANCE (FIXED)
    # =========================
    def calculateStance(self, phi, V, angle):
        """
        Stance phase:
        - Foot moves backward relative to body
        - Z compensated to keep leg length ~ constant
        """


        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))


        step_len = 0.06 * abs(V)


        # backward motion
        x = -c * step_len * phi
        y = -s * step_len * phi


        # LEG LENGTH COMPENSATION
        # As |x,y| increases → foot must go DOWN
        z = (x * x + y * y) * 0.6   # tuning gain


        return x, y, z




    # =========================
    # SWING (Bezier)
    # =========================
    def calculateSwing(self, phi, V, angle):
        """
        Swing phase:
        - Bezier curve
        - Z always negative (lift foot)
        """


        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))


        Vmag = V
        Vabs = abs(V)


        X = Vmag * c * np.array(
            [-0.06, -0.07, -0.08, -0.08, 0.0,
              0.0,  0.08,  0.08,  0.07, 0.06]
        )


        Y = Vmag * s * np.array(
            [ 0.06,  0.07,  0.08,  0.08, 0.0,
             -0.0, -0.08, -0.08, -0.07, -0.06]
        )


        Z = -Vabs * np.array(
            [0.0, 0.0, 0.04, 0.06, 0.07,
             0.07, 0.06, 0.04, 0.0, 0.0]
        )


        swingX = swingY = swingZ = 0.0
        for i in range(10):
            swingX += bernstein(phi, i, X[i])
            swingY += bernstein(phi, i, Y[i])
            swingZ += bernstein(phi, i, Z[i])


        return swingX, swingY, swingZ




    # =========================
    # PER-LEG TRAJECTORY
    # =========================
    def stepTrajectory(self, phi, V, angle, Wrot, centerToFoot):


        phi = phi % 1.0


        center = np.asarray(centerToFoot, dtype=float).reshape(3,)
        r = math.hypot(center[0], center[1])
        footAngle = math.atan2(center[1], center[0])


        # rotation heading
        if Wrot >= 0:
            rotAngle = 90.0 - math.degrees(footAngle - self.alpha)
        else:
            rotAngle = 270.0 - math.degrees(footAngle - self.alpha)


        # stance / swing
        if phi <= self.step_offset:
            p = phi / self.step_offset
            x1, y1, z1 = self.calculateStance(p, V, angle)
            x2, y2, z2 = self.calculateStance(p, Wrot, rotAngle)
        else:
            p = (phi - self.step_offset) / (1.0 - self.step_offset)
            x1, y1, z1 = self.calculateSwing(p, V, angle)
            x2, y2, z2 = self.calculateSwing(p, Wrot, rotAngle)


        # rotation alpha update
        mag = math.hypot(x2, y2)
        if r > 1e-6:
            self.alpha = math.atan2(mag, r)
        else:
            self.alpha = 0.0


        return np.array([x1 + x2, y1 + y2, z1 + z2])




    # =========================
    # MAIN LOOP
    # =========================
    def loop(self, V, angle, Wrot, T, offset, bodytoFeet_):


        if T is None or T < self.min_step_T:
            T = self.min_step_T


        if self.lastTime == 0.0:
            self.lastTime = time.time()


        self.phi = ((time.time() - self.lastTime) / T) % 1.0


        offs = self.crawl_offsets


        base = np.asarray(bodytoFeet_, dtype=float).reshape((4, 3))


        for i in range(4):
            center = base[i]
            step = self.stepTrajectory(self.phi + offs[i], V, angle, Wrot, center)


            self.bodytoFeet[i, 0] = base[i, 0] + step[0]
            self.bodytoFeet[i, 1] = base[i, 1] + step[1]
            self.bodytoFeet[i, 2] = base[i, 2] + step[2]


        return self.bodytoFeet





