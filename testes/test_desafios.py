"""Testes da seção Desafios históricos.

Garante que cada missão é resolvida pelo MOTOR REAL (round-trip), que o
catálogo público não vaza a resposta nem a configuração, que as dicas são
progressivas e que a API funciona de ponta a ponta.
"""

import pytest

from desafios import (
    dicas,
    missoes,
    _maquina_de,
    catalogo_publico,
    detalhe_publico,
    obter_dicas,
    verificar_resposta,
)
from enigma import Enigma


@pytest.mark.parametrize("id_missao", sorted(missoes))
def test_cada_missao_round_trip_pelo_motor_real(id_missao):
    """A configuração oficial da missão decifra a mensagem cifrada."""
    missao = missoes[id_missao]
    decifrado = _maquina_de(missao).cifrar_texto(missao["mensagem_cifrada"])
    assert decifrado == missao["texto_claro"]


@pytest.mark.parametrize("id_missao", sorted(missoes))
def test_configuracoes_sao_validas_para_o_modelo(id_missao):
    """A máquina da missão é criada sem erro e respeita as regras do modelo."""
    missao = missoes[id_missao]
    maquina = _maquina_de(missao)
    if missao["modelo"] == "M4":
        assert maquina.rotor_grego is not None
        assert maquina.nome_refletor in ("Bfino", "Cfino")
    else:
        assert maquina.rotor_grego is None
        assert maquina.nome_refletor in ("B", "C")


def test_m4_missao_preserva_rotor_grego_estatico():
    """Na missão M4, o rotor grego permanece na posição configurada
    (comportamento histórico: ele não avança durante a mensagem)."""
    missao = missoes["comboio-atlantico"]
    maquina = _maquina_de(missao)
    posicao_inicial = maquina.rotor_grego.posicao_rotor

    maquina.cifrar_texto("M" * 30)

    assert maquina.rotor_grego.posicao_rotor == posicao_inicial


def test_catalogo_publico_nao_vaza_resposta_nem_configuracao():
    for item in catalogo_publico():
        assert "texto_claro" not in item
        assert "config" not in item
        assert "rotores" not in item
        assert "posicoes" not in item
    detalhe = detalhe_publico("primeira-leitura")
    assert "texto_claro" not in detalhe


def test_verificar_resposta_correta_ignora_espacos_e_caixa():
    missao = missoes["primeira-leitura"]
    resultado = verificar_resposta(
        "primeira-leitura", "  convoia norte parte ao amanha  "
    )
    assert resultado["correto"] is True
    assert resultado["config"]["rotores"] == list(missao["rotores"])


def test_verificar_resposta_errada_e_vazia():
    resultado = verificar_resposta("primeira-leitura", "TEXTOERRADOCOMPLETO")
    assert resultado["correto"] is False
    assert "config" not in resultado

    vazio = verificar_resposta("primeira-leitura", "   ")
    assert vazio["correto"] is False


def test_dicas_sao_progressivas_e_validadas():
    assert obter_dicas("primeira-leitura", 1) == dicas["primeira-leitura"][:1]
    assert len(obter_dicas("radio-do-deserto", 3)) == 3

    with pytest.raises(ValueError, match="entre 1 e 3"):
        obter_dicas("primeira-leitura", 0)
    with pytest.raises(ValueError, match="entre 1 e 3"):
        obter_dicas("primeira-leitura", 4)
    with pytest.raises(ValueError, match="não encontrada"):
        obter_dicas("missao-inexistente", 1)


def test_vetor_referencia_helloworld_preservado():
    cifradora = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
    decifradora = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
    cifrado = cifradora.cifrar_texto("HELLOWORLD")
    assert cifrado == "ILBDAAMTAZ"
    assert decifradora.cifrar_texto(cifrado) == "HELLOWORLD"


@pytest.fixture
def cliente():
    from api import app
    app.config["TESTING"] = True
    with app.test_client() as cliente_flask:
        yield cliente_flask


def test_api_desafios_e2e(cliente):
    resposta = cliente.get("/api/desafios")
    assert resposta.status_code == 200
    missoes = resposta.get_json()["missoes"]
    assert len(missoes) == 4
    assert all("texto_claro" not in missao for missao in missoes)

    dica = cliente.post(
        "/api/desafios/comboio-atlantico/dica", json={"nivel": 2}
    )
    assert dica.status_code == 200
    assert len(dica.get_json()["dicas"]) == 2

    assert (
        cliente.post("/api/desafios/comboio-atlantico/dica", json={"nivel": 9}).status_code
        == 400
    )
    assert (
        cliente.get("/api/desafios/nao-existe").status_code == 404
    )

    clara = missoes["radio-do-deserto"]["texto_claro"]
    verificacao = cliente.post(
        "/api/desafios/radio-do-deserto/verificar",
        json={"resposta": clara.lower()},
    )
    assert verificacao.status_code == 200
    dados = verificacao.get_json()
    assert dados["correto"] is True
    assert dados["config"]["refletor"] == "C"
