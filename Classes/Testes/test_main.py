import re
from datetime import datetime

import pytest

from Classes.pagamento import Pagamento
from main import main

EMAIL = "stenio@email.com"
SENHA = "123456"
LOGIN = ["--email", EMAIL, "--senha", SENHA]


@pytest.fixture(autouse=True)
def limpar_cupons():
    Pagamento.CUPONS_VALIDOS.clear()
    yield
    Pagamento.CUPONS_VALIDOS.clear()


def executar(capsys, caminho, *argumentos):
    """Roda um comando da CLI e devolve só o que ele imprimiu."""
    capsys.readouterr()
    main(list(argumentos), caminho)
    return capsys.readouterr().out


def preparar_loja(capsys, caminho, estoque=10):
    executar(capsys, caminho, "cadastrar-cliente", "--nome", "Stênio", "--email", EMAIL, "--senha", SENHA,
             "--idade", "20", "--endereco", "Juazeiro do Norte")
    executar(capsys, caminho, "cadastrar-produto", "--nome", "Camisa", "--categoria", "Roupas", "--preco", "100",
             "--cor", "Azul", "--tamanho", "M", "--estoque", str(estoque))


def adicionar(capsys, caminho, quantidade, produto="Camisa"):
    return executar(capsys, caminho, "adicionar-carrinho", *LOGIN, "--produto", produto, "--quantidade", str(quantidade))


def confirmar(capsys, caminho, *extras, forma="PIX", distancia="200", data="05/10/2026"):
    return executar(capsys, caminho, "confirmar-pedido", *LOGIN, "--distancia", distancia, "--forma", forma,
                    "--data", data, *extras)


def protocolo_de(saida):
    return re.search(r"[A-Z]{2}\d{9}BR", saida).group(0)


# =========================================================
# Produtos
# =========================================================

