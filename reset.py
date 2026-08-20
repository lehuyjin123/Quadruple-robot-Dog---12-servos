import serial
import time

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyACM0' # Make sure this matches your correct port!
BAUD_RATE = 115200 
RESET_PULSE = 1500
NUM_SERVOS = 12

# Create the reset command string: "1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500,1500\n"
RESET_STRING = (str(RESET_PULSE) + ',') * (NUM_SERVOS - 1) + str(RESET_PULSE) + '\n'

print(f"Attempting to reset servos to {RESET_PULSE}us...")

try:
    # 1. Initialize the serial connection
    # Ensure you are running this after activating your venv!
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Wait for the connection to establish

    print(f"Connected to Arduino on {SERIAL_PORT}")
    print(f"Sending reset command: {RESET_STRING.strip()}")

    # 2. Send the command string
    # We send it as bytes, encoded in UTF-8
    ser.write(RESET_STRING.encode('utf-8'))

    # 3. Wait for the command to be processed
    time.sleep(1) 
    
    # 4. Close the connection
    ser.close()
    print("Reset complete. Connection closed.")

except serial.SerialException as e:
    print(f"\n--- ERROR ---")
    print(f"Failed to connect to {SERIAL_PORT}.")
    print(f"Please check: 1. Is the port correct? 2. Is the Arduino powered? 3. Permissions?")
    print(f"Original Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
