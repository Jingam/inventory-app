from ast import mod
import json
import sys
import os
import time
import threading
from dataclasses import dataclass


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
class Parts():
    partID = str
    partName: str
    partDescription: str
    modelNumber: str  # Initialize modelNumber to None; can be set later if needed
    manufacturer: str  # Initialize manufacturer to None; can be set later if needed
    quantity: int
    location: str  # Initialize location to None; can be set later if needed
    notes: str  # Initialize notes to an empty string; can be set later if needed
    category: str  # Initialize category to None; can be set later if needed
    specs = {}  # Initialize an empty dictionary to hold specifications associated with the part
    def quantityAdd(self, amount):
        """Adds the specified amount to the part's quantity."""
        self.quantity += amount
    def quantityRemove(self, amount):
        """Removes the specified amount from the part's quantity."""
        if self.quantity >= amount:
            self.quantity -= amount
        else:
            raise ValueError("Cannot remove more than available quantity.")
    def isStockLow(self, threshold):
        """Checks if the part's quantity is below the specified threshold."""
        return self.quantity < threshold

@dataclass
class Machine:
    machineID: str
    machineName: str
    machineDescription: str
    machineLocation: str

@dataclass
class Room:
    roomID: str
    roomName: str
    roomDescription: str
    machineList: list  # Initialize an empty list to hold machines associated with the room

@dataclass
class categories:
    def __init__(self, categoryID, categoryName, categoryDescription):
        self.categoryID = categoryID 
        self.categoryName = categoryName
        self.categoryDescription = categoryDescription
        self.partList = []  # Initialize an empty list to hold parts associated with the category


#==========================  Database Handling
def database(self):
    pass

#==========================  Main Operation Function
class inventorySystem:
    
    typespeed = 0.02
    def __init__(self):
        self.partsList: dict[str, Parts] = {}  # Initialize an empty dictionary to hold parts in the inventory system
        self.machineList: dict[str, Machine] = {}  # Initialize an empty dictionary to hold machines in the inventory system
        self.roomList = []  # Initialize an empty list to hold rooms in the inventory system
        self.categoriesList = []  # Initialize an empty list to hold categories in the inventory system
    def addPart(self):
        """Adds a new part to the inventory system."""
        partModel = input("Enter part model: ").strip().upper()
        for Part in self.partsList.values():
            if Part.modelNumber == partModel:
                type_print(f"Part with model number {partModel} already exists in the inventory.", self.typespeed)
                return
            else:
                self.partsList[self.assignPartKey()] = Parts(
                    partID=partModel, 
                    partName=input("Enter part name: ").strip(), 
                    partDescription=input("Enter part description: ").strip(), 
                    modelNumber=partModel, 
                    manufacturer=input("Enter manufacturer: ").strip(), 
                    quantity=input("Enter quantity: ").strip(), 
                    location=input("Enter location: ").strip(), 
                    notes=input("Enter notes (optional): ").strip(), 
                    category="")
        partID = input("Enter part ID: ").strip()
        partName = input("Enter part name: ").strip()
        partDescription = input("Enter part description: ").strip()
        modelNumber = input("Enter model number: ").strip()
        manufacturer = input("Enter manufacturer: ").strip()
        quantity = int(input("Enter quantity: ").strip())
        location = input("Enter location: ").strip()
        notes = input("Enter notes (optional): ").strip()
        category = input("Enter category: ").strip()


    def assignPartKey(self):
        """Assigns a unique key for a new part in the inventory system."""
        if not self.partsList:
            return "P001"  # Start with P001 if the parts list is empty
        else:
            # Extract the numeric part of the last part's key and increment it
            last_key = sorted(self.partsList.keys())[-1]
            last_number = int(last_key[1:])  # Assuming keys are in the format 'P###'
            new_number = last_number + 1
            return f"P{new_number:03d}"  # Format as P### with leading zeros
    def removePart(self, partID):
        pass
    def addMachine(self, machine):
        pass
    def removeMachine(self, machineID):
        pass
    def loadData(self):
        """Loads data from the JSON file into the inventory system."""
        try:
            with open('inventory_data.json', 'r') as file:
                data = json.load(file)
                self.partsList = data.get('partsList', {})
                self.machineList = data.get('machineList', {})
                self.roomList = data.get('roomList', [])
                self.categoriesList = data.get('categoriesList', [])
        except FileNotFoundError:
            print("Data file not found. Starting with an empty inventory.")
        except json.JSONDecodeError:
            print("Error decoding JSON data. Starting with an empty inventory.")
    def saveData(self):
        """Saves data from the inventory system to the JSON file."""
        data = {
            'partsList': self.partsList,
            'machineList': self.machineList,
            'roomList': self.roomList,
            'categoriesList': self.categoriesList
        }
        with open('inventory_data.json', 'w') as file:
            json.dump(data, file)
    def viewMachineList(self):
        """Displays the list of machines in the inventory system."""
        if not self.machineList:
            type_print("No machines in the inventory.\n", self.typespeed)
            return
        print("Machine List:")
        for machineID, machine in self.machineList.items():
            print(f"ID: {machineID}, Name: {machine.machineName}, Description: {machine.machineDescription}, Location: {machine.machineLocation}")
    def viewPartList(self, typeSpeed=0.03):
        """Displays the list of parts in the inventory system."""
        if not self.partsList:
            type_print(f"No parts in the inventory.", typeSpeed)
            return
        print("Part List:")
        for partID, part in self.partsList.items():
            print(f"ID: {partID}, Name: {part.partName}, Description: {part.partDescription}, Category: {part.categoryID}")

#=========================Menus========================


def mainMenu(system):
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
            machineMenu(system)
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
        

def partsMenu():
    type_print("Parts Menu")

def machineMenu(system):
    """Menu for managing machines in the inventory system."""
    typeSpeed = .01
    slowTypeSpeed = .03

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
            type_print("Machine List:", typeSpeed)
            system.viewMachineList()    #Needs a method to call machine list from database, needs to be global
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







#=========================  Main Program Execution=========================

system = inventorySystem()
system.loadData()  # Load data from the JSON file when the program starts
mainMenu(system)

#GIT TEST BRANCH FOR GIT
#NEXT TEXT LINE