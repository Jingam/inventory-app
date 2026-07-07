import time
from getpass import getpass

from util import *
from inventorySys import *


ADMIN = 'admin'
MANAGER = 'manager'
TECHNICIAN = 'technician'
VIEWER = 'viewer'


#========================= Shared Access/Auth Helpers =========================

def has_access(user, allowed_roles):
    return user.role in allowed_roles


def require_access(user, allowed_roles):
    if has_access(user, allowed_roles):
        return True
    type_print('Access denied for your role.', speed=0.01)
    return False


def prompt_new_password():
    while True:
        new_password = getpass('Enter new password: ').strip()
        confirm_password = getpass('Confirm new password: ').strip()
        if not new_password:
            type_print('Password cannot be empty.', speed=0.01)
            continue
        if new_password != confirm_password:
            type_print('Passwords do not match.', speed=0.01)
            continue
        return new_password


def login_menu(system):
    show_menu_screen('Login', 'Sign in to continue.')
    while True:
        username = input('Username: ').strip()
        password = getpass('Password: ').strip()
        account = system.authenticate_user(username, password)
        if account is None:
            type_print('Invalid username or password. Try again.', speed=0.01)
            continue

        if account.must_change_password:
            type_print('Password reset required. Please set a new password now.', speed=0.01)
            new_password = prompt_new_password()
            ok, message = system.change_password(username, password, new_password)
            type_print(message, speed=0.01)
            if not ok:
                continue

        type_print(f'Logged in as {account.username} ({account.role}).', speed=0.01)
        return account


#========================= Part Submenus =========================


def update_part_stock_menu(system, current_user):
    part = system.choose_part()
    if part is None:
        return

    type_print(
        f"Current stock for {part.partID}: New={part.stock.get('new', 0)} | "
        f"Installed={part.stock.get('installed', 0)} | "
        f"Used={part.stock.get('used', 0)} | Total={part.total_quantity()}",
        speed=0.01,
    )

    condition = input("Select stock bucket (new/used/installed): ").strip().lower()
    if condition not in ('new', 'used', 'installed'):
        type_print('Invalid stock bucket.', speed=0.01)
        return

    change = input('Enter quantity change (positive to add, negative to subtract): ').strip()
    try:
        delta = int(change)
    except ValueError:
        type_print('Quantity must be a number.', speed=0.01)
        return

    ok, message = system.add_stock(part, condition, delta, actor_role=current_user.role)
    type_print(message, speed=0.01)


def install_part_from_part_view_menu(system, current_user, part):
    if not require_access(current_user, {ADMIN, TECHNICIAN}):
        return

    if not system.machineList:
        type_print('No machines available. Add a machine first.', speed=0.01)
        pause_for_user()
        return

    show_menu_screen(f'Install {part.modelNumber}', 'Choose a machine for this part.')
    machine_choice = system.choose_machine()
    if machine_choice is None:
        return

    if userInputConfirm(f'Install {part.modelNumber} on {machine_choice.machineName}?') is False:
        return

    quantity = validateNumInput()
    ok, message = system.install_part_to_machine(machine_choice, part, quantity, actor_role=current_user.role)
    type_print(message, speed=0.01)


def select_or_create_category_for_part_update(system, current_user):
    while True:
        if not system.categoriesList:
            type_print('No categories exist yet for parts.', speed=0.01)
            create_now = userInputConfirm('Would you like to add a category now?')
            if not create_now:
                return None

            new_category = system.addCategory(actor_role=current_user.role)
            if new_category is not None:
                return new_category

            type_print('Category was not added. Please try again.', speed=0.01)
            continue

        show_menu_screen('Select Category', 'Choose an existing category or quit and add a new one.')
        selected_category = system.choose_category()
        if selected_category is not None:
            return selected_category

        add_instead = userInputConfirm('Would you like to add a new category instead?')
        if not add_instead:
            return None

        new_category = system.addCategory(actor_role=current_user.role)
        if new_category is not None:
            return new_category


