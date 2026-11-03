import json
import re

from main import main

EMAIL = "stenio@email.com"
EMAIL_MARIA = "maria@email.com"
SENHA = "123456"
CPF = "529.982.247-25"
CPF_MARIA = "111.444.777-35"
LOGIN = ["--email", EMAIL, "--senha", SENHA]
LOGIN_MARIA = ["--email", EMAIL_MARIA, "--senha", SENHA]


def executar(capsys, caminho, *argumentos):
    """Roda um comando da CLI e devolve só o que ele imprimiu."""
    capsys.readouterr()
    main(list(argumentos), caminho)
    return capsys.readouterr().out


def cadastrar_cliente(capsys, caminho, email=EMAIL, cpf=CPF, nome="Stênio"):
    return executar(capsys, caminho, "cadastrar-cliente", "--nome", nome, "--email", email, "--senha", SENHA,
                    "--idade", "20", "--endereco", "Rua das Flores, 10", "--cpf", cpf)


def cadastrar_produtos(capsys, caminho, estoque=10):
    executar(capsys, caminho, "cadastrar-produto", "--sku", "CAM-001", "--nome", "Camisa", "--categoria", "Roupas",
             "--preco", "100", "--cor", "Azul", "--tamanho", "M", "--estoque", str(estoque))
    executar(capsys, caminho, "cadastrar-produto", "--sku", "EBK-001", "--nome", "E-book Python", "--categoria", "Livros",
             "--preco", "50", "--estoque", "100", "--digital")


def preparar_loja(capsys, caminho, estoque=10, com_maria=False):
    cadastrar_cliente(capsys, caminho)
    if com_maria:
        cadastrar_cliente(capsys, caminho, EMAIL_MARIA, CPF_MARIA, "Maria")
    cadastrar_produtos(capsys, caminho, estoque)


def cadastrar_cupom(capsys, caminho, *extras, codigo="promo10", percentual="10", minimo="150"):
    return executar(capsys, caminho, "cadastrar-cupom", "--codigo", codigo, "--percentual", percentual,
                    "--valor-minimo", minimo, *extras)


def adicionar(capsys, caminho, quantidade, sku="CAM-001", login=LOGIN):
    return executar(capsys, caminho, "adicionar-carrinho", *login, "--sku", sku, "--quantidade", str(quantidade))


def criar_pedido(capsys, caminho, *extras, distancia="200", data="05/10/2026", login=LOGIN):
    argumentos = ["criar-pedido", *login, "--data", data]
    if distancia is not None:
        argumentos += ["--distancia", distancia]

    return executar(capsys, caminho, *argumentos, *extras)


def pagar(capsys, caminho, protocolo, *extras, forma="PIX", data="06/10/2026", login=LOGIN):
    return executar(capsys, caminho, "pagar-pedido", *login, "--protocolo", protocolo, "--forma", forma,
                    "--data", data, *extras)


def protocolo_de(saida):
    return re.search(r"PED\d{8}", saida).group(0)


def pedido_criado(capsys, caminho, quantidade=2, *extras, login=LOGIN, **opcoes):
    adicionar(capsys, caminho, quantidade, login=login)
    return protocolo_de(criar_pedido(capsys, caminho, *extras, login=login, **opcoes))


def pedido_pago(capsys, caminho, quantidade=2, login=LOGIN, **opcoes):
    protocolo = pedido_criado(capsys, caminho, quantidade, login=login, **opcoes)
    pagar(capsys, caminho, protocolo, login=login)
    return protocolo


def estoque_da_camisa(capsys, caminho):
    return re.search(r"CAM-001.*Estoque: (\d+)", executar(capsys, caminho, "listar-produtos")).group(1)


# =========================================================
# Clientes
# =========================================================

def test_cadastrar_cliente(tmp_path, capsys):
    saida = cadastrar_cliente(capsys, str(tmp_path / "dados.json"))

    assert "Cliente 'Stênio' cadastrado com sucesso!" in saida


