"""Teste de eficácia da busca M4 usando a mensagem real do catálogo.

O teste rápido valida os dados e o tamanho do escopo. As duas buscas exaustivas
só rodam quando ENIGMA_TESTE_COMBOIO_M4=1.

Importante: a configuração atual da missão registra aneis=(1, 8, 14, 21),
com o anel do rotor grego primeiro. Portanto, os anéis dos três rotores
principais da mensagem real são (8, 14, 21), e não (1, 8, 14). O teste faz
primeiro a busca com os valores pedidos (1, 8, 14) como diagnóstico e depois
com os valores correspondentes à missão atual. Nenhum algoritmo é alterado.

PowerShell:
    python -m pytest testes/test_m4_comboio_real.py -q -s
    $env:ENIGMA_TESTE_COMBOIO_M4="1"
    python -m pytest testes/test_m4_comboio_real.py -q -s
    Remove-Item Env:ENIGMA_TESTE_COMBOIO_M4
"""

import os
import time

import pytest

from busca_configuracoes import descrever_espaco, investigar
from desafios import _maquina_de, missoes
from enigma import Enigma

ID_MISSAO = "comboio-atlantico"
ROTORES_CONHECIDOS = ("VI", "II", "VIII")
ANEIS_SOLICITADOS = (1, 8, 14)
LIMITE_CANDIDATOS = 100

# 2 rotores gregos × 2 refletores × 26 posições gregas × 26³ posições principais.
CONFIGURACOES_ESPERADAS = 2 * 2 * 26 * (26 ** 3)
EXECUTAR_BUSCAS = os.environ.get("ENIGMA_TESTE_COMBOIO_M4") == "1"


def _missao_real():
    missao = missoes[ID_MISSAO]
    assert missao["modelo"] == "M4"
    assert missao["rotores"] == ROTORES_CONHECIDOS
    assert missao["mensagem_cifrada"] == "BTMZKSCOPHZKUSIFZEVNAMMLQWPKX"
    assert missao["texto_claro"] == "SUBMARINOSPARTEMDOPORTOANOITE"
    # A lista de aneis da M4 inclui o anel grego como primeiro valor.
    assert tuple(missao["aneis"]) == (1, 8, 14, 21)
    # A cifra do catálogo precisa continuar coerente com a configuração oficial.
    assert _maquina_de(missao).cifrar_texto(missao["mensagem_cifrada"]) == missao["texto_claro"]
    return missao


def _mapa_grego_refletor(rotor_grego, posicao_grega, refletor, aneis_principais):
    """Mapa Greek → refletor fino → Greek obtido pelo motor Enigma real."""
    aneis_motor = (0, *(anel - 1 for anel in aneis_principais))
    maquina = Enigma(
        rotores=(rotor_grego, *ROTORES_CONHECIDOS),
        posicoes_rotores=(ord(posicao_grega) - ord("A"), 0, 0, 0),
        configuracoes_anel=aneis_motor,
        nome_refletor=refletor,
        conexoes_plugboard="",
    )
    rotor = maquina.rotor_grego
    return tuple(
        rotor.cifrar_reverso(maquina.refletor.cifrar(rotor.cifrar_direto(letra)))
        for letra in range(26)
    )


