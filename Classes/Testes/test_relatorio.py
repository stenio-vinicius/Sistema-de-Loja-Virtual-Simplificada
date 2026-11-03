import pytest

from Classes.relatorio import Relatorio
from Classes.produto import Produto
from datetime import datetime

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


def test_gerar_relatorio_completo():
    camisa = Produto()
    camisa.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)

    caneca = Produto()
    caneca.CadastrarProduto("Caneca", "Casa", 20.00, "Branca", None, 30)

    relatorio = Relatorio()
    relatorio.RegistrarVenda(camisa, 4, 200.00, "05/10/2026")
    relatorio.RegistrarVenda(caneca, 2, 40.00, "20/10/2026")

    dados = relatorio.GerarRelatorio("01/10/2026", "15/10/2026")

    assert dados["quantidadeVendas"] == 2
    assert dados["faturamentoTotal"] == 240.00
    assert dados["faturamentoPeriodo"] == 200.00
    assert dados["vendasPorCategoria"] == {"Roupas": 200.00, "Casa": 40.00}
    assert dados["produtoMaisVendido"] == "Camisa"


def test_gerar_relatorio_sem_periodo_nao_calcula_faturamento_do_periodo():
    camisa = Produto()
    camisa.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10)

    relatorio = Relatorio()
    relatorio.RegistrarVenda(camisa, 1, 50.00, "05/10/2026")

    assert relatorio.GerarRelatorio()["faturamentoPeriodo"] is None


def test_gerar_relatorio_sem_vendas():
    dados = Relatorio().GerarRelatorio()

    assert dados["quantidadeVendas"] == 0
    assert dados["faturamentoTotal"] == 0
    assert dados["vendasPorCategoria"] == {}
    assert dados["produtoMaisVendido"] is None


def test_produto_mais_vendido_agrupa_pelo_sku_e_nao_pelo_nome():
    camisaM = Produto()
    camisaM.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "M", 10, "CAM-M")

    camisaG = Produto()
    camisaG.CadastrarProduto("Camisa", "Roupas", 50.00, "Azul", "G", 10, "CAM-G")

    caneca = Produto()
    caneca.CadastrarProduto("Caneca", "Casa", 20.00, "Branca", None, 30, "CAN-001")

    relatorio = Relatorio()
    relatorio.RegistrarVenda(camisaM, 4, 200.00, "05/10/2026")
    relatorio.RegistrarVenda(camisaG, 3, 150.00, "05/10/2026")
    relatorio.RegistrarVenda(caneca, 6, 120.00, "05/10/2026")

    # por nome, "Camisa" somaria 7 e ganharia; por SKU, a caneca (6) vence cada camisa (4 e 3)
    assert relatorio.ProdutoMaisVendido() == "Caneca"
