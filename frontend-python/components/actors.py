import streamlit as st
import pandas as pd
from services.api import get_request


def show_actors():
    st.header("Actores")

    status, data = get_request("/api/actors")

    if status == 200:
        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No se encontraron actores.")
    else:
        st.error(data.get("error", "Error al obtener actores."))