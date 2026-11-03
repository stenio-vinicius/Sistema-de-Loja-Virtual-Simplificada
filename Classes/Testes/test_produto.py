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


# ---------- SKU, estorno de estoque e produto digital ----------

from Classes.produto import ProdutoDigital


def test_produto_guarda_o_sku():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10, "CAM-001")

    assert produto.sku == "CAM-001"


def test_produto_sem_sku_informado():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)

    assert produto.sku is None


def test_estornar_estoque_devolve_as_unidades():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)
    produto.BaixarEstoque(4)

    produto.EstornarEstoque(4)

    assert produto.estoque == 10


def test_produto_fisico_nao_e_digital():
    produto = Produto()
    produto.CadastrarProduto("Camisa", "Roupas", 49.90, "Azul", "M", 10)

    assert produto.digital is False


def test_produto_digital_herda_de_produto_e_nao_tem_cor_nem_tamanho():
    ebook = ProdutoDigital()
    ebook.CadastrarProduto("E-book", "Livros", 50.00, "Azul", "M", 100, "EBK-001")

    assert issubclass(ProdutoDigital, Produto)
    assert ebook.digital is True
    assert ebook.cor is None
    assert ebook.tamanho is None
    assert ebook.sku == "EBK-001"


def test_produto_digital_tambem_controla_estoque():
    ebook = ProdutoDigital()
    ebook.CadastrarProduto("E-book", "Livros", 50.00, estoque=5, sku="EBK-001")

    assert ebook.BaixarEstoque(2) is True
    assert ebook.estoque == 3
