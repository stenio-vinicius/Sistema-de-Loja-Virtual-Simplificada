class Pedidos:
    """Armazena informações daquele pedido e retorna um número de protocolo fictício e o estado do pedido (PENDENTE, ENVIADO, ENTREGUE ou CANCELADO)."""

    def __init__(self):
        self._status = "PENDENTE"

    def ConfirmarPedido(self):
        if self._status == "PENDENTE":
            self._status = "ENVIADO"
        else:
            print(f"Não é possível confirmar um pedido com status '{self._status}'.")

    def CancelarPedido(self):
        if self._status == "ENTREGUE":
            print("Não é possível cancelar um pedido já entregue.")
        else:
            self._status = "CANCELADO"

    @property
    def status(self):
        return self._status
