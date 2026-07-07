import sys
import time
from typing import List, Optional
#
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
    return quantity
    
def mandateStrInput(printText):
    while True:
        userInput = input(f"{printText} or enter 'quit' to exit\n>:")
        if not userInput:
            type_print("Input field cannot be empty. Try again\n")
            continue
        elif normalize_text(userInput) == 'QUIT':
            return 'QUIT'
        else:
            return userInput.strip()
        
def optionalStrInput(printText):
    while True:
        userInput = input(f'{printText} or enter quit to exit\n>:')
        if not userInput: return None
        elif normalize_text(userInput) == 'QUIT':
            return 'quit'
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

def userInputConfirm(printText):
    while True:
        userInput = input(f'{printText} (Enter Y or N)\n>:')
        if userInput.upper() == 'Y':
            print()
            return True
        elif userInput.upper() == 'N':
            print()
            return False
        else:
            type_print("Please enter 'Y' or 'N'", 0.01)
            continue


def print_header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show_menu_screen(title: str, subtitle: Optional[str] = None) -> None:
    print()
    print_header(title)
    if subtitle:
        print(subtitle)
    print()


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    if not rows:
        print("No records found.")
        return

    widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    header_line = " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
    divider = "-+-".join("-" * widths[i] for i in range(len(headers)))

    print(header_line)
    print(divider)
    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))


def pause_for_user() -> None:
    """Pauses the program until the user presses Enter."""
    input("\nPress Enter to continue...")


def choose_index_or_quit(total_items: int, prompt: str = "Choose an item number or type quit to return:\n>: ") -> Optional[int]:
    """Prompts user to select a 1-based item index or quit; returns 0-based index or None."""
    choice = input(prompt).strip()
    if choice.lower() == 'quit':
        return None
    if not choice.isdigit():
        type_print('Invalid choice.', 0.01)
        pause_for_user()
        return None

    index = int(choice) - 1
    if index < 0 or index >= total_items:
        type_print('Choice out of range.', 0.01)
        pause_for_user()
        return None

    return index
