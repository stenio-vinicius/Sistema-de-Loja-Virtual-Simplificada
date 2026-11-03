import argparse
from datetime import datetime

from Classes.armazenamento import Armazenamento
from Classes.cliente import Cliente
from Classes.cupom import Cupom
from Classes.formatacao import FormatarMoeda
from Classes.pedidos import Pedidos
from Classes.produto import Produto, ProdutoDigital
from Classes.relatorio import Relatorio
from Classes.validacoes import ConverterData, DataValida, FORMATO_DATA

CAMINHO_DADOS = "dados.json"


# ---------- Funções auxiliares ----------

def hoje():
    return datetime.now().strftime(FORMATO_DATA)


def obter_data(texto):
    if texto is None:
        return hoje()

    if not DataValida(texto):
        print(f"Data inválida: '{texto}'. Use o formato DD/MM/AAAA.")
        return None

    return texto


def autenticar(armazenamento, email, senha):
    cliente = armazenamento.BuscarCliente(email)

    if cliente is None or not cliente.VerificarSenha(senha):
        print("E-mail ou senha incorretos.")
        return None

    return cliente


def buscar_pedido_do_cliente(args, armazenamento):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return None

    registro = armazenamento.BuscarPedido(args.protocolo)

    if registro is None or registro["cliente"].lower() != cliente.email.lower():
        print(f"Pedido '{args.protocolo}' não encontrado.")
        return None

    return registro


def encontrar_produto(produtos, sku):
    for produto in produtos:
        if produto.sku is not None and produto.sku.lower() == sku.strip().lower():
            return produto

    return None


def exibir_carrinho(carrinho):
    if not carrinho.itens:
        print("Seu carrinho está vazio.")
        return

    print("Itens do carrinho:")
    for numero, item in enumerate(carrinho.itens, start = 1):
        produto = item["produto"]
        subtotal = produto.preco * item["quantidade"]
        print(f"{numero}. [{produto.sku}] {produto.nome} | {item['quantidade']}x R$ {FormatarMoeda(produto.preco)} = R$ {FormatarMoeda(subtotal)}")

    print(f"Total: R$ {FormatarMoeda(carrinho.CalcularTotal())}")


def descrever_cupom(cupom, data):
    validade = cupom.validade if cupom.validade is not None else "sem validade"

    if cupom.usoMaximo is not None:
        usos = f"{cupom.usos}/{cupom.usoMaximo}"
    else:
        usos = f"{cupom.usos} (sem limite)"

    categorias = ", ".join(cupom.categorias) if cupom.categorias else "todas"

    return f"{cupom.codigo}: {cupom.percentual:g}% | mínimo R$ {FormatarMoeda(cupom.valorMinimo)} | validade: {validade} | usos: {usos} | categorias: {categorias} | {cupom.Situacao(data)}"


def mostrar_problemas(problemas):
    for problema in problemas:
        print(problema)


# ---------- Clientes ----------

def cmd_cadastrar_cliente(args, armazenamento):
    cliente = Cliente()
    cliente.CadastrarCliente(args.nome, args.email, args.senha, args.idade, args.endereco, args.cpf)

    problemas = cliente.Problemas()
    if problemas:
        mostrar_problemas(problemas)
        print("Cliente não cadastrado.")
        return

    if armazenamento.ExisteClienteComEmail(cliente.email):
        print(f"Já existe um cliente com o e-mail '{cliente.email}'.")
        return

    if armazenamento.ExisteClienteComCpf(cliente.cpf):
        print("Já existe um cliente com esse CPF.")
        return

    armazenamento.SalvarCliente(cliente)
    print(f"Cliente '{cliente.nome}' cadastrado com sucesso!")


def cmd_atualizar_cliente(args, armazenamento):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    cliente.AtualizarPerfil(nome = args.nome, senha = args.nova_senha, idade = args.idade, endereco = args.endereco, cpf = args.cpf)

    problemas = cliente.Problemas()
    if problemas:
        mostrar_problemas(problemas)
        print("Cadastro não atualizado.")
        return

    if not armazenamento.AtualizarCliente(cliente):
        print("Já existe outro cliente com esse CPF.")
        return

    print("Cadastro atualizado com sucesso!")


# ---------- Produtos ----------

