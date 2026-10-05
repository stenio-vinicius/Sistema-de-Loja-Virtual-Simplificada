class Produto:
    "Armazena as informações dos produtos, permitindo cadastro e modificações futuras, exibindo dados para o estoque."

    def __init__(self):
      self._nome = None
      self._categoria = None
      self._preco = None
      self._cor = None
      self._tamanho = None
      self._estoque = None

    def CadastrarProduto(self, nome, categoria, preco, cor, tamanho, estoque):
        self._nome = nome
        self._categoria = categoria
        self._preco = preco
        self._cor = cor
        self._tamanho = tamanho
        self._estoque = estoque

    def ModificarProduto(self, nome = None, categoria = None, preco = None, cor = None, tamanho = None, estoque = None):
        if nome is not None:
          self._nome = nome
        if nome is not None:
          self._categoria = categoria
        if nome is not None:
          self._preco = preco
        if nome is not None:
          self._cor = cor
        if nome is not None:
          self._tamanho = tamanho
        if nome is not None:
          self._estoque = estoque

    #Getters

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
