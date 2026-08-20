import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def write(reg, data):
    spi.writebytes([reg, data])

# Init MAX7219
write(0x09, 0x00)  # decode off
write(0x0A, 0x08)  # brightness
write(0x0B, 0x07)  # scan limit
write(0x0C, 0x01)  # shutdown off
write(0x0F, 0x00)  # test off

# Clear
for i in range(1, 9):
    write(i, 0x00)

time.sleep(1)

# Turn on all LEDs
for i in range(1, 9):
    write(i, 0xFF)
