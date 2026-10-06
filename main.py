import argparse
 
def main():
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

    # ADICIONAR AO CARRINHO
    sp_carrinho = subparsers.add_parser("adicionar-carrinho", help = "Adiciona um produto ao carrinho.")
    sp_carrinho.add_argument("--produto", required = True)
    sp_carrinho.add_argument("--quantidade", type = int, default = 1)

    # CONFIRMAR PEDIDO
    subparsers.add_parser("confirmar-pedido", help = "Confirma o pedido a partir do carrinho.")

    args = parser.parse_args()
