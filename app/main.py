"""
Suelo Inteligente - Interfaz Web
Aplicación para clasificación de fertilidad del suelo.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from io import BytesIO
import sys

# Añadir ruta raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.loader import CargadorDatos
from data.template import generar_plantilla_vacia, generar_plantilla_optima
from data.export import ExportadorResultados
from visualization.plots import GeneradorGraficas
from utils.logger import setup_logger
from utils.config import VALORES_REFERENCIA, COLUMNAS_CSV

# Configuración de la página
st.set_page_config(
    page_title="Suelo Inteligente",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar logger
logger = setup_logger()

# Títulos y estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        background-color: #2E8B57;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stDataFrame {
        font-size: 0.9em;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .alert-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

def mostrar_encabezado():
    st.markdown('<div class="main-header"><h1> Suelo Inteligente</h1><p>Clasificación de fertilidad en parcelas agrícolas</p></div>', unsafe_allow_html=True)
    st.markdown("Bienvenido a la herramienta de análisis de suelos. Utiliza el menú lateral para navegar entre las funcionalidades.")

def descargar_plantillas():
    st.header("📥 Descarga de Plantillas")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plantilla Vacía")
        st.write("Descarga un archivo CSV con los encabezados correctos para ingresar tus datos.")
        if st.button("Descargar Plantilla Vacía"):
            ruta = generar_plantilla_vacia("plantilla_vacia.csv")
            with open(ruta, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar CSV",
                    data=f,
                    file_name="plantilla_muestras.csv",
                    mime="text/csv"
                )
                st.success("Plantilla generada. Haz clic para descargar.")
    
    with col2:
        st.subheader("Ejemplo de Valores Óptimos")
        st.write("Descarga un archivo con una muestra de valores óptimos para referencia.")
        if st.button("Descargar Ejemplo Óptimo"):
            ruta = generar_plantilla_optima("ejemplo_optimo.csv")
            with open(ruta, "rb") as f:
                st.download_button(
                    label="️ Descargar Ejemplo",
                    data=f,
                    file_name="ejemplo_valores_optimos.csv",
                    mime="text/csv"
                )
                st.success("Ejemplo generado. Haz clic para descargar.")

def analisis_lote():
    st.header("Análisis por Lote (CSV)")
    
    uploaded_file = st.file_uploader("Sube tu archivo CSV con las muestras", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Guardar archivo temporalmente
            with open("temp_input.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.subheader("⚙️ Configuración de Procesamiento")
            modo_limpieza = st.selectbox(
                "Modo de manejo de datos faltantes",
                ["individual", "grupo"],
                help="Individual: Omite valores faltantes por muestra. Grupo: Rellena con media grupal."
            )
            
            if st.button("🚀 Procesar Muestras"):
                with st.spinner("Procesando datos..."):
                    loader = CargadorDatos()
                    df_crudo = loader.cargar_csv("temp_input.csv")
                    df_limpio, alertas = loader.validar_y_limpiar(df_crudo, modo=modo_limpieza)
                    
                    # Mostrar alertas
                    if alertas:
                        st.warning("⚠️ **Alertas de Validación:**")
                        for alerta in alertas:
                            st.write(f"- {alerta}")
                    
                    if df_limpio.empty:
                        st.error("❌ No hay datos válidos para procesar. Revisa las alertas.")
                        return
                    
                    muestras = loader.convertir_a_muestras(df_limpio)
                    
                    if not muestras:
                        st.error("❌ No se pudieron crear objetos Muestra.")
                        return
                    
                    st.success(f"✅ {len(muestras)} muestras procesadas correctamente.")
                    
                    # Exportar resultados
                    exporter = ExportadorResultados()
                    ruta_csv = exporter.a_csv(muestras, "resultados_lote.csv")
                    ruta_json = exporter.a_json(muestras, "resultados_lote.json")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with open(ruta_csv, "rb") as f:
                            st.download_button("⬇️ Descargar Resultados CSV", f, "resultados_muestras.csv", "text/csv")
                    with col2:
                        with open(ruta_json, "rb") as f:
                            st.download_button("⬇️ Descargar Resultados JSON", f, "resultados_muestras.json", "application/json")
                    
                    # Visualización
                    st.subheader("📈 Visualización de Resultados")
                    
                    # Tabla resumen
                    df_resultados = pd.read_csv(ruta_csv)
                    st.dataframe(df_resultados)
                    
                    # Gráficas
                    plotter = GeneradorGraficas()
                    
                    # 1. Gráficas de barras para cada muestra (si son pocas)
                    if len(muestras) <= 5:
                        st.write("**Gráficas de barras por muestra:**")
                        cols = st.columns(min(3, len(muestras)))
                        for i, m in enumerate(muestras):
                            with cols[i % 3]:
                                fig, ax = plt.subplots(figsize=(6, 4))
                                props = [p for p in m.propiedades if p.esta_en_rango_aceptable()]
                                if props:
                                    nombres = [p.nombre for p in props]
                                    valores = [p.normalizar_valor() for p in props]
                                    ax.bar(nombres, valores, color='skyblue', edgecolor='black')
                                    ax.axhline(y=1.0, color='red', linestyle='--', label='Óptimo')
                                    ax.set_title(f"Muestra {m.id}")
                                    ax.set_ylim(0, max(2.5, max(valores)*1.2))
                                    ax.legend()
                                    plt.xticks(rotation=45)
                                    st.pyplot(fig)
                    
                    # 2. Histograma de pH y MO (si hay suficientes datos)
                    if len(muestras) >= 3:
                        st.write("**Distribución de propiedades clave:**")
                        for prop in ['pH', 'MO']:
                            if any(m.obtener_propiedad(prop) for m in muestras):
                                fig, ax = plt.subplots(figsize=(8, 4))
                                valores = [m.obtener_propiedad(prop).normalizar_valor() 
                                          for m in muestras 
                                          if m.obtener_propiedad(prop) and m.obtener_propiedad(prop).esta_en_rango_aceptable()]
                                if len(valores) >= 2:
                                    ax.hist(valores, bins='auto', color='green', alpha=0.7, edgecolor='black')
                                    ax.axvline(x=1.0, color='red', linestyle='--', label='Óptimo')
                                    ax.set_title(f"Distribución de {prop}")
                                    ax.legend()
                                    st.pyplot(fig)
                    
                    # 3. Comparativa temporal (si hay IDs duplicados con fechas distintas)
                    ids_unicos = df_limpio['id'].unique()
                    ids_con_multiples_fechas = []
                    for uid in ids_unicos:
                        fechas = df_limpio[df_limpio['id'] == uid]['fecha'].unique()
                        if len(fechas) > 1:
                            ids_con_multiples_fechas.append(uid)
                    
                    if ids_con_multiples_fechas:
                        st.write("⏳ **Comparación Temporal Detectada:**")
                        for uid in ids_con_multiples_fechas:
                            sub_muestras = [m for m in muestras if m.id == uid]
                            sub_muestras.sort(key=lambda m: m.fecha_toma)
                            if len(sub_muestras) == 2:
                                m1, m2 = sub_muestras[0], sub_muestras[1]
                                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                                
                                # Gráfica superior
                                props_comunes = []
                                for p1 in m1.propiedades:
                                    p2 = m2.obtener_propiedad(p1.nombre)
                                    if p2: props_comunes.append((p1, p2))
                                
                                if props_comunes:
                                    nombres = [p1.nombre for p1, _ in props_comunes]
                                    v1 = [p1.normalizar_valor() for p1, _ in props_comunes]
                                    v2 = [p2.normalizar_valor() for _, p2 in props_comunes]
                                    
                                    x = range(len(nombres))
                                    ax1.bar([i-0.2 for i in x], v1, 0.4, label=m1.fecha_toma.strftime('%Y-%m-%d'), color='blue')
                                    ax1.bar([i+0.2 for i in x], v2, 0.4, label=m2.fecha_toma.strftime('%Y-%m-%d'), color='orange')
                                    ax1.set_xticks(x)
                                    ax1.set_xticklabels(nombres, rotation=45)
                                    ax1.legend()
                                    ax1.set_title(f"Comparación Temporal - ID: {uid}")
                                    
                                    # Gráfica inferior (cambios)
                                    cambios = [b-a for a, b in zip(v1, v2)]
                                    colores_cambio = ['green' if c >= 0 else 'red' for c in cambios]
                                    ax2.bar(nombres, cambios, color=colores_cambio, edgecolor='black')
                                    ax2.axhline(y=0, color='black', linewidth=1)
                                    ax2.set_ylabel('Cambio (Δ)')
                                    ax2.set_title('Variación entre fechas')
                                    
                                    plt.tight_layout()
                                    st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Error durante el procesamiento: {e}")
            logger.error(f"Error en análisis por lote: {e}")

def analisis_manual():
    st.header("Análisis Manual (Muestra Individual)")
    
    st.write("Ingresa los valores medidos para una muestra específica. Deja en blanco o 0 si no tienes el dato.")
    
    with st.form("form_manual"):
        col1, col2 = st.columns(2)
        
        with col1:
            id_muestra = st.text_input("ID de la Muestra", value="MANUAL-001")
            fecha_toma = st.date_input("Fecha de Toma", value=datetime.today())
            
            pH = st.number_input("pH (H2O)", min_value=0.0, step=0.1, value=0.0)
            MO = st.number_input("Materia Orgánica (%)", min_value=0.0, step=0.1, value=0.0)
            P = st.number_input("Fósforo Olsen (ppm)", min_value=0.0, step=0.1, value=0.0)
            Ca = st.number_input("Calcio (cmol kg-1)", min_value=0.0, step=0.1, value=0.0)
        
        with col2:
            ubicacion = st.text_input("Ubicación", value="Parcela A")
            Mg = st.number_input("Magnesio (cmol kg-1)", min_value=0.0, step=0.1, value=0.0)
            K = st.number_input("Potasio (cmol kg-1)", min_value=0.0, step=0.1, value=0.0)
            CICE = st.number_input("CICE (cmol kg-1)", min_value=0.0, step=0.1, value=0.0)
            C_BM = st.number_input("C Biomasa Microbiana (mg kg-1)", min_value=0.0, step=0.1, value=0.0)
            
        submitted = st.form_submit_button("🔍 Analizar Muestra")
        
        if submitted:
            from models.muestra import Muestra
            from models.propiedad import Propiedad
            
            muestra = Muestra(id=id_muestra, fecha_toma=datetime.combine(fecha_toma, datetime.min.time()), ubicacion=ubicacion)
            
            propiedades_input = {
                'pH': pH, 'MO': MO, 'P': P, 'Ca': Ca,
                'Mg': Mg, 'K': K, 'CICE': CICE, 'C_BM': C_BM
            }
            
            for nombre, valor in propiedades_input.items():
                if valor > 0:  # Solo agregar si hay valor
                    muestra.agregar_propiedad(Propiedad(nombre=nombre, valor=valor))
            
            if not muestra.propiedades:
                st.error("❌ Debes ingresar al menos un valor mayor a 0.")
                return
            
            # Mostrar resultados
            st.subheader(" Resultados del Análisis")
            
            nivel = muestra.obtener_nivel_fertilidad()
            calidad = muestra.calcular_calidad_acumulada()
            
            # Colores según nivel
            color_nivel = {
                "Muy Alta": "🟢", "Alta": "🟢", "Moderada": "🟡", "Baja": "🟠", "Muy Baja": ""
            }.get(nivel, "")
            
            st.markdown(f"""
                <div style="background-color: #1D1D1D; padding: 15px; border-radius: 5px;">
                    <h3>Nivel de Fertilidad: {color_nivel} {nivel}</h3>
                    <p>Calidad Acumulada: <b>{calidad:.2f}</b> (Escala 0-1)</p>
                    <p>Distancia al Óptimo (Euclidiana): {muestra.calcular_distancia_euclidiana():.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Tabla de propiedades
            st.subheader("Tabla de propiedades")
            datos_props = []
            for p in muestra.propiedades:
                datos_props.append({
                    "Propiedad": p.nombre,
                    "Valor Real": p.valor,
                    "Normalizado": p.normalizar_valor(),
                    "Fertilidad": p.evaluar_fertilidad(),
                    "Clasificación": p.obtener_clasificacion(),
                    "Desviación": p.calcular_desviacion()
                })
            
            st.dataframe(pd.DataFrame(datos_props))
            
            # Gráfica de barras
            st.subheader("Gráfica de Evaluación")
            fig, ax = plt.subplots(figsize=(10, 6))
            props_validas = [p for p in muestra.propiedades if p.esta_en_rango_aceptable()]
            if props_validas:
                nombres = [p.nombre for p in props_validas]
                valores = [p.normalizar_valor() for p in props_validas]
                colores = ['#2ecc71' if 0.8 <= v <= 1.0 else '#f1c40f' if 0.4 <= v < 0.8 else '#e74c3c' for v in valores]
                
                ax.bar(nombres, valores, color=colores, edgecolor='black')
                ax.axhline(y=1.0, color='blue', linestyle='--', linewidth=2, label='Óptimo')
                ax.set_ylabel('Valor Normalizado')
                ax.set_title(f'Perfil de Fertilidad - {id_muestra}')
                ax.set_ylim(0, max(2.5, max(valores)*1.2))
                ax.legend()
                plt.xticks(rotation=45)
                st.pyplot(fig)
                
                # Propiedades críticas
                criticas = muestra.obtener_propiedades_criticas(umbral=0.3)
                if criticas:
                    st.warning("️ **Propiedades que requieren atención (Desviación > 0.3):**")
                    for p in criticas:
                        st.write(f"- **{p.nombre}**: Valor {p.valor} (Normalizado: {p.normalizar_valor():.2f})")


def main():
    mostrar_encabezado()
    
    menu = st.sidebar.radio("Navegación", [
        "Inicio",
        "Análisis por Lote (CSV)",
        "Análisis Manual"
    ])
    
    if menu == "Inicio":
        st.write("""
        ### Acerca del Proyecto
        **Suelo Inteligente** es una herramienta desarrollada para la Licenciatura en Ciencias de Datos para Negocios.
        Permite a productores y técnicos analizar la fertilidad del suelo mediante métricas matemáticas rigurosas.
        
        #### Características:
        - ✅ Normalización basada en valores óptimos de referencia.
        - ✅ Clasificación de calidad según estándares agrícolas.
        - ✅ Detección de excesos y déficits mediante funciones piecewise.
        - ✅ Comparación temporal de muestras.
        - ✅ Exportación de resultados y reportes gráficos.
        
        #### Referencias:
        - FAO (2017). Soil Fertility Management.
        - CIMMYT. Fertilidad integral para el Altiplano.
        - Zhang et al. (2021). Machine Learning for Soil Fertility Classification.
        """)
    
    elif menu == " Descargar Plantillas":
        descargar_plantillas()
        
    elif menu == "Análisis por Lote (CSV)":
        analisis_lote()
        
    elif menu == "Análisis Manual":
        analisis_manual()
        

if __name__ == "__main__":
    main()