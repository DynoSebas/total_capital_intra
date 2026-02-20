"""Conexión y operaciones con SharePoint."""

import os
from typing import Optional

try:
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.user_credential import UserCredential
    SHAREPOINT_AVAILABLE = True
except ImportError:
    SHAREPOINT_AVAILABLE = False


def _get_credentials():
    """Obtiene credenciales desde st.secrets o variables de entorno."""
    try:
        import streamlit as st
        secrets = st.secrets.get("sharepoint", {})
        return {
            "site_url": secrets.get("site_url") or os.getenv("SHAREPOINT_SITE_URL"),
            "username": secrets.get("username") or os.getenv("SHAREPOINT_USERNAME"),
            "password": secrets.get("password") or os.getenv("SHAREPOINT_PASSWORD"),
        }
    except (ImportError, FileNotFoundError):
        return {
            "site_url": os.getenv("SHAREPOINT_SITE_URL"),
            "username": os.getenv("SHAREPOINT_USERNAME"),
            "password": os.getenv("SHAREPOINT_PASSWORD"),
        }


class SharePointClient:
    """Cliente para autenticar y operar con SharePoint."""

    def __init__(
        self,
        site_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        creds = _get_credentials()
        self.site_url = site_url or creds["site_url"]
        self.username = username or creds["username"]
        self.password = password or creds["password"]
        self.ctx: Optional[ClientContext] = None

    def authenticate(self) -> bool:
        """Autentica con SharePoint usando credenciales de usuario."""
        if not SHAREPOINT_AVAILABLE:
            raise ImportError(
                "Office365-REST-Python-Client no está instalado. "
                "Ejecuta: pip install Office365-REST-Python-Client"
            )
        if not all([self.site_url, self.username, self.password]):
            raise ValueError(
                "Faltan credenciales de SharePoint. "
                "Configura SHAREPOINT_SITE_URL, SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD "
                "en .streamlit/secrets.toml o variables de entorno."
            )
        try:
            credentials = UserCredential(self.username, self.password)
            self.ctx = ClientContext(self.site_url).with_credentials(credentials)
            # Verificar conexión
            web = self.ctx.web
            self.ctx.load(web)
            self.ctx.execute_query()
            return True
        except Exception as e:
            raise ConnectionError(f"Error al conectar con SharePoint: {e}") from e

    def list_files(self, folder_path: str = "/") -> list[dict]:
        """Lista archivos en una carpeta de SharePoint."""
        if self.ctx is None:
            self.authenticate()

        folder = self.ctx.web.get_folder_by_server_relative_url(folder_path)
        files = folder.files
        self.ctx.load(files)
        self.ctx.execute_query()

        return [
            {"name": f.properties.get("Name"), "size": f.properties.get("Length")}
            for f in files
        ]

    def download_file(self, server_path: str, local_path: str) -> None:
        """Descarga un archivo de SharePoint."""
        if self.ctx is None:
            self.authenticate()

        with open(local_path, "wb") as f:
            file = self.ctx.web.get_file_by_server_relative_url(server_path)
            file.download(f)
            self.ctx.execute_query()
