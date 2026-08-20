# -*- coding: utf-8 -*-
"""
Track1Led.py: LED Logic for Track 1. Shows a cycle of LOADING, FAILED, and 
TRYING states, transitioning to a TICK icon (success) at the end (28.0s to 29.18s).
"""
import time
import numpy as np # Included for potential future use

# --- Timing Constants (from src/timeline.py) ---
TRACK_START = 0.0
TRACK_END = 29.18
TICK_TIME_START = 28.0 

# --- Custom Cycle Constants based on user request (4.5 seconds total cycle) ---
# Increased from 2.1s to 4.5s for a slower, smoother transition.
CYCLE_DURATION = 3.5  # Total time for one full cycle: LOADING -> FAILED -> TRYING
STATE_DURATION = CYCLE_DURATION / 3.0 # Duration for each state (1.5s)

# LOADING animation has 3 frames (from Led8x8.py)
ANIMATION_FRAME_SPEED = STATE_DURATION / 3.0 # Duration per frame (0.5s)

STATES = ["LOADING", "FAILED", "TRYING"]

def run(t, led):
    """
    Controls the 8x8 LED matrix for the duration of Track 1.
    
    Args:
        t (float): Current time in seconds.
        led (Led8x8): Instance of the LED matrix driver.
    """
    # Guard clause: If time is outside the defined track, show NEUTRAL
    if t < TRACK_START or t >= TRACK_END:
        led.show("NEUTRAL") 
        return

    # --- State 1: Show TICK Icon (Success) at the end ---
    # From 28.0s up to 29.18s, show the successful completion icon.
    if t >= TICK_TIME_START:
        led.show("TICK")
        return

    # --- State 2: Show Cyclic Animation (LOADING, FAILED, TRYING) ---
    else:
        # Time relative to the start of the repeating cycle
        t_cycle = t % CYCLE_DURATION
        
        # Determine current state index (0=LOADING, 1=FAILED, 2=TRYING)
        state_idx = int(t_cycle // STATE_DURATION)
        state = STATES[state_idx]
        
        if state == "LOADING":
            # Time elapsed within the current LOADING state (0.0 to 1.5s)
            t_in_state = t_cycle - (STATE_DURATION * state_idx)
            
            # Calculate frame index (0, 1, or 2) for the LOADING animation (3 frames)
            frame_idx = int(t_in_state / ANIMATION_FRAME_SPEED)
            
            # Use the animated LOADING icon
            led.show("LOADING", frame_idx=frame_idx)
            
        else:
            # Show static FAILED or TRYING icon
            # Note: FAILED and TRYING are treated as static icons in the current Led8x8.py structure.
            led.show(state)
        
        return
