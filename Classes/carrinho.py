class Carrinho:
    """Armazena quais e quantos itens foram colocados no carrinho, observando também sua disponibilidade no estoque."""

    def __init__(self):
        self._itens = []

    def AdicionarItem(self, produto, quantidade):
        for item in self._itens:
            if item["produto"] == produto:
                item["quantidade"] += quantidade
                return
        self._itens.append({"produto": produto, "quantidade": quantidade})

    def RetirarItem(self, produto, quantidade):
        for item in self._itens:
            if item["produto"] == produto:
                if quantidade >= item["quantidade"]:
                    self._itens.remove(item)
                else:
                    item["quantidade"] -= quantidade
                return

    def CalcularTotal(self):
        total = 0
        for item in self._itens:
            total += item["produto"].preco * item["quantidade"]
        return total

    @property
    def itens(self):
        return self._itens
