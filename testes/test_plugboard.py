import pytest
from plugboard import Plugboard

# Teste de conexão simples, com AB, A deve produzir B, B deve produzir A
def test_conexao_simples():
    plugboard = Plugboard("AB")
    
    assert plugboard.cifrar(0) == 1
    assert plugboard.cifrar(1) == 0
    
# Teste de letras desconectadas, C -> C e Z -> Z
def test_letras_desconectadas_permanecem_iguais():
    plugboard = Plugboard("AB")
    
    assert plugboard.cifrar(2) == 2
    assert plugboard.cifrar(25) == 25
    
# Teste de múltiplas conexões. Uma não deve interferir nas outras.

def test_multiplas_conexoes():
    plugboard = Plugboard("AB CD EF")
    
    assert plugboard.cifrar(0) == 1 # A -> B
    assert plugboard.cifrar(1) == 0 # B -> A
    assert plugboard.cifrar(2) == 3 # C -> D
    assert plugboard.cifrar(3) == 2 # D -> C
    assert plugboard.cifrar(4) == 5 # E -> F
    assert plugboard.cifrar(5) == 4 # F -> E
    
# Testar conflitos com letras repetitas
def test_letra_nao_pode_ser_conectada_duas_vezes():
    with pytest.raises(ValueError):
        Plugboard("AB AC")

# Testar conflitos com auto-conexão
def test_letra_nao_pode_ser_conectada_a_si_mesma():
    with pytest.raises(ValueError):
        Plugboard("AA")
        
# Teste de limite das 13 conexões
def test_plugboard_aceita_13_conexoes():
    plugboard = Plugboard(
        "AB CD EF GH IJ KL MN OP QR ST UV WX YZ"
    )
    
    assert plugboard.cifrar(0) == 1
    assert plugboard.cifrar(24) == 25

# Testar caracteres desconectados
def test_obter_caracteres_desconectados():
    plugboard = Plugboard("AB CD EF")
    
    desconectados = plugboard.obter_caracteres_desconectados()
    
    assert desconectados == list(range(6, 26))
    
# Testando input com hifen
def test_conexoes_podem_ser_separadas_por_hifen():
    plugboard = Plugboard("AB-CD")
    
    assert plugboard.cifrar(0) == 1
    assert plugboard.cifrar(1) == 0
    assert plugboard.cifrar(2) == 3
    assert plugboard.cifrar(3) == 2
    
# Testando com vários separadores
def test_varios_separadores():
    plugboard = Plugboard("AB,CD EF")

    assert plugboard.cifrar(0) == 1
    assert plugboard.cifrar(1) == 0
    assert plugboard.cifrar(2) == 3
    assert plugboard.cifrar(3) == 2
    assert plugboard.cifrar(4) == 5
    assert plugboard.cifrar(5) == 4
    
# Teste com número impar de letras
def test_plugboard_com_letra_sobrando_gera_erro():
    with pytest.raises(ValueError):
        Plugboard("ABC")