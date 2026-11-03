import json

import pytest

from Classes.armazenamento import Armazenamento
from Classes.carrinho import Carrinho
from Classes.cliente import Cliente
from Classes.cupom import Cupom
from Classes.produto import Produto, ProdutoDigital


def novo_armazenamento(tmp_path):
    return Armazenamento(str(tmp_path / "dados.json"))


def criar_produto(sku="CAM-001", nome="Camisa", categoria="Roupas", preco=100.00, estoque=10, tamanho="M", digital=False):
    produto = ProdutoDigital() if digital else Produto()
    produto.CadastrarProduto(nome, categoria, preco, "Azul", tamanho, estoque, sku)
    return produto


def criar_cliente(email="stenio@email.com", cpf="529.982.247-25"):
    cliente = Cliente()
    cliente.CadastrarCliente("Stênio", email, "123456", 20, "Rua das Flores, 10", cpf)
    return cliente


def criar_cupom(codigo="promo10", **opcoes):
    dados = {"codigo": codigo, "percentual": 10, "valorMinimo": 150.00}
    dados.update(opcoes)

    cupom = Cupom()
    cupom.CadastrarCupom(**dados)
    return cupom


# =========================================================
# Produtos
# =========================================================

def test_listar_produtos_sem_arquivo_retorna_lista_vazia(tmp_path):
    assert novo_armazenamento(tmp_path).ListarProdutos() == []


