import customtkinter as ctk
from tkinter import messagebox

from services.api import post_request, get_request
from components.sidebar import Sidebar
from views.home_view import HomeView
from views.films_view import FilmsView
from views.actors_view import ActorsView
from views.categories_view import CategoriesView
from views.actors_admin_view import ActorsAdminView


class SakilaDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sakila Wiki Desktop")
        self.geometry("1200x720")
        self.minsize(1000, 620)

        self.username = ""

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#f4f6f8")

        self.show_login_view()

    # ==========================
    # UTILIDADES GENERALES
    # ==========================

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    # ==========================
    # LOGIN
    # ==========================

    def show_login_view(self):
        self.clear_window()

        container = ctk.CTkFrame(
            self,
            fg_color="#f4f6f8",
            corner_radius=0
        )
        container.pack(fill="both", expand=True)

        card = ctk.CTkFrame(
            container,
            width=430,
            height=350,
            fg_color="#ffffff",
            corner_radius=18,
            border_width=1,
            border_color="#d9dee3"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        title = ctk.CTkLabel(
            card,
            text="Sakila Wiki Desktop",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#1f2937"
        )
        title.pack(pady=(36, 8))

        subtitle = ctk.CTkLabel(
            card,
            text="Sistema cliente-servidor para consulta y administración de datos",
            font=ctk.CTkFont(size=13),
            text_color="#6b7280",
            wraplength=340,
            justify="center"
        )
        subtitle.pack(pady=(0, 28))

        self.username_entry = ctk.CTkEntry(
            card,
            width=320,
            height=42,
            placeholder_text="Nombre de usuario",
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(pady=(0, 14))
        self.username_entry.bind("<Return>", lambda event: self.login())

        login_button = ctk.CTkButton(
            card,
            text="Entrar al sistema",
            width=320,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.login
        )
        login_button.pack(pady=(0, 12))

        status, data = get_request("/api/health")

        if status == 200:
            status_text = "Servidor disponible"
            status_color = "#15803d"
        else:
            status_text = "Servidor no disponible"
            status_color = "#b91c1c"

        server_status = ctk.CTkLabel(
            card,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        server_status.pack(pady=(8, 0))

    def login(self):
        username = self.username_entry.get().strip()

        if username == "":
            self.show_error("Validación", "Debes escribir un nombre de usuario.")
            return

        status, data = post_request("/api/connect", {
            "username": username
        })

        if status == 200:
            self.username = username
            self.show_dashboard_view()
        else:
            self.show_error(
                "Error de conexión",
                data.get("error", "No se pudo iniciar sesión.")
            )

    # ==========================
    # DASHBOARD PRINCIPAL
    # ==========================

    def show_dashboard_view(self):
        self.clear_window()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        navigation_callbacks = {
            "home": self.show_home_view,
            "films": self.show_films_view,
            "actors": self.show_actors_view,
            "categories": self.show_categories_view,
            "actors_admin": self.show_actors_admin_view,
            "communication": self.show_communication_view,
        }

        self.sidebar = Sidebar(
            self,
            username=self.username,
            navigation_callbacks=navigation_callbacks,
            logout_callback=self.logout
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#f4f6f8"
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.show_home_view()

    def logout(self):
        if self.username != "":
            post_request("/api/disconnect", {
                "username": self.username
            })

        self.username = ""
        self.show_login_view()

    # ==========================
    # NAVEGACIÓN ENTRE VISTAS
    # ==========================

    def show_home_view(self):
        self.clear_content()
        HomeView(self.content_frame)

    def show_films_view(self):
        self.clear_content()
        FilmsView(self.content_frame)

    def show_actors_view(self):
        self.clear_content()
        ActorsAdminView(self.content_frame)

    def show_categories_view(self):
        self.clear_content()
        CategoriesView(self.content_frame)

    def show_actors_admin_view(self):
        self.clear_content()
        self.show_placeholder(
            "Admin Actores",
            "Aquí construiremos el CRUD completo de actores."
        )

    def show_communication_view(self):
        self.clear_content()
        self.show_placeholder(
            "Comunicación",
            "Aquí construiremos la lista de usuarios conectados, chat grupal y chat privado."
        )

    # ==========================
    # PLACEHOLDER TEMPORAL
    # ==========================

    def show_placeholder(self, title, description):
        container = ctk.CTkFrame(
            self.content_frame,
            fg_color="#f4f6f8",
            corner_radius=0
        )
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )
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

        card = ctk.CTkFrame(
            container,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        card.pack(fill="x", padx=32, pady=12)

        label = ctk.CTkLabel(
            card,
            text="Vista pendiente de implementar.",
            font=ctk.CTkFont(size=15),
            text_color="#6b7280"
        )
        label.pack(anchor="w", padx=20, pady=24)


if __name__ == "__main__":
    app = SakilaDesktopApp()
    app.mainloop()