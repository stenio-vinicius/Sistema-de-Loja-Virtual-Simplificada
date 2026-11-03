import pytest

from Classes.validacoes import ConverterData, CpfValido, DataValida, EmailValido, EnderecoValido, NormalizarCpf


def test_normalizar_cpf_remove_pontuacao():
    assert NormalizarCpf("529.982.247-25") == "52998224725"


@pytest.mark.parametrize("cpf", ["529.982.247-25", "52998224725", "111.444.777-35"])
def test_cpf_valido(cpf):
    assert CpfValido(cpf) is True


@pytest.mark.parametrize("cpf", [
    "529.982.247-24",     # dígito verificador errado
    "111.111.111-11",     # todos os dígitos iguais
    "123.456.789-00",
    "123",
    "",
    "abc",
    "529.982.247-250",    # dígitos demais
    None,
])
def test_cpf_invalido(cpf):
    assert CpfValido(cpf) is False


@pytest.mark.parametrize("email", ["a@b.com", "stenio@email.com", "maria.silva@ufca.edu.br"])
def test_email_valido(email):
    assert EmailValido(email) is True


@pytest.mark.parametrize("email", ["semarroba", "a@b", "a b@c.com", "@c.com", "a@@c.com", "a@.com", "a@c.", "", None])
def test_email_invalido(email):
    assert EmailValido(email) is False


def test_endereco_valido():
    assert EnderecoValido("Rua das Flores, 10") is True


@pytest.mark.parametrize("endereco", ["", "   ", "Rua", None])
def test_endereco_invalido(endereco):
    assert EnderecoValido(endereco) is False


def test_data_valida_e_conversao():
    assert DataValida("05/10/2026") is True
    assert ConverterData("05/10/2026").day == 5
    assert ConverterData("05/10/2026").month == 10


@pytest.mark.parametrize("data", ["31/02/2026", "ontem", "2026-10-05", "", None])
def test_data_invalida(data):
    assert DataValida(data) is False
