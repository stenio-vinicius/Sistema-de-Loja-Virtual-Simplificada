import pytest

from Classes.produto import Produto

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


def test_produto_baixar_estoque():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)

    assert produto.BaixarEstoque(3) is True
    assert produto.estoque == 7


def test_produto_baixa_exatamente_o_estoque():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)

    assert produto.BaixarEstoque(10) is True
    assert produto.estoque == 0


def test_produto_nao_baixa_alem_do_estoque(capsys):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)

    assert produto.BaixarEstoque(11) is False
    capturado = capsys.readouterr()

    assert produto.estoque == 10   # nada foi baixado
    assert "Estoque insuficiente" in capturado.out