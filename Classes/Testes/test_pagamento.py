import pytest

from Classes.pagamento import (
    Pagamento,
    PagamentoPix,
    PagamentoDebito,
    PagamentoCredito,
    PagamentoBoleto,
    CriarPagamento,
)


@pytest.fixture(autouse=True)
def limpar_cupons():
    Pagamento.CUPONS_VALIDOS.clear()
    yield
    Pagamento.CUPONS_VALIDOS.clear()


# ---------- Classe-mãe: cupons e fluxo geral ----------

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


def test_pagamento_sem_forma_definida_nao_paga(capsys):
    pagamento = Pagamento()   # a classe-mãe sozinha não tem forma de pagamento

    status = pagamento.PagarPedido(valor=100.00, frete=10.00)
    capturado = capsys.readouterr()

    assert status == "PENDENTE"
    assert pagamento.status == "PENDENTE"
    assert "Forma de pagamento não definida" in capturado.out


def test_cupons_sao_compartilhados_entre_as_classes_filhas(capsys):
    PagamentoPix().CadastrarCupom("PROMO10", 10, 150.00)

    PagamentoDebito().AplicarCupom("PROMO10", 200.00)   # outra classe-filha enxerga o mesmo cupom
    capturado = capsys.readouterr()

    assert "Cupom aplicado! 10% de desconto." in capturado.out


# ---------- Herança ----------

@pytest.mark.parametrize("classe", [PagamentoPix, PagamentoDebito, PagamentoCredito, PagamentoBoleto])
def test_formas_de_pagamento_herdam_de_pagamento(classe):
    assert issubclass(classe, Pagamento)
    assert isinstance(classe(), Pagamento)


# ---------- Polimorfismo: mesma chamada, resultado diferente ----------

@pytest.mark.parametrize("pagamento, totalEsperado", [
    (PagamentoDebito(), 220.00),
    (PagamentoBoleto(), 220.00),
    (PagamentoPix(), 209.00),               # 5% de desconto sobre 220
    (PagamentoCredito(3), 220.00),          # até 3 parcelas: sem juros
    (PagamentoCredito(4), 226.60),          # acima de 3 parcelas: 3% de juros
])
def test_calcular_total_depende_da_forma_de_pagamento(pagamento, totalEsperado):
    assert pagamento.CalcularTotal(200.00, 20.00) == pytest.approx(totalEsperado)


# ---------- Pagar pedido ----------

def test_pagar_pedido_com_cupom_no_debito(capsys):
    pagamento = PagamentoDebito()
    pagamento.CadastrarCupom("PROMO10", 10, 150.00)
    pagamento.AplicarCupom("PROMO10", 200.00)

    status = pagamento.PagarPedido(valor=200.00, frete=20.00)
    capturado = capsys.readouterr()

    # 200 - 10% = 180, + 20 de frete = 200
    assert status == "PAGO"
    assert pagamento.status == "PAGO"
    assert "Valor total a pagar: R$ 200,00" in capturado.out
    assert "Forma de pagamento: CARTAO_DEBITO" in capturado.out


def test_pagar_pedido_com_pix_aplica_desconto(capsys):
    pagamento = PagamentoPix()

    pagamento.PagarPedido(valor=200.00, frete=20.00)
    capturado = capsys.readouterr()

    assert "Valor total a pagar: R$ 209,00" in capturado.out
    assert "Forma de pagamento: PIX" in capturado.out


def test_pagar_pedido_no_credito_mostra_o_parcelamento(capsys):
    pagamento = PagamentoCredito(4)

    pagamento.PagarPedido(valor=200.00, frete=20.00)
    capturado = capsys.readouterr()

    assert "Valor total a pagar: R$ 226,60" in capturado.out
    assert "Parcelamento: 4x de R$ 56,65" in capturado.out


def test_credito_com_parcelas_invalidas_usa_uma_parcela(capsys):
    pagamento = PagamentoCredito(0)
    capturado = capsys.readouterr()

    assert pagamento.parcelas == 1
    assert "Número de parcelas inválido" in capturado.out


def test_forma_do_pagamento_vem_da_classe():
    assert PagamentoPix().forma == "PIX"
    assert PagamentoBoleto().forma == "BOLETO"


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
    pagamento = CriarPagamento("CARTAO_CREDITO", parcelas=6)

    assert pagamento.parcelas == 6


def test_criar_pagamento_com_forma_invalida_retorna_none(capsys):
    pagamento = CriarPagamento("DINHEIRO")
    capturado = capsys.readouterr()

    assert pagamento is None
    assert "Forma de pagamento inválida: DINHEIRO" in capturado.out


# ---------- Getter do desconto ----------

def test_desconto_comeca_zerado_e_muda_com_o_cupom():
    pagamento = PagamentoPix()
    pagamento.CadastrarCupom("PROMO10", 10, 150.00)

    assert pagamento.desconto == 0

    pagamento.AplicarCupom("PROMO10", 200.00)

    assert pagamento.desconto == 10