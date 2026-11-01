from rotor import Rotor
from enigma import Enigma

# Rotor base
def criar_rotor(nome):
    return Rotor.criar_rotor(
        nome = nome,
        posicao_rotor = 0,
        configuracao_anel = 0,
    )

# Maquina M4 base
def criar_maquina_m4(
    rotor_grego = "Beta",
    rotores = ("I", "II", "III"),
    posicoes = (0, 0, 0, 0),
    aneis = (0, 0, 0, 0),
    refletor = "Bfino",
    plugboard = "",
):
    return Enigma(
        rotores = (rotor_grego, *rotores),
        posicoes_rotores = posicoes,
        configuracoes_anel = aneis,
        nome_refletor = refletor,
        conexoes_plugboard = plugboard,
    )


# Integração do Rotor M4, com Rotores Beta e Gamma
def test_rotor_beta_existe():
    rotor = criar_rotor("Beta")
    
    assert rotor.nome == "Beta"

def test_rotor_gamma_existe():
    rotor = criar_rotor("Gamma")
    
    assert rotor.nome == "Gamma"   
    
# Ambos não possuem entalhes, então vamos testar
def test_rotor_beta_nao_tem_entalhe():
    rotor = criar_rotor("Beta")

    assert rotor.entalhes == ()


def test_rotor_gamma_nao_tem_entalhe():
    rotor = criar_rotor("Gamma")

    assert rotor.entalhes == ()

# Teste de cifragem
def test_rotor_beta_cifra_A_como_L():
    rotor = criar_rotor("Beta")

    assert rotor.cifrar_direto(0) == 11


def test_rotor_gamma_cifra_A_como_F():
    rotor = criar_rotor("Gamma")

    assert rotor.cifrar_direto(0) == 5

# Teste de fiação completa de BETA/GAMMA
def test_beta_direto_e_reverso_sao_inversos():
    rotor = criar_rotor("Beta")
    
    for letra in range(26):
        resultado = rotor.cifrar_direto(letra)
        original = rotor.cifrar_reverso(resultado)
        
        assert original == letra
    
def test_gamma_direto_e_reverso_sao_inversos():
    rotor = criar_rotor("Gamma")
    
    for letra in range(26):
        resultado = rotor.cifrar_direto(letra)
        original = rotor.cifrar_reverso(resultado)
        
        assert original == letra

# Teste da criação da M4 com quatro rotores
def test_m4_cria_quatro_rotores():
    maquina = criar_maquina_m4()
    
    assert maquina.rotor_grego.nome == "Beta"
    assert maquina.rotor_esquerdo.nome == "I"
    assert maquina.rotor_central.nome == "II"
    assert maquina.rotor_direito.nome == "III"
    
# Teste do caminho elétrico da Beta/Gamma
def test_m4_beta_entra_no_caminho_eletrico():
    maquina = criar_maquina_m4()
    
    resultado = maquina.cifrar(0)
    
    assert resultado != 0
    
# Teste se o rotor_grego gira ao ser acionado
def test_rotor_grego_nao_gira():
    maquina = criar_maquina_m4()
    
    posicao_inicial = maquina.rotor_grego.posicao_rotor
    
    maquina.cifrar(0)
    
    assert maquina.rotor_grego.posicao_rotor == posicao_inicial
    
# Testando se o restante dos rotores continuam avançando normalmente
def test_m4_rotores_normais_continuam_avancando():
    maquina = criar_maquina_m4()
    
    maquina.cifrar(0)
    
    assert maquina.rotor_esquerdo.posicao_rotor == 0
    assert maquina.rotor_central.posicao_rotor == 0
    assert maquina.rotor_direito.posicao_rotor == 1
    
# Testando agora o doublestepping na M4
def test_m4_double_stepping_continua_funcionando():
    maquina = criar_maquina_m4(
        posicoes = (0, 0, 4, 20),
    )
    
    maquina.girar_rotores()
    
    assert maquina.rotor_grego.posicao_rotor == 0
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 5
    assert maquina.rotor_direito.posicao_rotor == 21

    maquina.girar_rotores()

    assert maquina.rotor_grego.posicao_rotor == 0
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 6
    assert maquina.rotor_direito.posicao_rotor == 22
    