def collect_specs_for_category_menu(category_choice):
    specs = {}
    spec_fields = category_choice.specList or []
    if not spec_fields:
        return specs

    show_menu_screen(f'Enter Specs: {category_choice.categoryName}', 'Provide values for category-specific fields.')
    for field_name in spec_fields:
        field_label = str(field_name).strip()
        if not field_label:
            continue

        value = optionalStrInput(f'Enter {field_label} (optional)')
        if value == 'quit':
            return None
        if value is not None:
            specs[field_label] = value

    return specs


def update_part_fields_menu(system, current_user, part):
    if not require_access(current_user, {ADMIN, MANAGER}):
        return

    while True:
        print_header(f'Update Part: {part.modelNumber}')
        print("""
1. Name
2. Description
3. Model number
4. Manufacturer
5. Location
6. Notes
7. Category
8. Back
""")

        user_choice = input('>: ').strip()
        if user_choice == '1':
            new_value = mandateStrInput(f'Enter new name (current: {part.partName})')
            if new_value == 'QUIT':
                continue
            ok, message = system.update_part_field(part, 'name', new_value, actor_role=current_user.role)
        elif user_choice == '2':
            new_value = optionalStrInput(f'Enter new description (current: {part.partDescription})')
            if new_value == 'quit':
                continue
            if new_value is None:
                continue
            ok, message = system.update_part_field(part, 'description', new_value, actor_role=current_user.role)
        elif user_choice == '3':
            new_value = mandateStrInput(f'Enter new model number (current: {part.modelNumber})')
            if new_value == 'QUIT':
                continue
            ok, message = system.update_part_field(part, 'model', new_value, actor_role=current_user.role)
        elif user_choice == '4':
            new_value = mandateStrInput(f'Enter new manufacturer (current: {part.manufacturer})')
            if new_value == 'QUIT':
                continue
            ok, message = system.update_part_field(part, 'manufacturer', new_value, actor_role=current_user.role)
        elif user_choice == '5':
            new_value = optionalStrInput(f'Enter new location (current: {part.location})')
            if new_value == 'quit':
                continue
            if new_value is None:
                continue
            ok, message = system.update_part_field(part, 'location', new_value, actor_role=current_user.role)
        elif user_choice == '6':
            new_value = optionalStrInput(f'Enter new notes (current: {part.notes})')
            if new_value == 'quit':
                continue
            if new_value is None:
                continue
            ok, message = system.update_part_field(part, 'notes', new_value, actor_role=current_user.role)
        elif user_choice == '7':
            category_choice = select_or_create_category_for_part_update(system, current_user)
            if category_choice is None:
                continue

            specs = collect_specs_for_category_menu(category_choice)
            if specs is None:
                type_print('Category update cancelled.', speed=0.01)
                continue

            ok, message = system.update_part_category_details(
                part,
                category_choice.categoryID,
                specs,
                actor_role=current_user.role,
            )
        elif user_choice == '8':
            return
        else:
            type_print('Invalid option please try again.', speed=0.01)
            continue

        type_print(message, speed=0.01)


def part_actions_menu(system, current_user, part):
    while True:
        show_menu_screen(f'Part Actions: {part.modelNumber}', 'Choose what to do with this part.')
        print("""
1. Install on machine
2. Update stock quantity
3. View machines using this part
4. Edit part details
5. Back
""")

        choice = input('>: ').strip()
        if choice == '1':
            install_part_from_part_view_menu(system, current_user, part)
        elif choice == '2':
            if not require_access(current_user, {ADMIN, TECHNICIAN}):
                continue

            condition = input('Select stock bucket (new/used/installed): ').strip().lower()
            if condition not in ('new', 'used', 'installed'):
                type_print('Invalid stock bucket.', speed=0.01)
                continue

            change = input('Enter quantity change (positive to add, negative to subtract): ').strip()
            try:
                delta = int(change)
            except ValueError:
                type_print('Quantity must be a number.', speed=0.01)
                continue

            ok, message = system.add_stock(part, condition, delta, actor_role=current_user.role)
            type_print(message, speed=0.01)
        elif choice == '3':
            print_header(f'Machines using {part.modelNumber}')
            print(system.partMachineTable(part.partID))
            pause_for_user()
        elif choice == '4':
            update_part_fields_menu(system, current_user, part)
        elif choice == '5':
            return
        else:
            type_print('Invalid option please try again.', speed=0.01)