def test_cadastrar_cliente_com_dados_invalidos(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")

    saida = executar(capsys, caminho, "cadastrar-cliente", "--nome", "X", "--email", "sem-arroba", "--senha", "1",
                     "--idade", "20", "--endereco", "Rua", "--cpf", "111.111.111-11")

    assert "E-mail inválido." in saida
    assert "CPF inválido." in saida
    assert "Endereço obrigatório" in saida
    assert "Cliente não cadastrado." in saida
    assert "cadastrado com sucesso" in cadastrar_cliente(capsys, caminho)   # nada foi gravado antes


def test_cadastrar_cliente_com_email_repetido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cliente(capsys, caminho)

    saida = cadastrar_cliente(capsys, caminho, "STENIO@email.com", CPF_MARIA)

    assert "Já existe um cliente com o e-mail" in saida


def test_cadastrar_cliente_com_cpf_repetido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cliente(capsys, caminho)

    saida = cadastrar_cliente(capsys, caminho, EMAIL_MARIA, "52998224725")   # o mesmo CPF, sem pontuação

    assert "Já existe um cliente com esse CPF." in saida


def test_atualizar_cliente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cliente(capsys, caminho)

    saida = executar(capsys, caminho, "atualizar-cliente", *LOGIN, "--endereco", "Avenida Central, 500")

    assert "Cadastro atualizado com sucesso!" in saida


def test_atualizar_cliente_com_nova_senha(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cliente(capsys, caminho)

    executar(capsys, caminho, "atualizar-cliente", *LOGIN, "--nova-senha", "nova123")

    assert "E-mail ou senha incorretos." in executar(capsys, caminho, "ver-carrinho", *LOGIN)
    assert "carrinho está vazio" in executar(capsys, caminho, "ver-carrinho", "--email", EMAIL, "--senha", "nova123")


def test_atualizar_cliente_nao_aceita_cpf_de_outro(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cliente(capsys, caminho)
    cadastrar_cliente(capsys, caminho, EMAIL_MARIA, CPF_MARIA, "Maria")

    saida = executar(capsys, caminho, "atualizar-cliente", *LOGIN_MARIA, "--cpf", CPF)

    assert "Já existe outro cliente com esse CPF." in saida


def test_atualizar_cliente_com_senha_incorreta(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cliente(capsys, caminho)

    saida = executar(capsys, caminho, "atualizar-cliente", "--email", EMAIL, "--senha", "errada", "--nome", "Outro")

    assert "E-mail ou senha incorretos." in saida


# =========================================================
# Produtos
# =========================================================

def test_cadastrar_e_listar_produtos(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")

    cadastro = executar(capsys, caminho, "cadastrar-produto", "--sku", "CAM-001", "--nome", "Camisa",
                        "--categoria", "Roupas", "--preco", "49.90", "--cor", "Azul", "--tamanho", "M", "--estoque", "10")
    cadastrar_produtos_digital = executar(capsys, caminho, "cadastrar-produto", "--sku", "EBK-001", "--nome", "E-book",
                                          "--categoria", "Livros", "--preco", "30", "--estoque", "5", "--digital")
    listagem = executar(capsys, caminho, "listar-produtos")

    assert "Produto 'Camisa' (SKU CAM-001) cadastrado com sucesso!" in cadastro
    assert "cadastrado com sucesso" in cadastrar_produtos_digital
    assert "[CAM-001] Camisa | Roupas | R$ 49,90 | Físico | Cor: Azul | Tamanho: M | Estoque: 10" in listagem
    assert "[EBK-001] E-book | Livros | R$ 30,00 | Digital | Cor: - | Tamanho: - | Estoque: 5" in listagem


def test_sku_duplicado_e_recusado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_produtos(capsys, caminho)

    saida = executar(capsys, caminho, "cadastrar-produto", "--sku", "cam-001", "--nome", "Outra", "--categoria", "Roupas",
                     "--preco", "10", "--cor", "Azul", "--estoque", "1")

    assert "Já existe um produto com o SKU 'cam-001'." in saida


def test_mesmo_nome_com_sku_diferente_e_permitido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_produtos(capsys, caminho)

    saida = executar(capsys, caminho, "cadastrar-produto", "--sku", "CAM-002", "--nome", "Camisa", "--categoria", "Roupas",
                     "--preco", "100", "--cor", "Azul", "--tamanho", "G", "--estoque", "5")

    assert "cadastrado com sucesso" in saida


def test_produto_fisico_precisa_de_cor(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "cadastrar-produto", "--sku", "CAM-001", "--nome", "Camisa",
                     "--categoria", "Roupas", "--preco", "100", "--estoque", "5")

    assert "Produtos físicos precisam de cor" in saida
    assert "Produto não cadastrado." in saida


def test_produto_com_preco_ou_estoque_invalidos(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "cadastrar-produto", "--sku", " ", "--nome", "Camisa",
                     "--categoria", "Roupas", "--preco", "0", "--cor", "Azul", "--estoque", "-1")

    assert "O SKU é obrigatório." in saida
    assert "O preço deve ser maior que zero." in saida
    assert "O estoque não pode ser negativo." in saida


def test_listar_produtos_sem_nenhum_cadastrado(tmp_path, capsys):
    assert "Nenhum produto cadastrado." in executar(capsys, str(tmp_path / "dados.json"), "listar-produtos")


# =========================================================
# Cupons
# =========================================================

def test_cadastrar_e_listar_cupom_com_todas_as_regras(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")

    cadastro = cadastrar_cupom(capsys, caminho, "--validade", "31/12/2099", "--uso-maximo", "5", "--categorias", "Roupas, Livros")
    listagem = executar(capsys, caminho, "listar-cupons")

    assert "Cupom 'PROMO10' cadastrado: 10% de desconto para compras acima de R$ 150,00." in cadastro
    assert "PROMO10: 10% | mínimo R$ 150,00 | validade: 31/12/2099 | usos: 0/5 | categorias: Roupas, Livros | válido" in listagem


def test_listar_cupons_filtra_pelo_valor_da_compra(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cupom(capsys, caminho)

    abaixo = executar(capsys, caminho, "listar-cupons", "--valor", "100")
    acima = executar(capsys, caminho, "listar-cupons", "--valor", "200")

    assert "Nenhum cupom disponível para o valor informado." in abaixo
    assert "PROMO10" in acima


def test_listar_cupons_mostra_a_situacao(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cupom(capsys, caminho, "--validade", "01/01/2020")

    assert "expirado" in executar(capsys, caminho, "listar-cupons")


def test_cadastrar_cupom_repetido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    cadastrar_cupom(capsys, caminho)

    assert "Já existe um cupom com o código 'PROMO10'." in cadastrar_cupom(capsys, caminho, codigo="Promo10")


def test_cadastrar_cupom_com_percentual_invalido(tmp_path, capsys):
    saida = cadastrar_cupom(capsys, str(tmp_path / "dados.json"), percentual="150")

    assert "O percentual deve ser maior que 0 e no máximo 100." in saida
    assert "Cupom não cadastrado." in saida


def test_cadastrar_cupom_com_validade_invalida(tmp_path, capsys):
    saida = cadastrar_cupom(capsys, str(tmp_path / "dados.json"), "--validade", "amanhã")

    assert "Validade inválida" in saida


def test_listar_cupons_sem_nenhum_cadastrado(tmp_path, capsys):
    assert "Nenhum cupom cadastrado." in executar(capsys, str(tmp_path / "dados.json"), "listar-cupons")


# =========================================================
# Carrinho
# =========================================================

def test_carrinho_persiste_entre_execucoes_e_soma_o_mesmo_produto(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    adicionar(capsys, caminho, 2)
    adicionar(capsys, caminho, 1)
    saida = executar(capsys, caminho, "ver-carrinho", *LOGIN)

    assert "[CAM-001] Camisa | 3x R$ 100,00 = R$ 300,00" in saida
    assert "Total: R$ 300,00" in saida


def test_adicionar_acima_do_estoque_adiciona_so_o_que_cabe(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, estoque=3)

    saida = adicionar(capsys, caminho, 5)

    assert "Foram adicionadas apenas 3" in saida
    assert "3x R$ 100,00" in saida


def test_remover_do_carrinho_aos_poucos(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 5)

    parcial = executar(capsys, caminho, "remover-carrinho", *LOGIN, "--sku", "CAM-001", "--quantidade", "2")
    total = executar(capsys, caminho, "remover-carrinho", *LOGIN, "--sku", "CAM-001", "--quantidade", "10")

    assert "3x R$ 100,00" in parcial
    assert "Seu carrinho está vazio." in total


def test_remover_sku_que_nao_esta_no_carrinho(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "não está no seu carrinho" in executar(capsys, caminho, "remover-carrinho", *LOGIN, "--sku", "CAM-001")


def test_senha_incorreta_nao_acessa_o_carrinho(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "E-mail ou senha incorretos." in executar(capsys, caminho, "ver-carrinho", "--email", EMAIL, "--senha", "errada")


def test_email_inexistente_nao_acessa_o_carrinho(tmp_path, capsys):
    assert "E-mail ou senha incorretos." in executar(capsys, str(tmp_path / "dados.json"), "ver-carrinho", "--email", "x@x.com", "--senha", "1")


def test_adicionar_sku_inexistente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "Produto com SKU 'XXX' não encontrado." in adicionar(capsys, caminho, 1, sku="XXX")


def test_adicionar_quantidade_invalida(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "A quantidade deve ser pelo menos 1." in adicionar(capsys, caminho, 0)


# =========================================================
# Criar pedido (CRIADO)
# =========================================================

def test_criar_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = criar_pedido(capsys, caminho)

    assert re.search(r"Pedido PED\d{8} criado \(status CRIADO\)\.", saida)
    assert "Subtotal: R$ 200,00" in saida
    assert "Frete: R$ 20,00 (prazo estimado: 5 dias)" in saida
    assert "Total previsto: R$ 220,00" in saida
    assert estoque_da_camisa(capsys, caminho) == "10"   # criar o pedido não baixa o estoque
    assert "Seu carrinho está vazio." in executar(capsys, caminho, "ver-carrinho", *LOGIN)
    assert "CRIADO" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_criar_pedido_com_carrinho_vazio(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "Seu carrinho está vazio." in criar_pedido(capsys, caminho)


def test_produto_fisico_exige_a_distancia_para_criar_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 1)

    saida = criar_pedido(capsys, caminho, distancia=None)

    assert "Informe a distância" in saida
    assert "Pedido não criado." in saida


def test_distancia_acima_do_limite_nao_cria_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 1)

    saida = criar_pedido(capsys, caminho, distancia="5000")

    assert "Não foi possível calcular o frete" in saida
    assert "Pedido não criado." in saida


def test_pedido_so_com_produto_digital_nao_soma_frete(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 1, sku="EBK-001")

    saida = criar_pedido(capsys, caminho, distancia=None)
    protocolo = protocolo_de(saida)
    pagamento = pagar(capsys, caminho, protocolo)

    assert "Frete: R$ 0,00 (produtos digitais não somam frete)" in saida
    assert "Total previsto: R$ 50,00" in saida
    assert "Valor total a pagar: R$ 47,50" in pagamento   # R$ 50,00 com 5% do Pix


def test_data_invalida_ao_criar_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 1)

    assert "Data inválida" in criar_pedido(capsys, caminho, data="32/13/2026")


def test_cadastro_incompleto_impede_fechar_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 1)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    del dados["clientes"][0]["cpf"]   # cadastro antigo, de antes da validação do CPF
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo)

    saida = criar_pedido(capsys, caminho)

    assert "Cadastro incompleto ou inválido" in saida
    assert "CPF inválido." in saida
    assert "cadastrado" not in saida


def test_nao_cria_pedido_com_quantidade_acima_do_estoque(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    adicionar(capsys, caminho, 8)                               # Stênio separa 8 no carrinho
    pedido_pago(capsys, caminho, 5, login=LOGIN_MARIA)          # Maria compra 5, sobram 5

    saida = criar_pedido(capsys, caminho)

    assert "Estoque insuficiente de 'Camisa': o carrinho tem 8, mas há 5 em estoque." in saida
    assert "criado" not in saida


# =========================================================
# Cupons no pedido
# =========================================================

def test_criar_pedido_com_cupom(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    cadastrar_cupom(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = criar_pedido(capsys, caminho, "--cupom", "promo10")

    assert "Cupom 'PROMO10' aplicado! Desconto de R$ 20,00." in saida
    assert "Desconto do cupom PROMO10: - R$ 20,00" in saida
    assert "Total previsto: R$ 200,00" in saida


def test_cupom_inexistente_nao_cria_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    adicionar(capsys, caminho, 2)

    saida = criar_pedido(capsys, caminho, "--cupom", "NAOEXISTE")

    assert "Cupom 'NAOEXISTE' não encontrado." in saida
    assert "Pedido não criado." in saida


def test_cupom_expirado_nao_cria_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    cadastrar_cupom(capsys, caminho, "--validade", "01/10/2026")
    adicionar(capsys, caminho, 2)

    saida = criar_pedido(capsys, caminho, "--cupom", "promo10")

    assert "expirado em 01/10/2026" in saida
    assert "Pedido não criado." in saida


def test_cupom_abaixo_do_valor_minimo_nao_cria_o_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    cadastrar_cupom(capsys, caminho)
    adicionar(capsys, caminho, 1)   # compra de R$ 100,00

    saida = criar_pedido(capsys, caminho, "--cupom", "promo10")

    assert "só é válido para compras acima de R$ 150,00" in saida
    assert "Pedido não criado." in saida


def test_cupom_de_outra_categoria_nao_vale_para_o_carrinho(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    cadastrar_cupom(capsys, caminho, "--categorias", "Livros")
    adicionar(capsys, caminho, 2)   # só camisas (Roupas)

    saida = criar_pedido(capsys, caminho, "--cupom", "promo10")

    assert "Nenhum item do carrinho é elegível" in saida


def test_cupom_com_categoria_desconta_so_os_itens_elegiveis(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    cadastrar_cupom(capsys, caminho, "--categorias", "Roupas")
    adicionar(capsys, caminho, 2)
    adicionar(capsys, caminho, 1, sku="EBK-001")

    saida = criar_pedido(capsys, caminho, "--cupom", "promo10")

    assert "Desconto de R$ 20,00" in saida   # 10% de R$ 200,00 das camisas; o e-book fica de fora


def test_cupom_com_uso_maximo(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    cadastrar_cupom(capsys, caminho, "--uso-maximo", "1")
    protocolo_stenio = pedido_criado(capsys, caminho, 2, "--cupom", "promo10")
    protocolo_maria = pedido_criado(capsys, caminho, 2, "--cupom", "promo10", login=LOGIN_MARIA)   # ainda sobrava um uso

    primeiro = pagar(capsys, caminho, protocolo_stenio)
    segundo = pagar(capsys, caminho, protocolo_maria, login=LOGIN_MARIA)

    assert "Pagamento confirmado!" in primeiro
    assert "esgotado" in segundo
    assert "usos: 1/1" in executar(capsys, caminho, "listar-cupons")
    assert "esgotado" in executar(capsys, caminho, "listar-cupons")


def test_cupom_esgotado_nao_cria_novos_pedidos(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    cadastrar_cupom(capsys, caminho, "--uso-maximo", "1")
    protocolo = pedido_criado(capsys, caminho, 2, "--cupom", "promo10")
    pagar(capsys, caminho, protocolo)
    adicionar(capsys, caminho, 2, login=LOGIN_MARIA)

    saida = criar_pedido(capsys, caminho, "--cupom", "promo10", login=LOGIN_MARIA)

    assert "esgotado" in saida
    assert "Pedido não criado." in saida


# =========================================================
# Pagar pedido (PAGO)
# =========================================================

def test_pagar_pedido_baixa_o_estoque(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho)

    saida = pagar(capsys, caminho, protocolo)

    # (200 + 20 de frete) com 5% de desconto do Pix = 209
    assert "Valor total a pagar: R$ 209,00" in saida
    assert "Pagamento confirmado!" in saida
    assert estoque_da_camisa(capsys, caminho) == "8"
    assert "PAGO" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_pagar_no_credito_parcelado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho)

    saida = pagar(capsys, caminho, protocolo, "--parcelas", "4", forma="cartao_credito")

    assert "Valor total a pagar: R$ 226,60" in saida
    assert "Parcelamento: 4x de R$ 56,65" in saida


def test_pagar_com_forma_invalida_nao_baixa_o_estoque(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho)

    saida = pagar(capsys, caminho, protocolo, forma="DINHEIRO")

    assert "Forma de pagamento inválida: DINHEIRO" in saida
    assert estoque_da_camisa(capsys, caminho) == "10"
    assert "CRIADO" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_pagar_pedido_de_outro_cliente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    protocolo = pedido_criado(capsys, caminho)

    saida = pagar(capsys, caminho, protocolo, login=LOGIN_MARIA)

    assert f"Pedido '{protocolo}' não encontrado." in saida
    assert estoque_da_camisa(capsys, caminho) == "10"


def test_pagar_protocolo_inexistente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "não encontrado" in pagar(capsys, caminho, "PED00000000")


def test_nao_paga_duas_vezes(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)

    saida = pagar(capsys, caminho, protocolo)

    assert "Não é possível pagar um pedido com status 'PAGO'" in saida
    assert estoque_da_camisa(capsys, caminho) == "8"


def test_nao_paga_se_o_estoque_acabou_depois_da_criacao(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    protocolo_stenio = pedido_criado(capsys, caminho, 8)
    protocolo_maria = pedido_criado(capsys, caminho, 8, login=LOGIN_MARIA)   # os dois couberam no estoque de 10

    pagar(capsys, caminho, protocolo_stenio)                                 # sobram 2
    saida = pagar(capsys, caminho, protocolo_maria, login=LOGIN_MARIA)

    assert "Estoque insuficiente de 'Camisa'" in saida
    assert estoque_da_camisa(capsys, caminho) == "2"


def test_data_invalida_ao_pagar(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho)

    assert "Data inválida" in pagar(capsys, caminho, protocolo, data="ontem")


# =========================================================
# Enviar e entregar
# =========================================================

def test_fluxo_completo_da_criacao_a_entrega(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    cadastrar_cupom(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho, 2, "--cupom", "promo10")

    pagamento = pagar(capsys, caminho, protocolo)
    # 200 - 10% = 180, + 20 de frete = 200, com 5% de desconto do Pix = 190
    assert "Valor total a pagar: R$ 190,00" in pagamento

    envio = executar(capsys, caminho, "enviar-pedido", "--protocolo", protocolo)
    rastreio = re.search(r"[A-Z]{2}\d{9}BR", envio).group(0)
    assert "Pedido enviado!" in envio

    entrega = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "12/10/2026")
    assert "marcado como entregue em 12/10/2026" in entrega

    pedidos = executar(capsys, caminho, "listar-pedidos", *LOGIN)
    assert f"{protocolo} | 05/10/2026 | ENTREGUE | R$ 190,00 | 2 item(ns) | Rastreio: {rastreio} | Entrega: 12/10/2026" in pedidos
    assert "usos: 1 (sem limite)" in executar(capsys, caminho, "listar-cupons")


def test_nao_envia_pedido_que_nao_foi_pago(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho)

    saida = executar(capsys, caminho, "enviar-pedido", "--protocolo", protocolo)

    assert "Só é possível enviar um pedido pago" in saida
    assert "Rastreio: -" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_enviar_pedido_inexistente(tmp_path, capsys):
    assert "não encontrado" in executar(capsys, str(tmp_path / "dados.json"), "enviar-pedido", "--protocolo", "PED00000000")


def test_nao_entrega_pedido_que_nao_foi_enviado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)

    saida = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "12/10/2026")

    assert "Não é possível marcar como entregue um pedido com status 'PAGO'" in saida


def test_entregar_pedido_inexistente(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "entregar-pedido", "--protocolo", "PED00000000", "--data", "12/10/2026")

    assert "não encontrado" in saida


def test_entregar_com_data_invalida(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)
    executar(capsys, caminho, "enviar-pedido", "--protocolo", protocolo)

    assert "Data inválida" in executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "ontem")


def test_entregar_com_data_anterior_ao_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)
    executar(capsys, caminho, "enviar-pedido", "--protocolo", protocolo)

    saida = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "01/10/2026")

    assert "não pode ser anterior à data do pedido (05/10/2026)" in saida


def test_entregar_o_mesmo_pedido_duas_vezes(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)
    executar(capsys, caminho, "enviar-pedido", "--protocolo", protocolo)
    executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "10/10/2026")

    saida = executar(capsys, caminho, "entregar-pedido", "--protocolo", protocolo, "--data", "11/10/2026")

    assert "status 'ENTREGUE'" in saida
    assert "Entrega: 10/10/2026" in executar(capsys, caminho, "listar-pedidos", *LOGIN)   # a data original foi mantida


# =========================================================
# Cancelar pedido
# =========================================================

def test_cancelar_pedido_criado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_criado(capsys, caminho)

    saida = executar(capsys, caminho, "cancelar-pedido", *LOGIN, "--protocolo", protocolo, "--data", "05/10/2026")

    assert "Pedido cancelado." in saida
    assert "Estoque estornado." not in saida
    assert estoque_da_camisa(capsys, caminho) == "10"
    assert "CANCELADO" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_cancelar_pedido_pago_estorna_o_estoque_e_tira_a_venda_do_relatorio(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)
    assert estoque_da_camisa(capsys, caminho) == "8"
    assert "Faturamento total: R$ 200,00" in executar(capsys, caminho, "relatorio")

    saida = executar(capsys, caminho, "cancelar-pedido", *LOGIN, "--protocolo", protocolo, "--data", "08/10/2026")

    assert "Estoque estornado." in saida
    assert "Pedido cancelado." in saida
    assert estoque_da_camisa(capsys, caminho) == "10"
    assert "Nenhuma venda registrada." in executar(capsys, caminho, "relatorio")


def test_cancelamento_fora_da_janela(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)   # pago em 06/10/2026

    saida = executar(capsys, caminho, "cancelar-pedido", *LOGIN, "--protocolo", protocolo, "--data", "14/10/2026")

    assert "prazo de cancelamento (7 dias" in saida
    assert estoque_da_camisa(capsys, caminho) == "8"
    assert "PAGO" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_nao_cancela_pedido_enviado(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo = pedido_pago(capsys, caminho)
    executar(capsys, caminho, "enviar-pedido", "--protocolo", protocolo)

    saida = executar(capsys, caminho, "cancelar-pedido", *LOGIN, "--protocolo", protocolo, "--data", "08/10/2026")

    assert "Não é possível cancelar um pedido com status 'ENVIADO'" in saida
    assert estoque_da_camisa(capsys, caminho) == "8"


def test_cancelar_pedido_de_outro_cliente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    protocolo = pedido_criado(capsys, caminho)

    saida = executar(capsys, caminho, "cancelar-pedido", *LOGIN_MARIA, "--protocolo", protocolo)

    assert "não encontrado" in saida
    assert "CRIADO" in executar(capsys, caminho, "listar-pedidos", *LOGIN)


# =========================================================
# Listar pedidos
# =========================================================

def test_listar_pedidos_sem_nenhum_pedido(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)

    assert "Você ainda não fez nenhum pedido." in executar(capsys, caminho, "listar-pedidos", *LOGIN)


def test_listar_pedidos_mostra_so_os_do_cliente(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho, com_maria=True)
    protocolo = pedido_criado(capsys, caminho)

    assert protocolo in executar(capsys, caminho, "listar-pedidos", *LOGIN)
    assert "ainda não fez nenhum pedido" in executar(capsys, caminho, "listar-pedidos", *LOGIN_MARIA)


# =========================================================
# Relatório
# =========================================================

def test_relatorio_completo_e_por_periodo(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    protocolo1 = pedido_criado(capsys, caminho, 2, data="05/10/2026")
    pagar(capsys, caminho, protocolo1, data="05/10/2026")
    protocolo2 = pedido_criado(capsys, caminho, 1, data="20/10/2026")
    pagar(capsys, caminho, protocolo2, data="20/10/2026")

    completo = executar(capsys, caminho, "relatorio")
    periodo = executar(capsys, caminho, "relatorio", "--inicio", "01/10/2026", "--fim", "15/10/2026")

    assert "Vendas registradas: 2" in completo
    assert "Faturamento total: R$ 300,00" in completo
    assert "Roupas: R$ 300,00" in completo
    assert "Produto mais vendido: Camisa" in completo
    assert "Faturamento de 01/10/2026 a 15/10/2026: R$ 200,00" in periodo


def test_pedido_ainda_nao_pago_nao_entra_no_relatorio(tmp_path, capsys):
    caminho = str(tmp_path / "dados.json")
    preparar_loja(capsys, caminho)
    pedido_criado(capsys, caminho)

    assert "Nenhuma venda registrada." in executar(capsys, caminho, "relatorio")


def test_relatorio_sem_vendas(tmp_path, capsys):
    assert "Nenhuma venda registrada." in executar(capsys, str(tmp_path / "dados.json"), "relatorio")


def test_relatorio_com_periodo_incompleto(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio", "--inicio", "01/10/2026")

    assert "Informe --inicio e --fim juntos." in saida


def test_relatorio_com_data_invalida(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio", "--inicio", "32/13/2026", "--fim", "01/10/2026")

    assert "Data inválida" in saida


def test_relatorio_com_periodo_invertido(tmp_path, capsys):
    saida = executar(capsys, str(tmp_path / "dados.json"), "relatorio", "--inicio", "15/10/2026", "--fim", "01/10/2026")

    assert "A data inicial não pode ser depois da data final." in saida
