#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
dance.py
Che do nhay nhe nhang cho Miguel.
Track 1: Dung yen.
Track 2 & 3: Nhay nhip nhang voi bien do vua phai.
"""

import time
import numpy as np
import math

# =========================
# CAC MODULE CUA ROBOT MIGUEL
# =========================
try:
    from src.kinematic_model import robotKinematics
    from src.serial_com import ArduinoSerial
    from src import angleToPulse
    from src.gaitPlanner import trotGait
    from src.timeline import get_track
    from src.led8x8 import Led8x8
    from src import Track1Led, Track2Led, Track3Led
except ImportError as e:
    print(f"[ERROR] Thieu module: {e}")
    exit()

# =========================
# KHOI TAO HE THONG
# =========================
FPS = 30 
DT = 1.0 / FPS
HEIGHT_DEFAULT = 0.16
TAU = 2.0 * math.pi

robot = robotKinematics()
arduino = ArduinoSerial("/dev/ttyACM0") 
trot = trotGait()
led = Led8x8()

# Tu the dung mac dinh
bodytoFeet0 = np.array([
    [ 0.085, -0.075, -HEIGHT_DEFAULT],  # FR
    [ 0.085,  0.075, -HEIGHT_DEFAULT],  # FL
    [-0.11 , -0.075, -HEIGHT_DEFAULT],  # BR
    [-0.11 ,  0.075, -HEIGHT_DEFAULT],  # BL
], dtype=float)

orn = np.zeros(3)
pos = np.zeros(3)

start_time = time.time()
last_time = start_time

print("[INFO] Miguel dang san sang... Track 1 se dung yen.")

# =========================
# VONG LAP CHINH
# =========================
try:
    while True:
        now = time.time()
        if now - last_time < DT:
            continue

        last_time = now
        t = now - start_time
        track = get_track(t)

        if track == 0:
            break

        # DIEU KHIEN LED
        if track == 1:
            Track1Led.run(t, led)
        elif track == 2:
            Track2Led.run(t, led)
        elif track == 3:
            Track3Led.run(t, led)

        # TINH TOAN NHIP (PHASE)
        bpm = 120 
        if track == 1: bpm = 60
        elif track == 2: bpm = 120
        elif track == 3: bpm = 128
        
        phase = TAU * ((t * bpm / 60.0) % 1.0)

        # LOGIC CHUYEN DONG
        commandOrn = np.zeros(3)   # [Roll, Pitch, Yaw]
        commandPose = np.zeros(3)  # [X, Y, Z]

        # ---------- TRACK 1: DUNG YEN ----------
        if track == 1:
            # Dung yen hoan toan
            pass

        # ---------- TRACK 2: NHE NHANG ----------
        elif track == 2:
            # Lac Roll nhe 7 do
            commandOrn[0] = math.radians(7.0) * math.sin(phase * 0.5)
            # Nhun Z khe 1cm
            commandPose[2] = 0.01 * math.cos(phase)
            # Xoay Yaw nhe
            commandOrn[2] = math.radians(4.0) * math.sin(phase * 0.5)

        # ---------- TRACK 3: SOI DONG VUA PHAI ----------
        elif track == 3:
            # Ket hop Pitch va Roll
            commandOrn[0] = math.radians(6.0) * math.sin(phase)
            commandOrn[1] = math.radians(6.0) * math.cos(phase)
            # Yaw bien do 8 do
            commandOrn[2] = math.radians(8.0) * math.sin(phase * 0.5)
            # Nhun 1.2cm
            commandPose[2] = 0.012 * math.sin(phase)

        # TINH TOAN IK VA GUI LENH
        total_orn = orn + commandOrn
        total_pos = pos + commandPose

        try:
            # Giai dong hoc nghich
            FR, FL, BR, BL, _ = robot.solve(total_orn, total_pos, bodytoFeet0)
            pulses = angleToPulse.convert(FR, FL, BR, BL)
            arduino.serialSend(pulses)
        except:
            pass

        print(f"T={t:6.2f}s | Track={track} | Chill mode... ", end="\r")

except KeyboardInterrupt:
    print("\n[INFO] Dung chuong trinh.")
finally:
    # Ve vi tri can bang
    FR, FL, BR, BL, _ = robot.solve(orn, pos, bodytoFeet0)
    pulses = angleToPulse.convert(FR, FL, BR, BL)
    arduino.serialSend(pulses)
    print("[INFO] Da ve tu the nghi.")
