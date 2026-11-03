import re

import pytest

from Classes.carrinho import Carrinho
from Classes.cupom import Cupom
from Classes.pagamento import PagamentoCredito, PagamentoPix
from Classes.pedidos import Pedidos
from Classes.produto import Produto, ProdutoDigital


def criar_produto(sku="CAM-001", nome="Camisa", categoria="Roupas", preco=100.00, estoque=10):
    produto = Produto()
    produto.CadastrarProduto(nome, categoria, preco, "Azul", "M", estoque, sku)
    return produto


def criar_ebook(estoque=100):
    ebook = ProdutoDigital()
    ebook.CadastrarProduto("E-book", "Livros", 50.00, estoque=estoque, sku="EBK-001")
    return ebook


def criar_carrinho(quantidade=2, produto=None):
    carrinho = Carrinho()
    carrinho.AdicionarItem(produto if produto is not None else criar_produto(), quantidade)
    return carrinho


def criar_cupom(**opcoes):
    dados = {"codigo": "PROMO10", "percentual": 10, "valorMinimo": 150.00}
    dados.update(opcoes)

    cupom = Cupom()
    cupom.CadastrarCupom(**dados)
    return cupom


def criar_pedido(carrinho=None):
    return Pedidos(carrinho if carrinho is not None else criar_carrinho(), "05/10/2026")


def criar_pedido_com_frete(carrinho=None):
    """Carrinho de R$ 200,00 e frete de 200 km (R$ 20,00)."""
    pedido = criar_pedido(carrinho)
    pedido.DefinirFrete(200)
    return pedido


def criar_pedido_pago(forma="PIX"):
    pedido = criar_pedido_com_frete()
    pedido.PagarPedido(forma, data="06/10/2026")
    return pedido


def produto_do_pedido(pedido):
    return pedido.carrinho.itens[0]["produto"]


# =========================================================
# Criação
# =========================================================

def test_pedido_nasce_criado_com_protocolo_e_sem_rastreio():
    carrinho = criar_carrinho()
    pedido = Pedidos(carrinho, "05/10/2026")

    assert pedido.status == "CRIADO"
    assert pedido.carrinho is carrinho
    assert pedido.data == "05/10/2026"
    assert re.fullmatch(r"PED\d{8}", pedido.numeroProtocolo)
    assert pedido.codigoRastreio is None
    assert pedido.frete is None
    assert pedido.pagamento is None
    assert pedido.cupom is None


def test_pedidos_diferentes_tem_protocolos_diferentes():
    assert criar_pedido().numeroProtocolo != criar_pedido().numeroProtocolo


# =========================================================
# Frete
# =========================================================

def test_definir_frete_calcula_valor_e_prazo():
    pedido = criar_pedido_com_frete()

    assert pedido.frete.valor == 20.0
    assert pedido.frete.prazo == 5


def test_definir_frete_acima_do_limite_nao_define(capsys):
    pedido = criar_pedido()

    pedido.DefinirFrete(5000)
    capturado = capsys.readouterr()

    assert pedido.frete is None
    assert "Não foi possível calcular o frete" in capturado.out


def test_definir_frete_com_distancia_negativa(capsys):
    pedido = criar_pedido()

    pedido.DefinirFrete(-10)
    capturado = capsys.readouterr()

    assert pedido.frete is None
    assert "A distância não pode ser negativa." in capturado.out


def test_produto_fisico_exige_a_distancia(capsys):
    pedido = criar_pedido()

    pedido.DefinirFrete()
    capturado = capsys.readouterr()

    assert pedido.frete is None
    assert "Informe a distância" in capturado.out


def test_pedido_so_com_produtos_digitais_nao_soma_frete():
    pedido = criar_pedido(criar_carrinho(1, criar_ebook()))

    pedido.DefinirFrete()   # nem precisa de distância

    assert pedido.frete.valor == 0.0
    assert pedido.frete.prazo == 0
    assert pedido.valorPrevisto == 50.00


def test_pedido_misto_cobra_frete_pelo_produto_fisico():
    carrinho = criar_carrinho(2)
    carrinho.AdicionarItem(criar_ebook(), 1)
    pedido = criar_pedido(carrinho)

    pedido.DefinirFrete(200)

    assert pedido.frete.valor == 20.0
    assert pedido.valorPrevisto == 270.00   # 200 + 50 + 20 de frete


