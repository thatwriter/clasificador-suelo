<<<<<<< HEAD
import sys
sys.path.insert(2,"../desarrollo")
import pytest
from models.propiedad import Propiedad

def test_normalizacion_optimo(ph_optimo):
    assert ph_optimo.normalizar_valor() == pytest.approx(1.0)

def test_normalizacion_deficit(ph_moderado):
    assert ph_moderado.normalizar_valor() == pytest.approx(5.25 / 7.5)

# Reemplaza solo la función test_evaluar_fertilidad_piecewise en tests/test_propiedad.py
def test_evaluar_fertilidad_piecewise():
    # Caso 0 ≤ x ≤ 1
    p = Propiedad('pH', 3.75)  # 3.75/7.5 = 0.5
    assert p.evaluar_fertilidad() == pytest.approx(0.5)
    
    # Caso 1 < x ≤ 2
    p = Propiedad('pH', 11.25) # 11.25/7.5 = 1.5
    assert p.evaluar_fertilidad() == pytest.approx(0.5)  # 2 - 1.5
    
    # Caso x > 2
    p = Propiedad('pH', 16.0)  # 16/7.5 ≈ 2.13
    assert p.evaluar_fertilidad() == 0.0
    
    # Caso x < 0 (teórico)
    p = Propiedad('pH', -1.0)
    assert p.evaluar_fertilidad() == 0.0

def test_desviacion_optima(ph_optimo):
    assert ph_optimo.calcular_desviacion() == pytest.approx(0.0)

def test_rango_aceptable(ph_optimo, ph_deficit, ph_exceso):
    assert ph_optimo.esta_en_rango_aceptable() is True
    assert ph_deficit.esta_en_rango_aceptable() is False   # 3.75 < 2.5
    assert ph_exceso.esta_en_rango_aceptable() is False    # 15.0 > 15.0 (límite estricto)

def test_clasificacion_ph_optimo(ph_optimo):
    assert ph_optimo.obtener_clasificacion() == 'Muy Alta Calidad'

def test_clasificacion_ph_deficit_extremo(ph_deficit):
    # 2.0 / 7.5 ≈ 0.2667 (cae en rango "Baja Calidad" 0.20-0.39)
=======
import sys
sys.path.insert(2,"../desarrollo")
import pytest
from models.propiedad import Propiedad

def test_normalizacion_optimo(ph_optimo):
    assert ph_optimo.normalizar_valor() == pytest.approx(1.0)

def test_normalizacion_deficit(ph_moderado):
    assert ph_moderado.normalizar_valor() == pytest.approx(5.25 / 7.5)

# Reemplaza solo la función test_evaluar_fertilidad_piecewise en tests/test_propiedad.py
def test_evaluar_fertilidad_piecewise():
    # Caso 0 ≤ x ≤ 1
    p = Propiedad('pH', 3.75)  # 3.75/7.5 = 0.5
    assert p.evaluar_fertilidad() == pytest.approx(0.5)
    
    # Caso 1 < x ≤ 2
    p = Propiedad('pH', 11.25) # 11.25/7.5 = 1.5
    assert p.evaluar_fertilidad() == pytest.approx(0.5)  # 2 - 1.5
    
    # Caso x > 2
    p = Propiedad('pH', 16.0)  # 16/7.5 ≈ 2.13
    assert p.evaluar_fertilidad() == 0.0
    
    # Caso x < 0 (teórico)
    p = Propiedad('pH', -1.0)
    assert p.evaluar_fertilidad() == 0.0

def test_desviacion_optima(ph_optimo):
    assert ph_optimo.calcular_desviacion() == pytest.approx(0.0)

def test_rango_aceptable(ph_optimo, ph_deficit, ph_exceso):
    assert ph_optimo.esta_en_rango_aceptable() is True
    assert ph_deficit.esta_en_rango_aceptable() is False   # 3.75 < 2.5
    assert ph_exceso.esta_en_rango_aceptable() is False    # 15.0 > 15.0 (límite estricto)

def test_clasificacion_ph_optimo(ph_optimo):
    assert ph_optimo.obtener_clasificacion() == 'Muy Alta Calidad'

def test_clasificacion_ph_deficit_extremo(ph_deficit):
    # 2.0 / 7.5 ≈ 0.2667 (cae en rango "Baja Calidad" 0.20-0.39)
>>>>>>> d600836cf7352c426d09819cab589b00f4f36f77
    assert ph_deficit.normalizar_valor() == pytest.approx(2.0 / 7.5)