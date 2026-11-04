import pytest
import numpy as np

def test_calidad_acumulada_valida(muestra_valida):
    # pH=6.0→0.8, MO=4.0→0.666, P=14.0→0.7
    # f(0.8)=0.8, f(0.666)=0.666, f(0.7)=0.7
    esperado = (0.8 + 0.6666666666 + 0.7) / 3
    assert muestra_valida.calcular_calidad_acumulada() == pytest.approx(esperado, rel=1e-4)

def test_calidad_acumulada_filtra_extremos(muestra_con_nulos):
    # MO=0.0 → fuera de rango aceptable (min=2.0 → 0.5*min=1.0)
    # Solo se consideran pH y P
    esperado = (0.8 + 0.7) / 2  # f(0.8)=0.8, f(0.7)=0.7
    assert muestra_con_nulos.calcular_calidad_acumulada() == pytest.approx(esperado, rel=1e-4)

def test_distancia_euclidiana_optima(muestra_valida):
    # x_norm: [0.8, 0.666, 0.7] → Δ: [-0.2, -0.333, -0.3]
    d2 = np.sqrt((-0.2)**2 + (-0.3333333)**2 + (-0.3)**2)
    assert muestra_valida.calcular_distancia_euclidiana() == pytest.approx(d2, rel=1e-4)

def test_distancia_manhattan_optima(muestra_valida):
    d1 = abs(-0.2) + abs(-0.3333333) + abs(-0.3)
    assert muestra_valida.calcular_distancia_manhattan() == pytest.approx(d1, rel=1e-4)

def test_estadisticas_validas(muestra_valida):
    stats = muestra_valida.calcular_estadisticas()
    valores = [0.8, 0.6666666666, 0.7]
    assert stats['media'] == pytest.approx(np.mean(valores), rel=1e-4)
    assert stats['desviacion_estandar'] == pytest.approx(np.std(valores, ddof=1), rel=1e-4)
    assert stats['varianza'] == pytest.approx(stats['desviacion_estandar']**2, rel=1e-4)
    assert stats['n_propiedades'] == 3

def test_nivel_fertilidad(muestra_valida):
    # Calidad ~0.72 → Alta Calidad
    assert muestra_valida.obtener_nivel_fertilidad() == 'Alta'

def test_muestra_vacia():
    from models.muestra import Muestra
    from datetime import datetime
    m = Muestra(id='VACIO', fecha_toma=datetime.now())
    assert m.calcular_calidad_acumulada() == 0.0
    assert m.calcular_distancia_euclidiana() == float('inf')
    assert m.calcular_estadisticas()['n_propiedades'] == 0