def _executar_busca(missao, aneis_principais):
    conhecidos = {
        "rotores": ROTORES_CONHECIDOS,
        "aneis": tuple(aneis_principais),
        "plugboard_modo": "vazio",
    }
    espaco_esperado = descrever_espaco("M4", conhecidos, "ampliada")
    assert espaco_esperado["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert espaco_esperado["dentro_do_orcamento"] is True

    atualizacoes_progresso = []
    inicio = time.perf_counter()
    resultado = investigar(
        modo="ampliada",
        texto_cifrado=missao["mensagem_cifrada"],
        modelo="M4",
        idioma="pt",
        conhecidos=conhecidos,
        limite=LIMITE_CANDIDATOS,
        progresso=atualizacoes_progresso.append,
    )
    tempo_real = time.perf_counter() - inicio

    assert resultado["modo"] == "ampliada"
    assert resultado["metodo"] == "exaustiva"
    assert resultado["cobertura_completa"] is True
    assert resultado["combinacoes_testadas"] == CONFIGURACOES_ESPERADAS
    assert resultado["espaco"]["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert resultado["candidatos"], "A busca não devolveu candidatos."
    assert all(c.get("verificado_no_motor") is True for c in resultado["candidatos"])
    assert atualizacoes_progresso, "A busca não informou progresso."
    avaliadas_reportadas = [item["avaliadas"] for item in atualizacoes_progresso]
    assert avaliadas_reportadas == sorted(avaliadas_reportadas), "O progresso diminuiu durante a busca."

    return resultado, tempo_real


def test_dados_reais_do_comboio_e_escopo_controlado_estao_consistentes():
    missao = _missao_real()
    # O teste com anéis 1-8-14 tem o tamanho esperado, mas não corresponde aos
    # três anéis principais registrados na missão atual (8-14-21).
    espaco = descrever_espaco(
        "M4",
        {
            "rotores": ROTORES_CONHECIDOS,
            "aneis": ANEIS_SOLICITADOS,
            "plugboard_modo": "vazio",
        },
        "ampliada",
    )
    assert espaco["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert tuple(missao["aneis"][1:]) == (8, 14, 21)
    assert tuple(missao["aneis"][1:]) != ANEIS_SOLICITADOS
    print(
        "Dados da missão conferidos: ciphertext=BTMZKSCOPHZKUSIFZEVNAMMLQWPKX; "
        "anéis principais registrados=8-14-21; anéis solicitados para diagnóstico=1-8-14; "
        f"escopo por busca={CONFIGURACOES_ESPERADAS:,}.".replace(",", ".")
    )


@pytest.mark.skipif(
    not EXECUTAR_BUSCAS,
    reason="Busca M4 exaustiva (1.827.904 configurações por rodada); defina ENIGMA_TESTE_COMBOIO_M4=1.",
)
def test_diagnostico_m4_comboio_com_aneis_solicitados_1_8_14():
    """Mede a busca exatamente com anéis principais 1-8-14, sem presumir sucesso."""
    missao = _missao_real()
    resultado, tempo_real = _executar_busca(missao, ANEIS_SOLICITADOS)
    corretos = [c for c in resultado["candidatos"] if c["texto"] == missao["texto_claro"]]
    print(
        "Diagnóstico com anéis principais 1-8-14: "
        f"{tempo_real:.2f}s; {resultado['combinacoes_testadas']:,} configurações; "
        f"cobertura completa={resultado['cobertura_completa']}; "
        f"texto esperado entre os {len(resultado['candidatos'])} candidatos={bool(corretos)}; "
        f"melhor candidato={resultado['candidatos'][0]['texto']!r}.".replace(",", ".")
    )
    # Esta rodada é diagnóstica: não falha apenas porque os anéis pedidos podem
    # não corresponder à chave que produziu a mensagem real do catálogo.


@pytest.mark.skipif(
    not EXECUTAR_BUSCAS,
    reason="Busca M4 exaustiva (1.827.904 configurações por rodada); defina ENIGMA_TESTE_COMBOIO_M4=1.",
)
def test_m4_comboio_com_aneis_reais_recupera_texto_e_equivalencia_eletrica():
    """Confere a busca sobre a cifra real usando os anéis principais do catálogo."""
    missao = _missao_real()
    aneis_reais = tuple(missao["aneis"][1:])
    mapa_real = _mapa_grego_refletor(
        missao["rotor_grego"], missao["posicoes"][0], missao["refletor"], aneis_reais
    )

    resultado, tempo_real = _executar_busca(missao, aneis_reais)
    candidatos = resultado["candidatos"]
    corretos = [c for c in candidatos if c["texto"] == missao["texto_claro"]]

    assert corretos, (
        "A mensagem real não apareceu entre os candidatos com anéis principais "
        f"{aneis_reais}. Tempo={tempo_real:.2f}s; candidatos={len(candidatos)}; "
        f"melhor texto={candidatos[0].get('texto', '')!r}."
    )

    posicoes_principais_reais = "".join(missao["posicoes"][1:])
    equivalentes = []
    for candidato in corretos:
        if candidato.get("rotores") != list(ROTORES_CONHECIDOS):
            continue
        if candidato.get("aneis") != list(aneis_reais):
            continue
        if candidato.get("posicoes") != posicoes_principais_reais:
            continue
        if not all(chave in candidato for chave in ("rotor_grego", "posicao_grega", "refletor")):
            continue
        mapa_candidato = _mapa_grego_refletor(
            candidato["rotor_grego"], candidato["posicao_grega"],
            candidato["refletor"], aneis_reais,
        )
        if mapa_candidato == mapa_real:
            equivalentes.append(candidato)

    assert equivalentes, (
        "A busca recuperou o texto, mas não encontrou entre os candidatos a configuração "
        "principal esperada com o mesmo mapa elétrico grego+refletor. Confira o ranking."
    )

    melhor = equivalentes[0]
    print(
        "Comboio no Atlântico — M4 real: "
        f"{tempo_real:.2f}s; {resultado['combinacoes_testadas']:,} configurações; "
        f"cobertura completa={resultado['cobertura_completa']}; "
        f"texto recuperado=True; rotor grego={melhor['rotor_grego']}@{melhor['posicao_grega']}; "
        f"refletor={melhor['refletor']}; posições principais={melhor['posicoes']}; "
        "mapa elétrico equivalente=True.".replace(",", ".")
    )
