import customtkinter as ctk
from tkinter import ttk
from services.api import get_request


class ActorsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f4f6f8")
        self.pack(fill="both", expand=True)

        self.table = None

        self.build()
        self.load_actors()

    def build(self):
        self.create_header(
            "Actores",
            "Consulta los actores registrados en la base de datos Sakila."
        )

        controls = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        controls.pack(fill="x", padx=32, pady=(0, 16))

        refresh_button = ctk.CTkButton(
            controls,
            text="Actualizar",
            width=140,
            height=38,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.load_actors
        )
        refresh_button.pack(side="left", padx=16, pady=16)

        table_container = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        table_container.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        columns = ("actor_id", "first_name", "last_name")

        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings"
        )

        self.table.heading("actor_id", text="ID")
        self.table.heading("first_name", text="Nombre")
        self.table.heading("last_name", text="Apellido")

        self.table.column("actor_id", width=80, anchor="center")
        self.table.column("first_name", width=260)
        self.table.column("last_name", width=260)

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side="right", fill="y", padx=(0, 16), pady=16)

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
            wraplength=760,
            justify="left"
        )
        description_label.pack(anchor="w", pady=(4, 0))

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

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

    def load_actors(self):
        status, data = get_request("/api/actors")

        if status == 200:
            self.fill_table(data)
        else:
            self.show_error(data.get("error", "Error al obtener actores."))

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("360x160")
        error_window.resizable(False, False)

        label = ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=300,
            text_color="#b91c1c"
        )
        label.pack(expand=True, padx=20, pady=20)

        button = ctk.CTkButton(
            error_window,
            text="Aceptar",
            command=error_window.destroy
        )
        button.pack(pady=(0, 20))