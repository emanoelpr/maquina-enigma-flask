import pytest
from enigma import Enigma

def test_m3_rejeita_refletor_fino():
    with pytest.raises(ValueError):
        Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "Bfino", "")
        
def test_m4_rejeita_refletor_normal():
    with pytest.raises(ValueError):
        Enigma(("Beta", "I", "II", "III"), (0, 0, 0, 0), (0, 0, 0, 0), "B", "")
        
def test_m4_exige_rotor_grego_na_primeira_posicao():
    with pytest.raises(ValueError):
        Enigma(("IV", "I", "II", "III"), (0, 0, 0, 0), (0, 0, 0, 0), "Bfino", "")
 
 
def test_rotor_grego_nao_pode_ser_usado_nas_posicoes_normais():
    with pytest.raises(ValueError):
        Enigma(("Beta", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
 
 
def test_rotor_desconhecido_gera_erro():
    with pytest.raises(ValueError):
        Enigma(("I", "II", "X"), (0, 0, 0), (0, 0, 0), "B", "")
        
def test_m3_rejeita_quantidade_errada_de_posicoes():
    with pytest.raises(ValueError):
        Enigma(("I", "II", "III"), (0, 0), (0, 0, 0), "B", "",)
        
def test_m3_rejeita_quantidade_errada_de_aneis():
    with pytest.raises(ValueError):
        Enigma(("I", "II", "III"), (0, 0, 0), (0, 0), "B", "",)

def test_m4_rejeita_quantidade_errada_de_posicoes():
    with pytest.raises(ValueError):
        Enigma(("Beta", "I", "II", "III"), (0, 0, 0), (0, 0, 0, 0), "Bfino", "",)

def test_m4_rejeita_quantidade_errada_de_aneis():
    with pytest.raises(ValueError):
        Enigma(("Beta", "I", "II", "III"), (0, 0, 0, 0), (0, 0, 0), "Bfino", "",)