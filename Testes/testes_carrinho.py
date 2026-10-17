import pytest

from Classes import carrinho

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
