"""Testes de progresso, cancelamento e das tarefas de criptoanálise (API)."""

import time

import pytest

from api import app
from criptoanalise import BuscaCancelada, atacar_posicoes
from enigma import Enigma

texto_teste = "OPCILLAZFXLQTDNLGGLEKDIZOKQKGXIEZKD"
pt157 = (
    "OATAQUEAONORTEACONTECERAOAMANHECERCONFIRMADAPORNOSSASRADASRELATORIOS"
    "DAESQUADRILHAAEREAINDICAMQUEOFORTINHAPROVISLESCOMIDASPARAOINIMIGO"
    "DESCOBRIROMENSAGEMSECRETA"
)


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    with app.test_client() as cliente_flask:
        yield cliente_flask


def esperar_estado(cliente, id_tarefa, estados_finais, limite_segundos=30):
    estado = None
    fim = time.time() + limite_segundos
    while time.time() < fim:
        resposta = cliente.get(f"/api/criptoanalise/tarefas/{id_tarefa}")
        estado = resposta.get_json()
        if estado["estado"] in estados_finais:
            return estado
        time.sleep(0.05)
    raise AssertionError(f"Tarefa não alcançou {estados_finais}: {estado}")


def test_tarefa_m3_conclui_com_resultado_compativel_com_api(cliente):
    resposta = cliente.post(
        "/api/criptoanalise/tarefas",
        json={
            "modelo": "M3",
            "mensagem": texto_teste,
            "idioma": "en",
            "limite": 5,
        },
    )
    assert resposta.status_code == 200
    criacao = resposta.get_json()
    assert criacao["total_combinacoes"] == 17576

    estado = esperar_estado(cliente, criacao["id_tarefa"], {"concluida"})
    assert estado["porcentagem"] == 100.0

    resultado = estado["resultado"]
    assert resultado["combinacoes_testadas"] == 17576
    assert len(resultado["candidatos"]) == 5
    pontuacoes = [c["pontuacao"] for c in resultado["candidatos"]]
    assert pontuacoes == sorted(pontuacoes, reverse=True)


def test_tarefa_m4_pode_ser_cancelada_no_backend(cliente):
    resposta = cliente.post(
        "/api/criptoanalise/tarefas",
        json={
            "modelo": "M4",
            "mensagem": texto_teste * 3,
            "idioma": "pt",
            "limite": 5,
        },
    )
    criacao = resposta.get_json()

    estado = None
    fim = time.time() + 10
    while time.time() < fim:
        estado = cliente.get(
            f"/api/criptoanalise/tarefas/{criacao['id_tarefa']}"
        ).get_json()
        if estado["combinacoes_testadas"] > 0:
            break
        time.sleep(0.02)
    assert estado["combinacoes_testadas"] > 0

    cancelamento = cliente.post(
        f"/api/criptoanalise/tarefas/{criacao['id_tarefa']}/cancelar"
    )
    assert cancelamento.status_code == 200

    estado = esperar_estado(cliente, criacao["id_tarefa"], {"cancelada"})
    assert "resultado" not in estado
    assert estado["combinacoes_testadas"] < estado["total_combinacoes"]

    # Cancelamento repetido e consulta após o cancelamento não podem falhar.
    assert cliente.post(
        f"/api/criptoanalise/tarefas/{criacao['id_tarefa']}/cancelar"
    ).status_code == 200
    assert cliente.get(
        f"/api/criptoanalise/tarefas/{criacao['id_tarefa']}"
    ).get_json()["estado"] == "cancelada"


def test_tarefa_inexistente_retorna_404(cliente):
    assert cliente.get("/api/criptoanalise/tarefas/nao-existe").status_code == 404
    assert (
        cliente.post("/api/criptoanalise/tarefas/nao-existe/cancelar").status_code
        == 404
    )


def test_dados_invalidos_sao_recusados_na_criacao(cliente):
    resposta = cliente.post(
        "/api/criptoanalise/tarefas",
        json={"modelo": "M5", "mensagem": "ABCDEF"},
    )
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()

    resposta = cliente.post(
        "/api/criptoanalise/tarefas",
        json={"modelo": "M3", "mensagem": "ABCDEF", "idioma": "fr"},
    )
    assert resposta.status_code == 400


def test_rota_sincrona_legada_continua_funcionando(cliente):
    resposta = cliente.post(
        "/api/criptoanalise",
        json={"modelo": "M3", "mensagem": texto_teste, "idioma": "en", "limite": 2},
    )
    assert resposta.status_code == 200
    resultado = resposta.get_json()
    assert resultado["combinacoes_testadas"] == 17576
    assert len(resultado["candidatos"]) == 2


def test_progresso_e_monotonico_e_cobre_todo_espaco():
    chamadas = []
    atacar_posicoes(
        texto_teste,
        ("I", "II", "III"),
        [1, 1, 1],
        "B",
        "pt",
        limite=3,
        progresso=lambda feitas, total: chamadas.append((feitas, total)),
    )
    assert chamadas[0] == (0, 17576)
    assert chamadas[-1] == (17576, 17576)
    feitas = [chamada[0] for chamada in chamadas]
    assert feitas == sorted(feitas)


def test_cancelamento_interrompe_a_busca_com_excecao_propria():
    verificacoes = {"n": 0}

    def cancelar():
        verificacoes["n"] += 1
        return verificacoes["n"] > 3

    with pytest.raises(BuscaCancelada):
        atacar_posicoes(
            texto_teste,
            ("I", "II", "III"),
            [1, 1, 1],
            "B",
            "pt",
            limite=3,
            cancelado=cancelar,
        )


def test_busca_longa_em_duas_etapas_recupera_configuracao_e_texto():
    cifrado = Enigma(("I", "II", "III"), (3, 19, 0), (0, 7, 13), "B", "").cifrar_texto(pt157)

    resultado = atacar_posicoes(cifrado, ("I", "II", "III"), [1, 8, 14], "B", "pt", limite=3)

    melhor = resultado["candidatos"][0]
    assert melhor["posicoes"] == "DTA"
    assert melhor["texto"] == pt157


def test_mensagem_curta_com_estrangeirismo_aparece_entre_os_candidatos():
    # 17 letras com nome próprio estrangeiro: ambiguidade estatística real.
    # A configuração correta aparece entre os 10 primeiros (rank medido: 6),
    # mas NÃO há garantia de primeiro lugar em textos tão curtos.
    texto = "EUCOMIUMHAMBURGER"
    cifrado = Enigma(("I", "II", "III"), (3, 19, 0), (0, 7, 13), "B", "").cifrar_texto(texto)

    resultado = atacar_posicoes(cifrado, ("I", "II", "III"), [1, 8, 14], "B", "pt", limite=10)

    posicoes = [c["posicoes"] for c in resultado["candidatos"]]
    assert "DTA" in posicoes