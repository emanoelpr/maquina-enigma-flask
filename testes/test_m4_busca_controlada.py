"""Teste controlado da busca ampliada M4.

Escopo: ordem dos três rotores principais e anéis conhecidos; rotor grego,
refletor e todas as posições iniciais desconhecidos.

O teste rápido do escopo roda normalmente. A busca integral de ~1,83 milhão de
configurações só roda quando ENIGMA_TESTE_M4_AMPLIADA=1, pois pode levar vários
segundos ou minutos dependendo do computador.

Uso no Windows PowerShell:
    python -m pytest testes/test_m4_busca_controlada.py -q -s
    $env:ENIGMA_TESTE_M4_AMPLIADA="1"
    python -m pytest testes/test_m4_busca_controlada.py::test_m4_ampliada_recupera_texto_e_caminho_eletrico -q -s
    Remove-Item Env:ENIGMA_TESTE_M4_AMPLIADA
"""

import os
import time

import pytest

from busca_configuracoes import descrever_espaco, investigar
from enigma import Enigma

TEXTO_CLARO = (
    "OATAQUEAONORTEACONTECERAOAMANHECERCONFIRMADAPORNOSSASRADASRELATORIOS"
    "DAESQUADRILHAAEREAINDICAMQUEOFORTINHAPROVISLESCOMIDASPARAOINIMIGO"
    "DESCOBRIROMENSAGEMSECRETA"
)

ROTORES_PRINCIPAIS = ("VI", "II", "VIII")
ANEIS_PRINCIPAIS = (1, 8, 14)
POSICOES_PRINCIPAIS = "DTA"
ROTOR_GREGO_REAL = "Beta"
POSICAO_GREGA_REAL = "E"
REFLETOR_REAL = "Bfino"

# Orçamento esperado: 2 rotores gregos × 2 refletores × 26 posições gregas
# × 26³ posições dos rotores principais. Ordem e anéis ficam conhecidos.
CONFIGURACOES_ESPERADAS = 2 * 2 * 26 * (26 ** 3)


def _cifrar_m4_de_referencia():
    """Gera a cifra usando o motor real, sem depender da busca."""
    maquina = Enigma(
        rotores=(ROTOR_GREGO_REAL, *ROTORES_PRINCIPAIS),
        posicoes_rotores=(4, 3, 19, 0),  # E-D-T-A; posições iniciais
        configuracoes_anel=(0, 0, 7, 13),  # 1-1-8-14 na interface
        nome_refletor=REFLETOR_REAL,
        conexoes_plugboard="",
    )
    cifra = maquina.cifrar_texto(TEXTO_CLARO)
    assert len(cifra) == len(TEXTO_CLARO)
    return cifra


def _caminho_fixo_grego_refletor(grego, posicao_grega, refletor):
    """Obtém o mapa elétrico Greek→reflector→Greek pelo motor real.

    O rotor grego não avança. Aplicar as duas passagens diretamente permite
    comparar os 26 mapeamentos sem depender do avaliador vetorizado da busca.
    """
    maquina = Enigma(
        rotores=(grego, *ROTORES_PRINCIPAIS),
        posicoes_rotores=(ord(posicao_grega) - ord("A"), 0, 0, 0),
        configuracoes_anel=(0, 0, 7, 13),
        nome_refletor=refletor,
        conexoes_plugboard="",
    )
    rotor = maquina.rotor_grego
    return tuple(
        rotor.cifrar_reverso(maquina.refletor.cifrar(rotor.cifrar_direto(letra)))
        for letra in range(26)
    )


def _parametros_conhecidos():
    """Só fixa a ordem dos rotores principais, anéis e plugboard vazio."""
    return {
        "rotores": ROTORES_PRINCIPAIS,
        "aneis": ANEIS_PRINCIPAIS,
        "plugboard_modo": "vazio",
    }