def remove_installed_part_menu(system, current_user):
    machine = system.choose_machine()
    if machine is None:
        return

    if not machine.part_contained_ID:
        type_print('This machine has no installed parts.', speed=0.01)
        return

    print(machine.partTable(system.partsList, system.categoriesList))
    part_id = input('Enter part ID to remove from machine: ').strip().upper()
    if part_id not in machine.part_contained_ID:
        type_print('Part ID not installed on this machine.', speed=0.01)
        return

    part = system.partsList.get(part_id)
    if part is None:
        type_print('Part not found in inventory.', speed=0.01)
        return

    quantity = validateNumInput()
    destination = input('Send removed stock to inventory or discard? ').strip().lower()
    ok, message = system.move_installed_to_used(
        machine,
        part,
        quantity,
        destination,
        actor_role=current_user.role,
    )
    type_print(message, speed=0.01)


def operational_install_part_menu(system, current_user):
    machine = system.choose_machine()
    if machine is None:
        return

    part = system.choose_part()
    if part is None:
        return

    existing_qty = machine.part_contained_ID.get(part.partID, 0)
    if existing_qty > 0:
        type_print(
            f'{machine.machineName} currently has {existing_qty} installed of {part.modelNumber}.',
            speed=0.01,
        )
        if userInputConfirm('Do you want to remove some existing installed units first?'):
            remove_qty = validateNumInput()
            destination = input('Send removed stock to inventory or discard? ').strip().lower()
            ok, message = system.move_installed_to_used(
                machine,
                part,
                remove_qty,
                destination,
                actor_role=current_user.role,
            )
            type_print(message, speed=0.01)
            if not ok:
                return

    source_bucket = input('Install from which stock bucket? (new/used): ').strip().lower()
    if source_bucket not in ('new', 'used'):
        type_print('Invalid stock bucket. Use new or used.', speed=0.01)
        return

    quantity = validateNumInput()
    ok, message = system.install_part_to_machine_from_bucket(
        machine,
        part,
        quantity,
        source_bucket=source_bucket,
        actor_role=current_user.role,
    )
    type_print(message, speed=0.01)


def baseline_load_machine_parts_menu(system, current_user):
    if not require_access(current_user, {ADMIN}):
        return

    show_menu_screen('Baseline Machine Load', 'Admin-only setup path. This does not consume new/used stock.')
    machine = system.choose_machine()
    if machine is None:
        return

    part = system.choose_part()
    if part is None:
        return

    quantity = validateNumInput()
    ok, message = system.baseline_load_machine_part(
        machine,
        part,
        quantity,
        actor_role=current_user.role,
    )
    type_print(message, speed=0.01)


def view_part_machine_usage_menu(system):
    show_menu_screen('Part Machine Usage', 'Select a part to see which machines use it.')
    part = system.choose_part()
    if part is None:
        return

    print_header(f'Machines using {part.modelNumber}')
    print(system.partMachineTable(part.partID))
    pause_for_user()


def edit_part_details_menu(system, current_user):
    show_menu_screen('Edit Part Details', 'Choose a part, then choose the field to update.')
    part = system.choose_part()
    if part is None:
        return

    update_part_fields_menu(system, current_user, part)


def view_part_details_menu(system, current_user):
    show_menu_screen('Part Details', 'Select a part to view.')
    part = system.viewPartList(actor_role=current_user.role)
    if part is None:
        return
    part_actions_menu(system, current_user, part)


