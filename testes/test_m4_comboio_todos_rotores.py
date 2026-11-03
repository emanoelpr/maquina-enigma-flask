"""Teste isolado e pesado da busca M4 com ordem dos rotores desconhecida.

Missão: Comboio no Atlântico.
Conhecidos: anéis principais 8-14-21; plugboard vazio; modelo M4.
Desconhecidos: ordem dos rotores principais, rotor grego, refletor e todas
as posições iniciais.

O teste integral é deliberadamente ignorado na suíte rápida e só executa com:
    $env:ENIGMA_TESTE_M4_TODOS_ROTORES="1"
    python -m pytest testes/test_m4_comboio_todos_rotores.py::test_m4_comboio_busca_todas_as_ordens -q -s
    Remove-Item Env:ENIGMA_TESTE_M4_TODOS_ROTORES

O espaço é de 614.175.744 configurações. O orçamento é elevado SOMENTE em
memória de teste (monkeypatch) para permitir medir a busca completa sem mudar
o código de produção. A busca pode demorar muitos minutos. A cobertura e o
tempo reportados vêm do resultado real da função investigar().
"""

import os
import time

import pytest

import busca_configuracoes as modulo_busca
from busca_configuracoes import descrever_espaco, investigar
from criptoanalise import BuscaCancelada
from desafios import _maquina_de, missoes
from enigma import Enigma

ID_MISSAO = "comboio-atlantico"
MENSAGEM_CIFRADA = "BTMZKSCOPHZKUSIFZEVNAMMLQWPKX"
TEXTO_CLARO = "SUBMARINOSPARTEMDOPORTOANOITE"
ANEIS_PRINCIPAIS = (8, 14, 21)
PLUGBOARD = ""
LIMITE_CANDIDATOS = 100
CONFIGURACOES_ESPERADAS = 8 * 7 * 6 * 2 * 2 * 26 * (26 ** 3)
EXECUTAR_BUSCA_INTEGRAL = (
    os.environ.get("ENIGMA_TESTE_M4_TODOS_ROTORES") == "1"
)


def _conhecidos():
    """Não informa ordem, refletor, rotor grego nem posições iniciais."""
    return {
        "aneis": ANEIS_PRINCIPAIS,
        "plugboard_modo": "vazio",
        "plugboard": PLUGBOARD,
    }


def _validar_missao_real():
    missao = missoes[ID_MISSAO]
    assert missao["modelo"] == "M4"
    assert missao["mensagem_cifrada"] == MENSAGEM_CIFRADA
    assert missao["texto_claro"] == TEXTO_CLARO
    # Em desafios.py os anéis M4 estão na ordem: grego, esquerdo, central, direito.
    assert tuple(missao["aneis"][1:]) == ANEIS_PRINCIPAIS
    assert missao["plugboard"] == PLUGBOARD
    decifrado = _maquina_de(missao).cifrar_texto(MENSAGEM_CIFRADA)
    assert decifrado == TEXTO_CLARO, (
        "A mensagem do catálogo não confere com a configuração oficial do motor."
    )
    return missao


def _mapa_grego_refletor(grego, posicao_grega, refletor, aneis_principais):
    """Mapa elétrico Greek → refletor fino → Greek, medido no motor real."""
    # A ordem principal não altera este trecho fixo do caminho elétrico.
    maquina = Enigma(
        rotores=(grego, "VI", "II", "VIII"),
        posicoes_rotores=(ord(posicao_grega) - ord("A"), 0, 0, 0),
        configuracoes_anel=(0, *(anel - 1 for anel in aneis_principais)),
        nome_refletor=refletor,
        conexoes_plugboard="",
    )
    rotor = maquina.rotor_grego
    return tuple(
        rotor.cifrar_reverso(maquina.refletor.cifrar(rotor.cifrar_direto(letra)))
        for letra in range(26)
    )


