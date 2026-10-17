import pytest

from Classes import pedidos

def test_pedido_confirmar_muda_status_e_gera_protocolo():
    pedido = Pedidos()
    pedido.ConfirmarPedido()
 
    assert pedido.status == "ENVIADO"
    assert pedido.numeroProtocolo is not None
    assert len(pedido.numeroProtocolo) == 13
 
 
def test_pedido_nao_confirma_duas_vezes():
    pedido = Pedidos()
    pedido.ConfirmarPedido()
    protocoloAntes = pedido.numeroProtocolo
 
    pedido.ConfirmarPedido()
 
    assert pedido.numeroProtocolo == protocoloAntes
 
 
def test_pedido_marcar_como_entregue():
    pedido = Pedidos()
    pedido.ConfirmarPedido()
    pedido.MarcarComoEntregue("10/10/2026")
 
    assert pedido.status == "ENTREGUE"
    assert pedido.dataEntrega == "10/10/2026"
 
 
def test_pedido_nao_entrega_se_ainda_pendente():
    pedido = Pedidos()
    pedido.MarcarComoEntregue("10/10/2026")
 
    assert pedido.status == "PENDENTE"
    assert pedido.dataEntrega is None
 
 
def test_pedido_nao_cancela_se_ja_entregue():
    pedido = Pedidos()
    pedido.ConfirmarPedido()
    pedido.MarcarComoEntregue("10/10/2026")
 
    pedido.CancelarPedido()
 
    assert pedido.status == "ENTREGUE"
 
 
def test_pedido_cancela_se_pendente():
    pedido = Pedidos()
    pedido.CancelarPedido()
 
    assert pedido.status == "CANCELADO"
