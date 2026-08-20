from evdev import InputDevice, categorize, ecodes
from select import select
import numpy as np
import time




class Joystick:
    """
    evdev-based joystick
    Architecture aligned with Miguel's original controller
    """


    def __init__(self, event):
        self.gamepad = InputDevice(event)


        # Raw stick values (-1..1)
        self._raw_L3 = np.array([0., 0.])  # ABS_X, ABS_Y
        self._raw_R3 = np.array([0., 0.])  # ABS_RZ, ABS_Z


        # Smoothed outputs (±127 scale)
        self.L3 = np.array([0., 0.])
        self.R3 = np.array([0., 0.])


        # Filters
        self._alpha = 0.25
        self._deadzone = 0.15
        self._rate_hz = 50.0
        self._min_interval = 1.0 / self._rate_hz
        self._last_send = 0.0
        self._prev_output = None


        # Control states (KEEP ALL ORIGINAL VALUES)
        self.T = 1.8
        self.V = 0.
        self.angle = 0.
        self.Wrot = 0.
        self.compliantMode = False
        self.poseMode = False


        # Center of Mass (persistent like Miguel)
        self.CoM_pos = np.zeros(3)   # [X, Y, Z]
        self.CoM_orn = np.zeros(3)   # [Roll, Pitch, Yaw]


        self.calibration = 0


        # =========================
        # ORIENTATION GAIN (NEW)
        # =========================
        # Old: /3.0  -> too aggressive (~42 deg)
        # New: /8.0  -> smooth & safe (~16 deg)
        self.ORN_GAIN = 8.0




    # =========================
    # Helpers
    # =========================
    def _norm_axis(self, val):
        return (val - 128) / 127.0


    def _apply_deadzone(self, v, dz):
        if abs(v) < dz:
            return 0.0
        sign = 1.0 if v > 0 else -1.0
        return sign * (abs(v) - dz) / (1.0 - dz)


    def _scale_to_127(self, v):
        return v * 127.0




    # =========================
    # MAIN READ
    # =========================
    def read(self):


        now = time.time()
        r, _, _ = select([self.gamepad.fd], [], [], 0.)


        if r:
            for event in self.gamepad.read():


                # -------------------------
                # BUTTONS
                # -------------------------
                if event.type == ecodes.EV_KEY and event.value == 1:


                    if event.code == ecodes.BTN_SOUTH:   # A
                        self.compliantMode = not self.compliantMode


                    elif event.code == ecodes.BTN_NORTH: # Y
                        self.poseMode = not self.poseMode


                    elif event.code == ecodes.BTN_TL:    # LB
                        self.calibration -= 5


                    elif event.code == ecodes.BTN_TR:    # RB
                        self.calibration += 5




                # -------------------------
                # AXES
                # -------------------------
                elif event.type == ecodes.EV_ABS:
                    abse = categorize(event)
                    code = abse.event.code
                    val = abse.event.value


                    # Left stick
                    if code == ecodes.ABS_X:
                        self._raw_L3[0] = self._norm_axis(val)
                    elif code == ecodes.ABS_Y:
                        self._raw_L3[1] = -self._norm_axis(val)


                    # Right stick
                    elif code == ecodes.ABS_RZ:
                        self._raw_R3[0] = self._norm_axis(val)
                    elif code == ecodes.ABS_Z:
                        self._raw_R3[1] = -self._norm_axis(val)


                    # D-pad (ALWAYS ACTIVE – like Miguel)
                    elif code == ecodes.ABS_HAT0X:
                        if val == -1:
                            self.T -= 0.05
                        elif val == 1:
                            self.T += 0.05


                    elif code == ecodes.ABS_HAT0Y:
                        if val == -1:
                            self.CoM_pos[2] += 0.002
                        elif val == 1:
                            self.CoM_pos[2] -= 0.002




        # =========================
        # FILTERING
        # =========================
        lx = self._apply_deadzone(self._raw_L3[0], self._deadzone)
        ly = self._apply_deadzone(self._raw_L3[1], self._deadzone)
        rx = self._apply_deadzone(self._raw_R3[0], self._deadzone)
        ry = self._apply_deadzone(self._raw_R3[1], self._deadzone)


        target_L3 = np.array([
            self._scale_to_127(lx),
            self._scale_to_127(ly)
        ])


        target_R3 = np.array([
            self._scale_to_127(rx),
            self._scale_to_127(ry)
        ])


        self.L3 = self._alpha * target_L3 + (1 - self._alpha) * self.L3
        self.R3 = self._alpha * target_R3 + (1 - self._alpha) * self.R3




        # =========================
        # MODE LOGIC (MIGUEL STYLE)
        # =========================
        if not self.poseMode:
            # WALK MODE
            self.V = np.sqrt(self.L3[1]**2 + self.L3[0]**2) / 100.0
            self.angle = np.rad2deg(np.arctan2(-self.L3[0], -self.L3[1]))
            self.Wrot = -self.R3[0] / 250.0


            if self.V <= 0.035:
                self.V = 0.0
            if -0.035 <= self.Wrot <= 0.035:
                self.Wrot = 0.0


            # IMPORTANT: only reset orientation, NOT height
            self.CoM_orn[:] = 0.0
            self.CoM_pos[0:2] = 0.0


        else:
            # POSE MODE (SOFTENED)
            self.CoM_orn[0] = np.deg2rad(self.R3[0] / self.ORN_GAIN)   # Roll
            self.CoM_orn[1] = np.deg2rad(self.L3[1] / self.ORN_GAIN)   # Pitch
            self.CoM_orn[2] = -np.deg2rad(self.L3[0] / self.ORN_GAIN)  # Yaw


            self.CoM_pos[0] = -self.R3[1] / 8000.0   # softer forward shift


            self.V = 0.0
            self.angle = 0.0
            self.Wrot = 0.0




        output = (
            self.CoM_pos,
            self.CoM_orn,
            self.V,
            -self.angle,
            -self.Wrot,
            self.T,
            self.compliantMode
        )




        # =========================
        # RATE LIMIT
        # =========================
        if self._prev_output is None:
            self._prev_output = output
            self._last_send = now
            return output


        if now - self._last_send < self._min_interval:
            return self._prev_output


        self._last_send = now
        self._prev_output = output
        return output





