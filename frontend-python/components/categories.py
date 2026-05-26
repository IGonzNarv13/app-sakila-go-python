import streamlit as st
import pandas as pd
from services.api import get_request


def show_categories():
    st.header("Categorías")

    tab_categorias, tab_peliculas_categoria = st.tabs([
        "Listado de categorías",
        "Películas por categoría"
    ])

    with tab_categorias:
        st.subheader("Categorías disponibles")

        status, data = get_request("/api/categories")

        if status == 200:
            df = pd.DataFrame(data)

            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No se encontraron categorías.")
        else:
            st.error(data.get("error", "Error al obtener categorías."))

    with tab_peliculas_categoria:
        st.subheader("Consultar películas por categoría")

        status, categories = get_request("/api/categories")

        if status == 200 and len(categories) > 0:
            category_names = [category["name"] for category in categories]

            selected_category = st.selectbox(
                "Selecciona una categoría",
                category_names
            )

            if st.button("Consultar películas"):
                status, data = get_request(
                    f"/api/films/category?name={selected_category}"
                )

                if status == 200:
                    df = pd.DataFrame(data)

                    if not df.empty:
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No hay películas en esta categoría.")
                else:
                    st.error(
                        data.get("error", "Error al buscar películas por categoría.")
                    )
        else:
            st.error("No se pudieron cargar las categorías.")