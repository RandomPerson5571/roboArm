import serial
import time
import threading

class ArduinoController:
    def __init__(self, port='COM3', baudrate=9600):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
        self.running = True
        time.sleep(2)  # Wait for Arduino reset
        
        # Start the background thread to constantly read serial data
        self.read_thread = threading.Thread(target=self._listen_to_arduino, daemon=True)
        self.read_thread.start()

    def _listen_to_arduino(self):
        """Background thread loop that reads data without blocking the main program."""
        while self.running:
            if self.arduino.in_waiting > 0:
                try:
                    # Read what's in the buffer
                    response = self.arduino.readline().decode('utf-8').strip()
                    if response:
                        print(f"\n[Arduino]: {response}")
                        self.handle_response(response)
                except Exception as e:
                    print(f"Read error: {e}")
            time.sleep(0.01) # Small sleep to prevent 100% CPU usage

    def handle_response(self, response):
        """Process incoming messages from Arduino here."""
        if response == "TASK_COMPLETED":
            print("Success! Task finished.")
        elif response == "CANCELLED":
            print("Arduino confirmed the cancellation.")

    def send_command(self, command):
        """Send a command to the Arduino immediately."""
        print(f"[Python] Sending: {command}")
        self.arduino.write(f"{command}\n".encode('utf-8'))

    def close(self):
        self.running = False
        self.arduino.close()