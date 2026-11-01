from enigma import Enigma

import pytest

# Maquina padrão
@pytest.fixture
def maquina_padrao():
    return Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")

# Teste de criacao da maquina
def test_enigma_cria_tres_rotores(maquina_padrao):
    assert maquina_padrao.rotor_esquerdo.nome == "I"
    assert maquina_padrao.rotor_central.nome == "II"
    assert maquina_padrao.rotor_direito.nome == "III"
    
def test_enigma_cria_rotores_com_as_posicoes_iniciais():
    maquina = Enigma(("I", "II", "III"), (5, 10, 15), (0, 0, 0), "B", "")

    assert maquina.rotor_esquerdo.posicao_rotor == 5
    assert maquina.rotor_central.posicao_rotor == 10
    assert maquina.rotor_direito.posicao_rotor == 15
    
def test_enigma_cria_rotores_com_as_configuracoes_de_anel():
    maquina = Enigma(("I", "II", "III"), (0, 0, 0), (1, 5, 12), "B", "")

    assert maquina.rotor_esquerdo.configuracao_anel == 1
    assert maquina.rotor_central.configuracao_anel == 5
    assert maquina.rotor_direito.configuracao_anel == 12
    
# Teste de não-auto-cifragem. Nenhuma letra deve cifrar a si mesma
def test_nenhuma_letra_cifra_para_si_mesma():
    for letra in range(26):
        maquina = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
        
        resultado = maquina.cifrar(letra)
        
        assert resultado != letra, f"{chr(letra + 65)} cifrou para si mesma"
    
# Teste de cifrar duas vezes, deve voltar ao original
def test_cifrar_duas_vezes_retorna_original():
    maquina1 = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "AB CD")
    cifrado = maquina1.cifrar_texto("OLAMUNDO")
    
    maquina2 = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "AB CD")
    decifrado = maquina2.cifrar_texto(cifrado)
    
    assert decifrado == "OLAMUNDO"

# Teste com Vetor Histórico (AAAAA -> BDZGO)
def test_vetor_historico_AAAAA(maquina_padrao):
    assert maquina_padrao.cifrar_texto("AAAAA") == "BDZGO"
    
# Testando um texto longo
def test_cifrar_alfabeto_completo(maquina_padrao):
    resultado = maquina_padrao.cifrar_texto("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    assert len(resultado) == 26
    assert resultado.isalpha()

# Testando a criação dos refletores e plugboard
def test_enigma_cria_o_refletor_escolhido():
    maquina = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "C", "")

    assert maquina.refletor.cifrar(0) == 5


def test_enigma_cria_o_plugboard():
    maquina = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "AB CD")

    assert maquina.plugboard.cifrar(0) == 1
    assert maquina.plugboard.cifrar(1) == 0
    assert maquina.plugboard.cifrar(2) == 3
    assert maquina.plugboard.cifrar(3) == 2
    
# Impedir criação de rotores repetidos

def test_enigma_nao_permite_rotores_repetidos():
    with pytest.raises(ValueError):
        Enigma(("I", "I", "III"), (0, 0, 0), (0, 0, 0), "B", "")
        
# Teste de cifragem antes do rotor direito avançar
def test_cifrar_faz_o_rotor_direito_avancar_antes_da_cifragem(maquina_padrao):
    maquina_padrao.cifrar(0)

    assert maquina_padrao.rotor_direito.posicao_rotor == 1
    assert maquina_padrao.rotor_central.posicao_rotor == 0
    assert maquina_padrao.rotor_esquerdo.posicao_rotor == 0

# Cifragem retorna um numero entre 0 e 25
def test_cifrar_retorna_um_numero_entre_zero_e_25(maquina_padrao):
    resultado = maquina_padrao.cifrar(0)

    assert 0 <= resultado <= 25
    
# Teste da Cifragem de Texto
def test_cifrar_texto_retorna_apenas_letras(maquina_padrao):

    resultado = maquina_padrao.cifrar_texto("ABC DEF")

    assert resultado.isalpha()
    assert resultado.isupper()


def test_cifrar_texto_ignora_espacos(maquina_padrao):
    maquina1 = maquina_padrao
    maquina2 = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")

    resultado_com_espaco = maquina1.cifrar_texto("ABC DEF")
    resultado_sem_espaco = maquina2.cifrar_texto("ABCDEF")

    assert resultado_com_espaco == resultado_sem_espaco


def test_cifrar_texto_ignora_caracteres_que_nao_sao_letras(maquina_padrao):
    maquina1 = maquina_padrao
    maquina2 = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")

    resultado_com_simbolos = maquina1.cifrar_texto("A-B-C!")
    resultado_sem_simbolos = maquina2.cifrar_texto("ABC")

    assert resultado_com_simbolos == resultado_sem_simbolos
    
# Valida o .uuper na cifragem
def test_cifrar_texto_aceita_minisculas(maquina_padrao):
    maquina1 = maquina_padrao
    maquina2 = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "")
    
    assert maquina1.cifrar_texto("abc") == maquina2.cifrar_texto("ABC")
    
# Verificação de duas rotações consecutivas
def test_double_stepping_completo():
    maquina = maquina2 = Enigma(("I", "II", "III"), (0, 4, 20), (0, 0, 0), "B", "")
    maquina.girar_rotores()
    # B, F, V
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 5
    assert maquina.rotor_direito.posicao_rotor == 21
    
    maquina.girar_rotores()
    # B, G, W
    assert maquina.rotor_esquerdo.posicao_rotor == 1
    assert maquina.rotor_central.posicao_rotor == 6
    assert maquina.rotor_direito.posicao_rotor == 22

def test_cifrar_texto_vazio(maquina_padrao):
    resultado = maquina_padrao.cifrar_texto("")

    assert resultado == ""
    
def test_cifrar_texto_somente_com_caracteres_ignorados(maquina_padrao):
    resultado = maquina_padrao.cifrar_texto(" 123 !@#$% ")

    assert resultado == ""
    
# Caracteres ignorados não podem fazer os rotores avançarem
def test_caracteres_ignorados_nao_fazem_rotores_avancar(maquina_padrao):
    maquina1 = maquina_padrao

    maquina2 = Enigma(("I", "II", "III"), (0, 0, 0), (0, 0, 0), "B", "",)

    resultado1 = maquina1.cifrar_texto("A")
    resultado2 = maquina2.cifrar_texto("1 A !")

    assert resultado1 == resultado2

# Garantindo que a máquina consegue processar um texto maior sem quebrar
def test_cifrar_texto_longo(maquina_padrao):
    maquina = maquina_padrao

    texto = "A" * 1000
    resultado = maquina.cifrar_texto(texto)

    assert len(resultado) == 1000
    assert resultado.isalpha()
    assert resultado.isupper()