#========================= Machine Submenus =========================


def update_machine_fields_menu(system, current_user, machine):
    if not require_access(current_user, {ADMIN, MANAGER}):
        return

    while True:
        room_label = machine.machineLocation
        room_obj = system.roomList.get(machine.machineLocation)
        if room_obj is not None:
            room_label = f"{room_obj.roomID} - {room_obj.roomName}"

        show_menu_screen(f'Update Machine: {machine.machineName}', f'Current room: {room_label}')
        print("""
1. Name
2. Description
3. Room
4. Back
""")

        choice = input('>: ').strip()
        if choice == '1':
            new_name = mandateStrInput(f'Enter new machine name (current: {machine.machineName})')
            if new_name == 'QUIT':
                continue
            ok, message = system.update_machine_field(machine, 'name', new_name, actor_role=current_user.role)
        elif choice == '2':
            new_description = optionalStrInput(f'Enter new description (current: {machine.machineDescription})')
            if new_description == 'quit':
                continue
            if new_description is None:
                new_description = ''
            ok, message = system.update_machine_field(machine, 'description', new_description, actor_role=current_user.role)
        elif choice == '3':
            if not system.roomList:
                type_print('No rooms available. Add a room first.', speed=0.01)
                continue

            show_menu_screen('Select Room', 'Choose the new room for this machine.')
            room_choice = system.choose_room()
            if room_choice is None:
                continue

            ok, message = system.update_machine_field(machine, 'room', room_choice.roomID, actor_role=current_user.role)
        elif choice == '4':
            return
        else:
            type_print('Invalid option please try again.', speed=0.01)
            continue

        type_print(message, speed=0.01)


def view_machine_details_menu(system, current_user):
    show_menu_screen('Machine Details', 'Select a machine to view.')
    machine = system.viewMachineList()
    if machine is None:
        return

    if userInputConfirm('Would you like to update this machine?'):
        update_machine_fields_menu(system, current_user, machine)


#========================= Top-Level Menus =========================


def mainMenu(system, current_user):
    while True:
        show_menu_screen(f'Welcome, {current_user.username} ({current_user.role})', 'Main Menu')
        type_print("""
1. Machines
2. Parts
3. Reports
4. Rooms
5. Categories
6. Users
7. Change password
8. Logout
9. Exit
""", speed = 0.01)
        userInput = input(">: ")
        if userInput.strip() == '1':
            machineMenu(system, current_user)
        elif userInput.strip() == '2':
            partsMenu(system, current_user)
        elif userInput.strip() == '3':
            reportMenu(system, current_user)
        elif userInput.strip() == '4':
            roomMenu(system, current_user)
        elif userInput.strip() == '5':
            categoriesMenu(system, current_user)
        elif userInput.strip() == '6':
            user_accounts_menu(system, current_user)
        elif userInput.strip() == '7':
            old_password = getpass('Current password: ').strip()
            new_password = prompt_new_password()
            ok, message = system.change_password(current_user.username, old_password, new_password)
            type_print(message, speed=0.01)
            if ok:
                current_user = system.users[current_user.username]
        elif userInput.strip() == '8':
            return 'logout'
        elif userInput.strip() == '9':
            type_print('Goodbye', 0.08)
            time.sleep(1.5)
            return 'exit'
        else:
            type_print("Invalid operation please try again", speed = 0.035)

