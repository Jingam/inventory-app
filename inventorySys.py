import json
import base64
import hashlib
import hmac
import os
from datetime import datetime

from auth import hash_password, is_valid_role, normalize_role, verify_password
from models import *
from util import *

#==========================  Main Inventory System Class =========================
class inventorySystem:
    typespeed = 0.02
    DATA_KEY_ENV = 'INVENTORY_DATA_KEY'
    DATA_FORMAT_VERSION = 'invsys-v1'
    _DATA_KDF_SALT = b'inventory-app-data-salt-v1'
    _DATA_KEY_FALLBACK = 'inventory-app-dev-key'
    ACTION_PERMISSIONS = {
        'manage_users': {'admin'},
        'view_reports': {'admin', 'manager'},
        'manage_parts': {'admin', 'manager'},
        'manage_machines': {'admin', 'manager'},
        'update_stock': {'admin', 'technician'},
        'install_parts': {'admin', 'technician'},
        'baseline_machine_build': {'admin'},
        'manage_rooms': {'admin'},
        'manage_categories': {'admin'},
    }

    def __init__(self, file_path='inventory_data.json'):
        self.partsList: dict[str, Parts] = {}  # Initialize an empty dictionary to hold parts in the inventory system
        self.machineList: dict[str, Machine] = {}  # Initialize an empty dictionary to hold machines in the inventory system
        self.roomList: dict[str, Room] = {}  # Initialize an empty list to hold rooms in the inventory system
        self.categoriesList: dict[str, categories] = {} # Initialize an empty list to hold categories in the inventory system
        self.users: dict[str, UserAccount] = {}
        self.reportLogs: list[str] = []
        self.file_path = file_path
        self._ensure_default_admin()


 #==========================  Helper Functions =========================

    def _assign_sequential_key(self, existing_items: dict, prefix: str):
        """Assigns a unique key with a prefix and 3-digit incrementing suffix."""
        if not existing_items:
            return f"{prefix}001"

        last_key = sorted(existing_items.keys())[-1]
        last_number = int(last_key[1:])
        return f"{prefix}{last_number + 1:03d}"

    def assignPartKey(self):
        """Assigns a unique key for a new part in the inventory system."""
        return self._assign_sequential_key(self.partsList, 'P')
        
    def assignMachineKey(self):
        """Assigns a unique key for a new machine in the inventory system."""
        return self._assign_sequential_key(self.machineList, 'M')
        
    def assignRoomKey(self):
        """Assigns a unique key for a new room in the inventory system."""
        return self._assign_sequential_key(self.roomList, 'R')
        
    def assignCategoryKey(self):
        """Assigns a unique key for a new category in the inventory system."""
        return self._assign_sequential_key(self.categoriesList, 'C')
        
    
    #==========================  Lookup Helpers =========================

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
        return self.find_by_field(self.partsList, 'modelNumber', modelNumber)
    
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
                f"Quantity: {checkEmptyInfo(part.total_quantity())}, "
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

    #==========================  Selection Helpers =========================

    def choose_from_dict(self, data_dict, id_field, name_field):
        """Lets the user choose an object from a dictionary."""

        if not data_dict:
            print("No items found.")
            return None

        items = list(data_dict.values())

        print_header("Select from List")

        for index, obj in enumerate(items, start=1):
            obj_id = getattr(obj, id_field)
            obj_name = getattr(obj, name_field)
            print(f"{index}. {obj_id} - {obj_name}")

        if len(items) > 7:
            pause_for_user()

        selected_index = choose_index_or_quit(len(items))
        if selected_index is None:
            return None

        return items[selected_index]

    def choose_room(self):
        return self.choose_from_dict(self.roomList, "roomID", "roomName")
    
    def choose_machine(self):
        if not self.machineList:
            print("No items found.")
            pause_for_user()
            return None

        machines = list(self.machineList.values())

        print_header("Select Machine")
        print(f"{'#':<4} {'Machine ID':<12} {'Name':<24} {'Location':<14} {'Parts Qty':>10}")
        print("-" * 72)

        for index, machine in enumerate(machines, start=1):
            room_label = machine.machineLocation
            room_obj = self.roomList.get(machine.machineLocation)
            if room_obj is not None:
                room_label = f"{room_obj.roomID}-{room_obj.roomName}"

            total_parts_qty = sum(int(qty) for qty in machine.part_contained_ID.values())
            print(
                f"{index:<4} {machine.machineID:<12} {machine.machineName:<24} "
                f"{str(room_label):<14} {total_parts_qty:>10}"
            )

        if len(machines) > 7:
            pause_for_user()

        selected_index = choose_index_or_quit(len(machines))
        if selected_index is None:
            return None

        return machines[selected_index]
    
    def choose_part(self):
        if not self.partsList:
            print("No items found.")
            pause_for_user()
            return None

        parts = list(self.partsList.values())

        print_header("Select Part")
        print(f"{'#':<4} {'Part ID':<10} {'Model':<16} {'New':>6} {'Installed':>10} {'Used':>6} {'Total':>7} {'Category':<16}")
        print("-" * 95)

        for index, part in enumerate(parts, start=1):
            category_value = part.category or "None"
            category_obj = self.categoriesList.get(category_value)
            if category_obj is not None:
                category_value = category_obj.categoryName

            qty_new = part.stock.get('new', 0)
            qty_installed = part.stock.get('installed', 0)
            qty_used = part.stock.get('used', 0)

            print(
                f"{index:<4} {part.partID:<10} {part.modelNumber:<16} "
                f"{qty_new:>6} {qty_installed:>10} {qty_used:>6} {part.total_quantity():>7} "
                f"{str(category_value):<16}"
            )

        if len(parts) > 7:
            pause_for_user()

        selected_index = choose_index_or_quit(len(parts))
        if selected_index is None:
            return None

        return parts[selected_index]
    
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

    #==========================  Relationship Helpers =========================

    def _resolve_category_id(self, category_value):
        """Resolves category input to a known category ID when possible."""
        if not category_value:
            return None

        normalized = normalize_text(category_value)
        if normalized in self.categoriesList:
            return normalized

        for category in self.categoriesList.values():
            if normalize_text(category.categoryName) == normalized:
                return category.categoryID

        return category_value

    def _normalize_part_categories(self):
        for part in self.partsList.values():
            category_id = self._resolve_category_id(part.category)
            if category_id in self.categoriesList:
                part.category = category_id

    def _sync_part_machine_links(self):
        for part in self.partsList.values():
            part.machineID = {}

        for machine in self.machineList.values():
            for part_id, qty in machine.part_contained_ID.items():
                part = self.partsList.get(part_id)
                if part is not None:
                    part.machineID[machine.machineID] = qty

    def sync_relationships(self):
        self._normalize_part_categories()
        self._sync_part_machine_links()

    def get_parts_by_category(self, category_id):
        return [
            part for part in self.partsList.values()
            if normalize_text(str(part.category)) == normalize_text(str(category_id))
        ]

    def get_part_ids_by_category(self, category_id):
        return [part.partID for part in self.get_parts_by_category(category_id)]

    def get_machines_by_part(self, part_id):
        """Returns machines that currently contain the given part."""
        machines = []
        for machine in self.machineList.values():
            quantity = machine.part_contained_ID.get(part_id, 0)
            if quantity > 0:
                machines.append((machine, quantity))
        return machines

    def partMachineTable(self, part_id):
        """Returns a string table of machines using a specific part."""

        part = self.partsList.get(part_id)
        if part is None:
            return "Part not found."

        machines = self.get_machines_by_part(part_id)
        if not machines:
            return "This part is not used on any machines."

        lines = []
        header = f"{'Machine ID':<12} {'Machine Name':<24} {'Location':<12} {'Quantity':>10}"
        separator = "-" * len(header)

        lines.append(header)
        lines.append(separator)

        for machine, quantity in machines:
            lines.append(
                f"{machine.machineID:<12} {machine.machineName:<24} {machine.machineLocation:<12} {quantity:>10}"
            )

        return "\n".join(lines)