def cmd_cadastrar_produto(args, armazenamento):
    sku = args.sku.strip()

    problemas = []
    if sku == "":
        problemas.append("O SKU é obrigatório.")
    if args.preco <= 0:
        problemas.append("O preço deve ser maior que zero.")
    if args.estoque < 0:
        problemas.append("O estoque não pode ser negativo.")
    if not args.digital and args.cor is None:
        problemas.append("Produtos físicos precisam de cor (--cor).")

    if problemas:
        mostrar_problemas(problemas)
        print("Produto não cadastrado.")
        return

    produto = ProdutoDigital() if args.digital else Produto()
    produto.CadastrarProduto(args.nome, args.categoria, args.preco, args.cor, args.tamanho, args.estoque, sku)

    if armazenamento.SalvarProduto(produto):
        print(f"Produto '{produto.nome}' (SKU {produto.sku}) cadastrado com sucesso!")
    else:
        print(f"Já existe um produto com o SKU '{sku}'.")


def cmd_listar_produtos(args, armazenamento):
    produtos = armazenamento.ListarProdutos()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print("Produtos cadastrados:")
    for numero, produto in enumerate(produtos, start = 1):
        tipo = "Digital" if produto.digital else "Físico"
        cor = produto.cor if produto.cor is not None else "-"
        tamanho = produto.tamanho if produto.tamanho is not None else "-"
        print(f"{numero}. [{produto.sku}] {produto.nome} | {produto.categoria} | R$ {FormatarMoeda(produto.preco)} | {tipo} | Cor: {cor} | Tamanho: {tamanho} | Estoque: {produto.estoque}")


# ---------- Cupons ----------

def cmd_cadastrar_cupom(args, armazenamento):
    categorias = []
    if args.categorias is not None:
        categorias = args.categorias.split(",")

    cupom = Cupom()
    cupom.CadastrarCupom(args.codigo, args.percentual, args.valor_minimo, args.validade, args.uso_maximo, categorias)

    problemas = cupom.Problemas()
    if problemas:
        mostrar_problemas(problemas)
        print("Cupom não cadastrado.")
        return

    if armazenamento.SalvarCupom(cupom):
        print(f"Cupom '{cupom.codigo}' cadastrado: {cupom.percentual:g}% de desconto para compras acima de R$ {FormatarMoeda(cupom.valorMinimo)}.")
        print(descrever_cupom(cupom, hoje()))
    else:
        print(f"Já existe um cupom com o código '{cupom.codigo}'.")


def cmd_listar_cupons(args, armazenamento):
    cupons = armazenamento.ListarCupons()

    if not cupons:
        print("Nenhum cupom cadastrado.")
        return

    exibidos = 0
    for cupom in cupons:
        if args.valor is not None and args.valor < cupom.valorMinimo:
            continue

        print(descrever_cupom(cupom, hoje()))
        exibidos += 1

    if exibidos == 0:
        print("Nenhum cupom disponível para o valor informado.")


# ---------- Carrinho ----------

def cmd_adicionar_carrinho(args, armazenamento):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    if args.quantidade < 1:
        print("A quantidade deve ser pelo menos 1.")
        return

    produtos = armazenamento.ListarProdutos()
    produto = encontrar_produto(produtos, args.sku)

    if produto is None:
        print(f"Produto com SKU '{args.sku}' não encontrado.")
        return

    carrinho = armazenamento.CarregarCarrinho(cliente.email, produtos)
    carrinho.AdicionarItem(produto, args.quantidade)
    armazenamento.SalvarCarrinho(cliente.email, carrinho)

    exibir_carrinho(carrinho)


def cmd_remover_carrinho(args, armazenamento):
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
        if item["produto"].sku.lower() == args.sku.strip().lower():
            produtoNoCarrinho = item["produto"]

    if produtoNoCarrinho is None:
        print(f"O SKU '{args.sku}' não está no seu carrinho.")
        return

    carrinho.RetirarItem(produtoNoCarrinho, args.quantidade)
    armazenamento.SalvarCarrinho(cliente.email, carrinho)

    exibir_carrinho(carrinho)


def cmd_ver_carrinho(args, armazenamento):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    produtos = armazenamento.ListarProdutos()
    exibir_carrinho(armazenamento.CarregarCarrinho(cliente.email, produtos))


# ---------- Pedidos ----------

