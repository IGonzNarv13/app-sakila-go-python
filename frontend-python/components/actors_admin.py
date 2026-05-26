import streamlit as st
import pandas as pd
from services.api import get_request, post_request, put_request, delete_request


def show_actors_admin():
    st.header("Administración de actores")
    st.write(
        "Desde esta sección puedes crear, consultar, actualizar y eliminar "
        "actores usando la API REST en Go."
    )

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
                st.error(
                    data.get("error", "Actor no encontrado o error en la consulta.")
                )

    with tab_actualizar:
        st.subheader("Actualizar actor")

        with st.form("form_actualizar_actor"):
            actor_id_update = st.number_input(
                "ID del actor a actualizar",
                min_value=1,
                step=1,
                key="actualizar_actor_id"
            )

            first_name_update = st.text_input(
                "Nuevo nombre",
                placeholder="Ejemplo: Isaac"
            )
            last_name_update = st.text_input(
                "Nuevo apellido",
                placeholder="Ejemplo: Aprom"
            )

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
                        st.success(
                            data.get("message", "Actor actualizado correctamente.")
                        )
                        st.json(data)
                    else:
                        st.error(data.get("error", "Error al actualizar actor."))

    with tab_eliminar:
        st.subheader("Eliminar actor")

        st.warning(
            "Esta acción eliminará el actor de la base de datos. "
            "Si tiene relaciones con películas, la API eliminará primero esas relaciones."
        )

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