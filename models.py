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
    location: str  
    notes: str  
    category: str  
    specs: dict = field(default_factory=dict) 

    def to_dict(self):
        """Converts the part object into a JSON-serializable dictionary."""
        return {
            'partID': self.partID,
            'partName': self.partName,
            'partDescription': self.partDescription,
            'modelNumber': self.modelNumber,
            'manufacturer': self.manufacturer,
            'quantity': self.quantity,
            'location': self.location,
            'notes': self.notes,
            'category': self.category,
            'specs': self.specs,
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
            location=data.get('location', ''),
            notes=data.get('notes', ''),
            category=data.get('category', ''),
            specs=data.get('specs', {})
        )

    @classmethod
    def create_empty(cls):
        return cls(
            part_id=None,
            model="",
            manufacturer="",
            quantity=0
        )

    def quantityUpdate(self, new_quantity):
        """Updates the quantity of the part."""
        self.quantity = new_quantity
    
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

    def to_dict(self):
        """Converts the machine object into a JSON-serializable dictionary."""
        return {
            'machineID': self.machineID,
            'machineName': self.machineName,
            'machineDescription': self.machineDescription,
            'machineLocation': self.machineLocation,
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Machine instance from a dictionary."""
        return cls(
            machineID=data.get('machineID', ''),
            machineName=data.get('machineName', ''),
            machineDescription=data.get('machineDescription', ''),
            machineLocation=data.get('machineLocation', '')
        )
    


@dataclass
class Room:
    roomID: str
    roomName: str
    roomDescription: str
    machineList: list  # Initialize an empty list to hold machines associated with the room

    def to_dict(self):
        return {
            'roomID': self.roomID,
            'roomName': self.roomName,
            'roomDescription': self.roomDescription,
            'machineList': self.machineList,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            roomID=data.get('roomID', ''),
            roomName=data.get('roomName', ''),
            roomDescription=data.get('roomDescription', ''),
            machineList=data.get('machineList', [])
        )


@dataclass
class categories:
    categoryID: str
    categoryName: str
    categoryDescription: str
    partList: list  # Initialize an empty list to hold parts associated with the category

    def to_dict(self):
        return {
            'categoryID': self.categoryID,
            'categoryName': self.categoryName,
            'categoryDescription': self.categoryDescription,
            'partList': self.partList,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            categoryID=data.get('categoryID', ''),
            categoryName=data.get('categoryName', ''),
            categoryDescription=data.get('categoryDescription', ''),
            partList=data.get('partList', [])
        )