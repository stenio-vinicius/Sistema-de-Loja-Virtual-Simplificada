from Classes.validacoes import CpfValido, EmailValido, EnderecoValido, NormalizarCpf


class Cliente:
    """Armazena dados pessoais do cliente, permitindo cadastro e atualização do perfil do mesmo. E-mail e CPF são únicos e, junto com o endereço, precisam ser válidos para fechar um pedido."""

    def __init__(self):
        self._nome = None
        self._email = None
        self.__senha = None
        self._idade = None
        self._endereco = None
        self._cpf = None

    def CadastrarCliente(self, nome, email, senha, idade, endereco, cpf = None):
        self._nome = nome
        self._email = email
        self.__senha = senha
        self._idade = idade
        self._endereco = endereco
        self._cpf = NormalizarCpf(cpf) if cpf is not None else None

    def AtualizarPerfil(self, nome = None, email = None, senha = None, idade = None, endereco = None, cpf = None):
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
        if cpf is not None:
            self._cpf = NormalizarCpf(cpf)

    def VerificarSenha(self, senha):
        return self.__senha is not None and self.__senha == senha

    def Problemas(self):
        problemas = []

        if not EmailValido(self._email):
            problemas.append("E-mail inválido.")
        if not CpfValido(self._cpf):
            problemas.append("CPF inválido.")
        if not EnderecoValido(self._endereco):
            problemas.append("Endereço obrigatório (mínimo de 5 caracteres).")

        return problemas

    #Getters
    @property
    def nome(self):
        return self._nome

    @property
    def email(self):
        return self._email

    @property
    def senha(self):
        return self.__senha

    @property
    def idade(self):
        return self._idade

    @property
    def endereco(self):
        return self._endereco

    @property
    def cpf(self):
        return self._cpf