def cmd_criar_pedido(args, armazenamento):
    cliente = autenticar(armazenamento, args.email, args.senha)
    if cliente is None:
        return

    data = obter_data(args.data)
    if data is None:
        return

    problemas = cliente.Problemas()
    if problemas:
        print("Cadastro incompleto ou inválido. Corrija antes de fechar o pedido (comando atualizar-cliente):")
        mostrar_problemas(problemas)
        return

    produtos = armazenamento.ListarProdutos()
    carrinho = armazenamento.CarregarCarrinho(cliente.email, produtos)

    if not carrinho.itens:
        print("Seu carrinho está vazio.")
        return

    for item in carrinho.itens:
        produto = item["produto"]
        if item["quantidade"] > produto.estoque:
            print(f"Estoque insuficiente de '{produto.nome}': o carrinho tem {item['quantidade']}, mas há {produto.estoque} em estoque. Ajuste o carrinho (remover-carrinho) e tente de novo.")
            return

    pedido = Pedidos(carrinho, data)

    pedido.DefinirFrete(args.distancia)
    if pedido.frete is None:
        print("Pedido não criado.")
        return

    if args.cupom is not None:
        cupom = armazenamento.BuscarCupom(args.cupom)

        if cupom is None:
            print(f"Cupom '{args.cupom}' não encontrado.")
            print("Pedido não criado.")
            return

        if not pedido.AplicarCupom(cupom, data):
            print("Pedido não criado.")
            return

    armazenamento.RegistrarPedidoCriado(pedido, cliente.email)

    print(f"Pedido {pedido.numeroProtocolo} criado (status {pedido.status}).")
    print(f"Subtotal: R$ {FormatarMoeda(carrinho.CalcularTotal())}")
    if pedido.cupom is not None:
        print(f"Desconto do cupom {pedido.cupom.codigo}: - R$ {FormatarMoeda(pedido.valorDesconto)}")

    if pedido.frete.valor == 0 and not carrinho.PossuiProdutoFisico():
        print("Frete: R$ 0,00 (produtos digitais não somam frete)")
    else:
        print(f"Frete: R$ {FormatarMoeda(pedido.frete.valor)} (prazo estimado: {pedido.frete.prazo} dias)")

    print(f"Total previsto: R$ {FormatarMoeda(pedido.valorPrevisto)} (a forma de pagamento pode alterar o valor)")
    print(f"Para pagar: pagar-pedido --protocolo {pedido.numeroProtocolo} --forma PIX|CARTAO_DEBITO|CARTAO_CREDITO|BOLETO")


def cmd_pagar_pedido(args, armazenamento):
    registro = buscar_pedido_do_cliente(args, armazenamento)
    if registro is None:
        return

    data = obter_data(args.data)
    if data is None:
        return

    pedido = armazenamento.CarregarPedido(args.protocolo, armazenamento.ListarProdutos())

    if pedido.PagarPedido(args.forma, args.parcelas, data):
        armazenamento.RegistrarPagamento(pedido)


def cmd_enviar_pedido(args, armazenamento):
    if armazenamento.BuscarPedido(args.protocolo) is None:
        print(f"Pedido '{args.protocolo}' não encontrado.")
        return

    pedido = armazenamento.CarregarPedido(args.protocolo, armazenamento.ListarProdutos())

    if pedido.EnviarPedido():
        armazenamento.AtualizarPedido(pedido)


def cmd_entregar_pedido(args, armazenamento):
    if not DataValida(args.data):
        print(f"Data inválida: '{args.data}'. Use o formato DD/MM/AAAA.")
        return

    registro = armazenamento.BuscarPedido(args.protocolo)

    if registro is None:
        print(f"Pedido '{args.protocolo}' não encontrado.")
        return

    if ConverterData(args.data) < ConverterData(registro["data"]):
        print(f"A data de entrega não pode ser anterior à data do pedido ({registro['data']}).")
        return

    pedido = armazenamento.CarregarPedido(args.protocolo, armazenamento.ListarProdutos())

    if pedido.MarcarComoEntregue(args.data):
        armazenamento.AtualizarPedido(pedido)


def cmd_cancelar_pedido(args, armazenamento):
    registro = buscar_pedido_do_cliente(args, armazenamento)
    if registro is None:
        return

    data = obter_data(args.data)
    if data is None:
        return

    pedido = armazenamento.CarregarPedido(args.protocolo, armazenamento.ListarProdutos())
    estavaPago = pedido.status == "PAGO"

    if pedido.CancelarPedido(data):
        armazenamento.RegistrarCancelamento(pedido, estavaPago)