def test_escopo_m4_controlado_tem_total_esperado():
    conhecidos = _parametros_conhecidos()
    espaco = descrever_espaco("M4", conhecidos, "ampliada")

    assert espaco["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert espaco["dentro_do_orcamento"] is True
    assert espaco["heuristica"] is False

    dimensoes = {item["nome"]: item for item in espaco["dimensoes"]}
    assert dimensoes["Ordem dos rotores"]["tipo"] == "fixa"
    assert dimensoes["Anéis"]["tipo"] == "fixa"
    assert dimensoes["Refletor"]["tamanho"] == 2
    assert dimensoes["Rotor grego"]["tamanho"] == 2
    assert dimensoes["Posição do rotor grego"]["tamanho"] == 26
    assert dimensoes["Posições iniciais (3 rotores)"]["tamanho"] == 26 ** 3


@pytest.mark.skipif(
    os.environ.get("ENIGMA_TESTE_M4_AMPLIADA") != "1",
    reason=(
        "Busca exaustiva M4 controlada (~1,83 milhão de configurações). "
        "Defina ENIGMA_TESTE_M4_AMPLIADA=1 para executá-la."
    ),
)
def test_m4_ampliada_recupera_texto_e_caminho_eletrico():
    cifra = _cifrar_m4_de_referencia()
    caminho_real = _caminho_fixo_grego_refletor(
        ROTOR_GREGO_REAL, POSICAO_GREGA_REAL, REFLETOR_REAL
    )

    inicio = time.perf_counter()
    resultado = investigar(
        modo="ampliada",
        texto_cifrado=cifra,
        modelo="M4",
        idioma="pt",
        conhecidos=_parametros_conhecidos(),
        limite=25,
    )
    tempo = time.perf_counter() - inicio

    assert resultado["modo"] == "ampliada"
    assert resultado["metodo"] == "exaustiva"
    assert resultado["cobertura_completa"] is True
    assert resultado["combinacoes_testadas"] == CONFIGURACOES_ESPERADAS
    assert resultado["espaco"]["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert resultado["tempo_segundos"] >= 0

    candidatos = resultado["candidatos"]
    assert candidatos, "A busca não retornou candidatos."
    assert all(item.get("verificado_no_motor") is True for item in candidatos)

    # Primeiro, o texto claro deve ser recuperado e validado pelo motor real.
    candidatos_corretos = [item for item in candidatos if item["texto"] == TEXTO_CLARO]
    assert candidatos_corretos, (
        "O texto claro não apareceu nos 25 candidatos. "
        f"Configurações avaliadas={resultado['combinacoes_testadas']}; "
        f"tempo={tempo:.2f}s; melhor candidato={candidatos[0].get('texto', '')[:100]!r}"
    )

    # Em seguida, exige a ordem e os anéis conhecidos, as posições dos três
    # rotores principais e o mesmo mapa elétrico combinado de rotor grego +
    # refletor. Isso admite uma chave equivalente somente quando os 26 mapas
    # de entrada são idênticos — não apenas quando o texto é igual por acaso.
    equivalentes = []
    for candidato in candidatos_corretos:
        if candidato.get("rotores") != list(ROTORES_PRINCIPAIS):
            continue
        if candidato.get("aneis") != list(ANEIS_PRINCIPAIS):
            continue
        if candidato.get("posicoes") != POSICOES_PRINCIPAIS:
            continue
        if not all(
            chave in candidato
            for chave in ("rotor_grego", "posicao_grega", "refletor")
        ):
            continue
        caminho_candidato = _caminho_fixo_grego_refletor(
            candidato["rotor_grego"],
            candidato["posicao_grega"],
            candidato["refletor"],
        )
        if caminho_candidato == caminho_real:
            equivalentes.append(candidato)

    assert equivalentes, (
        "O texto claro foi recuperado, mas nenhum candidato entre os resultados "
        "preservou a configuração principal conhecida e o mapa elétrico equivalente "
        "do conjunto rotor grego + refletor. Confira o ranking e o limite de candidatos."
    )

    melhor = equivalentes[0]
    print(
        "M4 ampliada controlada: "
        f"{tempo:.2f}s; {resultado['combinacoes_testadas']:,} configurações; "
        f"cobertura completa={resultado['cobertura_completa']}; "
        f"rotor grego={melhor['rotor_grego']}@{melhor['posicao_grega']}; "
        f"refletor={melhor['refletor']}; "
        f"posição principal={melhor['posicoes']}; "
        f"mapa elétrico equivalente=True"
    )
