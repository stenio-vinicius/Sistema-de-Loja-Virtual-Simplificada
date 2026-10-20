import json

import pytest

from Classes.armazenamento import Armazenamento
from Classes.carrinho import Carrinho
from Classes.cliente import Cliente
from Classes.pedidos import Pedidos
from Classes.produto import Produto


def criar_produto(nome="Camisa", tamanho="M"):
    produto = Produto()
    produto.CadastrarProduto(nome, "Roupas", 49.90, "Azul", tamanho, 10)
    return produto


def test_listar_sem_arquivo_retorna_lista_vazia(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.ListarProdutos() == []


def test_salvar_e_listar_produto(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.SalvarProduto(criar_produto()) is True

    produtos = armazenamento.ListarProdutos()
    assert len(produtos) == 1
    assert produtos[0].nome == "Camisa"
    assert produtos[0].preco == 49.90
    assert produtos[0].estoque == 10


def test_tamanho_vazio_continua_vazio_ao_carregar(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    armazenamento.SalvarProduto(criar_produto(tamanho=None))

    assert armazenamento.ListarProdutos()[0].tamanho is None


def test_nome_duplicado_e_recusado(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.SalvarProduto(criar_produto("Camisa")) is True
    assert armazenamento.SalvarProduto(criar_produto("camisa")) is False   # mesmo nome, só muda a caixa

    assert len(armazenamento.ListarProdutos()) == 1


def test_dados_persistem_entre_instancias(tmp_path):
    caminho = str(tmp_path / "dados.json")
    Armazenamento(caminho).SalvarProduto(criar_produto())

    outra = Armazenamento(caminho)   # simula rodar o programa de novo

    assert len(outra.ListarProdutos()) == 1


def test_arquivo_json_tem_a_estrutura_esperada(tmp_path):
    caminho = tmp_path / "dados.json"
    Armazenamento(str(caminho)).SalvarProduto(criar_produto())

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    assert dados["produtos"][0]["nome"] == "Camisa"
    assert dados["produtos"][0]["preco"] == 49.90


# ---------- Clientes ----------

def criar_cliente(email="stenio@email.com"):
    cliente = Cliente()
    cliente.CadastrarCliente("Stênio", email, "123456", 20, "Juazeiro do Norte")
    return cliente


def test_salvar_e_buscar_cliente(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.SalvarCliente(criar_cliente()) is True

    cliente = armazenamento.BuscarCliente("STENIO@email.com")   # a busca ignora maiúsculas e minúsculas
    assert cliente.nome == "Stênio"
    assert cliente.email == "stenio@email.com"
    assert cliente.idade == 20


def test_buscar_cliente_inexistente_retorna_none(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.BuscarCliente("ninguem@email.com") is None


def test_email_duplicado_e_recusado(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.SalvarCliente(criar_cliente("stenio@email.com")) is True
    assert armazenamento.SalvarCliente(criar_cliente("STENIO@email.com")) is False

    assert len(armazenamento.ListarClientes()) == 1


def test_cliente_carregado_ainda_confere_a_senha(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    armazenamento.SalvarCliente(criar_cliente())

    cliente = armazenamento.BuscarCliente("stenio@email.com")

    assert cliente.VerificarSenha("123456") is True
    assert cliente.VerificarSenha("errada") is False


def test_listar_clientes(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    armazenamento.SalvarCliente(criar_cliente("a@email.com"))
    armazenamento.SalvarCliente(criar_cliente("b@email.com"))

    emails = []
    for cliente in armazenamento.ListarClientes():
        emails.append(cliente.email)

    assert emails == ["a@email.com", "b@email.com"]


# ---------- Cupons ----------

def test_salvar_e_listar_cupons(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.SalvarCupom("promo10", 10, 150.00) is True   # o código é guardado em maiúsculas

    assert armazenamento.ListarCupons() == {"PROMO10": {"percentual": 10, "valorMinimo": 150.00}}


def test_cupom_duplicado_e_recusado(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.SalvarCupom("PROMO10", 10, 150.00) is True
    assert armazenamento.SalvarCupom("promo10", 20, 300.00) is False

    assert armazenamento.ListarCupons()["PROMO10"]["percentual"] == 10


def test_listar_cupons_sem_arquivo_retorna_vazio(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.ListarCupons() == {}


# ---------- Carrinho ----------

def criar_produtos_salvos(armazenamento):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 100.00, "Azul", "M", 10)
    armazenamento.SalvarProduto(produto)
    return armazenamento.ListarProdutos()


def test_salvar_e_carregar_carrinho(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    produtos = criar_produtos_salvos(armazenamento)
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 3)

    armazenamento.SalvarCarrinho("stenio@email.com", carrinho)
    carregado = armazenamento.CarregarCarrinho("STENIO@email.com", produtos)   # a busca ignora maiúsculas e minúsculas

    assert len(carregado.itens) == 1
    assert carregado.itens[0]["produto"] is produtos[0]
    assert carregado.itens[0]["quantidade"] == 3


def test_carregar_carrinho_inexistente_retorna_carrinho_vazio(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.CarregarCarrinho("ninguem@email.com", []).itens == []


def test_carregar_carrinho_respeita_o_estoque_atual(tmp_path, capsys):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    produtos = criar_produtos_salvos(armazenamento)
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 8)
    armazenamento.SalvarCarrinho("stenio@email.com", carrinho)

    produtos[0].ModificarProduto(estoque=3)   # o estoque diminuiu depois de o carrinho ser salvo
    carregado = armazenamento.CarregarCarrinho("stenio@email.com", produtos)
    capturado = capsys.readouterr()

    assert carregado.itens[0]["quantidade"] == 3
    assert "Foram adicionadas apenas 3" in capturado.out


# ---------- Pedidos e vendas ----------

def criar_pedido_confirmado(armazenamento, forma="PIX", parcelas=1):
    produtos = criar_produtos_salvos(armazenamento)
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 2)

    pedido = Pedidos(carrinho)
    pedido.DefinirFrete(200)
    pedido.DefinirPagamento(forma, parcelas)
    pedido.ConfirmarPedido()
    return pedido


def test_salvar_pedido_confirmado_grava_pedido_estoque_venda_e_limpa_o_carrinho(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    pedido = criar_pedido_confirmado(armazenamento)

    armazenamento.SalvarPedidoConfirmado(pedido, "stenio@email.com", "05/10/2026")

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)
    assert registro["cliente"] == "stenio@email.com"
    assert registro["data"] == "05/10/2026"
    assert registro["status"] == "ENVIADO"
    assert registro["subtotal"] == 200.00
    assert registro["frete"] == {"distancia": 200, "valor": 20.0, "prazo": 5}
    assert registro["pagamento"]["forma"] == "PIX"
    assert registro["pagamento"]["valorTotal"] == pytest.approx(209.00)

    produtos = armazenamento.ListarProdutos()
    assert produtos[0].estoque == 8   # o estoque baixado foi gravado
    assert armazenamento.CarregarRelatorio().FaturamentoTotal() == 200.00
    assert armazenamento.CarregarCarrinho("stenio@email.com", produtos).itens == []


def test_pedido_no_credito_guarda_as_parcelas(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    pedido = criar_pedido_confirmado(armazenamento, "CARTAO_CREDITO", 4)

    armazenamento.SalvarPedidoConfirmado(pedido, "stenio@email.com", "05/10/2026")

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)
    assert registro["pagamento"]["parcelas"] == 4


def test_pedido_no_pix_nao_tem_parcelas(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    pedido = criar_pedido_confirmado(armazenamento, "PIX")

    armazenamento.SalvarPedidoConfirmado(pedido, "stenio@email.com", "05/10/2026")

    assert armazenamento.BuscarPedido(pedido.numeroProtocolo)["pagamento"]["parcelas"] is None


def test_buscar_pedido_ignora_maiusculas_e_minusculas(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    pedido = criar_pedido_confirmado(armazenamento)
    armazenamento.SalvarPedidoConfirmado(pedido, "stenio@email.com", "05/10/2026")

    assert armazenamento.BuscarPedido(pedido.numeroProtocolo.lower()) is not None


def test_buscar_pedido_inexistente_retorna_none(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.BuscarPedido("XX000000000BR") is None


def test_listar_pedidos_filtra_pelo_cliente(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    pedido = criar_pedido_confirmado(armazenamento)
    armazenamento.SalvarPedidoConfirmado(pedido, "stenio@email.com", "05/10/2026")

    assert len(armazenamento.ListarPedidos("STENIO@email.com")) == 1
    assert armazenamento.ListarPedidos("outro@email.com") == []


def test_atualizar_pedido(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))
    pedido = criar_pedido_confirmado(armazenamento)
    armazenamento.SalvarPedidoConfirmado(pedido, "stenio@email.com", "05/10/2026")

    assert armazenamento.AtualizarPedido(pedido.numeroProtocolo, "ENTREGUE", "10/10/2026") is True

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)
    assert registro["status"] == "ENTREGUE"
    assert registro["dataEntrega"] == "10/10/2026"


def test_atualizar_pedido_inexistente_retorna_falso(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.AtualizarPedido("XX000000000BR", "ENTREGUE", "10/10/2026") is False


def test_carregar_relatorio_sem_vendas_esta_vazio(tmp_path):
    armazenamento = Armazenamento(str(tmp_path / "dados.json"))

    assert armazenamento.CarregarRelatorio().FaturamentoTotal() == 0