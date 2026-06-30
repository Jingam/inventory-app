import json
from json.tool import main
from models import *
from util import *

#==========================  Main Inventory System Class =========================
class inventorySystem:
    typespeed = 0.02
    def __init__(self, file_path='inventory_data.json'):
        self.partsList: dict[str, Parts] = {}  # Initialize an empty dictionary to hold parts in the inventory system
        self.machineList: dict[str, Machine] = {}  # Initialize an empty dictionary to hold machines in the inventory system
        self.roomList = []  # Initialize an empty list to hold rooms in the inventory system
        self.categoriesList = []  # Initialize an empty list to hold categories in the inventory system
        self.file_path = file_path


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
            if part.modelNumber == normalize_text(modelNumber):
                return part
            
        return None
            
    def getPartGeneralInfo(self, partID):
        """Retrieves general information string about a part based on its ID."""
        part = self.partsList.get(partID)
        if part:
            print_string = (
                f"ID: {checkEmptyInfo(part.partID)}, "
                f"Name: {checkEmptyInfo(part.partName)}, "
                f"Model: {checkEmptyInfo(part.modelNumber)}, "
                f"Manufacturer: {checkEmptyInfo(part.manufacturer)}, "
                f"Quantity: {checkEmptyInfo(part.quantity)}, "
                f"Description: {checkEmptyInfo(part.partDescription)}, "
                f"Category: {checkEmptyInfo(part.category)}, "
                f"Location: {checkEmptyInfo(part.location)}, "
                f"Notes: {checkEmptyInfo(part.notes)}"
            )
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

    def loadData(self, file_path='inventory_data.json'):
        """Loads data from the JSON file into the inventory system."""
        self.file_path = file_path
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            self.partsList.clear()
            self.machineList.clear()
            self.roomList.clear()
            self.categoriesList.clear()

            if not isinstance(data, dict):
                print("Invalid inventory data structure. Starting with an empty inventory.")
                return

            parts_data = data.get('parts', data.get('partsList', {}))
            machines_data = data.get('machines', data.get('machineList', {}))
            rooms_data = data.get('rooms', data.get('roomList', []))
            categories_data = data.get('categories', data.get('categoriesList', []))

            if isinstance(parts_data, dict):
                for part_id, part_data in parts_data.items():
                    part = Parts.from_dict(part_data if isinstance(part_data, dict) else {})
                    self.partsList[part.partID or part_id] = part
            elif isinstance(parts_data, list):
                for part_data in parts_data:
                    part = Parts.from_dict(part_data)
                    self.partsList[part.partID] = part

            if isinstance(machines_data, dict):
                for machine_id, machine_data in machines_data.items():
                    machine = Machine.from_dict(machine_data if isinstance(machine_data, dict) else {})
                    self.machineList[machine.machineID or machine_id] = machine
            elif isinstance(machines_data, list):
                for machine_data in machines_data:
                    machine = Machine.from_dict(machine_data)
                    self.machineList[machine.machineID] = machine

            if isinstance(rooms_data, dict):
                for room_id, room_data in rooms_data.items():
                    room = Room.from_dict(room_data if isinstance(room_data, dict) else {})
                    self.roomList.append(room)
            elif isinstance(rooms_data, list):
                for room_data in rooms_data:
                    room = Room.from_dict(room_data)
                    self.roomList.append(room)

            if isinstance(categories_data, dict):
                for category_id, category_data in categories_data.items():
                    category = categories.from_dict(category_data if isinstance(category_data, dict) else {})
                    self.categoriesList.append(category)
            elif isinstance(categories_data, list):
                for category_data in categories_data:
                    category = categories.from_dict(category_data)
                    self.categoriesList.append(category)

        except FileNotFoundError:
            print("Data file not found. Starting with an empty inventory.")
        except json.JSONDecodeError:
            print("Error decoding JSON data. Starting with an empty inventory.")

    def saveData(self, file_path='inventory_data.json'):
        """Saves data from the inventory system to the JSON file."""
        self.file_path = file_path
        data = {
            'parts': {part_id: part.to_dict() for part_id, part in self.partsList.items()},
            'machines': {machine_id: machine.to_dict() for machine_id, machine in self.machineList.items()},
            'rooms': {room.roomID: room.to_dict() for room in self.roomList},
            'categories': {category.categoryID: category.to_dict() for category in self.categoriesList},
        }
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)


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
            self.saveData(self.file_path)
            type_print(f"Part {partName} with model number {partModel} added successfully.\n", self.typespeed)


    def removePart(self):
        """Remove part from parts list"""
        while True:
            if not self.partsList:
                type_print("No parts exists in list yet, please enter part first")
                break

            type_print('Select part ID from following list')
            self.viewPartList()
            del_part = mandateStrInput('Enter part you wish to delete or type exit to return to menu')
            if normalize_text(del_part) == 'EXIT':
                break

            part = self.partsList.get(del_part)
            if part is None:
                type_print("Part ID not found. Try again.")
                continue

            delSelect = mandateStrInput(
                f"Are you sure you want to delete {part.partName} ({del_part})? Y/N?"
            ).strip().upper()
            if delSelect == 'Y':
                self.partsList.pop(del_part, None)
                self.saveData(self.file_path)
                type_print(f"Part {del_part} removed.")
            else:
                type_print("Deletion cancelled.")


    def addMachine(self):
        while True:
            machineName = mandateStrInput("Enter the name of the machine you wish to add or type exit to return to menu")
            if 


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