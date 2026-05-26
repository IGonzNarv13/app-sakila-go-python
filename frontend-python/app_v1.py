import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8080"

st.set_page_config(
    page_title="Cliente Python - Sakila API",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Cliente Python para API Sakila")
st.write("Aplicación cliente desarrollada en Python que consume una API REST hecha en Go.")

# ==========================
# FUNCIONES AUXILIARES
# ==========================

def get_request(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {"error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."}
    except Exception as e:
        return 500, {"error": str(e)}


def post_request(endpoint, data):
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {"error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."}
    except Exception as e:
        return 500, {"error": str(e)}
    
def put_request(endpoint, data):
    try:
        response = requests.put(f"{API_URL}{endpoint}", json=data, timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {"error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."}
    except Exception as e:
        return 500, {"error": str(e)}


def delete_request(endpoint):
    try:
        response = requests.delete(f"{API_URL}{endpoint}", timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {"error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."}
    except Exception as e:
        return 500, {"error": str(e)}


# ==========================
# SESIÓN DE USUARIO
# ==========================

if "username" not in st.session_state:
    st.session_state.username = ""

if "connected" not in st.session_state:
    st.session_state.connected = False


with st.sidebar:
    st.header("Usuario")

    username_input = st.text_input("Nombre de usuario", value=st.session_state.username)

    if st.button("Conectar"):
        if username_input.strip() == "":
            st.warning("Escribe un nombre de usuario.")
        else:
            status, data = post_request("/api/connect", {
                "username": username_input.strip()
            })

            if status == 200:
                st.session_state.username = username_input.strip()
                st.session_state.connected = True
                st.success(data.get("message", "Usuario conectado."))
            else:
                st.error(data.get("error", "Error al conectar usuario."))

    if st.button("Desconectar"):
        if st.session_state.username == "":
            st.warning("No hay usuario conectado.")
        else:
            status, data = post_request("/api/disconnect", {
                "username": st.session_state.username
            })

            if status == 200:
                st.success(data.get("message", "Usuario desconectado."))
                st.session_state.username = ""
                st.session_state.connected = False
            else:
                st.error(data.get("error", "Error al desconectar usuario."))

    st.divider()

    if st.session_state.connected:
        st.success(f"Conectado como: {st.session_state.username}")
    else:
        st.info("Sin conexión de usuario")


# ==========================
# MENÚ PRINCIPAL
# ==========================

menu = st.sidebar.radio(
    "Menú",
    [
        "Inicio",
        "Películas",
        "Buscar película",
        "Actores",
        "Actores Admin",
        "Categorías",
        "Películas por categoría",
        "Usuarios conectados",
        "Mensajes"
    ]
)


# ==========================
# PÁGINA: INICIO
# ==========================

if menu == "Inicio":
    st.header("Inicio")

    st.write("""
    Este cliente consume una API REST creada en Go y conectada a la base de datos Sakila en MySQL.
    """)

    if st.button("Probar conexión con API"):
        status, data = get_request("/api/health")

        if status == 200:
            st.success("Servidor disponible")
            st.json(data)
        else:
            st.error(data.get("error", "Error al conectar con la API"))


# ==========================
# PÁGINA: PELÍCULAS
# ==========================

elif menu == "Películas":
    st.header("Listado de películas")

    status, data = get_request("/api/films")

    if status == 200:
        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No se encontraron películas.")
    else:
        st.error(data.get("error", "Error al obtener películas."))


# ==========================
# PÁGINA: BUSCAR PELÍCULA
# ==========================

elif menu == "Buscar película":
    st.header("Buscar película por título")

    title = st.text_input("Escribe parte del título", placeholder="Ejemplo: academy")

    if st.button("Buscar"):
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


# ==========================
# PÁGINA: ACTORES
# ==========================

elif menu == "Actores":
    st.header("Listado de actores")

    status, data = get_request("/api/actors")

    if status == 200:
        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No se encontraron actores.")
    else:
        st.error(data.get("error", "Error al obtener actores."))

# ==========================
# PÁGINA: ACTORES ADMIN
# ==========================

elif menu == "Actores Admin":
    st.header("Administración de Actores")
    st.write("Desde esta sección puedes crear, consultar, actualizar y eliminar actores usando la API REST en Go.")

    tab_listar, tab_crear, tab_buscar, tab_actualizar, tab_eliminar = st.tabs([
        "Listar",
        "Crear",
        "Buscar por ID",
        "Actualizar",
        "Eliminar"
    ])

    with tab_listar:
        st.subheader("Listado de actores")

        if st.button("Actualizar lista de actores", key="btn_listar_actores_crud"):
            status, data = get_request("/api/actors")

            if status == 200:
                df = pd.DataFrame(data)

                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No se encontraron actores.")
            else:
                st.error(data.get("error", "Error al obtener actores."))

    with tab_crear:
        st.subheader("Crear nuevo actor")

        with st.form("form_crear_actor"):
            first_name = st.text_input("Nombre", placeholder="Ejemplo: Isaac")
            last_name = st.text_input("Apellido", placeholder="Ejemplo: Gonzalez")

            submitted = st.form_submit_button("Crear actor")

            if submitted:
                if first_name.strip() == "" or last_name.strip() == "":
                    st.warning("El nombre y el apellido son obligatorios.")
                else:
                    status, data = post_request("/api/actors", {
                        "first_name": first_name.strip(),
                        "last_name": last_name.strip()
                    })

                    if status == 201:
                        st.success(data.get("message", "Actor creado correctamente."))
                        st.json(data)
                    else:
                        st.error(data.get("error", "Error al crear actor."))

    with tab_buscar:
        st.subheader("Buscar actor por ID")

        actor_id = st.number_input(
            "ID del actor",
            min_value=1,
            step=1,
            key="buscar_actor_id"
        )

        if st.button("Buscar actor", key="btn_buscar_actor"):
            status, data = get_request(f"/api/actors/{actor_id}")

            if status == 200:
                st.success("Actor encontrado.")
                st.json(data)
            else:
                st.error(data.get("error", "Actor no encontrado o error en la consulta."))

    with tab_actualizar:
        st.subheader("Actualizar actor")

        with st.form("form_actualizar_actor"):
            actor_id_update = st.number_input(
                "ID del actor a actualizar",
                min_value=1,
                step=1,
                key="actualizar_actor_id"
            )

            first_name_update = st.text_input("Nuevo nombre", placeholder="Ejemplo: Isaac")
            last_name_update = st.text_input("Nuevo apellido", placeholder="Ejemplo: Aprom")

            submitted_update = st.form_submit_button("Actualizar actor")

            if submitted_update:
                if first_name_update.strip() == "" or last_name_update.strip() == "":
                    st.warning("El nuevo nombre y apellido son obligatorios.")
                else:
                    status, data = put_request(f"/api/actors/{actor_id_update}", {
                        "first_name": first_name_update.strip(),
                        "last_name": last_name_update.strip()
                    })

                    if status == 200:
                        st.success(data.get("message", "Actor actualizado correctamente."))
                        st.json(data)
                    else:
                        st.error(data.get("error", "Error al actualizar actor."))

    with tab_eliminar:
        st.subheader("Eliminar actor")

        st.warning("Esta acción eliminará el actor de la base de datos.")

        actor_id_delete = st.number_input(
            "ID del actor a eliminar",
            min_value=1,
            step=1,
            key="eliminar_actor_id"
        )

        confirmar = st.checkbox("Confirmo que deseo eliminar este actor")

        if st.button("Eliminar actor", key="btn_eliminar_actor"):
            if not confirmar:
                st.warning("Debes confirmar la eliminación antes de continuar.")
            else:
                status, data = delete_request(f"/api/actors/{actor_id_delete}")

                if status == 200:
                    st.success(data.get("message", "Actor eliminado correctamente."))
                    st.json(data)
                else:
                    st.error(data.get("error", "Error al eliminar actor."))


# ==========================
# PÁGINA: CATEGORÍAS
# ==========================

elif menu == "Categorías":
    st.header("Categorías de películas")

    status, data = get_request("/api/categories")

    if status == 200:
        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No se encontraron categorías.")
    else:
        st.error(data.get("error", "Error al obtener categorías."))


# ==========================
# PÁGINA: PELÍCULAS POR CATEGORÍA
# ==========================

elif menu == "Películas por categoría":
    st.header("Buscar películas por categoría")

    status, categories = get_request("/api/categories")

    if status == 200 and len(categories) > 0:
        category_names = [category["name"] for category in categories]

        selected_category = st.selectbox("Selecciona una categoría", category_names)

        if st.button("Consultar películas"):
            status, data = get_request(f"/api/films/category?name={selected_category}")

            if status == 200:
                df = pd.DataFrame(data)

                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No hay películas en esta categoría.")
            else:
                st.error(data.get("error", "Error al buscar películas por categoría."))
    else:
        st.error("No se pudieron cargar las categorías.")


# ==========================
# PÁGINA: USUARIOS CONECTADOS
# ==========================

elif menu == "Usuarios conectados":
    st.header("Usuarios conectados")

    if st.button("Actualizar usuarios"):
        status, data = get_request("/api/users")

        if status == 200:
            df = pd.DataFrame(data)

            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay usuarios conectados.")
        else:
            st.error(data.get("error", "Error al obtener usuarios."))


# ==========================
# PÁGINA: MENSAJES
# ==========================

elif menu == "Mensajes":
    st.header("Mensajes y notificaciones")

    if not st.session_state.connected:
        st.warning("Primero conecta un usuario desde el menú lateral.")
    else:
        message = st.text_area("Escribe un mensaje")

        if st.button("Enviar mensaje"):
            if message.strip() == "":
                st.warning("El mensaje no puede estar vacío.")
            else:
                status, data = post_request("/api/messages", {
                    "username": st.session_state.username,
                    "text": message.strip()
                })

                if status == 201:
                    st.success("Mensaje enviado correctamente.")
                else:
                    st.error(data.get("error", "Error al enviar mensaje."))

    st.subheader("Mensajes recientes")

    if st.button("Actualizar mensajes"):
        status, data = get_request("/api/messages")

        if status == 200:
            if len(data) > 0:
                for msg in data:
                    st.info(f"{msg['sent_at']} - {msg['username']}: {msg['text']}")
            else:
                st.info("Todavía no hay mensajes.")

        else:
            st.error(data.get("error", "Error al obtener mensajes."))

    