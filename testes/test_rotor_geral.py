import pytest

from rotor import Rotor

# Teste de Identidade

def test_rotor_identidade_mantem_todas_as_letras():
    rotor = Rotor.criar_rotor(
        nome = "Identidade",
        posicao_rotor = 0,
        configuracao_anel = 0,
    )
    
    for letra in range(26):
        resultado = rotor._cifrar(
            letra,
            rotor.mapeamento_direto,
        )
        
        assert resultado == letra
        
def test_rotor_identidade_tem_mapeamento_reverso_identico():
    rotor = Rotor.criar_rotor(
        nome = "Identidade",
        posicao_rotor = 0,
        configuracao_anel = 0,
    )
    
    assert rotor.mapeamento_direto == rotor.mapeamento_reverso
    
# Testando inversão nos rotores

@pytest.mark.parametrize(
    "nome",
    [
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
    ]
)

def test_rotor_volta_para_a_entrada_ao_usar_mapeamento_reverso(nome):
    rotor = Rotor.criar_rotor(
        nome = nome,
        posicao_rotor = 0,
        configuracao_anel = 0,
    )
    
    for letra in range(26):
        ida = rotor._cifrar(
            letra,
            rotor.mapeamento_direto,
        )
        
        volta = rotor._cifrar(
            ida,
            rotor.mapeamento_reverso,
        )
        
        assert volta == letra
        
# Testando se o mapeamento tem repeticoes

@pytest.mark.parametrize(
    "nome",
    [
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
    ],
)

def test_rotor_tem_26_saidas_diferentes(nome):
    rotor = Rotor.criar_rotor(
        nome = nome,
        posicao_rotor = 0,
        configuracao_anel = 0,
    )
    
    resultados = []
    
    for letra in range(26):
        resultado = rotor._cifrar(
            letra,
            rotor.mapeamento_direto,
        )
        
        resultados.append(resultado)
        
    assert len(set(resultados)) == 26
    
# Testando a rotacao dos rotores

def test_rotor_retorna_a_posicao_inicial_apos_26_rotacoes():
    rotor = Rotor.criar_rotor(
        nome = "I",
        posicao_rotor = 7,
        configuracao_anel = 0,
    )
    
    posicao_inicial = rotor.posicao_rotor
    
    for _ in range(26):
        rotor.rotacionar()
        
    assert rotor.posicao_rotor == posicao_inicial
    
def test_rotor_rotaciona_uma_posicao():
    rotor = Rotor.criar_rotor(
        nome = "I",
        posicao_rotor = 7,
        configuracao_anel = 0,
    )
    
    rotor.rotacionar()
    
    assert rotor.posicao_rotor == 8
    
def test_rotor_rotaciona_de_Z_para_A():
    rotor = Rotor.criar_rotor(
        nome = "I",
        posicao_rotor = 25,
        configuracao_anel = 0,
    )
    
    rotor.rotacionar()
    
    assert rotor.posicao_rotor == 0
    
# Testar invalidez de nome de Rotor
def test_nome_de_rotor_invalido_gera_erro():
    with pytest.raises(ValueError):
        Rotor.criar_rotor(
            nome = "IX",
            posicao_rotor = 0,
            configuracao_anel = 0,
    )