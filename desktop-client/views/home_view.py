import customtkinter as ctk
from services.api import get_request


class HomeView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f4f6f8")
        self.pack(fill="both", expand=True)
        self.build()

    def build(self):
        self.create_header(
            "Inicio",
            "Panel principal del cliente de escritorio conectado a la API REST desarrollada en Go."
        )

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=32, pady=12)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.create_info_card(
            cards_frame,
            0,
            "Consultas Sakila",
            "Consulta películas, actores y categorías directamente desde MySQL."
        )

        self.create_info_card(
            cards_frame,
            1,
            "CRUD de actores",
            "Crea, consulta, actualiza y elimina actores mediante endpoints REST."
        )

        self.create_info_card(
            cards_frame,
            2,
            "Comunicación",
            "Interacción entre usuarios conectados mediante chat grupal y privado."
        )

        self.create_status_card()

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

    def create_info_card(self, parent, column, title, description):
        card = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        card.grid(row=0, column=column, padx=8, sticky="nsew")

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#111827"
        )
        title_label.pack(anchor="w", padx=18, pady=(18, 6))

        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=13),
            text_color="#6b7280",
            wraplength=260,
            justify="left"
        )
        desc_label.pack(anchor="w", padx=18, pady=(0, 18))

    def create_status_card(self):
        status_frame = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        status_frame.pack(fill="x", padx=32, pady=(20, 0))

        status_title = ctk.CTkLabel(
            status_frame,
            text="Estado de conexión",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#111827"
        )
        status_title.pack(anchor="w", padx=20, pady=(18, 8))

        status, data = get_request("/api/health")

        if status == 200:
            message = data.get("message", "Servidor disponible.")
            color = "#15803d"
        else:
            message = data.get("error", "Servidor no disponible.")
            color = "#b91c1c"

        status_label = ctk.CTkLabel(
            status_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=color
        )
        status_label.pack(anchor="w", padx=20, pady=(0, 18))