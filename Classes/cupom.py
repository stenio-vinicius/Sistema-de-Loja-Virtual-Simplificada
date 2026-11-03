from Classes.formatacao import FormatarMoeda
from Classes.validacoes import ConverterData, DataValida


class Cupom:
    """Cupom de desconto percentual com regras próprias: valor mínimo de compra, data de validade, número máximo de usos e categorias elegíveis."""

    def __init__(self):
        self._codigo = None
        self._percentual = None
        self._valorMinimo = 0
        self._validade = None
        self._usoMaximo = None
        self._categorias = []
        self._usos = 0

    def CadastrarCupom(self, codigo, percentual, valorMinimo = 0, validade = None, usoMaximo = None, categorias = None, usos = 0):
        self._codigo = codigo.strip().upper() if codigo is not None else None
        self._percentual = percentual
        self._valorMinimo = valorMinimo
        self._validade = validade
        self._usoMaximo = usoMaximo
        self._categorias = []
        self._usos = usos

        if categorias is not None:
            for categoria in categorias:
                if categoria.strip() != "":
                    self._categorias.append(categoria.strip())

    def Problemas(self):
        problemas = []

        if not self._codigo:
            problemas.append("O código do cupom é obrigatório.")
        if self._percentual is None or not (0 < self._percentual <= 100):
            problemas.append("O percentual deve ser maior que 0 e no máximo 100.")
        if self._valorMinimo < 0:
            problemas.append("O valor mínimo não pode ser negativo.")
        if self._validade is not None and not DataValida(self._validade):
            problemas.append("Validade inválida. Use o formato DD/MM/AAAA.")
        if self._usoMaximo is not None and self._usoMaximo < 1:
            problemas.append("O uso máximo deve ser pelo menos 1.")

        return problemas

    def _ItensElegiveis(self, itens):
        if not self._categorias:
            return itens

        categoriasElegiveis = []
        for categoria in self._categorias:
            categoriasElegiveis.append(categoria.lower())

        elegiveis = []
        for item in itens:
            if item["produto"].categoria.lower() in categoriasElegiveis:
                elegiveis.append(item)

        return elegiveis

    def MotivoDeRecusa(self, itens, data):
        if self._validade is not None and data is not None and ConverterData(data) > ConverterData(self._validade):
            return f"Cupom '{self._codigo}' expirado em {self._validade}."

        if self._usoMaximo is not None and self._usos >= self._usoMaximo:
            return f"Cupom '{self._codigo}' esgotado: o limite de {self._usoMaximo} uso(s) já foi atingido."

        if not self._ItensElegiveis(itens):
            return f"Nenhum item do carrinho é elegível para o cupom '{self._codigo}' (categorias: {', '.join(self._categorias)})."

        totalDaCompra = 0
        for item in itens:
            totalDaCompra += item["produto"].preco * item["quantidade"]

        if totalDaCompra < self._valorMinimo:
            return f"O cupom '{self._codigo}' só é válido para compras acima de R$ {FormatarMoeda(self._valorMinimo)}."

        return None

    def CalcularDesconto(self, itens):
        base = 0
        for item in self._ItensElegiveis(itens):
            base += item["produto"].preco * item["quantidade"]

        return base * self._percentual / 100

    def Situacao(self, data):
        if self._validade is not None and data is not None and ConverterData(data) > ConverterData(self._validade):
            return "expirado"

        if self._usoMaximo is not None and self._usos >= self._usoMaximo:
            return "esgotado"

        return "válido"

    def RegistrarUso(self):
        self._usos += 1

    @property
    def codigo(self):
        return self._codigo

    @property
    def percentual(self):
        return self._percentual

    @property
    def valorMinimo(self):
        return self._valorMinimo

    @property
    def validade(self):
        return self._validade

    @property
    def usoMaximo(self):
        return self._usoMaximo

    @property
    def categorias(self):
        return list(self._categorias)

    @property
    def usos(self):
        return self._usos
