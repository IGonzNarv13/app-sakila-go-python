import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, username, navigation_callbacks, logout_callback):
        super().__init__(
            parent,
            width=260,
            corner_radius=0,
            fg_color="#111827"
        )

        self.username = username
        self.navigation_callbacks = navigation_callbacks
        self.logout_callback = logout_callback

        self.grid_propagate(False)
        self.build()

    def build(self):
        title = ctk.CTkLabel(
            self,
            text="Sakila Wiki",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(28, 4), padx=20, anchor="w")

        user_label = ctk.CTkLabel(
            self,
            text=f"Usuario: {self.username}",
            font=ctk.CTkFont(size=13),
            text_color="#d1d5db"
        )
        user_label.pack(pady=(0, 24), padx=20, anchor="w")

        self.create_button("Inicio", self.navigation_callbacks["home"])
        self.create_button("Películas", self.navigation_callbacks["films"])
        self.create_button("Actores", self.navigation_callbacks["actors"])
        self.create_button("Categorías", self.navigation_callbacks["categories"])
        self.create_button("Comunicación", self.navigation_callbacks["communication"])

        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        logout_button = ctk.CTkButton(
            self,
            text="Cerrar sesión",
            height=38,
            fg_color="#991b1b",
            hover_color="#7f1d1d",
            command=self.logout_callback
        )
        logout_button.pack(padx=20, pady=(0, 24), fill="x")

    def create_button(self, text, command):
        button = ctk.CTkButton(
            self,
            text=text,
            height=38,
            anchor="w",
            fg_color="transparent",
            hover_color="#1f2937",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14),
            command=command
        )
        button.pack(padx=14, pady=4, fill="x")