def cmd_listar_pedidos(args, armazenamento):
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

        if registro["pagamento"] is not None:
            total = registro["pagamento"]["valorTotal"]
        else:
            total = registro["valorPrevisto"]

        rastreio = registro["codigoRastreio"] if registro["codigoRastreio"] is not None else "-"
        entrega = registro["dataEntrega"] if registro["dataEntrega"] is not None else "-"
        print(f"{numero}. {registro['protocolo']} | {registro['data']} | {registro['status']} | R$ {FormatarMoeda(total)} | {quantidadeItens} item(ns) | Rastreio: {rastreio} | Entrega: {entrega}")


# ---------- Relatório ----------

def cmd_relatorio(args, armazenamento):
    inicio = args.inicio
    fim = args.fim

    if (inicio is None) != (fim is None):
        print("Informe --inicio e --fim juntos.")
        return

    if inicio is not None:
        for texto in (inicio, fim):
            if not DataValida(texto):
                print(f"Data inválida: '{texto}'. Use o formato DD/MM/AAAA.")
                return

        if ConverterData(inicio) > ConverterData(fim):
            print("A data inicial não pode ser depois da data final.")
            return

    dados = armazenamento.CarregarRelatorio().GerarRelatorio(inicio, fim)

    if dados["quantidadeVendas"] == 0:
        print("Nenhuma venda registrada.")
        return

    print("RELATÓRIO DE VENDAS")
    print("(pedidos pagos; valores dos produtos, sem frete e sem descontos)")
    print(f"Vendas registradas: {dados['quantidadeVendas']}")
    print(f"Faturamento total: R$ {FormatarMoeda(dados['faturamentoTotal'])}")

    if dados["faturamentoPeriodo"] is not None:
        print(f"Faturamento de {inicio} a {fim}: R$ {FormatarMoeda(dados['faturamentoPeriodo'])}")

    print("Faturamento por categoria:")
    for categoria, valor in dados["vendasPorCategoria"].items():
        print(f"  - {categoria}: R$ {FormatarMoeda(valor)}")

    print(f"Produto mais vendido: {dados['produtoMaisVendido']}")


# ---------- Programa principal ----------

