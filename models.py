from dataclasses import dataclass, field
from util import *

@dataclass
class Parts():
    partID: str
    partName: str
    partDescription: str
    modelNumber: str 
    manufacturer: str  
    quantity: int
    usedQuantity: int
    location: str  
    notes: str  
    category: str  
    specs: dict = field(default_factory=dict) 
    machineID : dict = field(default_factory=str)

    def to_dict(self):
        """Converts the part object into a JSON-serializable dictionary."""
        return {
            'partID': self.partID,
            'partName': self.partName,
            'partDescription': self.partDescription,
            'modelNumber': self.modelNumber,
            'manufacturer': self.manufacturer,
            'quantity': self.quantity,
            'usedQuantity': self.usedQuantity,
            'location': self.location,
            'notes': self.notes,
            'category': self.category,
            'specs': self.specs,
            'machineID': self.machineID
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Parts instance from a dictionary."""
        return cls(
            partID=data.get('partID', ''),
            partName=data.get('partName', ''),
            partDescription=data.get('partDescription', ''),
            modelNumber=data.get('modelNumber', ''),
            manufacturer=data.get('manufacturer', ''),
            quantity=data.get('quantity', 0),
            usedQuantity=data.get('usedQuantity', 0),
            location=data.get('location', ''),
            notes=data.get('notes', ''),
            category=data.get('category', ''),
            specs=data.get('specs', {}),
            machineID=data.get('machineID', {})
        )

    @classmethod
    def create_empty(cls):
        return cls(
            partID=None,
            partName="",
            partDescription="",
            modelNumber="",
            manufacturer="",
            quantity=0
        )

    def quantityUpdate(self, new_quantity):
        """Updates the quantity of the part."""
        self.quantity = new_quantity

    def usedQuantityUpdate(self, new_used_quantity):
        """Updates the used quantity of the part."""
        self.usedQuantity = new_used_quantity

    def descriptionUpdate(self, new_description):
        """Updates the description of the part."""
        self.partDescription = new_description
    
    def nameUpdate(self, new_name):
        """Updates the name of the part."""
        self.partName = new_name

    def modelUpdate(self, new_model):
        """Updates the model number of the part."""
        self.modelNumber = new_model

    def manufacturerUpdate(self, new_manufacturer):
        """Updates the manufacturer of the part."""
        self.manufacturer = new_manufacturer

    def locationUpdate(self, new_location):
        """Updates the location of the part."""
        self.location = new_location

    def notesUpdate(self, new_notes):
        """Updates the notes of the part."""
        self.notes = new_notes  

    def categoryUpdate(self, new_category):
        """Updates the category of the part."""
        self.category = new_category
    
    @staticmethod
    def isStockLow(self, threshold):
        """Checks if the part's quantity is below the specified threshold."""
        return self.quantity < threshold
    
    @staticmethod
    def validateInput(self, input_value):
        """Validates the input for the part's attributes."""
        if input_value is None:
            type_print("Please enter a valid input")
        return True 
    
@dataclass
class Machine:
    machineID: str
    machineName: str
    machineDescription: str
    machineLocation: str

    part_contained_ID: dict = field(default_factory = dict)
    def to_dict(self):
        """Converts the machine object into a JSON-serializable dictionary."""
        return {
            'machineID': self.machineID,
            'machineName': self.machineName,
            'machineDescription': self.machineDescription,
            'machineLocation': self.machineLocation,
            'part_contained_ID': self.part_contained_ID
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Machine instance from a dictionary."""
        return cls(
            machineID=data.get('machineID', ''),
            machineName=data.get('machineName', ''),
            machineDescription=data.get('machineDescription', ''),
            machineLocation=data.get('machineLocation', ''),
            part_contained_ID=data.get('part_contained_ID', {})
        )
    
    def partTable(self, partsList):
        """Returns a string table showing each part model and quantity in this machine."""

        if not self.part_contained_ID:
            return "No parts assigned to this machine."

        lines = []

        header = f"{'Part Model':<20} {'Quantity':>10}"
        separator = "-" * len(header)

        lines.append(header)
        lines.append(separator)

        for partID, quantity in self.part_contained_ID.items():
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
    
    
    def updatePartQuantity(self, partID, new_quantity):
        """Updates the quantity of a specific part in the machine."""
        if partID in self.part_contained_ID:
            self.part_contained_ID[partID] = new_quantity
        else:
            type_print(f"Part ID {partID} not found in this machine.")

    def updateName(self, new_name):
        """Updates the name of the machine."""
        self.machineName = new_name

    def updateDescription(self, new_description):
        """Updates the description of the machine."""
        self.machineDescription = new_description

    def updateLocation(self, new_location):
        """Updates the location of the machine."""
        self.machineLocation = new_location



@dataclass
class Room:
    roomID: str
    roomName: str
    roomDescription: str
    machine_contained: dict = field(default_factory=str)  # Initialize an empty list to hold machines associated with the room

    def to_dict(self):
        return {
            'roomID': self.roomID,
            'roomName': self.roomName,
            'roomDescription': self.roomDescription,
            'machine_contained': self.machine_contained,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            roomID=data.get('roomID', ''),
            roomName=data.get('roomName', ''),
            roomDescription=data.get('roomDescription', ''),
            machine_contained=data.get('machine_contained', {})
        )

    def updateName(self, new_name):
        self.roomName = new_name

    def updateDescription(self, new_description):
        self.roomDescription = new_description

    def machineTable(self):
        """Returns a string table showing each machine in this room."""
        if not self.machine_contained:
            return "No machines assigned to this room."

        lines = []

        header = f"{'Machine ID':<20} {'Machine Name':<30} {'Description':<30}"
        separator = "-" * len(header)

        lines.append(header)
        lines.append(separator)

        for machineID, machine in self.machine_contained.items():
            lines.append(f"{machineID:<20} {machine.machineName:<30} {machine.machineDescription:<30}")

        return "\n".join(lines)


@dataclass
class categories:
    categoryID: str
    categoryName: str
    categoryDescription: str
    specList = []

    def to_dict(self):
        return {
            'categoryID': self.categoryID,
            'categoryName': self.categoryName,
            'categoryDescription': self.categoryDescription,
            'specList': self.specList,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            categoryID=data.get('categoryID', ''),
            categoryName=data.get('categoryName', ''),
            categoryDescription=data.get('categoryDescription', ''),
            specList=data.get('specList', [])
        )
    
    def updateName(self, new_name):
        self.categoryName = new_name

    def updateDescription(self, new_description):
        self.categoryDescription = new_description

    
