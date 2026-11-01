import pytest
from rotor import Rotor
from enigma import Enigma

# Primeiro teste, com Rotor I com Anel A. O entalhe Q tem que ser True
def test_entalhe_do_rotor_1_com_anel_A():
    rotor = Rotor.criar_rotor(
        nome="I",
        posicao_rotor=ord("Q") - 65,
        configuracao_anel=ord("A") - 65,
    )
    
    assert rotor.esta_na_posicao_do_entalhe()

def test_entalhe_do_rotor_1_com_anel_B_continua_em_Q():
    rotor = Rotor.criar_rotor(
        nome = "I",
        posicao_rotor = ord("Q") - 65,
        configuracao_anel = ord("B") - 65,
    )
    
    assert rotor.esta_na_posicao_do_entalhe()
    
def test_entalhe_do_rotor_1_com_anel_B_nao_dispara_em_R():
    rotor = Rotor.criar_rotor(
        nome = "I",
        posicao_rotor = ord("R") - 65,
        configuracao_anel = ord("B") - 65,
    )
    
    assert rotor.esta_na_posicao_do_entalhe() is False

# Checa a posição anterior e posterior do entalhe, de apos isto, teste de rotação.
def test_posicao_anterior_ao_entalhe():
    rotor = Rotor.criar_rotor(
        nome="I",
        posicao_rotor=ord("P") - 65,
        configuracao_anel=ord("A") - 65,
    )
    
    assert rotor.esta_na_posicao_do_entalhe() is False
    
def test_posicao_posterior_ao_entalhe():
    rotor = Rotor.criar_rotor(
        nome="I",
        posicao_rotor=ord("R") - 65,
        configuracao_anel=ord("A") - 65,
    )
    
    assert rotor.esta_na_posicao_do_entalhe() is False

def test_rotacao_com_anel_nao_A():
    rotor = Rotor.criar_rotor(
        nome="I",
        posicao_rotor=ord("Q") - 65,
        configuracao_anel=ord("M") - 65,
    )
    
    rotor.rotacionar()
    
    assert rotor.posicao_rotor == ord("R") - 65
    
# Teste da regra da Enigma
def test_entalhe_do_rotor_direito_nao_muda_com_configuracao_do_anel():
    # Rotor III (entalhe V): o avanço depende só da letra da janela
    sem_avanco = Enigma(("I", "II", "III"), (0, 0, 7), (0, 0, 12), "B", "")
    com_avanco = Enigma(("I", "II", "III"), (0, 0, 21), (0, 0, 12), "B", "")
    
    sem_avanco.girar_rotores()
    com_avanco.girar_rotores()
    
    assert sem_avanco.rotor_central.posicao_rotor == 0
    assert sem_avanco.rotor_direito.posicao_rotor == 8
    assert com_avanco.rotor_central.posicao_rotor == 1
    assert com_avanco.rotor_direito.posicao_rotor == 22