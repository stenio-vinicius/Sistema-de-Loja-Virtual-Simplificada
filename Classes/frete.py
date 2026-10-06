class Frete:
    """Calcula o frete do referente pedido de acordo com a distância do endereço do remetente e do destinatário e estima um prazo de entrega proporcional ao valor do frete."""

    DISTANCIA_MAXIMA_KM = 3000

    def __init__(self):
        self._frete = None
        self._distancia = None
        self._prazo = None

    def CalcularFrete(self, distancia):
        if distancia > self.DISTANCIA_MAXIMA_KM:
            print(f"Não foi possível calcular o frete. Endereço informado acima de {self.DISTANCIA_MAXIMA_KM} km da distribuidora.")
            self._frete = None
            return self._frete

        self._frete = distancia * 0.1
        return self._frete

    def PrazoEstimado(self, distancia):
        if distancia <= 100:
            self._prazo = 2
        elif distancia <= 500:
            self._prazo = 5
        elif distancia <= 1500:
            self._prazo = 8
        elif distancia <= 2000:
            self._prazo = 11
        elif distancia <= 2500:
            self._prazo = 14
        elif distancia <= self.DISTANCIA_MAXIMA_KM:
            self._prazo = 17
        else:
            print(f"Não foi possível estimar um prazo de entrega. Endereço informado acima de {self.DISTANCIA_MAXIMA_KM} km da distribuidora.")
            self._prazo = None

        return self._prazo
