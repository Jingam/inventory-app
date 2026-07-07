import json
from json.tool import main
from platform import machine

from models import *
from util import *

#==========================  Main Inventory System Class =========================
class inventorySystem:
    typespeed = 0.02
    def __init__(self, file_path='inventory_data.json'):
        self.partsList: dict[str, Parts] = {}  # Initialize an empty dictionary to hold parts in the inventory system
        self.machineList: dict[str, Machine] = {}  # Initialize an empty dictionary to hold machines in the inventory system
        self.roomList: dict[str, Room] = {}  # Initialize an empty list to hold rooms in the inventory system
        self.categoriesList: dict[str, categories] = {} # Initialize an empty list to hold categories in the inventory system
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
        
    
    def find_by_field(self, items: dict, field_name: str, search_value: str):
        search_value = normalize_text(search_value)

        for item in items.values():
            item_value = getattr(item, field_name, None)

            if item_value is None:
                continue

            if normalize_text(str(item_value)) == search_value:
                return item

        return None
    
    def getPartByModel(self, modelNumber):          
        return self.find_by_field(self.partsList, 'partModel', modelNumber)
    
    def getMachineByName(self, machineName):
        return self.find_by_field(self.machineList, 'machineName', machineName)
    
    def getRoomByName(self, roomName):
        return self.find_by_field(self.roomList, 'roomName', roomName)
    
    def getCategoryByName(self, categoryName):
        return self.find_by_field(self.categoriesList, 'categoryName', categoryName)
            
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
    

    def display_rooms(self):
        if not self.roomList:
            print("No rooms available.")
            return

        print("\nAvailable Rooms:")
        for room in self.roomList.values():
            print(f"{room.roomID}: {room.roomName}")

    def choose_from_dict(self, data_dict, id_field, name_field):
        """Lets the user choose an object from a dictionary."""

        if not data_dict:
            print("No items found.")
            return None

        items = list(data_dict.values())

        for index, obj in enumerate(items, start=1):
            obj_id = getattr(obj, id_field)
            obj_name = getattr(obj, name_field)
            print(f"{index}. {obj_id} - {obj_name}")

        choice = input("Choose an item number or type quit to return: ")

        if choice.lower() == "quit":
            return None

        if not choice.isdigit():
            print("Invalid choice.")
            return None

        choice = int(choice)

        if choice < 1 or choice > len(items):
            print("Choice out of range.")
            return None

        return items[choice - 1]

    def choose_room(self):
        return self.choose_from_dict(self.roomList, "roomID", "roomName")
    
    def choose_machine(self):
        return self.choose_from_dict(self.machineList, "machineID", "machineName")
    
    def choose_part(self):
        return self.choose_from_dict(self.partsList, "partID", "modelNumber")
    
    def choose_category(self):
        return self.choose_from_dict(self.categoriesList, "categoryID", "categoryName")
    
    def keyword_search(self, items: dict, keyword: str, fields: list[str]):
        keyword = normalize_text(keyword)
        results = []

        for item in items.values():
            for field in fields:
                value = getattr(item, field, "")

                if keyword in normalize_text(str(value)):
                    results.append(item)
                    break

        return results
    

#=========================  Data Persistence Functions =========================


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
            rooms_data = data.get('rooms', data.get('roomList', {}))
            categories_data = data.get('categories', data.get('categoriesList', {}))

            if isinstance(parts_data, dict):
                for part_id, part_data in parts_data.items():
                    part = Parts.from_dict(part_data if isinstance(part_data, dict) else {})
                    self.partsList[part.partID or part_id] = part

            if isinstance(machines_data, dict):
                for machine_id, machine_data in machines_data.items():
                    machine = Machine.from_dict(machine_data if isinstance(machine_data, dict) else {})
                    self.machineList[machine.machineID or machine_id] = machine

            if isinstance(rooms_data, dict):
                for room_id, room_data in rooms_data.items():
                    room = Room.from_dict(room_data if isinstance(room_data, dict) else {})
                    self.roomList[room.roomID or room_id] = room

            if isinstance(categories_data, dict):
                for category_id, category_data in categories_data.items():
                    category = categories.from_dict(category_data if isinstance(category_data, dict) else {})
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
            'rooms': {room_id: room.to_dict() for room_id, room in self.roomList.items()},
            'categories': {cat_id: cat.to_dict() for cat_id, cat in self.categoriesList.items()},
        }
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)


