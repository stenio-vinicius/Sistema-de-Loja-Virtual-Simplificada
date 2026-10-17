import pytest

from Classes.carrinho import Carrinho
from Classes.produto import Produto

def test_carrinho_adicionar_item_calcula_total():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 2)
 
    assert carrinho.CalcularTotal() == 100.00
 
 
def test_carrinho_adicionar_item_duplicado_soma_quantidade():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 2)
    carrinho.AdicionarItem(produto, 3)
 
    assert len(carrinho.itens) == 1
    assert carrinho.itens[0]["quantidade"] == 5
 
 
def test_carrinho_retirar_item_parcial():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 5)
    carrinho.RetirarItem(produto, 2)
 
    assert carrinho.itens[0]["quantidade"] == 3
 
 
def test_carrinho_retirar_mais_que_tem_remove_item():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 2)
    carrinho.RetirarItem(produto, 10)
 
    assert carrinho.itens == []

def test_carrinho_adiciona_so_o_que_cabe_no_estoque(capsys):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)

    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 11)
    capturado = capsys.readouterr()

    assert carrinho.itens[0]["quantidade"] == 10
    assert "apenas 10" in capturado.out


def test_carrinho_considera_o_que_ja_esta_no_carrinho(capsys):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)

    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 8)
    carrinho.AdicionarItem(produto, 3)
    capturado = capsys.readouterr()

    assert carrinho.itens[0]["quantidade"] == 10
    assert "apenas 2" in capturado.out


def test_carrinho_nao_adiciona_quando_nao_ha_mais_unidades(capsys):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)

    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 10)
    carrinho.AdicionarItem(produto, 1)
    capturado = capsys.readouterr()

    assert carrinho.itens[0]["quantidade"] == 10
    assert "Não há mais unidades" in capturado.out


def test_carrinho_aceita_exatamente_o_estoque_disponivel(capsys):
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)

    carrinho = Carrinho()
    carrinho.AdicionarItem(produto, 10)
    capturado = capsys.readouterr()

    assert carrinho.itens[0]["quantidade"] == 10
    assert capturado.out == ""