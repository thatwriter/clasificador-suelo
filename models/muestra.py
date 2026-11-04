<<<<<<< HEAD
"""
Clase Muestra: Representa una muestra de suelo con múltiples propiedades
Implementa cálculo de fertilidad acumulada y métricas estadísticas
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
from models.propiedad import Propiedad


@dataclass
class Muestra:
    """
    Representa una muestra de suelo con sus propiedades
    
    Atributos:
        id: Identificador único de la muestra
        fecha_toma: Fecha de recolección
        ubicacion: Ubicación geográfica (opcional)
        propiedades: Lista de propiedades del suelo
    """
    id: str
    fecha_toma: datetime
    ubicacion: str = ""
    propiedades: List[Propiedad] = field(default_factory=list)
    
    def agregar_propiedad(self, propiedad: Propiedad):
        """Agrega una propiedad a la muestra"""
        self.propiedades.append(propiedad)
    
    def obtener_propiedad(self, nombre: str) -> Optional[Propiedad]:
        """Obtiene una propiedad por su nombre"""
        for prop in self.propiedades:
            if prop.nombre == nombre:
                return prop
        return None
    
    def calcular_calidad_acumulada(self) -> float:
        """
        Calcula la calidad acumulada del suelo
        
        Fórmula: F̄ = (1/n) Σ f(x_i)
        donde f(x_i) es la evaluación de fertilidad de cada propiedad
        
        Retorna:
            float: Calidad promedio en [0, 1]
        """
        if not self.propiedades:
            return 0.0
        
        # Filtrar propiedades con valores válidos
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if not propiedades_validas:
            return 0.0
        
        fertilidades = [p.evaluar_fertilidad() for p in propiedades_validas]
        return sum(fertilidades) / len(fertilidades)
    
    def calcular_distancia_euclidiana(self) -> float:
        """
        Calcula la distancia euclidiana al vector óptimo (1,1,...,1)
        
        Fórmula: d₂ = √Σ(x_i - 1)²
        
        Retorna:
            float: Distancia euclidiana
        """
        if not self.propiedades:
            return float('inf')
        
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if not propiedades_validas:
            return float('inf')
        
        desviaciones = [(p.normalizar_valor() - 1) ** 2 
                       for p in propiedades_validas]
        return np.sqrt(sum(desviaciones))
    
    def calcular_distancia_manhattan(self) -> float:
        """
        Calcula la distancia de Manhattan al vector óptimo
        
        Fórmula: d₁ = Σ|x_i - 1|
        
        Retorna:
            float: Distancia de Manhattan
        """
        if not self.propiedades:
            return float('inf')
        
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if not propiedades_validas:
            return float('inf')
        
        return sum(abs(p.normalizar_valor() - 1) for p in propiedades_validas)
    
    def obtener_propiedades_criticas(self, umbral: float = 0.3) -> List[Propiedad]:
        """
        Identifica propiedades críticas (mayor desviación del óptimo)
        
        Args:
            umbral: Desviación mínima para considerar crítica
        
        Retorna:
            List[Propiedad]: Propiedades ordenadas por criticidad
        """
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        criticas = []
        for prop in propiedades_validas:
            desviacion = abs(prop.normalizar_valor() - 1)
            if desviacion >= umbral:
                criticas.append((prop, desviacion))
        
        # Ordenar por desviación descendente
        criticas.sort(key=lambda x: x[1], reverse=True)
        return [prop for prop, _ in criticas]
    
    def calcular_estadisticas(self) -> Dict[str, float]:
        """
        Calcula estadísticas descriptivas de las propiedades
        
        Retorna:
            Dict con media, desviación estándar, varianza, CV
        """
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if len(propiedades_validas) < 2:
            return {
                'media': self.calcular_calidad_acumulada(),
                'desviacion_estandar': 0.0,
                'varianza': 0.0,
                'cv': 0.0,
                'n_propiedades': len(propiedades_validas)
            }
        
        valores_norm = [p.normalizar_valor() for p in propiedades_validas]
        
        media = np.mean(valores_norm)
        desviacion = np.std(valores_norm, ddof=1)  # Muestral
        varianza = desviacion ** 2
        cv = (desviacion / media * 100) if media != 0 else 0.0
        
        return {
            'media': media,
            'desviacion_estandar': desviacion,
            'varianza': varianza,
            'cv': cv,
            'n_propiedades': len(propiedades_validas)
        }
    
    def obtener_nivel_fertilidad(self) -> str:
        """
        Determina el nivel de fertilidad basado en la calidad acumulada
        
        Retorna:
            str: Nivel de fertilidad
        """
        calidad = self.calcular_calidad_acumulada()
        
        if calidad >= 0.80:
            return "Muy Alta"
        elif calidad >= 0.60:
            return "Alta"
        elif calidad >= 0.40:
            return "Moderada"
        elif calidad >= 0.20:
            return "Baja"
        else:
            return "Muy Baja"
    
    def __str__(self) -> str:
        return (f"Muestra {self.id} ({self.fecha_toma.strftime('%Y-%m-%d')}): "
                f"Fertilidad {self.obtener_nivel_fertilidad()} "
=======
"""
Clase Muestra: Representa una muestra de suelo con múltiples propiedades
Implementa cálculo de fertilidad acumulada y métricas estadísticas
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
from models.propiedad import Propiedad


