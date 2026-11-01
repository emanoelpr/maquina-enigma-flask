"""Equivalência entre o avaliador acelerado da busca e o motor Enigma.

O avaliador acelerado (_montar_avaliador) precisa devolver exatamente a
mesma pontuação que o caminho original — motor Enigma + pontuar_candidato —
para toda posição inicial, incluindo casos de duplo passo e borda.
"""

import random
from itertools import product

from criptoanalise import _montar_avaliador, pontuar_candidato
from enigma import Enigma
from pontuacao import normalizar

trecho = normalizar(
    "OPCILLAZFXLQTDNLGGLEKDIZOKQKGXIEZKDATAQUEAOAMANHECERNOLITOR"
)[:150]


def numeros_do(texto):
    return [ord(letra) - ord("A") for letra in texto]


def test_avaliador_equivalente_ao_motor_em_todas_as_posicoes_m3():
    maquina = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
    avaliar = _montar_avaliador(maquina, "pt", numeros_do(trecho), False)

    for posicoes in product(range(26), repeat=3):
        for rotor, posicao in zip(
            (maquina.rotor_esquerdo, maquina.rotor_central, maquina.rotor_direito),
            posicoes,
        ):
            rotor.posicao_rotor = posicao

        esperado = pontuar_candidato(maquina.cifrar_texto(trecho), "pt")
        assert avaliar(posicoes) == esperado, posicoes


def test_avaliador_equivalente_ao_motor_em_amostra_m4():
    maquina = Enigma(
        ("Beta", "IV", "II", "V"), (0, 0, 0, 0), (0, 7, 13, 20), "Bfino", ""
    )
    avaliar = _montar_avaliador(maquina, "pt", numeros_do(trecho), True)

    sorteador = random.Random(42)
    casos = [
        (sorteador.randrange(26), sorteador.randrange(26),
         sorteador.randrange(26), sorteador.randrange(26))
        for _ in range(500)
    ]
    # Bordas e casos de duplo passo: origem, fim do alfabeto e entalhes.
    casos += [(0, 0, 0, 0), (25, 25, 25, 25), (4, 0, 20, 0), (4, 25, 20, 7)]

    for posicoes in casos:
        maquina.rotor_grego.posicao_rotor = posicoes[0]
        for rotor, posicao in zip(
            (maquina.rotor_esquerdo, maquina.rotor_central, maquina.rotor_direito),
            posicoes[1:],
        ):
            rotor.posicao_rotor = posicao

        esperado = pontuar_candidato(maquina.cifrar_texto(trecho), "pt")
        assert avaliar(posicoes) == esperado, posicoes


def test_avaliador_equivalente_com_aneis_rotores_e_idiomas_variados():
    configuracoes = [
        (("I", "II", "III"), (0, 0, 0), "B", "pt", None),
        (("IV", "II", "V"), (7, 13, 20), "C", "en", None),
        (("VI", "VII", "VIII"), (1, 8, 14), "B", "en", None),
        (("Beta", "IV", "II", "V"), (0, 7, 13, 20), "Bfino", "pt", True),
        (("Gamma", "VI", "VII", "VIII"), (5, 1, 8, 14), "Cfino", "en", True),
    ]

    for rotores, aneis, refletor, idioma, usa_grego in configuracoes:
        maquina = Enigma(
            rotores=rotores,
            posicoes_rotores=[0] * len(rotores),
            configuracoes_anel=aneis,
            nome_refletor=refletor,
            conexoes_plugboard="",
        )
        avaliar = _montar_avaliador(maquina, idioma, numeros_do(trecho), usa_grego)

        sorteador = random.Random(7)
        for _ in range(50):
            posicoes = tuple(sorteador.randrange(26) for _ in rotores)
            if usa_grego:
                maquina.rotor_grego.posicao_rotor = posicoes[0]
                principais = posicoes[1:]
            else:
                principais = posicoes
            for rotor, posicao in zip(
                (maquina.rotor_esquerdo, maquina.rotor_central, maquina.rotor_direito),
                principais,
            ):
                rotor.posicao_rotor = posicao

            esperado = pontuar_candidato(maquina.cifrar_texto(trecho), idioma)
            assert avaliar(posicoes) == esperado, (rotores, refletor, posicoes)


def test_m3_vetor_conhecido_ilbdaamtaz_helloworld():
    # A recíproca vale para a MESMA posição inicial: cada direção usa uma
    # máquina recém-criada, como em test_cifrar_duas_vezes_retorna_original.
    cifradora = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
    decifradora = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
    cifrado = cifradora.cifrar_texto("HELLOWORLD")
    assert cifrado == "ILBDAAMTAZ"
    assert decifradora.cifrar_texto(cifrado) == "HELLOWORLD"


def test_m4_recupera_mensagem_de_referencia():
    from criptoanalise import atacar_posicoes

    origem = Enigma(
        ("Beta", "IV", "II", "V"), (11, 3, 19, 2), (0, 7, 13, 20), "Bfino", ""
    )
    cifrado = origem.cifrar_texto("ATAQUEAOAMANHECERNOLITORALNORTECONFIRMADO")

    resultado = atacar_posicoes(
        cifrado, ("IV", "II", "V"), [8, 14, 21], "Bfino", "pt",
        limite=5, modelo="M4", rotor_grego="Beta",
    )

    melhor = resultado["candidatos"][0]
    assert melhor["posicoes"] == "DTC"
    assert melhor["posicao_grega"] == "L"
    assert melhor["texto"] == "ATAQUEAOAMANHECERNOLITORALNORTECONFIRMADO"
    assert resultado["combinacoes_testadas"] == 456976
