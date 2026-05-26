import html
import streamlit as st
from services.api import get_request, post_request


def init_chat_state():
    if "sidebar_view" not in st.session_state:
        st.session_state.sidebar_view = "users"

    if "chat_type" not in st.session_state:
        st.session_state.chat_type = "group"

    if "chat_target" not in st.session_state:
        st.session_state.chat_target = "general"


def render_chat_styles():
    st.markdown(
        """
<style>
.chat-title {
    font-size: 1.10rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.chat-subtitle {
    font-size: 0.83rem;
    color: #6c757d;
    margin-bottom: 14px;
}

.user-card {
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 8px;
    background-color: #ffffff;
}

.user-name {
    font-weight: 700;
    color: #212529;
    font-size: 0.92rem;
}

.user-date {
    font-size: 0.72rem;
    color: #6c757d;
}

.message-row {
    display: flex;
    width: 100%;
    margin-bottom: 10px;
}

.message-row-own {
    justify-content: flex-end;
}

.message-row-received {
    justify-content: flex-start;
}

.message-row-system {
    justify-content: center;
}

.message-bubble {
    max-width: 88%;
    padding: 10px 12px;
    border-radius: 12px;
    font-size: 0.9rem;
    line-height: 1.35;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.message-own {
    background-color: #d8f3dc;
    color: #1b4332;
    border-bottom-right-radius: 4px;
}

.message-received {
    background-color: #f1f3f5;
    color: #212529;
    border-bottom-left-radius: 4px;
}

.message-system {
    background-color: #dbeafe;
    color: #1e3a8a;
    text-align: center;
    font-size: 0.82rem;
    max-width: 92%;
    border-radius: 999px;
}

.message-author {
    font-weight: 700;
    font-size: 0.82rem;
    margin-bottom: 4px;
    color: #343a40;
}

.message-text {
    margin-bottom: 6px;
    white-space: pre-wrap;
}

.message-date {
    font-size: 0.72rem;
    opacity: 0.72;
}

.message-own .message-date {
    text-align: right;
}

.message-received .message-date {
    text-align: left;
}
</style>
        """,
        unsafe_allow_html=True
    )


def open_group_chat():
    st.session_state.sidebar_view = "chat"
    st.session_state.chat_type = "group"
    st.session_state.chat_target = "general"
    st.rerun()


def open_private_chat(username):
    st.session_state.sidebar_view = "chat"
    st.session_state.chat_type = "private"
    st.session_state.chat_target = username
    st.rerun()


def back_to_users():
    st.session_state.sidebar_view = "users"
    st.rerun()


def render_message(msg, current_user):
    sender = html.escape(str(msg.get("from", "")))
    text = html.escape(str(msg.get("text", "")))
    sent_at = html.escape(str(msg.get("sent_at", "")))
    msg_type = msg.get("type", "")

    if msg_type == "system" or sender == "Sistema":
        st.markdown(
            f'<div class="message-row message-row-system">'
            f'<div class="message-bubble message-system">{text}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        return

    if sender == current_user:
        st.markdown(
            f'<div class="message-row message-row-own">'
            f'<div class="message-bubble message-own">'
            f'<div class="message-text">{text}</div>'
            f'<div class="message-date">{sent_at}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(
        f'<div class="message-row message-row-received">'
        f'<div class="message-bubble message-received">'
        f'<div class="message-author">{sender}</div>'
        f'<div class="message-text">{text}</div>'
        f'<div class="message-date">{sent_at}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def show_users_panel():
    st.markdown('<div class="chat-title">Comunicación</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="chat-subtitle">Usuario conectado: {html.escape(st.session_state.username)}</div>',
        unsafe_allow_html=True
    )

    if st.button("Chat grupal", use_container_width=True):
        open_group_chat()

    st.divider()

    st.markdown("Usuarios conectados")

    status, users = get_request("/api/users")

    if status == 200:
        other_users = [
            user for user in users
            if user.get("username") != st.session_state.username
        ]

        if len(other_users) == 0:
            st.info("No hay otros usuarios conectados.")
        else:
            for user in other_users:
                username = user.get("username", "")
                connected_at = user.get("connected_at", "")

                st.markdown(
                    f'<div class="user-card">'
                    f'<div class="user-name">{html.escape(username)}</div>'
                    f'<div class="user-date">Conectado desde: {html.escape(connected_at)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    f"Chatear con {username}",
                    key=f"chat_user_{username}",
                    use_container_width=True
                ):
                    open_private_chat(username)
    else:
        st.error(users.get("error", "Error al obtener usuarios."))

    st.divider()

    if st.button("Actualizar usuarios", use_container_width=True):
        st.rerun()

    if st.button("Cerrar sesión", use_container_width=True):
        post_request("/api/disconnect", {
            "username": st.session_state.username
        })

        st.session_state.username = ""
        st.session_state.connected = False
        st.session_state.sidebar_view = "users"
        st.rerun()


def get_chat_title():
    if st.session_state.chat_type == "group":
        return "Chat grupal"

    return f"Chat con {st.session_state.chat_target}"


def get_messages_for_current_chat():
    if st.session_state.chat_type == "group":
        return get_request("/api/messages?type=group")

    current_user = st.session_state.username
    target = st.session_state.chat_target

    return get_request(
        f"/api/messages?type=private&user1={current_user}&user2={target}"
    )


def send_current_message(text):
    if st.session_state.chat_type == "group":
        return post_request("/api/messages", {
            "from": st.session_state.username,
            "to": "general",
            "text": text,
            "type": "group"
        })

    return post_request("/api/messages", {
        "from": st.session_state.username,
        "to": st.session_state.chat_target,
        "text": text,
        "type": "private"
    })


def show_chat_panel():
    if st.button("Volver atrás", use_container_width=True):
        back_to_users()

    st.markdown(
        f'<div class="chat-title">{html.escape(get_chat_title())}</div>',
        unsafe_allow_html=True
    )

    if st.button("Actualizar chat", use_container_width=True):
        st.rerun()

    st.divider()

    status, messages = get_messages_for_current_chat()

    if status == 200:
        if len(messages) > 0:
            recent_messages = messages[-20:]

            for msg in recent_messages:
                render_message(msg, st.session_state.username)
        else:
            st.info("Todavía no hay mensajes en este chat.")
    else:
        st.error(messages.get("error", "Error al cargar mensajes."))

    st.divider()

    new_message = st.text_area(
        "Mensaje",
        placeholder="Escribe un mensaje..."
    )

    if st.button("Enviar mensaje", use_container_width=True):
        if new_message.strip() == "":
            st.warning("El mensaje no puede estar vacío.")
        else:
            status, data = send_current_message(new_message.strip())

            if status == 201:
                st.success("Mensaje enviado.")
                st.rerun()
            else:
                st.error(data.get("error", "Error al enviar mensaje."))


def show_chat():
    init_chat_state()
    render_chat_styles()

    with st.sidebar:
        if st.session_state.sidebar_view == "users":
            show_users_panel()
        else:
            show_chat_panel()