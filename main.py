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
    banner = "=" * 72
    print(banner + '\n' + banner)
    print_header("Welcome to the Main Menu", speed = 0.005)
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
    headerSpeed = 0.005
    typeSpeed = .01
    slowTypeSpeed = .03

    while True:
        print_header("Parts Menu", headerSpeed)
        print("""
Select one of the following options:
1. Add Part
2. Remove Part
3. View Part List
4. Update Part
5. Back to Main Menu
""")
        
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
        type_print("Displaying Machine List...", slowTypeSpeed)
        machineChoice = system.choose_machine()  # This will display the list of machines and allow the user to select one
        if machineChoice is None:
            type_print("No machine selected. Returning to machine menu.", typeSpeed)
            return
        else: update_machine_menu(system, machineChoice)  # Call the update_machine_menu function with the selected machine


    while True:
        print_header("Machine Menu")
        print("""
Select one of the following options:
1. Add Machine 
2. Remove Machine
3. Machine List
4. Update Machine
5. Back to Main Menu
""")
        
        userInput = input(">: ")
        if userInput.strip() == '1':
            type_print("Add Machine", typeSpeed)     #Can be replaced with a function call to add a machine
            system.addMachine()
        elif userInput.strip() == '2': 
            type_print("Remove Machine", typeSpeed)  #Can be replaced with a function call to remove a machine
            system.remove_machine()
        elif userInput.strip() == '3':
            type_print("Machine List:", typeSpeed)
            system.viewMachineList()    #Needs a method to call machine list from database, needs to be global
        elif userInput.strip() == '4':
            type_print("Update Machine", typeSpeed)   #Needs a method to call machine list from database, can be local
            choose_machine = system.choose_machine()
            if choose_machine is None:
                type_print("No machine selected. Returning to machine menu.", typeSpeed)
                continue
            update_machine_menu(system, choose_machine)
        elif userInput.strip() == '5':
            return  # Exit the machine menu and return to the main menu
        else:
            type_print("Invalid operation please try again", typeSpeed)

def update_machine_menu(system, machineChoice):
        """Updates the details of an existing machine in the inventory system."""
        while True:
            print_header(f"Update Machine: {machineChoice.machineName}", speed=0.005)
            print("""
Select one of the following options:
1. Update machine name
2. Update machine room
3. Update machine parts list
4. Update machine description
5. View machine part list
6. Return to machine menu                      
""")
            
            userInput = input(">: ")
            if userInput.strip() == '1':
                type_print("Updating machine name...")
            elif userInput.strip() == '2':
                type_print("Updating machine room...")
            elif userInput.strip() == '3':
                type_print("Updating machine parts list...")
                system.add_part_to_machine(machineChoice)
            elif userInput.strip() == '4':
                type_print("Updating machine description...")
            elif userInput.strip() == '5':
                type_print("Viewing machine part list...")
                print(machineChoice.partTable(system.partsList))
                input("Press Enter to return to the update machine menu...")
            elif userInput.strip() == '6':
                return  # Exit the update machine menu and return to the machine menu
            else: 
                type_print("Invalid option please try again")

def reportMenu():
    print("Report Menu")

def roomMenu():
    print("Room Menu")

def specMenu():
    pass


def categoriesMenu():
    print_header("Categories Menu")
    print("""
Select one of the following options:
1. Add Category
2. Remove Category
3. View Category List
4. Update Category
5. Back to Main Menu
""")
    userInput = input(">: ")
    if userInput.strip() == '1':
        print("Add Category")
        system.addCategory()
    elif userInput.strip() == '2':
        print("Remove Category")
        system.removeCategory()
    elif userInput.strip() == '3':
        print("View Category List")
    elif userInput.strip() == '4':
        print("Update Category")
    elif userInput.strip() == '5':
        return  # Exit the categories menu and return to the main menu
    else:
        print("Invalid operation please try again")

def updateCategoryMenu():
    print_header("Update Category Menu")
    print("""
Select one of the following options:)
1. Update category name
2. Update category description
3. View category part list
4. Update category spec list
5. Return to categories menu
""")
    userInput = input(">: ")
    if userInput.strip() == '1':
        print("Update category name")
    elif userInput.strip() == '2':
        print("Update category description")
    elif userInput.strip() == '3':
        print("View category part list")
    elif userInput.strip() == '4':
        print("Update category spec list")
    elif userInput.strip() == '5':
        return  # Exit the update category menu and return to the categories menu
    else:
        print("Invalid operation please try again")


#=========================  Main Program Execution=========================

system = inventorySystem()
system.loadData()  # Load data from the JSON file when the program starts
mainMenu(system)

#GIT TEST BRANCH FOR GIT
#NEXT TEXT LINE