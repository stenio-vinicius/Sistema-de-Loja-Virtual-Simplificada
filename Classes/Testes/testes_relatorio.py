import pytest

from Classes import relatorio

def test_relatorio_faturamento_total():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    relatorio = Relatorio()
    relatorio.RegistrarVenda(produto, 2, 100.00, "05/10/2026")
    relatorio.RegistrarVenda(produto, 1, 50.00, "20/10/2026")
 
    assert relatorio.FaturamentoTotal() == 150.00
 
 
def test_relatorio_faturamento_por_periodo():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    relatorio = Relatorio()
    relatorio.RegistrarVenda(produto, 2, 100.00, "05/10/2026")
    relatorio.RegistrarVenda(produto, 1, 50.00, "20/10/2026")
 
    total = relatorio.FaturamentoPorPeriodo("01/10/2026", "15/10/2026")
 
    assert total == 100.00
 
 
def test_relatorio_vendas_por_categoria():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    relatorio = Relatorio()
    relatorio.RegistrarVenda(produto, 2, 100.00, "05/10/2026")
 
    vendas = relatorio.VendasPorCategoria()
 
    assert vendas == {"Roupas": 100.00}
 
 
def test_relatorio_produto_mais_vendido():
    produto1 = Produto()
    produto1.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)
 
    produto2 = Produto()
    produto2.CadastrarProduto("Calça", "Roupas", 80.00, "Preta", "G", 5)
 
    relatorio = Relatorio()
    relatorio.RegistrarVenda(produto1, 5, 250.00, "05/10/2026")
    relatorio.RegistrarVenda(produto2, 2, 160.00, "06/10/2026")
 
    assert relatorio.ProdutoMaisVendido() == "Camisa"
 
 
def test_relatorio_sem_vendas_produto_mais_vendido_retorna_none():
    relatorio = Relatorio()
    assert relatorio.ProdutoMaisVendido() is None
