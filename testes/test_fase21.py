"""Testes da Fase 2.1: modos de jogo, conquistas, sessão e galeria."""

import pytest

from desafios import (
    missoes,
    modos,
    pontos_por_modo,
    verificar_resposta,
)


@pytest.fixture
def cliente():
    from api import app
    app.config["TESTING"] = True
    with app.test_client() as cliente_flask:
        yield cliente_flask


def test_catalogo_publico_apresenta_contexto_por_missao():
    from desafios import detalhe_publico
    for id_missao in missoes:
        detalhe = detalhe_publico(id_missao)
        assert detalhe["local"]
        assert detalhe["pais_regiao"]
        assert detalhe["periodo"]
        assert detalhe["intro"]
        assert detalhe["contexto"]
        assert detalhe["quem_participava"]
        assert detalhe["fato_verificado"]
        assert "FATO DOCUMENTADO" in detalhe["fato_verificado"]
        assert "RECONSTRUÇÃO EDUCACIONAL" in detalhe["fato_verificado"]
        assert detalhe["fontes"], id_missao
        assert all(fonte["url"].startswith("https://") for fonte in detalhe["fontes"])


def test_pontos_por_modo_crescem_com_a_dificuldade():
    missao = missoes["primeira-leitura"]
    guiado = pontos_por_modo(missao, "guiado")
    investigacao = pontos_por_modo(missao, "investigacao")
    especialista = pontos_por_modo(missao, "especialista")
    assert guiado < investigacao < especialista
    assert (guiado, investigacao, especialista) == (25, 38, 50)


def test_modo_invalido_e_recusado():
    with pytest.raises(ValueError, match="Modo inválido"):
        verificar_resposta("primeira-leitura", missoes["primeira-leitura"]["texto_claro"], "facil")
    with pytest.raises(ValueError, match="Modo inválido"):
        pontos_por_modo(missoes["primeira-leitura"], "facil")


def test_validacao_continua_igual_em_todos_os_modos():
    """O modo muda a PONTUAÇÃO, nunca a validação do motor."""
    clara = missoes["radio-do-deserto"]["texto_claro"]
    for modo in modos:
        resultado = verificar_resposta("radio-do-deserto", clara.lower() + "  ", modo)
        assert resultado["correto"] is True
        assert resultado["mensagem_decifrada"] == clara


def test_fluxo_completo_na_sessao_do_servidor(cliente):
    clara = missoes["primeira-leitura"]["texto_claro"]

    # galeria é bloqueada ANTES da conclusão.
    assert cliente.get("/api/desafios/primeira-leitura/galeria").status_code == 403

    # Conclui no modo guiado: backend calcula 25 pontos e desbloqueia.
    primeira = cliente.post(
        "/api/desafios/primeira-leitura/verificar",
        json={"resposta": "  convoia norte parte ao amanha ", "modo": "guiado"},
    ).get_json()
    assert primeira["correto"] is True
    assert primeira["primeira_conclusao"] is True
    assert primeira["pontos"] == 25
    assert primeira["nova_conquista"]["id"] == "conquista-primeira-leitura"
    assert primeira["config"]["rotores"] == ["I", "II", "III"]

    # Progresso persiste na sessão (mesmo cliente, novas requisições).
    progresso = cliente.get("/api/desafios/progresso").get_json()
    assert progresso["concluidas"]["primeira-leitura"] == {"modo": "guiado", "pontos": 25}
    assert progresso["pontos_total"] == 25
    assert progresso["conquistas"] == ["conquista-primeira-leitura"]

    # Repetir a resposta correta NÃO duplica pontos nem conquista.
    repeticao = cliente.post(
        "/api/desafios/primeira-leitura/verificar",
        json={"resposta": clara, "modo": "especialista"},
    ).get_json()
    assert repeticao["correto"] is True
    assert repeticao["primeira_conclusao"] is False
    assert repeticao["pontos"] == 0
    assert repeticao["nova_conquista"] is None

    progresso = cliente.get("/api/desafios/progresso").get_json()
    assert progresso["pontos_total"] == 25

    # galeria liberada APÓS a conclusão.
    galeria = cliente.get("/api/desafios/primeira-leitura/galeria").get_json()
    assert len(galeria["itens"]) >= 1
    for item in galeria["itens"]:
        assert item["titulo_legenda"]
        assert item["fonte_url"]
        assert item["credito_licenca"]
        assert item["tipo"] in ("historica", "atual")


def test_resposta_errada_nao_desbloqueia_nada(cliente):
    resposta = cliente.post(
        "/api/desafios/radio-do-deserto/verificar",
        json={"resposta": "TEXTOTOTALMENTEERRADO", "modo": "especialista"},
    ).get_json()
    assert resposta["correto"] is False
    assert "config" not in resposta

    progresso = cliente.get("/api/desafios/progresso").get_json()
    assert "radio-do-deserto" not in progresso["concluidas"]


def test_configuracao_guiada_fornece_config_oficial(cliente):
    config = cliente.get("/api/desafios/comboio-atlantico/configuracao-guiada").get_json()
    assert config["modelo"] == "M4"
    assert config["rotor_grego"] == "Beta"
    assert len(config["posicoes"]) == 4
    assert config["refletor"] == "Bfino"


def test_galeria_tem_fontes_e_legenda_em_todas_as_missoes(cliente):
    from desafios import galeria_de
    for id_missao in missoes:
        for item in galeria_de(id_missao):
            assert item["titulo_legenda"]
            assert item["fonte_url"].startswith("https://")
            assert item["relacao"]


def test_arquivos_de_galeria_baixados_existem():
    import os
    from desafios import galeria
    for itens in galeria.values():
        for item in itens:
            if item["arquivo"]:
                caminho = os.path.join("enigma_frontend", item["arquivo"])
                assert os.path.getsize(caminho) > 5000, caminho
