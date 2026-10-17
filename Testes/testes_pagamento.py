import pytest

from Classes import pagamento

@pytest.fixture(autouse=True)
def limpar_cupons():
    
    Pagamento.CUPONS_VALIDOS.clear()
    yield
    Pagamento.CUPONS_VALIDOS.clear()
 
 
def test_pagamento_formatar_moeda():
    pagamento = Pagamento()
    assert pagamento.FormatarMoeda(150.5) == "150,50"
 
 
def test_pagamento_aplicar_cupom_valido(capsys):
    pagamento = Pagamento()
    pagamento.CadastrarCupom("PROMO10", 10, 150.00)
 
    pagamento.AplicarCupom("PROMO10", 200.00)
    capturado = capsys.readouterr()
 
    assert "Cupom aplicado! 10% de desconto." in capturado.out
 
 
def test_pagamento_cupom_abaixo_do_minimo_nao_aplica(capsys):
    pagamento = Pagamento()
    pagamento.CadastrarCupom("PROMO10", 10, 150.00)
 
    pagamento.AplicarCupom("PROMO10", 100.00)
    capturado = capsys.readouterr()
 
    assert "só é válido para compras acima" in capturado.out
 
 
def test_pagamento_pagar_pedido_com_desconto(capsys):
    pagamento = Pagamento()
    pagamento.CadastrarCupom("PROMO10", 10, 150.00)
    pagamento.AplicarCupom("PROMO10", 200.00)
 
    status = pagamento.PagarPedido(valor=200.00, frete=20.00, formaPagamento="PIX")
    capturado = capsys.readouterr()
 
    assert status == "PAGO"
    assert pagamento.status == "PAGO"
    assert "Valor total a pagar: R$ 200,00" in capturado.out
 
 
def test_pagamento_forma_invalida_nao_paga():
    pagamento = Pagamento()
    status = pagamento.PagarPedido(valor=100.00, frete=10.00, formaPagamento="DINHEIRO")
 
    assert status == "PENDENTE"
    assert pagamento.status == "PENDENTE"
