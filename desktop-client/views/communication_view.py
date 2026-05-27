import customtkinter as ctk
from tkinter import messagebox

from services.api import get_request, post_request, start_event_listener


class CommunicationView(ctk.CTkFrame):
    def __init__(self, parent, username):
        super().__init__(parent, fg_color="#f4f6f8")
        self.pack(fill="both", expand=True)

        self.username = username

        self.current_mode = "users"
        self.chat_type = "group"
        self.chat_target = "general"

        self.messages_frame = None
        self.message_entry = None
        self.users_container = None

        self.event_stop = start_event_listener(self.handle_server_event)

        self.build_users_view()

    # ==========================
    # UTILIDADES
    # ==========================

    def clear_view(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_error(self, message):
        messagebox.showerror("Aviso", message)

    def show_info(self, message):
        messagebox.showinfo("Información", message)

    def scroll_to_bottom(self):
        if self.messages_frame is None:
            return

        try:
            self.messages_frame.update_idletasks()
            self.messages_frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

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

    # ==========================
    # EVENTOS DEL SERVIDOR
    # ==========================

    def handle_server_event(self, event_type, data):
        self.after(0, lambda: self.process_server_event(event_type, data))

    def process_server_event(self, event_type, data):
        if event_type in ["user_connected", "user_disconnected"]:
            if self.current_mode == "users":
                self.build_users_view()
                return

            if self.current_mode == "chat" and self.chat_type == "group":
                self.load_messages()
                return

            return

        if event_type == "message_received":
            message_type = data.get("type", "")
            sender = data.get("from", "")
            target = data.get("to", "")

            if self.current_mode != "chat":
                return

            if self.chat_type == "group":
                if message_type in ["group", "system"]:
                    self.load_messages()
                return

            if self.chat_type == "private":
                if message_type != "private":
                    return

                current_user = self.username
                current_target = self.chat_target

                is_current_conversation = (
                    (sender == current_user and target == current_target) or
                    (sender == current_target and target == current_user)
                )

                if is_current_conversation:
                    self.load_messages()

    # ==========================
    # VISTA USUARIOS
    # ==========================

    def build_users_view(self):
        self.clear_view()

        self.current_mode = "users"

        self.create_header(
            "Comunicación",
            "Consulta usuarios conectados, accede al chat grupal o inicia conversaciones privadas."
        )

        main_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        main_container.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_rowconfigure(0, weight=1)

        self.build_user_actions_panel(main_container)
        self.build_connected_users_panel(main_container)

    def build_user_actions_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        title = ctk.CTkLabel(
            panel,
            text="Sesión activa",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#111827"
        )
        title.pack(anchor="w", padx=18, pady=(18, 8))

        user_label = ctk.CTkLabel(
            panel,
            text=f"Usuario: {self.username}",
            font=ctk.CTkFont(size=14),
            text_color="#374151"
        )
        user_label.pack(anchor="w", padx=18, pady=(0, 18))

        group_button = ctk.CTkButton(
            panel,
            text="Abrir chat grupal",
            height=40,
            command=self.open_group_chat
        )
        group_button.pack(fill="x", padx=18, pady=(0, 12))

        refresh_button = ctk.CTkButton(
            panel,
            text="Actualizar usuarios",
            height=40,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.build_users_view
        )
        refresh_button.pack(fill="x", padx=18, pady=(0, 12))

        info = ctk.CTkLabel(
            panel,
            text="Selecciona un usuario conectado para abrir una conversación privada.",
            font=ctk.CTkFont(size=13),
            text_color="#6b7280",
            wraplength=260,
            justify="left"
        )
        info.pack(anchor="w", padx=18, pady=(12, 0))

    def build_connected_users_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            panel,
            text="Usuarios conectados",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#111827"
        )
        title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        self.users_container = ctk.CTkScrollableFrame(
            panel,
            fg_color="#ffffff"
        )
        self.users_container.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        self.load_connected_users()

    def load_connected_users(self):
        if self.users_container is None:
            return

        for widget in self.users_container.winfo_children():
            widget.destroy()

        status, users = get_request("/api/users")

        if status != 200:
            self.show_error(users.get("error", "Error al obtener usuarios conectados."))
            return

        other_users = [
            user for user in users
            if user.get("username") != self.username
        ]

        if len(other_users) == 0:
            empty_label = ctk.CTkLabel(
                self.users_container,
                text="No hay otros usuarios conectados.",
                font=ctk.CTkFont(size=14),
                text_color="#6b7280"
            )
            empty_label.pack(anchor="w", padx=6, pady=10)
            return

        for user in other_users:
            username = user.get("username", "")
            connected_at = user.get("connected_at", "")

            self.create_user_card(username, connected_at)

    def create_user_card(self, username, connected_at):
        card = ctk.CTkFrame(
            self.users_container,
            fg_color="#f9fafb",
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb"
        )
        card.pack(fill="x", padx=4, pady=6)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=14, pady=(12, 4))

        name_label = ctk.CTkLabel(
            top_row,
            text=username,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827"
        )
        name_label.pack(side="left", anchor="w")

        date_label = ctk.CTkLabel(
            card,
            text=f"Conectado desde: {connected_at}",
            font=ctk.CTkFont(size=12),
            text_color="#6b7280"
        )
        date_label.pack(anchor="w", padx=14, pady=(0, 10))

        chat_button = ctk.CTkButton(
            card,
            text="Abrir chat privado",
            height=34,
            command=lambda user=username: self.open_private_chat(user)
        )
        chat_button.pack(fill="x", padx=14, pady=(0, 12))

    # ==========================
    # VISTA CHAT
    # ==========================

    def open_group_chat(self):
        self.chat_type = "group"
        self.chat_target = "general"
        self.build_chat_view()

    def open_private_chat(self, username):
        self.chat_type = "private"
        self.chat_target = username
        self.build_chat_view()

    def build_chat_view(self):
        self.clear_view()

        self.current_mode = "chat"

        title = "Chat grupal"

        if self.chat_type == "private":
            title = f"Chat con {self.chat_target}"

        self.create_header(
            title,
            "Envía y consulta mensajes usando la API REST del servidor."
        )

        main_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        main_container.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        self.build_chat_controls(main_container)
        self.build_messages_panel(main_container)
        self.build_message_input(main_container)

        self.load_messages()

    def build_chat_controls(self, parent):
        controls = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        back_button = ctk.CTkButton(
            controls,
            text="Volver a usuarios",
            width=150,
            height=38,
            fg_color="#374151",
            hover_color="#1f2937",
            command=self.build_users_view
        )
        back_button.pack(side="left", padx=(16, 8), pady=14)

        refresh_button = ctk.CTkButton(
            controls,
            text="Actualizar chat",
            width=150,
            height=38,
            command=self.load_messages
        )
        refresh_button.pack(side="left", padx=8, pady=14)

        chat_info = "Chat grupal"

        if self.chat_type == "private":
            chat_info = f"Conversación privada con {self.chat_target}"

        label = ctk.CTkLabel(
            controls,
            text=chat_info,
            font=ctk.CTkFont(size=13),
            text_color="#6b7280"
        )
        label.pack(side="left", padx=16, pady=14)

    def build_messages_panel(self, parent):
        self.messages_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        self.messages_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 12))

    def build_message_input(self, parent):
        input_panel = ctk.CTkFrame(
            parent,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#d9dee3"
        )
        input_panel.grid(row=2, column=0, sticky="ew")

        input_panel.grid_columnconfigure(0, weight=1)

        self.message_entry = ctk.CTkEntry(
            input_panel,
            placeholder_text="Escribe un mensaje",
            height=40
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=14)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        send_button = ctk.CTkButton(
            input_panel,
            text="Enviar",
            width=120,
            height=40,
            command=self.send_message
        )
        send_button.grid(row=0, column=1, padx=(8, 16), pady=14)

    # ==========================
    # MENSAJES
    # ==========================

    def load_messages(self):
        if self.messages_frame is None:
            return

        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        if self.chat_type == "group":
            status, messages = get_request("/api/messages?type=group")
        else:
            status, messages = get_request(
                f"/api/messages?type=private&user1={self.username}&user2={self.chat_target}"
            )

        if status != 200:
            self.show_error(messages.get("error", "Error al obtener mensajes."))
            return

        if len(messages) == 0:
            empty_label = ctk.CTkLabel(
                self.messages_frame,
                text="Todavía no hay mensajes en este chat.",
                font=ctk.CTkFont(size=14),
                text_color="#6b7280"
            )
            empty_label.pack(padx=16, pady=16)
            self.after(100, self.scroll_to_bottom)
            return

        for msg in messages[-40:]:
            self.render_message(msg)

        self.after(100, self.scroll_to_bottom)

    def render_message(self, msg):
        sender = msg.get("from", "")
        text = msg.get("text", "")
        sent_at = msg.get("sent_at", "")
        msg_type = msg.get("type", "")

        if msg_type == "system" or sender == "Sistema":
            self.render_system_message(text)
            return

        if sender == self.username:
            self.render_own_message(text, sent_at)
            return

        self.render_received_message(sender, text, sent_at)

    def render_system_message(self, text):
        row = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=6)

        bubble = ctk.CTkFrame(
            row,
            fg_color="#dbeafe",
            corner_radius=16
        )
        bubble.pack(anchor="center")

        label = ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=12),
            text_color="#1e3a8a",
            wraplength=520,
            justify="center"
        )
        label.pack(padx=14, pady=8)

    def render_own_message(self, text, sent_at):
        row = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=6)

        bubble = ctk.CTkFrame(
            row,
            fg_color="#d8f3dc",
            corner_radius=14
        )
        bubble.pack(anchor="e", padx=(160, 4))

        text_label = ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color="#1b4332",
            wraplength=420,
            justify="left"
        )
        text_label.pack(anchor="w", padx=12, pady=(10, 2))

        date_label = ctk.CTkLabel(
            bubble,
            text=sent_at,
            font=ctk.CTkFont(size=11),
            text_color="#52796f"
        )
        date_label.pack(anchor="e", padx=12, pady=(0, 8))

    def render_received_message(self, sender, text, sent_at):
        row = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=6)

        bubble = ctk.CTkFrame(
            row,
            fg_color="#f1f3f5",
            corner_radius=14
        )
        bubble.pack(anchor="w", padx=(4, 160))

        sender_label = ctk.CTkLabel(
            bubble,
            text=sender,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#343a40"
        )
        sender_label.pack(anchor="w", padx=12, pady=(10, 2))

        text_label = ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color="#212529",
            wraplength=420,
            justify="left"
        )
        text_label.pack(anchor="w", padx=12, pady=(0, 2))

        date_label = ctk.CTkLabel(
            bubble,
            text=sent_at,
            font=ctk.CTkFont(size=11),
            text_color="#6c757d"
        )
        date_label.pack(anchor="w", padx=12, pady=(0, 8))

    def send_message(self):
        text = self.message_entry.get().strip()

        if text == "":
            self.show_error("El mensaje no puede estar vacío.")
            return

        if self.chat_type == "group":
            payload = {
                "from": self.username,
                "to": "general",
                "text": text,
                "type": "group"
            }
        else:
            payload = {
                "from": self.username,
                "to": self.chat_target,
                "text": text,
                "type": "private"
            }

        status, data = post_request("/api/messages", payload)

        if status == 201:
            self.message_entry.delete(0, "end")
            self.load_messages()
        else:
            self.show_error(data.get("error", "Error al enviar mensaje."))