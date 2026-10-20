import random
import string

from Classes.frete import Frete
from Classes.pagamento import CriarPagamento


class Pedidos:
    """Coordena a compra: recebe o carrinho, define o frete e a forma de pagamento, confirma o pedido (cobrando o pagamento e baixando o estoque) e acompanha o seu estado (PENDENTE, ENVIADO, ENTREGUE ou CANCELADO), gerando um número de protocolo fictício ao confirmar."""

    def __init__(self, carrinho):
        self._carrinho = carrinho
        self._frete = None
        self._pagamento = None
        self._status = "PENDENTE"
        self._numeroProtocolo = None
        self._dataEntrega = None

    def _GerarNumeroProtocolo(self):
        letras = "".join(random.choices(string.ascii_uppercase, k=2))
        numeros = "".join(random.choices(string.digits, k=9))
        return f"{letras}{numeros}BR"

    def RestaurarEstado(self, status, numeroProtocolo, dataEntrega):
        self._status = status
        self._numeroProtocolo = numeroProtocolo
        self._dataEntrega = dataEntrega

    def DefinirFrete(self, distancia):
        if self._status != "PENDENTE":
            print(f"Não é possível alterar o frete de um pedido com status '{self._status}'.")
            return

        frete = Frete()

        if frete.CalcularFrete(distancia) is None:
            return

        frete.PrazoEstimado(distancia)
        self._frete = frete

    def DefinirPagamento(self, forma, parcelas=1):
        if self._status != "PENDENTE":
            print(f"Não é possível alterar o pagamento de um pedido com status '{self._status}'.")
            return

        pagamento = CriarPagamento(forma, parcelas)

        if pagamento is not None:
            self._pagamento = pagamento

    def AplicarCupom(self, codigo):
        if self._pagamento is None:
            print("Defina a forma de pagamento antes de aplicar um cupom.")
            return

        self._pagamento.AplicarCupom(codigo, self._carrinho.CalcularTotal())

    def ConfirmarPedido(self):
        if self._status != "PENDENTE":
            print(f"Não é possível confirmar um pedido com status '{self._status}'.")
            return

        if not self._carrinho.itens:
            print("Não é possível confirmar um pedido com o carrinho vazio.")
            return

        if self._frete is None:
            print("Defina o frete antes de confirmar o pedido.")
            return

        if self._pagamento is None:
            print("Defina a forma de pagamento antes de confirmar o pedido.")
            return

        for item in self._carrinho.itens:
            if item["quantidade"] > item["produto"].estoque:
                print(f"Estoque insuficiente de '{item['produto'].nome}'. Atualize o carrinho antes de confirmar.")
                return

        statusPagamento = self._pagamento.PagarPedido(self._carrinho.CalcularTotal(), self._frete.valor)

        if statusPagamento == "PAGO":
            for item in self._carrinho.itens:
                item["produto"].BaixarEstoque(item["quantidade"])

            self._status = "ENVIADO"
            self._numeroProtocolo = self._GerarNumeroProtocolo()
            print(f"Pedido confirmado! Número de protocolo: {self._numeroProtocolo}")

    def MarcarComoEntregue(self, dataEntrega):
        if self._status == "ENVIADO":
            self._status = "ENTREGUE"
            self._dataEntrega = dataEntrega
            print(f"Pedido marcado como entregue em {dataEntrega}.")
        else:
            print(f"Não é possível marcar como entregue um pedido com status '{self._status}'.")

    def CancelarPedido(self):
        if self._status == "ENTREGUE":
            print("Não é possível cancelar um pedido já entregue.")
        else:
            self._status = "CANCELADO"

    @property
    def carrinho(self):
        return self._carrinho

    @property
    def frete(self):
        return self._frete

    @property
    def pagamento(self):
        return self._pagamento

    @property
    def valorTotal(self):
        if self._frete is None or self._pagamento is None:
            return None

        return self._pagamento.CalcularTotal(self._carrinho.CalcularTotal(), self._frete.valor)

    @property
    def status(self):
        return self._status

    @property
    def numeroProtocolo(self):
        return self._numeroProtocolo

    @property
    def dataEntrega(self):
        return self._dataEntrega