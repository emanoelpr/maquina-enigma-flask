from enigma import Enigma
from configuracao import criar_configuracao

# Teste base de criação das configurações da Enigma
def test_configuracao_m3():
    configuracao = criar_configuracao()
    
    maquina = Enigma(**configuracao)

    assert maquina.rotor_esquerdo.nome == "I"
    assert maquina.rotor_central.nome == "II"
    assert maquina.rotor_direito.nome == "III"
    assert maquina.refletor.cifrar(0) == 24
    
def test_configuracao_m4():
    configuracao = criar_configuracao(
        rotores=("Gamma", "III", "II", "I"),
        posicoes_rotores=(3, 7, 12, 20),
        configuracoes_anel=(2, 5, 9, 4),
        nome_refletor="Bfino",
        conexoes_plugboard="AB CD EF",
    )
    
    maquina = Enigma(**configuracao)
    
    assert maquina.rotor_grego.nome == "Gamma"
    assert maquina.rotor_esquerdo.nome == "III"
    assert maquina.rotor_central.nome == "II"
    assert maquina.rotor_direito.nome == "I"