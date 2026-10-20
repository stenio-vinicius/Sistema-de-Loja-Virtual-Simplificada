import pytest

from Classes.carrinho import Carrinho
from Classes.pagamento import (
    Pagamento,
    PagamentoPix,
    PagamentoDebito,
    PagamentoCredito,
    PagamentoBoleto,
)
from Classes.pedidos import Pedidos
from Classes.produto import Produto


@pytest.fixture(autouse=True)
def limpar_cupons():
    Pagamento.CUPONS_VALIDOS.clear()
    yield
    Pagamento.CUPONS_VALIDOS.clear()


def criar_carrinho(preco=100.00, quantidade=2):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", preco, "Azul", "M", 10)

    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, quantidade)
    return carrinho


def criar_pedido_pronto(forma="PIX"):
    """Pedido com carrinho de R$ 200,00, frete de 200 km (R$ 20,00) e pagamento definido."""
    pedido = Pedidos(criar_carrinho())
    pedido.DefinirFrete(200)
    pedido.DefinirPagamento(forma)
    return pedido


# ---------- Relação com as outras classes ----------

def test_pedido_nasce_pendente_com_o_carrinho_associado():
    carrinho = criar_carrinho()
    pedido = Pedidos(carrinho)

    assert pedido.status == "PENDENTE"
    assert pedido.carrinho is carrinho
    assert pedido.frete is None
    assert pedido.pagamento is None


def test_definir_frete_cria_o_frete_do_pedido():
    pedido = Pedidos(criar_carrinho())

    pedido.DefinirFrete(200)

    assert pedido.frete.valor == 20.0
    assert pedido.frete.prazo == 5


def test_definir_frete_acima_do_limite_nao_define(capsys):
    pedido = Pedidos(criar_carrinho())

    pedido.DefinirFrete(5000)
    capturado = capsys.readouterr()

    assert pedido.frete is None
    assert "Não foi possível calcular o frete" in capturado.out


@pytest.mark.parametrize("forma, classeEsperada", [
    ("PIX", PagamentoPix),
    ("CARTAO_DEBITO", PagamentoDebito),
    ("CARTAO_CREDITO", PagamentoCredito),
    ("BOLETO", PagamentoBoleto),
])
def test_definir_pagamento_cria_a_forma_certa(forma, classeEsperada):
    pedido = Pedidos(criar_carrinho())

    pedido.DefinirPagamento(forma)

    assert type(pedido.pagamento) is classeEsperada


def test_definir_pagamento_credito_guarda_as_parcelas():
    pedido = Pedidos(criar_carrinho())

    pedido.DefinirPagamento("CARTAO_CREDITO", parcelas=6)

    assert pedido.pagamento.parcelas == 6


def test_definir_pagamento_invalido_nao_define(capsys):
    pedido = Pedidos(criar_carrinho())

    pedido.DefinirPagamento("DINHEIRO")
    capturado = capsys.readouterr()

    assert pedido.pagamento is None
    assert "Forma de pagamento inválida" in capturado.out


def test_pagamento_invalido_nao_apaga_o_anterior():
    pedido = Pedidos(criar_carrinho())
    pedido.DefinirPagamento("PIX")

    pedido.DefinirPagamento("DINHEIRO")

    assert type(pedido.pagamento) is PagamentoPix


def test_aplicar_cupom_sem_pagamento_definido(capsys):
    pedido = Pedidos(criar_carrinho())

    pedido.AplicarCupom("PROMO10")
    capturado = capsys.readouterr()

    assert "Defina a forma de pagamento antes de aplicar um cupom" in capturado.out


# ---------- Confirmar o pedido ----------

def test_confirmar_pedido_paga_e_muda_status_e_gera_protocolo(capsys):
    pedido = criar_pedido_pronto("PIX")

    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    # (200 + 20 de frete) com 5% de desconto do Pix = 209
    assert pedido.status == "ENVIADO"
    assert pedido.pagamento.status == "PAGO"
    assert pedido.numeroProtocolo is not None
    assert len(pedido.numeroProtocolo) == 13
    assert "Valor total a pagar: R$ 209,00" in capturado.out
    assert "Pedido confirmado!" in capturado.out


def test_confirmar_pedido_com_cupom(capsys):
    Pagamento().CadastrarCupom("PROMO10", 10, 150.00)
    pedido = criar_pedido_pronto("PIX")

    pedido.AplicarCupom("PROMO10")
    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    # 200 - 10% = 180, + 20 de frete = 200, com 5% de desconto do Pix = 190
    assert "Cupom aplicado! 10% de desconto." in capturado.out
    assert "Valor total a pagar: R$ 190,00" in capturado.out


