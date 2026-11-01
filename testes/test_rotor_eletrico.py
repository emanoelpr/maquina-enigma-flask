from rotor import Rotor

import pytest

@pytest.fixture
# Criação de Rotor padrão
def criar_rotor():
    def criar(
        nome = "I",
        posicao_rotor = 0,
        configuracao_anel = 0,
    ):
        return Rotor.criar_rotor(
            nome = nome,
            posicao_rotor = posicao_rotor,
            configuracao_anel = configuracao_anel,
        )
    return criar

# Teste básico de fiação
def test_rotor_I_mapeia_A_para_E(criar_rotor):
    rotor = criar_rotor()
    
    assert rotor._cifrar(0, rotor.mapeamento_direto) == 4

# Caminho reverso
def test_rotor_I_mapeia_E_de_volta_para_A(criar_rotor):
    rotor = criar_rotor()
    
    assert rotor._cifrar(4, rotor.mapeamento_reverso) == 0
    
# Verifica se B -> K
def test_rotor_I_mapeia_B_para_K(criar_rotor):
    rotor = criar_rotor()
    
    assert rotor._cifrar(1, rotor.mapeamento_direto) == 10
    
# Testando se o mapeamento muda ao girar o Rotor
def test_rotor_I_muda_o_mapeamento_quando_a_posicao_muda(criar_rotor):
    rotor = criar_rotor(posicao_rotor = 1)
    
    assert rotor._cifrar(0, rotor.mapeamento_direto) == 9 # Deslocamento = posicao - anel. Logo, (10 - 1) % 26 = 9
    
def test_rotor_I_muda_o_mapeamento_quando_o_anel_muda(criar_rotor):
    rotor = criar_rotor(configuracao_anel = 1)

    assert rotor._cifrar(0, rotor.mapeamento_direto) == 10 # (9 - (-1)) % 26 = 10
    
# Testando agora cada caso isoladamente. Testando se deslocamento = self.posicao_rotor - self.configuracao_anel
def test_rotor_I_combina_posicao_e_anel(criar_rotor):
    rotor = criar_rotor(posicao_rotor = 2, configuracao_anel = 1)
    
    assert rotor._cifrar(0, rotor.mapeamento_direto) == 9
    
# Testando se quando o rotor está em Z e girar, se volta para A
def test_rotor_volta_para_A_ao_girar_de_Z(criar_rotor):
    rotor = criar_rotor(posicao_rotor = 25)
        
    rotor.rotacionar()
    
    assert rotor.posicao_rotor == 0
    
# Agora, com dois entalhes

@pytest.mark.parametrize(
    "nome",
    ["VI", "VII", "VIII"],
)
def test_rotores_com_dois_entalhes_tem_entalhe_em_M(criar_rotor, nome):
    rotor = criar_rotor(
        nome = nome,
        posicao_rotor = 12,
    )
    
    assert rotor.esta_na_posicao_do_entalhe()
    
@pytest.mark.parametrize(
    "nome",
    ["VI", "VII", "VIII"],
)
def test_rotores_com_dois_entalhes_tem_entalhe_em_Z(criar_rotor, nome):
    rotor = criar_rotor(
        nome = nome,
        posicao_rotor = 25,
    )
    
    assert rotor.esta_na_posicao_do_entalhe()
    
# Agora, testado uma posicao que não é entalhe
@pytest.mark.parametrize(
    "nome",
    ["VI", "VII", "VIII"],
)
def test_rotores_com_dois_entalhes_nao_tem_entalhe_em_N(criar_rotor, nome):
    rotor = criar_rotor(
        nome = nome,
        posicao_rotor = 13,
    )
    
    assert rotor.esta_na_posicao_do_entalhe() is False

# Teste de rotacao
@pytest.mark.parametrize(
    "nome",
    ["VI", "VII", "VIII"],
)
def test_rotores_com_dois_entalhes_rotacionam_de_M_para_N(criar_rotor, nome):
    rotor = criar_rotor(
        nome = nome,
        posicao_rotor = 12,
    )
    
    rotor.rotacionar()
    
    assert rotor.posicao_rotor == 13
    
@pytest.mark.parametrize(
    "nome",
    ["VI", "VII", "VIII"],
)   
def test_rotores_com_dois_entalhes_rotacionam_de_Z_para_A(criar_rotor, nome):
    rotor = criar_rotor(
        nome = nome,
        posicao_rotor = 25,
    )
    
    rotor.rotacionar()
    
    assert rotor.posicao_rotor == 0
    
# Agora, vamos testar o mapeamento elétrico dos rotores
@pytest.mark.parametrize(
    "nome, entrada, saida",
    [
        ("II", 0, 0),   # A → A
        ("III", 0, 1),  # A → B
        ("IV", 0, 4),   # A → E
        ("V", 0, 21),   # A → V
        ("VI", 0, 9),   # A → J
        ("VII", 0, 13), # A → N
        ("VIII", 0, 5), # A → F
    ],
)
def test_rotor_mapeia_corretamente(criar_rotor, nome, entrada, saida):
    rotor = criar_rotor (nome = nome)

    assert rotor._cifrar(
        entrada,
        rotor.mapeamento_direto,
    ) == saida