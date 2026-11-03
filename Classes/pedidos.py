import random
import string

from Classes.formatacao import FormatarMoeda
from Classes.frete import Frete
from Classes.pagamento import CriarPagamento
from Classes.validacoes import ConverterData


class Pedidos:
    """Coordena a compra, do carrinho até a entrega. Estados: CRIADO -> PAGO -> ENVIADO -> ENTREGUE, ou CRIADO -> CANCELADO, ou PAGO -> CANCELADO (com estorno de estoque). Aplica as regras de frete, cupom, estoque e cancelamento."""

    JANELA_CANCELAMENTO_DIAS = 7

    def __init__(self, carrinho, data = None):
        self._carrinho = carrinho
        self._data = data
        self._frete = None
        self._cupom = None
        self._valorDesconto = 0.0
        self._pagamento = None
        self._status = "CRIADO"
        self._numeroProtocolo = self._GerarNumeroProtocolo()
        self._codigoRastreio = None
        self._dataPagamento = None
        self._dataEntrega = None
        self._dataCancelamento = None

    def _GerarNumeroProtocolo(self):
        numeros = "".join(random.choices(string.digits, k=8))
        return f"PED{numeros}"

    def _GerarCodigoRastreio(self):
        letras = "".join(random.choices(string.ascii_uppercase, k=2))
        numeros = "".join(random.choices(string.digits, k=9))
        return f"{letras}{numeros}BR"

    def _ItemSemEstoque(self):
        for item in self._carrinho.itens:
            if item["quantidade"] > item["produto"].estoque:
                return item["produto"]

        return None

    def _DentroDaJanelaDeCancelamento(self, dataCancelamento):
        if dataCancelamento is None or self._dataPagamento is None:
            return True

        dias = (ConverterData(dataCancelamento) - ConverterData(self._dataPagamento)).days
        return dias <= self.JANELA_CANCELAMENTO_DIAS

    def RestaurarEstado(self, status, numeroProtocolo, data, dataPagamento, dataEntrega, dataCancelamento, codigoRastreio, valorDesconto, cupom, frete):
        self._status = status
        self._numeroProtocolo = numeroProtocolo
        self._data = data
        self._dataPagamento = dataPagamento
        self._dataEntrega = dataEntrega
        self._dataCancelamento = dataCancelamento
        self._codigoRastreio = codigoRastreio
        self._valorDesconto = valorDesconto
        self._cupom = cupom
        self._frete = frete

    def DefinirFrete(self, distancia = None):
        if self._status != "CRIADO":
            print(f"Não é possível alterar o frete de um pedido com status '{self._status}'.")
            return

        frete = Frete()

        if not self._carrinho.PossuiProdutoFisico():
            frete.Isentar()
            self._frete = frete
            return

        if distancia is None:
            print("Informe a distância: o pedido tem produtos físicos e o frete é obrigatório.")
            return

        if distancia < 0:
            print("A distância não pode ser negativa.")
            return

        if frete.CalcularFrete(distancia) is None:
            return

        frete.PrazoEstimado(distancia)
        self._frete = frete

    def AplicarCupom(self, cupom, data = None):
        if self._status != "CRIADO":
            print(f"Não é possível aplicar cupom em um pedido com status '{self._status}'.")
            return False

        motivo = cupom.MotivoDeRecusa(self._carrinho.itens, data)
        if motivo is not None:
            print(motivo)
            return False

        desconto = cupom.CalcularDesconto(self._carrinho.itens)
        subtotal = self._carrinho.CalcularTotal()

        if desconto > subtotal:
            desconto = subtotal

        self._cupom = cupom
        self._valorDesconto = desconto
        print(f"Cupom '{cupom.codigo}' aplicado! Desconto de R$ {FormatarMoeda(desconto)}.")
        return True

    def PagarPedido(self, forma, parcelas = 1, data = None):
        if self._status != "CRIADO":
            print(f"Não é possível pagar um pedido com status '{self._status}'.")
            return False

        if not self._carrinho.itens:
            print("Não é possível pagar um pedido com o carrinho vazio.")
            return False

        if self._frete is None:
            print("O frete precisa ser calculado antes do pagamento.")
            return False

        produtoSemEstoque = self._ItemSemEstoque()
        if produtoSemEstoque is not None:
            print(f"Estoque insuficiente de '{produtoSemEstoque.nome}'. O pedido não pode ser pago.")
            return False

        if self._cupom is not None:
            motivo = self._cupom.MotivoDeRecusa(self._carrinho.itens, data)
            if motivo is not None:
                print(f"{motivo} Cancele o pedido e crie outro sem o cupom.")
                return False

        pagamento = CriarPagamento(forma, parcelas)
        if pagamento is None:
            return False

        pagamento.AplicarDesconto(self._valorDesconto)

        if pagamento.PagarPedido(self._carrinho.CalcularTotal(), self._frete.valor) != "PAGO":
            return False

        for item in self._carrinho.itens:
            item["produto"].BaixarEstoque(item["quantidade"])

        if self._cupom is not None:
            self._cupom.RegistrarUso()

        self._pagamento = pagamento
        self._status = "PAGO"
        self._dataPagamento = data
        print("Pagamento confirmado!")
        return True

    def EnviarPedido(self):
        if self._status != "PAGO":
            print(f"Só é possível enviar um pedido pago. Status atual: '{self._status}'.")
            return False

        self._status = "ENVIADO"
        self._codigoRastreio = self._GerarCodigoRastreio()
        print(f"Pedido enviado! Código de rastreio: {self._codigoRastreio}")
        return True

    def MarcarComoEntregue(self, dataEntrega):
        if self._status != "ENVIADO":
            print(f"Não é possível marcar como entregue um pedido com status '{self._status}'.")
            return False

        self._status = "ENTREGUE"
        self._dataEntrega = dataEntrega
        print(f"Pedido marcado como entregue em {dataEntrega}.")
        return True

    def CancelarPedido(self, dataCancelamento = None):
        if self._status in ("ENVIADO", "ENTREGUE", "CANCELADO"):
            print(f"Não é possível cancelar um pedido com status '{self._status}'.")
            return False

        if self._status == "PAGO":
            if not self._DentroDaJanelaDeCancelamento(dataCancelamento):
                print(f"O prazo de cancelamento ({self.JANELA_CANCELAMENTO_DIAS} dias após o pagamento) já passou.")
                return False

            for item in self._carrinho.itens:
                item["produto"].EstornarEstoque(item["quantidade"])

            print("Estoque estornado.")

        self._status = "CANCELADO"
        self._dataCancelamento = dataCancelamento
        print("Pedido cancelado.")
        return True

    @property
    def carrinho(self):
        return self._carrinho

    @property
    def frete(self):
        return self._frete

    @property
    def cupom(self):
        return self._cupom

    @property
    def valorDesconto(self):
        return self._valorDesconto

    @property
    def pagamento(self):
        return self._pagamento

    @property
    def valorPrevisto(self):
        if self._frete is None:
            return None

        valor = self._carrinho.CalcularTotal() - self._valorDesconto
        if valor < 0:
            valor = 0

        return valor + self._frete.valor

    @property
    def valorTotal(self):
        if self._pagamento is None or self._frete is None:
            return None

        return self._pagamento.CalcularTotal(self._carrinho.CalcularTotal(), self._frete.valor)

    @property
    def status(self):
        return self._status

    @property
    def numeroProtocolo(self):
        return self._numeroProtocolo

    @property
    def codigoRastreio(self):
        return self._codigoRastreio

    @property
    def data(self):
        return self._data

    @property
    def dataPagamento(self):
        return self._dataPagamento

    @property
    def dataEntrega(self):
        return self._dataEntrega

    @property
    def dataCancelamento(self):
        return self._dataCancelamento
