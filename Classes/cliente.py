class Cliente:
    """Armazena dados pessoais do cliente, permitindo cadastro e atualização do perfil do mesmo."""

    def __init__(self):
        self._nome = None
        self._email = None
        self.__senha = None
        self._idade = None
        self._endereco = None

    def CadastrarCliente(self, nome, email, senha, idade, endereco):
        self._nome = nome
        self._email = email
        self.__senha = senha
        self._idade = idade
        self._endereco = endereco

    def AtualizarPerfil(self, nome=None, email=None, senha=None, idade=None, endereco=None):
        if nome is not None:
            self._nome = nome
        if email is not None:
            self._email = email
        if senha is not None:
            self.__senha = senha
        if idade is not None:
            self._idade = idade
        if endereco is not None:
            self._endereco = endereco

    #Getters
    @property
    def nome(self):
        return self._nome

    @property
    def email(self):
        return self._email

    @property
    def idade(self):
        return self._idade

    @property
    def endereco(self):
        return self._endereco