def test_confirmar_pedido_no_credito_parcelado(capsys):
    pedido = Pedidos(criar_carrinho())
    pedido.DefinirFrete(200)
    pedido.DefinirPagamento("CARTAO_CREDITO", parcelas=4)

    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    assert pedido.status == "ENVIADO"
    assert "Parcelamento: 4x de R$ 56,65" in capturado.out


def test_nao_confirma_com_carrinho_vazio(capsys):
    pedido = Pedidos(Carrinho())
    pedido.DefinirFrete(200)
    pedido.DefinirPagamento("PIX")

    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    assert pedido.status == "PENDENTE"
    assert "carrinho vazio" in capturado.out


def test_nao_confirma_sem_frete(capsys):
    pedido = Pedidos(criar_carrinho())
    pedido.DefinirPagamento("PIX")

    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    assert pedido.status == "PENDENTE"
    assert "Defina o frete" in capturado.out


def test_nao_confirma_sem_pagamento(capsys):
    pedido = Pedidos(criar_carrinho())
    pedido.DefinirFrete(200)

    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    assert pedido.status == "PENDENTE"
    assert "Defina a forma de pagamento" in capturado.out


def test_pedido_nao_confirma_duas_vezes():
    pedido = criar_pedido_pronto()
    pedido.ConfirmarPedido()
    protocoloAntes = pedido.numeroProtocolo

    pedido.ConfirmarPedido()

    assert pedido.numeroProtocolo == protocoloAntes


def test_nao_altera_frete_nem_pagamento_depois_de_confirmado(capsys):
    pedido = criar_pedido_pronto("PIX")
    pedido.ConfirmarPedido()
    freteAntes = pedido.frete
    capsys.readouterr()

    pedido.DefinirFrete(1000)
    pedido.DefinirPagamento("BOLETO")
    capturado = capsys.readouterr()

    assert pedido.frete is freteAntes
    assert type(pedido.pagamento) is PagamentoPix
    assert "Não é possível alterar o frete" in capturado.out
    assert "Não é possível alterar o pagamento" in capturado.out


# ---------- Entrega e cancelamento ----------

def test_pedido_marcar_como_entregue():
    pedido = criar_pedido_pronto()
    pedido.ConfirmarPedido()

    pedido.MarcarComoEntregue("10/10/2026")

    assert pedido.status == "ENTREGUE"
    assert pedido.dataEntrega == "10/10/2026"


def test_pedido_nao_entrega_se_ainda_pendente():
    pedido = Pedidos(criar_carrinho())

    pedido.MarcarComoEntregue("10/10/2026")

    assert pedido.status == "PENDENTE"
    assert pedido.dataEntrega is None


def test_pedido_nao_cancela_se_ja_entregue():
    pedido = criar_pedido_pronto()
    pedido.ConfirmarPedido()
    pedido.MarcarComoEntregue("10/10/2026")

    pedido.CancelarPedido()

    assert pedido.status == "ENTREGUE"


def test_pedido_cancela_se_pendente():
    pedido = Pedidos(criar_carrinho())

    pedido.CancelarPedido()

    assert pedido.status == "CANCELADO"


# ---------- Estoque, valor total e restauração do estado ----------

def test_confirmar_pedido_baixa_o_estoque():
    pedido = criar_pedido_pronto()
    produto = pedido.carrinho.itens[0]["produto"]

    pedido.ConfirmarPedido()

    assert produto.estoque == 8   # tinha 10 e foram vendidas 2


def test_nao_confirma_se_o_estoque_diminuiu_depois_de_montar_o_carrinho(capsys):
    pedido = criar_pedido_pronto()
    produto = pedido.carrinho.itens[0]["produto"]
    produto.ModificarProduto(estoque=1)

    pedido.ConfirmarPedido()
    capturado = capsys.readouterr()

    assert pedido.status == "PENDENTE"
    assert pedido.pagamento.status == "PENDENTE"   # nada foi cobrado
    assert produto.estoque == 1
    assert "Estoque insuficiente" in capturado.out


def test_valor_total_do_pedido():
    pedido = Pedidos(criar_carrinho())
    assert pedido.valorTotal is None

    pedido.DefinirFrete(200)
    assert pedido.valorTotal is None   # ainda falta o pagamento

    pedido.DefinirPagamento("PIX")
    assert pedido.valorTotal == pytest.approx(209.00)


def test_restaurar_estado_permite_marcar_como_entregue():
    pedido = Pedidos(Carrinho())
    pedido.RestaurarEstado("ENVIADO", "AB123456789BR", None)

    pedido.MarcarComoEntregue("10/10/2026")

    assert pedido.status == "ENTREGUE"
    assert pedido.numeroProtocolo == "AB123456789BR"
    assert pedido.dataEntrega == "10/10/2026"