def test_cadastrar_e_listar_produto(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")

    saida = executar(capsys, caminho, "cadastrar-produto", "--nome", "Camisa", "--categoria", "Roupas",
                     "--preco", "49.90", "--cor", "Azul", "--tamanho", "M", "--estoque", "10")
    listagem = executar(capsys, caminho, "listar-produtos")

    assert "cadastrado com sucesso" in saida
    assert "Camisa" in listagem
    assert "R$ 49,90" in listagem


def test_cadastrar_produto_duplicado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = executar(capsys, caminho, "cadastrar-produto", "--nome", "camisa", "--categoria", "Roupas",
                     "--preco", "10", "--cor", "Azul", "--estoque", "1")

    assert "Já existe um produto chamado 'camisa'" in saida


def test_listar_produtos_sem_nenhum_cadastrado(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "listar-produtos")

    assert "Nenhum produto cadastrado." in saida


# =========================================================
# Clientes
# =========================================================

def test_cadastrar_cliente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")

    saida = executar(capsys, caminho, "cadastrar-cliente", "--nome", "Stênio", "--email", EMAIL, "--senha", SENHA,
                     "--idade", "20", "--endereco", "Juazeiro do Norte")

    assert "Cliente 'Stênio' cadastrado com sucesso!" in saida


def test_cadastrar_cliente_com_email_repetido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = executar(capsys, caminho, "cadastrar-cliente", "--nome", "Outro", "--email", "STENIO@email.com",
                     "--senha", "abc", "--idade", "30", "--endereco", "X")

    assert "Já existe um cliente com o e-mail" in saida


# =========================================================
# Cupons
# =========================================================

def test_cadastrar_e_listar_cupom(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")

    cadastro = executar(capsys, caminho, "cadastrar-cupom", "--codigo", "promo10", "--percentual", "10",
                        "--valor-minimo", "150")
    listagem = executar(capsys, caminho, "listar-cupons")

    assert "Cupom 'PROMO10' cadastrado: 10% de desconto" in cadastro
    assert "PROMO10: 10% (válido para compras acima de R$ 150,00)" in listagem


def test_listar_cupons_filtra_pelo_valor_da_compra(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    executar(capsys, caminho, "cadastrar-cupom", "--codigo", "promo10", "--percentual", "10", "--valor-minimo", "150")

    abaixo = executar(capsys, caminho, "listar-cupons", "--valor", "100")
    acima = executar(capsys, caminho, "listar-cupons", "--valor", "200")

    assert "Nenhum cupom disponível" in abaixo
    assert "PROMO10" in acima


def test_cadastrar_cupom_repetido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    argumentos = ["cadastrar-cupom", "--codigo", "promo10", "--percentual", "10", "--valor-minimo", "150"]
    executar(capsys, caminho, *argumentos)

    saida = executar(capsys, caminho, *argumentos)

    assert "Já existe um cupom com o código 'PROMO10'" in saida


def test_listar_cupons_sem_nenhum_cadastrado(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "listar-cupons")

    assert "Nenhum cupom cadastrado." in saida


# =========================================================
# Carrinho
# =========================================================

def test_carrinho_persiste_entre_execucoes_e_soma_o_mesmo_produto(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    adicionar(capsys, caminho, 2)
    adicionar(capsys, caminho, 1)
    saida = executar(capsys, caminho, "ver-carrinho", *LOGIN)

    assert "3x R$ 100,00 = R$ 300,00" in saida
    assert "Total: R$ 300,00" in saida


def test_adicionar_acima_do_estoque_adiciona_so_o_que_cabe(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, estoque=3)

    saida = adicionar(capsys, caminho, 5)

    assert "Foram adicionadas apenas 3" in saida
    assert "3x R$ 100,00" in saida


def test_remover_do_carrinho_aos_poucos(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 5)

    parcial = executar(capsys, caminho, "remover-carrinho", *LOGIN, "--produto", "Camisa", "--quantidade", "2")
    total = executar(capsys, caminho, "remover-carrinho", *LOGIN, "--produto", "Camisa", "--quantidade", "10")

    assert "3x R$ 100,00" in parcial
    assert "Seu carrinho está vazio." in total


def test_remover_produto_que_nao_esta_no_carrinho(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = executar(capsys, caminho, "remover-carrinho", *LOGIN, "--produto", "Camisa")

    assert "não está no seu carrinho" in saida


def test_senha_incorreta_nao_acessa_o_carrinho(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = executar(capsys, caminho, "ver-carrinho", "--email", EMAIL, "--senha", "errada")

    assert "E-mail ou senha incorretos." in saida


def test_email_inexistente_nao_acessa_o_carrinho(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "ver-carrinho", "--email", "x@x.com", "--senha", "1")

    assert "E-mail ou senha incorretos." in saida


def test_adicionar_produto_inexistente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = adicionar(capsys, caminho, 1, produto="Calça")

    assert "Produto 'Calça' não encontrado." in saida


def test_adicionar_quantidade_invalida(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = adicionar(capsys, caminho, 0)

    assert "A quantidade deve ser pelo menos 1." in saida


# =========================================================
# Pedido
# =========================================================

def test_fluxo_completo_da_compra_a_entrega(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)
    executar(capsys, caminho, "cadastrar-cupom", "--codigo", "promo10", "--percentual", "10", "--valor-minimo", "150")

    saida = confirmar(capsys, caminho, "--cupom", "promo10")

    # 200 - 10% = 180, + 20 de frete = 200, com 5% de desconto do Pix = 190
    assert "Cupom aplicado! 10% de desconto." in saida
    assert "Valor total a pagar: R$ 190,00" in saida
    assert "Pedido confirmado!" in saida
    assert "Prazo estimado de entrega: 5 dias." in saida
    protocolo = protocolo_de(saida)

    assert "Estoque: 8" in executar(capsys, caminho, "listar-produtos")
    assert "Seu carrinho está vazio." in executar(capsys, caminho, "ver-carrinho", *LOGIN)

    pedidos = executar(capsys, caminho, "listar-pedidos", *LOGIN)
    assert protocolo in pedidos
    assert "ENVIADO" in pedidos
    assert "R$ 190,00" in pedidos
    assert "2 item(ns)" in pedidos

    relatorio = executar(capsys, caminho, "relatorio")
    assert "Faturamento total: R$ 200,00" in relatorio
    assert "Roupas: R$ 200,00" in relatorio
    assert "Produto mais vendido: Camisa" in relatorio

    entrega = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "10/10/2026")
    assert "marcado como entregue em 10/10/2026" in entrega

    pedidos = executar(capsys, caminho, "listar-pedidos", *LOGIN)
    assert "ENTREGUE" in pedidos
    assert "Entrega: 10/10/2026" in pedidos


def test_confirmar_no_credito_parcelado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = executar(capsys, caminho, "confirmar-pedido", *LOGIN, "--distancia", "200", "--forma", "cartao_credito",
                     "--parcelas", "4", "--data", "05/10/2026")

    assert "Valor total a pagar: R$ 226,60" in saida
    assert "Parcelamento: 4x de R$ 56,65" in saida


def test_confirmar_com_carrinho_vazio(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = confirmar(capsys, caminho)

    assert "Seu carrinho está vazio." in saida


def test_forma_invalida_nao_confirma_nem_baixa_o_estoque(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = confirmar(capsys, caminho, forma="DINHEIRO")

    assert "Forma de pagamento inválida: DINHEIRO" in saida
    assert "Pedido não confirmado." in saida
    assert "Estoque: 10" in executar(capsys, caminho, "listar-produtos")
    assert "2x R$ 100,00" in executar(capsys, caminho, "ver-carrinho", *LOGIN)


def test_distancia_acima_do_limite_nao_confirma(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = confirmar(capsys, caminho, distancia="5000")

    assert "Não foi possível calcular o frete" in saida
    assert "Pedido não confirmado." in saida


def test_distancia_negativa_nao_confirma(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = confirmar(capsys, caminho, distancia="-5")

    assert "A distância não pode ser negativa." in saida


def test_cupom_inexistente_nao_confirma(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = confirmar(capsys, caminho, "--cupom", "NAOEXISTE")

    assert "Cupom de desconto indisponível!" in saida
    assert "Pedido não confirmado: cupom indisponível." in saida
    assert "Estoque: 10" in executar(capsys, caminho, "listar-produtos")


def test_cupom_abaixo_do_valor_minimo_nao_confirma(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 1)   # compra de R$ 100,00
    executar(capsys, caminho, "cadastrar-cupom", "--codigo", "promo10", "--percentual", "10", "--valor-minimo", "150")

    saida = confirmar(capsys, caminho, "--cupom", "promo10")

    assert "só é válido para compras acima de R$ 150,00" in saida
    assert "Pedido não confirmado: cupom indisponível." in saida


def test_data_invalida_no_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = confirmar(capsys, caminho, data="32/13/2026")

    assert "Data inválida" in saida


def test_pedido_usa_a_data_de_hoje_por_padrao(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)
    antes = datetime.now().strftime("%d/%m/%Y")

    executar(capsys, caminho, "confirmar-pedido", *LOGIN, "--distancia", "200", "--forma", "PIX")
    depois = datetime.now().strftime("%d/%m/%Y")
    pedidos = executar(capsys, caminho, "listar-pedidos", *LOGIN)

    assert antes in pedidos or depois in pedidos


def test_listar_pedidos_sem_nenhum_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    saida = executar(capsys, caminho, "listar-pedidos", *LOGIN)

    assert "Você ainda não fez nenhum pedido." in saida


def test_estoque_nao_permite_vender_mais_do_que_existe(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, estoque=2)
    adicionar(capsys, caminho, 2)
    confirmar(capsys, caminho)   # vende as 2 unidades

    saida = adicionar(capsys, caminho, 1)

    assert "Não há mais unidades" in saida


# =========================================================
# Entrega
# =========================================================

def criar_pedido_enviado(tmp_path, capsys, data="05/10/2026"):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)
    saida = confirmar(capsys, caminho, data=data)
    return caminho, protocolo_de(saida)


def test_entregar_pedido_inexistente(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "entregar-pedido", "--protocolo", "XX000000000BR",
                     "--data", "10/10/2026")

    assert "não encontrado" in saida


def test_entregar_pedido_com_data_invalida(tmp_path, capsys):
    caminho, protocolo = criar_pedido_enviado(tmp_path, capsys)

    saida = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "ontem")

    assert "Data inválida" in saida


def test_entregar_pedido_com_data_anterior_ao_pedido(tmp_path, capsys):
    caminho, protocolo = criar_pedido_enviado(tmp_path, capsys, data="05/10/2026")

    saida = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "01/10/2026")

    assert "não pode ser anterior à data do pedido (05/10/2026)" in saida


def test_entregar_o_mesmo_pedido_duas_vezes(tmp_path, capsys):
    caminho, protocolo = criar_pedido_enviado(tmp_path, capsys)
    executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "10/10/2026")

    saida = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "11/10/2026")

    assert "Não é possível marcar como entregue um pedido com status 'ENTREGUE'" in saida
    assert "Entrega: 10/10/2026" in executar(capsys, caminho, "listar-pedidos", *LOGIN)   # a data original foi mantida


# =========================================================
# Relatório
# =========================================================

def test_relatorio_por_periodo(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)
    confirmar(capsys, caminho, data="05/10/2026")   # R$ 200,00
    adicionar(capsys, caminho, 1)
    confirmar(capsys, caminho, data="20/10/2026")   # R$ 100,00

    saida = executar(capsys, caminho, "relatorio", "--inicio", "01/10/2026", "--fim", "15/10/2026")

    assert "Vendas registradas: 2" in saida
    assert "Faturamento total: R$ 300,00" in saida
    assert "Faturamento de 01/10/2026 a 15/10/2026: R$ 200,00" in saida


def test_relatorio_sem_vendas(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio")

    assert "Nenhuma venda registrada." in saida


def test_relatorio_com_periodo_incompleto(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio", "--inicio", "01/10/2026")

    assert "Informe --inicio e --fim juntos." in saida


def test_relatorio_com_data_invalida(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio", "--inicio", "32/13/2026", "--fim", "01/10/2026")

    assert "Data inválida" in saida


def test_relatorio_com_periodo_invertido(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio", "--inicio", "15/10/2026", "--fim", "01/10/2026")

    assert "A data inicial não pode ser depois da data final." in saida