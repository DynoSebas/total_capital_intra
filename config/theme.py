"""Colores corporativos y constantes para Total Capital."""

# Colores corporativos (Azul profesional)
PRIMARY_COLOR = "#1E3A5F"
SECONDARY_COLOR = "#2E5A8F"
ACCENT_COLOR = "#4A90D9"
SUCCESS_COLOR = "#28A745"
BACKGROUND_LIGHT = "#F8FAFC"

# CSS personalizado para la aplicación
CUSTOM_CSS = """
<style>
    /* Botones con bordes redondeados y colores corporativos */
    .stButton > button {
        border-radius: 8px !important;
        background-color: #1E3A5F !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #2E5A8F !important;
        color: white !important;
        border: none !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #1E3A5F !important;
    }
</style>
"""
