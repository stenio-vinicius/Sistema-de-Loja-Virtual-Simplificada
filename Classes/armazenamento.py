import json
import os

from Classes.carrinho import Carrinho
from Classes.cliente import Cliente
from Classes.cupom import Cupom
from Classes.frete import Frete
from Classes.pagamento import PagamentoCredito
from Classes.pedidos import Pedidos
from Classes.produto import Produto, ProdutoDigital
from Classes.relatorio import Relatorio
from Classes.validacoes import NormalizarCpf


class Armazenamento:
    """Cuida da leitura e da gravação dos dados da loja em um arquivo JSON."""

    def __init__(self, caminho = "dados.json"):
        self._caminho = caminho

    def _Carregar(self):
        dados = {}

        if os.path.exists(self._caminho):
            with open(self._caminho, "r", encoding = "utf-8") as arquivo:
                dados = json.load(arquivo)

        dados.setdefault("produtos", [])
        dados.setdefault("clientes", [])
        dados.setdefault("cupons", {})
        dados.setdefault("carrinhos", {})
        dados.setdefault("pedidos", [])
        dados.setdefault("vendas", [])
        return dados

    def _Salvar(self, dados):
        with open(self._caminho, "w", encoding = "utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii = False, indent = 4)

    # ---------- Produtos ----------

    def _CriarProduto(self, registro):
        produto = ProdutoDigital() if registro.get("digital", False) else Produto()
        produto.CadastrarProduto(
            registro["nome"],
            registro["categoria"],
            registro["preco"],
            registro["cor"],
            registro["tamanho"],
            registro["estoque"],
            registro.get("sku")
        )
        return produto

    def SalvarProduto(self, produto):
        if produto.sku is None or produto.sku.strip() == "":
            return False

        dados = self._Carregar()

        for existente in dados["produtos"]:
            if existente.get("sku") is not None and existente["sku"].lower() == produto.sku.lower():
                return False

        dados["produtos"].append({
            "sku": produto.sku,
            "nome": produto.nome,
            "categoria": produto.categoria,
            "preco": produto.preco,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "estoque": produto.estoque,
            "digital": produto.digital
        })
        self._Salvar(dados)
        return True

    def ListarProdutos(self):
        produtos = []

        for registro in self._Carregar()["produtos"]:
            produtos.append(self._CriarProduto(registro))

        return produtos

    # ---------- Clientes ----------

    def _CriarCliente(self, registro):
        cliente = Cliente()
        cliente.CadastrarCliente(
            registro["nome"],
            registro["email"],
            registro["senha"],
            registro["idade"],
            registro["endereco"],
            registro.get("cpf")
        )
        return cliente

    def ExisteClienteComEmail(self, email):
        for registro in self._Carregar()["clientes"]:
            if registro["email"].lower() == email.lower():
                return True

        return False

    def ExisteClienteComCpf(self, cpf):
        for registro in self._Carregar()["clientes"]:
            if registro.get("cpf") is not None and registro["cpf"] == NormalizarCpf(cpf):
                return True

        return False

    def SalvarCliente(self, cliente):
        if self.ExisteClienteComEmail(cliente.email) or self.ExisteClienteComCpf(cliente.cpf):
            return False

        dados = self._Carregar()
        dados["clientes"].append({
            "nome": cliente.nome,
            "email": cliente.email,
            "senha": cliente.senha,
            "idade": cliente.idade,
            "endereco": cliente.endereco,
            "cpf": cliente.cpf
        })
        self._Salvar(dados)
        return True

    def BuscarCliente(self, email):
        for registro in self._Carregar()["clientes"]:
            if registro["email"].lower() == email.lower():
                return self._CriarCliente(registro)

        return None

    def AtualizarCliente(self, cliente):
        dados = self._Carregar()

        for registro in dados["clientes"]:
            if registro.get("cpf") is not None and registro["cpf"] == cliente.cpf and registro["email"].lower() != cliente.email.lower():
                return False

        for registro in dados["clientes"]:
            if registro["email"].lower() == cliente.email.lower():
                registro["nome"] = cliente.nome
                registro["senha"] = cliente.senha
                registro["idade"] = cliente.idade
                registro["endereco"] = cliente.endereco
                registro["cpf"] = cliente.cpf
                self._Salvar(dados)
                return True

        return False

    def ListarClientes(self):
        clientes = []

        for registro in self._Carregar()["clientes"]:
            clientes.append(self._CriarCliente(registro))

        return clientes

    # ---------- Cupons ----------

    def _CriarCupom(self, codigo, registro):
        cupom = Cupom()
        cupom.CadastrarCupom(
            codigo,
            registro["percentual"],
            registro["valorMinimo"],
            registro.get("validade"),
            registro.get("usoMaximo"),
            registro.get("categorias", []),
            registro.get("usos", 0)
        )
        return cupom

    def _RegistroDoCupom(self, cupom):
        return {
            "percentual": cupom.percentual,
            "valorMinimo": cupom.valorMinimo,
            "validade": cupom.validade,
            "usoMaximo": cupom.usoMaximo,
            "categorias": cupom.categorias,
            "usos": cupom.usos
        }

    def SalvarCupom(self, cupom):
        dados = self._Carregar()

        if cupom.codigo in dados["cupons"]:
            return False

        dados["cupons"][cupom.codigo] = self._RegistroDoCupom(cupom)
        self._Salvar(dados)
        return True

    def BuscarCupom(self, codigo):
        registro = self._Carregar()["cupons"].get(codigo.strip().upper())

        if registro is None:
            return None

        return self._CriarCupom(codigo.strip().upper(), registro)

    def ListarCupons(self):
        cupons = []

        for codigo, registro in self._Carregar()["cupons"].items():
            cupons.append(self._CriarCupom(codigo, registro))

        return cupons

    # ---------- Carrinho (um por cliente, identificado pelo e-mail) ----------

    def SalvarCarrinho(self, email, carrinho):
        dados = self._Carregar()

        itens = []
        for item in carrinho.itens:
            itens.append({
                "sku": item["produto"].sku,
                "quantidade": item["quantidade"]
            })

        dados["carrinhos"][email.lower()] = itens
        self._Salvar(dados)

    def CarregarCarrinho(self, email, produtos):
        carrinho = Carrinho()

        for registro in self._Carregar()["carrinhos"].get(email.lower(), []):
            for produto in produtos:
                if produto.sku is not None and produto.sku.lower() == registro["sku"].lower():
                    carrinho.RestaurarItem(produto, registro["quantidade"])
                    break

        return carrinho

    # ---------- Pedidos ----------

    def _ItensDoPedido(self, pedido):
        itens = []

        for item in pedido.carrinho.itens:
            produto = item["produto"]
            itens.append({
                "sku": produto.sku,
                "produto": produto.nome,
                "categoria": produto.categoria,
                "precoUnitario": produto.preco,
                "quantidade": item["quantidade"],
                "digital": produto.digital
            })

        return itens

    def _AtualizarEstoques(self, dados, pedido):
        for item in pedido.carrinho.itens:
            produto = item["produto"]

            for registro in dados["produtos"]:
                if registro.get("sku") is not None and registro["sku"].lower() == produto.sku.lower():
                    registro["estoque"] = produto.estoque

    def _AtualizarRegistro(self, dados, pedido):
        for registro in dados["pedidos"]:
            if registro["protocolo"].upper() == pedido.numeroProtocolo.upper():
                registro["status"] = pedido.status
                registro["codigoRastreio"] = pedido.codigoRastreio
                registro["dataPagamento"] = pedido.dataPagamento
                registro["dataEntrega"] = pedido.dataEntrega
                registro["dataCancelamento"] = pedido.dataCancelamento
                return registro

        return None

    def RegistrarPedidoCriado(self, pedido, emailCliente):
        dados = self._Carregar()

        cupom = None
        if pedido.cupom is not None:
            cupom = {"codigo": pedido.cupom.codigo, "valorDesconto": pedido.valorDesconto}

        dados["pedidos"].append({
            "protocolo": pedido.numeroProtocolo,
            "cliente": emailCliente,
            "data": pedido.data,
            "status": pedido.status,
            "itens": self._ItensDoPedido(pedido),
            "subtotal": pedido.carrinho.CalcularTotal(),
            "frete": {
                "distancia": pedido.frete.distancia,
                "valor": pedido.frete.valor,
                "prazo": pedido.frete.prazo
            },
            "cupom": cupom,
            "valorPrevisto": pedido.valorPrevisto,
            "pagamento": None,
            "codigoRastreio": None,
            "dataPagamento": None,
            "dataEntrega": None,
            "dataCancelamento": None
        })

        dados["carrinhos"][emailCliente.lower()] = []
        self._Salvar(dados)

    def RegistrarPagamento(self, pedido):
        dados = self._Carregar()
        registro = self._AtualizarRegistro(dados, pedido)

        parcelas = None
        if isinstance(pedido.pagamento, PagamentoCredito):
            parcelas = pedido.pagamento.parcelas

        registro["pagamento"] = {
            "forma": pedido.pagamento.forma,
            "parcelas": parcelas,
            "valorTotal": pedido.valorTotal
        }

        self._AtualizarEstoques(dados, pedido)

        for item in pedido.carrinho.itens:
            produto = item["produto"]
            dados["vendas"].append({
                "protocolo": pedido.numeroProtocolo,
                "produto": {
                    "sku": produto.sku,
                    "nome": produto.nome,
                    "categoria": produto.categoria,
                    "preco": produto.preco
                },
                "quantidade": item["quantidade"],
                "valorTotal": produto.preco * item["quantidade"],
                "data": pedido.dataPagamento
            })

        if pedido.cupom is not None:
            dados["cupons"][pedido.cupom.codigo] = self._RegistroDoCupom(pedido.cupom)

        self._Salvar(dados)

    def AtualizarPedido(self, pedido):
        dados = self._Carregar()

        if self._AtualizarRegistro(dados, pedido) is None:
            return False

        self._Salvar(dados)
        return True

    def RegistrarCancelamento(self, pedido, estavaPago):
        dados = self._Carregar()

        if self._AtualizarRegistro(dados, pedido) is None:
            return False

        if estavaPago:
            self._AtualizarEstoques(dados, pedido)

            vendasRestantes = []
            for venda in dados["vendas"]:
                if venda["protocolo"].upper() != pedido.numeroProtocolo.upper():
                    vendasRestantes.append(venda)

            dados["vendas"] = vendasRestantes

        self._Salvar(dados)
        return True

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

    def CarregarPedido(self, protocolo, produtos):
        registro = self.BuscarPedido(protocolo)

        if registro is None:
            return None

        carrinho = Carrinho()
        for item in registro["itens"]:
            for produto in produtos:
                if produto.sku is not None and produto.sku.lower() == item["sku"].lower():
                    carrinho.RestaurarItem(produto, item["quantidade"])
                    break

        frete = Frete()
        frete.Restaurar(registro["frete"]["distancia"], registro["frete"]["valor"], registro["frete"]["prazo"])

        cupom = None
        valorDesconto = 0.0
        if registro["cupom"] is not None:
            cupom = self.BuscarCupom(registro["cupom"]["codigo"])
            valorDesconto = registro["cupom"]["valorDesconto"]

        pedido = Pedidos(carrinho)
        pedido.RestaurarEstado(
            registro["status"],
            registro["protocolo"],
            registro["data"],
            registro["dataPagamento"],
            registro["dataEntrega"],
            registro["dataCancelamento"],
            registro["codigoRastreio"],
            valorDesconto,
            cupom,
            frete
        )
        return pedido

    # ---------- Relatório ----------

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
                None,
                registro["produto"].get("sku")
            )
            relatorio.RegistrarVenda(produto, registro["quantidade"], registro["valorTotal"], registro["data"])

        return relatorio
