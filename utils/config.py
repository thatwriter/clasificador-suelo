"""
Configuración global del sistema Suelo Inteligente
Valores de referencia, rangos óptimos y parámetros del sistema
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class ValorReferencia:
    """Valores mínimo y máximo de referencia para cada indicador"""
    nombre: str
    unidad: str
    minimo: float
    maximo: float
    
    @property
    def optimo(self) -> float:
        """Valor óptimo = máximo de referencia"""
        return self.maximo
    
    @property
    def rango_aceptable_min(self) -> float:
        """Límite inferior aceptable: mitad del mínimo"""
        return self.minimo * 0.5
    
    @property
    def rango_aceptable_max(self) -> float:
        """Límite superior aceptable: doble del máximo"""
        return self.maximo * 2.0


# Tabla de valores de referencia (basado en PP.pdf)
VALORES_REFERENCIA: Dict[str, ValorReferencia] = {
    'pH': ValorReferencia('pH (H2O)', '', 5.0, 7.5),
    'MO': ValorReferencia('Materia Orgánica', '%', 2.0, 6.0),
    'P': ValorReferencia('Fósforo Olsen', 'ppm', 8.0, 20.0),
    'Ca': ValorReferencia('Calcio', 'cmol kg-1', 8.0, 35.0),
    'Mg': ValorReferencia('Magnesio', 'cmol kg-1', 2.0, 5.0),
    'K': ValorReferencia('Potasio', 'cmol kg-1', 0.2, 1.0),
    'CICE': ValorReferencia('CICE', 'cmol kg-1', 15.0, 40.0),
    'C_BM': ValorReferencia('Carbono Biomasa Microbiana', 'mg kg-1', 10.0, 400.0),
}

# Clasificaciones de calidad (basado en tabla del PP.pdf)
CLASIFICACIONES = {
    'Exceso': (1.00, 1.30),
    'Muy Alta Calidad': (0.80, 1.00),
    'Alta Calidad': (0.60, 0.79),
    'Moderada Calidad': (0.40, 0.59),
    'Baja Calidad': (0.20, 0.39),
    'Muy Baja Calidad': (0.0, 0.19),
    'Déficit': (-1.0, 0.0),
}

# Mapeo de columnas CSV esperadas
COLUMNAS_CSV = ['id', 'fecha', 'pH', 'MO', 'P', 'Ca', 'Mg', 'K', 'CICE', 'C_BM']

# Parámetros del sistema
K_BETA = 5  # Factor de concentración para distribución Beta (NO USADO por ahora)
PRECISION_DECIMALES = 2