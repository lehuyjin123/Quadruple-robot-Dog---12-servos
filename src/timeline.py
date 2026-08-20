# Timeline.py

TRACK_1 = (0.0, 29.18)
TRACK_2 = (30.14, 123.13)
TRACK_3 = (126.10, 180.0)

def get_track(t):
    # Track 1 + transition
    if 0.0 <= t < TRACK_2[0]:
        return 1

    # Track 2 + transition
    elif TRACK_2[0] <= t < TRACK_3[0]:
        return 2

    # Track 3
    elif TRACK_3[0] <= t < TRACK_3[1]:
        return 3

    # End
    else:
        return 0
