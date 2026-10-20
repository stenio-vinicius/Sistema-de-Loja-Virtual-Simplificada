import argparse
from datetime import datetime

from Classes.armazenamento import Armazenamento
from Classes.carrinho import Carrinho
from Classes.cliente import Cliente
from Classes.pagamento import Pagamento
from Classes.pedidos import Pedidos
from Classes.produto import Produto
from Classes.relatorio import Relatorio

CAMINHO_DADOS = "dados.json"


# ---------- Funções auxiliares ----------

def carregar_cupons(armazenamento):
    Pagamento.CUPONS_VALIDOS.clear()

    for codigo, regras in armazenamento.ListarCupons().items():
        Pagamento().CadastrarCupom(codigo, regras["percentual"], regras["valorMinimo"])


def autenticar(armazenamento, email, senha):
    cliente = armazenamento.BuscarCliente(email)

    if cliente is None or not cliente.VerificarSenha(senha):
        print("E-mail ou senha incorretos.")
        return None

    return cliente


def converter_data(texto):
    return datetime.strptime(texto, Relatorio.FORMATO_DATA)


def data_valida(texto):
    try:
        converter_data(texto)
        return True
    except ValueError:
        print(f"Data inválida: '{texto}'. Use o formato DD/MM/AAAA.")
        return False


def hoje():
    return datetime.now().strftime(Relatorio.FORMATO_DATA)


def encontrar_produto(produtos, nome):
    for produto in produtos:
        if produto.nome.lower() == nome.lower():
            return produto

    return None


def exibir_carrinho(carrinho, formatador):
    if not carrinho.itens:
        print("Seu carrinho está vazio.")
        return

    print("Itens do carrinho:")
    for numero, item in enumerate(carrinho.itens, start = 1):
        produto = item["produto"]
        subtotal = produto.preco * item["quantidade"]
        print(f"{numero}. {produto.nome} | {item['quantidade']}x R$ {formatador.FormatarMoeda(produto.preco)} = R$ {formatador.FormatarMoeda(subtotal)}")

    print(f"Total: R$ {formatador.FormatarMoeda(carrinho.CalcularTotal())}")


# ---------- Comandos ----------

def cmd_cadastrar_cliente(args, armazenamento, formatador):
    cliente = Cliente()
    cliente.CadastrarCliente(args.nome, args.email, args.senha, args.idade, args.endereco)

    if armazenamento.SalvarCliente(cliente):
        print(f"Cliente '{cliente.nome}' cadastrado com sucesso!")
    else:
        print(f"Já existe um cliente com o e-mail '{cliente.email}'.")


def cmd_cadastrar_produto(args, armazenamento, formatador):
    produto = Produto()
    produto.CadastrarProduto(args.nome, args.categoria, args.preco, args.cor, args.tamanho, args.estoque)

    if armazenamento.SalvarProduto(produto):
        print(f"Produto '{produto.nome}' cadastrado com sucesso!")
    else:
        print(f"Já existe um produto chamado '{produto.nome}'.")


def cmd_listar_produtos(args, armazenamento, formatador):
    produtos = armazenamento.ListarProdutos()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print("Produtos cadastrados:")
    for numero, produto in enumerate(produtos, start = 1):
        tamanho = produto.tamanho if produto.tamanho is not None else "-"
        print(f"{numero}. {produto.nome} | {produto.categoria} | R$ {formatador.FormatarMoeda(produto.preco)} | Cor: {produto.cor} | Tamanho: {tamanho} | Estoque: {produto.estoque}")


def cmd_cadastrar_cupom(args, armazenamento, formatador):
    codigo = args.codigo.upper()

    if armazenamento.SalvarCupom(codigo, args.percentual, args.valor_minimo):
        print(f"Cupom '{codigo}' cadastrado: {args.percentual:g}% de desconto para compras acima de R$ {formatador.FormatarMoeda(args.valor_minimo)}.")
    else:
        print(f"Já existe um cupom com o código '{codigo}'.")


