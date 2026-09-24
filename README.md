# Sistema-de-Loja-Virtual-Simplificada

## DESCRIÇÃO DO PROJETO:
- Desenvolvimento de um software simples para uma loja virtual com finalidade de obtenção de nota no trabalho da disciplina de PROGRAMAÇÃO ORIENTADA A OBJETOS do 2° semestre do curso de Engenharia de Software da Universidade Federal do Cariri (UFCA).

## OBJETIVOS: 
- Criação de um software simples funcional para um sistema de administração de uma loja virtual, sendo exigido alguns requisitos, como:
  Cadastro de Produtos e Clientes;
  Carrinho;
  Pedidos;
  Pagamentos;
  Cálculo de Frete;
  Emissão de Nota/Sumário de Compra;
  Relatório de Vendas.
  Contendo também, de forma obrigatória, um método de salvamento de dados implementado no software, como um arquivo JSON ou SQLite.

## ESTRUTURA PLANEJADA DE CLASSES:
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
      - Tamanho (Opcional)
      - Cor (Opcional)
      - Disponibilidade no Estoque
 
  - Métodos:
    - CadastrarProduto()
    - ModificarProduto()
 
- Classe: **Carrinho**
  - Atributos:
    - Itens
    - Quantidade de itens adicionados
    - Valor por item
    - Valor total dos itens adicionados no carrinho

  - Métodos:
    - AdicionarItem()
    - RetirarItem()
    - CalcularTotal()
 
- Classe: **Pedidos**
  - Atributos:
    - Quantidade
    - Status
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
    - Data da Confirmação do Pedido
    - Horário da Confirmação do Pedido
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

- Classe: **Relatório de Vendas**
  - Atributos:
    - Top N
    - Ticket Médio
    - Data
    - Faturamento Total
   
  - Métodos:
    - GerarRelatorio()
    
## UML TEXTUAL:
-----------
### Cliente
-----------
Atributos: 
  - Nome: str
  - E-mail: str
  - Senha: str
  - Idade: int
  - Endereço: str

Métodos:
  - CadatrarCliente(nome: str, email: str, senha: str, idade: int, endereco: str)
  - AtualizarPefil(nome: str = None, email: str = None, senha: str = None, idade: int = None, endereco: str = None)
-------------------------------------------------------------------------------------------------------------------

### Produto
-----------
Atributos:
  - Nome: str
  - Categoria: str
  - Preço: float
  - Tamanho (Se necessário): str
  - Cor: str
  - Disponibilidade no Estoque: int

Métodos:
  - CadastrarProduto(nome: str, categoria: str, preco: float, tamanho: str [0..1], cor: str [0..1], disponibilidade: int)
  - ModificarProduto(nome: str = None, categoria: str = None, preco: float = None, tamanho: str [0..1], cor: str [0..1], disponibilidade: int = None)
-----------------------------------------------------------------------------------------------------------------------------------------------------

### Carrinho
------------
Atributos:
  - Itens: str
  - Quantidade de itens adicionados: int
  - Valor por item: float
  - Valor total dos itens adicionados no carrinho: float

Métodos:
  - AdicionarItem(item: str, quantidade: int)
  - RetirarItem(item: str, quantidade: int)
  - CalcularTotal(quantidade: int, valor_item: floar, valor_total: float)
-------------------------------------------------------------------------

### Pedidos
------------
Atributos:
  - Quantidade: int
  - Status: bool
  - Número de Protocolo: str

Métodos:
  - ConfirmarPedido(status: bool)
  - CancelarPedido(status: bool)
---------------------------------

### Pagamento:
--------------
Atributos:
  - Valor: float
  - Desconto: float
  - Valor do Frete: float
  - Status: bool
  - Forma de Pagamento: str

Métodos:
  - AplicarCumpom(desconto: float)
  - PagarPedido(valor: float, desconto: float, frete: float)
  ----------------------------------------------------------

### Frete
---------
Atributos:
  - Valor: float
  - Distância baseada no endereço no remetente e do destinatário: float
  - Prazo de Entrega Estimado: str

Métodos:
  - CalcularFrete(valor: float, distancia: float)
  - PrazoEstimado(prazo: str)
------------------------------------------------------------------------

### Nota Fiscal
---------------
Atributos:
  - Nome da Empresa: str
  - Cadastro Nacional de Pessoa Jurídica (CNPJ): str
  - Data da Confirmação do Pedido: str
  - Horário da Confirmação do Pedido: str
  - Nome do Cliente: str
  - Itens do Pedido: str
  - Valor Por Item: float
  - Valor Total do Pedido: float
  - Descontos: float
  - Forma de Pagamento: str
  - Endereço do Cliente: str
  - Transportadora: str
  - Número de Protocolo: str

Métodos:
  - GerarNota(nome_empresa: str, cnpj: str, data: str, hora: str, nome_cliente: str, itens_pedido: str, valor_item: float, valor_total: float, descontos: float, forma_pagamento: str, endereco: str, transportadora: str, numero_protocolo: str)
----------------------------------------------------------------------------------------------------------------------------------------------------------------

### Relatório de Vendas
-----------------------
Atributos:
  - Top N: str
  - Ticket Médio: float
  - Data: str
  - Faturamento Total: float

Métodos:
  - GerarRelatorio(top_n: str, ticket_medio: float, data: str, faturamento: float)
---------------------------------------------------------------------------------