def partsMenu(system, current_user):
    """Menu for managing parts in the inventory system."""
    typeSpeed = 0.01

    while True:
        show_menu_screen('Parts Menu', 'Part actions.')
        print("""
1. View parts
2. Add part
3. Remove part
4. Update stock
5. View machines using a part
6. Edit part details
7. Back to Main Menu
""")
        
        userInput = input(">: ")
        if userInput.strip() == '1':
            view_part_details_menu(system, current_user)
        elif userInput.strip() == '2':
            if not require_access(current_user, {ADMIN, MANAGER}):
                continue
            type_print('Add Part', typeSpeed)
            system.addPart(actor_role=current_user.role)
        elif userInput.strip() == '3':
            if not require_access(current_user, {ADMIN, MANAGER}):
                continue
            type_print('Remove Part', typeSpeed)
            system.removePart(actor_role=current_user.role)
        elif userInput.strip() == '4':
            if not require_access(current_user, {ADMIN, TECHNICIAN}):
                continue
            update_part_stock_menu(system, current_user)
        elif userInput.strip() == '5':
            view_part_machine_usage_menu(system)
        elif userInput.strip() == '6':
            edit_part_details_menu(system, current_user)
        elif userInput.strip() == '7':
            return
        else:
            type_print('Invalid operation please try again', typeSpeed)

def machineMenu(system, current_user):
    """Menu for managing machines in the inventory system."""
    typeSpeed = .01

    while True:
        show_menu_screen('Machine Menu', 'Machine actions.')
        print("""
1. View machines
2. Add machine
3. Remove machine
4. Install part (operational)
5. Baseline load machine parts (admin)
6. Remove installed part
7. Back to Main Menu
""")
        
        userInput = input(">: ")

        if userInput.strip() == '1':
            view_machine_details_menu(system, current_user)
        elif userInput.strip() == '2': 
            if not require_access(current_user, {ADMIN, MANAGER}):
                continue
            type_print('Add Machine', typeSpeed)
            system.addMachine(actor_role=current_user.role)
        elif userInput.strip() == '3':
            if not require_access(current_user, {ADMIN, MANAGER}):
                continue
            type_print('Remove Machine', typeSpeed)
            system.removeMachine(actor_role=current_user.role)
        elif userInput.strip() == '4':
            if not require_access(current_user, {ADMIN, TECHNICIAN}):
                continue
            operational_install_part_menu(system, current_user)
        elif userInput.strip() == '5':
            baseline_load_machine_parts_menu(system, current_user)
        elif userInput.strip() == '6':
            if not require_access(current_user, {ADMIN, TECHNICIAN}):
                continue
            remove_installed_part_menu(system, current_user)
        elif userInput.strip() == '7':
            return
        else:
            type_print('Invalid operation please try again', typeSpeed)


def reportMenu(system, current_user):
    if not require_access(current_user, {ADMIN, MANAGER}):
        return

    show_menu_screen('Report Logs', 'Recent activity.')
    logs = system.get_recent_logs(100, actor_role=current_user.role)
    if not logs:
        print('No logs available.')
    else:
        for line in logs:
            print(line)
    pause_for_user()


#========================= Room/Category/User Menus =========================


def roomMenu(system, current_user):
    while True:
        show_menu_screen('Room Menu', 'Room actions.')
        print("""
1. View rooms
2. Add room
3. Remove room
4. Update room
5. Back to Main Menu
""")
        userInput = input(">: ")

        if userInput.strip() == '1':
            print_header('View Rooms')
            system.viewRoomList()
        elif userInput.strip() == '2':
            if not require_access(current_user, {ADMIN}):
                continue
            print_header('Add Room')
            system.addRoom(actor_role=current_user.role)
        elif userInput.strip() == '3':
            if not require_access(current_user, {ADMIN}):
                continue
            print_header('Remove Room')
            roomChoice = system.choose_room()
            if roomChoice is None:
                type_print('No room selected. Returning to room menu.')
                continue
            else:
                system.removeRoom(roomChoice.roomID, actor_role=current_user.role)
        elif userInput.strip() == '4':
            if not require_access(current_user, {ADMIN}):
                continue
            roomChoice = system.choose_room()
            if roomChoice is None:
                type_print('No room selected. Returning to room menu.')
                continue
            update_room_menu(system, current_user, roomChoice)
        elif userInput.strip() == '5':
            return
        
        else:
            type_print("Invalid operation please try again")    


