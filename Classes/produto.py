class Produto:
    """Armazena as informações dos produtos, permitindo cadastro e modificações futuras, exibindo dados para o estoque. Cada produto é identificado por um SKU único."""

    def __init__(self):
        self._sku = None
        self._nome = None
        self._categoria = None
        self._preco = None
        self._cor = None
        self._tamanho = None
        self._estoque = None

    def CadastrarProduto(self, nome, categoria, preco, cor, tamanho, estoque, sku = None):
        self._sku = sku
        self._nome = nome
        self._categoria = categoria
        self._preco = preco
        self._cor = cor
        self._tamanho = tamanho
        self._estoque = estoque

    def ModificarProduto(self, nome = None, categoria = None, preco = None, cor = None, tamanho = None, estoque = None):
        if nome is not None:
            self._nome = nome
        if categoria is not None:
            self._categoria = categoria
        if preco is not None:
            self._preco = preco
        if cor is not None:
            self._cor = cor
        if tamanho is not None:
            self._tamanho = tamanho
        if estoque is not None:
            self._estoque = estoque

    def BaixarEstoque(self, quantidade):
        if quantidade > self._estoque:
            print(f"Estoque insuficiente de '{self._nome}'.")
            return False

        self._estoque -= quantidade
        return True

    def EstornarEstoque(self, quantidade):
        self._estoque += quantidade

    #Getters
    @property
    def sku(self):
        return self._sku

    @property
    def nome(self):
        return self._nome

    @property
    def categoria(self):
        return self._categoria

    @property
    def preco(self):
        return self._preco

    @property
    def cor(self):
        return self._cor

    @property
    def tamanho(self):
        return self._tamanho

    @property
    def estoque(self):
        return self._estoque

    @property
    def digital(self):
        return False


class ProdutoDigital(Produto):
    """Produto digital: não tem cor nem tamanho, não é enviado e, por isso, não soma frete ao pedido."""

    def CadastrarProduto(self, nome, categoria, preco, cor = None, tamanho = None, estoque = 0, sku = None):
        super().CadastrarProduto(nome, categoria, preco, None, None, estoque, sku)

    @property
    def digital(self):
        return True
