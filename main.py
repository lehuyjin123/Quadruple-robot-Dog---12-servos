# -*- coding: utf-8 -*-
#!/usr/bin/env python3


import numpy as np
import time
import csv
 
from src.kinematic_model import robotKinematics
from src.joystick import Joystick
from src.serial_com import ArduinoSerial
from src import angleToPulse
from src.gaitPlanner import trotGait
from src.CoM_stabilization import stabilize


robotKinematics = robotKinematics()
joystick = Joystick('/dev/input/event0')
arduino = ArduinoSerial('/dev/ttyACM0') #need to specify the serial port
trot = trotGait() 
control = stabilize()


# --- ROBOT PROPERTIES ---
"""initial safe position"""
#angles (Chá»‰ lÃ  giÃ¡ trá»‹ khá»Ÿi táº¡o ban Ä‘áº§u, khÃ´ng Ä‘Æ°á»£c sá»­ dá»¥ng trong vÃ²ng láº·p chÃ­nh)
targetAngs = np.array([0 , np.pi/4 , -np.pi/2, 0 ,#BR
                        0 , np.pi/4 , -np.pi/2, 0 ,#BL
                        0 , np.pi/4 , -np.pi/2, 0 ,#FL
                        0 , np.pi/4 , -np.pi/2, 0 ])#FR


"initial foot position"
Ydist = 0.18
Xdist = 0.25
height = 0.16


# Chuyá»ƒn Ä‘á»•i tá»« np.matrix sang np.array Ä‘á»ƒ tÆ°Æ¡ng thÃ­ch tá»‘t hÆ¡n
bodytoFeet0 = np.array([[ 0.085 , -0.075 , -height], # FR
                         [ 0.085 ,  0.075 , -height], # FL
                         [-0.11 , -0.075 , -height], # BR
                         [-0.11 ,  0.075 , -height]], dtype=float) # BL


orn = np.array([0. , 0. , 0.])
pos = np.array([0. , 0. , 0.])
Upid_yorn = [0.]
Upid_y = [0.]
Upid_xorn = [0.]
Upid_x = [0.]


startTime = time.time()
lastTime = startTime
t = []
               
T = 0.4 #period of time (in seconds) of every step
offset = np.array([0. , 0.5 , 0.5 , 0.]) #defines the offset between each foot step in this order (FR,FL,BR,BL)
interval = 0.030 # Táº§n sá»‘ vÃ²ng láº·p ~33.3Hz


# --- MAIN LOOP ---
for k in range(100000000000):
    if (time.time()-lastTime >= interval):
        loopTime = time.time() - lastTime
        lastTime = time.time()
        t = time.time() - startTime
        
        # Äá»c input tá»« Joystick
        commandPose , commandOrn , V , angle , Wrot , T , compliantMode = joystick.read()  
        
        # Äá»c Serial tá»« Arduino
        arduinoLoopTime , Xacc , Yacc , realRoll , realPitch = arduino.serialRecive()
        
        # TÃ­nh toÃ¡n Body Compliant
        forceModule , forceAngle , Vcompliant , collision = control.bodyCompliant(Xacc , Yacc , compliantMode)
            
        # Tá»•ng váº­n tá»‘c (Joystick + Compliant)
        V_cmd = V       
        V_auto = Vcompliant
        V_total = V_cmd + V_auto
        
        # Láº­p káº¿ hoáº¡ch dÃ¡ng Ä‘i (Gait Planner)
        if np.linalg.norm(V_total) > 0.001 or abs(forceAngle) > 0.001:
                bodytoFeet = trot.loop(V_total, angle + forceAngle, Wrot, T, offset, bodytoFeet0)
        else:
                bodytoFeet = bodytoFeet0.copy()  # stay at default stance (no walking)


        
        # ---------------------------------------------------------------------------------
        #####   kinematics Model: Input body orientation, deviation and foot position    ####
        # ---------------------------------------------------------------------------------
        FR_angles, FL_angles, BR_angles, BL_angles , transformedBodytoFeet = robotKinematics.solve(
            orn + commandOrn,
            pos + commandPose ,
            bodytoFeet
        )
        pulsesCommand = angleToPulse.convert(FR_angles, FL_angles, BR_angles, BL_angles)


        arduino.serialSend(pulsesCommand)#send serial command to arduino
        
#         Upid_x , Upid_y , errorX , errorY , Upid_xorn , Upid_yorn = control.centerPoint(realPitch , realRoll)
#         orn[0] = Upid_xorn
#         orn[1] = Upid_yorn
#         pos[0] = Upid_x
#         pos[1] = Upid_y


        # --- DYNAMIC CONSOLE OUTPUT ---
        # Ghi Ä‘Ã¨ dÃ²ng console báº±ng thÃ´ng sá»‘ má»›i
        output_line = (
            f"T: {t:.2f}s | "
            f"Loop Time (RPI): {loopTime*1000:.1f}ms | "
            f"Loop Time (Arduino): {arduinoLoopTime:.1f}ms | "
            f"Roll: {realRoll:.2f}Â° | "
            f"Pitch: {realPitch:.2f}Â°"
        )
     
        print (output_line.ljust(120), end='\r')