def cmd_listar_cupons(args, armazenamento, formatador):
    if not armazenamento.ListarCupons():
        print("Nenhum cupom cadastrado.")
        return

    carregar_cupons(armazenamento)

    valorCompra = float("inf")
    if args.valor is not None:
        valorCompra = args.valor

    formatador.ListarCupons(valorCompra)


def cmd_adicionar_carrinho(args, armazenamento, formatador):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    if args.quantidade < 1:
        print("A quantidade deve ser pelo menos 1.")
        return

    produtos = armazenamento.ListarProdutos()
    produto = encontrar_produto(produtos, args.produto)

    if produto is None:
        print(f"Produto '{args.produto}' não encontrado.")
        return

    carrinho = armazenamento.CarregarCarrinho(cliente.email, produtos)
    carrinho.AdicionarItem(produto, args.quantidade)
    armazenamento.SalvarCarrinho(cliente.email, carrinho)

    exibir_carrinho(carrinho, formatador)


def cmd_remover_carrinho(args, armazenamento, formatador):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    if args.quantidade < 1:
        print("A quantidade deve ser pelo menos 1.")
        return

    produtos = armazenamento.ListarProdutos()
    carrinho = armazenamento.CarregarCarrinho(cliente.email, produtos)

    produtoNoCarrinho = None
    for item in carrinho.itens:
        if item["produto"].nome.lower() == args.produto.lower():
            produtoNoCarrinho = item["produto"]

    if produtoNoCarrinho is None:
        print(f"'{args.produto}' não está no seu carrinho.")
        return

    carrinho.RetirarItem(produtoNoCarrinho, args.quantidade)
    armazenamento.SalvarCarrinho(cliente.email, carrinho)

    exibir_carrinho(carrinho, formatador)


def cmd_ver_carrinho(args, armazenamento, formatador):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    produtos = armazenamento.ListarProdutos()
    carrinho = armazenamento.CarregarCarrinho(cliente.email, produtos)

    exibir_carrinho(carrinho, formatador)


def cmd_confirmar_pedido(args, armazenamento, formatador):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    data = hoje()
    if args.data is not None:
        if not data_valida(args.data):
            return
        data = args.data

    if args.distancia < 0:
        print("A distância não pode ser negativa.")
        return

    produtos = armazenamento.ListarProdutos()
    carrinho = armazenamento.CarregarCarrinho(cliente.email, produtos)

    if not carrinho.itens:
        print("Seu carrinho está vazio.")
        return

    pedido = Pedidos(carrinho)

    pedido.DefinirFrete(args.distancia)
    if pedido.frete is None:
        print("Pedido não confirmado.")
        return

    pedido.DefinirPagamento(args.forma, args.parcelas)
    if pedido.pagamento is None:
        print("Pedido não confirmado.")
        return

    if args.cupom is not None:
        carregar_cupons(armazenamento)
        pedido.AplicarCupom(args.cupom.upper())

        if pedido.pagamento.desconto == 0:
            print("Pedido não confirmado: cupom indisponível.")
            return

    pedido.ConfirmarPedido()

    if pedido.status != "ENVIADO":
        return

    armazenamento.SalvarPedidoConfirmado(pedido, cliente.email, data)
    print(f"Prazo estimado de entrega: {pedido.frete.prazo} dias.")


def cmd_listar_pedidos(args, armazenamento, formatador):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    pedidos = armazenamento.ListarPedidos(cliente.email)

    if not pedidos:
        print("Você ainda não fez nenhum pedido.")
        return

    print("Seus pedidos:")
    for numero, registro in enumerate(pedidos, start = 1):
        quantidadeItens = 0
        for item in registro["itens"]:
            quantidadeItens += item["quantidade"]

        entrega = registro["dataEntrega"] if registro["dataEntrega"] is not None else "-"
        total = formatador.FormatarMoeda(registro["pagamento"]["valorTotal"])
        print(f"{numero}. {registro['protocolo']} | {registro['data']} | {registro['status']} | R$ {total} | {quantidadeItens} item(ns) | Entrega: {entrega}")


