from ast import mod
import json
import sys
import os
import time
import threading
import dataclass


#==========================  Global Variables
#speed = 0.03

#==========================  Helper Functions
# def skipPrint():
#     """Sets the global variable delay to 0, allowing the user to skip the type_print delay."""
#     global speed
#     input()
#     speed = 0  # Set delay to zero to skip the printing delay

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

#==========================   Main Data Containers
@dataclass
def Parts(self):
    def __init__(self):
        self.partID = str
        self.partDict = {
            "partName": str,
            "partDescription": str,
            "modelNumber": str,  # Initialize modelNumber to None; can be set later if needed
            "manufacturer": str,  # Initialize manufacturer to None; can be set later if needed
            "quantity": int
            }  
        self.specs = []  # Initialize an empty list to hold specifications associated with the part

@dataclass
def Machine(self):
    def __init__(self, machineID, machineName, machineDescription, machineLocation):
        self.machineID = machineID
        self.machineName = machineName
        self.machineDescription = machineDescription
        self.partsList = []  # Initialize an empty list to hold parts associated with the machine
        self.room = machineLocation

@dataclass
def Room(self):
    def __init__(self, roomID, roomName, roomDescription):
        self.roomID = roomID
        self.roomName = roomName
        self.roomDescription = roomDescription
        self.machineList = []  # Initialize an empty list to hold machines associated with the room

@dataclass
def categories(self):
    def __init__(self, categoryID, categoryName, categoryDescription):
        self.categoryID = categoryID
        self.categoryName = categoryName
        self.categoryDescription = categoryDescription
        self.partList = []  # Initialize an empty list to hold parts associated with the category


#==========================  Database Handling
def database(self):
    pass

#==========================  Main Operation Function
def inventorySystem():
    pass


#=========================Menus========================
def partsMenu():
    print("Parts Menu")

def machineMenu():
    """Menu for managing machines in the inventory system."""
    typeSpeed = .02
    slowTypeSpeed = .05

    def display_machine_list():
        """Displays the list of machines in the inventory system."""
        # This function should retrieve and display the machine list from the database.
        # For now, it will just print a placeholder message.
        type_print("Displaying Machine List...", typeSpeed)
    
    def add_machine():
        """Adds a new machine to the inventory system."""
        # This function should handle the logic for adding a new machine.
        # For now, it will just print a placeholder message.
        type_print("Adding a new machine...", typeSpeed)

    def remove_machine():
        """Removes a machine from the inventory system."""
        # This function should handle the logic for removing a machine.
        # For now, it will just print a placeholder message.
        type_print("Removing a machine...", typeSpeed)

    def update_machine():
        """Updates the details of an existing machine in the inventory system."""
        # This function should handle the logic for updating a machine's details.
        # For now, it will just print a placeholder message.
        type_print("Updating machine details...", typeSpeed)

    while True:
        type_print('=' * 10 + "Machine Menu" + '=' * 10, typeSpeed)
        type_print("""
Select one of the following options:
1. Add Machine 
2. Remove Machine
3. View Machine Part List
4. Machine List
5. Update Machine
6. Back to Main Menu
""", typeSpeed)
        
        userInput = input(">: ")
        if userInput.strip() == '1':
            type_print("Add Machine", typeSpeed)     #Can be replaced with a function call to add a machine
        elif userInput.strip() == '2': 
            type_print("Remove Machine", typeSpeed)  #Can be replaced with a function call to remove a machine
        elif userInput.strip() == '3':
            type_print("View Machine Part List", typeSpeed)  #Can be replaced with a function call to view the part list of a machine, needs to call a method outside scope
        elif userInput.strip() == '4':
            type_print("Machine List", typeSpeed)    #Needs a method to call machine list from database, needs to be global
        elif userInput.strip() == '5':
            type_print("Update Machine", typeSpeed)   #Needs a method to call machine list from database, can be local
        elif userInput.strip() == '6':
            return  # Exit the machine menu and return to the main menu
        else:
            type_print("Invalid operation please try again", typeSpeed)



def reportMenu():
    print("Report Menu")

def roomMenu():
    print("Room Menu")

def specMenu():
    pass


def categoriesMenu():
    pass





#system = inventorySystem()


def mainMenu():
    banner = "=" * 30 
    print(banner + '\n' + banner + '\n' + banner)
    type_print("  Welcome to the Main Menu", speed =.05)
    while True:
        type_print("""
Select one of the following options:
1. Machine Menu
2. Parts Menu
3. Reports Menu
4. Exit
""", speed = 0.01)
        userInput = input(">: ")
        if userInput.strip() == '1':
            machineMenu()
        elif userInput.strip() == '2':
            partsMenu()
        elif userInput.strip() == '3':
            reportMenu()
        elif userInput.strip() == '4':
            type_print('Goodbye', 0.08)
            time.sleep(1.5)
            break
        else:
            type_print("Invalid operation please try again", speed = 0.035)
        

mainMenu()

#GIT TEST BRANCH FOR GIT
#NEXT TEXT LINE