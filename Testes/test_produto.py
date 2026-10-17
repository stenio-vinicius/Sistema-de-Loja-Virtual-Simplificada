import pytest

from Classes import produto

def test_produto_cadastro():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)
 
    assert produto.nome == "Camisa"
    assert produto.preco == 49.90
    assert produto.estoque == 10
 
 
def test_produto_modificar_parcial():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)
 
    produto.ModificarProduto(preco=39.90)
 
    assert produto.preco == 39.90
    assert produto.nome == "Camisa"
