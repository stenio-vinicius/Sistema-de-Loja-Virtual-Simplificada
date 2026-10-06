import random
import string


class Pedidos:
    """Armazena informações daquele pedido e retorna um número de protocolo fictício e o estado do pedido (PENDENTE, ENVIADO, ENTREGUE ou CANCELADO)."""

    def __init__(self):
        self._status = "PENDENTE"
        self._numeroProtocolo = None
        self._dataEntrega = None

    def _GerarNumeroProtocolo(self):
        letras = "".join(random.choices(string.ascii_uppercase, k=2))
        numeros = "".join(random.choices(string.digits, k=9))
        return f"{letras}{numeros}BR"

    def ConfirmarPedido(self):
        if self._status == "PENDENTE":
            self._status = "ENVIADO"
            self._numeroProtocolo = self._GerarNumeroProtocolo()
            print(f"Pedido confirmado! Número de protocolo: {self._numeroProtocolo}")
        else:
            print(f"Não é possível confirmar um pedido com status '{self._status}'.")

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
    def status(self):
        return self._status

    @property
    def numeroProtocolo(self):
        return self._numeroProtocolo

    @property
    def dataEntrega(self):
        return self._dataEntrega
