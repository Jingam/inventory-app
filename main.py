from ast import mod
import sys
import time
#import threading - Not used yet
from models import *
from util import *
from inventorySys import *


#==========================  Global Variables =========================


#==========================  Helper Functions =========================
# def skipPrint():
#     """Sets the global variable delay to 0, allowing the user to skip the type_print delay."""
#     global speeds
#     input()
#     speed = 0  # Set delay to zero to skip the printing delay




#==========================  Database Handling =========================
def database(self):
    pass


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
            partsMenu(system)
        elif userInput.strip() == '3':
            reportMenu()
        elif userInput.strip() == '4':
            type_print('Goodbye', 0.08)
            time.sleep(1.5)
            break
        else:
            type_print("Invalid operation please try again", speed = 0.035)
        #

def partsMenu(system):
    """Menu for managing parts in the inventory system."""
    typeSpeed = .01
    slowTypeSpeed = .03

    while True:
        type_print('=' * 10 + "Parts Menu" + '=' * 10, typeSpeed)
        type_print("""
Select one of the following options:
1. Add Part
2. Remove Part
3. View Part List
4. Update Part
5. Back to Main Menu
""", typeSpeed)
        
        userInput = input(">: ")
        if userInput.strip() == '1':
            type_print("Add Part", typeSpeed)
            system.addPart() 
        elif userInput.strip() == '2':
            type_print("Remove Part", typeSpeed)
            system.removePart()
        elif userInput.strip() == '3':
            type_print("View Part List", typeSpeed)
            system.viewPartList()
        elif userInput.strip() == '4':
            type_print("Update Part", typeSpeed)
            system.updatePart()
        elif userInput.strip() == '5':
            return
        else:
            type_print("Invalid operation please try again", typeSpeed)

def machineMenu(system):
    """Menu for managing machines in the inventory system."""
    typeSpeed = .01
    slowTypeSpeed = .03

    def display_machine_list():
        """Displays the list of machines in the inventory system."""
        type_print("Displaying Machine List...", typeSpeed)
    
    def add_machine():
        """Adds a new machine to the inventory system."""
        type_print("Adding a new machine...", typeSpeed)

    def remove_machine():
        """Removes a machine from the inventory system."""
        type_print("Removing a machine...", typeSpeed)

    def update_machine(system):
        """Updates the details of an existing machine in the inventory system."""
        while True:
            type_print('=' * 10 + "Update Machine Menu" + '=' * 10, typeSpeed)
            type_print("""
Select one of the following options:
1. Update machine name
2. Update machine room
3. Update machine parts list
4. Update machine description
5. Return to machine menu                      
""", typeSpeed)
            
            userInput = input(">: ")
            if userInput.strip() == '1':
                type_print("Updating machine name...")
            elif userInput.strip() == '2':
                type_print("Updating machine room...")
            elif userInput.strip() == '3':
                type_print("Updating machine parts list...")
                system.add_part_to_machine()
            elif userInput.strip() == '4':
                type_print("Updating machine description...")
            elif userInput.strip() == '5':
                return
            else: type_print("Invalid option please try again")

    while True:
        type_print('=' * 10 + "Machine Menu" + '=' * 10, typeSpeed)
        type_print("""
Select one of the following options:
1. Add Machine 
2. Remove Machine
3. View Machine Parts List
4. Machine List
5. Update Machine
6. Back to Main Menu
""", typeSpeed)
        
        userInput = input(">: ")
        if userInput.strip() == '1':
            type_print("Add Machine", typeSpeed)     #Can be replaced with a function call to add a machine
            system.addMachine()
        elif userInput.strip() == '2': 
            type_print("Remove Machine", typeSpeed)  #Can be replaced with a function call to remove a machine
            system.remove_machine()
        elif userInput.strip() == '3':
            type_print("View Machine Part List", typeSpeed)  #Can be replaced with a function call to view the part list of a machine, needs to call a method outside scope
        elif userInput.strip() == '4':
            type_print("Machine List:", typeSpeed)
            system.viewMachineList()    #Needs a method to call machine list from database, needs to be global
        elif userInput.strip() == '5':
            type_print("Update Machine", typeSpeed)   #Needs a method to call machine list from database, can be local
            update_machine(system)
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