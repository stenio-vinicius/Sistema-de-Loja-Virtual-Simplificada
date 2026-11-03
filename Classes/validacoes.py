from datetime import datetime

FORMATO_DATA = "%d/%m/%Y"


def ConverterData(texto):
    return datetime.strptime(texto, FORMATO_DATA)


def DataValida(texto):
    try:
        ConverterData(texto)
        return True
    except (ValueError, TypeError):
        return False


def NormalizarCpf(cpf):
    digitos = ""

    for caractere in str(cpf):
        if caractere.isdigit():
            digitos += caractere

    return digitos


def CpfValido(cpf):
    if cpf is None:
        return False

    digitos = NormalizarCpf(cpf)

    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False

    for posicao in (9, 10):
        soma = 0
        for indice in range(posicao):
            soma += int(digitos[indice]) * (posicao + 1 - indice)

        verificador = (soma * 10) % 11
        if verificador == 10:
            verificador = 0

        if verificador != int(digitos[posicao]):
            return False

    return True


def EmailValido(email):
    if email is None or " " in email:
        return False

    partes = email.split("@")
    if len(partes) != 2:
        return False

    usuario, dominio = partes

    return usuario != "" and "." in dominio and not dominio.startswith(".") and not dominio.endswith(".")


def EnderecoValido(endereco):
    return endereco is not None and len(endereco.strip()) >= 5
