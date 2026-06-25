import json
import sys
import time


#==========================   Main Data Containers
@classmethod
def Parts(self):
    pass

@classmethod
def Machine(self):
    pass

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
    typeSpeed = .02
    while True:
        type_print('=' * 10 + "Machine Menu" + '=' * 10, typeSpeed)
        type_print("""
Select one of the following options:
1.
""")



def reportMenu():
    print("Report Menu")

def roomMenu():
    print("Room Menu")

def specMenu():
    pass

def specsMenu():
    pass

def categoriesMenu():
    pass





#system = inventorySystem()

def type_print(text, speed=0.03):
    """Prints text character by character with a customizable delay."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)
    print()  # Adds a final newline at the very end

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
            time.sleep(2)
            break
        else:
            type_print("Invalid operation please try again", speed = 0.035)
        

mainMenu()