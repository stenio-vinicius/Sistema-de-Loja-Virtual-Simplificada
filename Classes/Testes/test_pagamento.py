import pytest

from Classes.pagamento import (
    Pagamento,
    PagamentoPix,
    PagamentoDebito,
    PagamentoCredito,
    PagamentoBoleto,
    CriarPagamento,
)


# ---------- Classe-mãe ----------

def test_pagamento_formatar_moeda():
    assert Pagamento().FormatarMoeda(150.5) == "150,50"


def test_pagamento_sem_forma_definida_nao_paga(capsys):
    pagamento = Pagamento()   # a classe-mãe sozinha não tem forma de pagamento

    status = pagamento.PagarPedido(valor=100.00, frete=10.00)
    capturado = capsys.readouterr()

    assert status == "PENDENTE"
    assert pagamento.status == "PENDENTE"
    assert "Forma de pagamento não definida" in capturado.out


def test_desconto_comeca_zerado():
    assert Pagamento().desconto == 0


def test_aplicar_desconto_reduz_o_total():
    pagamento = PagamentoDebito()
    pagamento.AplicarDesconto(20.00)

    # 200 - 20 = 180, + 20 de frete = 200
    assert pagamento.desconto == 20.00
    assert pagamento.CalcularTotal(200.00, 20.00) == 200.00


def test_desconto_negativo_e_ignorado():
    pagamento = PagamentoDebito()
    pagamento.AplicarDesconto(-50.00)

    assert pagamento.desconto == 0
    assert pagamento.CalcularTotal(200.00, 20.00) == 220.00


def test_desconto_maior_que_o_valor_nao_deixa_o_total_negativo():
    pagamento = PagamentoDebito()
    pagamento.AplicarDesconto(500.00)

    assert pagamento.CalcularTotal(200.00, 20.00) == 20.00   # sobra só o frete, nunca menos que zero


# ---------- Herança e polimorfismo ----------

@pytest.mark.parametrize("classe", [PagamentoPix, PagamentoDebito, PagamentoCredito, PagamentoBoleto])
def test_formas_de_pagamento_herdam_de_pagamento(classe):
    assert issubclass(classe, Pagamento)
    assert isinstance(classe(), Pagamento)


@pytest.mark.parametrize("pagamento, totalEsperado", [
    (PagamentoDebito(), 220.00),
    (PagamentoBoleto(), 220.00),
    (PagamentoPix(), 209.00),               # 5% de desconto sobre 220
    (PagamentoCredito(3), 220.00),          # até 3 parcelas: sem juros
    (PagamentoCredito(4), 226.60),          # acima de 3 parcelas: 3% de juros
])
def test_calcular_total_depende_da_forma_de_pagamento(pagamento, totalEsperado):
    assert pagamento.CalcularTotal(200.00, 20.00) == pytest.approx(totalEsperado)


def test_forma_do_pagamento_vem_da_classe():
    assert PagamentoPix().forma == "PIX"
    assert PagamentoBoleto().forma == "BOLETO"


# ---------- Pagar ----------

def test_pagar_pedido_com_desconto_no_debito(capsys):
    pagamento = PagamentoDebito()
    pagamento.AplicarDesconto(20.00)

    status = pagamento.PagarPedido(valor=200.00, frete=20.00)
    capturado = capsys.readouterr()

    assert status == "PAGO"
    assert pagamento.status == "PAGO"
    assert "Valor total a pagar: R$ 200,00" in capturado.out
    assert "Forma de pagamento: CARTAO_DEBITO" in capturado.out


def test_pagar_pedido_com_pix_aplica_desconto(capsys):
    PagamentoPix().PagarPedido(valor=200.00, frete=20.00)
    capturado = capsys.readouterr()

    assert "Valor total a pagar: R$ 209,00" in capturado.out
    assert "Forma de pagamento: PIX" in capturado.out


def test_pagar_pedido_no_credito_mostra_o_parcelamento(capsys):
    PagamentoCredito(4).PagarPedido(valor=200.00, frete=20.00)
    capturado = capsys.readouterr()

    assert "Valor total a pagar: R$ 226,60" in capturado.out
    assert "Parcelamento: 4x de R$ 56,65" in capturado.out


def test_credito_com_parcelas_invalidas_usa_uma_parcela(capsys):
    pagamento = PagamentoCredito(0)
    capturado = capsys.readouterr()

    assert pagamento.parcelas == 1
    assert "Número de parcelas inválido" in capturado.out


# ---------- CriarPagamento ----------

@pytest.mark.parametrize("forma, classeEsperada", [
    ("PIX", PagamentoPix),
    ("pix", PagamentoPix),                  # ignora maiúsculas e minúsculas
    ("CARTAO_DEBITO", PagamentoDebito),
    ("CARTAO_CREDITO", PagamentoCredito),
    ("BOLETO", PagamentoBoleto),
])
def test_criar_pagamento_escolhe_a_classe_certa(forma, classeEsperada):
    assert type(CriarPagamento(forma)) is classeEsperada


def test_criar_pagamento_credito_recebe_as_parcelas():
    assert CriarPagamento("CARTAO_CREDITO", parcelas=6).parcelas == 6


def test_criar_pagamento_com_forma_invalida_retorna_none(capsys):
    pagamento = CriarPagamento("DINHEIRO")
    capturado = capsys.readouterr()

    assert pagamento is None
    assert "Forma de pagamento inválida: DINHEIRO" in capturado.out
