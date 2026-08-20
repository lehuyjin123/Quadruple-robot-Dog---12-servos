# -*- coding: utf-8 -*-
"""
Track2Led.py: LED Logic for Track 2 (Avicii - The Nights). 
Implements a lip-sync and rhythmic pattern based on the song's BPM.
"""
import math

# --- Timing Constants (from src/timeline.py) ---
TRACK_START = 30.14
# Avicii - The Nights is ~126 BPM -> Beat period is T_beat = 60/126 ~ 0.476 seconds
BEAT_PERIOD = 0.25

# Define break periods (absolute time in seconds)
BREAK_PERIODS = [
    (49.5, 51.0),
    (72.0, 74.0),
    (90.0, 120.0) # Note: Track 2 ends at 123.13s based on timeline.py
]

def run(t, led):
    """
    Controls the 8x8 LED matrix for the duration of Track 2 using predefined faces.
    
    Args:
        t (float): Current time in seconds.
        led (Led8x8): Instance of the LED matrix driver.
    """
    # Time relative to the start of Track 2
    t_track = t - TRACK_START
    
    # If the track hasn't started, show neutral
    if t_track < 0:
        led.show("NEUTRAL")
        return

    # --- 0. Check for Break Periods (No Vocal/Rhythm Activity) ---
    is_in_break = False
    for start, end in BREAK_PERIODS:
        if start <= t < end:
            is_in_break = True
            break
            
    if is_in_break:
        # Show a neutral or closed face during the break
        led.show("NEUTRAL")
        return


    # --- 1. Calculate Rhythm & Beat Data ---
    
    # Time within one beat cycle (0.0 to BEAT_PERIOD)
    t_beat_cycle = t_track % BEAT_PERIOD
    
    # Beat index within a 4/4 measure (0, 1, 2, 3)
    beat_index = int((t_track // BEAT_PERIOD) % 4)
    
    # --- 2. Downbeat Accent (Must run before lip sync logic to ensure WIDE overrides) ---
    
    # A quick, intense flash on the main downbeat (beat 1 of the measure, index 0)
    # This remains quick (0.05s) for a sharp visual punch
    if beat_index == 0 and t_beat_cycle < 0.05:
        # Use the WIDE face for a quick, bright visual accent
        led.show("WIDE")
        return # Skip lip sync if flash is active

    # --- 3. Lip Sync / Vocal Rhythm ---
    
    # The primary vocal rhythm occurs on beats 1 and 3 (index 0 and 2)
    is_vocal_beat = beat_index == 0 or beat_index == 2
    
    # Mouth open phase (simulates vocal burst) - Use WIDE for happy 'open mouth'. 
    # Duration shortened to 25% of the beat (was 40%).
    if is_vocal_beat and t_beat_cycle < BEAT_PERIOD * 0.25:
        # Show 'WIDE' (cu?i to) for the strong vocal syllable
        led.show("WIDE")
        
    # Resting or filler beat (beat 2 and 4, or end of beat 1 & 3)
    else:
        # Show neutral face during non-vocal beats or resting periods
        led.show("NEUTRAL")
