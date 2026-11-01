import re

from enigma import Enigma
from criptoanalise import atacar_posicoes

rotores = ("I", "II", "III")
aneis = [1, 1, 1]

texto_claro = re.sub(r"[^A-Z]", "", """
A ENIGMA FOI UMA FAMILIA DE MAQUINAS DE CIFRAR ELETROMECANICAS USADAS NA PRIMEIRA METADE DO SECULO XX.
A CADA TECLA PRESSIONADA OS ROTORES GIRAVAM E A SUBSTITUICAO MUDAVA, DE MODO QUE A MESMA LETRA NUNCA ERA CIFRADA DA MESMA FORMA DUAS VEZES SEGUIDAS.
O SINAL PERCORRIA O PLUGBOARD, OS TRES ROTORES, O REFLETOR E VOLTAVA ANTES DE ACENDER UMA LAMPADA NO PAINEL.
OS ANALISTAS DE BLETCHLEY PARK EXPLORAVAM OS HABITOS DOS OPERADORES E O FATO DE NENHUMA LETRA PODER SER CIFRADA COMO ELA MESMA PARA RECUPERAR AS CONFIGURACOES DIARIAS.
""")

def test_busca_escontra_a_posicao_correta_e_recupera_o_texto():
    # Posições D, R, J (3, 17, 9)
    cifrado = Enigma(rotores, (3, 17, 9), (0, 0, 0), "B", "").cifrar_texto(texto_claro)
    
    resultado = atacar_posicoes(cifrado, rotores, aneis, "B", "pt", limite = 5)
    
    posicoes = [candidato["posicoes"] for candidato in resultado["candidatos"]]
    
    assert "DRJ" in posicoes
    
    candidato = resultado["candidatos"][posicoes.index("DRJ")]
    assert candidato["texto"] == texto_claro
    
def test_busca_inclui_o_tempo_gasto():
    resultado = atacar_posicoes("OPCILLAZFXLQTDNLGGLEKDIZOKQKGXIEZKD", rotores, aneis, "B", "en", limite=1)
    
    assert resultado["tempo_segundos"] >= 0