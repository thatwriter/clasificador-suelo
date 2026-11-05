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
/* ============================================
   🌆 RETROFUTURISMO ECO-TECH — Suelo Inteligente
   Estética: Synthwave + Solarpunk
   ============================================ */

/* ---------- Variables de diseño ---------- */
:root {
    --bg-deep: #0a0e1a;          /* Fondo principal profundo */
    --bg-panel: #111827;         /* Paneles y tarjetas */
    --bg-sidebar: #0d1420;       /* Sidebar */
    --neon-green: #39ff14;       /* Verde neón principal */
    --neon-cyan: #00f0ff;        /* Cyan de acento */
    --neon-magenta: #ff2e97;     /* Magenta para alertas */
    --neon-amber: #ffb627;       /* Ámbar para warnings */
    --text-primary: #e6f1ff;     /* Texto principal */
    --text-muted: #8892b0;       /* Texto secundario */
    --grid-color: rgba(57, 255, 20, 0.08); /* Grid de fondo */
    --glow-green: 0 0 10px rgba(57, 255, 20, 0.6), 0 0 20px rgba(57, 255, 20, 0.3);
    --glow-cyan: 0 0 10px rgba(0, 240, 255, 0.6), 0 0 20px rgba(0, 240, 255, 0.3);
}

/* ---------- Fondo principal con grid retro ---------- */
.stApp {
    background:
        linear-gradient(rgba(10, 14, 26, 0.92), rgba(10, 14, 26, 0.92)),
        linear-gradient(var(--grid-color) 1px, transparent 1px) 0 0 / 40px 40px,
        linear-gradient(90deg, var(--grid-color) 1px, transparent 1px) 0 0 / 40px 40px,
        radial-gradient(ellipse at top, #0f2027 0%, var(--bg-deep) 70%);
    color: var(--text-primary);
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
}

/* ---------- Scanlines sutiles (efecto CRT) ---------- */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.08) 0px,
        rgba(0, 0, 0, 0.08) 1px,
        transparent 1px,
        transparent 3px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ---------- Sidebar retro ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-sidebar) 0%, #050810 100%);
    border-right: 1px solid var(--neon-green);
    box-shadow: 2px 0 20px rgba(57, 255, 20, 0.15);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--neon-green);
    text-shadow: var(--glow-green);
    letter-spacing: 2px;
    text-transform: uppercase;
}

section[data-testid="stSidebar"] .stRadio label {
    color: var(--text-primary);
    transition: all 0.3s ease;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--neon-cyan);
    text-shadow: var(--glow-cyan);
    transform: translateX(4px);
}

/* ---------- Header principal con gradiente neón ---------- */
.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    border: 1px solid var(--neon-green);
    box-shadow: var(--glow-green), inset 0 0 30px rgba(57, 255, 20, 0.1);
    color: var(--neon-green);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: "";
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent 40%, rgba(57, 255, 20, 0.1) 50%, transparent 60%);
    animation: shine 6s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%); }
    100% { transform: translateX(100%) translateY(100%); }
}

.main-header h1 {
    font-family: 'Orbitron', 'Courier New', monospace;
    letter-spacing: 4px;
    text-transform: uppercase;
    text-shadow: 0 0 15px var(--neon-green), 0 0 30px rgba(57, 255, 20, 0.5);
    margin: 0;
    position: relative;
    z-index: 1;
}

.main-header p {
    color: var(--neon-cyan);
    letter-spacing: 2px;
    text-shadow: var(--glow-cyan);
    margin-top: 8px;
    position: relative;
    z-index: 1;
}

/* ---------- Títulos generales ---------- */
h1, h2, h3, h4 {
    color: var(--neon-cyan);
    font-family: 'Orbitron', 'Courier New', monospace;
    letter-spacing: 1.5px;
    border-bottom: 1px dashed rgba(0, 240, 255, 0.3);
    padding-bottom: 8px;
}

h1 { text-shadow: var(--glow-cyan); }
h2 { color: var(--neon-green); text-shadow: var(--glow-green); }

/* ---------- Botones estilo terminal ---------- */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, #0f2027, #203a43);
    color: var(--neon-green);
    border: 1px solid var(--neon-green);
    border-radius: 6px;
    padding: 0.5rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    transition: all 0.3s ease;
    box-shadow: 0 0 8px rgba(57, 255, 20, 0.3);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--neon-green);
    color: var(--bg-deep);
    box-shadow: var(--glow-green);
    transform: translateY(-2px);
}

/* Botón primario (submit de forms) */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--neon-cyan), #0088aa);
    color: var(--bg-deep);
    border: 1px solid var(--neon-cyan);
    box-shadow: var(--glow-cyan);
    font-weight: 700;
}

.stFormSubmitButton > button:hover {
    background: var(--neon-cyan);
    box-shadow: 0 0 25px var(--neon-cyan);
}

