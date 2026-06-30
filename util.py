import sys
import time

def flush_input():
    """Discards all accumulated user keystrokes in the buffer."""
    try:
        # For Windows
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        # For Linux / MacOS
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

def type_print(text, speed=.03):
    """Prints text character by character with a customizable delay."""
    # thread = threading.Thread(target=skipPrint)
    # thread.daemon = True
    # thread.start()

    for char in text:   
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()
    flush_input()  # Clear any accumulated input after printing

def normalize_text(text):
    """Normalizes text by stripping whitespace and converting to uppercase."""
    return text.strip().upper()

def normalize_model(model_number):
    """Normalizes model numbers by stripping whitespace and converting to uppercase."""
    return model_number.strip().upper()

def validateNumInput():
    quantity_input = input("Enter quantity: ").strip() #Add quantity validation to ensure it's a number and not negative later
    try:
        quantity = int(quantity_input)
        if quantity < 0:
                type_print("Quantity cannot be negative. Setting quantity to 0.")
                quantity = 0
    except ValueError:
        type_print("Quantity must be a number. Setting quantity to 0.")
        quantity = 0
    else: 
        return quantity_input
    
def mandateStrInput(printText):
    while True:
        userInput = input(f"{printText}")
        if not userInput:
            type_print("Input field cannot be empty. Try again")
            continue
        else:
            return userInput.strip()


def checkEmptyInfo(info):
    """Returns 'None' for empty or missing values; otherwise returns the trimmed value."""
    if info is None:
        return "None"

    if isinstance(info, str):
        info = info.strip()
        if not info:
            return "None"

    return info


