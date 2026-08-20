import numpy as np

# --- 1. SERVO CONSTANTS ---
# SERVO_FACTOR: Based on 2000us / 270 degrees = 7.407 us/degree (Used for all 270 deg servos)
SERVO_FACTOR = 7.407 

# SERVO_FACTOR_180: Factor for the 180-degree servo (FL Tibia), in case you need it later.
SERVO_FACTOR_180 = 11.111 

DEG_TO_RAD = 180.0 / np.pi

# --- 2. CLAMPING LIMITS (500us to 2500us range) ---
MIN_PULSE = 500
MAX_PULSE = 2500


def convert(FR_angles, FL_angles, BR_angles, BL_angles):
    """
    Converts joint angles (in radians) into pulse widths (in microseconds)
    using the user's previously supplied offsets.
    """
    pulse = np.empty([12])
    
    # Radians to Degrees conversion
    FR_deg = FR_angles * DEG_TO_RAD
    FL_deg = FL_angles * DEG_TO_RAD
    BR_deg = BR_angles * DEG_TO_RAD
    BL_deg = BL_angles * DEG_TO_RAD
    
    # ----------------------------------------------------
    # --- FRONT-RIGHT (FR) - Signs match original working configuration ---
    # ----------------------------------------------------
    # pulse[0] = FRH (Coxa) - Bias: 1514. Sign is effectively (+)
    pulse[0] = int(-SERVO_FACTOR * FR_deg[0] * (-1)) + 1500
    
    # pulse[1] = FRF (Femur) - Bias: 1815. Sign is (-)
    pulse[1] = int(-SERVO_FACTOR * FR_deg[1]) + 1850
    
    # pulse[2] = FRT (Tibia) - Bias: 1403. Sign is (+), angle relative to -90 deg
    pulse[2] = int(SERVO_FACTOR * (FR_deg[2] + 90)) + 1413
    
    # ----------------------------------------------------
    # --- FRONT-LEFT (FL) - REVERTING COXA SIGN TO POSITIVE ---
    # ----------------------------------------------------
    # pulse[3] = FLH (Coxa) - Bias: 1484. REVERTED back to POSITIVE sign
    pulse[3] = int(SERVO_FACTOR * FL_deg[0]) + 1480
    
    # pulse[4] = FLF (Femur) - Bias: 1185. Sign is (+)
    pulse[4] = int(SERVO_FACTOR * FL_deg[1]) + 1205
    
    # pulse[5] = FLT (Tibia) - Bias: 1642. Reverting to standard factor 
    pulse[5] = int(-SERVO_FACTOR * (FL_deg[2] + 90)) + 1642 
    
    # ----------------------------------------------------
    # --- BACK-RIGHT (BR) - Signs match original working configuration ---
    # ----------------------------------------------------
    # pulse[6] = BRH (Coxa) - Bias: 1484. Sign is effectively (+)
    pulse[6] = int(SERVO_FACTOR * BR_deg[0] * (-1)) + 1484
    
    # pulse[7] = BRF (Femur) - Bias: 1820. Sign is (-)
    pulse[7] = int(-SERVO_FACTOR * BR_deg[1]) + 1800
    
    # pulse[8] = BRT (Tibia) - Bias: 1402. Sign is (+), angle relative to -90 deg
    pulse[8] = int(SERVO_FACTOR * (BR_deg[2] + 90)) + 1415
    
    # ----------------------------------------------------
    # --- BACK-LEFT (BL) - Signs match original working configuration ---
    # ----------------------------------------------------
    # pulse[9] = BLH (Coxa) - Bias: 1514. Sign is (-)
    pulse[9] = int(-SERVO_FACTOR * BL_deg[0]) + 1514
    
    # pulse[10] = BLF (Femur) - Bias: 1180. Sign is (+)
    pulse[10] = int(SERVO_FACTOR * BL_deg[1]) + 1120
    
    # pulse[11] = BLT (Tibia) - Bias: 1598. Sign is (-), angle relative to -90 deg
    pulse[11] = int(-SERVO_FACTOR * (BL_deg[2] + 90)) + 1598
    
    # --- CLAMPING: Apply unified limits to all 12 joints ---
    pulse = np.clip(pulse, MIN_PULSE, MAX_PULSE)

    return pulse