def cmd_entregar_pedido(args, armazenamento, formatador):
    if not data_valida(args.data):
        return

    registro = armazenamento.BuscarPedido(args.protocolo)

    if registro is None:
        print(f"Pedido '{args.protocolo}' não encontrado.")
        return

    if converter_data(args.data) < converter_data(registro["data"]):
        print(f"A data de entrega não pode ser anterior à data do pedido ({registro['data']}).")
        return

    pedido = Pedidos(Carrinho())
    pedido.RestaurarEstado(registro["status"], registro["protocolo"], registro["dataEntrega"])
    pedido.MarcarComoEntregue(args.data)

    if pedido.status == "ENTREGUE":
        armazenamento.AtualizarPedido(registro["protocolo"], pedido.status, pedido.dataEntrega)


def cmd_relatorio(args, armazenamento, formatador):
    inicio = args.inicio
    fim = args.fim

    if (inicio is None) != (fim is None):
        print("Informe --inicio e --fim juntos.")
        return

    if inicio is not None:
        if not data_valida(inicio) or not data_valida(fim):
            return

        if converter_data(inicio) > converter_data(fim):
            print("A data inicial não pode ser depois da data final.")
            return

    dados = armazenamento.CarregarRelatorio().GerarRelatorio(inicio, fim)

    if dados["quantidadeVendas"] == 0:
        print("Nenhuma venda registrada.")
        return

    print("RELATÓRIO DE VENDAS")
    print("(valores dos produtos vendidos, sem frete e sem descontos)")
    print(f"Vendas registradas: {dados['quantidadeVendas']}")
    print(f"Faturamento total: R$ {formatador.FormatarMoeda(dados['faturamentoTotal'])}")

    if dados["faturamentoPeriodo"] is not None:
        print(f"Faturamento de {inicio} a {fim}: R$ {formatador.FormatarMoeda(dados['faturamentoPeriodo'])}")

    print("Faturamento por categoria:")
    for categoria, valor in dados["vendasPorCategoria"].items():
        print(f"  - {categoria}: R$ {formatador.FormatarMoeda(valor)}")

    print(f"Produto mais vendido: {dados['produtoMaisVendido']}")


# ---------- Programa principal ----------

