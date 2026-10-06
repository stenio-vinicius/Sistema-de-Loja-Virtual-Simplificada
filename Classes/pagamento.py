class Pagamento:
    """Administra informações já inseridas, aplica cupom de desconto (se disponível), soma o valor do frete, controla a forma de pagamento escolhida pelo usuário e retorna o estado do pagamento (PENDENTE ou PAGO)."""

    CUPONS_VALIDOS = {}
    FORMAS_PAGAMENTO_VALIDAS = ["PIX", "CARTAO_DEBITO", "CARTAO_CREDITO", "BOLETO"]

    def __init__(self):
        self._valor = None
        self._desconto = 0
        self._frete = 0
        self._formaPagamento = None
        self._status = "PENDENTE"

    def FormatarMoeda(self, valor):
        return f"{valor:.2f}".replace(".", ",")

    def CadastrarCupom(self, codigo, percentual, valorMinimo):
        self.CUPONS_VALIDOS[codigo] = {
            "percentual": percentual,
            "valorMinimo": valorMinimo
        }

    def ListarCupons(self, valorCompra):
        algumCupomValido = False

        for codigo, regras in self.CUPONS_VALIDOS.items():
            if valorCompra >= regras["valorMinimo"]:
                print(f"{codigo}: {regras['percentual']}% (válido para compras acima de R$ {self.FormatarMoeda(regras['valorMinimo'])})")
                algumCupomValido = True

        if not algumCupomValido:
            print("Nenhum cupom disponível para o valor da sua compra.")

    def AplicarCupom(self, codigo, valorCompra):
        if codigo not in self.CUPONS_VALIDOS:
            print("Cupom de desconto indisponível!")
            return

        regras = self.CUPONS_VALIDOS[codigo]
        if valorCompra < regras["valorMinimo"]:
            print(f"Esse cupom só é válido para compras acima de R$ {self.FormatarMoeda(regras['valorMinimo'])}")
            return

        self._desconto = regras["percentual"]
        print(f"Cupom aplicado! {self._desconto}% de desconto.")

    def PagarPedido(self, valor, frete, formaPagamento):
        if formaPagamento not in self.FORMAS_PAGAMENTO_VALIDAS:
            print(f"Forma de pagamento inválida: {formaPagamento}")
            return self._status

        self._valor = valor
        self._frete = frete
        self._formaPagamento = formaPagamento

        valor_com_desconto = self._valor * (1 - self._desconto / 100)
        valor_total = valor_com_desconto + self._frete

        print(f"Valor total a pagar: R$ {self.FormatarMoeda(valor_total)}")
        print(f"Forma de pagamento: {self._formaPagamento}")

        self._status = "PAGO"
        return self._status

    @property
    def status(self):
        return self._status