#=========================  Part Operation Functions =========================
    def addPart(self):
        """Adds a new part to the inventory system."""
        partModel = mandateStrInput("Enter part model:").upper()
        existingPart = self.getPartByModel(partModel)
        if existingPart:
            type_print(f"Part with model number {existingPart} already exists in the inventory.", self.typespeed)
            return
        elif partModel == 'quit':
            return
        else:
            if userInputConfirm(f'Confirm you would like to add {partModel} to inventory: Y or N?') is False:
                return
            else:
                type_print(f"Adding new part with model number {partModel}.\n", self.typespeed)
                new_partID = self.assignPartKey()
                partName = mandateStrInput("Enter part name:")
                if partName is None:
                    return
                partDescription = optionalStrInput("Enter part description (optional):")
                if partDescription is 'quit':
                    return
                manufacturer = mandateStrInput("Enter part manufacturer:")
                if manufacturer is None:
                    return
                quantity = validateNumInput()
                location = optionalStrInput("Enter location:")
                if location == 'quit':
                    return
                notes = optionalStrInput("Enter notes (optional):")
                if notes == 'quit':
                    return
                category = optionalStrInput("Enter category:")
                if category == 'quit':
                    return
                specs = {}  # Initialize an empty dictionary for specs; can be populated later if needed

            new_part = Parts(
                partID=new_partID,
                partName=partName,
                partDescription=partDescription,
                modelNumber=partModel,
                manufacturer=manufacturer,
                stock={"new": quantity, "used": 0, "installed": 0},
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
                return
            type_print('Select part ID from following list')
            del_part = self.choose_part()
            if del_part is None: return

            delSelect = userInputConfirm(f"Are you sure you want to delete {del_part.modelNumber}?")
            if delSelect:
                self.partsList.pop(del_part.partID, None)
                self.saveData(self.file_path)
                type_print(f"Part {del_part.modelNumber} removed.")
            else:
                type_print("Deletion cancelled.")
            self.saveData(self.file_path)

    def add_stock(self, part, condition, amount):
        part.stock[condition] += amount
        self.saveData(self.file_path)

    def updatePart(self, part):
        """Update part information in the inventory system."""
        while True:
            if not self.partsList:
                type_print("No parts exists in list yet, please enter part first")
                return
            if part is None: return

            type_print(f"Updating part {part.partID}. Please enter new values or leave blank to keep current value.")

            new_name = optionalStrInput(f"Enter new name (current: {part.partName}):")
            if new_name is not None:
                part.partName = new_name

            new_description = optionalStrInput(f"Enter new description (current: {part.partDescription}):")
            if new_description is not None:
                part.partDescription = new_description

            new_manufacturer = optionalStrInput(f"Enter new manufacturer (current: {part.manufacturer}):")
            if new_manufacturer is not None:
                part.manufacturer = new_manufacturer
            self.saveData(self.file_path)

    def viewPartList(self):
        """Displays a list of all parts in the inventory system."""
        if not self.partsList:
            type_print("No parts in the inventory.\n", self.typespeed)
            return

        partChoice = self.choose_part()
        if partChoice is None:
            return
        else:
            type_print(f"ID: {partChoice.partID}", self.typespeed)
            type_print(f"Name: {partChoice.partName}", self.typespeed)
            type_print(f"Description: {partChoice.partDescription}", self.typespeed)
            type_print(f"Model Number: {partChoice.modelNumber}", self.typespeed)
            type_print(f"Manufacturer: {partChoice.manufacturer}", self.typespeed)
            type_print(f"Quantity (New): {partChoice.stock.get('new', 0)}", self.typespeed)
            type_print(f"Quantity (Used): {partChoice.stock.get('used', 0)}", self.typespeed)
            type_print(f"Quantity (Installed): {partChoice.stock.get('installed', 0)}", self.typespeed)
            type_print(f"Location: {partChoice.location}", self.typespeed)
            type_print(f"Notes: {partChoice.notes}", self.typespeed)
            type_print(f"Category: {partChoice.category}\n", self.typespeed)
        userChoice = userInputConfirm("Would you like to update this part?")
        if userChoice:
            self.updatePart(partChoice)

    def viewPartListTable(self, partsList):
        """Returns a string table showing each part model and quantity"""
        if not self.partsList:
            type_print("No parts in the inventory.\n", self.typespeed)
            return
        lines = []

        header = f"{'Part Model':<20} {'Quantity':>10}"
        separator = "-" * len(header)

        lines.append(header)
        lines.append(separator)

        for partID, quantity in self.partsList.items():
            part = None

            for p in partsList.values():
                if p.partID == partID:
                    part = p
                    break

            if part is not None:
                model = part.modelNumber
            else:
                model = f"Unknown Part ID {partID}"
            
            lines.append(f"{model:<20} {quantity:>10}")

        return "\n".join(lines)

#==========================  Machine Operation Functions =========================

    def addMachine(self):
        newMachineName = mandateStrInput("Enter the name of the machine you wish to add")
        if newMachineName == 'QUIT':
            return

        existingMachine = self.getMachineByName(newMachineName)
        if existingMachine is not None:
            type_print(f"Machine with name {newMachineName} already exists")
            return

        if userInputConfirm(f"Confirm you would like to add {newMachineName} to inventory") is False:
            return

        if not self.roomList:
            type_print("No rooms available. Add a room first.")
            pause_for_user()
            return

        type_print(f"Adding new machine with name {newMachineName}")

        machineID = self.assignMachineKey()

        roomChoice = self.choose_room()
        if roomChoice is None:
            type_print("No room selected. Machine was not added.")
            return

        machineDescription = optionalStrInput("Enter the description of machine")
        if machineDescription == 'quit':
            return

        new_machine = Machine(
            machineID=machineID,
            machineName=newMachineName,
            machineLocation=roomChoice.roomID,  # store room ID only
            machineDescription=machineDescription or ''
        )

        self.machineList[machineID] = new_machine
        self.saveData(self.file_path)

        type_print(
            f"Machine: {newMachineName} with ID: {machineID} "
            f"added to room {roomChoice.roomName} successfully"
    )
            


    def removeMachine(self):
        while True:
            if not self.machineList:
                type_print("No machines exists in list yet, please add a machine first")
                return
            
            type_print("Choose a list from the following:")
            machineChoice = self.choose_machine()
            if machineChoice is None: return
            else:
                delSelect = userInputConfirm(f"Are you sure you want to delete {machineChoice}?")
                if delSelect:
                    self.machineList.pop(machineChoice, None)
                    self.saveData(self.file_path)
                    type_print(f'Machine: {machineChoice} removed.')
                else:
                    type_print("Deletion cancelled.")
            
    def add_part_to_machine(self, machineChoice):
        type_print("Select a part from the following to add:")
        partChoice = self.choose_part()
        if partChoice is None: 
            type_print("No available parts to choose from, please add a part first")
            return
        elif partChoice.partID in machineChoice.part_contained_ID:
            type_print(f"{partChoice.modelNumber} is already assigned to {machineChoice.machineName}.")
            return
        confirmChoice = userInputConfirm(f"Confirm you'd like to add {partChoice.modelNumber} to {machineChoice.machineName}?")
        if confirmChoice is None: return 
        else:
            partQuantity = validateNumInput()
            type_print(f"Adding {partQuantity} - {partChoice.modelNumber} to {machineChoice.machineName}")
            partChoice.stock['installed'] += partQuantity
            machineChoice.part_contained_ID[partChoice.partID] = partQuantity
        self.saveData(self.file_path)


    def viewMachineList(self):
        machine = self.choose_machine()

        if machine is None:
            return None

        print(f"\nID: {machine.machineID}")
        print(f"Name: {machine.machineName}")
        print(f"Location: {machine.machineLocation}")
        print(f"Description: {machine.machineDescription}")
        print("\nParts:")
        print(machine.partTable(self.partsList))

        return machine

    
#=========================  Room Operation Functions =========================

    def addRoom(self):
        """Adds a new room to the inventory system."""
        newRoomName = mandateStrInput("Enter the name of the room you wish to add")
        if newRoomName is None:
            return
        existingRoom = self.getRoomByName(newRoomName)
        if existingRoom is not None:
            type_print(f'Room with name {newRoomName} already exists')
            return
        if userInputConfirm(f"Confirm you would like to add {newRoomName} to inventory") is False:
            return
        else:
            type_print(f'Adding new room with name {newRoomName}')
            newRoomID = self.assignRoomKey()
            newRoomDescription = optionalStrInput('Enter the description of room')
            
        new_room = Room(
            roomID = newRoomID,
            roomName = newRoomName,
            roomDescription = newRoomDescription
        )
        self.roomList[newRoomID] = new_room
        self.saveData(self.file_path)
        type_print(f'Room: {newRoomName} with ID: { newRoomID} added sucessfully')

    def removeRoom(self, roomChoice):
        if not self.roomList:
            type_print("No rooms exists in list yet, please add a room first")
            return
            
        if roomChoice is None: return
        else:
            delSelect = userInputConfirm(f"Are you sure you want to delete {roomChoice}?")
            if delSelect:
                self.roomList.pop(roomChoice, None)
                self.saveData(self.file_path)
                type_print(f'Room: {roomChoice} removed.')
            else:
                type_print("Deletion cancelled.")
        self.saveData(self.file_path)


    def updateRoom(self, machineID, newRoomID):
        """Updates the room ID assigned to a machine."""

        if machineID not in self.machineList:
            type_print(f"Machine ID {machineID} not found in the inventory.")
            return False

        if newRoomID not in self.roomList:
            type_print(f"Room ID {newRoomID} not found in the inventory.")
            return False

        self.machineList[machineID].machineLocation = newRoomID
        self.saveData(self.file_path)
        return True

    def viewRoomList(self):
        """Displays rooms and the machines assigned to each room."""

        if not self.roomList:
            type_print("No rooms in the inventory.\n", self.typespeed)
            return

        for roomID, room in self.roomList.items():
            machines_in_room = [
                machine for machine in self.machineList.values()
                if machine.machineLocation == roomID
            ]

            if machines_in_room:
                machine_names = ", ".join(
                    f"{machine.machineID} - {machine.machineName}"
                    for machine in machines_in_room
                )
            else:
                machine_names = "None"

            print(
                f"ID: {roomID}, "
                f"Name: {room.roomName}, "
                f"Description: {room.roomDescription}, "
                f"Machines: {machine_names}"
            )

        pause_for_user()


    def roomMachineTable(self, roomID):
        """Returns a string table of machines assigned to a room."""

        if roomID not in self.roomList:
            return "Room not found."

        machines = [
            machine for machine in self.machineList.values()
            if machine.machineLocation == roomID
        ]

        if not machines:
            return "No machines assigned to this room."

        lines = []
        header = f"{'Machine Name':<30} {'Description':<30}"
        separator = "-" * len(header)

        lines.append(header)
        lines.append(separator)

        for machine in machines:
            machine_id = str(machine.machineID or "")
            machine_name = str(machine.machineName or "")
            description = str(machine.machineDescription or "")

        lines.append(
            f"{machine_id:<12} "
            f"{machine_name:<30} "
            f"{description:<30}"
        )

        return "\n".join(lines)

#=========================  Category Operation Functions =========================


    def addCategory(self):
        """Adds a new category to the inventory system."""
        newCategoryName = mandateStrInput("Enter the name of the category you wish to add")
        if newCategoryName is None:
            return
        existingCategory = self.getCategoryByName(newCategoryName)
        if existingCategory is not None:
            type_print(f'Category with name {newCategoryName} already exists')
            return
        if userInputConfirm(f"Confirm you would like to add {newCategoryName} to inventory") is False:
            return
        else:
            type_print(f'Adding new category with name {newCategoryName}')
            newCategoryID = self.assignCategoryKey()
            newCategoryDescription = optionalStrInput('Enter the description of category')
            specFields = []
            print("Enter the specification fields for this category. Type 'done' when finished.")
            while True:
                input = mandateStrInput("Enter a specification field (or type 'done' to finish):")
                if normalize_text(input) == 'DONE':
                    break
                specFields.append(input)
            
        new_category = categories(
            categoryID = newCategoryID,
            categoryName = newCategoryName,
            categoryDescription = newCategoryDescription,
            specList = specFields
        )
        self.categoriesList[newCategoryID] = new_category
        self.saveData(self.file_path)
        type_print(f'Category: {newCategoryName} with ID: { newCategoryID} added sucessfully')


    def removeCategory(self, categoryChoice):
        if not self.categoriesList:
            type_print("No categories exists in list yet, please add a category first")
            return
            
        if categoryChoice is None: return
        else:
            delSelect = userInputConfirm(f"Are you sure you want to delete {categoryChoice}?")
            if delSelect:
                self.categoriesList.pop(categoryChoice, None)
                self.saveData(self.file_path)
                type_print(f'Category: {categoryChoice} removed.')
            else:
                type_print("Deletion cancelled.")

    def display_categories(self):
        """Displays the list of categories in the inventory system."""
        if not self.categoriesList:
            type_print("No categories in the inventory.\n", self.typespeed)
            return
        categoryChoice = self.choose_category()
        if categoryChoice is None:
            return
        else:
            type_print(f"ID: {categoryChoice.categoryID}, Name: {categoryChoice.categoryName}, Description: {categoryChoice.categoryDescription}, Specs: {', '.join(categoryChoice.specList)}", speed = 0.005)
            pause_for_user()
            type_print(f"Parts in this category: {', '.join(categoryChoice.partList)}", speed = 0.005)
            pause_for_user()
            userChoice = userInputConfirm("Would you like to update this category? (Y/N)")
            if userChoice:
                new_name = optionalStrInput(f"Enter new name (current: {categoryChoice.categoryName}):")
                if new_name is not None:
                    categoryChoice.categoryName = new_name

                new_description = optionalStrInput(f"Enter new description (current: {categoryChoice.categoryDescription}):")
                if new_description is not None:
                    categoryChoice.categoryDescription = new_description
                self.saveData(self.file_path)

