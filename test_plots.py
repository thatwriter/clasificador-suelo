"""Prueba rápida del módulo de visualización"""
from datetime import datetime
from models.propiedad import Propiedad
from models.muestra import Muestra
from visualization.plots import GeneradorGraficas

# Crear muestras de prueba
m1 = Muestra(id='TEST-001', fecha_toma=datetime(2026, 1, 15))
m1.agregar_propiedad(Propiedad('pH', 6.5))
m1.agregar_propiedad(Propiedad('MO', 4.2))
m1.agregar_propiedad(Propiedad('P', 15.0))

m2 = Muestra(id='TEST-001', fecha_toma=datetime(2026, 3, 20))  # Mismo ID, fecha diferente
m2.agregar_propiedad(Propiedad('pH', 6.8))
m2.agregar_propiedad(Propiedad('MO', 3.9))
m2.agregar_propiedad(Propiedad('P', 18.0))

m3 = Muestra(id='TEST-002', fecha_toma=datetime(2026, 2, 10))
m3.agregar_propiedad(Propiedad('pH', 5.0))
m3.agregar_propiedad(Propiedad('MO', 2.1))
m3.agregar_propiedad(Propiedad('K', 0.8))

muestras = [m1, m2, m3]
plotter = GeneradorGraficas()

print("🎨 Generando gráficas de prueba...")

# 1. Barras para muestra individual
ruta1 = plotter.barras_vs_optimo(m1)
print(f"✓ Barras: {ruta1}")

# 2. Histograma de pH
ruta2 = plotter.histograma_extremos(muestras, 'pH')
print(f"✓ Histograma pH: {ruta2}")

# 3. Dispersión pH vs MO
ruta3 = plotter.dispersion_propiedad(muestras, 'pH', 'MO')
print(f"✓ Dispersión: {ruta3}")

# 4. Comparativa temporal (mismo ID)
ruta4 = plotter.comparativa_temporal(m1, m2)
print(f"✓ Comparativa: {ruta4}")

# 5. Alertas generales
ruta5 = plotter.alerta_valores_extremos(muestras)
print(f"✓ Alertas: {ruta5}")

# 6. Reporte completo
reporte = plotter.generar_reporte_grafico(muestras, "prueba_completa")
print(f"\n📊 Reporte completo: {len(reporte)} gráficas generadas")
for tipo, ruta in reporte.items():
    print(f"  • {tipo}: {ruta}")

print("\n✅ Prueba completada. Revisa la carpeta 'graficas/'")