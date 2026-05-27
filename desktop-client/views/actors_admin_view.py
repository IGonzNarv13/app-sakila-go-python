import customtkinter as ctk
from tkinter import ttk, messagebox
from services.api import get_request, post_request, put_request, delete_request


class ActorsAdminView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f4f6f8")
        self.pack(fill="both", expand=True)

        self.table = None

        self.actor_id_entry = None
        self.first_name_entry = None
        self.last_name_entry = None

        self.search_id_entry = None

        self.build()
        self.load_actors()

    def build(self):
        self.create_header(
            "Actores",
            "Administra los actores registrados en Sakila mediante operaciones de consulta, creación, actualización y eliminación."
        )

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        main_container.grid_columnconfigure(0, weight=2)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        self.build_table_panel(main_container)
        self.build_form_panel(main_container)

    def create_header(self, title, description):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 16))

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#111827"
        )
        title_label.pack(anchor="w")

        description_label = ctk.CTkLabel(
            header,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color="#6b7280",
            wraplength=880,
            justify="left"
        )
        description_label.pack(anchor="w", pady=(4, 0))

    # ==========================
    # PANEL TABLA
    # ==========================

    def build_table_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(
            panel,
            text="Listado de actores",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#111827"
        )
        title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        controls = ctk.CTkFrame(panel, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        controls.grid_columnconfigure(0, weight=1)

        self.search_id_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Buscar por ID",
            height=38
        )
        self.search_id_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        search_button = ctk.CTkButton(
            controls,
            text="Buscar",
            width=100,
            height=38,
            command=self.search_actor_by_id
        )
        search_button.grid(row=0, column=1, padx=4)

        refresh_button = ctk.CTkButton(
            controls,
            text="Actualizar",
            width=110,
            height=38,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.load_actors
        )
        refresh_button.grid(row=0, column=2, padx=(4, 0))

        table_frame = ctk.CTkFrame(panel, fg_color="#ffffff")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("actor_id", "first_name", "last_name")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.table.heading("actor_id", text="ID")
        self.table.heading("first_name", text="Nombre")
        self.table.heading("last_name", text="Apellido")

        self.table.column("actor_id", width=80, anchor="center")
        self.table.column("first_name", width=220)
        self.table.column("last_name", width=220)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.table.bind("<<TreeviewSelect>>", self.on_actor_select)

    # ==========================
    # PANEL FORMULARIO
    # ==========================

    def build_form_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        title = ctk.CTkLabel(
            panel,
            text="Formulario de actor",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#111827"
        )
        title.pack(anchor="w", padx=18, pady=(18, 14))

        id_label = ctk.CTkLabel(
            panel,
            text="ID del actor",
            font=ctk.CTkFont(size=13),
            text_color="#374151"
        )
        id_label.pack(anchor="w", padx=18, pady=(0, 4))

        self.actor_id_entry = ctk.CTkEntry(
            panel,
            placeholder_text="Se llena al seleccionar o buscar",
            height=38
        )
        self.actor_id_entry.pack(fill="x", padx=18, pady=(0, 12))

        first_name_label = ctk.CTkLabel(
            panel,
            text="Nombre",
            font=ctk.CTkFont(size=13),
            text_color="#374151"
        )
        first_name_label.pack(anchor="w", padx=18, pady=(0, 4))

        self.first_name_entry = ctk.CTkEntry(
            panel,
            placeholder_text="Nombre del actor",
            height=38
        )
        self.first_name_entry.pack(fill="x", padx=18, pady=(0, 12))

        last_name_label = ctk.CTkLabel(
            panel,
            text="Apellido",
            font=ctk.CTkFont(size=13),
            text_color="#374151"
        )
        last_name_label.pack(anchor="w", padx=18, pady=(0, 4))

        self.last_name_entry = ctk.CTkEntry(
            panel,
            placeholder_text="Apellido del actor",
            height=38
        )
        self.last_name_entry.pack(fill="x", padx=18, pady=(0, 18))

        create_button = ctk.CTkButton(
            panel,
            text="Crear actor",
            height=38,
            command=self.create_actor
        )
        create_button.pack(fill="x", padx=18, pady=(0, 10))

        update_button = ctk.CTkButton(
            panel,
            text="Actualizar actor",
            height=38,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.update_actor
        )
        update_button.pack(fill="x", padx=18, pady=(0, 10))

        delete_button = ctk.CTkButton(
            panel,
            text="Eliminar actor",
            height=38,
            fg_color="#991b1b",
            hover_color="#7f1d1d",
            command=self.delete_actor
        )
        delete_button.pack(fill="x", padx=18, pady=(0, 10))

        clear_button = ctk.CTkButton(
            panel,
            text="Limpiar formulario",
            height=38,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.clear_form
        )
        clear_button.pack(fill="x", padx=18, pady=(0, 18))

        note = ctk.CTkLabel(
            panel,
            text="Para actualizar o eliminar, selecciona un actor de la tabla o búscalo por ID.",
            font=ctk.CTkFont(size=12),
            text_color="#6b7280",
            wraplength=260,
            justify="left"
        )
        note.pack(anchor="w", padx=18, pady=(4, 0))

    # ==========================
    # CARGA Y TABLA
    # ==========================

    def load_actors(self):
        status, data = get_request("/api/actors")

        if status == 200:
            self.fill_table(data)
        else:
            self.show_error(data.get("error", "Error al obtener actores."))

    def fill_table(self, actors):
        self.clear_table()

        for actor in actors:
            self.table.insert(
                "",
                "end",
                values=(
                    actor.get("actor_id", ""),
                    actor.get("first_name", ""),
                    actor.get("last_name", "")
                )
            )

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def on_actor_select(self, event):
        selected_item = self.table.focus()

        if not selected_item:
            return

        values = self.table.item(selected_item, "values")

        if len(values) < 3:
            return

        self.set_form_values(values[0], values[1], values[2])

    def set_form_values(self, actor_id, first_name, last_name):
        self.actor_id_entry.delete(0, "end")
        self.actor_id_entry.insert(0, str(actor_id))

        self.first_name_entry.delete(0, "end")
        self.first_name_entry.insert(0, str(first_name))

        self.last_name_entry.delete(0, "end")
        self.last_name_entry.insert(0, str(last_name))

    def clear_form(self):
        self.actor_id_entry.delete(0, "end")
        self.first_name_entry.delete(0, "end")
        self.last_name_entry.delete(0, "end")
        self.search_id_entry.delete(0, "end")

        for item in self.table.selection():
            self.table.selection_remove(item)

    # ==========================
    # CRUD
    # ==========================

    def search_actor_by_id(self):
        actor_id = self.search_id_entry.get().strip()

        if actor_id == "":
            self.show_error("Debes escribir un ID para buscar.")
            return

        if not actor_id.isdigit():
            self.show_error("El ID debe ser numérico.")
            return

        status, data = get_request(f"/api/actors/{actor_id}")

        if status == 200:
            self.clear_table()
            self.fill_table([data])
            self.set_form_values(
                data.get("actor_id", ""),
                data.get("first_name", ""),
                data.get("last_name", "")
            )
        else:
            self.show_error(data.get("error", "Actor no encontrado."))

    def create_actor(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()

        if first_name == "" or last_name == "":
            self.show_error("El nombre y apellido son obligatorios.")
            return

        status, data = post_request("/api/actors", {
            "first_name": first_name,
            "last_name": last_name
        })

        if status == 201:
            self.show_info(data.get("message", "Actor creado correctamente."))
            self.clear_form()
            self.load_actors()
        else:
            self.show_error(data.get("error", "Error al crear actor."))

    def update_actor(self):
        actor_id = self.actor_id_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()

        if actor_id == "":
            self.show_error("Debes seleccionar o buscar un actor para actualizar.")
            return

        if not actor_id.isdigit():
            self.show_error("El ID del actor debe ser numérico.")
            return

        if first_name == "" or last_name == "":
            self.show_error("El nombre y apellido son obligatorios.")
            return

        status, data = put_request(f"/api/actors/{actor_id}", {
            "first_name": first_name,
            "last_name": last_name
        })

        if status == 200:
            self.show_info(data.get("message", "Actor actualizado correctamente."))
            self.clear_form()
            self.load_actors()
        else:
            self.show_error(data.get("error", "Error al actualizar actor."))

    def delete_actor(self):
        actor_id = self.actor_id_entry.get().strip()

        if actor_id == "":
            self.show_error("Debes seleccionar o buscar un actor para eliminar.")
            return

        if not actor_id.isdigit():
            self.show_error("El ID del actor debe ser numérico.")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Seguro que deseas eliminar este actor? Esta acción también puede eliminar sus relaciones con películas."
        )

        if not confirm:
            return

        status, data = delete_request(f"/api/actors/{actor_id}")

        if status == 200:
            self.show_info(data.get("message", "Actor eliminado correctamente."))
            self.clear_form()
            self.load_actors()
        else:
            self.show_error(data.get("error", "Error al eliminar actor."))

    # ==========================
    # ALERTAS
    # ==========================

    def show_error(self, message):
        messagebox.showerror("Aviso", message)

    def show_info(self, message):
        messagebox.showinfo("Información", message)