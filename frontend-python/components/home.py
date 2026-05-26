import streamlit as st
from services.api import get_request


def show_home():
    st.header("Inicio")

    st.write("""
    Bienvenido al sistema **Sakila Wiki**, una aplicación cliente-servidor
    desarrollada con Go, Python y MySQL.
    """)

    st.markdown("### Funciones principales")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Consulta de películas, actores y categorías desde Sakila.")

    with col2:
        st.info("Administración de actores mediante operaciones CRUD.")

    with col3:
        st.info("Chat interno para interacción entre usuarios conectados.")

    st.divider()

    if st.button("Probar conexión con la API"):
        status, data = get_request("/api/health")

        if status == 200:
            st.success("Servidor Go disponible.")
            st.json(data)
        else:
            st.error(data.get("error", "Error al conectar con la API."))