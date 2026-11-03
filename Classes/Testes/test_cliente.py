import pytest

from Classes.cliente import Cliente

def test_cliente_cadastro():
    cliente = Cliente()
    cliente.CadastrarCliente("Stênio", "stenio@email.com", "123456", 17, "Juazeiro do Norte")
 
    assert cliente.nome == "Stênio"
    assert cliente.email == "stenio@email.com"
    assert cliente.idade == 17
    assert cliente.endereco == "Juazeiro do Norte"
 
 
def test_cliente_atualizar_perfil_parcial():
    cliente = Cliente()
    cliente.CadastrarCliente("Stênio", "stenio@email.com", "123456", 17, "Juazeiro do Norte")
 
    cliente.AtualizarPerfil(idade=22)
 
    assert cliente.idade == 22
    assert cliente.nome == "Stênio"


def criar_cliente(senha="123456"):
    cliente = Cliente()
    cliente.CadastrarCliente("Maria", "maria@email.com", senha, 20, "Crato")
    return cliente


def test_verificar_senha_correta_e_incorreta():
    cliente = criar_cliente("123456")

    assert cliente.VerificarSenha("123456") is True
    assert cliente.VerificarSenha("654321") is False


def test_verificar_senha_sem_cadastro_retorna_falso():
    assert Cliente().VerificarSenha("123456") is False


def test_atualizar_perfil_troca_a_senha():
    cliente = criar_cliente("123456")

    cliente.AtualizarPerfil(senha="nova123")

    assert cliente.VerificarSenha("nova123") is True
    assert cliente.VerificarSenha("123456") is False


# ---------- CPF e validação dos dados ----------

def criar_cliente_completo(**mudancas):
    dados = {"nome": "Maria", "email": "maria@email.com", "senha": "123456", "idade": 20,
             "endereco": "Rua das Flores, 10", "cpf": "529.982.247-25"}
    dados.update(mudancas)

    cliente = Cliente()
    cliente.CadastrarCliente(**dados)
    return cliente


def test_cpf_e_guardado_so_com_digitos():
    assert criar_cliente_completo().cpf == "52998224725"


def test_cliente_com_dados_validos_nao_tem_problemas():
    assert criar_cliente_completo().Problemas() == []


def test_cliente_com_dados_invalidos_lista_todos_os_problemas():
    cliente = criar_cliente_completo(email="maria-email", cpf="111.111.111-11", endereco="Rua")

    assert cliente.Problemas() == [
        "E-mail inválido.",
        "CPF inválido.",
        "Endereço obrigatório (mínimo de 5 caracteres).",
    ]


def test_cliente_sem_cpf_tem_problema():
    cliente = Cliente()
    cliente.CadastrarCliente("Maria", "maria@email.com", "123456", 20, "Rua das Flores, 10")

    assert cliente.cpf is None
    assert "CPF inválido." in cliente.Problemas()


def test_atualizar_perfil_troca_o_cpf():
    cliente = criar_cliente_completo(cpf="111.111.111-11")

    cliente.AtualizarPerfil(cpf="529.982.247-25")

    assert cliente.cpf == "52998224725"
    assert cliente.Problemas() == []
