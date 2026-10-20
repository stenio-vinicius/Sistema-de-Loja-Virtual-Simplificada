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