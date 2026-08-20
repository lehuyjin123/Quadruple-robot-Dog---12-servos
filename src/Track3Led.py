# Track3Led.py
import math

def run(t, led):
    level = int((math.sin(2 * math.pi * 2 * t) + 1) * 3)
    led.show_wave(level)
