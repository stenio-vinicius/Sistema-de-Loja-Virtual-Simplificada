from Classes.cupom import Cupom
from Classes.produto import Produto


def criar_itens(roupas=2, livros=1):
    camisa = Produto()
    camisa.CadastrarProduto("Camisa", "Roupas", 100.00, "Azul", "M", 10, "CAM-001")

    livro = Produto()
    livro.CadastrarProduto("Livro", "Livros", 50.00, None, None, 10, "LIV-001")

    itens = []
    if roupas:
        itens.append({"produto": camisa, "quantidade": roupas})
    if livros:
        itens.append({"produto": livro, "quantidade": livros})
    return itens


def criar_cupom(**opcoes):
    dados = {"codigo": "promo10", "percentual": 10, "valorMinimo": 150.00}
    dados.update(opcoes)

    cupom = Cupom()
    cupom.CadastrarCupom(**dados)
    return cupom


# ---------- Cadastro e validação ----------

def test_cadastro_normaliza_codigo_e_categorias():
    cupom = criar_cupom(codigo="  promo10 ", categorias=[" Roupas ", ""])

    assert cupom.codigo == "PROMO10"
    assert cupom.categorias == ["Roupas"]


def test_categorias_devolve_uma_copia():
    cupom = criar_cupom(categorias=["Roupas"])

    cupom.categorias.append("Livros")

    assert cupom.categorias == ["Roupas"]


def test_cupom_valido_nao_tem_problemas():
    assert criar_cupom(validade="31/12/2026", usoMaximo=5).Problemas() == []


def test_problemas_do_cupom():
    assert "O percentual deve ser maior que 0 e no máximo 100." in criar_cupom(percentual=0).Problemas()
    assert "O percentual deve ser maior que 0 e no máximo 100." in criar_cupom(percentual=101).Problemas()
    assert "O valor mínimo não pode ser negativo." in criar_cupom(valorMinimo=-1).Problemas()
    assert "Validade inválida. Use o formato DD/MM/AAAA." in criar_cupom(validade="amanhã").Problemas()
    assert "O uso máximo deve ser pelo menos 1." in criar_cupom(usoMaximo=0).Problemas()
    assert "O código do cupom é obrigatório." in criar_cupom(codigo="  ").Problemas()


# ---------- Regras de uso ----------

def test_cupom_valido_para_a_compra():
    assert criar_cupom().MotivoDeRecusa(criar_itens(), "05/10/2026") is None


def test_cupom_expirado():
    cupom = criar_cupom(validade="30/09/2026")

    assert "expirado em 30/09/2026" in cupom.MotivoDeRecusa(criar_itens(), "05/10/2026")


def test_cupom_vale_ate_o_ultimo_dia_da_validade():
    cupom = criar_cupom(validade="05/10/2026")

    assert cupom.MotivoDeRecusa(criar_itens(), "05/10/2026") is None


def test_cupom_esgotado():
    cupom = criar_cupom(usoMaximo=2, usos=2)

    assert "esgotado" in cupom.MotivoDeRecusa(criar_itens(), "05/10/2026")


def test_registrar_uso_leva_ao_limite():
    cupom = criar_cupom(usoMaximo=1)
    assert cupom.MotivoDeRecusa(criar_itens(), "05/10/2026") is None

    cupom.RegistrarUso()

    assert cupom.usos == 1
    assert "esgotado" in cupom.MotivoDeRecusa(criar_itens(), "05/10/2026")


def test_cupom_sem_item_elegivel():
    cupom = criar_cupom(categorias=["Eletrônicos"])

    assert "Nenhum item do carrinho é elegível" in cupom.MotivoDeRecusa(criar_itens(), "05/10/2026")


def test_cupom_abaixo_do_valor_minimo():
    cupom = criar_cupom(valorMinimo=500.00)

    assert "só é válido para compras acima de R$ 500,00" in cupom.MotivoDeRecusa(criar_itens(), "05/10/2026")


def test_sem_data_nao_confere_a_validade():
    cupom = criar_cupom(validade="01/01/2020")

    assert cupom.MotivoDeRecusa(criar_itens(), None) is None


# ---------- Desconto ----------

def test_desconto_sobre_todos_os_itens_quando_nao_ha_categorias():
    # 2 camisas (200) + 1 livro (50) = 250; 10% = 25
    assert criar_cupom().CalcularDesconto(criar_itens()) == 25.00


def test_desconto_so_sobre_os_itens_das_categorias_elegiveis():
    # só as camisas (200) entram na base; 10% = 20
    assert criar_cupom(categorias=["roupas"]).CalcularDesconto(criar_itens()) == 20.00


# ---------- Situação ----------

def test_situacao_do_cupom():
    assert criar_cupom().Situacao("05/10/2026") == "válido"
    assert criar_cupom(validade="01/10/2026").Situacao("05/10/2026") == "expirado"
    assert criar_cupom(usoMaximo=1, usos=1).Situacao("05/10/2026") == "esgotado"
