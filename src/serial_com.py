import serial
import time
import numpy

class ArduinoSerial:
    def __init__(self , port):
        self.arduino = serial.Serial(port, 115200, timeout = 1)
        self.arduino.setDTR(False)
        time.sleep(1)
        self.arduino.flushInput()
        self.arduino.setDTR(True)
        time.sleep(2)
        self.lastTime = 0.
        self.previousMillis = 0.
        self.interval = 0.02

    def serialSend(self, pulse):  
        comando = "<{0}#{1}#{2}#{3}#{4}#{5}#{6}#{7}#{8}#{9}#{10}#{11}>"
        command = comando.format(int(pulse[0]), int(pulse[1]), int(pulse[2]), 
                                 int(pulse[3]), int(pulse[4]), int(pulse[5]), 
                                 int(pulse[6]), int(pulse[7]), int(pulse[8]), 
                                 int(pulse[9]), int(pulse[10]), int(pulse[11]))
        self.arduino.write(command.encode('utf8'))
        self.lastTime = time.time()
        # DEBUG: show exactly what was sent
        print("[TX -> Arduino]:", command)

    def serialRecive(self):
        try:
            startMarker = 60   # '<'
            endMarker = 62     # '>'
            getSerialValue = bytes()
            x = "z"  # any value not start/end
            byteCount = -1
            
            # Wait for start marker
            while ord(x) != startMarker: 
                x = self.arduino.read()
            
            # Read until end marker
            while ord(x) != endMarker:
                if ord(x) != startMarker:
                    getSerialValue += x
                    byteCount += 1
                x = self.arduino.read()
            
            # DEBUG: show raw received string
            raw_str = getSerialValue.decode('ascii', errors='replace')
            print("[RX <- Arduino]:", raw_str)
            
            loopTime , Xacc , Yacc , roll , pitch  = numpy.fromstring(getSerialValue.decode('ascii', errors='replace'), sep = '#' )
                    
        except ValueError:
            loopTime = 0.
            Xacc = 0.
            Yacc = 0.
            roll = 0.
            pitch = 0.
            pass
        
        self.arduino.flushInput()
        return loopTime, Xacc, Yacc, roll, pitch

    def close(self):
        self.arduino.close()