/* ---------- Inputs y selects ---------- */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(17, 24, 39, 0.8) !important;
    color: var(--text-primary) !important;
    border: 1px solid rgba(57, 255, 20, 0.3) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--neon-cyan) !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
}

/* ---------- DataFrames estilo terminal ---------- */
.stDataFrame {
    font-size: 0.9em;
    border: 1px solid rgba(57, 255, 20, 0.3);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 0 15px rgba(57, 255, 20, 0.1);
}

/* ---------- Cajas de éxito / alerta / warning ---------- */
.success-box {
    background: linear-gradient(135deg, rgba(57, 255, 20, 0.1), rgba(0, 240, 255, 0.05));
    border: 1px solid var(--neon-green);
    border-left: 4px solid var(--neon-green);
    padding: 12px 15px;
    border-radius: 6px;
    margin-top: 10px;
    color: var(--neon-green);
    box-shadow: inset 0 0 15px rgba(57, 255, 20, 0.1);
}

.alert-box {
    background: linear-gradient(135deg, rgba(255, 46, 151, 0.1), rgba(255, 46, 151, 0.05));
    border: 1px solid var(--neon-magenta);
    border-left: 4px solid var(--neon-magenta);
    padding: 12px 15px;
    border-radius: 6px;
    margin-top: 10px;
    color: #ff8ac4;
    box-shadow: inset 0 0 15px rgba(255, 46, 151, 0.1);
}

/* Mensajes nativos de Streamlit */
.stAlert {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

div[data-testid="stNotification"] {
    font-family: 'JetBrains Mono', monospace;
}

/* ---------- Spinner personalizado ---------- */
.stSpinner > div {
    border-top-color: var(--neon-cyan) !important;
}

/* ---------- File uploader ---------- */
.stFileUploader > div {
    border: 2px dashed var(--neon-cyan) !important;
    background: rgba(0, 240, 255, 0.03) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: var(--neon-green) !important;
    box-shadow: var(--glow-green);
}

/* ---------- Scrollbar retro ---------- */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: var(--bg-deep);
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--neon-green), var(--neon-cyan));
    border-radius: 5px;
    box-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
}

/* ---------- Links ---------- */
a {
    color: var(--neon-cyan) !important;
    text-decoration: none;
    transition: all 0.2s ease;
}
a:hover {
    color: var(--neon-green) !important;
    text-shadow: var(--glow-green);
}

/* ---------- Efecto flicker en el título (opcional, sutil) ---------- */
.main-header h1 {
    animation: flicker 4s infinite;
}
@keyframes flicker {
    0%, 97%, 100% { opacity: 1; }
    98% { opacity: 0.85; }
    99% { opacity: 0.95; }
}

/* ---------- Responsive ---------- */
@media (max-width: 768px) {
    .main-header h1 { font-size: 1.5em; letter-spacing: 2px; }
    .main-header p { font-size: 0.85em; }
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
        
        #### ¿Te gustaría leer nuestra investigación?
        """)
        html_content = """
  <iframe class="scribd_iframe_embed" title="Suelo Inteligente Clasificación de fertilidad en parcelas.pdf" src="https://www.scribd.com/embeds/1093630991/content?start_page=1&view_mode=scroll&access_key=key-AjXNhNBRaDGHKzkdkB9l" tabindex="0" target="_blank" data-auto-height="false" data-aspect-ratio="0.7080062794348508" scrolling="no" width="400" height="600" frameborder="0" ></iframe> <p style="margin: 12px auto 6px auto; font-family: Helvetica,Arial,Sans-serif; font-size: 14px; line-height: normal; display: block;"> <a title="View Suelo Inteligente Clasificación de fertilidad en parcelas.pdf on Scribd" href="https://es.scribd.com/document/1093630991/Suelo-Inteligente-Clasificacion-de-fertilidad-en-parcelas-pdf#from_embed"  style="color: #098642; text-decoration: underline;"> Suelo Inteligente Clasificación de fertilidad en parcelas.pdf </a> by <a title="View Jesus Edgar Jaramillo Armenta's profile on Scribd" href="https://es.scribd.com/user/142590975/Jesus-Edgar-Jaramillo-Armenta#from_embed" target="_blank" style="color: #098642; text-decoration: underline;" > Jesus Edgar Jaramillo Armenta </a> </p> 
"""

# st.html inserta el HTML directamente en la página (no en iframe)
# st.html(html_content) 

# O usar st.iframe para aislar el contenido en un iframe
        st.iframe(html_content)
    
    elif menu == " Descargar Plantillas":
        descargar_plantillas()
        
    elif menu == "Análisis por Lote (CSV)":
        analisis_lote()
        
    elif menu == "Análisis Manual":
        analisis_manual()
        

if __name__ == "__main__":
    main()