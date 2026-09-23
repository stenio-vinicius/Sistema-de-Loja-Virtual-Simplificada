# Sistema-de-Loja-Virtual-Simplificada

#### DESCRIÇÃO DO PROJETO:
- Desenvolvimento de um software simples para uma loja virtual com finalidade de obtenção de nota no trabalho da disciplina de PROGRAMAÇÃO ORIENTADA A OBJETOS do 2° semestre do curso de Engenharia de Software da Universidade Federal do Cariri (UFCA).

#### OBJETIVOS: 
- Criação de um software simples funcional para um sistema de administração de uma loja virtual, sendo exigido alguns requisitos, como:
  Cadastro de Produtos e Clientes;
  Carrinho;
  Pedidos;
  Pagamentos;
  Cálculo de Frete;
  Emissão de Nota/Sumário de Compra;
  Relatório de Vendas.
  Contendo tamném, de forma obrigatória, um método de salvamento de dados implementado no software, como um arquivo JSON ou SQLite.

#### ESTRUTURA PLANEJADA DE CLASSES:
- Classe: **Cliente**
  - Atributos:
    - Nome
    - E-mail
    - Senha
    - Idade
    - Endereço
 
  - Métodos:
    - CadatrarCliente()
    - AtualizarPefil()

- Classe: **Produto**
    - Atributos:
      - Nome
      - Categoria
      - Preço
      - Tamanho (Se necessário)
      - Cor
      - Disponibilidade no Estoque
 
  - Métodos:
    - CadastrarProduto()
    - ModificarProduto()
    - ComprarProduto()
 
- Classe: **Carrinho**
  - Atributos:
    - Itens
    - Quantidade de itens adicionados
    - Valor total dos itens adicionados no carrinho

  - Métodos:
    - AdicionarItem()
    - RetirarItem()
    - CalcularTotal()
 
- Classe: **Pedidos**
  - Atributos:
    - Quantidade
    - Status
    - Localização
    - Número de Protocolo

  - Métodos:
    - ConfirmarPedido()
    - CancelarPedido()

- Classe: **Pagamento**
  - Atributos:
    - Valor
    - Desconto
    - Status
    - Forma de Pagamento

  - Métodos:
    - PagarPedido()
    - AplicarCumpom()
    - ConfirmarEndereço()
 
- Classe: **Frete**
  - Atributos:
    - Valor
    - Distância
    - Prazo
 
  - Métodos:
    - CalcularFrete()
    - PrazoEstimado()
 
- Classe: **Nota Fiscal**
  - Atributos:
    - Nome da Empresa
    - Cadastro Nacional de Pessoa Jurídica (CNPJ)
    - Data e Horário da Confirmação do Pedido
    - Nome do Cliente
    - Itens do Pedido
    - Valor Por Item
    - Valor Total do Pedido
    - Descontos
    - Forma de Pagamento
    - Endereço do Cliente
    - Transportadora
    - Número de Protocolo
 
  - Métodos:
     - GerarNota()