def main(argumentos = None, caminhoDados = CAMINHO_DADOS):
    parser = argparse.ArgumentParser(prog = "Loja", description = "Sistema de Loja Virtual Simplificada")

    subparsers = parser.add_subparsers(dest = "comando", required = True)

    # CADASTRO DE CLIENTES
    sp_cliente = subparsers.add_parser("cadastrar-cliente", help = "Cadastra um novo cliente.")
    sp_cliente.add_argument("--nome", required = True)
    sp_cliente.add_argument("--email", required = True)
    sp_cliente.add_argument("--senha", required = True)
    sp_cliente.add_argument("--idade", type = int, required = True)
    sp_cliente.add_argument("--endereco", required = True)

    # CADASTRO DE PRODUTOS
    sp_produtos = subparsers.add_parser("cadastrar-produto", help = "Cadastra um novo produto.")
    sp_produtos.add_argument("--nome", required = True)
    sp_produtos.add_argument("--categoria", required = True)
    sp_produtos.add_argument("--preco", type = float, required = True)
    sp_produtos.add_argument("--cor", required = True)
    sp_produtos.add_argument("--tamanho")
    sp_produtos.add_argument("--estoque", type = int, required = True)

    # LISTAR PRODUTOS
    subparsers.add_parser("listar-produtos", help = "Lista todos os produtos cadastrados.")

    # CADASTRO DE CUPONS (uso do administrador)
    sp_cupom = subparsers.add_parser("cadastrar-cupom", help = "Cadastra um novo cupom de desconto.")
    sp_cupom.add_argument("--codigo", required = True)
    sp_cupom.add_argument("--percentual", type = float, required = True)
    sp_cupom.add_argument("--valor-minimo", type = float, required = True)

    # LISTAR CUPONS
    sp_listar_cupons = subparsers.add_parser("listar-cupons", help = "Lista os cupons cadastrados (opcionalmente, só os válidos para um valor de compra).")
    sp_listar_cupons.add_argument("--valor", type = float)

    # ADICIONAR AO CARRINHO
    sp_carrinho = subparsers.add_parser("adicionar-carrinho", help = "Adiciona um produto ao carrinho.")
    sp_carrinho.add_argument("--email", required = True)
    sp_carrinho.add_argument("--senha", required = True)
    sp_carrinho.add_argument("--produto", required = True)
    sp_carrinho.add_argument("--quantidade", type = int, default = 1)

    # REMOVER DO CARRINHO
    sp_remover = subparsers.add_parser("remover-carrinho", help = "Retira unidades de um produto do carrinho.")
    sp_remover.add_argument("--email", required = True)
    sp_remover.add_argument("--senha", required = True)
    sp_remover.add_argument("--produto", required = True)
    sp_remover.add_argument("--quantidade", type = int, default = 1)

    # VER CARRINHO
    sp_ver = subparsers.add_parser("ver-carrinho", help = "Mostra os itens e o total do carrinho.")
    sp_ver.add_argument("--email", required = True)
    sp_ver.add_argument("--senha", required = True)

    # CONFIRMAR PEDIDO
    sp_pedido = subparsers.add_parser("confirmar-pedido", help = "Confirma o pedido a partir do carrinho.")
    sp_pedido.add_argument("--email", required = True)
    sp_pedido.add_argument("--senha", required = True)
    sp_pedido.add_argument("--distancia", type = float, required = True, help = "Distância até o endereço de entrega, em km.")
    sp_pedido.add_argument("--forma", required = True, help = "PIX, CARTAO_DEBITO, CARTAO_CREDITO ou BOLETO.")
    sp_pedido.add_argument("--parcelas", type = int, default = 1, help = "Número de parcelas (só vale para CARTAO_CREDITO).")
    sp_pedido.add_argument("--cupom", help = "Código de um cupom cadastrado.")
    sp_pedido.add_argument("--data", help = "Data do pedido no formato DD/MM/AAAA (padrão: hoje).")

    # LISTAR PEDIDOS
    sp_pedidos = subparsers.add_parser("listar-pedidos", help = "Lista os pedidos do cliente.")
    sp_pedidos.add_argument("--email", required = True)
    sp_pedidos.add_argument("--senha", required = True)

    # ENTREGAR PEDIDO (uso do administrador)
    sp_entregar = subparsers.add_parser("entregar-pedido", help = "Marca um pedido enviado como entregue.")
    sp_entregar.add_argument("--protocolo", required = True)
    sp_entregar.add_argument("--data", required = True, help = "Data da entrega no formato DD/MM/AAAA.")

    # RELATÓRIO DE VENDAS (uso do administrador)
    sp_relatorio = subparsers.add_parser("relatorio", help = "Mostra o relatório de vendas.")
    sp_relatorio.add_argument("--inicio", help = "Data inicial do período (DD/MM/AAAA).")
    sp_relatorio.add_argument("--fim", help = "Data final do período (DD/MM/AAAA).")

    args = parser.parse_args(argumentos)

    armazenamento = Armazenamento(caminhoDados)
    formatador = Pagamento()

    comandos = {
        "cadastrar-cliente": cmd_cadastrar_cliente,
        "cadastrar-produto": cmd_cadastrar_produto,
        "listar-produtos": cmd_listar_produtos,
        "cadastrar-cupom": cmd_cadastrar_cupom,
        "listar-cupons": cmd_listar_cupons,
        "adicionar-carrinho": cmd_adicionar_carrinho,
        "remover-carrinho": cmd_remover_carrinho,
        "ver-carrinho": cmd_ver_carrinho,
        "confirmar-pedido": cmd_confirmar_pedido,
        "listar-pedidos": cmd_listar_pedidos,
        "entregar-pedido": cmd_entregar_pedido,
        "relatorio": cmd_relatorio,
    }

    comandos[args.comando](args, armazenamento, formatador)


if __name__ == "__main__":
    main()