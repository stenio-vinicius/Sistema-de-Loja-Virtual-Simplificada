import argparse


class Cliente:
    "Armazena dados pessoais do cliente, permitindo cadastro e atualização do perfil do mesmo."

    def CadastrarCliente(self, nome, email, senha, idade, endereco):
        pass

    def AtualizarPerfil(nome = None, email = None, senha = None, idade = None, endereco = None):
        pass

class Produto:
    "Armazena as informações dos produtos, permitindo cadastro e modificações futuras, exibindo dados para o estoque."

    def CadastrarProduto(nome, categoria, preco, cor, tamanho, estoque):
        pass

    def ModificarProduto(nome = None, categoria = None, preco = None, cor = None, tamanho = None, disponibilidade = None):
        pass

class Carrinho:
    "Armazena quais e quantos itens foram colocados no carrinho, observando também sua disponibilidade no estoque."

    def AdicionarItem(item, quantidade):
        pass

    def RetirarItem(item, quantidade):
        pass

    def CalcularTotal(quantidade, valor_item, valor_total):
        pass

class Pedidos:
    "Armazena informações daquele pedido e retorna um número de protocolo fictício e o estado do pedido (PENDENTE OU ENVIADO OU ENTREGUE)"

    def ConfirmarPedido(status):
        pass

    def CancelarPedido(status):
        pass

class Pagamento:
    "Administra informações já inseridas, aplica cupom de desconto (se disponível), soma o valor do frete, controla a forma de pagamento escolhida pelo usuário e retorna o estado do pagamento (PENDENTE OU PAGO) "

    def AplicarCupom(desconto):
        pass

    def PagarPedido(valor, desconto, frete):
        pass

class Frete:
    "Calcula o frete do referente pedido de acordo com a distância do endereço do remetente e do destinatário e estima um prazo de entrega proporcional ao valor do frete."

    def CalcularFrete(valor, distancia):
        pass

    def PrazoEstimado(prazo):
        pass

class Nota_Fiscal:
    "Retorna as informações mais importantes para controle do usúario."

    def GerarNota(nome_empresa, cnpj, data, hora, nome_cliente, itens_pedido, valor_item, valor_total, descontos, forma_pagamento, endereco, transportadora, numero_protocolo):
        pass
        
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
