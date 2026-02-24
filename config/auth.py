"""Carga credenciales y configura el autenticador."""

from pathlib import Path

import yaml

CREDENTIALS_PATH = Path(__file__).parent / "credentials.yaml"
CREDENTIALS_EXAMPLE = Path(__file__).parent / "credentials.yaml.example"


def _default_credentials_config() -> dict:
    """Retorna una estructura minima valida para streamlit-authenticator."""
    return {
        "credentials": {"usernames": {}},
        "cookie": {
            "name": "total_capital_cookie",
            "key": "cambia_esta_clave_en_produccion",
            "expiry_days": 30,
        },
        "preauthorized": {"emails": []},
    }


def _ensure_credentials_file() -> tuple[bool, str]:
    """
    Garantiza que exista credentials.yaml para poder guardar nuevos usuarios.
    Si no existe, lo inicializa desde credentials.yaml.example o crea uno minimo.
    """
    if CREDENTIALS_PATH.exists():
        return True, ""

    try:
        if CREDENTIALS_EXAMPLE.exists():
            with open(CREDENTIALS_EXAMPLE, "r", encoding="utf-8") as src:
                config = yaml.safe_load(src) or {}

            if not isinstance(config, dict):
                config = _default_credentials_config()
            else:
                config.setdefault("credentials", {}).setdefault("usernames", {})
                config.setdefault("cookie", _default_credentials_config()["cookie"])
                config.setdefault("preauthorized", {"emails": []})
        else:
            config = _default_credentials_config()

        with open(CREDENTIALS_PATH, "w", encoding="utf-8") as dst:
            yaml.dump(config, dst, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception as e:
        return False, f"No se pudo inicializar config/credentials.yaml: {e}"

    return True, ""


def load_credentials():
    """Carga credenciales desde credentials.yaml o credentials.yaml.example."""
    path = CREDENTIALS_PATH if CREDENTIALS_PATH.exists() else CREDENTIALS_EXAMPLE
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def register_user(
    username: str,
    password: str,
    name: str = "",
    email: str = "",
    department: str = "General",
) -> tuple[bool, str]:
    """
    Registra un nuevo usuario y lo guarda en credentials.yaml.
    Retorna (éxito, mensaje).
    """
    username = (username or "").strip().lower()
    if not username:
        return False, "El usuario no puede estar vacío."
    if not (password or "").strip():
        return False, "La contraseña no puede estar vacía."

    ok, err = _ensure_credentials_file()
    if not ok:
        return False, err

    try:
        import streamlit_authenticator as stauth
    except ImportError:
        return False, "Falta instalar streamlit-authenticator."

    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    if not isinstance(config, dict):
        config = _default_credentials_config()

    usernames = config.get("credentials", {}).get("usernames", {})
    if username in usernames:
        return False, f"El usuario '{username}' ya existe."

    hashed = stauth.Hasher().hash(password.strip())
    name = (name or username).strip() or username
    email = (email or "").strip() or f"{username}@totalcapital.com"

    usernames[username] = {
        "email": email,
        "name": name,
        "password": hashed,
        "department": (department or "General").strip() or "General",
    }
    config.setdefault("credentials", {})["usernames"] = usernames

    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return True, f"Usuario '{username}' registrado. Ya puedes iniciar sesión."


def get_user_department(username: str) -> str | None:
    """Obtiene el departamento asignado a un usuario."""
    config = load_credentials()
    if not config:
        return None
    usernames = config.get("credentials", {}).get("usernames", {})
    user = usernames.get(username, {})
    return user.get("department")
