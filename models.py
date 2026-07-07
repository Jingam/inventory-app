from dataclasses import dataclass, field
from util import *

@dataclass
class Parts():
    partID: str
    partName: str
    partDescription: str
    modelNumber: str 
    manufacturer: str  
    location: str  
    notes: str  
    category: str  
    specs: dict = field(default_factory=dict) 
    machineID : dict = field(default_factory=dict)
    stock: dict = field(default_factory=lambda: {
        "new": 0,
        "used": 0,
        "installed": 0
    })

    def to_dict(self):
        """Converts the part object into a JSON-serializable dictionary."""
        return {
            'partID': self.partID,
            'partName': self.partName,
            'partDescription': self.partDescription,
            'modelNumber': self.modelNumber,
            'manufacturer': self.manufacturer,
            'stock': self.stock,
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
            stock=data.get('stock', {"new": 0, "used": 0, "installed": 0}),
            location=data.get('location', ''),
            notes=data.get('notes', ''),
            category=data.get('category', ''),
            specs=data.get('specs', {}),
            machineID=data.get('machineID', {})
        )

    @classmethod
    def create_empty(cls):
        return cls(
            partID='',
            partName="",
            partDescription="",
            modelNumber="",
            manufacturer="",
            location="",
            notes="",
            category="",
            specs={},
            machineID={},
            stock={"new": 0, "used": 0, "installed": 0}
        )


    def total_quantity(self):
        return self.stock["new"] + self.stock["used"] + self.stock["installed"]

    def quantityUpdate(self, new_quantity):
        """Updates the quantity of the part."""
        if new_quantity < 0:
            type_print("Quantity cannot be negative. Setting quantity to 0.")
            new_quantity = 0
        self.stock["new"] = new_quantity

    def usedQuantityUpdate(self, new_used_quantity):
        """Updates the used quantity of the part."""
        if new_used_quantity < 0:
            type_print("Used quantity cannot be negative. Setting used quantity to 0.")
            new_used_quantity = 0
        self.stock["used"] = new_used_quantity

    def descriptionUpdate(self, new_description):
        """Updates the description of the part."""
        if new_description == 'QUIT':
            type_print("Part description update cancelled.")
            return
        self.partDescription = new_description
    
    def nameUpdate(self, new_name):
        """Updates the name of the part."""
        if new_name == 'QUIT':
            type_print("Part name update cancelled.")
            return
        self.partName = new_name

    def modelUpdate(self, new_model):
        """Updates the model number of the part."""
        if new_model == 'QUIT':
            type_print("Part model number update cancelled.")
            return
        self.modelNumber = new_model

    def manufacturerUpdate(self, new_manufacturer):
        """Updates the manufacturer of the part."""
        if new_manufacturer == 'QUIT':
            type_print("Part manufacturer update cancelled.")
            return
        self.manufacturer = new_manufacturer

    def locationUpdate(self, new_location):
        """Updates the location of the part."""
        if new_location == 'QUIT':
            type_print("Part location update cancelled.")
            return
        self.location = new_location

    def notesUpdate(self, new_notes):
        """Updates the notes of the part."""
        if new_notes == 'QUIT':
            type_print("Part notes update cancelled.")
            return
        self.notes = new_notes  

    def categoryUpdate(self, new_category):
        """Updates the category of the part."""
        if new_category == 'QUIT':
            type_print("Part category update cancelled.")
            return
        self.category = new_category
    
    def isStockLow(self, threshold):
        """Checks if the part's quantity is below the specified threshold."""
        return self.total_quantity() < threshold
    
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
            machineDescription=data.get('machineDescription') or '',
            machineLocation=data.get('machineLocation', ''),
            part_contained_ID=data.get('part_contained_ID', {})
        )
    
    def partTable(self, partsList, categoriesList=None):
        """Returns a string table showing installed parts and their stock breakdown."""

        if not self.part_contained_ID:
            return "No parts assigned to this machine."

        lines = []

        header = f"{'Part ID':<10} {'Part Model':<18} {'Category':<18} {'On Machine':>10} {'New':>8} {'Used':>8} {'Installed':>10} {'Total':>8}"
        separator = "-" * len(header)

        lines.append(header)
        lines.append(separator)

        for partID, quantity in self.part_contained_ID.items():
            part = partsList.get(partID)

            if part is not None:
                model = part.modelNumber
                category_value = part.category
                if categoriesList:
                    category = categoriesList.get(category_value)
                    if category is not None:
                        category_value = category.categoryName
                stock_new = part.stock.get('new', 0)
                stock_used = part.stock.get('used', 0)
                stock_installed = part.stock.get('installed', 0)
                stock_total = part.total_quantity()
            else:
                model = f"Unknown Part ID {partID}"
                category_value = "Unknown"
                stock_new = 0
                stock_used = 0
                stock_installed = 0
                stock_total = 0

            lines.append(
                f"{partID:<10} {model:<18} {str(category_value):<18} {quantity:>10} "
                f"{stock_new:>8} {stock_used:>8} {stock_installed:>10} {stock_total:>8}"
            )

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

    def to_dict(self):
        return {
            'roomID': self.roomID,
            'roomName': self.roomName,
            'roomDescription': self.roomDescription,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            roomID=data.get('roomID', ''),
            roomName=data.get('roomName', ''),
            roomDescription=data.get('roomDescription', ''),
        )

    def updateName(self, new_name):
        if new_name == 'QUIT':
            type_print("Room name update cancelled.")
            return
        self.roomName = new_name

    def updateDescription(self, new_description):
        if new_description == 'QUIT':
            type_print("Room description update cancelled.")
            return
        self.roomDescription = new_description


@dataclass
class UserAccount:
    username: str
    password_hash: str
    role: str
    must_change_password: bool = False

    def to_dict(self):
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'must_change_password': self.must_change_password,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            role=data.get('role', 'viewer'),
            must_change_password=bool(data.get('must_change_password', False)),
        )



@dataclass
class categories:
    categoryID: str
    categoryName: str
    categoryDescription: str
    specList: list = field(default_factory=list)

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
        if new_name == 'QUIT':
            type_print("Category name update cancelled.")
            return
        self.categoryName = new_name

    def updateDescription(self, new_description):
        if new_description == 'QUIT':
            type_print("Category description update cancelled.")
            return
        self.categoryDescription = new_description

    
