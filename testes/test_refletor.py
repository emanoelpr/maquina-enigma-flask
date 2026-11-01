import pytest
from refletor import Refletor

# Teste simples de refletor. A -> Y, Y -> A. E se aplicar o refletor duas vezes na mesma letra, deve voltar a letra original.
def test_refletor_B_reflete_A_para_Y():
    refletor = Refletor.criar_refletor("B")
    
    assert refletor.cifrar(0) == 24
    
def test_refletor_B_reflete_Y_para_A():
    refletor = Refletor.criar_refletor("B")
    
    assert refletor.cifrar(24) == 0
    
# Teste de refletor duas vezes em cada uma das letras
def test_refletor_B_alfabeto():
    refletor = Refletor.criar_refletor("B")
    
    for letra in range(26):
        resultado = refletor.cifrar(letra)
        resultado_novamente = refletor.cifrar(resultado)
        
        assert resultado_novamente == letra
        
# Teste que não pode haver auto-reflexão
def test_refletor_B_nao_reflete_letra_para_ela_mesma():
    refletor = Refletor.criar_refletor("B")
    
    for letra in range(26):
        assert refletor.cifrar(letra) != letra
        
# Testando se todos os refletores respeitam as regras de espelhamento
def test_todos_os_refletores_sao_espelhados():
    for nome in ("B", "C", "Bfino", "Cfino"):
        refletor = Refletor.criar_refletor(nome)
        
        for letra in range(26):
            resultado = refletor.cifrar(letra)
            
            assert refletor.cifrar(resultado) == letra
            
# Nenhum refletor pode refletir uma letra para ela mesma
def test_todos_os_refletores_nao_refletem_para_si_mesmos():
    for nome in ("B", "C", "Bfino", "Cfino"):
        refletor = Refletor.criar_refletor(nome)
        
        for letra in range(26):
            assert refletor.cifrar(letra) != letra
            
# Testando se os refletores estão usando as tabelas definidas, testando um por um para identificar erros
def test_refletor_B_tem_mapeamentos_corretos():
    refletor = Refletor.criar_refletor("B")
        
    assert refletor.cifrar(0) == 24 # A -> Y
    assert refletor.cifrar(1) == 17 # B -> R
    assert refletor.cifrar(2) == 20 # C -> U

def test_refletor_C_tem_mapeamentos_corretos():
    refletor = Refletor.criar_refletor("C")

    assert refletor.cifrar(0) == 5    # A → F
    assert refletor.cifrar(1) == 21   # B → V
    assert refletor.cifrar(2) == 15   # C → P
    
def test_refletor_Bfino_tem_mapeamentos_corretos():
    refletor = Refletor.criar_refletor("Bfino")

    assert refletor.cifrar(0) == 4    # A → E
    assert refletor.cifrar(1) == 13   # B → N
    assert refletor.cifrar(2) == 10   # C → K
    
def test_refletor_Cfino_tem_mapeamentos_corretos():
    refletor = Refletor.criar_refletor("Cfino")

    assert refletor.cifrar(0) == 17   # A → R
    assert refletor.cifrar(1) == 3    # B → D
    assert refletor.cifrar(2) == 14   # C → O
    
# Garantindo que não tenha configurações inválidas
def test_refletor_invalido_gera_erro():
    with pytest.raises(ValueError):
        Refletor.criar_refletor("X")