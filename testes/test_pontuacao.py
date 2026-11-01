"""Regressões da pontuação linguística com mensagens genéricas.

As mensagens abaixo não pertencem às listas de palavras frequentes nem
foram usadas para ajustar as tabelas: o objetivo é garantir que a busca
recupera a configuração correta por qualidade linguística geral, e não
por coincidência com um exemplo específico (como HELLOWORLD).
"""

from criptoanalise import atacar_posicoes
from enigma import Enigma
from pontuacao import pontuar_idioma, trigramas

pt_claro = "AMANHECEUNEBLINANABAIAEOSBARCOSAGUARDARAMOFAROLACENDER"
en_claro = (
    "THEFOGLIFTEDSLOWLYANDTHEOLDFERRYWAITEDFORTHELIGHTHOUSETO"
    "BLINKTWICEBEFORELEAVINGTHEHARBOR"
)


def test_mensagem_generica_pt_recupera_configuracao_no_topo():
    # I-II-III, posições AAA, anéis 1-1-1, refletor B
    cifrado = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "").cifrar_texto(pt_claro)

    resultado = atacar_posicoes(cifrado, ("I", "II", "III"), [1, 1, 1], "B", "pt", limite=3)

    melhor = resultado["candidatos"][0]
    assert melhor["posicoes"] == "AAA", melhor["posicoes"]
    assert melhor["texto"] == pt_claro


def test_mensagem_generica_en_recupera_configuracao_no_topo():
    # III-I-II, posições F-K-P (5, 10, 15), anéis 1-1-1, refletor B
    cifrado = Enigma(("III", "I", "II"), (5, 10, 15), (0, 0, 0), "B", "").cifrar_texto(en_claro)

    resultado = atacar_posicoes(cifrado, ("III", "I", "II"), [1, 1, 1], "B", "en", limite=3)

    melhor = resultado["candidatos"][0]
    assert melhor["posicoes"] == "FKP", melhor["posicoes"]
    assert melhor["texto"] == en_claro


def test_idioma_influencia_a_pontuacao():
    texto_pt = "QUEESTACOMUMASPORTASDASAQUIDAVELHA"
    texto_en = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"

    assert pontuar_idioma(texto_pt, "pt") > pontuar_idioma(texto_pt, "en")
    assert pontuar_idioma(texto_en, "en") > pontuar_idioma(texto_en, "pt")


def test_tabelas_tem_formato_corpus():
    for idioma in ("pt", "en"):
        tabela = trigramas[idioma]
        assert len(tabela) == 300, (idioma, len(tabela))
        assert all(isinstance(peso, int) and 1 <= peso <= 10 for peso in tabela.values())
