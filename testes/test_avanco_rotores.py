from enigma import Enigma

import pytest
# Máquina padrão
@pytest.fixture
def maquina_padrao():
    return Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")

# Testando se o rotor direito gira a cada acionamento
def test_rotor_direito_gira_uma_posicao(maquina_padrao):
    maquina_padrao.girar_rotores()
    
    assert maquina_padrao.rotor_direito.posicao_rotor == 1
    # De 0, 0, 0. Queremos 0, 0, 1
    
# Teste de entalhe do Rotor direito acionando o central

def test_rotor_direito_no_entalhe_faz_rotor_central_avancar():
    maquina = Enigma(
        rotores= ("I", "II", "III"),
        posicoes_rotores = (0, 0, 21),
        configuracoes_anel = (0, 0, 0),
        nome_refletor= "B",
        conexoes_plugboard = "",
    )
    
    maquina.girar_rotores()
    
    assert maquina.rotor_central.posicao_rotor == 1
    assert maquina.rotor_direito.posicao_rotor == 22
    # Verificamos V -> W no Rotor Direito, e A -> B no Rotor Central
    
# Verificação de double-stepping. Pois, o rotor II possui entalhe E, quando o rotor central está em E, o rotor esquerdo e central avançam, além do direito.
# Se A, E, A. Deve ser B, F, B

def test_rotor_central_no_entalhe_faz_rotor_esquerdo_e_central_avancarem():
    maquina = Enigma(
        rotores = ("I", "II", "III"),
        posicoes_rotores = (0, 4, 0),
        configuracoes_anel = (0, 0, 0),
        nome_refletor = "B",
        conexoes_plugboard="",
    )
    
    maquina.girar_rotores()
    
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 5
    assert maquina.rotor_direito.posicao_rotor == 1
    
    # Comecamos em A, E, A. Esperando B, F, B
    
# Testando agora com entalhes A, E, V

def test_rotores_central_e_direito_simultaneamente_no_entalhe():
    maquina = Enigma(
        rotores = ("I", "II", "III"),
        posicoes_rotores = (0, 4, 21),
        configuracoes_anel = (0, 0, 0),
        nome_refletor = "B",
        conexoes_plugboard = "",
    )
    
    maquina.girar_rotores()
    
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 5
    assert maquina.rotor_direito.posicao_rotor == 22
    
    # Esperamos B, F, W.
    

# Agora, vamos testar a sequência de avanço. Vamos começar com A, A, U e girar duas vezes. Esperamos A, B, W após passar por A, A, V.

def test_rotor_central_avanca_no_avanco_seguinte_ao_entalhe_do_direito():
    maquina = Enigma(
        rotores = ("I", "II", "III"),
        posicoes_rotores = (0, 0 , 20),
        configuracoes_anel = (0, 0, 0),
        nome_refletor = "B",
        conexoes_plugboard = "",
    )
    
    maquina.girar_rotores()
    
    assert maquina.rotor_esquerdo.posicao_rotor == 0
    assert maquina.rotor_central.posicao_rotor == 0
    assert maquina.rotor_direito.posicao_rotor == 21
    
    maquina.girar_rotores()
    
    assert maquina.rotor_esquerdo.posicao_rotor == 0
    assert maquina.rotor_central.posicao_rotor == 1
    assert maquina.rotor_direito.posicao_rotor == 22
    
# Teste comparativo na mesma posicão, mudando apenas a configuração do anel.

def test_entalhe_do_rotor_direito_nao_muda_com_configuracao_do_anel():
    maquina_anel_A = Enigma(("I", "II", "III"), (0, 0, 21), (0, 0, 0), "B", "")
    maquina_anel_M = Enigma(("I", "II", "III"), (0, 0, 21), (0, 0, 12), "B", "")
    
    maquina_anel_A.girar_rotores()
    maquina_anel_M.girar_rotores()
    
    # Ambas devem avançar igual: A, A, V -> A, B, W
    assert maquina_anel_A.rotor_central.posicao_rotor == 1
    assert maquina_anel_M.rotor_central.posicao_rotor == 1
    assert maquina_anel_A.rotor_direito.posicao_rotor == 22
    assert maquina_anel_M.rotor_direito.posicao_rotor == 22
    
def test_double_stepping_com_configuracao_de_anel():
    # Anéis diferentes de A não alteram o avanço: A, D, V -> A, E, W -> B, F, X
    maquina = Enigma(("I", "II", "III"), (0, 3, 21), (2, 1, 2), "B", "")
    
    maquina.girar_rotores()
    
    assert maquina.rotor_esquerdo.posicao_rotor == 0   # A
    assert maquina.rotor_central.posicao_rotor == 4    # E
    assert maquina.rotor_direito.posicao_rotor == 22   # W
    
    # Central no entalhe E: avança junto com o esquerdo (duplo avanço)
    maquina.girar_rotores()
    
    assert maquina.rotor_esquerdo.posicao_rotor == 1   # B
    assert maquina.rotor_central.posicao_rotor == 5    # F
    assert maquina.rotor_direito.posicao_rotor == 23   # X
 