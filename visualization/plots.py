"""
Módulo de visualización para Suelo Inteligente
Genera gráficas de análisis de fertilidad del suelo
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from models.muestra import Muestra
from models.propiedad import Propiedad
from utils.config import VALORES_REFERENCIA, CLASIFICACIONES
from utils.logger import setup_logger

logger = setup_logger()

# Configuración de estilo para gráficas profesionales
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Colores semánticos para clasificación
COLORES_CLASIFICACION = {
    'Exceso': '#ff6b6b',
    'Muy Alta Calidad': '#51cf66',
    'Alta Calidad': '#94d82d',
    'Moderada Calidad': '#fcc419',
    'Baja Calidad': '#ff922b',
    'Muy Baja Calidad': '#ff6b6b',
    'Déficit': '#c92a2a',
    'Fuera de rango': '#868e96'
}


class GeneradorGraficas:
    """Genera visualizaciones para análisis de fertilidad del suelo"""
    
    def __init__(self, dir_salida: str = "graficas"):
        self.dir_salida = dir_salida
        os.makedirs(dir_salida, exist_ok=True)
        logger.info(f"📁 Directorio de gráficas: {dir_salida}")
    
    def _guardar_grafica(self, fig, nombre_archivo: str) -> str:
        """Guarda una figura matplotlib como JPG"""
        ruta = os.path.join(self.dir_salida, f"{nombre_archivo}.jpg")
        fig.savefig(ruta, format='jpg', dpi=300, bbox_inches='tight')
        plt.close(fig)  # Liberar memoria
        logger.info(f"🖼️ Gráfica guardada: {ruta}")
        return ruta
    
    def barras_vs_optimo(self, muestra: Muestra, nombre_archivo: Optional[str] = None) -> str:
        """
        Gráfica de barras: valores normalizados vs valor óptimo (línea en 1.0)
        
        Args:
            muestra: Objeto Muestra con propiedades a graficar
            nombre_archivo: Nombre base para el archivo de salida
        
        Retorna:
            str: Ruta del archivo JPG generado
        """
        if nombre_archivo is None:
            nombre_archivo = f"barras_{muestra.id}_{muestra.fecha_toma.strftime('%Y%m%d')}"
        
        propiedades = [p for p in muestra.propiedades if p.esta_en_rango_aceptable()]
        if not propiedades:
            logger.warning("⚠️ No hay propiedades válidas para graficar")
            raise ValueError("No hay datos para graficar")
        
        nombres = [p.nombre for p in propiedades]
        valores_norm = [p.normalizar_valor() for p in propiedades]
        colores = [COLORES_CLASIFICACION.get(p.obtener_clasificacion(), '#868e96') 
                   for p in propiedades]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Barras de valores normalizados
        barras = ax.bar(nombres, valores_norm, color=colores, edgecolor='black', alpha=0.8)
        
        # Línea del valor óptimo (1.0)
        ax.axhline(y=1.0, color='blue', linestyle='--', linewidth=2, label='Óptimo (1.0)')
        
        # Líneas de rangos aceptables [0.5, 2.0]
        ax.axhline(y=0.5, color='orange', linestyle=':', linewidth=1, alpha=0.7, label='Límite inferior')
        ax.axhline(y=2.0, color='orange', linestyle=':', linewidth=1, alpha=0.7, label='Límite superior')
        
        # Etiquetas y título
        ax.set_ylabel('Valor Normalizado (x_real / x_óptimo)')
        ax.set_title(f'Análisis de Fertilidad - Muestra {muestra.id}\n{muestra.fecha_toma.strftime("%Y-%m-%d")}')
        ax.set_ylim(0, max(2.5, max(valores_norm) * 1.2))
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        # Rotar etiquetas del eje X
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Leyenda de colores por clasificación
        legend_elements = [
            mpatches.Patch(color=COLORES_CLASIFICACION[cat], label=cat)
            for cat in ['Muy Alta Calidad', 'Alta Calidad', 'Moderada Calidad', 
                       'Baja Calidad', 'Déficit', 'Exceso']
            if cat in COLORES_CLASIFICACION
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=8, title='Clasificación')
        
        # Añadir valores en las barras
        for barra, valor in zip(barras, valores_norm):
            height = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., height + 0.05,
                   f'{valor:.2f}', ha='center', va='bottom', fontsize=9)
        
        return self._guardar_grafica(fig, nombre_archivo)
    
    def histograma_extremos(self, muestras: List[Muestra], propiedad: str, 
                           nombre_archivo: Optional[str] = None) -> str:
        """
        Histograma de distribución de una propiedad específica, destacando extremos
        """
        if nombre_archivo is None:
            nombre_archivo = f"hist_{propiedad}_{datetime.now().strftime('%Y%m%d')}"
        
        # Extraer valores normalizados de la propiedad
        valores = []
        for m in muestras:
            p = m.obtener_propiedad(propiedad)
            if p and p.esta_en_rango_aceptable():
                valores.append(p.normalizar_valor())
        
        if len(valores) < 2:
            logger.warning(f"⚠️ Insuficientes datos para histograma de {propiedad}")
            raise ValueError(f"Se requieren al menos 2 valores válidos de {propiedad}")
        
        ref = VALORES_REFERENCIA.get(propiedad)
        if not ref:
            raise ValueError(f"Propiedad '{propiedad}' no está en VALORES_REFERENCIA")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histograma principal
        n_bins = min(15, max(5, len(valores) // 3))
        ax.hist(valores, bins=n_bins, edgecolor='black', alpha=0.7, 
                color='steelblue', label='Distribución')
        
        # Marcar valor óptimo y límites
        ax.axvline(x=1.0, color='blue', linestyle='--', linewidth=2, label='Óptimo (1.0)')
        ax.axvline(x=0.5, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
        ax.axvline(x=2.0, color='orange', linestyle=':', linewidth=1.5, alpha=0.7, 
                   label='Límites aceptables')
        
        # Sombrear regiones de clasificación (CORREGIDO)
        added_categories = set()
        for categoria, (min_v, max_v) in CLASIFICACIONES.items():
            if min_v >= -1 and max_v <= 2:
                label = categoria if categoria not in added_categories else ""
                added_categories.add(categoria)
                ax.axvspan(min_v, max_v, color=COLORES_CLASIFICACION[categoria], 
                          alpha=0.1, label=label)
        
        # Estadísticas descriptivas
        media = np.mean(valores)
        mediana = np.median(valores)
        desviacion = np.std(valores, ddof=1)
        
        stats_text = (f'Media: {media:.2f}\n'
                     f'Mediana: {mediana:.2f}\n'
                     f'Desv. Est.: {desviacion:.2f}\n'
                     f'n = {len(valores)}')
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        ax.set_xlabel(f'Valor Normalizado de {propiedad}')
        ax.set_ylabel('Frecuencia')
        ax.set_title(f'Distribución de {ref.nombre} - {len(muestras)} muestras')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(axis='y', alpha=0.3)
        
        return self._guardar_grafica(fig, nombre_archivo)
    
    def dispersion_propiedad(self, muestras: List[Muestra], prop_x: str, prop_y: str,
                             nombre_archivo: Optional[str] = None) -> str:
        """
        Gráfico de dispersión entre dos propiedades
        
        Args:
            muestras: Lista de objetos Muestra
            prop_x: Nombre de la propiedad para eje X
            prop_y: Nombre de la propiedad para eje Y
            nombre_archivo: Nombre base para el archivo de salida
        
        Retorna:
            str: Ruta del archivo JPG generado
        """
        if nombre_archivo is None:
            nombre_archivo = f"disp_{prop_x}_{prop_y}_{datetime.now().strftime('%Y%m%d')}"
        
        # Extraer pares de valores
        x_vals, y_vals, colores, ids = [], [], [], []
        for m in muestras:
            px = m.obtener_propiedad(prop_x)
            py = m.obtener_propiedad(prop_y)
            if (px and px.esta_en_rango_aceptable() and 
                py and py.esta_en_rango_aceptable()):
                x_vals.append(px.normalizar_valor())
                y_vals.append(py.normalizar_valor())
                colores.append(COLORES_CLASIFICACION.get(m.obtener_nivel_fertilidad(), '#868e96'))
                ids.append(m.id)
        
        if len(x_vals) < 3:
            logger.warning(f"⚠️ Insuficientes datos para dispersión {prop_x} vs {prop_y}")
            raise ValueError("Se requieren al menos 3 pares de valores válidos")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot
        scatter = ax.scatter(x_vals, y_vals, c=colores, s=80, edgecolors='black', 
                            alpha=0.7, cmap='viridis')
        
        # Líneas del punto óptimo (1, 1)
        ax.axvline(x=1.0, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=1.0, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax.plot([1], [1], 'b*', markersize=20, label='Punto Óptimo')
        
        # Cuadrantes de interpretación
        ax.text(0.02, 0.98, 'Cuadrantes:\n• Superior-Derecha: Exceso en ambas\n• Inferior-Izquierda: Déficit en ambas\n• Otros: Mixto',
                transform=ax.transAxes, fontsize=8, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
        
        # Etiquetas
        ref_x = VALORES_REFERENCIA.get(prop_x)
        ref_y = VALORES_REFERENCIA.get(prop_y)
        ax.set_xlabel(f'{ref_x.nombre if ref_x else prop_x} (normalizado)')
        ax.set_ylabel(f'{ref_y.nombre if ref_y else prop_y} (normalizado)')
        ax.set_title(f'Relación entre {prop_x} y {prop_y}\n{len(x_vals)} muestras válidas')
        
        # Cuadrícula y leyenda
        ax.grid(True, alpha=0.3)
        
        # Leyenda de niveles de fertilidad
        legend_elements = [
            mpatches.Patch(color=COLORES_CLASIFICACION.get(nivel, '#868e96'), label=nivel)
            for nivel in ['Muy Alta', 'Alta', 'Moderada', 'Baja', 'Muy Baja']
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9, title='Nivel de Fertilidad')
        
        # Anotar algunos puntos (los más extremos)
        for i, (x, y, sid) in enumerate(zip(x_vals, y_vals, ids)):
            if abs(x - 1) > 0.5 or abs(y - 1) > 0.5:  # Solo los más desviados
                ax.annotate(sid, (x, y), textcoords="offset points", 
                           xytext=(5, 5), ha='left', fontsize=7, alpha=0.8)
        
        return self._guardar_grafica(fig, nombre_archivo)
    
    def comparativa_temporal(self, muestra_1: Muestra, muestra_2: Muestra,
                             nombre_archivo: Optional[str] = None) -> str:
        """
        Gráfica comparativa entre dos muestras del mismo ID con diferentes fechas
        
        Args:
            muestra_1: Primera muestra (más antigua)
            muestra_2: Segunda muestra (más reciente)
            nombre_archivo: Nombre base para el archivo de salida
        
        Retorna:
            str: Ruta del archivo JPG generado
        """
        if muestra_1.id != muestra_2.id:
            raise ValueError("Las muestras deben tener el mismo ID para comparación temporal")
        
        if nombre_archivo is None:
            nombre_archivo = f"comp_{muestra_1.id}_temporal"
        
        # Encontrar propiedades comunes
        props_comunes = []
        for p1 in muestra_1.propiedades:
            p2 = muestra_2.obtener_propiedad(p1.nombre)
            if p2 and p1.esta_en_rango_aceptable() and p2.esta_en_rango_aceptable():
                props_comunes.append((p1, p2))
        
        if not props_comunes:
            raise ValueError("No hay propiedades comunes válidas para comparar")
        
        nombres = [p1.nombre for p1, _ in props_comunes]
        valores_1 = [p1.normalizar_valor() for p1, _ in props_comunes]
        valores_2 = [p2.normalizar_valor() for _, p2 in props_comunes]
        cambios = [v2 - v1 for v1, v2 in zip(valores_1, valores_2)]
        
        # Colores según dirección del cambio
        colores = ['#2ecc71' if c > 0 else '#e74c3c' if c < 0 else '#95a5a6' 
                   for c in cambios]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # Gráfica superior: valores normalizados
        x = np.arange(len(nombres))
        width = 0.35
        
        ax1.bar(x - width/2, valores_1, width, label=muestra_1.fecha_toma.strftime('%Y-%m-%d'), 
                color='steelblue', edgecolor='black', alpha=0.8)
        ax1.bar(x + width/2, valores_2, width, label=muestra_2.fecha_toma.strftime('%Y-%m-%d'), 
                color='coral', edgecolor='black', alpha=0.8)
        ax1.axhline(y=1.0, color='blue', linestyle='--', linewidth=1.5, label='Óptimo')
        ax1.set_ylabel('Valor Normalizado')
        ax1.set_title(f'Comparación Temporal - Muestra {muestra_1.id}')
        ax1.set_xticks(x)
        ax1.set_xticklabels(nombres, rotation=45, ha='right')
        ax1.legend(loc='upper right')
        ax1.grid(axis='y', alpha=0.3)
        
        # Gráfica inferior: cambios
        bars = ax2.bar(nombres, cambios, color=colores, edgecolor='black', alpha=0.8)
        ax2.axhline(y=0, color='black', linewidth=0.5)
        ax2.set_ylabel('Cambio (Δ)')
        ax2.set_xlabel('Propiedad')
        ax2.set_title('Variación entre muestras (positivo = mejora/acercamiento al óptimo)')
        ax2.set_xticklabels(nombres, rotation=45, ha='right')
        ax2.grid(axis='y', alpha=0.3)
        
        # Añadir valores de cambio en las barras inferiores
        for barra, cambio in zip(bars, cambios):
            height = barra.get_height()
            ax2.text(barra.get_x() + barra.get_width()/2., 
                    height + (0.02 if height >= 0 else -0.05),
                    f'{cambio:+.2f}', ha='center', va='bottom' if height >= 0 else 'top', 
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        return self._guardar_grafica(fig, nombre_archivo)
    
    def alerta_valores_extremos(self, muestras: List[Muestra], 
                                nombre_archivo: Optional[str] = None) -> str:
        """
        Gráfica de alerta: resumen visual de valores fuera de rango aceptable
        
        Args:
            muestras: Lista de objetos Muestra a evaluar
            nombre_archivo: Nombre base para el archivo de salida
        
        Retorna:
            str: Ruta del archivo JPG generado
        """
        if nombre_archivo is None:
            nombre_archivo = f"alertas_{datetime.now().strftime('%Y%m%d')}"
        
        # Contar alertas por propiedad
        alertas_por_prop = {}
        total_muestras = len(muestras)
        
        for m in muestras:
            for p in m.propiedades:
                if not p.esta_en_rango_aceptable():
                    if p.nombre not in alertas_por_prop:
                        alertas_por_prop[p.nombre] = {'bajo': 0, 'alto': 0}
                    if p.valor < VALORES_REFERENCIA[p.nombre].minimo * 0.5:
                        alertas_por_prop[p.nombre]['bajo'] += 1
                    elif p.valor > VALORES_REFERENCIA[p.nombre].maximo * 2.0:
                        alertas_por_prop[p.nombre]['alto'] += 1
        
        if not alertas_por_prop:
            # Gráfica de "todo correcto"
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, '✅ Todos los valores dentro de rango aceptable', 
                   ha='center', va='center', fontsize=14, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title('Validación de Datos - Sin Alertas')
            return self._guardar_grafica(fig, nombre_archivo)
        
        # Preparar datos para gráfica de barras agrupadas
        props = list(alertas_por_prop.keys())
        bajos = [alertas_por_prop[p]['bajo'] for p in props]
        altos = [alertas_por_prop[p]['alto'] for p in props]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(props))
        width = 0.35
        
        ax.bar(x - width/2, bajos, width, label='Valores muy bajos (< 0.5×mín)', 
              color='#c92a2a', edgecolor='black')
        ax.bar(x + width/2, altos, width, label='Valores muy altos (> 2.0×máx)', 
              color='#e67700', edgecolor='black')
        
        ax.set_ylabel('Número de alertas')
        ax.set_xlabel('Propiedad del suelo')
        ax.set_title(f'⚠️ Alertas de Valores Extremos - {total_muestras} muestras procesadas')
        ax.set_xticks(x)
        ax.set_xticklabels(props, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        # Añadir conteo en las barras
        for barras in [ax.patches[:len(props)], ax.patches[len(props):]]:
            for barra in barras:
                height = barra.get_height()
                if height > 0:
                    ax.text(barra.get_x() + barra.get_width()/2., height + 0.1,
                           f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # Nota explicativa
        fig.text(0.5, 0.02, 
                'Nota: Valores fuera de [0.5×mín, 2.0×máx] se descartan del análisis.',
                ha='center', fontsize=9, style='italic', bbox=dict(facecolor='yellow', alpha=0.2))
        
        return self._guardar_grafica(fig, nombre_archivo)
    
    def generar_reporte_grafico(self, muestras: List[Muestra], 
                                nombre_reporte: str = "reporte_completo") -> Dict[str, str]:
        """
        Genera un conjunto completo de gráficas para un reporte
        
        Args:
            muestras: Lista de objetos Muestra
            nombre_reporte: Prefijo para los archivos de salida
        
        Retorna:
            Dict[str, str]: Mapeo de tipo de gráfica a ruta del archivo
        """
        resultados = {}
        
        try:
            # 1. Gráficas individuales (si hay pocas muestras)
            if len(muestras) <= 5:
                for m in muestras:
                    ruta = self.barras_vs_optimo(m, f"{nombre_reporte}_{m.id}")
                    resultados[f'barras_{m.id}'] = ruta
            
            # 2. Histogramas por propiedad (si hay suficientes datos)
            if len(muestras) >= 3:
                for prop in ['pH', 'MO', 'P', 'K']:  # Propiedades clave
                    if any(m.obtener_propiedad(prop) for m in muestras):
                        try:
                            ruta = self.histograma_extremos(muestras, prop, 
                                                           f"{nombre_reporte}_hist_{prop}")
                            resultados[f'hist_{prop}'] = ruta
                        except ValueError:
                            continue  # Saltar si no hay datos suficientes
            
            # 3. Dispersión entre propiedades clave
            pares = [('pH', 'MO'), ('P', 'K'), ('Ca', 'Mg')]
            for px, py in pares:
                if any(m.obtener_propiedad(px) and m.obtener_propiedad(py) for m in muestras):
                    try:
                        ruta = self.dispersion_propiedad(muestras, px, py,
                                                        f"{nombre_reporte}_disp_{px}_{py}")
                        resultados[f'disp_{px}_{py}'] = ruta
                    except ValueError:
                        continue
            
            # 4. Comparativas temporales (mismo ID, diferentes fechas)
            ids_unicos = {m.id for m in muestras}
            for uid in ids_unicos:
                muestras_id = [m for m in muestras if m.id == uid]
                if len(muestras_id) == 2:
                    # Ordenar por fecha
                    muestras_id.sort(key=lambda m: m.fecha_toma)
                    try:
                        ruta = self.comparativa_temporal(muestras_id[0], muestras_id[1],
                                                        f"{nombre_reporte}_comp_{uid}")
                        resultados[f'comp_{uid}'] = ruta
                    except ValueError:
                        continue
            
            # 5. Gráfica de alertas general
            ruta_alertas = self.alerta_valores_extremos(muestras, f"{nombre_reporte}_alertas")
            resultados['alertas'] = ruta_alertas
            
            logger.info(f"✅ Reporte gráfico completo generado: {len(resultados)} gráficas")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error al generar reporte gráfico: {e}")
            raise