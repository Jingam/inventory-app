import json
from json.tool import main
from models import *
from util import *

#==========================  Main Inventory System Class =========================
class inventorySystem:
    typespeed = 0.02
    def __init__(self):
        self.partsList: dict[str, Parts] = {}  # Initialize an empty dictionary to hold parts in the inventory system
        self.machineList: dict[str, Machine] = {}  # Initialize an empty dictionary to hold machines in the inventory system
        self.roomList = []  # Initialize an empty list to hold rooms in the inventory system
        self.categoriesList = []  # Initialize an empty list to hold categories in the inventory system


 #==========================  Helper Functions =========================       

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
        
    def assignMachineKey(self):
        """Assigns a unique key for a new machine in the inventory system."""
        if not self.machineList:
            return "M001"  # Start with P001 if the parts list is empty
        else:
            # Extract the numeric part of the last part's key and increment it
            last_key = sorted(self.machineList.keys())[-1]
            last_number = int(last_key[1:])  # Assuming keys are in the format 'P###'
            new_number = last_number + 1
            return f"M{new_number:03d}"  # Format as P### with leading zeros
        
    def assignRoomKey(self):
        """Assigns a unique key for a new part in the inventory system."""
        if not self.roomList:
            return "R001"  # Start with R001 if the parts list is empty
        else:
            # Extract the numeric part of the last part's key and increment it
            last_key = sorted(self.roomList.keys())[-1]
            last_number = int(last_key[1:])  # Assuming keys are in the format 'P###'
            new_number = last_number + 1
            return f"R{new_number:03d}"  # Format as P### with leading zeros
        
    def assignCategoryKey(self):
        """Assigns a unique key for a new part in the inventory system."""
        if not self.categoriesList:
            return "C001"  # Start with C001 if the parts list is empty
        else:
            # Extract the numeric part of the last part's key and increment it
            last_key = sorted(self.categoriesList.keys())[-1]
            last_number = int(last_key[1:])  # Assuming keys are in the format 'P###'
            new_number = last_number + 1
            return f"C{new_number:03d}"  # Format as P### with leading zeros
        
    def getPartByModel(self, modelNumber):
        """Retrieves a part object from the inventory system based on its model number."""
        for part in self.partsList.values():
            if part.modelNumber == modelNumber:
                return part
            
        return None
            
    def getPartGeneralInfo(self, partID):
        """Retrieves general information string about a part based on its ID."""
        part = self.partsList.get(partID)
        if part:
            print_string = (f"ID: {part.partID}, Name: {part.partName}, Model: {part.modelNumber}, Manufacturer: {part.manufacturer}, Quantity: {part.quantity}, Description: {part.partDescription}, Category: {part.category}")
            return print_string
        else:
            return "No Info Found" 

    def getPartSpecs(self, partID):
        """Retrieves the specifications of a part based on its ID."""
        part = self.partsList.get(partID)
        if part:
            return part.specs
        else:
            return None  # Return None if no part with the specified ID is found
        
    def searchPartByID(self, partID):
        """Searches for a part in the inventory system based on its ID."""
        return self.partsList.get(partID, None)  # Return the part if found, otherwise return None
    
    def searchPart(self, searchTerm):
        """Searches for parts in the inventory system based on a search term."""
        results = []
        for part in self.partsList.values():
            if (searchTerm.lower() in part.partName.lower() or
                searchTerm.lower() in part.partDescription.lower() or
                searchTerm.lower() in part.modelNumber.lower() or
                searchTerm.lower() in part.manufacturer.lower()):
                results.append(part)
        return results  # Return a list of matching parts

    def loadData(self):
        """Loads data from the JSON file into the inventory system."""
        try:
            with open('inventory_data.json', 'r') as file:
                data = json.load(file)
                # self.partsList = data.get('partsList', {})
                # self.machineList = data.get('machineList', {})
                # self.roomList = data.get('roomList', [])
                # self.categoriesList = data.get('categoriesList', [])
                for part_data in data["parts"]:
                    part = Parts.from_dict(part_data)
                    self.partsList[part.partID] = part
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


#=========================  Main Operation Functions =========================
    def addPart(self):
        """Adds a new part to the inventory system."""

        partModel = normalize_text(input("Enter part model: "))
        existingPart = self.getPartByModel(partModel)
        if existingPart:
            type_print(f"Part with model number {existingPart.modelNumber} already exists in the inventory.", self.typespeed)
            
        else:
            type_print(f"Adding new part with model number {partModel}.", self.typespeed)
            new_partID = self.assignPartKey()
            partName = mandateStrInput("Enter part name: ")
            partDescription = input("Enter part description (optional): ").strip()
            manufacturer = mandateStrInput("Enter part manufacturer: ")
            quantity = validateNumInput()
            location = input("Enter location: ").strip()
            notes = input("Enter notes (optional): ").strip()
            category = input("Enter category: ").strip()
            specs = {}  # Initialize an empty dictionary for specs; can be populated later if needed

            new_part = Parts(
                partID=new_partID,
                partName=partName,
                partDescription=partDescription,
                modelNumber=partModel,
                manufacturer=manufacturer,
                quantity=quantity,
                location=location,
                notes=notes,
                category=category,
                specs=specs
            )
            self.partsList[new_partID] = new_part
            type_print(f"Part {partName} with model number {partModel} added successfully.\n", self.typespeed)


    def removePart(self):
        """Remove part from parts list"""
        while True:
            if not self.partsList:
                type_print("No parts exists in list yet, please enter part first")
                break
            else:
                type_print('Select part ID from following list')
                time.sleep(2)
                self.viewPartList()
                del_part = mandateStrInput('Enter part you wish to delete or type exit to return to menu')
                if normalize_text(del_part) == 'exit':
                    break
                delSelect = mandateStrInput(f"Are you sure you want to delete {self.partsList.get(del_part)}? Y\N?") 
                if self.partsList(del_part) and delSelect == 'Y':
                    self.partsList.pop(del_part, None)
                elif not delSelect == 'Y':

                    
                    


    def addMachine(self, machine):
        pass

    def removeMachine(self, machineID):
        pass

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
        for partID in self.partsList.keys():
            type_print(self.getPartGeneralInfo(partID), typeSpeed)