# Mesmo teste, com confiuracoes de anel
def test_m4_double_stepping_com_configuracao_de_anel():
    maquina = criar_maquina_m4(
        posicoes = (0, 0, 3, 21),
        aneis = (0, 2, 1, 2),
    )
    
    maquina.girar_rotores()
    
    assert maquina.rotor_grego.posicao_rotor == 0
    assert maquina.rotor_esquerdo.posicao_rotor == 0
    assert maquina.rotor_central.posicao_rotor == 4
    assert maquina.rotor_direito.posicao_rotor == 22

    maquina.girar_rotores()

    assert maquina.rotor_grego.posicao_rotor == 0
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 5
    assert maquina.rotor_direito.posicao_rotor == 23
    
# Teste elétrico isolado da M4
def test_m4_beta_e_refletor_fino_formam_caminho_reversivel():
    maquina = criar_maquina_m4()
    
    for letra in range(26):
        resultado = maquina.rotor_grego.cifrar_direto(letra)
        resultado = maquina.refletor.cifrar(resultado)
        resultado = maquina.rotor_grego.cifrar_reverso(resultado)
        
        assert 0 <= resultado < 26
        
# Teste elétrico, se é reversível (Beta -> Refletor -> Beta)
def test_m4_beta_refletor_beta_e_reversivel():
    maquina = criar_maquina_m4()
    
    for letra in range(26):
        resultado = maquina.rotor_grego.cifrar_direto(letra)
        resultado = maquina.refletor.cifrar(resultado)
        resultado = maquina.rotor_grego.cifrar_reverso(resultado)
        
        novamente = maquina.rotor_grego.cifrar_direto(resultado)
        novamente = maquina.refletor.cifrar(novamente)
        novamente = maquina.rotor_grego.cifrar_reverso(novamente)
        
        assert novamente == letra
        
# Vetor de integracao da M4
def test_m4_vetor_conhecido_gamma():
    maquina = criar_maquina_m4(
        rotor_grego = "Gamma",
        rotores = ("III", "II", "I"),
    )
    
    assert maquina.cifrar_texto("ABC") == "BPF"
    
# Testes de existencia do rotor grego
def test_m3_nao_possui_rotor_grego():
    maquina = Enigma(
        rotores=("I", "II", "III"),
        posicoes_rotores=(0, 0, 0),
        configuracoes_anel=(0, 0, 0),
        nome_refletor="B",
        conexoes_plugboard="",
    )
    
    assert maquina.rotor_grego is None
    
def test_m4_possui_rotor_grego():
    maquina = criar_maquina_m4()

    assert maquina.rotor_grego is not None
    assert maquina.rotor_grego.nome == "Beta"
    
# Teste de integracao de M4 + Anel + Posicao + Plugboard
def test_m4_com_aneis_posicoes_e_plugboard():
    maquina = criar_maquina_m4(
        rotor_grego = "Gamma",
        rotores = ("III", "II", "I"),
        posicoes = (3, 7, 12, 20),
        aneis = (2, 5, 9, 4),
        plugboard = "AB CD EF",
    )
    
    resultado = maquina.cifrar_texto("TESTE")
    
    assert len(resultado) == 5
    assert resultado.isalpha()
    assert resultado.isupper()
    
# Teste de reciprocidade em ambas as maquinas com mesma configuracao
def test_m4_reciprocidade_com_configuracao_complexa():
    maquina1 = criar_maquina_m4(
        rotor_grego="Gamma",
        rotores=("III", "II", "I"),
        posicoes=(3, 7, 12, 20),
        aneis=(2, 5, 9, 4),
        plugboard="AB CD EF",
    )

    cifrado = maquina1.cifrar_texto("TESTE")

    maquina2 = criar_maquina_m4(
        rotor_grego="Gamma",
        rotores=("III", "II", "I"),
        posicoes=(3, 7, 12, 20),
        aneis=(2, 5, 9, 4),
        plugboard="AB CD EF",
    )

    decifrado = maquina2.cifrar_texto(cifrado)

    assert decifrado == "TESTE"