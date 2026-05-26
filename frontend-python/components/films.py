import streamlit as st
import pandas as pd
from services.api import get_request


def show_films():
    st.header("Películas")

    tab_listado, tab_busqueda = st.tabs([
        "Listado",
        "Buscar por título"
    ])

    with tab_listado:
        st.subheader("Listado de películas")

        status, data = get_request("/api/films")

        if status == 200:
            df = pd.DataFrame(data)

            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se encontraron películas.")
        else:
            st.error(data.get("error", "Error al obtener películas."))

    with tab_busqueda:
        st.subheader("Buscar película por título")

        title = st.text_input(
            "Escribe parte del título",
            placeholder="Ejemplo: academy"
        )

        if st.button("Buscar película"):
            if title.strip() == "":
                st.warning("Escribe un título para buscar.")
            else:
                status, data = get_request(f"/api/films/search?title={title.strip()}")

                if status == 200:
                    df = pd.DataFrame(data)

                    if not df.empty:
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No se encontraron resultados.")
                else:
                    st.error(data.get("error", "Error al buscar película."))