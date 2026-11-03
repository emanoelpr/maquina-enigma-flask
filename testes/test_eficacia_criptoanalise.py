"""Testes de recuperação real da criptoanálise Enigma.

Copie este arquivo para testes/test_eficacia_criptoanalise.py.

Os dois primeiros testes verificam recuperação com ordem de rotores conhecida,
mas posições iniciais desconhecidas, para M3 e M4. O terceiro é uma busca
ampliada M3 de ~11,8 milhões de configurações; execute-o somente quando quiser
medir a cobertura mais ampla, definindo ENIGMA_TESTE_BUSCA_AMPLA=1.
"""

import os
import time

import pytest

from busca_configuracoes import investigar
from enigma import Enigma

TEXTO_CLARO = (
    "OATAQUEAONORTEACONTECERAOAMANHECERCONFIRMADAPORNOSSASRADASRELATORIOS"
    "DAESQUADRILHAAEREAINDICAMQUEOFORTINHAPROVISLESCOMIDASPARAOINIMIGO"
    "DESCOBRIROMENSAGEMSECRETA"
)


def _cifrar_m3():
    """Vetor reprodutível com rotores I-II-III, anéis 1-8-14, refletor B."""
    maquina = Enigma(
        rotores=("I", "II", "III"),
        posicoes_rotores=(3, 19, 0),  # DTA: posição inicial desconhecida na busca
        configuracoes_anel=(0, 7, 13),
        nome_refletor="B",
        conexoes_plugboard="",
    )
    return maquina.cifrar_texto(TEXTO_CLARO)


def _cifrar_m4():
    """Vetor M4 com Beta, rotores VI-II-VIII, anéis 1-8-14, refletor Bfino."""
    maquina = Enigma(
        rotores=("Beta", "VI", "II", "VIII"),
        posicoes_rotores=(4, 3, 19, 0),  # rotor grego E; rotores principais DTA
        configuracoes_anel=(0, 0, 7, 13),
        nome_refletor="Bfino",
        conexoes_plugboard="",
    )
    return maquina.cifrar_texto(TEXTO_CLARO)


def _validar_resultado(resultado, tempo):
    candidatos = resultado["candidatos"]
    assert candidatos, "A busca não devolveu candidatos."
    assert any(candidato["texto"] == TEXTO_CLARO for candidato in candidatos), (
        "O texto original não apareceu entre os candidatos. "
        f"Método={resultado.get('metodo')}; "
        f"combinações={resultado.get('combinacoes_testadas')}; "
        f"tempo={tempo:.2f}s; "
        f"melhor candidato={candidatos[0].get('texto', '')[:100]}"
    )
    assert all(candidato.get("verificado_no_motor") is True for candidato in candidatos)


def test_configurada_m3_recupera_texto_com_posicoes_desconhecidas():
    cifra = _cifrar_m3()
    inicio = time.perf_counter()
    resultado = investigar(
        modo="configurada",
        texto_cifrado=cifra,
        modelo="M3",
        idioma="pt",
        conhecidos={
            "rotores": ("I", "II", "III"),
            "aneis": (1, 8, 14),
            "refletor": "B",
            "plugboard_modo": "vazio",
        },
        limite=10,
    )
    tempo = time.perf_counter() - inicio
    _validar_resultado(resultado, tempo)
    assert resultado["cobertura_completa"] is True
    assert resultado["combinacoes_testadas"] == 26 ** 3
    print(f"M3 configurada: {tempo:.2f}s; {resultado['combinacoes_testadas']:,} posições")


def test_configurada_m4_recupera_texto_com_posicoes_desconhecidas():
    cifra = _cifrar_m4()
    inicio = time.perf_counter()
    resultado = investigar(
        modo="configurada",
        texto_cifrado=cifra,
        modelo="M4",
        idioma="pt",
        conhecidos={
            "rotores": ("VI", "II", "VIII"),
            "aneis": (1, 8, 14),
            "refletor": "Bfino",
            "rotor_grego": "Beta",
            "plugboard_modo": "vazio",
        },
        limite=10,
    )
    tempo = time.perf_counter() - inicio
    _validar_resultado(resultado, tempo)
    assert resultado["cobertura_completa"] is True
    assert resultado["combinacoes_testadas"] == 26 ** 4
    print(f"M4 configurada: {tempo:.2f}s; {resultado['combinacoes_testadas']:,} posições")


@pytest.mark.skipif(
    os.environ.get("ENIGMA_TESTE_BUSCA_AMPLA") != "1",
    reason="Busca ampliada M3 testa ~11,8 milhões de configurações; ativar por variável de ambiente.",
)
def test_ampliada_m3_descobre_ordem_de_rotores_e_refletor():
    cifra = _cifrar_m3()
    inicio = time.perf_counter()
    resultado = investigar(
        modo="ampliada",
        texto_cifrado=cifra,
        modelo="M3",
        idioma="pt",
        conhecidos={
            # A ordem dos rotores e o refletor ficam desconhecidos.
            # Os anéis são conhecidos para manter a busca dentro do orçamento.
            "aneis": (1, 8, 14),
            "plugboard_modo": "vazio",
        },
        limite=10,
    )
    tempo = time.perf_counter() - inicio
    _validar_resultado(resultado, tempo)
    assert resultado["cobertura_completa"] is True
    assert resultado["combinacoes_testadas"] == 8 * 7 * 6 * 2 * (26 ** 3)
    print(
        "M3 ampliada: "
        f"{tempo:.2f}s; {resultado['combinacoes_testadas']:,} configurações; "
        f"cobertura completa={resultado['cobertura_completa']}"
    )
