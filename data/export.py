import pandas as pd
import json
import os
from typing import List
from models.muestra import Muestra
from utils.logger import setup_logger

logger = setup_logger()

class ExportadorResultados:
    def __init__(self, dir_salida="resultados"):
        self.dir_salida = dir_salida
        os.makedirs(dir_salida, exist_ok=True)

    def _df_resultados(self, muestras: List[Muestra]) -> pd.DataFrame:
        filas = []
        for m in muestras:
            fila = {
                'id': m.id, 'fecha': m.fecha_toma.strftime("%Y-%m-%d"),
                'nivel_fertilidad': m.obtener_nivel_fertilidad(),
                'calidad_acumulada': round(m.calcular_calidad_acumulada(), 4),
                'distancia_euclidiana': round(m.calcular_distancia_euclidiana(), 4),
                'distancia_manhattan': round(m.calcular_distancia_manhattan(), 4)
            }
            for p in m.propiedades:
                fila[f'{p.nombre}_norm'] = round(p.normalizar_valor(), 4)
                fila[f'{p.nombre}_fertilidad'] = round(p.evaluar_fertilidad(), 4)
                fila[f'{p.nombre}_clasif'] = p.obtener_clasificacion()
            filas.append(fila)
        return pd.DataFrame(filas)

    def a_csv(self, muestras: List[Muestra], nombre="resultados.csv") -> str:
        ruta = os.path.join(self.dir_salida, nombre)
        self._df_resultados(muestras).to_csv(ruta, index=False, encoding="utf-8")
        logger.info(f" Exportado CSV: {ruta}")
        return ruta

    def a_json(self, muestras: List[Muestra], nombre="resultados.json") -> str:
        ruta = os.path.join(self.dir_salida, nombre)
        datos = [{
            "id": m.id, "fecha": m.fecha_toma.isoformat(),
            "nivel": m.obtener_nivel_fertilidad(),
            "calidad": m.calcular_calidad_acumulada(),
            "estadisticas": m.calcular_estadisticas(),
            "propiedades": [{
                "nombre": p.nombre, "real": p.valor,
                "norm": p.normalizar_valor(), "fert": p.evaluar_fertilidad(),
                "clasif": p.obtener_clasificacion()
            } for p in m.propiedades]
        } for m in muestras]
        with open(ruta, 'w', encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Exportado JSON: {ruta}")
        return ruta

    def a_txt(self, muestras: List[Muestra], nombre="reporte_tecnico.txt") -> str:
        ruta = os.path.join(self.dir_salida, nombre)
        with open(ruta, 'w', encoding="utf-8") as f:
            f.write("REPORTE TÉCNICO - SUELO INTELIGENTE\n" + "="*50 + "\n\n")
            for m in muestras:
                f.write(f"MUESTRA: {m.id} | {m.fecha_toma.strftime('%Y-%m-%d')}\n")
                f.write(f"NIVEL: {m.obtener_nivel_fertilidad()} | CALIDAD: {m.calcular_calidad_acumulada():.2f}\n")
                for p in m.propiedades:
                    f.write(f"  {p.nombre}: {p.valor} {p.unidad} → Norm: {p.normalizar_valor():.2f} | Fert: {p.evaluar_fertilidad():.2f} [{p.obtener_clasificacion()}]\n")
                f.write("-" * 50 + "\n")
        logger.info(f"💾 Exportado TXT: {ruta}")
        return ruta
    