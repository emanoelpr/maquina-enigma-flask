"""Bateria isolada de confiabilidade para a criptoanálise M4.

Os testes rápidos verificam os fixtures, a cobertura matemática e o cancelamento.
As buscas exaustivas de 614.175.744 configurações ficam desativadas por padrão.

Windows PowerShell — suíte rápida:
    python -m pytest testes/test_bateria_confiabilidade_m4.py -q -s

Executar apenas um cenário pesado:
    $env:ENIGMA_TESTE_M4_BATERIA="1"
    $env:ENIGMA_TESTE_M4_CASO="comboio-real"
    python -m pytest "testes/test_bateria_confiabilidade_m4.py::test_busca_m4_exaustiva_e_registra_confiabilidade" -q -s
    Remove-Item Env:ENIGMA_TESTE_M4_BATERIA
    Remove-Item Env:ENIGMA_TESTE_M4_CASO

Executar todos os cenários pesados (cada um pode levar muitos minutos):
    $env:ENIGMA_TESTE_M4_BATERIA="1"
    python -m pytest testes/test_bateria_confiabilidade_m4.py -q -s
    Remove-Item Env:ENIGMA_TESTE_M4_BATERIA

Opcionalmente, a bateria grava/atualiza o relatório JSON em:
    testes/relatorios/relatorio_confiabilidade_m4.json

Nenhum algoritmo ou arquivo de produção é alterado por este teste.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

import busca_configuracoes as modulo_busca
from busca_configuracoes import descrever_espaco, investigar
from criptoanalise import BuscaCancelada
from desafios import _maquina_de, missoes
from enigma import Enigma


ANEIS_PRINCIPAIS = (8, 14, 21)
PLUGBOARD = ""
TOTAL_POSICOES_PRINCIPAIS = 26 ** 3
CONFIGURACOES_ESPERADAS = 8 * 7 * 6 * 2 * 2 * 26 * TOTAL_POSICOES_PRINCIPAIS
LIMITE_CANDIDATOS = 100
ENV_BATERIA = "ENIGMA_TESTE_M4_BATERIA"
ENV_CASO = "ENIGMA_TESTE_M4_CASO"
RELATORIO = Path(__file__).resolve().parent / "relatorios" / "relatorio_confiabilidade_m4.json"

# Todos usam os mesmos anéis conhecidos (8-14-21) e plugboard vazio, mas
# variam o texto, a ordem dos rotores, o rotor grego, o refletor e as posições.
# O primeiro é a missão real; os outros são mensagens sintéticas cifradas pelo motor.
CASOS = [
    {
        "id": "comboio-real",
        "descricao": "Missão Comboio no Atlântico do catálogo",
        "texto_claro": "SUBMARINOSPARTEMDOPORTOANOITE",
        "rotores": ("VI", "II", "VIII"),
        "rotor_grego": "Beta",
        "refletor": "Bfino",
        "posicao_grega": "S",
        "posicoes_principais": "DTC",
        "aneis_principais": ANEIS_PRINCIPAIS,
    },
    {
        "id": "gamma-cfino",
        "descricao": "Mensagem sintética com Gamma e refletor Cfino",
        "texto_claro": "RELATORIOCONFIRMADOTRANSMITIDOANTESDOAMANHECER",
        "rotores": ("VIII", "V", "III"),
        "rotor_grego": "Gamma",
        "refletor": "Cfino",
        "posicao_grega": "M",
        "posicoes_principais": "LQF",
        "aneis_principais": ANEIS_PRINCIPAIS,
    },
    {
        "id": "beta-ordem-alternativa",
        "descricao": "Mensagem sintética com ordem alternativa e Beta",
        "texto_claro": "UNIDADESDEVEMAGUARDARONOVOSINALANTESDEALTERARAPOSICAO",
        "rotores": ("IV", "VII", "I"),
        "rotor_grego": "Beta",
        "refletor": "Bfino",
        "posicao_grega": "R",
        "posicoes_principais": "HXN",
        "aneis_principais": ANEIS_PRINCIPAIS,
    },
]


def _posicoes_numericas(posicoes: str) -> tuple[int, ...]:
    return tuple(ord(letra) - ord("A") for letra in posicoes)


def _gerar_cifra(caso: dict) -> str:
    """Gera a mensagem com o motor Enigma real, de forma independente da busca."""
    maquina = Enigma(
        rotores=(caso["rotor_grego"], *caso["rotores"]),
        posicoes_rotores=(
            ord(caso["posicao_grega"]) - ord("A"),
            *_posicoes_numericas(caso["posicoes_principais"]),
        ),
        configuracoes_anel=(0, *(anel - 1 for anel in caso["aneis_principais"])),
        nome_refletor=caso["refletor"],
        conexoes_plugboard=PLUGBOARD,
    )
    cifra = maquina.cifrar_texto(caso["texto_claro"])
    assert len(cifra) == len(caso["texto_claro"])
    return cifra


def _conhecidos(caso: dict) -> dict:
    """Deixa ordem, rotor grego, refletor e posições desconhecidos."""
    return {
        "aneis": tuple(caso["aneis_principais"]),
        "plugboard_modo": "vazio",
        "plugboard": PLUGBOARD,
    }


def _mapa_grego_refletor(grego: str, posicao_grega: str, refletor: str,
                          ordem_rotores: tuple[str, ...], aneis: tuple[int, ...]) -> tuple[int, ...]:
    """Calcula o mapa composto Greek→refletor fino→Greek com o motor real."""
    maquina = Enigma(
        rotores=(grego, *ordem_rotores),
        posicoes_rotores=(ord(posicao_grega) - ord("A"), 0, 0, 0),
        configuracoes_anel=(0, *(anel - 1 for anel in aneis)),
        nome_refletor=refletor,
        conexoes_plugboard="",
    )
    rotor = maquina.rotor_grego
    return tuple(
        rotor.cifrar_reverso(
            maquina.refletor.cifrar(rotor.cifrar_direto(letra))
        )
        for letra in range(26)
    )


def _validar_fixture(caso: dict) -> str:
    """Valida a cifra em round-trip; a mensagem não vem pré-cifrada no teste."""
    assert caso["aneis_principais"] == ANEIS_PRINCIPAIS
    cifra = _gerar_cifra(caso)
    maquina_decifradora = Enigma(
        rotores=(caso["rotor_grego"], *caso["rotores"]),
        posicoes_rotores=(
            ord(caso["posicao_grega"]) - ord("A"),
            *_posicoes_numericas(caso["posicoes_principais"]),
        ),
        configuracoes_anel=(0, *(anel - 1 for anel in caso["aneis_principais"])),
        nome_refletor=caso["refletor"],
        conexoes_plugboard=PLUGBOARD,
    )
    assert maquina_decifradora.cifrar_texto(cifra) == caso["texto_claro"]

    if caso["id"] == "comboio-real":
        missao = missoes["comboio-atlantico"]
        assert cifra == missao["mensagem_cifrada"]
        assert caso["texto_claro"] == missao["texto_claro"]
        assert tuple(missao["aneis"][1:]) == ANEIS_PRINCIPAIS
    return cifra


def _encontrar_equivalencia(candidatos: list[dict], caso: dict) -> tuple[bool, bool, dict | None]:
    """Devolve (configuração exata, mapa elétrico equivalente, candidato-base)."""
    mapa_real = _mapa_grego_refletor(
        caso["rotor_grego"], caso["posicao_grega"], caso["refletor"],
        tuple(caso["rotores"]), tuple(caso["aneis_principais"]),
    )
    exata = False
    equivalente = False
    exemplo = None

    for candidato in candidatos:
        if candidato.get("texto") != caso["texto_claro"]:
            continue
        # Comparar a parte principal evita classificar como equivalente uma
        # simples coincidência de texto em uma mensagem finita.
        if candidato.get("rotores") != list(caso["rotores"]):
            continue
        if candidato.get("aneis") != list(caso["aneis_principais"]):
            continue
        if candidato.get("posicoes") != caso["posicoes_principais"]:
            continue
        if not all(k in candidato for k in ("rotor_grego", "posicao_grega", "refletor")):
            continue

        mapa_candidato = _mapa_grego_refletor(
            candidato["rotor_grego"], candidato["posicao_grega"],
            candidato["refletor"], tuple(caso["rotores"]),
            tuple(caso["aneis_principais"]),
        )
        if mapa_candidato == mapa_real:
            equivalente = True
            exemplo = candidato
        if (
            candidato["rotor_grego"] == caso["rotor_grego"]
            and candidato["posicao_grega"] == caso["posicao_grega"]
            and candidato["refletor"] == caso["refletor"]
        ):
            exata = True
            exemplo = candidato

    return exata, equivalente, exemplo


def _salvar_relatorio(registro: dict) -> None:
    """Mescla o resultado deste cenário ao JSON da bateria, sem perder os outros."""
    RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    dados = {"descricao": "Bateria de confiabilidade da criptoanálise M4",
             "escopo_por_caso": CONFIGURACOES_ESPERADAS, "casos": {}}
    if RELATORIO.exists():
        try:
            anterior = json.loads(RELATORIO.read_text(encoding="utf-8"))
            if isinstance(anterior, dict) and isinstance(anterior.get("casos"), dict):
                dados["casos"].update(anterior["casos"])
        except (OSError, json.JSONDecodeError):
            # Um relatório anterior inválido não deve mascarar o teste atual.
            pass
    dados["casos"][registro["id"]] = registro
    RELATORIO.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_escopo_de_cada_caso_tem_614_milhoes_de_configuracoes():
    """Teste rápido: confirma que todos os casos usam exatamente o mesmo escopo."""
    assert CONFIGURACOES_ESPERADAS == 614_175_744
    for caso in CASOS:
        cifra = _validar_fixture(caso)
        espaco = descrever_espaco("M4", _conhecidos(caso), "ampliada")
        assert len(cifra) == len(caso["texto_claro"])
        assert espaco["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
        assert espaco["heuristica"] is False
        assert espaco["dentro_do_orcamento"] is False
    print(
        "Fixtures M4 validados pelo motor real: "
        + ", ".join(f"{c['id']} ({len(c['texto_claro'])} letras)" for c in CASOS)
        + f"; escopo exaustivo por caso={CONFIGURACOES_ESPERADAS:,}.".replace(",", ".")
    )


@pytest.mark.parametrize("caso", CASOS, ids=[caso["id"] for caso in CASOS])
def test_mensagem_de_cada_caso_e_gerada_e_decifrada_pelo_motor_real(caso):
    cifra = _validar_fixture(caso)
    assert cifra
    print(f"Fixture {caso['id']}: {len(cifra)} letras; round-trip do motor real OK.")


def test_cancelamento_da_bateria_m4_para_apos_um_bloco(monkeypatch):
    """Teste rápido de cancelamento real; não percorre o espaço completo."""
    caso = CASOS[0]
    _validar_fixture(caso)
    monkeypatch.setattr(
        modulo_busca, "orcamento_exaustivo",
        max(modulo_busca.orcamento_exaustivo, CONFIGURACOES_ESPERADAS + 1),
    )
    chamadas = {"n": 0}

    def cancelar_apos_bloco() -> bool:
        chamadas["n"] += 1
        return chamadas["n"] >= 2

    inicio = time.perf_counter()
    with pytest.raises(BuscaCancelada) as capturada:
        investigar(
            modo="ampliada", texto_cifrado=_gerar_cifra(caso), modelo="M4",
            idioma="pt", conhecidos=_conhecidos(caso), limite=LIMITE_CANDIDATOS,
            cancelado=cancelar_apos_bloco,
        )
    tempo = time.perf_counter() - inicio
    avaliadas = capturada.value.combinacoes_testadas
    assert chamadas["n"] >= 2
    assert avaliadas == TOTAL_POSICOES_PRINCIPAIS
    assert 0 < avaliadas < CONFIGURACOES_ESPERADAS
    print(
        f"Cancelamento M4: {tempo:.2f}s; {avaliadas:,}/"
        f"{CONFIGURACOES_ESPERADAS:,} configurações; interrupção confirmada."
        .replace(",", ".")
    )


@pytest.mark.parametrize("caso", CASOS, ids=[caso["id"] for caso in CASOS])
def test_busca_m4_exaustiva_e_registra_confiabilidade(caso, monkeypatch):
    """Busca pesada: cobertura total, ranking, tempo e equivalência elétrica."""
    if os.environ.get(ENV_BATERIA) != "1":
        pytest.skip(f"Busca pesada desativada; defina {ENV_BATERIA}=1 para habilitar.")
    caso_solicitado = os.environ.get(ENV_CASO)
    if caso_solicitado and caso_solicitado != caso["id"]:
        pytest.skip(f"Executando apenas {caso_solicitado!r}, não {caso['id']!r}.")

    cifra = _validar_fixture(caso)
    espaco = descrever_espaco("M4", _conhecidos(caso), "ampliada")
    assert espaco["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS

    # Aumenta o limite só neste teste, via monkeypatch. O módulo de produção
    # volta automaticamente ao orçamento normal ao fim do teste.
    monkeypatch.setattr(
        modulo_busca, "orcamento_exaustivo",
        max(modulo_busca.orcamento_exaustivo, CONFIGURACOES_ESPERADAS + 1),
    )

    eventos_progresso = []
    ultimo_aviso = {"hora": time.perf_counter()}

    def progresso(evento: dict) -> None:
        avaliadas = int(evento.get("avaliadas", 0))
        if not eventos_progresso or avaliadas >= eventos_progresso[-1]["avaliadas"]:
            eventos_progresso.append({
                "avaliadas": avaliadas,
                "fase": str(evento.get("fase", "busca")),
            })
        agora = time.perf_counter()
        if agora - ultimo_aviso["hora"] >= 30:
            percentual = 100 * avaliadas / CONFIGURACOES_ESPERADAS
            print(
                f"\n[{caso['id']}] progresso: {avaliadas:,}/"
                f"{CONFIGURACOES_ESPERADAS:,} ({percentual:.2f}%), "
                f"fase={evento.get('fase', 'busca')}".replace(",", "."),
                flush=True,
            )
            ultimo_aviso["hora"] = agora

    inicio = time.perf_counter()
    resultado = investigar(
        modo="ampliada", texto_cifrado=cifra, modelo="M4", idioma="pt",
        conhecidos=_conhecidos(caso), limite=LIMITE_CANDIDATOS,
        progresso=progresso,
    )
    tempo = time.perf_counter() - inicio

    candidatos = resultado["candidatos"]
    ranking_texto = next(
        (i for i, candidato in enumerate(candidatos, start=1)
         if candidato.get("texto") == caso["texto_claro"]),
        None,
    )
    config_exata, mapa_equivalente, exemplo_equivalente = _encontrar_equivalencia(
        candidatos, caso
    )
    rank_config = None
    if exemplo_equivalente is not None:
        rank_config = next(
            (i for i, c in enumerate(candidatos, start=1) if c is exemplo_equivalente),
            None,
        )

    registro = {
        "id": caso["id"],
        "descricao": caso["descricao"],
        "texto_claro": caso["texto_claro"],
        "mensagem_cifrada": cifra,
        "comprimento_mensagem": len(cifra),
        "configuracao_original": {
            "modelo": "M4",
            "rotores": list(caso["rotores"]),
            "rotor_grego": caso["rotor_grego"],
            "refletor": caso["refletor"],
            "posicao_grega": caso["posicao_grega"],
            "posicoes_principais": caso["posicoes_principais"],
            "aneis_principais": list(caso["aneis_principais"]),
            "plugboard": PLUGBOARD,
        },
        "configuracoes_esperadas": CONFIGURACOES_ESPERADAS,
        "configuracoes_avaliadas": resultado["combinacoes_testadas"],
        "cobertura_completa": resultado["cobertura_completa"],
        "tempo_segundos_externo": round(tempo, 3),
        "tempo_segundos_algoritmo": resultado.get("tempo_segundos"),
        "candidatos_retornados": len(candidatos),
        "ranking_texto_correto": ranking_texto,
        "texto_no_top_10": ranking_texto is not None and ranking_texto <= 10,
        "texto_no_top_25": ranking_texto is not None and ranking_texto <= 25,
        "texto_no_top_100": ranking_texto is not None and ranking_texto <= 100,
        "configuracao_fisica_exata_no_top_100": config_exata,
        "mapa_eletrico_equivalente_no_top_100": mapa_equivalente,
        "ranking_configuracao_equivalente": rank_config,
        "candidatos_verificados_pelo_motor_real": all(
            c.get("verificado_no_motor") is True for c in candidatos
        ),
        "progresso_final_observado": eventos_progresso[-1]["avaliadas"] if eventos_progresso else None,
        "eventos_progresso": len(eventos_progresso),
    }
    _salvar_relatorio(registro)

    print(
        f"\nBATERIA M4 — {caso['id']}: {tempo:.2f}s; "
        f"cobertura={resultado['combinacoes_testadas']:,}/"
        f"{CONFIGURACOES_ESPERADAS:,} ({resultado['cobertura_completa']}); "
        f"ranking do texto={ranking_texto}; "
        f"top10={registro['texto_no_top_10']}, "
        f"top25={registro['texto_no_top_25']}, "
        f"top100={registro['texto_no_top_100']}; "
        f"configuração exata={config_exata}; mapa equivalente={mapa_equivalente}."
        .replace(",", "."),
        flush=True,
    )
    print(f"Relatório JSON atualizado: {RELATORIO}", flush=True)

    assert resultado["modo"] == "ampliada"
    assert resultado["metodo"] == "exaustiva"
    assert resultado["espaco"]["configuracoes_exaustivas"] == CONFIGURACOES_ESPERADAS
    assert resultado["combinacoes_testadas"] == CONFIGURACOES_ESPERADAS
    assert resultado["cobertura_completa"] is True
    assert eventos_progresso, "A busca não informou progresso."
    progresso_contagens = [evento["avaliadas"] for evento in eventos_progresso]
    assert progresso_contagens == sorted(progresso_contagens), "O progresso diminuiu."
    assert candidatos, "A busca não retornou candidatos."
    assert registro["candidatos_verificados_pelo_motor_real"], (
        "Um ou mais candidatos não foram verificados pelo motor Enigma real."
    )
    assert ranking_texto is not None, (
        f"Texto correto não apareceu entre os {len(candidatos)} candidatos. "
        f"Relatório salvo em {RELATORIO}. Isso é uma falha de recuperação/ranking, "
        "não uma falha de cobertura exaustiva."
    )
    assert mapa_equivalente, (
        "O texto foi recuperado, mas não apareceu no top 100 uma configuração com a "
        "mesma ordem/posições principais e mapa elétrico Greek+refletor equivalente. "
        f"Relatório salvo em {RELATORIO}."
    )
