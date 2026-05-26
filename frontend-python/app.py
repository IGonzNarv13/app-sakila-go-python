import streamlit as st

from components.login import init_session, show_login
from components.chat import show_chat
from components.home import show_home
from components.films import show_films
from components.actors import show_actors
from components.categories import show_categories
from components.actors_admin import show_actors_admin


init_session()

if not st.session_state.connected:
    show_login()
    st.stop()


st.set_page_config(
    page_title="Sakila Wiki",
    page_icon="🎬",
    layout="wide"
)

show_chat()

st.title("🎬 Sakila Wiki")
st.caption(f"Sesión activa: {st.session_state.username}")

st.write(
    "Aplicación cliente-servidor tipo wiki para consulta de datos, "
    "administración de actores y comunicación entre usuarios."
)

st.divider()

tab_inicio, tab_peliculas, tab_actores, tab_categorias, tab_admin = st.tabs([
    "Inicio",
    "Películas",
    "Actores",
    "Categorías",
    "Admin Actores"
])

with tab_inicio:
    show_home()

with tab_peliculas:
    show_films()

with tab_actores:
    show_actors()

with tab_categorias:
    show_categories()

with tab_admin:
    show_actors_admin()