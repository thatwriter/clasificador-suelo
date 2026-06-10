"""
Clase Propiedad: Representa una medición físico-química del suelo
Implementa normalización y evaluación de fertilidad
"""

from dataclasses import dataclass
from typing import Optional
from utils.config import VALORES_REFERENCIA, ValorReferencia


@dataclass
class Propiedad:
    """
    Representa una propiedad del suelo (pH, MO, nutrientes, etc.)
    
    Atributos:
        nombre: Identificador de la propiedad (pH, MO, P, etc.)
        valor: Valor medido
        unidad: Unidad de medida
        escala_referencia: Valores de referencia para esta propiedad
    """
    nombre: str
    valor: float
    unidad: str = ""
    escala_referencia: Optional[ValorReferencia] = None
    
    def __post_init__(self):
        """Inicializa la escala de referencia si no se proporcionó"""
        if self.escala_referencia is None and self.nombre in VALORES_REFERENCIA:
            self.escala_referencia = VALORES_REFERENCIA[self.nombre]
            if not self.unidad:
                self.unidad = self.escala_referencia.unidad
    
    def normalizar_valor(self) -> float:
        """
        Calcula el valor normalizado usando razón al óptimo
        Fórmula: x_norm = x_real / x_óptimo
        """
        if self.escala_referencia is None:
            raise ValueError(f"No hay escala de referencia para {self.nombre}")
        return self.valor / self.escala_referencia.optimo
    
    def evaluar_fertilidad(self) -> float:
        """
        Evalúa la contribución a la fertilidad usando función triangular simétrica
        """
        x_norm = self.normalizar_valor()
        if x_norm < 0 or x_norm > 2:
            return 0.0
        elif x_norm <= 1:
            return x_norm
        else:
            return 2 - x_norm
    
    def calcular_desviacion(self) -> float:
        """Desviación respecto al valor óptimo: Δx = x_norm - 1"""
        return self.normalizar_valor() - 1
    
    def esta_en_rango_aceptable(self) -> bool:
        """Verifica si el valor está dentro del rango aceptable [0.5×min, 2.0×max]"""
        if self.escala_referencia is None:
            return True
        return (self.escala_referencia.rango_aceptable_min <= 
                self.valor <= 
                self.escala_referencia.rango_aceptable_max)
    
    def obtener_clasificacion(self) -> str:
        """
        Obtiene la clasificación de calidad según el valor normalizado.
        Prioriza rangos para evitar solapamiento en 1.00 y -1.0/0.
        """
        from utils.config import CLASIFICACIONES
        
        x_norm = self.normalizar_valor()
        
        # Manejo explícito de límites compartidos en la tabla oficial
        if 0.80 <= x_norm <= 1.00:
            return "Muy Alta Calidad"
        if 1.00 < x_norm <= 1.30:
            return "Exceso"
        if -1.0 <= x_norm < 0:
            return "Déficit"
            
        # Fallback para el resto de categorías
        for categoria, (min_val, max_val) in CLASIFICACIONES.items():
            if min_val <= x_norm <= max_val:
                return categoria
        
        return "Fuera de rango"
    
    def __str__(self) -> str:
        return f"{self.nombre}: {self.valor} {self.unidad} (norm: {self.normalizar_valor():.2f})"