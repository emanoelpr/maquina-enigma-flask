
import pytest

from enigma import Enigma
from criptoanalise import atacar_posicoes


rotores = ("I", "II", "III")
aneis = [1, 1, 1]


def test_rejeita_texto_curto():
    with pytest.raises(ValueError, match="pelo menos três letras"):
        atacar_posicoes(
            "AB", rotores, aneis, "B", "pt"
        )

def test_rejeita_idioma_invalido():
    with pytest.raises(ValueError, match="Idioma inválido"):
        atacar_posicoes(
            "ABCDEF", rotores, aneis, "B", "fr"
        )

def test_rejeita_quantidade_incorreta_de_rotores():
    with pytest.raises(ValueError, match="exatamente três rotores"):
        atacar_posicoes(
            "ABCDEF", ("I", "II"), [1, 1], "B", "pt"
        )

def test_rejeita_rotores_repetidos():
    with pytest.raises(ValueError, match="devem ser diferentes"):
        atacar_posicoes(
            "ABCDEF", ("I", "I", "III"), aneis, "B", "pt"
        )

def test_rejeita_refletor_invalido():
    with pytest.raises(ValueError, match="refletores B ou C"):
        atacar_posicoes(
            "ABCDEF", rotores, aneis, "Bfino", "pt"
        )

def test_rejeita_limite_invalido():
    with pytest.raises(ValueError, match="limite"):
        atacar_posicoes(
            "ABCDEF", rotores, aneis, "B", "pt", limite=0
        )

def test_busca_testa_todas_as_posicoes_e_retorna_candidatos():
    resultado = atacar_posicoes(
        "OPCILLAZFXLQTDNLGGLEKDIZOKQKGXIEZKD",
        rotores,
        aneis,
        "B",
        "en",
        limite=5,
    )

    assert resultado["combinacoes_testadas"] == 17576
    assert resultado["idioma"] == "en"
    assert len(resultado["candidatos"]) == 5

    pontuacoes = [
        candidato["pontuacao"]
        for candidato in resultado["candidatos"]
    ]

    assert pontuacoes == sorted(pontuacoes, reverse=True)

    for candidato in resultado["candidatos"]:
        assert len(candidato["posicoes"]) == 3
        assert all(letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                   for letra in candidato["posicoes"])
        assert candidato["idioma"] == "en"
