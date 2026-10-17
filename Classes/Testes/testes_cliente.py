import pytest

from Classes import cliente

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
