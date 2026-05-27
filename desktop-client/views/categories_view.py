import customtkinter as ctk
from tkinter import ttk
from services.api import get_request


class CategoriesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f4f6f8")
        self.pack(fill="both", expand=True)

        self.categories_table = None

        self.build()
        self.load_categories()

    def build(self):
        self.create_header(
            "Categorías",
            "Consulta el catálogo de categorías disponibles dentro de la base de datos Sakila."
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
            text="Actualizar categorías",
            width=180,
            height=38,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.load_categories
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

        columns = ("category_id", "name")

        self.categories_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings"
        )

        self.categories_table.heading("category_id", text="ID")
        self.categories_table.heading("name", text="Categoría")

        self.categories_table.column("category_id", width=100, anchor="center")
        self.categories_table.column("name", width=400)

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.categories_table.yview
        )
        self.categories_table.configure(yscrollcommand=scrollbar.set)

        self.categories_table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(16, 0),
            pady=16
        )
        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 16),
            pady=16
        )

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
            wraplength=860,
            justify="left"
        )
        description_label.pack(anchor="w", pady=(4, 0))

    def load_categories(self):
        status, data = get_request("/api/categories")

        if status == 200:
            self.fill_table(data)
        else:
            self.show_error(data.get("error", "Error al obtener categorías."))

    def fill_table(self, categories):
        self.clear_table()

        for category in categories:
            self.categories_table.insert(
                "",
                "end",
                values=(
                    category.get("category_id", ""),
                    category.get("name", "")
                )
            )

    def clear_table(self):
        for item in self.categories_table.get_children():
            self.categories_table.delete(item)

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Aviso")
        error_window.geometry("380x160")
        error_window.resizable(False, False)

        label = ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=320,
            text_color="#b91c1c"
        )
        label.pack(expand=True, padx=20, pady=20)

        button = ctk.CTkButton(
            error_window,
            text="Aceptar",
            command=error_window.destroy
        )
        button.pack(pady=(0, 20))