import customtkinter as ctk
from tkinter import ttk
from services.api import get_request


class FilmsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f4f6f8")
        self.pack(fill="both", expand=True)

        self.search_entry = None
        self.category_option = None
        self.table = None
        self.categories = []

        self.build()
        self.load_categories()
        self.load_films()

    def build(self):
        self.create_header(
            "Películas",
            "Consulta películas registradas en Sakila mediante búsqueda por título, categoría o filtros combinados."
        )

        controls = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        controls.pack(fill="x", padx=32, pady=(0, 16))

        controls.grid_columnconfigure(0, weight=2)
        controls.grid_columnconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Buscar por título",
            height=38
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=16)

        self.category_option = ctk.CTkOptionMenu(
            controls,
            values=["Todas las categorías"],
            height=38
        )
        self.category_option.grid(row=0, column=1, sticky="ew", padx=8, pady=16)

        search_button = ctk.CTkButton(
            controls,
            text="Buscar",
            width=120,
            height=38,
            command=self.search_films
        )
        search_button.grid(row=0, column=2, padx=8, pady=16)

        clear_button = ctk.CTkButton(
            controls,
            text="Limpiar filtros",
            width=130,
            height=38,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.clear_filters
        )
        clear_button.grid(row=0, column=3, padx=(8, 16), pady=16)

        table_container = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        table_container.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        columns = ("film_id", "title", "release_year", "rating", "length")

        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings"
        )

        self.table.heading("film_id", text="ID")
        self.table.heading("title", text="Título")
        self.table.heading("release_year", text="Año")
        self.table.heading("rating", text="Clasificación")
        self.table.heading("length", text="Duración")

        self.table.column("film_id", width=60, anchor="center")
        self.table.column("title", width=360)
        self.table.column("release_year", width=80, anchor="center")
        self.table.column("rating", width=120, anchor="center")
        self.table.column("length", width=90, anchor="center")

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
            wraplength=860,
            justify="left"
        )
        description_label.pack(anchor="w", pady=(4, 0))

    def load_categories(self):
        status, data = get_request("/api/categories")

        if status == 200:
            self.categories = data
            category_names = ["Todas las categorías"]

            for category in data:
                category_name = category.get("name", "")
                if category_name != "":
                    category_names.append(category_name)

            self.category_option.configure(values=category_names)
            self.category_option.set("Todas las categorías")
        else:
            self.show_error(data.get("error", "Error al obtener categorías."))

    def load_films(self):
        status, data = get_request("/api/films")

        if status == 200:
            self.fill_table(data)
        else:
            self.show_error(data.get("error", "Error al obtener películas."))

    def search_films(self):
        title = self.search_entry.get().strip().lower()
        category = self.category_option.get().strip()

        has_title = title != ""
        has_category = category != "" and category != "Todas las categorías"

        if not has_title and not has_category:
            self.load_films()
            return

        if has_title and not has_category:
            status, data = get_request(f"/api/films/search?title={title}")

            if status == 200:
                self.fill_table(data)
            else:
                self.show_error(data.get("error", "Error al buscar películas."))
            return

        if has_category:
            status, data = get_request(f"/api/films/category?name={category}")

            if status != 200:
                self.show_error(data.get("error", "Error al buscar películas por categoría."))
                return

            if has_title:
                data = [
                    film for film in data
                    if title in str(film.get("title", "")).lower()
                ]

            self.fill_table(data)

    def clear_filters(self):
        self.search_entry.delete(0, "end")
        self.category_option.set("Todas las categorías")
        self.load_films()

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def fill_table(self, films):
        self.clear_table()

        for film in films:
            self.table.insert(
                "",
                "end",
                values=(
                    film.get("film_id", ""),
                    film.get("title", ""),
                    film.get("release_year", ""),
                    film.get("rating", ""),
                    film.get("length", "")
                )
            )

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