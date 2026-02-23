"""Lógica de procesamiento para el módulo de Administración."""

import re
import pandas as pd

# Constantes por banco
BANCO_VE_POR_MAS = "ve_por_mas"
BANCO_VE_POR_MAS_HEADER_ROW = 9  # Los nombres de columnas están en la línea 10 (índice 9)

#diccionario con id y tags
tags = {
    "00000368682":"DGE USD",
    "00000712825":"DGE MXN",
    "00000469012":"BSI USD",
    "00000712804":"BSI MXN",
    "00000391197":"DGP USD",
    "00000712791":"DGP MXN",
    "00000642340":"SVC USD",
    "00000712833":"SVC MXN",
    "25600585353":"BSI MXN SC",
    "25601044520":"BSI MXN SC 2",
    "95600019492":"BSI USD SC",
    "95600993391":"BSI USD SC 2",
    "0124988817" : "DGP BBVA"

}

def process_ve_por_mas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa CSV del Banco VE POR MAS.
    - Headers en fila 10
    - Output: FECHA, CONCEPTO (extraído de DESCRIPCIÓN, solo lo que está después de "CONCEPTO:")
    """
    if df.empty:
        return pd.DataFrame(columns=["FECHA", "CONCEPTO", "MONTO"])

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

    #detectar las columnas de retiros y depositos    
    retiros_col = None
    deposito_col = None
    for col in df.columns:
        col_lowe = str(col).lower()
        if "retiros" in col_lowe:
            retiros_col = col
        if "depósitos" in col_lowe:
            deposito_col = col
    if retiros_col is None or deposito_col is None:  #validación en caso de que no se encuentren las columnas 
        raise ValueError("No se encontraron las columnas RETIROS o DEPOSITOS en el CSV.")

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
            #si no encontro concepto busca traspaso o recepcion
            idx_traspaso = text.upper().find("TRASPASO")
            idx_recepcion = text.upper().find("RECEPCION")

            if idx_traspaso >= 0 or idx_recepcion >= 0:  
                #si alguna de las dos existe buscamos recepcion primero por que en las 
                #de recepcion tambien se encuentra la palabra traspaso
                if idx_recepcion >= 0: 
                    operacion = "RECEPCION"
                else:
                    operacion = "TRASPASO"

                parts = text.split()  
                id_banco = parts[-1]

                tag_final = tags.get(id_banco, id_banco)
                return f"{operacion} {tag_final}"  #regresamos la operacion con el tag 
        after = text[idx + 9 :].strip()  # después de "CONCEPTO:"
        parts = _FIELD_PATTERN.split(after)
        return parts[0].strip() if parts else after

    result = pd.DataFrame()
    result["FECHA"] = df[fecha_col]
    result["CONCEPTO"] = df[desc_col].apply(extract_concepto)
    

    #funcion para obtner el monto de la transacción
    def obtener_monto_transaccion(row): 
        #Obtener valores de las columnas de retiros y depositos
        retiro = row[retiros_col]       
        deposito = row[deposito_col]
        
        #devolver el valor de la columna retiro o deposito 
        if pd.notna(retiro) and str(retiro).strip() != "":
            return retiro
        if pd.notna(deposito) and str(deposito).strip() != "":
            return deposito
            
        return pd.NA

    result["MONTO"] = df.apply(obtener_monto_transaccion, axis=1)

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