def test_nao_altera_o_frete_depois_de_pago(capsys):
    pedido = criar_pedido_pago()
    freteAntes = pedido.frete
    capsys.readouterr()

    pedido.DefinirFrete(1000)
    capturado = capsys.readouterr()

    assert pedido.frete is freteAntes
    assert "Não é possível alterar o frete" in capturado.out


# =========================================================
# Cupom
# =========================================================

def test_aplicar_cupom_valido(capsys):
    pedido = criar_pedido_com_frete()
    cupom = criar_cupom()

    assert pedido.AplicarCupom(cupom, "05/10/2026") is True
    capturado = capsys.readouterr()

    assert pedido.cupom is cupom
    assert pedido.valorDesconto == 20.00
    assert "Cupom 'PROMO10' aplicado! Desconto de R$ 20,00." in capturado.out
    assert pedido.valorPrevisto == 200.00   # 200 - 20 + 20 de frete


def test_cupom_recusado_nao_altera_o_pedido(capsys):
    pedido = criar_pedido_com_frete()

    assert pedido.AplicarCupom(criar_cupom(validade="01/10/2026"), "05/10/2026") is False
    capturado = capsys.readouterr()

    assert pedido.cupom is None
    assert pedido.valorDesconto == 0
    assert "expirado em 01/10/2026" in capturado.out


def test_cupom_so_desconta_os_itens_das_categorias_elegiveis():
    carrinho = criar_carrinho(2)
    carrinho.AdicionarItem(criar_ebook(), 1)
    pedido = criar_pedido(carrinho)

    pedido.AplicarCupom(criar_cupom(categorias=["Roupas"]), "05/10/2026")

    assert pedido.valorDesconto == 20.00   # 10% de R$ 200,00; o e-book fica de fora


def test_desconto_nunca_passa_do_valor_dos_produtos():
    pedido = criar_pedido_com_frete()

    pedido.AplicarCupom(criar_cupom(percentual=100), "05/10/2026")

    assert pedido.valorDesconto == 200.00
    assert pedido.valorPrevisto == 20.00   # sobra só o frete; o total nunca fica negativo


def test_nao_aplica_cupom_em_pedido_pago(capsys):
    pedido = criar_pedido_pago()
    capsys.readouterr()

    assert pedido.AplicarCupom(criar_cupom(), "06/10/2026") is False
    assert "Não é possível aplicar cupom" in capsys.readouterr().out


# =========================================================
# Pagamento
# =========================================================

def test_pagar_pedido_baixa_o_estoque_e_muda_o_status(capsys):
    pedido = criar_pedido_com_frete()

    assert pedido.PagarPedido("PIX", data="06/10/2026") is True
    capturado = capsys.readouterr()

    # (200 + 20 de frete) com 5% de desconto do Pix = 209
    assert pedido.status == "PAGO"
    assert pedido.dataPagamento == "06/10/2026"
    assert type(pedido.pagamento) is PagamentoPix
    assert pedido.pagamento.status == "PAGO"
    assert pedido.valorTotal == pytest.approx(209.00)
    assert produto_do_pedido(pedido).estoque == 8
    assert "Valor total a pagar: R$ 209,00" in capturado.out
    assert "Pagamento confirmado!" in capturado.out


def test_pedido_criado_ainda_nao_baixa_o_estoque():
    pedido = criar_pedido_com_frete()

    assert produto_do_pedido(pedido).estoque == 10
    assert pedido.valorTotal is None


def test_pagar_com_cupom_registra_o_uso(capsys):
    pedido = criar_pedido_com_frete()
    cupom = criar_cupom()
    pedido.AplicarCupom(cupom, "05/10/2026")

    pedido.PagarPedido("PIX", data="06/10/2026")
    capturado = capsys.readouterr()

    # 200 - 20 de cupom = 180, + 20 de frete = 200, com 5% do Pix = 190
    assert "Valor total a pagar: R$ 190,00" in capturado.out
    assert cupom.usos == 1


def test_pagar_no_credito_parcelado(capsys):
    pedido = criar_pedido_com_frete()

    pedido.PagarPedido("CARTAO_CREDITO", parcelas=4, data="06/10/2026")
    capturado = capsys.readouterr()

    assert type(pedido.pagamento) is PagamentoCredito
    assert pedido.pagamento.parcelas == 4
    assert "Parcelamento: 4x de R$ 56,65" in capturado.out