def update_room_menu(system, current_user, roomChoice):
    while True:
        show_menu_screen(f'Update Room: {roomChoice.roomName}', 'Room actions.')
        print("""
1. Rename room
2. Edit description
3. View machines in room
4. Return to room menu
""")

        userInput = input('>: ').strip()
        if userInput == '1':
            new_name = mandateStrInput('Enter new room name')
            if new_name == 'QUIT':
                continue
            roomChoice.updateName(new_name)
            system.saveData(system.file_path)
            type_print(f'Room name updated to: {new_name}', speed=0.01)
        elif userInput == '2':
            new_description = optionalStrInput('Enter new room description')
            if new_description == 'quit':
                continue
            roomChoice.roomDescription = new_description
            system.saveData(system.file_path)
            type_print('Room description updated.', speed=0.01)
        elif userInput == '3':
            print(system.getRoomMachineList(roomChoice.roomID))
            pause_for_user()
        elif userInput == '4':
            return
        else:
            type_print('Invalid option please try again', speed=0.01)


def categoriesMenu(system, current_user):
    while True:
        show_menu_screen('Categories Menu', 'Category actions.')
        print("""
1. View categories
2. Add category
3. Remove category
4. Back to Main Menu
""")
        userInput = input('>: ')
        if userInput.strip() == '1':
            system.display_categories()
        elif userInput.strip() == '2':
            if not require_access(current_user, {ADMIN}):
                continue
            type_print('Add Category', 0.01)
            system.addCategory(actor_role=current_user.role)
        elif userInput.strip() == '3':
            if not require_access(current_user, {ADMIN}):
                continue
            categoryChoice = system.choose_category()
            if categoryChoice is not None:
                system.removeCategory(categoryChoice.categoryID, actor_role=current_user.role)
        elif userInput.strip() == '4':
            return
        else:
            type_print('Invalid operation please try again', speed=0.01)


def user_accounts_menu(system, current_user):
    if not require_access(current_user, {ADMIN}):
        return

    while True:
        show_menu_screen('User Accounts', 'Admin account tools.')
        print("""
    1. List users
    2. Add user
    3. Remove user
    4. Reset password
    5. Change role
6. Back to Main Menu
""")

        userInput = input('>: ').strip()
        if userInput == '1':
            users = system.list_users()
            rows = [[u.username, u.role, str(u.must_change_password)] for u in users]
            print_table(['Username', 'Role', 'Must Change Password'], rows)
            pause_for_user()
        elif userInput == '2':
            username = input('New username: ').strip()
            role = input('Role (admin/manager/technician/viewer): ').strip().lower()
            password = prompt_new_password()
            ok, message = system.add_user(
                username,
                password,
                role,
                must_change_password=False,
                actor_role=current_user.role,
            )
            type_print(message, speed=0.01)
        elif userInput == '3':
            username = input('Username to remove: ').strip()
            ok, message = system.remove_user(username, actor_role=current_user.role)
            type_print(message, speed=0.01)
        elif userInput == '4':
            username = input('Username to reset password: ').strip()
            new_password = prompt_new_password()
            ok, message = system.reset_password(
                username,
                new_password,
                must_change_password=True,
                actor_role=current_user.role,
            )
            type_print(message, speed=0.01)
        elif userInput == '5':
            username = input('Username to update role: ').strip()
            role = input('New role (admin/manager/technician/viewer): ').strip().lower()
            ok, message = system.set_user_role(username, role, actor_role=current_user.role)
            type_print(message, speed=0.01)
        elif userInput == '6':
            return
        else:
            type_print('Invalid option.', speed=0.01)


#=========================  Main Program Execution=========================

system = inventorySystem()
system.loadData()  # Load data from the JSON file when the program starts
while True:
    current_user = login_menu(system)
    result = mainMenu(system, current_user)
    if result == 'exit':
        break