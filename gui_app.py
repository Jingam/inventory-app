import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from inventorySys import inventorySystem
from models import Machine, Parts, Room, categories


class LoginFrame(ttk.Frame):
    def __init__(self, app):
        super().__init__(app, padding=20)
        self.app = app

        ttk.Label(self, text="Inventory Manager", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 16), sticky="w"
        )

        ttk.Label(self, text="Username").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=4)

        self.login_btn = ttk.Button(self, text="Login", command=self._submit)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=(14, 0), sticky="ew")

        self.columnconfigure(1, weight=1)
        self.username_entry.focus_set()

        self.username_entry.bind("<Return>", self._on_enter)
        self.password_entry.bind("<Return>", self._on_enter)

    def _on_enter(self, _event):
        if self.winfo_ismapped():
            self._submit()

    def _submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Login", "Username and password are required.")
            return
        self.app.attempt_login(username, password)


class MainMenuFrame(ttk.Frame):
    def __init__(self, app, account):
        super().__init__(app, padding=16)
        self.app = app
        self.system = app.system
        self.account = account

        title_text = f"Welcome, {account.username} ({account.role})"
        ttk.Label(self, text=title_text, font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self._build_role_aware_buttons()
        self._build_dynamic_top_menus()

    def _build_role_aware_buttons(self):
        for child in self.button_frame.winfo_children():
            child.destroy()

        button_specs = [
            ("Machines", self.open_machine_menu, self._can_see("manage_machines")),
            ("Parts", self.open_parts_menu, self._can_see("manage_parts")),
            ("Reports", self.open_reports, self.system.has_permission(self.account.role, "view_reports")),
            ("Debug Data", self.open_debug_window, True),
            ("Rooms", self.open_room_menu, True),
            ("Categories", self.open_category_menu, True),
            ("Users", self.open_users_menu, self.system.has_permission(self.account.role, "manage_users")),
            ("Change Password", self.change_password, True),
            ("Refresh Navigation", self._build_dynamic_top_menus, True),
            ("Logout", self.logout, True),
            ("Exit", self.app.exit_app, True),
        ]

        visible_specs = [spec for spec in button_specs if spec[2]]
        for idx, (label, callback, _visible) in enumerate(visible_specs):
            row = idx // 2
            col = idx % 2
            btn = ttk.Button(self.button_frame, text=label, command=callback)
            btn.grid(row=row, column=col, sticky="ew", padx=6, pady=6)

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

    def _can_see(self, privileged_action):
        if self.system.has_permission(self.account.role, privileged_action):
            return True

        # Non-privileged roles still get access to read-only section entry points.
        if privileged_action in {"manage_machines", "manage_parts"}:
            return True
        return False

    def _required_label(self, parent, text, row):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", padx=12, pady=4)
        tk.Label(parent, text="*", fg="red").grid(row=row, column=0, sticky="e", padx=(0, 4), pady=4)

    def _show_missing_required_fields(self, title, missing_fields, focus_widget=None):
        joined = "\n".join(f"- {field}" for field in missing_fields)
        messagebox.showerror(title, f"Please fill in required fields:\n\n{joined}")
        if focus_widget is not None:
            try:
                focus_widget.focus_set()
            except tk.TclError:
                pass

    def _get_room_name(self, room_id):
        room = self.system.roomList.get(room_id)
        if room is None:
            return room_id
        return room.roomName

    def _get_part_display_id(self, part_key, part):
        return part.partID or part_key

    def _open_action_list_window(self, title, items, label_fn, action_text, action_fn):
        window, created = self._open_or_focus_window(
            key=f"action:{title}",
            title=title,
            geometry="640x360",
        )
        if not created:
            return

        listbox = tk.Listbox(window)
        listbox.pack(fill="both", expand=True, padx=12, pady=12)

        keys = []
        for item in items:
            item_key, item_label = label_fn(item)
            keys.append(item_key)
            listbox.insert("end", item_label)

        def run_action():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror(title, "Please select an item first.")
                return
            selected_key = keys[selection[0]]
            if action_fn(selected_key):
                window.destroy()

        ttk.Button(window, text=action_text, command=run_action).pack(pady=(0, 12))

    def _build_dynamic_top_menus(self):
        menubar = tk.Menu(self.app)

        machine_menu = tk.Menu(menubar, tearoff=0)
        if self.system.machineList:
            for machine in self.system.machineList.values():
                machine_menu.add_command(
                    label=f"{machine.machineID} - {machine.machineName}",
                    command=lambda machine_id=machine.machineID: self.open_machine_editor(machine_id),
                )
        else:
            machine_menu.add_command(label="No machines", state="disabled")
        machine_menu.add_separator()
        if self.system.has_permission(self.account.role, "manage_machines"):
            machine_menu.add_command(label="Add New Machine...", command=self.open_add_machine_window)
        else:
            machine_menu.add_command(label="Add New Machine...", state="disabled")
        menubar.add_cascade(label="Machines", menu=machine_menu)

        room_menu = tk.Menu(menubar, tearoff=0)
        if self.system.roomList:
            for room in self.system.roomList.values():
                room_menu.add_command(
                    label=f"{room.roomID} - {room.roomName}",
                    command=lambda room_id=room.roomID: self.open_room_editor(room_id),
                )
        else:
            room_menu.add_command(label="No rooms", state="disabled")
        room_menu.add_separator()
        if self.system.has_permission(self.account.role, "manage_rooms"):
            room_menu.add_command(label="Add New Room...", command=self.open_add_room_window)
        else:
            room_menu.add_command(label="Add New Room...", state="disabled")
        menubar.add_cascade(label="Rooms", menu=room_menu)

        category_menu = tk.Menu(menubar, tearoff=0)
        if self.system.categoriesList:
            for category in self.system.categoriesList.values():
                category_menu.add_command(
                    label=f"{category.categoryID} - {category.categoryName}",
                    command=lambda category_id=category.categoryID: self.open_category_editor(category_id),
                )
        else:
            category_menu.add_command(label="No categories", state="disabled")
        category_menu.add_separator()
        if self.system.has_permission(self.account.role, "manage_categories"):
            category_menu.add_command(label="Add New Category...", command=self.open_add_category_window)
        else:
            category_menu.add_command(label="Add New Category...", state="disabled")
        menubar.add_cascade(label="Categories", menu=category_menu)

        self.app.config(menu=menubar)

    def _parse_geometry_size(self, geometry):
        try:
            size_segment = str(geometry).split("+", 1)[0]
            width_text, height_text = size_segment.lower().split("x", 1)
            width = int(width_text)
            height = int(height_text)
            if width <= 0 or height <= 0:
                return 0, 0
            return width, height
        except (ValueError, AttributeError):
            return 0, 0

    def _autosize_and_center_window(
        self,
        window,
        min_width=0,
        min_height=0,
        preferred_width_ratio=None,
        preferred_height_ratio=None,
    ):
        if window is None or not window.winfo_exists():
            return

        try:
            window.update_idletasks()
        except tk.TclError:
            return

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        requested_width = window.winfo_reqwidth()
        requested_height = window.winfo_reqheight()

        width = max(min_width, requested_width)
        height = max(min_height, requested_height)

        if preferred_width_ratio is not None:
            width = max(width, int(screen_width * preferred_width_ratio))
        if preferred_height_ratio is not None:
            height = max(height, int(screen_height * preferred_height_ratio))

        max_width = max(320, int(screen_width * 0.95))
        max_height = max(240, int(screen_height * 0.90))
        width = min(width, max_width)
        height = min(height, max_height)

        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _open_or_focus_window(
        self,
        key,
        title,
        geometry,
        parent_window=None,
        modal=False,
        preferred_width_ratio=None,
        preferred_height_ratio=None,
    ):
        existing = self.app.open_windows.get(key)
        if existing is not None and existing.winfo_exists():
            existing.deiconify()
            existing.lift()
            existing.focus_set()
            refresh_callback = self.app.window_refreshers.get(key)
            if refresh_callback is not None:
                refresh_callback()
            return existing, False

        window = tk.Toplevel(self.app)
        window.title(title)
        min_width, min_height = self._parse_geometry_size(geometry)
        if min_width > 0 and min_height > 0:
            window.minsize(min_width, min_height)
        window.geometry(geometry)

        if parent_window is None:
            focused_widget = self.app.focus_get()
            if focused_widget is not None:
                try:
                    parent_window = focused_widget.winfo_toplevel()
                except tk.TclError:
                    parent_window = None

        if parent_window is not None and parent_window is not window:
            try:
                window.transient(parent_window)
            except tk.TclError:
                pass

        if modal:
            try:
                window.grab_set()
            except tk.TclError:
                pass

        window.lift()
        self.app.open_windows[key] = window

        window.after_idle(
            lambda win=window, min_w=min_width, min_h=min_height, pref_w=preferred_width_ratio, pref_h=preferred_height_ratio: self._autosize_and_center_window(
                win,
                min_w,
                min_h,
                pref_w,
                pref_h,
            )
        )

        def _close_window():
            self.app.open_windows.pop(key, None)
            self.app.window_refreshers.pop(key, None)
            window.destroy()

        def _cleanup_window_refs(event):
            if event.widget is window:
                self.app.open_windows.pop(key, None)
                self.app.window_refreshers.pop(key, None)

        window.bind("<Destroy>", _cleanup_window_refs, add="+")
        window.protocol("WM_DELETE_WINDOW", _close_window)
        return window, True

    def _register_window_refresher(self, key, refresh_callback):
        self.app.window_refreshers[key] = refresh_callback

    def _refresh_registered_windows(self, *keys):
        for key in keys:
            window = self.app.open_windows.get(key)
            refresh_callback = self.app.window_refreshers.get(key)
            if window is None or not window.winfo_exists() or refresh_callback is None:
                continue
            refresh_callback()

    def _treeview_item_from_double_click(self, tree, event):
        region = tree.identify("region", event.x, event.y)
        if region not in {"tree", "cell"}:
            return None

        item_id = tree.identify_row(event.y)
        if not item_id:
            return None

        tree.selection_set(item_id)
        tree.focus(item_id)
        return item_id

    def _listbox_index_from_double_click(self, listbox, event):
        index = listbox.nearest(event.y)
        if index < 0:
            return None

        bbox = listbox.bbox(index)
        if not bbox:
            return None

        x, y, width, height = bbox
        if not (x <= event.x <= x + width and y <= event.y <= y + height):
            return None

        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        return index

    def _known_manufacturers(self):
        return sorted(
            {
                (part.manufacturer or "").strip()
                for part in self.system.partsList.values()
                if (part.manufacturer or "").strip()
            },
            key=str.upper,
        )

    def _open_manufacturer_picker(self, parent_window, manufacturer_var, target_entry=None):
        manufacturers = self._known_manufacturers()
        if not manufacturers:
            messagebox.showinfo("Parts", "No previously used manufacturers found yet.")
            return

        picker_window, created_picker = self._open_or_focus_window(
            key="picker:Manufacturer",
            title="Choose Manufacturer",
            geometry="360x260",
            parent_window=parent_window,
            modal=True,
        )
        if not created_picker:
            return

        ttk.Label(picker_window, text="Select a manufacturer").pack(anchor="w", padx=12, pady=(12, 6))
        listbox = tk.Listbox(picker_window, height=9)
        listbox.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        for name in manufacturers:
            listbox.insert("end", name)

        def apply_selection(_event=None):
            selection = listbox.curselection()
            if not selection:
                return

            manufacturer_var.set(manufacturers[selection[0]])
            if target_entry is not None:
                target_entry.focus_set()
            picker_window.destroy()

        listbox.bind("<Double-Button-1>", apply_selection)
        ttk.Button(picker_window, text="Use Selected", command=apply_selection).pack(padx=12, pady=(0, 12), fill="x")

    def _coerce_sort_value(self, value, numeric=False):
        if value is None:
            return float("-inf") if numeric else ""

        text = str(value).strip()
        if numeric:
            try:
                return float(text)
            except ValueError:
                return float("-inf")
        return text.lower()

    def _make_treeview_sortable(self, tree, numeric_columns=None):
        numeric_columns = set(numeric_columns or [])
        sort_state = {"column": None, "descending": False}

        def _sort_by_column(column_id):
            descending = False
            if sort_state["column"] == column_id:
                descending = not sort_state["descending"]

            children = tree.get_children("")
            row_data = []
            for item in children:
                value = tree.set(item, column_id)
                row_data.append((self._coerce_sort_value(value, numeric=(column_id in numeric_columns)), item))

            row_data.sort(key=lambda row: row[0], reverse=descending)
            for index, (_value, item) in enumerate(row_data):
                tree.move(item, "", index)

            sort_state["column"] = column_id
            sort_state["descending"] = descending

        for column_id in tree["columns"]:
            tree.heading(column_id, command=lambda cid=column_id: _sort_by_column(cid))

    def open_baseline_load_machine_part_window(self, machine_id, refresh_callback=None):
        if not self.system.has_permission(self.account.role, "baseline_machine_build"):
            messagebox.showerror("Machines", "Access denied: only admin can perform baseline machine load.")
            return

        machine = self.system.machineList.get(machine_id)
        if machine is None:
            messagebox.showerror("Machines", "Machine not found.")
            return

        if not self.system.partsList:
            messagebox.showerror("Machines", "No parts available. Create a part first.")
            return

        window, created = self._open_or_focus_window(
            key=f"form:BaselineLoad:{machine_id}",
            title=f"Baseline Load Part - {machine.machineID}",
            geometry="620x250",
        )
        if not created:
            return

        ttk.Label(window, text=f"Machine: {machine.machineID} - {machine.machineName}").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 8)
        )

        ttk.Label(window, text="Part").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        part_pairs = []
        for part in sorted(self.system.partsList.values(), key=lambda item: item.partName.upper()):
            label = f"{part.partID} | {part.modelNumber} | {part.partName}"
            part_pairs.append((label, part.partID))
        part_var = tk.StringVar(value=(part_pairs[0][0] if part_pairs else ""))
        part_box = ttk.Combobox(window, textvariable=part_var, values=[label for label, _ in part_pairs], state="readonly")
        part_box.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Quantity").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(window, textvariable=qty_var, width=16)
        qty_entry.grid(row=2, column=1, sticky="w", padx=12, pady=4)

        def submit_baseline_load():
            selected_label = part_var.get().strip()
            part_id = next((pid for label, pid in part_pairs if label == selected_label), None)
            if part_id is None:
                messagebox.showerror("Machines", "Please select a valid part.")
                part_box.focus_set()
                return

            try:
                quantity = int(qty_var.get().strip())
            except ValueError:
                messagebox.showerror("Machines", "Quantity must be a valid integer.")
                qty_entry.focus_set()
                return

            part = self.system.partsList.get(part_id)
            if part is None:
                messagebox.showerror("Machines", "Selected part was not found.")
                return

            ok, message = self.system.baseline_load_machine_part(
                machine,
                part,
                quantity,
                actor_role=self.account.role,
            )
            if ok:
                messagebox.showinfo("Machines", message)
                if refresh_callback is not None:
                    refresh_callback(machine.machineID)
                window.destroy()
            else:
                messagebox.showerror("Machines", message)

        ttk.Button(window, text="Baseline Load", command=submit_baseline_load).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 12)
        )
        window.columnconfigure(1, weight=1)

    def open_install_machine_part_window(self, machine_id, refresh_callback=None):
        if not self.system.has_permission(self.account.role, "install_parts"):
            messagebox.showerror("Machines", "Access denied: only technician or admin can install parts.")
            return

        machine = self.system.machineList.get(machine_id)
        if machine is None:
            messagebox.showerror("Machines", "Machine not found.")
            return

        available_parts = [
            part
            for part in self.system.partsList.values()
            if part.stock.get("new", 0) > 0 or part.stock.get("used", 0) > 0
        ]
        if not available_parts:
            messagebox.showerror("Machines", "No inventory parts are available to install.")
            return

        window, created = self._open_or_focus_window(
            key=f"form:InstallPart:{machine_id}",
            title=f"Install Part - {machine.machineID}",
            geometry="680x300",
        )
        if not created:
            return

        ttk.Label(window, text=f"Machine: {machine.machineID} - {machine.machineName}").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 8)
        )

        ttk.Label(window, text="Part").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        part_pairs = []
        for part in sorted(available_parts, key=lambda item: item.partName.upper()):
            label = (
                f"{part.partID} | {part.modelNumber} | {part.partName} "
                f"(new {part.stock.get('new', 0)}, used {part.stock.get('used', 0)})"
            )
            part_pairs.append((label, part.partID))
        part_var = tk.StringVar(value=(part_pairs[0][0] if part_pairs else ""))
        part_box = ttk.Combobox(window, textvariable=part_var, values=[label for label, _ in part_pairs], state="readonly")
        part_box.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Source Stock").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        bucket_var = tk.StringVar(value="new")
        bucket_box = ttk.Combobox(window, textvariable=bucket_var, values=("new", "used"), state="readonly")
        bucket_box.grid(row=2, column=1, sticky="w", padx=12, pady=4)

        ttk.Label(window, text="Quantity").grid(row=3, column=0, sticky="w", padx=12, pady=4)
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(window, textvariable=qty_var, width=16)
        qty_entry.grid(row=3, column=1, sticky="w", padx=12, pady=4)

        availability_label = ttk.Label(window, text="")
        availability_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=12, pady=(4, 0))

        def update_availability(_event=None):
            selected_label = part_var.get().strip()
            part_id = next((pid for label, pid in part_pairs if label == selected_label), None)
            part = self.system.partsList.get(part_id) if part_id else None
            if part is None:
                availability_label.configure(text="")
                return
            bucket = bucket_var.get().strip().lower() or "new"
            availability_label.configure(text=f"Available in {bucket}: {part.stock.get(bucket, 0)}")

        part_box.bind("<<ComboboxSelected>>", update_availability)
        bucket_box.bind("<<ComboboxSelected>>", update_availability)
        update_availability()

        def submit_install():
            selected_label = part_var.get().strip()
            part_id = next((pid for label, pid in part_pairs if label == selected_label), None)
            if part_id is None:
                messagebox.showerror("Machines", "Please select a valid part.")
                part_box.focus_set()
                return

            try:
                quantity = int(qty_var.get().strip())
            except ValueError:
                messagebox.showerror("Machines", "Quantity must be a valid integer.")
                qty_entry.focus_set()
                return

            part = self.system.partsList.get(part_id)
            if part is None:
                messagebox.showerror("Machines", "Selected part was not found.")
                return

            ok, message = self.system.install_part_to_machine_from_bucket(
                machine,
                part,
                quantity,
                source_bucket=bucket_var.get(),
                actor_role=self.account.role,
            )
            if ok:
                messagebox.showinfo("Machines", message)
                if refresh_callback is not None:
                    refresh_callback(machine.machineID)
                window.destroy()
            else:
                messagebox.showerror("Machines", message)
                update_availability()

        ttk.Button(window, text="Install Part", command=submit_install).grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 12)
        )
        window.columnconfigure(1, weight=1)

    def open_add_machine_window(self, default_room_name=None, on_created=None):
        if not self.system.has_permission(self.account.role, "manage_machines"):
            messagebox.showerror("Machines", "Access denied: only manager or admin can add machines.")
            return

        if not self.system.roomList:
            messagebox.showerror("Machines", "No rooms available. Add a room first.")
            return

        window, created = self._open_or_focus_window(
            key="form:AddMachine",
            title="Add New Machine",
            geometry="520x230",
            modal=True,
        )
        if not created:
            return

        self._required_label(window, "Name", 0)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(window, textvariable=name_var, width=36)
        name_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

        ttk.Label(window, text="Description").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(window, textvariable=desc_var, width=36)
        desc_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Room", 2)
        room_names = sorted([room.roomName for room in self.system.roomList.values()])
        initial_room_name = default_room_name if default_room_name in room_names else (room_names[0] if room_names else "")
        room_var = tk.StringVar(value=initial_room_name)
        room_box = ttk.Combobox(
            window,
            textvariable=room_var,
            values=room_names,
            state="readonly",
        )
        room_box.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        def add_machine():
            machine_name = name_var.get().strip()
            room_name = room_var.get().strip()

            missing = []
            if not machine_name:
                missing.append("Name")
            if not room_name:
                missing.append("Room")
            if missing:
                focus_widget = name_entry if "Name" in missing else room_box
                self._show_missing_required_fields("Machines", missing, focus_widget)
                return

            existing_machine = self.system.getMachineByName(machine_name)
            if existing_machine is not None:
                messagebox.showerror("Machines", f"Machine with name {machine_name} already exists.")
                return

            room_obj = self.system.getRoomByName(room_name)
            if room_obj is None:
                messagebox.showerror("Machines", "Selected room was not found.")
                room_box.focus_set()
                return

            machine_id = self.system.assignMachineKey()
            self.system.machineList[machine_id] = Machine(
                machineID=machine_id,
                machineName=machine_name,
                machineDescription=desc_var.get().strip(),
                machineLocation=room_obj.roomID,
            )
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Machines", "menu:Rooms")
            if on_created is not None:
                on_created(self.system.machineList[machine_id])
            messagebox.showinfo("Machines", f"Machine {machine_name} added.")
            window.destroy()

        ttk.Button(window, text="Add Machine", command=add_machine).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 12)
        )

        window.columnconfigure(1, weight=1)
        name_entry.focus_set()

    def open_delete_machine_window(self):
        if not self.system.has_permission(self.account.role, "manage_machines"):
            messagebox.showerror("Machines", "Access denied: only manager or admin can remove machines.")
            return

        machines = list(self.system.machineList.values())
        if not machines:
            messagebox.showerror("Machines", "No machines available to delete.")
            return

        def delete_machine(machine_id):
            machine = self.system.machineList.get(machine_id)
            if machine is None:
                messagebox.showerror("Machines", "Machine not found.")
                return False

            if not messagebox.askyesno("Delete Machine", f"Delete {machine.machineID} - {machine.machineName}?"):
                return False

            for part_id, quantity in machine.part_contained_ID.items():
                part = self.system.partsList.get(part_id)
                if part is not None:
                    part.stock["installed"] = max(0, part.stock.get("installed", 0) - quantity)
                    part.stock["new"] = part.stock.get("new", 0) + quantity
                    part.machineID.pop(machine.machineID, None)

            self.system.machineList.pop(machine.machineID, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Machines", "menu:Rooms", "menu:Parts")
            messagebox.showinfo("Machines", f"Machine {machine.machineName} removed.")
            return True

        self._open_action_list_window(
            "Delete Machine",
            machines,
            lambda m: (m.machineID, f"{m.machineID} | {m.machineName} | room {self._get_room_name(m.machineLocation)}"),
            "Delete Selected",
            delete_machine,
        )

    def open_add_room_window(self):
        if not self.system.has_permission(self.account.role, "manage_rooms"):
            messagebox.showerror("Rooms", "Access denied: only admin can add rooms.")
            return

        window, created = self._open_or_focus_window(
            key="form:AddRoom",
            title="Add New Room",
            geometry="520x190",
            modal=True,
        )
        if not created:
            return

        self._required_label(window, "Name", 0)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(window, textvariable=name_var, width=36)
        name_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

        ttk.Label(window, text="Description").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar()
        ttk.Entry(window, textvariable=desc_var, width=36).grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        def add_room():
            room_name = name_var.get().strip()
            if not room_name:
                self._show_missing_required_fields("Rooms", ["Name"], name_entry)
                return

            existing_room = self.system.getRoomByName(room_name)
            if existing_room is not None:
                messagebox.showerror("Rooms", f"Room with name {room_name} already exists.")
                return

            room_id = self.system.assignRoomKey()
            self.system.roomList[room_id] = Room(
                roomID=room_id,
                roomName=room_name,
                roomDescription=desc_var.get().strip(),
            )
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Rooms", "menu:Machines")
            messagebox.showinfo("Rooms", f"Room {room_name} added.")
            window.destroy()

        ttk.Button(window, text="Add Room", command=add_room).grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 12)
        )

        window.columnconfigure(1, weight=1)
        name_entry.focus_set()

    def open_delete_room_window(self):
        if not self.system.has_permission(self.account.role, "manage_rooms"):
            messagebox.showerror("Rooms", "Access denied: only admin can remove rooms.")
            return

        rooms = list(self.system.roomList.values())
        if not rooms:
            messagebox.showerror("Rooms", "No rooms available to delete.")
            return

        def delete_room(room_id):
            room = self.system.roomList.get(room_id)
            if room is None:
                messagebox.showerror("Rooms", "Room not found.")
                return False

            if not messagebox.askyesno("Delete Room", f"Delete {room.roomID} - {room.roomName}?"):
                return False

            for machine in self.system.machineList.values():
                if machine.machineLocation == room_id:
                    messagebox.showerror("Rooms", "Room cannot be removed while machines are assigned to it.")
                    return False

            self.system.roomList.pop(room_id, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Rooms", "menu:Machines")
            messagebox.showinfo("Rooms", f"Room {room.roomName} removed.")
            return True

        self._open_action_list_window(
            "Delete Room",
            rooms,
            lambda r: (r.roomID, f"{r.roomID} | {r.roomName}"),
            "Delete Selected",
            delete_room,
        )

    def open_add_category_window(self, on_created=None):
        if not self.system.has_permission(self.account.role, "manage_categories"):
            messagebox.showerror("Categories", "Access denied: only admin can add categories.")
            return

        window, created = self._open_or_focus_window(
            key="form:AddCategory",
            title="Add New Category",
            geometry="560x240",
            modal=True,
        )
        if not created:
            if on_created is not None:
                callbacks = getattr(window, "_on_created_callbacks", [])
                callbacks.append(on_created)
                window._on_created_callbacks = callbacks
            return

        callbacks = []
        if on_created is not None:
            callbacks.append(on_created)
        window._on_created_callbacks = callbacks

        self._required_label(window, "Name", 0)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(window, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

        ttk.Label(window, text="Description").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar()
        ttk.Entry(window, textvariable=desc_var, width=40).grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Specs (comma separated)").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        specs_var = tk.StringVar()
        ttk.Entry(window, textvariable=specs_var, width=40).grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        def add_category():
            category_name = name_var.get().strip()
            if not category_name:
                self._show_missing_required_fields("Categories", ["Name"], name_entry)
                return

            existing_category = self.system.getCategoryByName(category_name)
            if existing_category is not None:
                messagebox.showerror("Categories", f"Category with name {category_name} already exists.")
                return

            category_id = self.system.assignCategoryKey()
            raw_specs = specs_var.get().strip()
            specs = [item.strip() for item in raw_specs.split(",") if item.strip()] if raw_specs else []

            self.system.categoriesList[category_id] = categories(
                categoryID=category_id,
                categoryName=category_name,
                categoryDescription=desc_var.get().strip(),
                specList=specs,
            )
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Categories", "menu:Parts")
            for callback in getattr(window, "_on_created_callbacks", []):
                callback(self.system.categoriesList[category_id])
            messagebox.showinfo("Categories", f"Category {category_name} added.")
            window.destroy()

        ttk.Button(window, text="Add Category", command=add_category).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 12)
        )

        window.columnconfigure(1, weight=1)
        name_entry.focus_set()

    def open_delete_category_window(self):
        if not self.system.has_permission(self.account.role, "manage_categories"):
            messagebox.showerror("Categories", "Access denied: only admin can remove categories.")
            return

        categories_items = list(self.system.categoriesList.values())
        if not categories_items:
            messagebox.showerror("Categories", "No categories available to delete.")
            return

        def delete_category(category_id):
            category_item = self.system.categoriesList.get(category_id)
            if category_item is None:
                messagebox.showerror("Categories", "Category not found.")
                return False

            if not messagebox.askyesno(
                "Delete Category",
                f"Delete {category_item.categoryID} - {category_item.categoryName}?\nParts in this category will be unassigned.",
            ):
                return False

            for part in self.system.partsList.values():
                if str(part.category).strip().upper() == category_id.strip().upper():
                    part.category = ""

            self.system.categoriesList.pop(category_id, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Categories", "menu:Parts", "menu:Machines")
            messagebox.showinfo("Categories", f"Category {category_item.categoryName} removed.")
            return True

        self._open_action_list_window(
            "Delete Category",
            categories_items,
            lambda c: (c.categoryID, f"{c.categoryID} | {c.categoryName}"),
            "Delete Selected",
            delete_category,
        )

    def open_delete_part_window(self):
        if not self.system.has_permission(self.account.role, "manage_parts"):
            messagebox.showerror("Parts", "Access denied: only manager or admin can remove parts.")
            return

        parts_items = list(self.system.partsList.values())
        if not parts_items:
            messagebox.showerror("Parts", "No parts available to delete.")
            return

        def delete_part(part_id):
            part = self.system.partsList.get(part_id)
            if part is None:
                messagebox.showerror("Parts", "Part not found.")
                return False

            installed_qty = part.stock.get("installed", 0)
            if installed_qty > 0:
                messagebox.showerror(
                    "Parts",
                    "Part cannot be removed while quantity is installed on machines.",
                )
                return False

            if not messagebox.askyesno("Delete Part", f"Delete {part.partID} - {part.modelNumber}?"):
                return False

            self.system.partsList.pop(part_id, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Parts", "menu:Categories", "menu:Machines")
            messagebox.showinfo("Parts", f"Part {part.modelNumber} removed.")
            return True

        self._open_action_list_window(
            "Delete Part",
            parts_items,
            lambda p: (p.partID, f"{p.partID} | {p.modelNumber} | total {p.total_quantity()}"),
            "Delete Selected",
            delete_part,
        )

    def _open_list_window(self, title, items, label_fn, open_fn):
        window, created = self._open_or_focus_window(
            key=f"list:{title}",
            title=title,
            geometry="640x360",
        )
        if not created:
            return

        listbox = tk.Listbox(window)
        listbox.pack(fill="both", expand=True, padx=12, pady=12)

        keys = []
        for item in items:
            item_key, item_label = label_fn(item)
            keys.append(item_key)
            listbox.insert("end", item_label)

        def open_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror(title, "Please select an item first.")
                return
            selected_key = keys[selection[0]]
            open_fn(selected_key)

        def open_selected_double_click(event):
            index = self._listbox_index_from_double_click(listbox, event)
            if index is None:
                return
            open_fn(keys[index])

        listbox.bind("<Double-Button-1>", open_selected_double_click)
        ttk.Button(window, text="Open Selected", command=open_selected).pack(pady=(0, 12))

    def open_machine_menu(self):
        window, created = self._open_or_focus_window(
            key="menu:Machines",
            title="Machines",
            geometry="1040x600",
            preferred_width_ratio=0.90,
            preferred_height_ratio=0.82,
        )
        if not created:
            return

        can_manage = self.system.has_permission(self.account.role, "manage_machines")

        top_bar = ttk.Frame(window)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(
            top_bar,
            text="Add New Machine",
            command=self.open_add_machine_window,
            state=("normal" if can_manage else "disabled"),
        ).pack(side="left")
        ttk.Button(
            top_bar,
            text="Delete Machine",
            command=self.open_delete_machine_window,
            state=("normal" if can_manage else "disabled"),
        ).pack(side="left", padx=(8, 0))

        ttk.Label(window, text="Machines").pack(anchor="w", padx=12)

        tree = ttk.Treeview(window, columns=("id", "name", "room"), show="headings", height=10)
        tree.heading("id", text="Machine ID")
        tree.heading("name", text="Name")
        tree.heading("room", text="Room")
        tree.column("id", width=100, minwidth=85, stretch=False, anchor="w")
        tree.column("name", width=280, minwidth=180, stretch=False, anchor="w")
        tree.column("room", width=560, minwidth=220, stretch=True, anchor="w")
        tree.pack(fill="x", expand=False, padx=12, pady=(6, 12))
        self._make_treeview_sortable(tree)

        def refresh_machine_list():
            current_selection = tree.selection()
            selected_machine_id = current_selection[0] if current_selection else None
            for child in tree.get_children():
                tree.delete(child)
            for machine in self.system.machineList.values():
                tree.insert(
                    "",
                    "end",
                    iid=machine.machineID,
                    values=(machine.machineID, machine.machineName, self._get_room_name(machine.machineLocation)),
                )
            if selected_machine_id and tree.exists(selected_machine_id):
                tree.selection_set(selected_machine_id)
                refresh_machine_parts(selected_machine_id)
            else:
                children = tree.get_children()
                if children:
                    tree.selection_set(children[0])
                    refresh_machine_parts(children[0])
                else:
                    refresh_machine_parts()

        def refresh_machine_parts(machine_id=None):
            for child in parts_tree.get_children():
                parts_tree.delete(child)

            if not machine_id:
                parts_status.configure(text="Select a machine to view installed parts.")
                return

            machine = self.system.machineList.get(machine_id)
            if machine is None:
                parts_status.configure(text="Machine not found.")
                return

            contained_parts = []
            for part_id, quantity in machine.part_contained_ID.items():
                part = self.system.partsList.get(part_id)
                if part is not None:
                    contained_parts.append((part, quantity))

            contained_parts.sort(key=lambda item: item[0].partName.upper())

            if not contained_parts:
                parts_status.configure(text="No parts installed in this machine.")
                return

            parts_status.configure(text=f"{len(contained_parts)} part type(s) installed.")
            for part, quantity in contained_parts:
                category_name = ""
                category = self.system.categoriesList.get(part.category)
                if category is not None:
                    category_name = category.categoryName
                display_part_id = self._get_part_display_id(part.partID, part)
                parts_tree.insert(
                    "",
                    "end",
                    iid=part.partID or display_part_id,
                    values=(
                        display_part_id,
                        part.modelNumber,
                        part.partName,
                        part.manufacturer,
                        category_name,
                        (part.partDescription or "").strip(),
                        quantity,
                    ),
                )

        def get_selected_machine_id(show_error=False):
            selected = tree.selection()
            if not selected:
                if show_error:
                    messagebox.showerror("Machines", "Please select a machine first.")
                return None
            return selected[0]

        def open_selected_machine(_event=None):
            machine_id = get_selected_machine_id()
            if machine_id is None:
                return
            self.open_machine_editor(machine_id)

        def open_selected_machine_double_click(event):
            item_id = self._treeview_item_from_double_click(tree, event)
            if item_id is None:
                return
            self.open_machine_editor(item_id)

        def open_selected_machine_part(_event=None):
            selected = parts_tree.selection()
            if not selected:
                messagebox.showerror("Parts", "Please select a part first.")
                return
            self.open_part_editor(selected[0])

        def open_selected_machine_part_double_click(event):
            item_id = self._treeview_item_from_double_click(parts_tree, event)
            if item_id is None:
                return
            self.open_part_editor(item_id)

        def open_baseline_load_for_selected_machine():
            machine_id = get_selected_machine_id(show_error=True)
            if machine_id is None:
                return
            self.open_baseline_load_machine_part_window(machine_id, refresh_machine_parts)

        def open_install_for_selected_machine():
            machine_id = get_selected_machine_id(show_error=True)
            if machine_id is None:
                return
            self.open_install_machine_part_window(machine_id, refresh_machine_parts)

        def on_machine_selection(_event=None):
            machine_id = get_selected_machine_id()
            refresh_machine_parts(machine_id)

        parts_frame = ttk.LabelFrame(window, text="Parts Installed In Selected Machine", padding=8)
        parts_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        parts_tree = ttk.Treeview(
            parts_frame,
            columns=("id", "model", "name", "manufacturer", "category", "description", "qty"),
            show="headings",
            height=8,
        )
        parts_tree.heading("id", text="Part ID")
        parts_tree.heading("model", text="Model")
        parts_tree.heading("name", text="Name")
        parts_tree.heading("manufacturer", text="Manufacturer")
        parts_tree.heading("category", text="Category")
        parts_tree.heading("description", text="Description")
        parts_tree.heading("qty", text="Installed Qty")
        parts_tree.column("id", width=100, minwidth=85, stretch=False, anchor="w")
        parts_tree.column("model", width=160, minwidth=120, stretch=False, anchor="w")
        parts_tree.column("name", width=220, minwidth=160, stretch=False, anchor="w")
        parts_tree.column("manufacturer", width=160, minwidth=130, stretch=False, anchor="w")
        parts_tree.column("category", width=150, minwidth=120, stretch=False, anchor="w")
        parts_tree.column("description", width=300, minwidth=180, stretch=True, anchor="w")
        parts_tree.column("qty", width=110, minwidth=90, stretch=False, anchor="center")
        parts_tree.pack(fill="both", expand=True)
        self._make_treeview_sortable(parts_tree, numeric_columns={"qty"})

        parts_status = ttk.Label(parts_frame, text="Select a machine to view installed parts.")
        parts_status.pack(anchor="w", pady=(8, 0))

        parts_actions = ttk.Frame(parts_frame)
        parts_actions.pack(fill="x", pady=(8, 0))

        ttk.Button(parts_actions, text="Edit Selected Part", command=open_selected_machine_part).pack(side="right")
        ttk.Button(
            parts_actions,
            text="Install From Inventory",
            command=open_install_for_selected_machine,
            state=("normal" if self.system.has_permission(self.account.role, "install_parts") else "disabled"),
        ).pack(side="right", padx=(0, 8))
        ttk.Button(
            parts_actions,
            text="Baseline Load Part",
            command=open_baseline_load_for_selected_machine,
            state=("normal" if self.system.has_permission(self.account.role, "baseline_machine_build") else "disabled"),
        ).pack(side="right", padx=(0, 8))

        tree.bind("<<TreeviewSelect>>", on_machine_selection)
        tree.bind("<Double-Button-1>", open_selected_machine_double_click)
        ttk.Button(window, text="Open Selected", command=open_selected_machine).pack(pady=(0, 12))
        parts_tree.bind("<Double-Button-1>", open_selected_machine_part_double_click)
        self._register_window_refresher("menu:Machines", refresh_machine_list)
        refresh_machine_list()

    def open_room_menu(self):
        window, created = self._open_or_focus_window(
            key="menu:Rooms",
            title="Rooms",
            geometry="980x560",
            preferred_width_ratio=0.86,
            preferred_height_ratio=0.80,
        )
        if not created:
            return

        can_manage = self.system.has_permission(self.account.role, "manage_rooms")

        top_bar = ttk.Frame(window)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(
            top_bar,
            text="Add New Room",
            command=self.open_add_room_window,
            state=("normal" if can_manage else "disabled"),
        ).pack(side="left")
        ttk.Button(
            top_bar,
            text="Delete Room",
            command=self.open_delete_room_window,
            state=("normal" if can_manage else "disabled"),
        ).pack(side="left", padx=(8, 0))

        ttk.Label(window, text="Rooms").pack(anchor="w", padx=12)

        tree = ttk.Treeview(window, columns=("id", "name", "description"), show="headings", height=10)
        tree.heading("id", text="Room ID")
        tree.heading("name", text="Name")
        tree.heading("description", text="Description")
        tree.column("id", width=90, minwidth=75, stretch=False, anchor="w")
        tree.column("name", width=220, minwidth=180, stretch=False, anchor="w")
        tree.column("description", width=560, minwidth=320, stretch=True, anchor="w")
        tree.pack(fill="x", expand=False, padx=12, pady=(6, 12))
        self._make_treeview_sortable(tree)

        def refresh_room_list():
            current_selection = tree.selection()
            selected_room_id = current_selection[0] if current_selection else None
            for child in tree.get_children():
                tree.delete(child)
            for room in self.system.roomList.values():
                description = (room.roomDescription or "").strip()
                tree.insert("", "end", iid=room.roomID, values=(room.roomID, room.roomName, description))
            if selected_room_id and tree.exists(selected_room_id):
                tree.selection_set(selected_room_id)
                refresh_room_machines(selected_room_id)
            else:
                children = tree.get_children()
                if children:
                    tree.selection_set(children[0])
                    refresh_room_machines(children[0])
                else:
                    refresh_room_machines()

        machines_frame = ttk.LabelFrame(window, text="Machines In Selected Room", padding=8)
        machines_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        machines_tree = ttk.Treeview(machines_frame, columns=("id", "name"), show="headings", height=8)
        machines_tree.heading("id", text="Machine ID")
        machines_tree.heading("name", text="Machine Name")
        machines_tree.column("id", width=110, minwidth=90, stretch=False, anchor="w")
        machines_tree.column("name", width=620, minwidth=280, stretch=True, anchor="w")
        machines_tree.pack(fill="both", expand=True)
        self._make_treeview_sortable(machines_tree)

        empty_label = ttk.Label(
            machines_frame,
            text="Select a room to view assigned machines.",
        )
        empty_label.pack(anchor="w", pady=(8, 0))

        def refresh_room_machines(room_id=None):
            for child in machines_tree.get_children():
                machines_tree.delete(child)

            if not room_id:
                empty_label.configure(text="Select a room to view assigned machines.")
                return

            machines = [
                machine
                for machine in self.system.machineList.values()
                if machine.machineLocation == room_id
            ]
            machines.sort(key=lambda machine: machine.machineName.upper())

            if not machines:
                empty_label.configure(text="No machines assigned to this room.")
                return

            empty_label.configure(text=f"{len(machines)} machine(s) assigned.")
            for machine in machines:
                machines_tree.insert("", "end", iid=machine.machineID, values=(machine.machineID, machine.machineName))

        def get_selected_room_id(show_error=False):
            selected = tree.selection()
            if not selected:
                if show_error:
                    messagebox.showerror("Rooms", "Please select a room first.")
                return None
            return selected[0]

        def open_add_machine_for_selected_room():
            room_id = get_selected_room_id(show_error=True)
            if room_id is None:
                return
            room = self.system.roomList.get(room_id)
            if room is None:
                messagebox.showerror("Rooms", "Selected room was not found.")
                return

            def on_machine_created(_machine):
                refresh_room_machines(room_id)

            self.open_add_machine_window(default_room_name=room.roomName, on_created=on_machine_created)

        def open_selected_room_machine(_event=None):
            selected = machines_tree.selection()
            if not selected:
                messagebox.showerror("Machines", "Please select a machine first.")
                return
            self.open_machine_editor(selected[0])

        def open_selected_room_machine_double_click(event):
            item_id = self._treeview_item_from_double_click(machines_tree, event)
            if item_id is None:
                return
            self.open_machine_editor(item_id)

        def open_selected_room(_event=None):
            selected = tree.selection()
            if not selected:
                return
            self.open_room_editor(selected[0])

        def open_selected_room_double_click(event):
            item_id = self._treeview_item_from_double_click(tree, event)
            if item_id is None:
                return
            self.open_room_editor(item_id)

        def on_room_selection(_event=None):
            selected = tree.selection()
            if not selected:
                refresh_room_machines()
                return
            refresh_room_machines(selected[0])

        tree.bind("<<TreeviewSelect>>", on_room_selection)
        tree.bind("<Double-Button-1>", open_selected_room_double_click)
        ttk.Button(window, text="Open Selected", command=open_selected_room).pack(pady=(0, 12))
        machines_actions = ttk.Frame(machines_frame)
        machines_actions.pack(fill="x", pady=(8, 0))
        ttk.Button(
            machines_actions,
            text="Add New Machine",
            command=open_add_machine_for_selected_room,
            state=("normal" if self.system.has_permission(self.account.role, "manage_machines") else "disabled"),
        ).pack(side="right")
        ttk.Button(machines_actions, text="Edit Selected Machine", command=open_selected_room_machine).pack(side="right", padx=(0, 8))
        machines_tree.bind("<Double-Button-1>", open_selected_room_machine_double_click)
        self._register_window_refresher("menu:Rooms", refresh_room_list)
        refresh_room_list()

    def open_category_menu(self):
        window, created = self._open_or_focus_window(
            key="menu:Categories",
            title="Categories",
            geometry="1040x680",
            preferred_width_ratio=0.90,
            preferred_height_ratio=0.88,
        )
        if not created:
            return

        can_manage = self.system.has_permission(self.account.role, "manage_categories")

        top_bar = ttk.Frame(window)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(
            top_bar,
            text="Add New Category",
            command=self.open_add_category_window,
            state=("normal" if can_manage else "disabled"),
        ).pack(side="left")
        ttk.Button(
            top_bar,
            text="Delete Category",
            command=self.open_delete_category_window,
            state=("normal" if can_manage else "disabled"),
        ).pack(side="left", padx=(8, 0))

        ttk.Label(window, text="Categories").pack(anchor="w", padx=12)

        tree = ttk.Treeview(window, columns=("id", "name", "description"), show="headings", height=10)
        tree.heading("id", text="Category ID")
        tree.heading("name", text="Name")
        tree.heading("description", text="Description")
        tree.column("id", width=100, minwidth=85, stretch=False, anchor="w")
        tree.column("name", width=240, minwidth=180, stretch=False, anchor="w")
        tree.column("description", width=540, minwidth=320, stretch=True, anchor="w")
        tree.pack(fill="x", expand=False, padx=12, pady=(6, 12))
        self._make_treeview_sortable(tree)

        def refresh_category_list():
            current_selection = tree.selection()
            selected_category_id = current_selection[0] if current_selection else None
            for child in tree.get_children():
                tree.delete(child)
            for category in self.system.categoriesList.values():
                tree.insert(
                    "",
                    "end",
                    iid=category.categoryID,
                    values=(
                        category.categoryID,
                        category.categoryName,
                        (category.categoryDescription or "").strip(),
                    ),
                )
            if selected_category_id and tree.exists(selected_category_id):
                tree.selection_set(selected_category_id)
                refresh_category_specs(selected_category_id)
                refresh_category_parts(selected_category_id)
            else:
                children = tree.get_children()
                if children:
                    tree.selection_set(children[0])
                    refresh_category_specs(children[0])
                    refresh_category_parts(children[0])
                else:
                    refresh_category_specs()
                    refresh_category_parts()

        specs_frame = ttk.LabelFrame(window, text="Spec Fields For Selected Category", padding=8)
        specs_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        specs_tree = ttk.Treeview(specs_frame, columns=("spec",), show="headings", height=8)
        specs_tree.heading("spec", text="Spec Field")
        specs_tree.column("spec", width=760, minwidth=240, stretch=True, anchor="w")
        specs_tree.pack(fill="both", expand=True)
        self._make_treeview_sortable(specs_tree)

        empty_label = ttk.Label(specs_frame, text="Select a category to view spec fields.")
        empty_label.pack(anchor="w", pady=(8, 0))

        def refresh_category_specs(category_id=None):
            for child in specs_tree.get_children():
                specs_tree.delete(child)

            if not category_id:
                empty_label.configure(text="Select a category to view spec fields.")
                return

            category = self.system.categoriesList.get(category_id)
            if category is None:
                empty_label.configure(text="Category not found.")
                return

            spec_fields = [str(item).strip() for item in (category.specList or []) if str(item).strip()]
            if not spec_fields:
                empty_label.configure(text="No spec fields defined for this category.")
                return

            empty_label.configure(text=f"{len(spec_fields)} spec field(s) defined.")
            for spec in spec_fields:
                specs_tree.insert("", "end", values=(spec,))

        parts_frame = ttk.LabelFrame(window, text="Parts In Selected Category", padding=8)
        parts_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        parts_tree = ttk.Treeview(parts_frame, columns=("id", "model", "name", "total"), show="headings", height=8)
        parts_tree.heading("id", text="Part ID")
        parts_tree.heading("model", text="Model")
        parts_tree.heading("name", text="Name")
        parts_tree.heading("total", text="Total Qty")
        parts_tree.column("id", width=100, minwidth=85, stretch=False, anchor="w")
        parts_tree.column("model", width=150, minwidth=120, stretch=False, anchor="w")
        parts_tree.column("name", width=560, minwidth=240, stretch=True, anchor="w")
        parts_tree.column("total", width=100, minwidth=85, stretch=False, anchor="center")
        parts_tree.pack(fill="both", expand=True)
        self._make_treeview_sortable(parts_tree, numeric_columns={"total"})

        parts_status = ttk.Label(parts_frame, text="Select a category to view related parts.")
        parts_status.pack(anchor="w", pady=(8, 0))

        def refresh_category_parts(category_id=None):
            for child in parts_tree.get_children():
                parts_tree.delete(child)

            if not category_id:
                parts_status.configure(text="Select a category to view related parts.")
                return

            related_parts = [
                (part_key, part)
                for part_key, part in self.system.partsList.items()
                if str(part.category).strip().upper() == category_id.strip().upper()
            ]
            related_parts.sort(key=lambda item: item[1].partName.upper())

            if not related_parts:
                parts_status.configure(text="No parts assigned to this category.")
                return

            parts_status.configure(text=f"{len(related_parts)} part(s) assigned.")
            for part_key, part in related_parts:
                display_part_id = self._get_part_display_id(part_key, part)
                parts_tree.insert(
                    "",
                    "end",
                    iid=part_key,
                    values=(display_part_id, part.modelNumber, part.partName, part.total_quantity()),
                )

        def open_selected_category(_event=None):
            selected = tree.selection()
            if not selected:
                return
            self.open_category_editor(selected[0])

        def open_selected_category_double_click(event):
            item_id = self._treeview_item_from_double_click(tree, event)
            if item_id is None:
                return
            self.open_category_editor(item_id)

        def on_category_selection(_event=None):
            selected = tree.selection()
            if not selected:
                refresh_category_specs()
                refresh_category_parts()
                return
            refresh_category_specs(selected[0])
            refresh_category_parts(selected[0])

        def open_selected_category_part(_event=None):
            selected = parts_tree.selection()
            if not selected:
                return
            self.open_part_editor(selected[0])

        def open_selected_category_part_double_click(event):
            item_id = self._treeview_item_from_double_click(parts_tree, event)
            if item_id is None:
                return
            self.open_part_editor(item_id)

        tree.bind("<<TreeviewSelect>>", on_category_selection)
        tree.bind("<Double-Button-1>", open_selected_category_double_click)
        ttk.Button(window, text="Open Selected", command=open_selected_category).pack(pady=(0, 12))
        ttk.Button(parts_frame, text="Edit Selected Part", command=open_selected_category_part).pack(anchor="e", pady=(8, 0))
        parts_tree.bind("<Double-Button-1>", open_selected_category_part_double_click)
        self._register_window_refresher("menu:Categories", refresh_category_list)
        refresh_category_list()

    def open_parts_menu(self):
        window, created = self._open_or_focus_window(
            key="menu:Parts",
            title="Parts",
            geometry="1100x620",
            preferred_width_ratio=0.92,
            preferred_height_ratio=0.90,
        )
        if not created:
            return

        can_manage_parts = self.system.has_permission(self.account.role, "manage_parts")

        top_bar = ttk.Frame(window)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(
            top_bar,
            text="Add New Part",
            command=self.open_add_part_window,
            state=("normal" if can_manage_parts else "disabled"),
        ).pack(side="left")
        ttk.Button(
            top_bar,
            text="Delete Part",
            command=self.open_delete_part_window,
            state=("normal" if can_manage_parts else "disabled"),
        ).pack(side="left", padx=(8, 0))

        search_var = tk.StringVar()
        search_frame = ttk.Frame(top_bar)
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="Search").pack(side="left", padx=(0, 6))
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=28)
        search_entry.pack(side="left")

        ttk.Label(window, text="Parts").pack(anchor="w", padx=12)

        tree = ttk.Treeview(
            window,
            columns=("id", "model", "name", "category", "new", "installed", "used", "total"),
            show="headings",
            height=10,
        )
        tree.heading("id", text="Part ID")
        tree.heading("model", text="Model")
        tree.heading("name", text="Name")
        tree.heading("category", text="Category")
        tree.heading("new", text="New")
        tree.heading("installed", text="Installed")
        tree.heading("used", text="Used")
        tree.heading("total", text="Total")
        tree.column("id", width=90, minwidth=80, stretch=False, anchor="w")
        tree.column("model", width=140, minwidth=120, stretch=False, anchor="w")
        tree.column("name", width=240, minwidth=180, stretch=True, anchor="w")
        tree.column("category", width=170, minwidth=140, stretch=False, anchor="w")
        tree.column("new", width=70, minwidth=60, stretch=False, anchor="center")
        tree.column("installed", width=90, minwidth=80, stretch=False, anchor="center")
        tree.column("used", width=70, minwidth=60, stretch=False, anchor="center")
        tree.column("total", width=70, minwidth=60, stretch=False, anchor="center")
        tree.pack(fill="x", expand=False, padx=12, pady=(6, 12))
        self._make_treeview_sortable(tree, numeric_columns={"new", "installed", "used", "total"})

        list_status_label = ttk.Label(window, text="")
        list_status_label.pack(anchor="w", padx=12, pady=(0, 8))

        def _part_matches_keyword(part_key, part, keyword):
            if not keyword:
                return True

            category_name = ""
            category = self.system.categoriesList.get(part.category)
            if category is not None:
                category_name = category.categoryName

            specs = part.specs if isinstance(part.specs, dict) else {}
            spec_text = " ".join(f"{k} {v}" for k, v in specs.items())

            haystack = " ".join(
                [
                    str(part_key),
                    part.partID,
                    part.modelNumber,
                    part.partName,
                    part.partDescription,
                    part.manufacturer,
                    part.location,
                    part.notes,
                    str(part.category),
                    category_name,
                    spec_text,
                ]
            ).lower()

            return keyword in haystack

        def refresh_parts_list():
            keyword = search_var.get().strip().lower()
            current_selection = tree.selection()
            selected_part_id = current_selection[0] if current_selection else current_part_id["value"]
            for child in tree.get_children():
                tree.delete(child)

            visible_count = 0
            for part_key, part in self.system.partsList.items():
                if not _part_matches_keyword(part_key, part, keyword):
                    continue

                category_name = ""
                category = self.system.categoriesList.get(part.category)
                if category is not None:
                    category_name = category.categoryName
                display_part_id = self._get_part_display_id(part_key, part)
                tree.insert(
                    "",
                    "end",
                    iid=part_key,
                    values=(
                        display_part_id,
                        part.modelNumber,
                        part.partName,
                        category_name,
                        part.stock.get("new", 0),
                        part.stock.get("installed", 0),
                        part.stock.get("used", 0),
                        part.total_quantity(),
                    ),
                )
                visible_count += 1

            if keyword:
                list_status_label.configure(text=f"Showing {visible_count} matching part(s) for: {search_var.get().strip()}")
            else:
                list_status_label.configure(text=f"Showing {visible_count} part(s).")

            if selected_part_id and tree.exists(selected_part_id):
                tree.selection_set(selected_part_id)
                refresh_part_details(selected_part_id)
            else:
                children = tree.get_children()
                if children:
                    tree.selection_set(children[0])
                    refresh_part_details(children[0])
                else:
                    refresh_part_details()

        def run_search(_event=None):
            refresh_parts_list()

        def clear_search():
            search_var.set("")
            refresh_parts_list()

        ttk.Button(search_frame, text="Find", command=run_search).pack(side="left", padx=(6, 0))
        ttk.Button(search_frame, text="Clear", command=clear_search).pack(side="left", padx=(6, 0))
        search_entry.bind("<Return>", run_search)

        details_frame = ttk.LabelFrame(window, text="Selected Part Details", padding=8)
        details_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        summary_frame = ttk.Frame(details_frame)
        summary_frame.pack(fill="x", pady=(0, 10))

        summary_labels = {
            "description": ttk.Label(summary_frame, text="Description: "),
            "manufacturer": ttk.Label(summary_frame, text="Manufacturer: "),
            "location": ttk.Label(summary_frame, text="Location: "),
            "notes": ttk.Label(summary_frame, text="Notes: "),
        }
        for idx, key in enumerate(("description", "manufacturer", "location", "notes")):
            summary_labels[key].grid(row=idx, column=0, sticky="w", pady=2)

        specs_tree = ttk.Treeview(details_frame, columns=("field", "value"), show="headings", height=8)
        specs_tree.heading("field", text="Spec")
        specs_tree.heading("value", text="Value")
        specs_tree.column("field", width=220, minwidth=140, stretch=False, anchor="w")
        specs_tree.column("value", width=620, minwidth=220, stretch=True, anchor="w")
        specs_tree.pack(fill="both", expand=True)
        self._make_treeview_sortable(specs_tree)

        specs_status_label = ttk.Label(details_frame, text="Select a part to view details and specs.")
        specs_status_label.pack(anchor="w", pady=(8, 0))

        usage_frame = ttk.LabelFrame(details_frame, text="Machines Using Selected Part", padding=8)
        usage_frame.pack(fill="both", expand=True, pady=(10, 0))

        usage_tree = ttk.Treeview(
            usage_frame,
            columns=("machine_id", "machine_name", "location", "qty"),
            show="headings",
            height=7,
        )
        usage_tree.heading("machine_id", text="Machine ID")
        usage_tree.heading("machine_name", text="Machine Name")
        usage_tree.heading("location", text="Room")
        usage_tree.heading("qty", text="Installed Qty")
        usage_tree.column("machine_id", width=110, minwidth=90, stretch=False, anchor="w")
        usage_tree.column("machine_name", width=260, minwidth=180, stretch=False, anchor="w")
        usage_tree.column("location", width=260, minwidth=180, stretch=True, anchor="w")
        usage_tree.column("qty", width=120, minwidth=100, stretch=False, anchor="center")
        usage_tree.pack(fill="both", expand=True)
        self._make_treeview_sortable(usage_tree, numeric_columns={"qty"})

        usage_status_label = ttk.Label(usage_frame, text="Select a part to view where it is installed.")
        usage_status_label.pack(anchor="w", pady=(8, 0))

        usage_actions = ttk.Frame(usage_frame)
        usage_actions.pack(fill="x", pady=(8, 0))

        current_part_id = {"value": None}

        def refresh_part_details(part_id=None):
            for child in specs_tree.get_children():
                specs_tree.delete(child)
            for child in usage_tree.get_children():
                usage_tree.delete(child)

            if not part_id:
                current_part_id["value"] = None
                summary_labels["description"].configure(text="Description: ")
                summary_labels["manufacturer"].configure(text="Manufacturer: ")
                summary_labels["location"].configure(text="Location: ")
                summary_labels["notes"].configure(text="Notes: ")
                specs_status_label.configure(text="Select a part to view details and specs.")
                usage_status_label.configure(text="Select a part to view where it is installed.")
                return

            part = self.system.partsList.get(part_id)
            if part is None:
                current_part_id["value"] = None
                specs_status_label.configure(text="Part not found.")
                usage_status_label.configure(text="Part not found.")
                return

            current_part_id["value"] = part_id

            summary_labels["description"].configure(text=f"Description: {(part.partDescription or '').strip()}")
            summary_labels["manufacturer"].configure(text=f"Manufacturer: {(part.manufacturer or '').strip()}")
            summary_labels["location"].configure(text=f"Location: {(part.location or '').strip()}")
            summary_labels["notes"].configure(text=f"Notes: {(part.notes or '').strip()}")

            specs = part.specs or {}
            if not specs:
                specs_status_label.configure(text="No spec values recorded for this part.")
            else:
                specs_status_label.configure(text=f"{len(specs)} spec value(s) recorded.")
                for field, value in sorted(specs.items()):
                    specs_tree.insert("", "end", values=(field, value))

            machines_using_part = self.system.get_machines_by_part(part_id)
            machines_using_part.sort(key=lambda item: item[0].machineName.upper())

            if not machines_using_part:
                usage_status_label.configure(text="This part is not installed on any machine.")
                return

            usage_status_label.configure(text=f"Installed on {len(machines_using_part)} machine(s).")
            for machine, quantity in machines_using_part:
                usage_tree.insert(
                    "",
                    "end",
                    iid=machine.machineID,
                    values=(
                        machine.machineID,
                        machine.machineName,
                        self._get_room_name(machine.machineLocation),
                        quantity,
                    ),
                )

        def open_selected_part(_event=None):
            selected = tree.selection()
            part_id = selected[0] if selected else current_part_id["value"]
            if not part_id:
                messagebox.showerror("Parts", "Please select a part first.")
                return
            self.open_part_editor(part_id)

        def open_selected_part_double_click(event):
            item_id = self._treeview_item_from_double_click(tree, event)
            if item_id is None:
                return
            self.open_part_editor(item_id)

        def open_selected_usage_machine(_event=None):
            selected = usage_tree.selection()
            if not selected:
                messagebox.showerror("Machines", "Please select a machine first.")
                return
            self.open_machine_editor(selected[0])

        def open_selected_usage_machine_double_click(event):
            item_id = self._treeview_item_from_double_click(usage_tree, event)
            if item_id is None:
                return
            self.open_machine_editor(item_id)

        def on_part_selection(_event=None):
            selected = tree.selection()
            if not selected:
                refresh_part_details()
                return
            refresh_part_details(selected[0])

        tree.bind("<<TreeviewSelect>>", on_part_selection)
        tree.bind("<Double-Button-1>", open_selected_part_double_click)
        ttk.Button(window, text="Edit Selected Part", command=open_selected_part).pack(pady=(0, 12))
        ttk.Button(usage_actions, text="Open Selected Machine", command=open_selected_usage_machine).pack(side="right")
        usage_tree.bind("<Double-Button-1>", open_selected_usage_machine_double_click)
        self._register_window_refresher("menu:Parts", refresh_parts_list)
        refresh_parts_list()

    def open_add_part_window(self):
        if not self.system.has_permission(self.account.role, "manage_parts"):
            messagebox.showerror("Parts", "Access denied: only manager or admin can add parts.")
            return

        if not self.system.categoriesList:
            messagebox.showerror("Parts", "No categories available. Add a category first.")
            return

        window, created = self._open_or_focus_window(
            key="form:AddPart",
            title="Add New Part",
            geometry="760x520",
            modal=True,
        )
        if not created:
            return

        self._required_label(window, "Model", 0)
        model_var = tk.StringVar()
        model_entry = ttk.Entry(window, textvariable=model_var, width=42)
        model_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

        self._required_label(window, "Name", 1)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(window, textvariable=name_var, width=42)
        name_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Description").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar()
        ttk.Entry(window, textvariable=desc_var, width=42).grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Manufacturer", 3)
        manufacturer_var = tk.StringVar()
        manufacturer_frame = ttk.Frame(window)
        manufacturer_frame.grid(row=3, column=1, sticky="ew", padx=12, pady=4)
        manufacturer_entry = ttk.Entry(manufacturer_frame, textvariable=manufacturer_var, width=36)
        manufacturer_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            manufacturer_frame,
            text="...",
            width=3,
            command=lambda: self._open_manufacturer_picker(window, manufacturer_var, manufacturer_entry),
        ).pack(side="left", padx=(6, 0))

        ttk.Label(window, text="Quantity (new stock)").grid(row=4, column=0, sticky="w", padx=12, pady=4)
        qty_var = tk.StringVar(value="0")
        ttk.Entry(window, textvariable=qty_var, width=42).grid(row=4, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Location").grid(row=5, column=0, sticky="w", padx=12, pady=4)
        location_var = tk.StringVar()
        ttk.Entry(window, textvariable=location_var, width=42).grid(row=5, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Notes").grid(row=6, column=0, sticky="w", padx=12, pady=4)
        notes_var = tk.StringVar()
        ttk.Entry(window, textvariable=notes_var, width=42).grid(row=6, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Category", 7)
        category_pairs = [(cat.categoryID, cat.categoryName) for cat in self.system.categoriesList.values()]
        category_display = [cat_name for _cat_id, cat_name in category_pairs]
        category_var = tk.StringVar(value=category_display[0])
        category_box = ttk.Combobox(window, textvariable=category_var, values=category_display, state="readonly")
        category_box.grid(
            row=7, column=1, sticky="ew", padx=12, pady=4
        )
        ttk.Button(
            window,
            text="Add Category...",
            command=lambda: self.open_add_category_window(on_created=refresh_categories),
        ).grid(row=7, column=2, sticky="w", padx=(0, 12), pady=4)

        ttk.Label(window, text="Category Specs").grid(row=8, column=0, sticky="nw", padx=12, pady=4)
        specs_frame = ttk.Frame(window)
        specs_frame.grid(row=8, column=1, columnspan=2, sticky="ew", padx=12, pady=4)
        specs_entries = {}

        def render_spec_fields(preserved_values=None):
            preserved_values = preserved_values or {}
            for child in specs_frame.winfo_children():
                child.destroy()
            specs_entries.clear()

            selected_name = category_var.get().strip()
            selected_category = self.system.getCategoryByName(selected_name)
            if selected_category is None:
                ttk.Label(specs_frame, text="Select a valid category to enter specs.").grid(row=0, column=0, sticky="w")
                return

            spec_fields = selected_category.specList or []
            if not spec_fields:
                ttk.Label(specs_frame, text="No preset spec fields for this category.").grid(row=0, column=0, sticky="w")
                return

            for idx, field_name in enumerate(spec_fields):
                label = str(field_name).strip()
                if not label:
                    continue
                ttk.Label(specs_frame, text=label).grid(row=idx, column=0, sticky="w", padx=(0, 8), pady=2)
                entry_var = tk.StringVar(value=preserved_values.get(label, ""))
                entry = ttk.Entry(specs_frame, textvariable=entry_var, width=36)
                entry.grid(row=idx, column=1, sticky="ew", pady=2)
                specs_entries[label] = entry_var

            specs_frame.columnconfigure(1, weight=1)

        def refresh_categories(created_category=None):
            nonlocal category_pairs
            category_pairs = [(cat.categoryID, cat.categoryName) for cat in self.system.categoriesList.values()]
            category_names = [cat_name for _cat_id, cat_name in category_pairs]
            category_box.configure(values=category_names)
            if created_category is not None:
                category_var.set(created_category.categoryName)
            elif category_names and category_var.get().strip() not in category_names:
                category_var.set(category_names[0])
            render_spec_fields()

        def on_category_change(_event=None):
            existing_values = {field: var.get().strip() for field, var in specs_entries.items()}
            render_spec_fields(existing_values)

        category_box.bind("<<ComboboxSelected>>", on_category_change)
        render_spec_fields()

        def add_part():
            model = model_var.get().strip().upper()
            part_name = name_var.get().strip()
            manufacturer = manufacturer_var.get().strip()
            category_choice = category_var.get().strip()

            missing = []
            if not model:
                missing.append("Model")
            if not part_name:
                missing.append("Name")
            if not manufacturer:
                missing.append("Manufacturer")
            if not category_choice:
                missing.append("Category")
            if missing:
                focus_widget = model_entry
                if "Name" in missing:
                    focus_widget = name_entry
                elif "Manufacturer" in missing:
                    focus_widget = manufacturer_entry
                elif "Category" in missing:
                    focus_widget = category_box
                self._show_missing_required_fields("Parts", missing, focus_widget)
                return

            if self.system.getPartByModel(model) is not None:
                messagebox.showerror("Parts", f"Part model {model} already exists.")
                return

            try:
                quantity = int(qty_var.get().strip() or "0")
            except ValueError:
                messagebox.showerror("Parts", "Quantity must be a valid integer.")
                return

            if quantity < 0:
                quantity = 0

            category_obj = self.system.getCategoryByName(category_choice)
            if category_obj is None:
                messagebox.showerror("Parts", "Selected category is invalid.")
                category_box.focus_set()
                return
            category_id = category_obj.categoryID

            specs_dict = {
                field: value_var.get().strip()
                for field, value_var in specs_entries.items()
                if value_var.get().strip()
            }

            part_id = self.system.assignPartKey()
            self.system.partsList[part_id] = Parts(
                partID=part_id,
                partName=part_name,
                partDescription=desc_var.get().strip(),
                modelNumber=model,
                manufacturer=manufacturer,
                stock={"new": quantity, "used": 0, "installed": 0},
                location=location_var.get().strip(),
                notes=notes_var.get().strip(),
                category=category_id,
                specs=specs_dict,
            )
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Parts", "menu:Categories", "menu:Machines")
            messagebox.showinfo("Parts", f"Part {model} added.")
            window.destroy()

        ttk.Button(window, text="Add Part", command=add_part).grid(
            row=9, column=0, columnspan=3, sticky="ew", padx=12, pady=(12, 12)
        )

        window.columnconfigure(1, weight=1)
        window.columnconfigure(2, weight=0)
        manufacturer_frame.columnconfigure(0, weight=1)
        model_entry.focus_set()

    def open_part_editor(self, part_id):
        part = self.system.partsList.get(part_id)
        if part is None:
            messagebox.showerror("Parts", "Part not found.")
            return

        can_edit = self.system.has_permission(self.account.role, "manage_parts")

        window, created = self._open_or_focus_window(
            key=f"editor:Part:{part.partID}",
            title=f"Part {part.partID}",
            geometry="760x540",
        )
        if not created:
            return

        ttk.Label(window, text=f"Part ID: {part.partID}").grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(12, 4))

        self._required_label(window, "Model", 1)
        model_var = tk.StringVar(value=part.modelNumber)
        model_entry = ttk.Entry(window, textvariable=model_var, width=42)
        model_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Name", 2)
        name_var = tk.StringVar(value=part.partName)
        name_entry = ttk.Entry(window, textvariable=name_var, width=42)
        name_entry.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Description").grid(row=3, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar(value=part.partDescription)
        desc_entry = ttk.Entry(window, textvariable=desc_var, width=42)
        desc_entry.grid(row=3, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Manufacturer", 4)
        manufacturer_var = tk.StringVar(value=part.manufacturer)
        manufacturer_frame = ttk.Frame(window)
        manufacturer_frame.grid(row=4, column=1, sticky="ew", padx=12, pady=4)
        manufacturer_entry = ttk.Entry(manufacturer_frame, textvariable=manufacturer_var, width=36)
        manufacturer_entry.pack(side="left", fill="x", expand=True)
        manufacturer_picker_btn = ttk.Button(
            manufacturer_frame,
            text="...",
            width=3,
            command=lambda: self._open_manufacturer_picker(window, manufacturer_var, manufacturer_entry),
        )
        manufacturer_picker_btn.pack(side="left", padx=(6, 0))

        ttk.Label(window, text="Location").grid(row=5, column=0, sticky="w", padx=12, pady=4)
        location_var = tk.StringVar(value=part.location)
        location_entry = ttk.Entry(window, textvariable=location_var, width=42)
        location_entry.grid(row=5, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Notes").grid(row=6, column=0, sticky="w", padx=12, pady=4)
        notes_var = tk.StringVar(value=part.notes)
        notes_entry = ttk.Entry(window, textvariable=notes_var, width=42)
        notes_entry.grid(row=6, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Category", 7)
        category_names = [cat.categoryName for cat in self.system.categoriesList.values()]
        current_category_name = self.system.categoriesList.get(part.category).categoryName if part.category in self.system.categoriesList else ""
        category_var = tk.StringVar(value=current_category_name)
        category_box = ttk.Combobox(window, textvariable=category_var, values=category_names, state="readonly")
        category_box.grid(row=7, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Category Specs").grid(row=8, column=0, sticky="nw", padx=12, pady=4)
        specs_frame = ttk.Frame(window)
        specs_frame.grid(row=8, column=1, columnspan=2, sticky="ew", padx=12, pady=4)
        specs_entries = {}

        def render_spec_fields(preserved_values=None):
            preserved_values = preserved_values or {}
            for child in specs_frame.winfo_children():
                child.destroy()
            specs_entries.clear()

            selected_category = self.system.getCategoryByName(category_var.get().strip())
            if selected_category is None:
                ttk.Label(specs_frame, text="Select a valid category to edit specs.").grid(row=0, column=0, sticky="w")
                return

            fields = selected_category.specList or []
            if not fields:
                ttk.Label(specs_frame, text="No preset spec fields for this category.").grid(row=0, column=0, sticky="w")
                return

            for idx, field_name in enumerate(fields):
                key = str(field_name).strip()
                if not key:
                    continue
                ttk.Label(specs_frame, text=key).grid(row=idx, column=0, sticky="w", padx=(0, 8), pady=2)
                entry_var = tk.StringVar(value=preserved_values.get(key, ""))
                ttk.Entry(specs_frame, textvariable=entry_var, width=36).grid(row=idx, column=1, sticky="ew", pady=2)
                specs_entries[key] = entry_var

            specs_frame.columnconfigure(1, weight=1)

        def on_category_change(_event=None):
            existing_values = {field: var.get().strip() for field, var in specs_entries.items()}
            render_spec_fields(existing_values)

        category_box.bind("<<ComboboxSelected>>", on_category_change)
        render_spec_fields(part.specs or {})

        if not can_edit:
            model_entry.configure(state="disabled")
            name_entry.configure(state="disabled")
            desc_entry.configure(state="disabled")
            manufacturer_entry.configure(state="disabled")
            manufacturer_picker_btn.configure(state="disabled")
            location_entry.configure(state="disabled")
            notes_entry.configure(state="disabled")
            category_box.configure(state="disabled")
            for child in specs_frame.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.configure(state="disabled")

        def save_part():
            if not can_edit:
                return

            missing = []
            if not model_var.get().strip():
                missing.append("Model")
            if not name_var.get().strip():
                missing.append("Name")
            if not manufacturer_var.get().strip():
                missing.append("Manufacturer")
            if not category_var.get().strip():
                missing.append("Category")
            if missing:
                focus_widget = model_entry
                if "Name" in missing:
                    focus_widget = name_entry
                elif "Manufacturer" in missing:
                    focus_widget = manufacturer_entry
                elif "Category" in missing:
                    focus_widget = category_box
                self._show_missing_required_fields("Parts", missing, focus_widget)
                return

            selected_category = self.system.getCategoryByName(category_var.get().strip())
            if selected_category is None:
                messagebox.showerror("Parts", "Selected category is invalid.")
                category_box.focus_set()
                return

            proposed_model = model_var.get().strip().upper()
            existing_by_model = self.system.getPartByModel(proposed_model)
            if existing_by_model is not None and existing_by_model.partID != part.partID:
                messagebox.showerror("Parts", f"Part model {proposed_model} already exists.")
                model_entry.focus_set()
                return

            updates = [
                ("name", name_var.get().strip()),
                ("description", desc_var.get().strip()),
                ("model", proposed_model),
                ("manufacturer", manufacturer_var.get().strip()),
                ("location", location_var.get().strip()),
                ("notes", notes_var.get().strip()),
            ]

            for field_name, value in updates:
                ok, message = self.system.update_part_field(
                    part,
                    field_name,
                    value,
                    actor_role=self.account.role,
                    persist=False,
                    sync=False,
                )
                if not ok:
                    messagebox.showerror("Parts", message)
                    return

            updated_specs = {
                field: value_var.get().strip()
                for field, value_var in specs_entries.items()
                if value_var.get().strip()
            }
            ok, message = self.system.update_part_category_details(
                part,
                selected_category.categoryID,
                updated_specs,
                actor_role=self.account.role,
                persist=False,
            )
            if not ok:
                messagebox.showerror("Parts", message)
                return

            self.system.saveData(self.system.file_path)

            messagebox.showinfo("Parts", "Part updated successfully.")
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Parts", "menu:Categories", "menu:Machines")
            window.destroy()

        save_btn = ttk.Button(window, text="Save", command=save_part)
        save_btn.grid(row=9, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 12))
        if not can_edit:
            save_btn.configure(state="disabled")

        def delete_part_from_editor():
            if not can_edit:
                return

            installed_qty = part.stock.get("installed", 0)
            if installed_qty > 0:
                messagebox.showerror(
                    "Parts",
                    "Part cannot be removed while quantity is installed on machines.",
                )
                return

            if not messagebox.askyesno("Delete Part", f"Delete {part.partID} - {part.modelNumber}?"):
                return

            self.system.partsList.pop(part.partID, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Parts", "menu:Categories", "menu:Machines")
            messagebox.showinfo("Parts", f"Part {part.modelNumber} removed.")
            window.destroy()

        delete_btn = tk.Button(
            window,
            text="Delete",
            fg="red",
            activeforeground="red",
            command=delete_part_from_editor,
        )
        delete_btn.grid(row=9, column=2, sticky="ew", padx=12, pady=(12, 12))
        if not can_edit:
            delete_btn.configure(state="disabled")

        window.columnconfigure(1, weight=1)

    def open_reports(self):
        logs = self.system.get_recent_logs(100, actor_role=self.account.role)
        window, created = self._open_or_focus_window(
            key="menu:Reports",
            title="Reports",
            geometry="880x420",
            preferred_width_ratio=0.80,
            preferred_height_ratio=0.70,
        )
        if not created:
            return

        text = tk.Text(window, wrap="none")
        text.pack(fill="both", expand=True, padx=12, pady=12)

        if logs:
            text.insert("1.0", "\n".join(logs))
        else:
            text.insert("1.0", "No logs available.")
        text.configure(state="disabled")

    def open_debug_window(self):
        window, created = self._open_or_focus_window(
            key="menu:DebugData",
            title="Debug Data",
            geometry="1080x720",
            preferred_width_ratio=0.92,
            preferred_height_ratio=0.90,
        )
        if not created:
            return

        top_bar = ttk.Frame(window)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))

        text = tk.Text(window, wrap="none")
        text.pack(fill="both", expand=True, padx=12, pady=12)

        x_scroll = ttk.Scrollbar(window, orient="horizontal", command=text.xview)
        x_scroll.pack(fill="x", padx=12, pady=(0, 12))
        text.configure(xscrollcommand=x_scroll.set)

        def build_debug_snapshot():
            lines = []

            def add_section(title):
                lines.append(title)
                lines.append("-" * len(title))

            add_section("Counts")
            lines.append(f"parts: {len(self.system.partsList)}")
            lines.append(f"machines: {len(self.system.machineList)}")
            lines.append(f"rooms: {len(self.system.roomList)}")
            lines.append(f"categories: {len(self.system.categoriesList)}")
            lines.append(f"users: {len(self.system.users)}")
            lines.append("")

            add_section("Dictionary Keys")
            lines.append(f"part keys: {list(self.system.partsList.keys())}")
            lines.append(f"machine keys: {list(self.system.machineList.keys())}")
            lines.append(f"room keys: {list(self.system.roomList.keys())}")
            lines.append(f"category keys: {list(self.system.categoriesList.keys())}")
            lines.append("")

            add_section("Part Summary")
            if not self.system.partsList:
                lines.append("<no parts>")
            for key, part in self.system.partsList.items():
                category_name = ""
                category = self.system.categoriesList.get(part.category)
                if category is not None:
                    category_name = category.categoryName
                lines.append(
                    f"{key}: id={part.partID!r}, model={part.modelNumber!r}, name={part.partName!r}, "
                    f"category={part.category!r}, category_name={category_name!r}, "
                    f"stock={part.stock!r}, machine_links={part.machineID!r}"
                )
            lines.append("")

            add_section("Machine Summary")
            if not self.system.machineList:
                lines.append("<no machines>")
            for key, machine in self.system.machineList.items():
                room_name = self._get_room_name(machine.machineLocation)
                lines.append(
                    f"{key}: id={machine.machineID!r}, name={machine.machineName!r}, "
                    f"room={machine.machineLocation!r}/{room_name!r}, parts={machine.part_contained_ID!r}"
                )
            lines.append("")

            add_section("Room Summary")
            if not self.system.roomList:
                lines.append("<no rooms>")
            for key, room in self.system.roomList.items():
                contained = [
                    machine.machineID
                    for machine in self.system.machineList.values()
                    if machine.machineLocation == room.roomID
                ]
                lines.append(
                    f"{key}: id={room.roomID!r}, name={room.roomName!r}, description={room.roomDescription!r}, "
                    f"machines={contained!r}"
                )
            lines.append("")

            add_section("Category Summary")
            if not self.system.categoriesList:
                lines.append("<no categories>")
            for key, category in self.system.categoriesList.items():
                part_ids = [part.partID for part in self.system.get_parts_by_category(category.categoryID)]
                lines.append(
                    f"{key}: id={category.categoryID!r}, name={category.categoryName!r}, "
                    f"specs={category.specList!r}, parts={part_ids!r}"
                )
            lines.append("")

            add_section("Sanity Checks")
            duplicate_models = {}
            for part in self.system.partsList.values():
                duplicate_models.setdefault((part.modelNumber or "").strip().upper(), []).append(part.partID)
            duplicate_models = {model: ids for model, ids in duplicate_models.items() if model and len(ids) > 1}
            lines.append(f"duplicate part models: {duplicate_models if duplicate_models else '<none>'}")

            missing_room_refs = [
                (machine.machineID, machine.machineLocation)
                for machine in self.system.machineList.values()
                if machine.machineLocation not in self.system.roomList
            ]
            lines.append(f"machines with missing rooms: {missing_room_refs if missing_room_refs else '<none>'}")

            missing_category_refs = [
                (part.partID, part.category)
                for part in self.system.partsList.values()
                if part.category and part.category not in self.system.categoriesList
            ]
            lines.append(f"parts with missing categories: {missing_category_refs if missing_category_refs else '<none>'}")

            missing_part_refs = []
            for machine in self.system.machineList.values():
                for part_id in machine.part_contained_ID.keys():
                    if part_id not in self.system.partsList:
                        missing_part_refs.append((machine.machineID, part_id))
            lines.append(f"machines with missing part refs: {missing_part_refs if missing_part_refs else '<none>'}")

            return "\n".join(lines)

        def refresh_debug_window():
            text.configure(state="normal")
            text.delete("1.0", "end")
            text.insert("1.0", build_debug_snapshot())
            text.configure(state="disabled")

        ttk.Button(top_bar, text="Refresh", command=refresh_debug_window).pack(side="left")
        self._register_window_refresher("menu:DebugData", refresh_debug_window)
        refresh_debug_window()

    def open_users_menu(self):
        window, created = self._open_or_focus_window(
            key="menu:Users",
            title="Users",
            geometry="840x460",
        )
        if not created:
            return

        can_manage_users = self.system.has_permission(self.account.role, "manage_users")

        top_bar = ttk.Frame(window)
        top_bar.pack(fill="x", padx=12, pady=(12, 0))

        tree = ttk.Treeview(window, columns=("username", "role", "must_change"), show="headings")
        tree.heading("username", text="Username")
        tree.heading("role", text="Role")
        tree.heading("must_change", text="Must Change Password")
        tree.pack(fill="both", expand=True, padx=12, pady=12)
        self._make_treeview_sortable(tree)

        def refresh_users():
            for child in tree.get_children():
                tree.delete(child)
            for user in self.system.list_users():
                tree.insert(
                    "",
                    "end",
                    iid=user.username,
                    values=(user.username, user.role, str(user.must_change_password)),
                )

        def selected_username():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Users", "Please select a user first.")
                return None
            return tree.item(selected[0], "values")[0]

        def open_selected_user(_event=None):
            username = selected_username()
            if username is None:
                return
            self.open_user_editor(username, refresh_users)

        def add_user():
            dialog, created = self._open_or_focus_window(
                key="form:AddUser",
                title="Add User",
                geometry="460x260",
            )
            if not created:
                return

            ttk.Label(dialog, text="Username").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
            username_var = tk.StringVar()
            username_entry = ttk.Entry(dialog, textvariable=username_var, width=30)
            username_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

            ttk.Label(dialog, text="Temporary Password").grid(row=1, column=0, sticky="w", padx=12, pady=4)
            password_var = tk.StringVar()
            password_entry = ttk.Entry(dialog, textvariable=password_var, width=30, show="*")
            password_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

            ttk.Label(dialog, text="Role").grid(row=2, column=0, sticky="w", padx=12, pady=4)
            role_var = tk.StringVar(value="viewer")
            role_box = ttk.Combobox(
                dialog,
                textvariable=role_var,
                values=("admin", "manager", "technician", "viewer"),
                state="readonly",
            )
            role_box.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

            must_change_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                dialog,
                text="Require password change on next login",
                variable=must_change_var,
            ).grid(row=3, column=0, columnspan=2, sticky="w", padx=12, pady=6)

            def submit_add_user():
                username = username_var.get().strip()
                password = password_var.get()
                if not username:
                    messagebox.showerror("Add User", "Username cannot be empty.")
                    username_entry.focus_set()
                    return
                if not password:
                    messagebox.showerror("Add User", "Password cannot be empty.")
                    password_entry.focus_set()
                    return

                ok, message = self.system.add_user(
                    username=username,
                    password=password,
                    role=role_var.get(),
                    must_change_password=must_change_var.get(),
                    actor_role=self.account.role,
                )
                if ok:
                    messagebox.showinfo("Users", message)
                    refresh_users()
                    dialog.destroy()
                else:
                    messagebox.showerror("Users", message)

            ttk.Button(dialog, text="Create User", command=submit_add_user).grid(
                row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 12)
            )
            dialog.columnconfigure(1, weight=1)
            username_entry.focus_set()

        def remove_user():
            username = selected_username()
            if username is None:
                return
            if not messagebox.askyesno("Remove User", f"Remove user {username}?"):
                return

            ok, message = self.system.remove_user(username, actor_role=self.account.role)
            if ok:
                messagebox.showinfo("Users", message)
                refresh_users()
            else:
                messagebox.showerror("Users", message)

        def reset_password():
            username = selected_username()
            if username is None:
                return

            dialog, created = self._open_or_focus_window(
                key="form:ResetUserPassword",
                title="Reset Password",
                geometry="500x230",
            )
            if not created:
                return

            ttk.Label(dialog, text="Username").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
            username_var = tk.StringVar(value=username)
            username_entry = ttk.Entry(dialog, textvariable=username_var, width=32)
            username_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

            ttk.Label(dialog, text="New Password").grid(row=1, column=0, sticky="w", padx=12, pady=4)
            password_var = tk.StringVar()
            password_entry = ttk.Entry(dialog, textvariable=password_var, width=32, show="*")
            password_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

            must_change_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                dialog,
                text="Require user to change password at next login",
                variable=must_change_var,
            ).grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=6)

            def submit_reset_password():
                target_user = username_var.get().strip()
                new_password = password_var.get()
                if not target_user:
                    messagebox.showerror("Reset Password", "Username cannot be empty.")
                    username_entry.focus_set()
                    return
                if not new_password:
                    messagebox.showerror("Reset Password", "Password cannot be empty.")
                    password_entry.focus_set()
                    return

                ok, message = self.system.reset_password(
                    target_user,
                    new_password,
                    must_change_password=must_change_var.get(),
                    actor_role=self.account.role,
                )
                if ok:
                    messagebox.showinfo("Users", message)
                    refresh_users()
                    dialog.destroy()
                else:
                    messagebox.showerror("Users", message)

            ttk.Button(dialog, text="Reset Password", command=submit_reset_password).grid(
                row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 12)
            )
            dialog.columnconfigure(1, weight=1)
            password_entry.focus_set()

        def change_role():
            username = selected_username()
            if username is None:
                return

            dialog, created = self._open_or_focus_window(
                key="form:ChangeUserRole",
                title="Change User Role",
                geometry="470x210",
            )
            if not created:
                return

            ttk.Label(dialog, text="Username").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
            username_var = tk.StringVar(value=username)
            username_entry = ttk.Entry(dialog, textvariable=username_var, width=30)
            username_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=(12, 4))

            ttk.Label(dialog, text="Role").grid(row=1, column=0, sticky="w", padx=12, pady=4)
            role_var = tk.StringVar(value="viewer")
            role_box = ttk.Combobox(
                dialog,
                textvariable=role_var,
                values=("admin", "manager", "technician", "viewer"),
                state="readonly",
            )
            role_box.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

            def submit_change_role():
                target_user = username_var.get().strip()
                if not target_user:
                    messagebox.showerror("Change Role", "Username cannot be empty.")
                    username_entry.focus_set()
                    return

                ok, message = self.system.set_user_role(target_user, role_var.get(), actor_role=self.account.role)
                if ok:
                    messagebox.showinfo("Users", message)
                    refresh_users()
                    dialog.destroy()
                else:
                    messagebox.showerror("Users", message)

            ttk.Button(dialog, text="Update Role", command=submit_change_role).grid(
                row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 12)
            )
            dialog.columnconfigure(1, weight=1)
            role_box.focus_set()

        ttk.Button(
            top_bar,
            text="Add User",
            command=add_user,
            state=("normal" if can_manage_users else "disabled"),
        ).pack(side="left")
        ttk.Button(top_bar, text="Open Selected", command=open_selected_user).pack(side="left", padx=(8, 0))
        ttk.Button(top_bar, text="Refresh", command=refresh_users).pack(side="left", padx=(8, 0))

        def open_selected_user_double_click(event):
            item_id = self._treeview_item_from_double_click(tree, event)
            if item_id is None:
                return
            self.open_user_editor(item_id, refresh_users)

        tree.bind("<Double-Button-1>", open_selected_user_double_click)
        refresh_users()

    def open_user_editor(self, username, refresh_callback=None):
        user = self.system.users.get(username)
        if user is None:
            messagebox.showerror("Users", f"User {username} not found.")
            return

        can_manage_users = self.system.has_permission(self.account.role, "manage_users")

        window, created = self._open_or_focus_window(
            key=f"editor:User:{username}",
            title=f"User {username}",
            geometry="520x320",
        )
        if not created:
            return

        ttk.Label(window, text=f"Username: {user.username}").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 8)
        )

        ttk.Label(window, text="Role").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        role_var = tk.StringVar(value=user.role)
        role_box = ttk.Combobox(
            window,
            textvariable=role_var,
            values=("admin", "manager", "technician", "viewer"),
            state=("readonly" if can_manage_users else "disabled"),
        )
        role_box.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        must_change_var = tk.BooleanVar(value=user.must_change_password)
        ttk.Checkbutton(
            window,
            text="Require password change at next login",
            variable=must_change_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=6)
        if not can_manage_users:
            for child in window.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.configure(state="disabled")

        ttk.Label(window, text="New Password").grid(row=3, column=0, sticky="w", padx=12, pady=4)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(window, textvariable=password_var, width=32, show="*")
        password_entry.grid(row=3, column=1, sticky="ew", padx=12, pady=4)
        if not can_manage_users:
            password_entry.configure(state="disabled")

        def run_refresh():
            if refresh_callback is not None:
                refresh_callback()

        def save_role():
            if not can_manage_users:
                return
            ok, message = self.system.set_user_role(user.username, role_var.get(), actor_role=self.account.role)
            if ok:
                current_user = self.system.users.get(user.username)
                if current_user is not None:
                    must_change_var.set(current_user.must_change_password)
                messagebox.showinfo("Users", message)
                run_refresh()
            else:
                messagebox.showerror("Users", message)

        def reset_user_password():
            if not can_manage_users:
                return
            new_password = password_var.get()
            if not new_password:
                messagebox.showerror("Reset Password", "Password cannot be empty.")
                password_entry.focus_set()
                return

            ok, message = self.system.reset_password(
                user.username,
                new_password,
                must_change_password=must_change_var.get(),
                actor_role=self.account.role,
            )
            if ok:
                password_var.set("")
                messagebox.showinfo("Users", message)
                run_refresh()
            else:
                messagebox.showerror("Users", message)

        def remove_user():
            if not can_manage_users:
                return
            if not messagebox.askyesno("Remove User", f"Remove user {user.username}?"):
                return

            ok, message = self.system.remove_user(user.username, actor_role=self.account.role)
            if ok:
                messagebox.showinfo("Users", message)
                run_refresh()
                window.destroy()
            else:
                messagebox.showerror("Users", message)

        save_role_btn = ttk.Button(window, text="Save Role", command=save_role)
        save_role_btn.grid(
            row=4, column=0, sticky="ew", padx=12, pady=(12, 6)
        )

        reset_password_btn = ttk.Button(window, text="Reset Password", command=reset_user_password)
        reset_password_btn.grid(
            row=4, column=1, sticky="ew", padx=12, pady=(12, 6)
        )

        delete_btn = tk.Button(
            window,
            text="Delete",
            fg="red",
            activeforeground="red",
            command=remove_user,
        )
        delete_btn.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 12))
        if not can_manage_users:
            save_role_btn.configure(state="disabled")
            reset_password_btn.configure(state="disabled")
            delete_btn.configure(state="disabled")

        if not can_manage_users:
            role_box.configure(state="disabled")

        window.columnconfigure(1, weight=1)

    def open_machine_editor(self, machine_id):
        machine = self.system.machineList.get(machine_id)
        if machine is None:
            messagebox.showerror("Machines", "Machine not found.")
            return

        can_edit = self.system.has_permission(self.account.role, "manage_machines")

        window, created = self._open_or_focus_window(
            key=f"editor:Machine:{machine.machineID}",
            title=f"Machine {machine.machineID}",
            geometry="520x280",
        )
        if not created:
            return

        ttk.Label(window, text=f"Machine ID: {machine.machineID}").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))

        self._required_label(window, "Name", 1)
        name_var = tk.StringVar(value=machine.machineName)
        name_entry = ttk.Entry(window, textvariable=name_var, width=36)
        name_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Description").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar(value=machine.machineDescription)
        desc_entry = ttk.Entry(window, textvariable=desc_var, width=36)
        desc_entry.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        self._required_label(window, "Room", 3)
        room_names = sorted([room.roomName for room in self.system.roomList.values()])
        room_var = tk.StringVar(value=self._get_room_name(machine.machineLocation))
        room_box = ttk.Combobox(window, textvariable=room_var, values=room_names, state="readonly")
        room_box.grid(row=3, column=1, sticky="ew", padx=12, pady=4)

        if not can_edit:
            name_entry.configure(state="disabled")
            desc_entry.configure(state="disabled")
            room_box.configure(state="disabled")

        def save_machine():
            missing = []
            if not name_var.get().strip():
                missing.append("Name")
            if not room_var.get().strip():
                missing.append("Room")
            if missing:
                focus_widget = name_entry if "Name" in missing else room_box
                self._show_missing_required_fields("Machines", missing, focus_widget)
                return

            selected_room = self.system.getRoomByName(room_var.get().strip())
            if selected_room is None:
                messagebox.showerror("Machines", "Selected room was not found.")
                room_box.focus_set()
                return

            ok1, msg1 = self.system.update_machine_field(
                machine,
                "name",
                name_var.get().strip(),
                actor_role=self.account.role,
                persist=False,
            )
            if not ok1:
                messagebox.showerror("Machines", msg1)
                return

            ok2, msg2 = self.system.update_machine_field(
                machine,
                "description",
                desc_var.get().strip(),
                actor_role=self.account.role,
                persist=False,
            )
            if not ok2:
                messagebox.showerror("Machines", msg2)
                return

            ok3, msg3 = self.system.update_machine_field(
                machine,
                "room",
                selected_room.roomID,
                actor_role=self.account.role,
                persist=False,
            )
            if not ok3:
                messagebox.showerror("Machines", msg3)
                return

            self.system.saveData(self.system.file_path)

            messagebox.showinfo("Machines", "Machine updated successfully.")
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Machines", "menu:Rooms", "menu:Parts")

        save_btn = ttk.Button(window, text="Save", command=save_machine)
        save_btn.grid(row=4, column=0, padx=12, pady=(12, 12), sticky="ew")
        if not can_edit:
            save_btn.configure(state="disabled")

        def delete_machine_from_editor():
            if not can_edit:
                return
            if not messagebox.askyesno("Delete Machine", f"Delete {machine.machineID} - {machine.machineName}?"):
                return

            for part_id, quantity in machine.part_contained_ID.items():
                part = self.system.partsList.get(part_id)
                if part is not None:
                    part.stock["installed"] = max(0, part.stock.get("installed", 0) - quantity)
                    part.stock["new"] = part.stock.get("new", 0) + quantity
                    part.machineID.pop(machine.machineID, None)

            self.system.machineList.pop(machine.machineID, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Machines", "menu:Rooms", "menu:Parts")
            messagebox.showinfo("Machines", f"Machine {machine.machineName} removed.")
            window.destroy()

        delete_btn = tk.Button(
            window,
            text="Delete",
            fg="red",
            activeforeground="red",
            command=delete_machine_from_editor,
        )
        delete_btn.grid(row=4, column=1, padx=12, pady=(12, 12), sticky="ew")
        if not can_edit:
            delete_btn.configure(state="disabled")

        window.columnconfigure(1, weight=1)

    def open_room_editor(self, room_id):
        room = self.system.roomList.get(room_id)
        if room is None:
            messagebox.showerror("Rooms", "Room not found.")
            return

        can_edit = self.system.has_permission(self.account.role, "manage_rooms")

        window, created = self._open_or_focus_window(
            key=f"editor:Room:{room.roomID}",
            title=f"Room {room.roomID}",
            geometry="520x220",
        )
        if not created:
            return

        ttk.Label(window, text=f"Room ID: {room.roomID}").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))

        self._required_label(window, "Name", 1)
        name_var = tk.StringVar(value=room.roomName)
        name_entry = ttk.Entry(window, textvariable=name_var, width=36)
        name_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Description").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar(value=room.roomDescription)
        desc_entry = ttk.Entry(window, textvariable=desc_var, width=36)
        desc_entry.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        if not can_edit:
            name_entry.configure(state="disabled")
            desc_entry.configure(state="disabled")

        def save_room():
            if not can_edit:
                return

            missing = []
            if not name_var.get().strip():
                missing.append("Name")
            if missing:
                self._show_missing_required_fields("Rooms", missing, name_entry)
                return

            room.roomName = name_var.get().strip()
            room.roomDescription = desc_var.get().strip()
            self.system.saveData(self.system.file_path)
            messagebox.showinfo("Rooms", "Room updated successfully.")
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Rooms", "menu:Machines")

        save_btn = ttk.Button(window, text="Save", command=save_room)
        save_btn.grid(row=3, column=0, padx=12, pady=(12, 12), sticky="ew")
        if not can_edit:
            save_btn.configure(state="disabled")

        def delete_room_from_editor():
            if not can_edit:
                return
            if not messagebox.askyesno("Delete Room", f"Delete {room.roomID} - {room.roomName}?"):
                return

            for machine in self.system.machineList.values():
                if machine.machineLocation == room.roomID:
                    messagebox.showerror("Rooms", "Room cannot be removed while machines are assigned to it.")
                    return

            self.system.roomList.pop(room.roomID, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Rooms", "menu:Machines")
            messagebox.showinfo("Rooms", f"Room {room.roomName} removed.")
            window.destroy()

        delete_btn = tk.Button(
            window,
            text="Delete",
            fg="red",
            activeforeground="red",
            command=delete_room_from_editor,
        )
        delete_btn.grid(row=3, column=1, padx=12, pady=(12, 12), sticky="ew")
        if not can_edit:
            delete_btn.configure(state="disabled")

        window.columnconfigure(1, weight=1)

    def open_category_editor(self, category_id):
        category = self.system.categoriesList.get(category_id)
        if category is None:
            messagebox.showerror("Categories", "Category not found.")
            return

        can_edit = self.system.has_permission(self.account.role, "manage_categories")

        window, created = self._open_or_focus_window(
            key=f"editor:Category:{category.categoryID}",
            title=f"Category {category.categoryID}",
            geometry="560x280",
        )
        if not created:
            return

        ttk.Label(window, text=f"Category ID: {category.categoryID}").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))

        self._required_label(window, "Name", 1)
        name_var = tk.StringVar(value=category.categoryName)
        name_entry = ttk.Entry(window, textvariable=name_var, width=40)
        name_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Description").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        desc_var = tk.StringVar(value=category.categoryDescription)
        desc_entry = ttk.Entry(window, textvariable=desc_var, width=40)
        desc_entry.grid(row=2, column=1, sticky="ew", padx=12, pady=4)

        ttk.Label(window, text="Specs (comma separated)").grid(row=3, column=0, sticky="w", padx=12, pady=4)
        specs_var = tk.StringVar(value=", ".join(category.specList or []))
        specs_entry = ttk.Entry(window, textvariable=specs_var, width=40)
        specs_entry.grid(row=3, column=1, sticky="ew", padx=12, pady=4)

        if not can_edit:
            name_entry.configure(state="disabled")
            desc_entry.configure(state="disabled")
            specs_entry.configure(state="disabled")

        def save_category():
            if not can_edit:
                return

            missing = []
            if not name_var.get().strip():
                missing.append("Name")
            if missing:
                self._show_missing_required_fields("Categories", missing, name_entry)
                return

            category.categoryName = name_var.get().strip()
            category.categoryDescription = desc_var.get().strip()
            raw_specs = specs_var.get().strip()
            if raw_specs:
                category.specList = [item.strip() for item in raw_specs.split(",") if item.strip()]
            else:
                category.specList = []

            self.system.saveData(self.system.file_path)
            messagebox.showinfo("Categories", "Category updated successfully.")
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Categories", "menu:Parts", "menu:Machines")

        save_btn = ttk.Button(window, text="Save", command=save_category)
        save_btn.grid(row=4, column=0, padx=12, pady=(12, 12), sticky="ew")
        if not can_edit:
            save_btn.configure(state="disabled")

        def delete_category_from_editor():
            if not can_edit:
                return
            if not messagebox.askyesno(
                "Delete Category",
                f"Delete {category.categoryID} - {category.categoryName}?\nParts in this category will be unassigned.",
            ):
                return

            for part in self.system.partsList.values():
                if str(part.category).strip().upper() == category.categoryID.strip().upper():
                    part.category = ""

            self.system.categoriesList.pop(category.categoryID, None)
            self.system.saveData(self.system.file_path)
            self._build_dynamic_top_menus()
            self._refresh_registered_windows("menu:Categories", "menu:Parts", "menu:Machines")
            messagebox.showinfo("Categories", f"Category {category.categoryName} removed.")
            window.destroy()

        delete_btn = tk.Button(
            window,
            text="Delete",
            fg="red",
            activeforeground="red",
            command=delete_category_from_editor,
        )
        delete_btn.grid(row=4, column=1, padx=12, pady=(12, 12), sticky="ew")
        if not can_edit:
            delete_btn.configure(state="disabled")

        window.columnconfigure(1, weight=1)

    def change_password(self):
        current_password = simpledialog.askstring("Change Password", "Current password", show="*", parent=self.app)
        if current_password is None:
            return

        new_password = simpledialog.askstring("Change Password", "New password", show="*", parent=self.app)
        if new_password is None:
            return

        confirm_password = simpledialog.askstring("Change Password", "Confirm new password", show="*", parent=self.app)
        if confirm_password is None:
            return

        if not new_password:
            messagebox.showerror("Change Password", "Password cannot be empty.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Change Password", "Passwords do not match.")
            return

        ok, message = self.system.change_password(self.account.username, current_password, new_password)
        if ok:
            messagebox.showinfo("Change Password", message)
        else:
            messagebox.showerror("Change Password", message)

    def logout(self):
        self.app.show_login()


class InventoryGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Manager")
        self.geometry("900x560")
        self.minsize(840, 520)
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.system = inventorySystem()
        self.system.loadData()

        self.current_frame = None
        self.current_user = None
        self.open_windows = {}
        self.window_refreshers = {}

        self.show_login()

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        for key, window in list(self.open_windows.items()):
            if window is not None and window.winfo_exists():
                window.destroy()
            self.open_windows.pop(key, None)
            self.window_refreshers.pop(key, None)

        self.current_user = None
        self.config(menu=tk.Menu(self))
        self.clear_frame()
        frame = LoginFrame(self)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

    def show_main_menu(self, account):
        self.current_user = account
        self.clear_frame()
        frame = MainMenuFrame(self, account)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

    def attempt_login(self, username, password):
        account = self.system.authenticate_user(username, password)
        if account is None:
            messagebox.showerror("Login", "Invalid username or password.")
            return

        if account.must_change_password:
            new_password = simpledialog.askstring(
                "Password Reset Required",
                "Enter a new password",
                show="*",
                parent=self,
            )
            if new_password is None:
                return

            confirm_password = simpledialog.askstring(
                "Password Reset Required",
                "Confirm the new password",
                show="*",
                parent=self,
            )
            if confirm_password is None:
                return

            if not new_password:
                messagebox.showerror("Password Reset", "Password cannot be empty.")
                return

            if new_password != confirm_password:
                messagebox.showerror("Password Reset", "Passwords do not match.")
                return

            ok, message = self.system.change_password(username, password, new_password)
            if not ok:
                messagebox.showerror("Password Reset", message)
                return

            refreshed_account = self.system.users.get(account.username)
            if refreshed_account is not None:
                account = refreshed_account

        self.show_main_menu(account)

    def exit_app(self):
        self.destroy()


def launch_inventory_gui():
    app = InventoryGUIApp()
    app.mainloop()
