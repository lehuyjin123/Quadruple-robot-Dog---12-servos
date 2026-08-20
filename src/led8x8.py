# MAX7219 8x8 LED matrix driver + predefined faces/animations




from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
import time
import numpy as np




class Led8x8:
    def __init__(self):
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(
            serial,
            cascaded=1,
            block_orientation=90,
            rotate=0
        )
        # To avoid dependency issues with numpy in Track2Led mock
        self.matrix = np.zeros((8, 8), dtype=int)




    # ======================
    # STATIC FACES
    # ======================
    FACES = {
        "NEUTRAL": [
            "00100100",
            "00100100",
            "00000000",
            "00000000",
            "01000010",
            "00111100",
            "00000000",
            "00000000",
        ],
        "SMILE": [
            "00100100",
            "00100100",
            "00000000",
            "00000000",
            "01000010",
            "00111100",
            "00000000",
            "00000000",
        ],
        "O": [
            "00100100",
            "00100100",
            "00000000",
            "00111100",
            "01000010",
            "01000010",
            "00111100",
            "00000000",
        ],
        "WIDE": [
            "00100100",
            "00100100",
            "00000000",
            "11111111",
            "10000001",
            "01000010",
            "00100100",
            "00011000",
        ],
        "CLOSED": [
            "00000000",
            "00000000",
            "00000000",
            "00000000",
            "00000000",
            "00111100",
            "00000000",
            "00000000",
        ],
    }




    # ======================
    # ICONS / ANIMATIONS
    # ======================
    ICONS = {
        # --- NEW: TICK Icon ---
        "TICK": [
            "00000001",
            "00000010",
            "10000100",
            "01001000",
            "00110000",
            "00000000",
            "00000000",
            "00000000",
        ],
        # --- Original Icons ---
        "LOADING": [
            [
                "00011000",
                "00100100",
                "01000010",
                "11111001",
                "11111001",
                "01000010",
                "00100100",
                "00011000",
            ],
            [
                "00011000",
                "00100100",
                "01000110",
                "10001101",
                "10011001",
                "01000010",
                "00100100",
                "00011000",
            ],
            [
                "00011000",
                "00100100",
                "01000010",
                "10011001",
                "10001101",
                "01000110",
                "00100100",
                "00011000",
            ],
        ],




        "FAILED": [
            "10000001",
            "01000010",
            "00100100",
            "00011000",
            "00011000",
            "00100100",
            "01000010",
            "10000001",
        ],




        "TRYING": [
            [
                "00011000",
                "00100100",
                "01000010",
                "10001001",
                "10000101",
                "01000010",
                "00100100",
                "00011000",
            ]
        ],
    }




    # ======================
    # LOW-LEVEL DRAW
    # ======================
    def _draw_bitmap(self, bitmap):
        # Convert list of strings (e.g., "00100100") to list of lists of "1" or "0"
        # for proper handling, but luma's canvas typically expects drawing commands.
        # Since the original implementation passed the bitmap directly, we adapt to that structure.
       
        # NOTE: The original Luma implementation typically uses a 1-bit PIL image
        # or simple draw commands. We adapt to the string list format:
        with canvas(self.device) as draw:
            for y, row_str in enumerate(bitmap):
                for x, bit_char in enumerate(row_str):
                    if bit_char == "1":
                        # In the luma library, draw.point expects a boolean/color value.
                        # Assuming "white" is the 'on' state for max7219.
                        draw.point((x, y), fill="white")




    def clear(self):
        with canvas(self.device):
            pass




    # ======================
    # PUBLIC API
    # ======================
    def show(self, name, frame_idx=0):
        """
        Show face or icon.
        frame_idx is used if the icon is animated.
        """
        if name in self.FACES:
            self._draw_bitmap(self.FACES[name])




        elif name in self.ICONS:
            icon = self.ICONS[name]




            # Animated icon (list of lists of strings)
            if isinstance(icon[0], list) and isinstance(icon[0][0], str) and len(icon[0][0]) == 8:
                idx = frame_idx % len(icon)
                self._draw_bitmap(icon[idx])
            # Static icon (list of strings)
            else:
                self._draw_bitmap(icon)




    # ======================
    # SOUNDWAVE (Track 3)
    # ======================
    def show_wave(self, level):
        """
        level: int 0..7
        """
        level = max(0, min(7, level))
        with canvas(self.device) as draw:
            for x in range(8):
                # Draw from the bottom (row 7) up to the level
                for y in range(7 - level, 8):
                    draw.point((x, y), fill="white")




    # ======================
    # DEBUG HELPERS
    # ======================
    def blink(self, name, times=3, interval=0.15):
        for _ in range(times):
            self.show(name)
            time.sleep(interval)
            self.clear()
            time.sleep(interval)



