<<<<<<< HEAD
from data.template import generar_plantilla_vacia, generar_plantilla_optima
from data.loader import CargadorDatos
from data.export import ExportadorResultados
import os

# 1. Generar plantillas
generar_plantilla_vacia()
generar_plantilla_optima()
print("📄 Plantillas generadas en la raíz.")

# 2. Simular carga y procesamiento
loader = CargadorDatos()
exporter = ExportadorResultados()

# Usa el ejemplo generado
df_crudo = loader.cargar_csv("ejemplo_valores_optimos.csv")
df_limpio, alertas = loader.validar_y_limpiar(df_crudo, modo="individual")
print("\n🔍 Alertas de validación:")
for a in alertas: print(f"  {a}")

muestras = loader.convertir_a_muestras(df_limpio)
if muestras:
    print(f"\n Muestra procesada: {muestras[0]}")
    
    # 3. Exportar resultados
    exporter.a_csv(muestras)
    exporter.a_json(muestras)
    exporter.a_txt(muestras)
    print("\n✅ Pipeline completado. Revisa la carpeta 'resultados/'")
else:
=======
from data.template import generar_plantilla_vacia, generar_plantilla_optima
from data.loader import CargadorDatos
from data.export import ExportadorResultados
import os

# 1. Generar plantillas
generar_plantilla_vacia()
generar_plantilla_optima()
print("📄 Plantillas generadas en la raíz.")

# 2. Simular carga y procesamiento
loader = CargadorDatos()
exporter = ExportadorResultados()

# Usa el ejemplo generado
df_crudo = loader.cargar_csv("ejemplo_valores_optimos.csv")
df_limpio, alertas = loader.validar_y_limpiar(df_crudo, modo="individual")
print("\n🔍 Alertas de validación:")
for a in alertas: print(f"  {a}")

muestras = loader.convertir_a_muestras(df_limpio)
if muestras:
    print(f"\n Muestra procesada: {muestras[0]}")
    
    # 3. Exportar resultados
    exporter.a_csv(muestras)
    exporter.a_json(muestras)
    exporter.a_txt(muestras)
    print("\n✅ Pipeline completado. Revisa la carpeta 'resultados/'")
else:
>>>>>>> d600836cf7352c426d09819cab589b00f4f36f77
    print("⚠️ No se generaron muestras válidas.")