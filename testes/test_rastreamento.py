"""Testes do rastreamento do percurso elétrico da letra (motor real)."""

from enigma import Enigma
import pytest


def configuracao_padrao():
    return ("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", ""


def test_resultado_final_igual_ao_motor_em_todas_as_letras():
    for letra in range(26):
        rastreadora = Enigma(("I", "II", "III"), (5, 10, 15), (0, 0, 0), "B", "")
        resultado, etapas = rastreadora.cifrar_com_rastreamento(letra)

        comum = Enigma(("I", "II", "III"), (5, 10, 15), (0, 0, 0), "B", "")
        assert resultado == comum.cifrar(letra), letra
        # O rastreamento não pode alterar o estado dos rotores.
        assert rastreadora.rotor_direito.posicao_rotor == comum.rotor_direito.posicao_rotor
        assert rastreadora.rotor_central.posicao_rotor == comum.rotor_central.posicao_rotor
        assert rastreadora.rotor_esquerdo.posicao_rotor == comum.rotor_esquerdo.posicao_rotor


def test_primeira_etapa_e_plugboard_de_entrada_e_ultima_e_de_saida():
    rastreadora = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "AB CD")
    resultado, etapas = rastreadora.cifrar_com_rastreamento(0)  # letra A

    assert etapas[0]["componente"] == "Plugboard (entrada)"
    assert etapas[0]["antes"] == 0
    assert etapas[0]["depois"] == 1  # A entra, B sai do plugboard
    assert etapas[-1]["componente"] == "Plugboard (saída)"
    assert etapas[-1]["depois"] == resultado


def test_caminho_inclui_ida_volta_e_refletor_na_ordem():
    _, etapas = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "").cifrar_com_rastreamento(0)

    componentes = [etapa["componente"] for etapa in etapas]
    assert componentes == [
        "Plugboard (entrada)",
        "Rotor III", "Rotor II", "Rotor I",
        "Refletor B",
        "Rotor I", "Rotor II", "Rotor III",
        "Plugboard (saída)",
    ]
    sentidos = [etapa.get("sentido") for etapa in etapas[1:4]]
    assert sentidos == ["ida", "ida", "ida"]
    sentidos_volta = [etapa.get("sentido") for etapa in etapas[5:8]]
    assert sentidos_volta == ["volta", "volta", "volta"]


def test_nenhuma_letra_cifra_para_si_mesma_no_rastreamento():
    for letra in range(26):
        _, etapas = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "").cifrar_com_rastreamento(letra)
        assert etapas[-1]["depois"] != letra


def test_avanco_e_duplo_passo_registrados_nas_posicoes():
    # Partindo de A-D-U (0, 3, 20): A-E-V, A-F-W, B-F-X (duplo passo no 3º).
    maquina = Enigma(("I", "II", "III"), (0, 3, 20), (0, 0, 0), "B", "")
    esperado = [(0, 3, 21), (0, 4, 22), (1, 5, 23)]
    observado = []
    for _ in range(3):
        _, etapas = maquina.cifrar_com_rastreamento(0)
        # Posição registrada na etapa do rotor DIREITO (primeira após o plugboard)
        observado.append((
            etapas[3]["posicao"],   # rotor esquerdo (índice: plug, dir, cen, esq)
            etapas[2]["posicao"],   # rotor central
            etapas[1]["posicao"],   # rotor direito
        ))
    assert observado == esperado


def test_m4_registra_rotor_grego_que_nao_avanca():
    maquina = Enigma(("Beta", "I", "II", "III"), (7, 0, 0, 0), (0, 0, 0, 0), "Bfino", "")
    componentes = []
    for _ in range(5):
        resultado, etapas = maquina.cifrar_com_rastreamento(0)
        componentes.append(etapas)
        assert maquina.rotor_grego.posicao_rotor == 7

    etapas = componentes[0]
    gregos = [e for e in etapas if e["componente"] == "Rotor grego Beta"]
    assert len(gregos) == 2
    assert gregos[0]["sentido"] == "ida"
    assert gregos[1]["sentido"] == "volta"
    # O grego não avança: ida e volta ocorrem na MESMA posição.
    assert gregos[0]["posicao"] == gregos[1]["posicao"] == 7
    assert etapas[4]["componente"] == "Rotor grego Beta"
    assert etapas[5]["componente"].startswith("Refletor")


