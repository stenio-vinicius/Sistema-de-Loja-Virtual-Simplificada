import pytest

from Classes.frete import Frete

def test_frete_calcular_valor():
    frete = Frete()
    assert frete.CalcularFrete(200) == 20.0
 
 
def test_frete_acima_da_distancia_maxima_nao_calcula():
    frete = Frete()
    assert frete.CalcularFrete(5000) is None
 
 
@pytest.mark.parametrize("distancia, prazoEsperado", [
    (80, 2),
    (450, 5),
    (1200, 8),
    (1800, 11),
    (2200, 14),
    (2900, 17),
])
def test_frete_prazo_estimado_por_faixa(distancia, prazoEsperado):
    
    frete = Frete()
    assert frete.PrazoEstimado(distancia) == prazoEsperado
 
 
def test_frete_prazo_acima_da_distancia_maxima_retorna_none():
    frete = Frete()
    assert frete.PrazoEstimado(5000) is None


def test_frete_expoe_valor_e_prazo_calculados():
    frete = Frete()
    frete.CalcularFrete(200)
    frete.PrazoEstimado(200)

    assert frete.valor == 20.0
    assert frete.prazo == 5


def test_frete_guarda_a_distancia_calculada():
    frete = Frete()
    frete.CalcularFrete(200)

    assert frete.distancia == 200


def test_frete_acima_do_limite_nao_guarda_a_distancia():
    frete = Frete()
    frete.CalcularFrete(5000)

    assert frete.distancia is None