import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Tuple
from models.propiedad import Propiedad
from models.muestra import Muestra
from utils.config import VALORES_REFERENCIA, COLUMNAS_CSV
from utils.logger import setup_logger

logger = setup_logger()

class CargadorDatos:
    def __init__(self):
        self.alertas = []

    def cargar_csv(self, filepath: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath, dtype=str)
            logger.info(f"✅ CSV cargado: {filepath} ({len(df)} registros)")
            return df
        except Exception as e:
            logger.error(f"❌ Error al leer CSV: {e}")
            raise ValueError(f"Archivo inválido: {e}")

    def validar_y_limpiar(self, df: pd.DataFrame, modo: str = "individual") -> Tuple[pd.DataFrame, List[str]]:
        self.alertas = []
        df_clean = df.copy()

        # 1. Verificar columnas obligatorias
        if 'id' not in df_clean.columns:
            df_clean['id'] = "AUTO-" + df_clean.index.astype(str)
            self.alertas.append(" ID asignado automáticamente.")
        if 'fecha' not in df_clean.columns:
            df_clean['fecha'] = datetime.now().strftime("%Y-%m-%d")
            self.alertas.append(" Fecha actual asignada.")

        # 2. Conversión numérica segura
        cols_numericas = [c for c in COLUMNAS_CSV[2:] if c in df_clean.columns]
        for col in cols_numericas:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        # 3. Validación de rangos y detección de extremos
        for idx in df_clean.index:
            for col in cols_numericas:
                val = df_clean.at[idx, col]
                if pd.isna(val):
                    continue
                ref = VALORES_REFERENCIA.get(col)
                if ref:
                    limite_inf = ref.minimo * 0.5
                    limite_sup = ref.maximo * 2.0
                    if val < limite_inf or val > limite_sup:
                        msg = f"⚠️ Fila {idx} | {col}: {val} fuera de rango [{limite_inf:.2f}, {limite_sup:.2f}]. Se descarta."
                        self.alertas.append(msg)
                        df_clean.at[idx, col] = np.nan

        # 4. Manejo de valores faltantes según modo
        if modo == "individual":
            # Se operará solo con columnas presentes (las NaN se filtran en los cálculos)
            pass
        elif modo == "grupo":
            group_col = 'id' if 'id' in df_clean.columns else None
            if group_col and df_clean[group_col].nunique() > 1:
                df_clean[cols_numericas] = df_clean.groupby(group_col)[cols_numericas].transform(
                    lambda x: x.fillna(x.mean())
                )
            else:
                df_clean[cols_numericas] = df_clean[cols_numericas].fillna(df_clean[cols_numericas].mean())
            self.alertas.append("📊 Valores faltantes imputados con media grupal.")

        # 5. Filtrar filas sin datos numéricos válidos
        df_valido = df_clean.dropna(subset=cols_numericas, how='all').reset_index(drop=True)
        if len(df_valido) < len(df_clean):
            self.alertas.append(f"🗑️ {len(df_clean) - len(df_valido)} registros eliminados por falta de datos.")
            
        logger.info(f"✅ Validación completada. {len(df_valido)} registros listos.")
        return df_valido, self.alertas

    def convertir_a_muestras(self, df: pd.DataFrame) -> List[Muestra]:
        muestras = []
        cols_numericas = [c for c in COLUMNAS_CSV[2:] if c in df.columns]
        
        for _, row in df.iterrows():
            m = Muestra(
                id=str(row['id']),
                fecha_toma=datetime.strptime(str(row['fecha']), "%Y-%m-%d"),
                ubicacion=str(row.get('ubicacion', ''))
            )
            for col in cols_numericas:
                val = row[col]
                if pd.notna(val):
                    m.agregar_propiedad(Propiedad(nombre=col, valor=float(val)))
            if m.propiedades:
                muestras.append(m)
                
        logger.info(f"✅ {len(muestras)} objetos Muestra creados.")
        return muestras