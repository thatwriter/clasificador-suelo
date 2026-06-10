import pandas as pd
from utils.config import VALORES_REFERENCIA, COLUMNAS_CSV

def generar_plantilla_vacia(filepath="plantilla_muestras.csv") -> str:
    df = pd.DataFrame(columns=COLUMNAS_CSV)
    df.to_csv(filepath, index=False, encoding="utf-8")
    return filepath

def generar_plantilla_optima(filepath="ejemplo_valores_optimos.csv") -> str:
    optima = {col: "" for col in COLUMNAS_CSV}
    optima['id'] = 'OPT-001'
    optima['fecha'] = '2026-05-10'
    for col in COLUMNAS_CSV[2:]:
        if col in VALORES_REFERENCIA:
            optima[col] = VALORES_REFERENCIA[col].optimo
    df = pd.DataFrame([optima])
    df.to_csv(filepath, index=False, encoding="utf-8")
    return filepath