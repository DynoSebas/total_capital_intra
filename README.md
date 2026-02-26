# Total Capital - Intranet de Automatización

Aplicación web interna con Streamlit para centralizar herramientas de automatización por departamento (Administración, RRHH, Ventas).

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Login y credenciales de usuarios

La app usa `streamlit-authenticator` con credenciales en un archivo YAML.

1. Copia `config/credentials.yaml.example` a `config/credentials.yaml`
2. Genera hashes para las contraseñas:
   ```bash
   python scripts/generate_password_hash.py TU_CONTRASEÑA
   ```
3. Sustituye los placeholders en `credentials.yaml` por los hashes generados
4. Añade usuarios con su `department` (Administración, RRHH, Ventas)

**Usuarios de prueba** (si usas `credentials.yaml` de ejemplo): `admin1`, `rrhh1`, `ventas1` con contraseña `demo123`

**Nunca subas `config/credentials.yaml` a Git.**

## Configuración de credenciales SharePoint

Para usar la conexión a SharePoint:

1. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`
2. Completa los valores de `site_url`, `username` y `password`
3. O bien define las variables de entorno: `SHAREPOINT_SITE_URL`, `SHAREPOINT_USERNAME`, `SHAREPOINT_PASSWORD`

**Nunca subas `secrets.toml` a Git.**

## Ejecución

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

## Estructura del proyecto

```
├── app.py                 # Punto de entrada
├── assets/                 # Logo para la página de login (logo.png)
├── config/
│   ├── theme.py           # Colores corporativos y CSS
│   ├── auth.py            # Carga de credenciales
│   ├── credentials.yaml.example
│   └── credentials.yaml   # (gitignore) Credenciales de usuarios
├── scripts/
│   └── generate_password_hash.py  # Utilidad para hashear contraseñas
├── modules/
│   ├── admin/             # Módulo Administración
│   │   ├── admin_logic.py # Procesamiento CSV
│   │   └── admin_ui.py    # Interfaz
│   └── shared/
│       └── sharepoint.py  # Cliente SharePoint
└── requirements.txt
```

## Módulo Administración

- Sube un CSV de estado de cuenta bancario
- Procesa: elimina filas vacías, convierte fechas, agrupa por concepto
- Descarga el resultado en formato Excel (.xlsx)

El CSV debe tener columnas como: fecha, concepto, monto (o equivalentes en inglés: date, concept, amount).

## Añadir nuevos departamentos

1. Crear carpeta `modules/{departamento}/`
2. Añadir `{departamento}_logic.py` y `{departamento}_ui.py`
3. Registrar en `app.py` en el diccionario `MODULES`

## Despliegue

Recomendado: [Streamlit Community Cloud](https://share.streamlit.io/) o Railway/Render.

En Streamlit Cloud, configura los secrets en "Advanced settings" durante el despliegue.
