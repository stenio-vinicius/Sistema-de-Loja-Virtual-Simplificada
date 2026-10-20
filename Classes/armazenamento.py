import json
import os

from Classes.carrinho import Carrinho
from Classes.cliente import Cliente
from Classes.pagamento import PagamentoCredito
from Classes.produto import Produto
from Classes.relatorio import Relatorio


class Armazenamento:
    """Cuida da leitura e da gravação dos dados da loja em um arquivo JSON."""

    def __init__(self, caminho="dados.json"):
        self._caminho = caminho

    def _Carregar(self):
        dados = {}

        if os.path.exists(self._caminho):
            with open(self._caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

        dados.setdefault("produtos", [])
        dados.setdefault("clientes", [])
        dados.setdefault("cupons", {})
        dados.setdefault("carrinhos", {})
        dados.setdefault("pedidos", [])
        dados.setdefault("vendas", [])
        return dados

    def _Salvar(self, dados):
        with open(self._caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    # ---------- Produtos ----------

    def SalvarProduto(self, produto):
        dados = self._Carregar()

        for existente in dados["produtos"]:
            if existente["nome"].lower() == produto.nome.lower():
                return False

        dados["produtos"].append({
            "nome": produto.nome,
            "categoria": produto.categoria,
            "preco": produto.preco,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "estoque": produto.estoque
        })
        self._Salvar(dados)
        return True

    def ListarProdutos(self):
        produtos = []

        for registro in self._Carregar()["produtos"]:
            produto = Produto()
            produto.CadastrarProduto(
                registro["nome"],
                registro["categoria"],
                registro["preco"],
                registro["cor"],
                registro["tamanho"],
                registro["estoque"]
            )
            produtos.append(produto)

        return produtos

    # ---------- Clientes ----------

    def _CriarCliente(self, registro):
        cliente = Cliente()
        cliente.CadastrarCliente(
            registro["nome"],
            registro["email"],
            registro["senha"],
            registro["idade"],
            registro["endereco"]
        )
        return cliente

    def SalvarCliente(self, cliente):
        dados = self._Carregar()

        for existente in dados["clientes"]:
            if existente["email"].lower() == cliente.email.lower():
                return False

        dados["clientes"].append({
            "nome": cliente.nome,
            "email": cliente.email,
            "senha": cliente.senha,
            "idade": cliente.idade,
            "endereco": cliente.endereco
        })
        self._Salvar(dados)
        return True

    def BuscarCliente(self, email):
        for registro in self._Carregar()["clientes"]:
            if registro["email"].lower() == email.lower():
                return self._CriarCliente(registro)

        return None

    def ListarClientes(self):
        clientes = []

        for registro in self._Carregar()["clientes"]:
            clientes.append(self._CriarCliente(registro))

        return clientes

    # ---------- Cupons ----------

    def SalvarCupom(self, codigo, percentual, valorMinimo):
        dados = self._Carregar()
        codigo = codigo.upper()

        if codigo in dados["cupons"]:
            return False

        dados["cupons"][codigo] = {
            "percentual": percentual,
            "valorMinimo": valorMinimo
        }
        self._Salvar(dados)
        return True

    def ListarCupons(self):
        return self._Carregar()["cupons"]

    # ---------- Carrinho (um por cliente, identificado pelo e-mail) ----------

    def SalvarCarrinho(self, email, carrinho):
        dados = self._Carregar()

        itens = []
        for item in carrinho.itens:
            itens.append({
                "produto": item["produto"].nome,
                "quantidade": item["quantidade"]
            })

        dados["carrinhos"][email.lower()] = itens
        self._Salvar(dados)

    def CarregarCarrinho(self, email, produtos):
        carrinho = Carrinho()

        for registro in self._Carregar()["carrinhos"].get(email.lower(), []):
            for produto in produtos:
                if produto.nome.lower() == registro["produto"].lower():
                    carrinho.AdicionarItem(produto, registro["quantidade"])
                    break

        return carrinho

    # ---------- Pedidos e vendas ----------

    def SalvarPedidoConfirmado(self, pedido, emailCliente, data):
        dados = self._Carregar()

        itens = []
        for item in pedido.carrinho.itens:
            produto = item["produto"]

            for registro in dados["produtos"]:
                if registro["nome"].lower() == produto.nome.lower():
                    registro["estoque"] = produto.estoque

            itens.append({
                "produto": produto.nome,
                "categoria": produto.categoria,
                "precoUnitario": produto.preco,
                "quantidade": item["quantidade"]
            })

            dados["vendas"].append({
                "produto": {
                    "nome": produto.nome,
                    "categoria": produto.categoria,
                    "preco": produto.preco
                },
                "quantidade": item["quantidade"],
                "valorTotal": produto.preco * item["quantidade"],
                "data": data
            })

        parcelas = None
        if isinstance(pedido.pagamento, PagamentoCredito):
            parcelas = pedido.pagamento.parcelas

        dados["pedidos"].append({
            "protocolo": pedido.numeroProtocolo,
            "cliente": emailCliente,
            "data": data,
            "status": pedido.status,
            "dataEntrega": pedido.dataEntrega,
            "itens": itens,
            "subtotal": pedido.carrinho.CalcularTotal(),
            "frete": {
                "distancia": pedido.frete.distancia,
                "valor": pedido.frete.valor,
                "prazo": pedido.frete.prazo
            },
            "pagamento": {
                "forma": pedido.pagamento.forma,
                "parcelas": parcelas,
                "desconto": pedido.pagamento.desconto,
                "valorTotal": pedido.valorTotal
            }
        })

        dados["carrinhos"][emailCliente.lower()] = []
        self._Salvar(dados)

    def BuscarPedido(self, protocolo):
        for registro in self._Carregar()["pedidos"]:
            if registro["protocolo"].upper() == protocolo.upper():
                return registro

        return None

    def ListarPedidos(self, email):
        pedidos = []

        for registro in self._Carregar()["pedidos"]:
            if registro["cliente"].lower() == email.lower():
                pedidos.append(registro)

        return pedidos

    def AtualizarPedido(self, protocolo, status, dataEntrega):
        dados = self._Carregar()

        for registro in dados["pedidos"]:
            if registro["protocolo"].upper() == protocolo.upper():
                registro["status"] = status
                registro["dataEntrega"] = dataEntrega
                self._Salvar(dados)
                return True

        return False

    def CarregarRelatorio(self):
        relatorio = Relatorio()

        for registro in self._Carregar()["vendas"]:
            produto = Produto()
            produto.CadastrarProduto(
                registro["produto"]["nome"],
                registro["produto"]["categoria"],
                registro["produto"]["preco"],
                None,
                None,
                None
            )
            relatorio.RegistrarVenda(produto, registro["quantidade"], registro["valorTotal"], registro["data"])

        return relatorio