# Reemplaza el archivo completo tests/conftest.py
import pytest
from datetime import datetime
from models.propiedad import Propiedad
from models.muestra import Muestra

@pytest.fixture
def ph_optimo():
    return Propiedad(nombre='pH', valor=7.5)

@pytest.fixture
def ph_deficit():
    return Propiedad(nombre='pH', valor=2.0)  # 2.0 < 2.5 (0.5 * mínimo)

@pytest.fixture
def ph_exceso():
    return Propiedad(nombre='pH', valor=15.1)  # 15.1 > 15.0 (2.0 * máximo)

@pytest.fixture
def ph_moderado():
    return Propiedad(nombre='pH', valor=5.25)

@pytest.fixture
def muestra_valida():
    m = Muestra(id='TEST-001', fecha_toma=datetime.now())
    m.agregar_propiedad(Propiedad('pH', 6.0))
    m.agregar_propiedad(Propiedad('MO', 4.0))
    m.agregar_propiedad(Propiedad('P', 14.0))
    return m

@pytest.fixture
def muestra_con_nulos():
    m = Muestra(id='TEST-002', fecha_toma=datetime.now())
    m.agregar_propiedad(Propiedad('pH', 6.0))
    m.agregar_propiedad(Propiedad('MO', 0.0))
    m.agregar_propiedad(Propiedad('P', 14.0))
    return m