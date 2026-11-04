import sys
sys.path.insert(2,"../desarrollo")
from utils.config import VALORES_REFERENCIA, CLASIFICACIONES

def test_valores_referencia_completos():
    assert set(VALORES_REFERENCIA.keys()) == {'pH', 'MO', 'P', 'Ca', 'Mg', 'K', 'CICE', 'C_BM'}

def test_propiedades_valor_referencia():
    ref = VALORES_REFERENCIA['pH']
    assert ref.optimo == 7.5
    assert ref.minimo == 5.0
    assert ref.rango_aceptable_min == 2.5  # 0.5 * 5.0
    assert ref.rango_aceptable_max == 15.0 # 2.0 * 7.5

def test_clasificaciones_rangos_validos():
    for cat, (min_v, max_v) in CLASIFICACIONES.items():
        assert min_v <= max_v
        assert isinstance(cat, str)