def test_sequencia_helloworld_corresponde_ao_vetor_conhecido():
    config = ("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", ""

    rastreadora = Enigma(*config)
    letras = []
    for letra in "HELLOWORLD":
        resultado, _ = rastreadora.cifrar_com_rastreamento(ord(letra) - ord("A"))
        letras.append(chr(resultado + ord("A")))

    assert "".join(letras) == "ILBDAAMTAZ"

    comum = Enigma(*config)
    assert comum.cifrar_texto("HELLOWORLD") == "ILBDAAMTAZ"


def test_sequencia_de_letras_igual_ao_cifrar_texto():
    config = ("IV", "II", "V"), (3, 19, 0), (0, 7, 13), "C", "AV BS"
    texto = "ATAQUEAOAMANHECER"

    rastreadora = Enigma(*config)
    letras = []
    for letra in texto:
        resultado, _ = rastreadora.cifrar_com_rastreamento(ord(letra) - ord("A"))
        letras.append(chr(resultado + ord("A")))

    comum = Enigma(*config)
    assert "".join(letras) == comum.cifrar_texto(texto)


@pytest.fixture
def cliente():
    from api import app
    app.config["TESTING"] = True
    with app.test_client() as cliente_flask:
        yield cliente_flask


def test_api_percurso_devolve_etapas_e_posicoes_finais(cliente):
    resposta = cliente.post(
        "/api/percurso",
        json={
            "modelo": "M3",
            "letra": "A",
            "rotores": ["I", "II", "III"],
            "posicoes": ["A", "A", "A"],
            "aneis": [1, 1, 1],
            "refletor": "B",
            "plugboard": "",
        },
    )
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados["letra_entrada"] == "A"
    assert dados["letra_saida"] == dados["etapas"][-1]["depois"]
    assert len(dados["posicoes_finais"]) == 3
    assert dados["posicoes_finais"] == ["A", "A", "B"]  # rotor direito avançou


def test_api_percurso_letra_final_igual_ao_endpoint_cifrar(cliente):
    corpo = {
        "modelo": "M3",
        "rotores": ["IV", "II", "V"],
        "posicoes": ["D", "T", "C"],
        "aneis": [1, 8, 14],
        "refletor": "C",
        "plugboard": "AV BS",
    }
    percurso = cliente.post("/api/percurso", json={**corpo, "letra": "H"}).get_json()
    cifrar = cliente.post("/api/cifrar", json={**corpo, "mensagem": "H"}).get_json()
    assert percurso["letra_saida"] == cifrar["resultado"]


def test_api_percurso_rejeita_letra_invalida(cliente):
    for letra in ("", "AB", "1", "ç"):
        resposta = cliente.post("/api/percurso", json={"letra": letra})
        assert resposta.status_code == 400
        assert "erro" in resposta.get_json()


def test_api_percurso_m4_inclui_rotor_grego(cliente):
    resposta = cliente.post(
        "/api/percurso",
        json={
            "modelo": "M4",
            "letra": "X",
            "rotores": ["IV", "II", "V"],
            "posicoes": ["L", "D", "T", "C"],
            "aneis": [1, 8, 14, 21],
            "refletor": "B-Thin",
            "rotor_grego": "Beta",
        },
    )
    assert resposta.status_code == 200
    dados = resposta.get_json()
    componentes = [etapa["componente"] for etapa in dados["etapas"]]
    assert "Rotor grego Beta" in componentes
    assert "Refletor Bfino" in componentes
    assert len(dados["posicoes_finais"]) == 4
    assert dados["posicoes_finais"][0] == "L"  # grego não avança