def test_pagar_pedido_so_com_produtos_digitais(capsys):
    pedido = criar_pedido(criar_carrinho(1, criar_ebook()))
    pedido.DefinirFrete()

    pedido.PagarPedido("PIX", data="06/10/2026")
    capturado = capsys.readouterr()

    assert "Valor total a pagar: R$ 47,50" in capturado.out   # R$ 50,00 com 5% do Pix, sem frete


def test_frete_e_obrigatorio_antes_do_pagamento(capsys):
    pedido = criar_pedido()

    assert pedido.PagarPedido("PIX", data="06/10/2026") is False
    capturado = capsys.readouterr()

    assert pedido.status == "CRIADO"
    assert "O frete precisa ser calculado antes do pagamento." in capturado.out
    assert produto_do_pedido(pedido).estoque == 10


def test_nao_paga_se_o_estoque_nao_cobre_o_pedido(capsys):
    pedido = criar_pedido_com_frete()
    produto_do_pedido(pedido).ModificarProduto(estoque=1)

    assert pedido.PagarPedido("PIX", data="06/10/2026") is False
    capturado = capsys.readouterr()

    assert pedido.status == "CRIADO"
    assert produto_do_pedido(pedido).estoque == 1
    assert "Estoque insuficiente" in capturado.out


def test_forma_de_pagamento_invalida_nao_paga_nem_baixa_o_estoque(capsys):
    pedido = criar_pedido_com_frete()

    assert pedido.PagarPedido("DINHEIRO", data="06/10/2026") is False
    capturado = capsys.readouterr()

    assert pedido.status == "CRIADO"
    assert pedido.pagamento is None
    assert produto_do_pedido(pedido).estoque == 10
    assert "Forma de pagamento inválida" in capturado.out


def test_cupom_esgotado_entre_a_criacao_e_o_pagamento(capsys):
    cupom = criar_cupom(usoMaximo=1)
    primeiro = criar_pedido_com_frete()
    segundo = criar_pedido_com_frete()
    primeiro.AplicarCupom(cupom, "05/10/2026")
    segundo.AplicarCupom(cupom, "05/10/2026")   # ainda havia um uso disponível

    assert primeiro.PagarPedido("PIX", data="06/10/2026") is True
    capsys.readouterr()
    assert segundo.PagarPedido("PIX", data="06/10/2026") is False
    capturado = capsys.readouterr()

    assert segundo.status == "CRIADO"
    assert "esgotado" in capturado.out


def test_cupom_expirado_entre_a_criacao_e_o_pagamento(capsys):
    pedido = criar_pedido_com_frete()
    pedido.AplicarCupom(criar_cupom(validade="06/10/2026"), "05/10/2026")
    capsys.readouterr()

    assert pedido.PagarPedido("PIX", data="07/10/2026") is False
    assert "expirado em 06/10/2026" in capsys.readouterr().out


def test_nao_paga_duas_vezes(capsys):
    pedido = criar_pedido_pago()
    capsys.readouterr()

    assert pedido.PagarPedido("PIX", data="07/10/2026") is False
    assert "Não é possível pagar um pedido com status 'PAGO'" in capsys.readouterr().out
    assert produto_do_pedido(pedido).estoque == 8   # o estoque foi baixado uma vez só


# =========================================================
# Envio e entrega
# =========================================================

def test_enviar_pedido_pago_gera_o_codigo_de_rastreio(capsys):
    pedido = criar_pedido_pago()
    capsys.readouterr()

    assert pedido.EnviarPedido() is True
    capturado = capsys.readouterr()

    assert pedido.status == "ENVIADO"
    assert re.fullmatch(r"[A-Z]{2}\d{9}BR", pedido.codigoRastreio)
    assert pedido.codigoRastreio in capturado.out


def test_nao_envia_pedido_que_ainda_nao_foi_pago(capsys):
    pedido = criar_pedido_com_frete()

    assert pedido.EnviarPedido() is False

    assert pedido.status == "CRIADO"
    assert pedido.codigoRastreio is None
    assert "Só é possível enviar um pedido pago" in capsys.readouterr().out


