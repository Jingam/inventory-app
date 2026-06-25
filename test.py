import sys
import time
import threading

# Global variable to control the printing speed
delay = 0.1  # Set to your desired 'slow print' speed

def wait_for_enter():
    global delay
    input()  # Waits for the user to press Enter
    delay = 0  # Changes the delay to zero instantly

# Start the listener thread in the background
threading.Thread(target=wait_for_enter, daemon=True).start()

def slow_print(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Test the live print
slow_print("This text is printing slowly... Press ENTER to skip.")