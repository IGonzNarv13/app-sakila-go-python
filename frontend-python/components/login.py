import streamlit as st
from services.api import post_request


def init_session():
    if "username" not in st.session_state:
        st.session_state.username = ""

    if "connected" not in st.session_state:
        st.session_state.connected = False


def show_login():
    st.set_page_config(
        page_title="Sakila Wiki",
        page_icon="🎬",
        layout="wide"
    )

    st.title("🎬 Sakila Wiki")
    st.subheader("Sistema cliente-servidor para consulta y administración de datos")

    st.write(
        "Inicia sesión para acceder al sistema, consultar información de Sakila "
        "y participar en el chat interno."
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Iniciar sesión")

        username = st.text_input(
            "Nombre de usuario",
            placeholder="Ejemplo: Isaac"
        )

        if st.button("Entrar al sistema", use_container_width=True):
            if username.strip() == "":
                st.warning("Debes escribir un nombre de usuario.")
                return

            status, data = post_request("/api/connect", {
                "username": username.strip()
            })

            if status == 200:
                st.session_state.username = username.strip()
                st.session_state.connected = True
                st.success("Sesión iniciada correctamente.")
                st.rerun()
            else:
                st.error(data.get("error", "No se pudo iniciar sesión."))