def test_marcar_como_entregue():
    pedido = criar_pedido_pago()
    pedido.EnviarPedido()

    assert pedido.MarcarComoEntregue("12/10/2026") is True

    assert pedido.status == "ENTREGUE"
    assert pedido.dataEntrega == "12/10/2026"


def test_nao_entrega_pedido_que_nao_foi_enviado(capsys):
    pedido = criar_pedido_pago()
    capsys.readouterr()

    assert pedido.MarcarComoEntregue("12/10/2026") is False

    assert pedido.status == "PAGO"
    assert pedido.dataEntrega is None
    assert "Não é possível marcar como entregue" in capsys.readouterr().out


# =========================================================
# Cancelamento
# =========================================================

def test_cancelar_pedido_criado_nao_mexe_no_estoque():
    pedido = criar_pedido_com_frete()

    assert pedido.CancelarPedido("05/10/2026") is True

    assert pedido.status == "CANCELADO"
    assert pedido.dataCancelamento == "05/10/2026"
    assert produto_do_pedido(pedido).estoque == 10


def test_cancelar_pedido_pago_estorna_o_estoque(capsys):
    pedido = criar_pedido_pago()
    assert produto_do_pedido(pedido).estoque == 8
    capsys.readouterr()

    assert pedido.CancelarPedido("08/10/2026") is True
    capturado = capsys.readouterr()

    assert pedido.status == "CANCELADO"
    assert produto_do_pedido(pedido).estoque == 10
    assert "Estoque estornado." in capturado.out


def test_cancelar_no_ultimo_dia_da_janela():
    pedido = criar_pedido_pago()   # pago em 06/10/2026

    assert pedido.CancelarPedido("13/10/2026") is True   # 7 dias depois


def test_nao_cancela_pedido_pago_fora_da_janela(capsys):
    pedido = criar_pedido_pago()   # pago em 06/10/2026
    capsys.readouterr()

    assert pedido.CancelarPedido("14/10/2026") is False   # 8 dias depois
    capturado = capsys.readouterr()

    assert pedido.status == "PAGO"
    assert produto_do_pedido(pedido).estoque == 8
    assert "prazo de cancelamento (7 dias" in capturado.out


@pytest.mark.parametrize("etapas", [["enviar"], ["enviar", "entregar"]])
def test_nao_cancela_pedido_enviado_ou_entregue(etapas, capsys):
    pedido = criar_pedido_pago()
    pedido.EnviarPedido()
    if "entregar" in etapas:
        pedido.MarcarComoEntregue("12/10/2026")
    status = pedido.status
    capsys.readouterr()

    assert pedido.CancelarPedido("13/10/2026") is False

    assert pedido.status == status
    assert f"Não é possível cancelar um pedido com status '{status}'" in capsys.readouterr().out


def test_nao_cancela_pedido_ja_cancelado(capsys):
    pedido = criar_pedido_com_frete()
    pedido.CancelarPedido("05/10/2026")
    capsys.readouterr()

    assert pedido.CancelarPedido("05/10/2026") is False
    assert "status 'CANCELADO'" in capsys.readouterr().out


def test_nao_paga_pedido_cancelado(capsys):
    pedido = criar_pedido_com_frete()
    pedido.CancelarPedido("05/10/2026")
    capsys.readouterr()

    assert pedido.PagarPedido("PIX", data="06/10/2026") is False
    assert "Não é possível pagar um pedido com status 'CANCELADO'" in capsys.readouterr().out


# =========================================================
# Valores e restauração
# =========================================================

def test_valor_previsto_so_existe_depois_do_frete():
    pedido = criar_pedido()
    assert pedido.valorPrevisto is None

    pedido.DefinirFrete(200)
    assert pedido.valorPrevisto == 220.00


def test_restaurar_estado_permite_continuar_o_pedido():
    pedido = Pedidos(criar_carrinho())
    frete = criar_pedido_com_frete().frete

    pedido.RestaurarEstado("ENVIADO", "PED12345678", "05/10/2026", "06/10/2026", None, None, "AB123456789BR", 0.0, None, frete)
    pedido.MarcarComoEntregue("12/10/2026")

    assert pedido.status == "ENTREGUE"
    assert pedido.numeroProtocolo == "PED12345678"
    assert pedido.codigoRastreio == "AB123456789BR"
    assert pedido.dataPagamento == "06/10/2026"
    assert pedido.dataEntrega == "12/10/2026"