#=========================  User Management Functions =========================
    def has_permission(self, actor_role, action):
        allowed_roles = self.ACTION_PERMISSIONS.get(action, set())
        return normalize_role(actor_role) in allowed_roles

    def require_permission(self, actor_role, action):
        if self.has_permission(actor_role, action):
            return True
        return False

    def _ensure_default_admin(self):
        if 'admin' not in self.users:
            self.users['admin'] = UserAccount(
                username='admin',
                password_hash=hash_password('admin123'),
                role='admin',
                must_change_password=True,
            )
            self._log('SYSTEM', 'Created default admin account.')

    def _find_user_key(self, username):
        normalized = (username or '').strip().upper()
        if not normalized:
            return None

        for key in self.users.keys():
            if key.upper() == normalized:
                return key

        return None

    def _log(self, actor, action):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.reportLogs.append(f'[{timestamp}] {actor}: {action}')

    def get_recent_logs(self, limit=50, actor_role='viewer'):
        if not self.require_permission(actor_role, 'view_reports'):
            return []
        return self.reportLogs[-limit:]

    def authenticate_user(self, username, password):
        user_key = self._find_user_key(username)
        if user_key is None:
            return None
        account = self.users.get(user_key)
        if account is None:
            return None
        if not verify_password(password, account.password_hash):
            return None
        return account

    def list_users(self):
        return sorted(self.users.values(), key=lambda user: user.username.upper())

    def add_user(self, username, password, role, must_change_password=False, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_users'):
            return False, 'Access denied: only admin can manage users.'

        username = (username or '').strip()
        if not username:
            return False, 'Username cannot be empty.'
        if username in self.users:
            return False, f'User {username} already exists.'

        role = normalize_role(role)
        if not is_valid_role(role):
            return False, 'Invalid role. Use admin, manager, technician, or viewer.'

        self.users[username] = UserAccount(
            username=username,
            password_hash=hash_password(password),
            role=role,
            must_change_password=must_change_password,
        )
        self._log('ADMIN', f'Added user {username} ({role}).')
        self.saveData(self.file_path)
        return True, f'User {username} created.'

    def remove_user(self, username, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_users'):
            return False, 'Access denied: only admin can manage users.'

        user_key = self._find_user_key(username)
        if user_key is None:
            return False, f'User {username} not found.'

        if user_key == 'admin':
            return False, 'Built-in admin cannot be removed.'
        self.users.pop(user_key)
        self._log('ADMIN', f'Removed user {user_key}.')
        self.saveData(self.file_path)
        return True, f'User {user_key} removed.'

    def reset_password(self, username, new_password, must_change_password=True, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_users'):
            return False, 'Access denied: only admin can manage users.'

        user_key = self._find_user_key(username)
        if user_key is None:
            return False, f'User {username} not found.'

        account = self.users.get(user_key)
        if account is None:
            return False, f'User {username} not found.'
        account.password_hash = hash_password(new_password)
        account.must_change_password = must_change_password
        self._log('ADMIN', f'Reset password for {user_key}.')
        self.saveData(self.file_path)
        return True, f'Password reset for {user_key}.'

    def change_password(self, username, old_password, new_password):
        account = self.authenticate_user(username, old_password)
        if account is None:
            return False, 'Current password is incorrect.'
        account.password_hash = hash_password(new_password)
        account.must_change_password = False
        self._log(username, 'Changed password.')
        self.saveData(self.file_path)
        return True, 'Password changed successfully.'

    def set_user_role(self, username, role, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_users'):
            return False, 'Access denied: only admin can manage users.'

        user_key = self._find_user_key(username)
        if user_key is None:
            return False, f'User {username} not found.'

        account = self.users.get(user_key)
        if account is None:
            return False, f'User {username} not found.'
        role = normalize_role(role)
        if not is_valid_role(role):
            return False, 'Invalid role. Use admin, manager, technician, or viewer.'
        account.role = role
        self._log('ADMIN', f'Updated role for {user_key} to {role}.')
        self.saveData(self.file_path)
        return True, f'Role for {user_key} updated to {role}.'



    def install_part_to_machine_from_bucket(self, machine, part, quantity, source_bucket='new', actor_role='viewer'):
        if not self.require_permission(actor_role, 'install_parts'):
            return False, 'Access denied: only technician or admin can install parts.'

        if quantity <= 0:
            return False, 'Quantity must be greater than zero.'

        source_bucket = normalize_text(source_bucket).lower()
        if source_bucket not in ('new', 'used'):
            return False, 'Source bucket must be new or used.'

        available_qty = part.stock.get(source_bucket, 0)
        if quantity > available_qty:
            return False, f'Only {available_qty} {source_bucket} units are available.'

        current_qty = machine.part_contained_ID.get(part.partID, 0)
        machine.part_contained_ID[part.partID] = current_qty + quantity
        part.stock[source_bucket] = available_qty - quantity
        part.stock['installed'] = part.stock.get('installed', 0) + quantity
        part.machineID[machine.machineID] = machine.part_contained_ID[part.partID]
        self._log(
            actor_role.upper(),
            f'Installed {quantity}x {part.partID} to {machine.machineID} from {source_bucket} stock.',
        )
        self.saveData(self.file_path)
        return True, 'Part installed successfully.'

    def install_part_to_machine(self, machine, part, quantity, actor_role='viewer'):
        """Compatibility wrapper: installs from new stock by default."""
        return self.install_part_to_machine_from_bucket(
            machine,
            part,
            quantity,
            source_bucket='new',
            actor_role=actor_role,
        )

    def baseline_load_machine_part(self, machine, part, quantity, actor_role='viewer'):
        """Admin-only baseline load for initial database setup; does not consume new/used stock."""
        if not self.require_permission(actor_role, 'baseline_machine_build'):
            return False, 'Access denied: only admin can perform baseline machine load.'

        if quantity <= 0:
            return False, 'Quantity must be greater than zero.'

        current_qty = machine.part_contained_ID.get(part.partID, 0)
        machine.part_contained_ID[part.partID] = current_qty + quantity
        part.stock['installed'] = part.stock.get('installed', 0) + quantity
        part.machineID[machine.machineID] = machine.part_contained_ID[part.partID]

        self._log('ADMIN', f'Baseline loaded {quantity}x {part.partID} on {machine.machineID}.')
        self.saveData(self.file_path)
        return True, 'Baseline machine part load completed.'

    def move_installed_to_used(self, machine, part, quantity, destination, actor_role='viewer'):
        if not self.require_permission(actor_role, 'update_stock'):
            return False, 'Access denied: only technician or admin can move installed stock.'

        if quantity <= 0:
            return False, 'Quantity must be greater than zero.'

        installed_on_machine = machine.part_contained_ID.get(part.partID, 0)
        if quantity > installed_on_machine:
            return False, f'Only {installed_on_machine} installed units are available on this machine.'

        machine.part_contained_ID[part.partID] = installed_on_machine - quantity
        if machine.part_contained_ID[part.partID] == 0:
            machine.part_contained_ID.pop(part.partID, None)

        part.stock['installed'] = max(0, part.stock.get('installed', 0) - quantity)

        destination = normalize_text(destination)
        if destination == 'INVENTORY':
            part.stock['used'] = part.stock.get('used', 0) + quantity
        elif destination != 'DISCARD':
            return False, 'Destination must be inventory or discard.'

        if part.partID in machine.part_contained_ID:
            part.machineID[machine.machineID] = machine.part_contained_ID[part.partID]
        else:
            part.machineID.pop(machine.machineID, None)

        self._log('TECHNICIAN', f'Moved {quantity}x {part.partID} from {machine.machineID} to {destination}.')
        self.saveData(self.file_path)
        return True, 'Installed stock updated successfully.'

    def getRoomMachineList(self, roomID):
        return self.roomMachineTable(roomID)

    def _get_data_secret(self):
        secret = os.environ.get(self.DATA_KEY_ENV, '').strip()
        if secret:
            return secret
        return self._DATA_KEY_FALLBACK

    def _derive_data_keys(self):
        secret = self._get_data_secret().encode('utf-8')
        key_material = hashlib.pbkdf2_hmac(
            'sha256',
            secret,
            self._DATA_KDF_SALT,
            200_000,
            dklen=64,
        )
        return key_material[:32], key_material[32:]

    def _stream_xor(self, payload: bytes, encryption_key: bytes, nonce: bytes):
        output = bytearray(len(payload))
        offset = 0
        counter = 0

        while offset < len(payload):
            stream_block = hashlib.sha256(
                encryption_key + nonce + counter.to_bytes(8, 'big')
            ).digest()
            block_len = min(32, len(payload) - offset)

            for i in range(block_len):
                output[offset + i] = payload[offset + i] ^ stream_block[i]

            offset += block_len
            counter += 1

        return bytes(output)

    def _encrypt_payload_dict(self, data: dict):
        encryption_key, mac_key = self._derive_data_keys()
        plaintext = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        nonce = os.urandom(16)
        ciphertext = self._stream_xor(plaintext, encryption_key, nonce)
        tag = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()

        return {
            '__enc__': self.DATA_FORMAT_VERSION,
            'kdf': 'pbkdf2-sha256',
            'iter': 200000,
            'nonce': base64.b64encode(nonce).decode('ascii'),
            'ciphertext': base64.b64encode(ciphertext).decode('ascii'),
            'mac': base64.b64encode(tag).decode('ascii'),
        }

    def _decrypt_payload_dict(self, encrypted_data: dict):
        encryption_key, mac_key = self._derive_data_keys()

        try:
            nonce = base64.b64decode(encrypted_data['nonce'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            provided_tag = base64.b64decode(encrypted_data['mac'])
        except (KeyError, ValueError, TypeError) as error:
            raise ValueError('Encrypted data payload is invalid.') from error

        expected_tag = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_tag, provided_tag):
            raise ValueError('Encrypted data verification failed. Wrong key or tampered file.')

        plaintext = self._stream_xor(ciphertext, encryption_key, nonce)

        try:
            return json.loads(plaintext.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError('Encrypted payload could not be decoded.') from error
    

#=========================  Data Persistence Functions =========================


    def loadData(self, file_path='inventory_data.json'):
        """Loads data from the JSON file into the inventory system."""
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                raw_data = json.load(file)

            if isinstance(raw_data, dict) and raw_data.get('__enc__') == self.DATA_FORMAT_VERSION:
                data = self._decrypt_payload_dict(raw_data)
            else:
                data = raw_data

            self.partsList.clear()
            self.machineList.clear()
            self.roomList.clear()
            self.categoriesList.clear()
            self.users.clear()
            self.reportLogs.clear()

            if not isinstance(data, dict):
                print("Invalid inventory data structure. Starting with an empty inventory.")
                return

            parts_data = data.get('parts', {})
            machines_data = data.get('machines', {})
            rooms_data = data.get('rooms', {})
            categories_data = data.get('categories', {})
            users_data = data.get('users', {})
            logs_data = data.get('report_logs', [])

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
                    self.categoriesList[category.categoryID or category_id] = category

            if isinstance(users_data, dict):
                for username, user_data in users_data.items():
                    if isinstance(user_data, dict):
                        user = UserAccount.from_dict(user_data)
                        resolved_username = user.username or username
                        if resolved_username:
                            self.users[resolved_username] = user

            if isinstance(logs_data, list):
                self.reportLogs = [str(line) for line in logs_data]

            self._ensure_default_admin()

            self.sync_relationships()

        except FileNotFoundError:
            print("Data file not found. Starting with an empty inventory.")
        except json.JSONDecodeError:
            print("Error decoding JSON data. Starting with an empty inventory.")
        except ValueError as error:
            print(f"Error loading encrypted data: {error}")

    def saveData(self, file_path='inventory_data.json'):
        """Saves data from the inventory system to the JSON file."""
        self.file_path = file_path
        self.sync_relationships()
        data = {
            'parts': {part_id: part.to_dict() for part_id, part in self.partsList.items()},
            'machines': {machine_id: machine.to_dict() for machine_id, machine in self.machineList.items()},
            'rooms': {room_id: room.to_dict() for room_id, room in self.roomList.items()},
            'categories': {cat_id: cat.to_dict() for cat_id, cat in self.categoriesList.items()},
            'users': {username: user.to_dict() for username, user in self.users.items()},
            'report_logs': self.reportLogs,
        }

        encrypted_payload = self._encrypt_payload_dict(data)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(encrypted_payload, file, indent=2)


#=========================  Part Operation Functions =========================
    def _select_or_create_category_for_part(self, actor_role='viewer'):
        """Lets the user select an existing category or create a new one."""
        while True:
            if not self.categoriesList:
                type_print('No categories exist yet for parts.')
                create_now = userInputConfirm('Would you like to add a category now?')
                if not create_now:
                    return None

                new_category = self.addCategory(actor_role=actor_role)
                if new_category is not None:
                    return new_category

                type_print('Category was not added. Please try again.')
                continue

            print_header('Select Category for Part')
            selected_category = self.choose_category()
            if selected_category is not None:
                return selected_category

            add_instead = userInputConfirm('Would you like to add a new category instead?')
            if not add_instead:
                return None

            new_category = self.addCategory(actor_role=actor_role)
            if new_category is not None:
                return new_category

    def _collect_specs_for_category(self, category_choice):
        """Collects part specs based on the selected category's spec list."""
        specs = {}
        if category_choice is None:
            return specs

        spec_fields = category_choice.specList or []
        if not spec_fields:
            return specs

        print_header(f"Enter Specs: {category_choice.categoryName}")
        for field_name in spec_fields:
            field_label = str(field_name).strip()
            if not field_label:
                continue

            value = optionalStrInput(f"Enter {field_label} (optional)")
            if value == 'quit':
                return None
            if value is not None:
                specs[field_label] = value

        return specs

    def addPart(self, actor_role='viewer'):
        """Adds a new part to the inventory system."""
        if not self.require_permission(actor_role, 'manage_parts'):
            type_print('Access denied: only manager or admin can add parts.')
            return

        partModel = mandateStrInput("Enter part model:").upper()
        if partModel == 'QUIT':
            return
        existingPart = self.getPartByModel(partModel)
        if existingPart:
            type_print(f"Part with model number {existingPart} already exists in the inventory.", self.typespeed)
            return
        else:
            if userInputConfirm(f'Confirm you would like to add {partModel} to inventory: Y or N?') is False:
                return
            else:
                type_print(f"Adding new part with model number {partModel}.\n", self.typespeed)
                new_partID = self.assignPartKey()
                partName = mandateStrInput("Enter part name:")
                if partName == 'QUIT':
                    return
                partDescription = optionalStrInput("Enter part description (optional):")
                if partDescription == 'quit':
                    return
                manufacturer = mandateStrInput("Enter part manufacturer:")
                if manufacturer == 'QUIT':
                    return
                quantity = validateNumInput()
                location = optionalStrInput("Enter location:")
                if location == 'quit':
                    return
                notes = optionalStrInput("Enter notes (optional):")
                if notes == 'quit':
                    return

                category_choice = self._select_or_create_category_for_part(actor_role=actor_role)
                if category_choice is None:
                    type_print('Part creation cancelled. A category selection is required.')
                    return

                category_id = category_choice.categoryID
                specs = self._collect_specs_for_category(category_choice)
                if specs is None:
                    type_print('Part creation cancelled.')
                    return

            new_part = Parts(
                partID=new_partID,
                partName=partName,
                partDescription=partDescription,
                modelNumber=partModel,
                manufacturer=manufacturer,
                stock={"new": quantity, "used": 0, "installed": 0},
                location=location,
                notes=notes,
                category=category_id,
                specs=specs
            )
            self.partsList[new_partID] = new_part
            self._log('MANAGER', f'Added part {new_partID} ({partModel}).')
            self.saveData(self.file_path)
            type_print(f"Part {partName} with model number {partModel} added successfully.\n", self.typespeed)


    def removePart(self, actor_role='viewer'):
        """Remove part from parts list"""
        if not self.require_permission(actor_role, 'manage_parts'):
            type_print('Access denied: only manager or admin can remove parts.')
            return

        while True:
            if not self.partsList:
                type_print("No parts exists in list yet, please enter part first")
                return
            type_print('Select part ID from following list')
            del_part = self.choose_part()
            if del_part is None: return

            delSelect = userInputConfirm(f"Are you sure you want to delete {del_part.modelNumber}?")
            if delSelect:
                for machine in self.machineList.values():
                    machine.part_contained_ID.pop(del_part.partID, None)
                self.partsList.pop(del_part.partID, None)
                self._log('MANAGER', f'Removed part {del_part.partID}.')
                self.saveData(self.file_path)
                type_print(f"Part {del_part.modelNumber} removed.")
            else:
                type_print("Deletion cancelled.")
            self.saveData(self.file_path)

    def add_stock(self, part, condition, amount, actor_role='viewer'):
        if not self.require_permission(actor_role, 'update_stock'):
            return False, 'Access denied: only technician or admin can update stock.'
        if condition not in part.stock:
            return False, 'Invalid stock bucket.'

        new_value = part.stock.get(condition, 0) + amount
        if new_value < 0:
            return False, 'Stock cannot go below zero.'

        part.stock[condition] = new_value
        self._log(actor_role.upper(), f'Adjusted {condition} stock for {part.partID} by {amount}.')
        self.saveData(self.file_path)
        return True, 'Stock updated.'

    def update_part_field(self, part, field_name, new_value, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_parts'):
            return False, 'Access denied: only manager or admin can update part details.'

        if part is None:
            return False, 'Part not found.'

        if field_name == 'name':
            part.nameUpdate(new_value)
        elif field_name == 'description':
            part.descriptionUpdate(new_value)
        elif field_name == 'model':
            part.modelUpdate(new_value)
        elif field_name == 'manufacturer':
            part.manufacturerUpdate(new_value)
        elif field_name == 'location':
            part.locationUpdate(new_value)
        elif field_name == 'notes':
            part.notesUpdate(new_value)
        elif field_name == 'category':
            part.categoryUpdate(self._resolve_category_id(new_value))
        else:
            return False, 'Invalid part field.'

        self.sync_relationships()
        self.saveData(self.file_path)
        return True, 'Part updated successfully.'

    def update_part_category_details(self, part, category_id, specs, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_parts'):
            return False, 'Access denied: only manager or admin can update part details.'

        if part is None:
            return False, 'Part not found.'

        resolved_category_id = self._resolve_category_id(category_id)
        if resolved_category_id not in self.categoriesList:
            return False, 'Selected category was not found.'

        part.categoryUpdate(resolved_category_id)
        part.specs = specs or {}

        self.sync_relationships()
        self.saveData(self.file_path)
        return True, 'Part category and specs updated successfully.'

    def update_machine_field(self, machine, field_name, new_value, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_machines'):
            return False, 'Access denied: only manager or admin can update machine details.'

        if machine is None:
            return False, 'Machine not found.'

        if field_name == 'name':
            machine.updateName(new_value)
        elif field_name == 'description':
            machine.updateDescription(new_value)
        elif field_name == 'room':
            if new_value not in self.roomList:
                return False, 'Selected room was not found.'
            machine.updateLocation(new_value)
        else:
            return False, 'Invalid machine field.'

        self.saveData(self.file_path)
        return True, 'Machine updated successfully.'

    def viewPartList(self, actor_role='viewer'):
        """Displays a list of all parts in the inventory system."""
        if not self.partsList:
            type_print("No parts in the inventory.\n", self.typespeed)
            return

        partChoice = self.choose_part()
        if partChoice is None:
            return
        else:
            print()
            type_print(f"ID: {partChoice.partID}", self.typespeed)
            type_print(f"Name: {partChoice.partName}", self.typespeed)
            type_print(f"Description: {partChoice.partDescription}", self.typespeed)
            type_print(f"Model Number: {partChoice.modelNumber}", self.typespeed)
            type_print(f"Manufacturer: {partChoice.manufacturer}", self.typespeed)
            type_print(f"Quantity (New): {partChoice.stock.get('new', 0)}", self.typespeed)
            type_print(f"Quantity (Installed): {partChoice.stock.get('installed', 0)}", self.typespeed)
            type_print(f"Quantity (Used): {partChoice.stock.get('used', 0)}", self.typespeed)
            type_print(
                f"Stock Distribution: New={partChoice.stock.get('new', 0)} | "
                f"Installed={partChoice.stock.get('installed', 0)} | "
                f"Used={partChoice.stock.get('used', 0)} | "
                f"Total={partChoice.total_quantity()}",
                self.typespeed,
            )
            type_print(f"Location: {partChoice.location}", self.typespeed)
            type_print(f"Notes: {partChoice.notes}", self.typespeed)
            category_label = partChoice.category
            category_obj = self.categoriesList.get(partChoice.category)
            if category_obj is not None:
                category_label = f"{category_obj.categoryID} - {category_obj.categoryName}"
            type_print(f"Category: {category_label}", self.typespeed)
            if partChoice.specs:
                specs_line = ", ".join(f"{key}: {value}" for key, value in partChoice.specs.items())
                type_print(f"Specs: {specs_line}\n", self.typespeed)
            else:
                type_print("Specs: None\n", self.typespeed)
            pause_for_user()
            return partChoice

#==========================  Machine Operation Functions =========================

    def addMachine(self, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_machines'):
            type_print('Access denied: only manager or admin can add machines.')
            return

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

        type_print(f"Adding new machine with name {newMachineName}\n")

        machineID = self.assignMachineKey()

        type_print("Select a room for the machine from the following list:")
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
        self._log('MANAGER', f'Added machine {machineID} ({newMachineName}).')
        self.saveData(self.file_path)

        type_print(
            f"Machine: {newMachineName} with ID: {machineID} "
            f"added to room {roomChoice.roomName} successfully"
    )
            


    def removeMachine(self, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_machines'):
            type_print('Access denied: only manager or admin can remove machines.')
            return

        while True:
            if not self.machineList:
                type_print("No machines exists in list yet, please add a machine first")
                return
            
            type_print("Choose a list from the following:")
            machineChoice = self.choose_machine()
            if machineChoice is None: return
            else:
                delSelect = userInputConfirm(f"Are you sure you want to delete {machineChoice.machineName}?")
                if delSelect:
                    for part_id, quantity in machineChoice.part_contained_ID.items():
                        part = self.partsList.get(part_id)
                        if part is not None:
                            part.stock['installed'] = max(0, part.stock.get('installed', 0) - quantity)
                            part.stock['new'] = part.stock.get('new', 0) + quantity
                            part.machineID.pop(machineChoice.machineID, None)

                    self.machineList.pop(machineChoice.machineID, None)
                    self._log('MANAGER', f'Removed machine {machineChoice.machineID}.')
                    self.saveData(self.file_path)
                    type_print(f'Machine: {machineChoice.machineName} removed.')
                else:
                    type_print("Deletion cancelled.")
            
    def add_part_to_machine(self, machineChoice, actor_role='viewer'):
        if not self.require_permission(actor_role, 'install_parts'):
            type_print('Access denied: only technician or admin can install parts.')
            return

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
            ok, message = self.install_part_to_machine(machineChoice, partChoice, partQuantity, actor_role=actor_role)
            type_print(message)


    def viewMachineList(self):
        print_header('Machine Details')
        machine = self.choose_machine()

        if machine is None:
            return None

        print(f"\nID: {machine.machineID}")
        print(f"Name: {machine.machineName}")
        print(f"Location: {machine.machineLocation}")
        print(f"Description: {machine.machineDescription}")
        print("\nParts:")
        print(machine.partTable(self.partsList, self.categoriesList))
        pause_for_user()

        return machine

    
#=========================  Room Operation Functions =========================

    def addRoom(self, actor_role='viewer'):
        """Adds a new room to the inventory system."""
        if not self.require_permission(actor_role, 'manage_rooms'):
            type_print('Access denied: only admin can add rooms.')
            return

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

    def removeRoom(self, roomChoice, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_rooms'):
            type_print('Access denied: only admin can remove rooms.')
            return

        if not self.roomList:
            type_print("No rooms exists in list yet, please add a room first")
            return
            
        if roomChoice is None: return
        else:
            delSelect = userInputConfirm(f"Are you sure you want to delete {roomChoice}?")
            if delSelect:
                for machine in self.machineList.values():
                    if machine.machineLocation == roomChoice:
                        type_print("Room cannot be removed while machines are assigned to it.")
                        return
                self.roomList.pop(roomChoice, None)
                self.saveData(self.file_path)
                type_print(f'Room: {roomChoice} removed.')
            else:
                type_print("Deletion cancelled.")
        self.saveData(self.file_path)


    def updateRoom(self, machineID, newRoomID, actor_role='viewer'):
        """Updates the room ID assigned to a machine."""

        if not self.require_permission(actor_role, 'manage_rooms'):
            type_print('Access denied: only admin can update rooms.')
            return False

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

        print_header('Room Overview')
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


    def addCategory(self, actor_role='viewer'):
        """Adds a new category to the inventory system."""
        if not self.require_permission(actor_role, 'manage_categories'):
            type_print('Access denied: only admin can add categories.')
            return None

        newCategoryName = mandateStrInput("Enter the name of the category you wish to add")
        if newCategoryName in (None, 'QUIT'):
            return None
        existingCategory = self.getCategoryByName(newCategoryName)
        if existingCategory is not None:
            type_print(f'Category with name {newCategoryName} already exists')
            return None
        if userInputConfirm(f"Confirm you would like to add {newCategoryName} to inventory") is False:
            return None
        else:
            type_print(f'Adding new category with name {newCategoryName}')
            newCategoryID = self.assignCategoryKey()
            newCategoryDescription = optionalStrInput('Enter the description of category')
            if newCategoryDescription == 'quit':
                return None
            specFields = []
            print("Enter the specification fields for this category. Type 'done' when finished.")
            while True:
                spec_input = mandateStrInput("Enter a specification field (or type 'done' to finish):")
                if normalize_text(spec_input) == 'DONE':
                    break
                if normalize_text(spec_input) == 'QUIT':
                    return
                specFields.append(spec_input)
            
        new_category = categories(
            categoryID = newCategoryID,
            categoryName = newCategoryName,
            categoryDescription = newCategoryDescription,
            specList = specFields
        )
        self.categoriesList[newCategoryID] = new_category
        self.saveData(self.file_path)
        type_print(f'Category: {newCategoryName} with ID: { newCategoryID} added sucessfully')
        return new_category


    def removeCategory(self, categoryChoice, actor_role='viewer'):
        if not self.require_permission(actor_role, 'manage_categories'):
            type_print('Access denied: only admin can remove categories.')
            return

        if not self.categoriesList:
            type_print("No categories exists in list yet, please add a category first")
            return
            
        if categoryChoice is None: return
        else:
            delSelect = userInputConfirm(f"Are you sure you want to delete {categoryChoice}?")
            if delSelect:
                for part in self.partsList.values():
                    if normalize_text(str(part.category)) == normalize_text(str(categoryChoice)):
                        part.category = ''
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

        print_header('Category Overview')
        categoryChoice = self.choose_category()
        if categoryChoice is None:
            return
        else:
            part_ids = self.get_part_ids_by_category(categoryChoice.categoryID)
            type_print(f"ID: {categoryChoice.categoryID}, Name: {categoryChoice.categoryName}, Description: {categoryChoice.categoryDescription}, Specs: {', '.join(categoryChoice.specList)}", speed = 0.005)
            pause_for_user()
            type_print(f"Parts in this category: {', '.join(part_ids) if part_ids else 'None'}", speed = 0.005)
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
                # Update spec list
                