def test_escopo_m4_todos_rotores_calcula_cobertura_completa():
    """Teste rápido: documenta a quantidade exata, sem iniciar a busca longa."""
    missao = _validar_missao_real()
    assert tuple(missao["aneis"][1:]) == ANEIS_PRINCIPAIS

    espaco = descrever_espaco("M4", _conhecidos(), "ampliada")
    assert espaco["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert CONFIGURACOES_ESPERADAS == 614_175_744

    dimensoes = {item["nome"]: item for item in espaco["dimensoes"]}
    assert dimensoes["Ordem dos rotores"]["tamanho"] == 8 * 7 * 6
    assert dimensoes["Ordem dos rotores"]["tipo"] == "exaustiva"
    assert dimensoes["Refletor"]["tamanho"] == 2
    assert dimensoes["Rotor grego"]["tamanho"] == 2
    assert dimensoes["Posição do rotor grego"]["tamanho"] == 26
    assert dimensoes["Posições iniciais (3 rotores)"]["tamanho"] == 26 ** 3
    assert dimensoes["Anéis"]["tipo"] == "fixa"

    dentro_do_orcamento = espaco["dentro_do_orcamento"]
    print(
        "Escopo M4 todos os rotores: "
        f"{CONFIGURACOES_ESPERADAS:,} configurações; "
        f"orçamento atual={espaco['orcamento']:,}; "
        f"dentro do orçamento de produção={dentro_do_orcamento}. "
        "Dimensões desconhecidas: ordem (336), rotor grego (2), "
        "refletor (2), posição grega (26) e posições principais (26³)."
        .replace(",", ".")
    )


def test_cancelamento_interrompe_busca_m4_ampla_depois_de_um_bloco(monkeypatch):
    """Testa cancelamento real após um bloco de 17.576 posições, sem busca longa."""
    _validar_missao_real()
    # Permite iniciar a busca apenas durante este teste; não altera o arquivo
    # nem o orçamento do processo depois que o teste termina.
    monkeypatch.setattr(
        modulo_busca,
        "orcamento_exaustivo",
        max(modulo_busca.orcamento_exaustivo, CONFIGURACOES_ESPERADAS + 1),
    )

    chamadas_cancelamento = {"n": 0}

    def cancelar_apos_um_bloco():
        chamadas_cancelamento["n"] += 1
        # Primeira consulta: autoriza o primeiro bloco. Segunda: interrompe
        # antes de começar o bloco seguinte.
        return chamadas_cancelamento["n"] >= 2

    inicio = time.perf_counter()
    with pytest.raises(BuscaCancelada) as capturada:
        investigar(
            modo="ampliada",
            texto_cifrado=MENSAGEM_CIFRADA,
            modelo="M4",
            idioma="pt",
            conhecidos=_conhecidos(),
            limite=10,
            cancelado=cancelar_apos_um_bloco,
        )
    duracao = time.perf_counter() - inicio
    avaliadas = capturada.value.combinacoes_testadas

    assert chamadas_cancelamento["n"] >= 2
    assert 0 < avaliadas < CONFIGURACOES_ESPERADAS
    assert avaliadas % (26 ** 3) == 0
    print(
        f"Cancelamento M4: {duracao:.2f}s; {avaliadas:,} configurações "
        f"avaliadas de {CONFIGURACOES_ESPERADAS:,}; cancelamento real confirmado."
        .replace(",", ".")
    )


@pytest.mark.skipif(
    not EXECUTAR_BUSCA_INTEGRAL,
    reason=(
        "Busca M4 integral (614.175.744 configurações), mantida fora da suíte rápida. "
        "Defina ENIGMA_TESTE_M4_TODOS_ROTORES=1 para executá-la explicitamente."
    ),
)
def test_m4_comboio_busca_todas_as_ordens(monkeypatch):
    """Executa o escopo inteiro, mede cobertura/tempo e verifica a recuperação real."""
    missao = _validar_missao_real()
    # Eleva o limite exclusivamente dentro deste teste de estresse. O arquivo
    # de produção permanece inalterado e o monkeypatch é revertido ao final.
    monkeypatch.setattr(
        modulo_busca,
        "orcamento_exaustivo",
        max(modulo_busca.orcamento_exaustivo, CONFIGURACOES_ESPERADAS + 1),
    )

    progresso = []
    inicio = time.perf_counter()
    ultima_notificacao = {"tempo": inicio, "avaliadas": -1}

    def acompanhar_progresso(evento):
        progresso.append(evento)
        agora = time.perf_counter()
        avaliadas_agora = evento.get("avaliadas", 0)
        # Saída viva aproximadamente a cada 10 segundos, sem inundar o terminal.
        if agora - ultima_notificacao["tempo"] >= 10:
            percentual = 100 * avaliadas_agora / CONFIGURACOES_ESPERADAS
            print(
                f"Progresso M4: {avaliadas_agora:,}/"
                f"{CONFIGURACOES_ESPERADAS:,} ({percentual:.2f}%); "
                f"fase={evento.get('fase', 'busca')}.".replace(",", "."),
                flush=True,
            )
            ultima_notificacao["tempo"] = agora
            ultima_notificacao["avaliadas"] = avaliadas_agora

    resultado = investigar(
        modo="ampliada",
        texto_cifrado=MENSAGEM_CIFRADA,
        modelo="M4",
        idioma="pt",
        conhecidos=_conhecidos(),
        limite=LIMITE_CANDIDATOS,
        progresso=acompanhar_progresso,
    )
    tempo_real = time.perf_counter() - inicio

    avaliadas = resultado["combinacoes_testadas"]
    cobertura = resultado["cobertura_completa"]
    candidatos = resultado["candidatos"]
    recuperados = [c for c in candidatos if c["texto"] == TEXTO_CLARO]

    print(
        "M4 Comboio — ordem dos rotores desconhecida: "
        f"{tempo_real:.2f}s; avaliadas={avaliadas:,}/"
        f"{CONFIGURACOES_ESPERADAS:,}; cobertura completa={cobertura}; "
        f"texto esperado entre os {len(candidatos)} candidatos={bool(recuperados)}."
        .replace(",", ".")
    )

    assert resultado["modo"] == "ampliada"
    assert resultado["metodo"] == "exaustiva"
    assert resultado["espaco"]["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert avaliadas == CONFIGURACOES_ESPERADAS
    assert cobertura is True
    assert progresso, "A busca não reportou progresso."
    valores_progresso = [registro["avaliadas"] for registro in progresso]
    assert valores_progresso == sorted(valores_progresso), "O progresso diminuiu."
    assert candidatos, "A busca não devolveu candidatos."
    assert all(c.get("verificado_no_motor") is True for c in candidatos), (
        "Todos os candidatos finais devem ser verificados pelo motor Enigma real."
    )
    assert recuperados, (
        "A busca cobriu todo o escopo, mas a mensagem esperada não ficou entre os "
        f"{len(candidatos)} candidatos. Melhor candidato: {candidatos[0]['texto']!r}. "
        "Isso indica uma limitação de ranking/recuperação com esta mensagem curta; "
        "o algoritmo não foi alterado por este teste."
    )

    # A mensagem recuperada deve corresponder à chave física da missão, ou a
    # uma representação eletricamente equivalente do trecho grego + refletor.
    mapa_real = _mapa_grego_refletor(
        missao["rotor_grego"], missao["posicoes"][0], missao["refletor"], ANEIS_PRINCIPAIS
    )
    equivalentes = []
    for candidato in recuperados:
        if candidato.get("rotores") != list(missao["rotores"]):
            continue
        if candidato.get("aneis") != list(ANEIS_PRINCIPAIS):
            continue
        if candidato.get("posicoes") != "".join(missao["posicoes"][1:]):
            continue
        if not all(
            chave in candidato
            for chave in ("rotor_grego", "posicao_grega", "refletor")
        ):
            continue
        mapa_candidato = _mapa_grego_refletor(
            candidato["rotor_grego"], candidato["posicao_grega"],
            candidato["refletor"], ANEIS_PRINCIPAIS,
        )
        if mapa_candidato == mapa_real:
            equivalentes.append(candidato)

    print(
        "Configuração histórica/equivalência elétrica exata presente entre os candidatos: "
        f"{bool(equivalentes)}."
    )
    assert equivalentes, (
        "O texto correto apareceu, mas a configuração correspondente à missão ou seu mapa "
        "elétrico equivalente não apareceu entre os candidatos retornados."
    )