@dataclass
class Muestra:
    """
    Representa una muestra de suelo con sus propiedades
    
    Atributos:
        id: Identificador único de la muestra
        fecha_toma: Fecha de recolección
        ubicacion: Ubicación geográfica (opcional)
        propiedades: Lista de propiedades del suelo
    """
    id: str
    fecha_toma: datetime
    ubicacion: str = ""
    propiedades: List[Propiedad] = field(default_factory=list)
    
    def agregar_propiedad(self, propiedad: Propiedad):
        """Agrega una propiedad a la muestra"""
        self.propiedades.append(propiedad)
    
    def obtener_propiedad(self, nombre: str) -> Optional[Propiedad]:
        """Obtiene una propiedad por su nombre"""
        for prop in self.propiedades:
            if prop.nombre == nombre:
                return prop
        return None
    
    def calcular_calidad_acumulada(self) -> float:
        """
        Calcula la calidad acumulada del suelo
        
        Fórmula: F̄ = (1/n) Σ f(x_i)
        donde f(x_i) es la evaluación de fertilidad de cada propiedad
        
        Retorna:
            float: Calidad promedio en [0, 1]
        """
        if not self.propiedades:
            return 0.0
        
        # Filtrar propiedades con valores válidos
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if not propiedades_validas:
            return 0.0
        
        fertilidades = [p.evaluar_fertilidad() for p in propiedades_validas]
        return sum(fertilidades) / len(fertilidades)
    
    def calcular_distancia_euclidiana(self) -> float:
        """
        Calcula la distancia euclidiana al vector óptimo (1,1,...,1)
        
        Fórmula: d₂ = √Σ(x_i - 1)²
        
        Retorna:
            float: Distancia euclidiana
        """
        if not self.propiedades:
            return float('inf')
        
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if not propiedades_validas:
            return float('inf')
        
        desviaciones = [(p.normalizar_valor() - 1) ** 2 
                       for p in propiedades_validas]
        return np.sqrt(sum(desviaciones))
    
    def calcular_distancia_manhattan(self) -> float:
        """
        Calcula la distancia de Manhattan al vector óptimo
        
        Fórmula: d₁ = Σ|x_i - 1|
        
        Retorna:
            float: Distancia de Manhattan
        """
        if not self.propiedades:
            return float('inf')
        
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if not propiedades_validas:
            return float('inf')
        
        return sum(abs(p.normalizar_valor() - 1) for p in propiedades_validas)
    
    def obtener_propiedades_criticas(self, umbral: float = 0.3) -> List[Propiedad]:
        """
        Identifica propiedades críticas (mayor desviación del óptimo)
        
        Args:
            umbral: Desviación mínima para considerar crítica
        
        Retorna:
            List[Propiedad]: Propiedades ordenadas por criticidad
        """
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        criticas = []
        for prop in propiedades_validas:
            desviacion = abs(prop.normalizar_valor() - 1)
            if desviacion >= umbral:
                criticas.append((prop, desviacion))
        
        # Ordenar por desviación descendente
        criticas.sort(key=lambda x: x[1], reverse=True)
        return [prop for prop, _ in criticas]
    
    def calcular_estadisticas(self) -> Dict[str, float]:
        """
        Calcula estadísticas descriptivas de las propiedades
        
        Retorna:
            Dict con media, desviación estándar, varianza, CV
        """
        propiedades_validas = [p for p in self.propiedades 
                              if p.esta_en_rango_aceptable()]
        
        if len(propiedades_validas) < 2:
            return {
                'media': self.calcular_calidad_acumulada(),
                'desviacion_estandar': 0.0,
                'varianza': 0.0,
                'cv': 0.0,
                'n_propiedades': len(propiedades_validas)
            }
        
        valores_norm = [p.normalizar_valor() for p in propiedades_validas]
        
        media = np.mean(valores_norm)
        desviacion = np.std(valores_norm, ddof=1)  # Muestral
        varianza = desviacion ** 2
        cv = (desviacion / media * 100) if media != 0 else 0.0
        
        return {
            'media': media,
            'desviacion_estandar': desviacion,
            'varianza': varianza,
            'cv': cv,
            'n_propiedades': len(propiedades_validas)
        }
    
    def obtener_nivel_fertilidad(self) -> str:
        """
        Determina el nivel de fertilidad basado en la calidad acumulada
        
        Retorna:
            str: Nivel de fertilidad
        """
        calidad = self.calcular_calidad_acumulada()
        
        if calidad >= 0.80:
            return "Muy Alta"
        elif calidad >= 0.60:
            return "Alta"
        elif calidad >= 0.40:
            return "Moderada"
        elif calidad >= 0.20:
            return "Baja"
        else:
            return "Muy Baja"
    
    def __str__(self) -> str:
        return (f"Muestra {self.id} ({self.fecha_toma.strftime('%Y-%m-%d')}): "
                f"Fertilidad {self.obtener_nivel_fertilidad()} "
>>>>>>> d600836cf7352c426d09819cab589b00f4f36f77
                f"({self.calcular_calidad_acumulada():.2f})")