"""Punto de entrada principal - Intranet Total Capital."""

import base64
from pathlib import Path

import streamlit as st

from config.theme import CUSTOM_CSS, LOGIN_PAGE_CSS
from config.auth import load_credentials, get_user_department, register_user
from modules.admin import admin_ui

st.set_page_config(
    page_title="Total Capital Intranet",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyectar CSS personalizado
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Cargar credenciales y autenticar
config = load_credentials()
if not config:
    st.error(
        "No se encontró credentials.yaml. "
        "Copia config/credentials.yaml.example a config/credentials.yaml y configura los usuarios."
    )
    st.stop()

try:
    import streamlit_authenticator as stauth

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    name = st.session_state.get("name")
    authentication_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")

    if authentication_status is None or authentication_status is False:
        logo_path = Path(__file__).parent / "assets" / "logo.png"

        def _render_branding(logo_path):
            logo_b64 = ""
            if logo_path.exists():
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(
                '<div class="login-branding-box">'
                + (
                    f'<img src="data:image/png;base64,{logo_b64}" alt="Total Capital" class="login-branding-logo"/>'
                    if logo_b64
                    else ""
                )
                + '<h3 class="login-branding-title">Bienvenido a Total Capital</h3>'
                + '<p class="login-branding-subtitle">Intranet de automatización y herramientas internas.</p>'
                + "</div>",
                unsafe_allow_html=True,
            )

        if st.query_params.get("page") == "register":
            st.markdown(LOGIN_PAGE_CSS, unsafe_allow_html=True)
            st.markdown('<div class="login-page">', unsafe_allow_html=True)
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.subheader("Crear cuenta")
                st.markdown(
                    '<p class="login-register-prompt">¿Ya tienes cuenta? <a href="?">Inicia sesión</a></p>',
                    unsafe_allow_html=True,
                )
                with st.form("form_register", clear_on_submit=True):
                    reg_username = st.text_input("Usuario", key="reg_username", placeholder="ej: mi_usuario")
                    reg_password = st.text_input("Contraseña", type="password", key="reg_password", placeholder="Elige una contraseña")
                    reg_name = st.text_input("Nombre (opcional)", key="reg_name", placeholder="Tu nombre")
                    reg_department = st.selectbox(
                        "Departamento",
                        options=["General", "Administración", "RRHH", "Ventas"],
                        key="reg_department",
                    )
                    submitted = st.form_submit_button("Registrarme")
                    if submitted:
                        if reg_username and reg_password:
                            ok, msg = register_user(
                                username=reg_username,
                                password=reg_password,
                                name=reg_name or reg_username,
                                department=reg_department,
                            )
                            if ok:
                                st.success(msg)
                                st.info("Redirigiendo al inicio de sesión…")
                                st.query_params.clear()
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error("Usuario y contraseña son obligatorios.")
            with col_right:
                _render_branding(logo_path)
            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()

        st.markdown(LOGIN_PAGE_CSS, unsafe_allow_html=True)
        st.markdown('<div class="login-page">', unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader("Iniciar sesión")
            authenticator.login("main", key="Iniciar sesión")
            if st.session_state.get("authentication_status") is True:
                st.rerun()
            if authentication_status is False:
                st.error("Usuario o contraseña incorrectos.")
            elif authentication_status is None:
                st.warning("Por favor ingresa tu usuario y contraseña.")
            st.markdown("---")
            st.markdown(
                '<p class="login-register-prompt">¿No tienes cuenta? <a href="?page=register">Regístrate</a></p>',
                unsafe_allow_html=True,
            )
        with col_right:
            _render_branding(logo_path)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # Usuario autenticado
    # Barra lateral - Logo arriba del botón de cerrar sesión
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), width=140)
    authenticator.logout("Cerrar sesión", "sidebar")
    st.sidebar.markdown("---")
    st.sidebar.title("Total Capital")
    st.sidebar.markdown(f"**Hola, {name}**")
    st.sidebar.markdown("---")

    user_dept = get_user_department(username)
    all_depts = ["Administración", "RRHH", "Ventas"]
    # Si el usuario tiene departamento asignado, filtrar opciones (o mostrar solo el suyo)
    dept_options = [user_dept] if user_dept else all_depts
    default_idx = 0
    if user_dept:
        default_idx = all_depts.index(user_dept) if user_dept in all_depts else 0
        dept_options = all_depts  # Permitir ver todos los departamentos

    departamento = st.sidebar.selectbox(
        "Departamento",
        options=all_depts,
        index=default_idx,
        help="Selecciona el departamento para acceder a sus herramientas.",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Intranet de Automatización v1.0")

    # Enrutamiento según departamento seleccionado
    MODULES = {
        "Administración": admin_ui.render,
        "RRHH": lambda: st.info("Módulo RRHH - Próximamente."),
        "Ventas": lambda: st.info("Módulo Ventas - Próximamente."),
    }

    render_fn = MODULES.get(departamento)
    if render_fn:
        render_fn()
    else:
        st.warning("Selecciona un departamento en la barra lateral.")

except Exception as e:
    st.error(f"Error al cargar autenticación: {e}")
    st.info("Verifica que config/credentials.yaml existe y tiene el formato correcto.")
