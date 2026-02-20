"""Carga credenciales y configura el autenticador."""

import os
from pathlib import Path

import yaml

CREDENTIALS_PATH = Path(__file__).parent / "credentials.yaml"
CREDENTIALS_EXAMPLE = Path(__file__).parent / "credentials.yaml.example"


def load_credentials():
    """Carga credenciales desde credentials.yaml o credentials.yaml.example."""
    path = CREDENTIALS_PATH if CREDENTIALS_PATH.exists() else CREDENTIALS_EXAMPLE
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_user_department(username: str) -> str | None:
    """Obtiene el departamento asignado a un usuario."""
    config = load_credentials()
    if not config:
        return None
    usernames = config.get("credentials", {}).get("usernames", {})
    user = usernames.get(username, {})
    return user.get("department")
