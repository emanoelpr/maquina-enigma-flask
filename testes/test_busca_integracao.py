"""Testes adicionais de integração da busca automática M3/M4."""
import time

import pytest

from api import app
from busca_configuracoes import descrever_espaco


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_escopo_avancado_m4_sem_parametros_aceita_triagem_ampla(cliente):
    resposta = cliente.post(
        "/api/criptoanalise/escopo",
        json={"modo": "avancada", "modelo": "M4", "mensagem": "AAAA", "idioma": "pt"},
    )
    assert resposta.status_code == 200, resposta.get_json()
    dados = resposta.get_json()
    assert dados["configuracoes_exaustivas"] == 614_175_744
    assert dados["orcamento"] == 650_000_000
    assert dados["dentro_do_orcamento"] is True
    assert dados["heuristica"] is True


def test_escopo_ampliado_m4_sem_parametros_nao_finge_ser_viavel(cliente):
    resposta = cliente.post(
        "/api/criptoanalise/escopo",
        json={"modo": "ampliada", "modelo": "M4", "mensagem": "AAAA", "idioma": "pt"},
    )
    assert resposta.status_code == 400
    assert "acima do limite" in resposta.get_json()["erro"]


def test_escopo_configurado_m3_com_chave_conhecida(cliente):
    resposta = cliente.post(
        "/api/criptoanalise/escopo",
        json={
            "modo": "configurada", "modelo": "M3", "mensagem": "AAAA", "idioma": "pt",
            "rotores": ["I", "II", "III"], "aneis": [1, 1, 1], "refletor": "B",
            "plugboard_modo": "vazio",
        },
    )
    assert resposta.status_code == 200, resposta.get_json()
    assert resposta.get_json()["configuracoes_exaustivas"] == 17_576


def test_descricao_orcamento_diferencia_busca_exaustiva_e_avancada():
    escopo = descrever_espaco("M4", {"plugboard_modo": "vazio"}, "avancada")
    assert escopo["orcamento"] == 650_000_000
    assert escopo["dentro_do_orcamento"] is True
    assert escopo["configuracoes_exaustivas"] == 614_175_744
