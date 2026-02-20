"""Lógica de procesamiento para el módulo de Administración."""

import re
import pandas as pd

# Constantes por banco
BANCO_VE_POR_MAS = "ve_por_mas"
BANCO_VE_POR_MAS_HEADER_ROW = 9  # Los nombres de columnas están en la línea 10 (índice 9)


def process_ve_por_mas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa CSV del Banco VE POR MAS.
    - Headers en fila 10
    - Output: FECHA, CONCEPTO (extraído de DESCRIPCIÓN, solo lo que está después de "CONCEPTO:")
    """
    if df.empty:
        return pd.DataFrame(columns=["FECHA", "CONCEPTO"])

    # Detectar columna FECHA (mismo nombre en el CSV)
    fecha_col = None
    for col in df.columns:
        if str(col).strip().upper() == "FECHA":
            fecha_col = col
            break
    if fecha_col is None:
        raise ValueError("No se encontró la columna FECHA en el CSV.")

    # Detectar columna DESCRIPCIÓN
    desc_col = None
    for col in df.columns:
        if "descripci" in str(col).lower() or "descripcion" in str(col).lower():
            desc_col = col
            break
    if desc_col is None:
        raise ValueError("No se encontró la columna DESCRIPCIÓN en el CSV.")

    # Extraer CONCEPTO: texto después de "CONCEPTO:" hasta el siguiente " PALABRA:" o " PALABRA PALABRA:"
    # Ej: "CONCEPTO: IMPACTA REFERENCIA: 1 BENEFICIARIO: ..." -> solo "IMPACTA"
    # Split por el patrón " PALABRA:" (espacio + palabra + dos puntos)
    _FIELD_PATTERN = re.compile(r"\s+[A-Za-z0-9_]+(?:\s+[A-Za-z0-9_]+)*\s*:")

    def extract_concepto(text):
        if pd.isna(text):
            return ""
        text = str(text).strip()
        idx = text.upper().find("CONCEPTO:")
        if idx < 0:
            return text
        after = text[idx + 9 :].strip()  # después de "CONCEPTO:"
        parts = _FIELD_PATTERN.split(after)
        return parts[0].strip() if parts else after

    result = pd.DataFrame()
    result["FECHA"] = df[fecha_col]
    result["CONCEPTO"] = df[desc_col].apply(extract_concepto)

    # Quitar filas vacías
    result = result.dropna(subset=["FECHA"], how="all")
    result = result.replace(r"^\s*$", pd.NA, regex=True)
    result = result.dropna(how="all")

    return result


def process_bank_csv(df: pd.DataFrame, bank: str) -> pd.DataFrame:
    """
    Procesa CSV según el banco seleccionado.
    """
    if bank == BANCO_VE_POR_MAS:
        return process_ve_por_mas(df)
    raise ValueError(f"Banco no soportado: {bank}")
