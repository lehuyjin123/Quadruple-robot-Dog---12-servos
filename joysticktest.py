import serial, time
s = serial.Serial('/dev/ttyACM0',115200)
while True:
    line = s.readline().decode(errors='ignore')
    print(line)
