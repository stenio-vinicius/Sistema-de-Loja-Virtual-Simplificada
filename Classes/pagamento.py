from Classes.formatacao import FormatarMoeda


class Pagamento:
    """Calcula e conclui o pagamento de um pedido: aplica o desconto do cupom, soma o valor do frete e retorna o estado do pagamento (PENDENTE ou PAGO). É a classe-mãe das formas de pagamento: Pix, débito, crédito e boleto herdam daqui e definem a sua própria regra de valor."""

    FORMA = None

    def __init__(self):
        self._valor = None
        self._desconto = 0
        self._frete = 0
        self._status = "PENDENTE"

    def FormatarMoeda(self, valor):
        return FormatarMoeda(valor)

    def AplicarDesconto(self, valorDesconto):
        if valorDesconto < 0:
            valorDesconto = 0

        self._desconto = valorDesconto

    def CalcularTotal(self, valor, frete):
        valor_com_desconto = valor - self._desconto

        if valor_com_desconto < 0:
            valor_com_desconto = 0

        return valor_com_desconto + frete

    def PagarPedido(self, valor, frete):
        if self.FORMA is None:
            print("Forma de pagamento não definida. Use Pix, débito, crédito ou boleto.")
            return self._status

        self._valor = valor
        self._frete = frete

        valor_total = self.CalcularTotal(valor, frete)

        print(f"Valor total a pagar: R$ {self.FormatarMoeda(valor_total)}")
        print(f"Forma de pagamento: {self.FORMA}")

        self._status = "PAGO"
        return self._status

    @property
    def status(self):
        return self._status

    @property
    def forma(self):
        return self.FORMA

    @property
    def desconto(self):
        return self._desconto


class PagamentoPix(Pagamento):
    """Pagamento via Pix, com 5% de desconto sobre o total."""

    FORMA = "PIX"
    DESCONTO_PIX = 5

    def CalcularTotal(self, valor, frete):
        total = super().CalcularTotal(valor, frete)
        return total * (1 - self.DESCONTO_PIX / 100)


class PagamentoDebito(Pagamento):
    """Pagamento no cartão de débito, sem alteração no valor."""

    FORMA = "CARTAO_DEBITO"


class PagamentoCredito(Pagamento):
    """Pagamento no cartão de crédito, com parcelamento. Até 3 parcelas sem juros; acima disso, 3% de juros sobre o total."""

    FORMA = "CARTAO_CREDITO"
    PARCELAS_SEM_JUROS = 3
    JUROS_PERCENTUAL = 3

    def __init__(self, parcelas=1):
        super().__init__()

        if parcelas < 1:
            print("Número de parcelas inválido. Usando 1 parcela.")
            parcelas = 1

        self._parcelas = parcelas

    def CalcularTotal(self, valor, frete):
        total = super().CalcularTotal(valor, frete)

        if self._parcelas > self.PARCELAS_SEM_JUROS:
            total = total * (1 + self.JUROS_PERCENTUAL / 100)

        return total

    def PagarPedido(self, valor, frete):
        status = super().PagarPedido(valor, frete)

        valorParcela = self.CalcularTotal(valor, frete) / self._parcelas
        print(f"Parcelamento: {self._parcelas}x de R$ {self.FormatarMoeda(valorParcela)}")

        return status

    @property
    def parcelas(self):
        return self._parcelas


class PagamentoBoleto(Pagamento):
    """Pagamento via boleto, sem alteração no valor."""

    FORMA = "BOLETO"


FORMAS_PAGAMENTO = {
    "PIX": PagamentoPix,
    "CARTAO_DEBITO": PagamentoDebito,
    "CARTAO_CREDITO": PagamentoCredito,
    "BOLETO": PagamentoBoleto,
}


def CriarPagamento(forma, parcelas=1):
    classe = FORMAS_PAGAMENTO.get(forma.upper())

    if classe is None:
        print(f"Forma de pagamento inválida: {forma}")
        return None

    if classe is PagamentoCredito:
        return classe(parcelas)

    return classe()