def test_salvar_e_listar_produto(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarProduto(criar_produto()) is True

    produtos = armazenamento.ListarProdutos()
    assert len(produtos) == 1
    assert produtos[0].sku == "CAM-001"
    assert produtos[0].nome == "Camisa"
    assert produtos[0].preco == 100.00
    assert produtos[0].estoque == 10
    assert produtos[0].digital is False


def test_tamanho_vazio_continua_vazio_ao_carregar(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarProduto(criar_produto(tamanho=None))

    assert armazenamento.ListarProdutos()[0].tamanho is None


def test_sku_duplicado_e_recusado_ignorando_a_caixa(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarProduto(criar_produto("CAM-001")) is True
    assert armazenamento.SalvarProduto(criar_produto("cam-001", nome="Outro nome")) is False

    assert len(armazenamento.ListarProdutos()) == 1


def test_mesmo_nome_com_sku_diferente_e_permitido(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarProduto(criar_produto("CAM-M", tamanho="M")) is True
    assert armazenamento.SalvarProduto(criar_produto("CAM-G", tamanho="G")) is True

    assert len(armazenamento.ListarProdutos()) == 2


def test_produto_sem_sku_e_recusado(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarProduto(criar_produto(sku=None)) is False
    assert armazenamento.SalvarProduto(criar_produto(sku="  ")) is False
    assert armazenamento.ListarProdutos() == []


def test_produto_digital_continua_digital_ao_carregar(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarProduto(criar_produto("EBK-001", "E-book", "Livros", 50.00, 100, digital=True))

    produto = armazenamento.ListarProdutos()[0]

    assert isinstance(produto, ProdutoDigital)
    assert produto.digital is True
    assert produto.cor is None
    assert produto.tamanho is None


def test_dados_persistem_entre_instancias(tmp_path):
    caminho = str(tmp_path / "dados.json")
    Armazenamento(caminho).SalvarProduto(criar_produto())

    assert len(Armazenamento(caminho).ListarProdutos()) == 1


def test_arquivo_json_tem_a_estrutura_esperada(tmp_path):
    caminho = tmp_path / "dados.json"
    Armazenamento(str(caminho)).SalvarProduto(criar_produto())

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    assert dados["produtos"][0]["sku"] == "CAM-001"
    assert dados["produtos"][0]["preco"] == 100.00
    for chave in ("clientes", "cupons", "carrinhos", "pedidos", "vendas"):
        assert chave in dados


# =========================================================
# Clientes
# =========================================================

def test_salvar_e_buscar_cliente(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarCliente(criar_cliente()) is True

    cliente = armazenamento.BuscarCliente("STENIO@email.com")   # a busca ignora maiúsculas e minúsculas
    assert cliente.nome == "Stênio"
    assert cliente.email == "stenio@email.com"
    assert cliente.cpf == "52998224725"


def test_buscar_cliente_inexistente_retorna_none(tmp_path):
    assert novo_armazenamento(tmp_path).BuscarCliente("ninguem@email.com") is None


def test_email_duplicado_e_recusado(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarCliente(criar_cliente("stenio@email.com", "529.982.247-25")) is True
    assert armazenamento.SalvarCliente(criar_cliente("STENIO@email.com", "111.444.777-35")) is False

    assert armazenamento.ExisteClienteComEmail("Stenio@Email.com") is True
    assert len(armazenamento.ListarClientes()) == 1


def test_cpf_duplicado_e_recusado_mesmo_com_pontuacao_diferente(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarCliente(criar_cliente("a@email.com", "529.982.247-25")) is True
    assert armazenamento.SalvarCliente(criar_cliente("b@email.com", "52998224725")) is False

    assert armazenamento.ExisteClienteComCpf("529.982.247-25") is True
    assert armazenamento.ExisteClienteComCpf("111.444.777-35") is False


def test_cliente_carregado_ainda_confere_a_senha(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarCliente(criar_cliente())

    cliente = armazenamento.BuscarCliente("stenio@email.com")

    assert cliente.VerificarSenha("123456") is True
    assert cliente.VerificarSenha("errada") is False


def test_listar_clientes(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarCliente(criar_cliente("a@email.com", "529.982.247-25"))
    armazenamento.SalvarCliente(criar_cliente("b@email.com", "111.444.777-35"))

    emails = []
    for cliente in armazenamento.ListarClientes():
        emails.append(cliente.email)

    assert emails == ["a@email.com", "b@email.com"]


def test_atualizar_cliente(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarCliente(criar_cliente())
    cliente = armazenamento.BuscarCliente("stenio@email.com")
    cliente.AtualizarPerfil(nome="Stênio Silva", endereco="Avenida Central, 500")

    assert armazenamento.AtualizarCliente(cliente) is True

    atualizado = armazenamento.BuscarCliente("stenio@email.com")
    assert atualizado.nome == "Stênio Silva"
    assert atualizado.endereco == "Avenida Central, 500"


def test_atualizar_cliente_nao_aceita_cpf_de_outro(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarCliente(criar_cliente("a@email.com", "529.982.247-25"))
    armazenamento.SalvarCliente(criar_cliente("b@email.com", "111.444.777-35"))
    cliente = armazenamento.BuscarCliente("b@email.com")
    cliente.AtualizarPerfil(cpf="529.982.247-25")

    assert armazenamento.AtualizarCliente(cliente) is False


def test_atualizar_cliente_inexistente(tmp_path):
    assert novo_armazenamento(tmp_path).AtualizarCliente(criar_cliente()) is False


def test_cliente_antigo_sem_cpf_no_arquivo_carrega_com_cpf_vazio(tmp_path):
    caminho = tmp_path / "dados.json"
    caminho.write_text(json.dumps({"clientes": [
        {"nome": "Antigo", "email": "antigo@email.com", "senha": "1", "idade": 30, "endereco": "Rua A, 1"}
    ]}), encoding="utf-8")

    cliente = Armazenamento(str(caminho)).BuscarCliente("antigo@email.com")

    assert cliente.cpf is None
    assert "CPF inválido." in cliente.Problemas()


# =========================================================
# Cupons
# =========================================================

def test_salvar_buscar_e_listar_cupons(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    cupom = criar_cupom(validade="31/12/2026", usoMaximo=5, categorias=["Roupas"])

    assert armazenamento.SalvarCupom(cupom) is True

    buscado = armazenamento.BuscarCupom("promo10")   # a busca ignora maiúsculas e minúsculas
    assert buscado.codigo == "PROMO10"
    assert buscado.percentual == 10
    assert buscado.valorMinimo == 150.00
    assert buscado.validade == "31/12/2026"
    assert buscado.usoMaximo == 5
    assert buscado.categorias == ["Roupas"]
    assert buscado.usos == 0
    assert len(armazenamento.ListarCupons()) == 1


def test_cupom_duplicado_e_recusado(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)

    assert armazenamento.SalvarCupom(criar_cupom("promo10")) is True
    assert armazenamento.SalvarCupom(criar_cupom("PROMO10", percentual=50)) is False

    assert armazenamento.BuscarCupom("PROMO10").percentual == 10


def test_buscar_cupom_inexistente_retorna_none(tmp_path):
    assert novo_armazenamento(tmp_path).BuscarCupom("NAOEXISTE") is None


def test_listar_cupons_sem_arquivo_retorna_lista_vazia(tmp_path):
    assert novo_armazenamento(tmp_path).ListarCupons() == []


# =========================================================
# Carrinho
# =========================================================

def test_salvar_e_carregar_carrinho(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarProduto(criar_produto())
    produtos = armazenamento.ListarProdutos()
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 3)

    armazenamento.SalvarCarrinho("stenio@email.com", carrinho)
    carregado = armazenamento.CarregarCarrinho("STENIO@email.com", produtos)   # ignora maiúsculas e minúsculas

    assert len(carregado.itens) == 1
    assert carregado.itens[0]["produto"] is produtos[0]
    assert carregado.itens[0]["quantidade"] == 3


def test_carregar_carrinho_inexistente_retorna_carrinho_vazio(tmp_path):
    assert novo_armazenamento(tmp_path).CarregarCarrinho("ninguem@email.com", []).itens == []


def test_carregar_carrinho_mantem_a_quantidade_mesmo_acima_do_estoque_atual(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarProduto(criar_produto())
    produtos = armazenamento.ListarProdutos()
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 8)
    armazenamento.SalvarCarrinho("stenio@email.com", carrinho)

    produtos[0].ModificarProduto(estoque=3)   # o estoque diminuiu depois
    carregado = armazenamento.CarregarCarrinho("stenio@email.com", produtos)

    assert carregado.itens[0]["quantidade"] == 8   # quem barra é a criação do pedido


def test_carregar_carrinho_ignora_produto_que_nao_existe_mais(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    armazenamento.SalvarProduto(criar_produto())
    produtos = armazenamento.ListarProdutos()
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 1)
    armazenamento.SalvarCarrinho("stenio@email.com", carrinho)

    assert armazenamento.CarregarCarrinho("stenio@email.com", []).itens == []


# =========================================================
# Pedidos, pagamento, envio, cancelamento e vendas
# =========================================================

EMAIL = "stenio@email.com"


def criar_pedido_criado(armazenamento, cupom=None):
    """Salva o produto, monta o pedido (carrinho de R$ 200,00, frete de R$ 20,00) e o registra como CRIADO."""
    from Classes.pedidos import Pedidos

    armazenamento.SalvarProduto(criar_produto())
    if cupom is not None:
        armazenamento.SalvarCupom(cupom)

    produtos = armazenamento.ListarProdutos()
    carrinho = Carrinho()
    carrinho.AdicionarItem(produtos[0], 2)

    pedido = Pedidos(carrinho, "05/10/2026")
    pedido.DefinirFrete(200)
    if cupom is not None:
        pedido.AplicarCupom(armazenamento.BuscarCupom(cupom.codigo), "05/10/2026")

    armazenamento.RegistrarPedidoCriado(pedido, EMAIL)
    return pedido


def pagar(armazenamento, protocolo, forma="PIX", parcelas=1, data="06/10/2026"):
    pedido = armazenamento.CarregarPedido(protocolo, armazenamento.ListarProdutos())
    assert pedido.PagarPedido(forma, parcelas, data) is True
    armazenamento.RegistrarPagamento(pedido)
    return pedido


def test_registrar_pedido_criado_grava_o_pedido_e_esvazia_o_carrinho(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)

    assert registro["cliente"] == EMAIL
    assert registro["data"] == "05/10/2026"
    assert registro["status"] == "CRIADO"
    assert registro["itens"][0]["sku"] == "CAM-001"
    assert registro["itens"][0]["quantidade"] == 2
    assert registro["subtotal"] == 200.00
    assert registro["frete"] == {"distancia": 200, "valor": 20.0, "prazo": 5}
    assert registro["cupom"] is None
    assert registro["valorPrevisto"] == 220.00
    assert registro["pagamento"] is None
    assert registro["codigoRastreio"] is None
    assert armazenamento.CarregarCarrinho(EMAIL, armazenamento.ListarProdutos()).itens == []
    assert armazenamento.ListarProdutos()[0].estoque == 10   # criar o pedido não baixa o estoque


def test_registrar_pedido_criado_com_cupom_guarda_o_desconto(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento, criar_cupom())

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)

    assert registro["cupom"] == {"codigo": "PROMO10", "valorDesconto": 20.00}
    assert registro["valorPrevisto"] == 200.00


def test_carregar_pedido_restaura_o_pedido_completo(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    original = criar_pedido_criado(armazenamento, criar_cupom())

    restaurado = armazenamento.CarregarPedido(original.numeroProtocolo.lower(), armazenamento.ListarProdutos())

    assert restaurado.numeroProtocolo == original.numeroProtocolo
    assert restaurado.status == "CRIADO"
    assert restaurado.data == "05/10/2026"
    assert restaurado.carrinho.CalcularTotal() == 200.00
    assert restaurado.frete.valor == 20.0
    assert restaurado.frete.prazo == 5
    assert restaurado.cupom.codigo == "PROMO10"
    assert restaurado.valorDesconto == 20.00


def test_carregar_pedido_inexistente_retorna_none(tmp_path):
    assert novo_armazenamento(tmp_path).CarregarPedido("PED00000000", []) is None


def test_registrar_pagamento_baixa_o_estoque_e_registra_a_venda(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)

    pagar(armazenamento, pedido.numeroProtocolo)

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)
    assert registro["status"] == "PAGO"
    assert registro["dataPagamento"] == "06/10/2026"
    assert registro["pagamento"]["forma"] == "PIX"
    assert registro["pagamento"]["parcelas"] is None
    assert registro["pagamento"]["valorTotal"] == pytest.approx(209.00)
    assert armazenamento.ListarProdutos()[0].estoque == 8
    assert armazenamento.CarregarRelatorio().FaturamentoTotal() == 200.00


def test_pedido_no_credito_guarda_as_parcelas(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)

    pagar(armazenamento, pedido.numeroProtocolo, "CARTAO_CREDITO", 4)

    assert armazenamento.BuscarPedido(pedido.numeroProtocolo)["pagamento"]["parcelas"] == 4


def test_pagamento_com_cupom_incrementa_o_uso_gravado(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento, criar_cupom(usoMaximo=2))

    pagar(armazenamento, pedido.numeroProtocolo)

    assert armazenamento.BuscarCupom("PROMO10").usos == 1


def test_atualizar_pedido_grava_envio_e_entrega(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)
    pagar(armazenamento, pedido.numeroProtocolo)

    restaurado = armazenamento.CarregarPedido(pedido.numeroProtocolo, armazenamento.ListarProdutos())
    restaurado.EnviarPedido()
    assert armazenamento.AtualizarPedido(restaurado) is True

    restaurado = armazenamento.CarregarPedido(pedido.numeroProtocolo, armazenamento.ListarProdutos())
    restaurado.MarcarComoEntregue("12/10/2026")
    armazenamento.AtualizarPedido(restaurado)

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)
    assert registro["status"] == "ENTREGUE"
    assert registro["codigoRastreio"] is not None
    assert registro["dataEntrega"] == "12/10/2026"
    assert registro["pagamento"]["forma"] == "PIX"   # a atualização não apaga o pagamento


def test_atualizar_pedido_inexistente_retorna_falso(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)
    pedido._numeroProtocolo = "PED00000000"

    assert armazenamento.AtualizarPedido(pedido) is False


def test_cancelar_pedido_pago_estorna_o_estoque_e_remove_a_venda(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)
    pagar(armazenamento, pedido.numeroProtocolo)

    restaurado = armazenamento.CarregarPedido(pedido.numeroProtocolo, armazenamento.ListarProdutos())
    assert restaurado.CancelarPedido("08/10/2026") is True
    assert armazenamento.RegistrarCancelamento(restaurado, True) is True

    registro = armazenamento.BuscarPedido(pedido.numeroProtocolo)
    assert registro["status"] == "CANCELADO"
    assert registro["dataCancelamento"] == "08/10/2026"
    assert armazenamento.ListarProdutos()[0].estoque == 10
    assert armazenamento.CarregarRelatorio().FaturamentoTotal() == 0


def test_cancelar_pedido_criado_nao_mexe_no_estoque(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)

    restaurado = armazenamento.CarregarPedido(pedido.numeroProtocolo, armazenamento.ListarProdutos())
    restaurado.CancelarPedido("05/10/2026")
    armazenamento.RegistrarCancelamento(restaurado, False)

    assert armazenamento.BuscarPedido(pedido.numeroProtocolo)["status"] == "CANCELADO"
    assert armazenamento.ListarProdutos()[0].estoque == 10


def test_registrar_cancelamento_de_pedido_inexistente_retorna_falso(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    pedido = criar_pedido_criado(armazenamento)
    pedido._numeroProtocolo = "PED00000000"

    assert armazenamento.RegistrarCancelamento(pedido, False) is False


def test_buscar_pedido_inexistente_retorna_none(tmp_path):
    assert novo_armazenamento(tmp_path).BuscarPedido("PED00000000") is None


def test_listar_pedidos_filtra_pelo_cliente(tmp_path):
    armazenamento = novo_armazenamento(tmp_path)
    criar_pedido_criado(armazenamento)

    assert len(armazenamento.ListarPedidos("STENIO@email.com")) == 1
    assert armazenamento.ListarPedidos("outro@email.com") == []


def test_carregar_relatorio_sem_vendas_esta_vazio(tmp_path):
    assert novo_armazenamento(tmp_path).CarregarRelatorio().FaturamentoTotal() == 0
