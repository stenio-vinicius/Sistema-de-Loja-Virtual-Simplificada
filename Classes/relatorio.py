class Relatorio:
    """Mostra um relatório de vendas com algumas informações, como: faturamento por período, faturamento total, vendas por categoria e produto mais vendido."""

    FORMATO_DATA = "%d/%m/%Y"

    def __init__(self):
        self._vendas = []

    def RegistrarVenda(self, produto, quantidade, valorTotal, data):
        self._vendas.append({
            "produto": produto,
            "quantidade": quantidade,
            "valorTotal": valorTotal,
            "data": data
        })

    def FaturamentoPorPeriodo(self, dataInicio, dataFim):
        inicio = datetime.strptime(dataInicio, self.FORMATO_DATA)
        fim = datetime.strptime(dataFim, self.FORMATO_DATA)

        total = 0
        for venda in self._vendas:
            dataVenda = datetime.strptime(venda["data"], self.FORMATO_DATA)
            if inicio <= dataVenda <= fim:
                total += venda["valorTotal"]
        return total

    def FaturamentoTotal(self):
        total = 0
        for venda in self._vendas:
            total += venda["valorTotal"]
        return total

    def VendasPorCategoria(self):
        vendasPorCategoria = {}
        for venda in self._vendas:
            categoria = venda["produto"].categoria
            if categoria not in vendasPorCategoria:
                vendasPorCategoria[categoria] = 0
            vendasPorCategoria[categoria] += venda["valorTotal"]
        return vendasPorCategoria

    def ProdutoMaisVendido(self):
        quantidadePorProduto = {}
        for venda in self._vendas:
            nome = venda["produto"].nome
            if nome not in quantidadePorProduto:
                quantidadePorProduto[nome] = 0
            quantidadePorProduto[nome] += venda["quantidade"]

        if not quantidadePorProduto:
            return None

        return max(quantidadePorProduto, key=quantidadePorProduto.get)