def criar_parser():
    parser = argparse.ArgumentParser(prog = "Loja", description = "Sistema de Loja Virtual Simplificada")
    subparsers = parser.add_subparsers(dest = "comando", required = True)

    # CLIENTES
    sp = subparsers.add_parser("cadastrar-cliente", help = "Cadastra um novo cliente (e-mail e CPF únicos e válidos).")
    sp.add_argument("--nome", required = True)
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--idade", type = int, required = True)
    sp.add_argument("--endereco", required = True)
    sp.add_argument("--cpf", required = True)

    sp = subparsers.add_parser("atualizar-cliente", help = "Atualiza o cadastro do cliente.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--nome")
    sp.add_argument("--nova-senha")
    sp.add_argument("--idade", type = int)
    sp.add_argument("--endereco")
    sp.add_argument("--cpf")

    # PRODUTOS
    sp = subparsers.add_parser("cadastrar-produto", help = "Cadastra um novo produto (SKU único).")
    sp.add_argument("--sku", required = True)
    sp.add_argument("--nome", required = True)
    sp.add_argument("--categoria", required = True)
    sp.add_argument("--preco", type = float, required = True)
    sp.add_argument("--cor", help = "Obrigatória para produtos físicos.")
    sp.add_argument("--tamanho")
    sp.add_argument("--estoque", type = int, required = True)
    sp.add_argument("--digital", action = "store_true", help = "Produto digital: não soma frete.")

    subparsers.add_parser("listar-produtos", help = "Lista todos os produtos cadastrados.")

    # CUPONS (uso do administrador)
    sp = subparsers.add_parser("cadastrar-cupom", help = "Cadastra um novo cupom de desconto.")
    sp.add_argument("--codigo", required = True)
    sp.add_argument("--percentual", type = float, required = True)
    sp.add_argument("--valor-minimo", type = float, required = True)
    sp.add_argument("--validade", help = "Última data de uso (DD/MM/AAAA).")
    sp.add_argument("--uso-maximo", type = int, help = "Quantas vezes o cupom pode ser usado no total.")
    sp.add_argument("--categorias", help = "Categorias elegíveis, separadas por vírgula (padrão: todas).")

    sp = subparsers.add_parser("listar-cupons", help = "Lista os cupons cadastrados.")
    sp.add_argument("--valor", type = float, help = "Mostra só os cupons cujo valor mínimo cabe nessa compra.")

    # CARRINHO
    sp = subparsers.add_parser("adicionar-carrinho", help = "Adiciona um produto ao carrinho.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--sku", required = True)
    sp.add_argument("--quantidade", type = int, default = 1)

    sp = subparsers.add_parser("remover-carrinho", help = "Retira unidades de um produto do carrinho.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--sku", required = True)
    sp.add_argument("--quantidade", type = int, default = 1)

    sp = subparsers.add_parser("ver-carrinho", help = "Mostra os itens e o total do carrinho.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)

    # PEDIDOS
    sp = subparsers.add_parser("criar-pedido", help = "Cria o pedido (CRIADO) a partir do carrinho, calculando o frete e aplicando o cupom.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--distancia", type = float, help = "Distância até o endereço, em km (obrigatória se houver produto físico).")
    sp.add_argument("--cupom", help = "Código de um cupom cadastrado.")
    sp.add_argument("--data", help = "Data do pedido (DD/MM/AAAA). Padrão: hoje.")

    sp = subparsers.add_parser("pagar-pedido", help = "Paga um pedido CRIADO (PAGO) e baixa o estoque.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--protocolo", required = True)
    sp.add_argument("--forma", required = True, help = "PIX, CARTAO_DEBITO, CARTAO_CREDITO ou BOLETO.")
    sp.add_argument("--parcelas", type = int, default = 1, help = "Número de parcelas (só vale para CARTAO_CREDITO).")
    sp.add_argument("--data", help = "Data do pagamento (DD/MM/AAAA). Padrão: hoje.")

    sp = subparsers.add_parser("enviar-pedido", help = "Envia um pedido PAGO (ENVIADO) e gera o código de rastreio.")
    sp.add_argument("--protocolo", required = True)

    sp = subparsers.add_parser("entregar-pedido", help = "Marca um pedido ENVIADO como ENTREGUE.")
    sp.add_argument("--protocolo", required = True)
    sp.add_argument("--data", required = True, help = "Data da entrega (DD/MM/AAAA).")

    sp = subparsers.add_parser("cancelar-pedido", help = "Cancela um pedido CRIADO ou PAGO (estorna o estoque se já estiver pago).")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)
    sp.add_argument("--protocolo", required = True)
    sp.add_argument("--data", help = "Data do cancelamento (DD/MM/AAAA). Padrão: hoje.")

    sp = subparsers.add_parser("listar-pedidos", help = "Lista os pedidos do cliente.")
    sp.add_argument("--email", required = True)
    sp.add_argument("--senha", required = True)

    # RELATÓRIO (uso do administrador)
    sp = subparsers.add_parser("relatorio", help = "Mostra o relatório de vendas.")
    sp.add_argument("--inicio", help = "Data inicial do período (DD/MM/AAAA).")
    sp.add_argument("--fim", help = "Data final do período (DD/MM/AAAA).")

    return parser


COMANDOS = {
    "cadastrar-cliente": cmd_cadastrar_cliente,
    "atualizar-cliente": cmd_atualizar_cliente,
    "cadastrar-produto": cmd_cadastrar_produto,
    "listar-produtos": cmd_listar_produtos,
    "cadastrar-cupom": cmd_cadastrar_cupom,
    "listar-cupons": cmd_listar_cupons,
    "adicionar-carrinho": cmd_adicionar_carrinho,
    "remover-carrinho": cmd_remover_carrinho,
    "ver-carrinho": cmd_ver_carrinho,
    "criar-pedido": cmd_criar_pedido,
    "pagar-pedido": cmd_pagar_pedido,
    "enviar-pedido": cmd_enviar_pedido,
    "entregar-pedido": cmd_entregar_pedido,
    "cancelar-pedido": cmd_cancelar_pedido,
    "listar-pedidos": cmd_listar_pedidos,
    "relatorio": cmd_relatorio,
}


def main(argumentos = None, caminhoDados = CAMINHO_DADOS):
    args = criar_parser().parse_args(argumentos)
    COMANDOS[args.comando](args, Armazenamento(caminhoDados))


if __name__ == "__main__":
    main()
