import pytest
import cli

# Argumentos padrão
def test_argumentos_padrao():
    argumentos = cli.criar_argumentos_padrao()

    assert argumentos["modo"] == "m3"
    assert argumentos["rotores"] == ("I", "II", "III")
    assert argumentos["posicoes"] == ("A", "A", "A")
    assert argumentos["aneis"] == ("A", "A", "A")
    assert argumentos["refletor"] == "B"
    assert argumentos["plugboard"] == ""
    assert argumentos["texto"] == ""

def test_cli_m3_cifra_texto():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--rotores", "I", "II", "III",
        "--posicoes", "A", "A", "A",
        "--aneis", "A", "A", "A",
        "--refletor", "B",
        "--texto", "AAAAA",     
    ])
    
    resultado = cli.executar(argumentos)
    
    assert resultado == "BDZGO"
    
def test_cli_m4_cifra_texto():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--refletor", "Bfino",
        "--texto", "ABC",
    ])

    resultado = cli.executar(argumentos)

    assert resultado == "BPF"
    
def test_cli_m4_gera_a_mesma_configuracao_da_enigma():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--refletor", "Bfino",
        "--texto", "ABC",
    ])

    assert tuple(argumentos.rotores) == ("Gamma", "III", "II", "I")
    assert cli.converter_letras_para_numeros(argumentos.posicoes) == (0, 0, 0, 0)
    assert cli.converter_letras_para_numeros(argumentos.aneis) == (0, 0, 0, 0)
    assert argumentos.refletor == "Bfino"

def test_cli_m3_nao_aceita_refletor_fino():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--rotores", "I", "II", "III",
        "--posicoes", "A", "A", "A",
        "--aneis", "A", "A", "A",
        "--refletor", "Bfino",
        "--texto", "ABC",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)

def test_cli_m4_nao_aceita_refletor_normal():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--refletor", "B",
        "--texto", "ABC",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)

def test_cli_rejeita_posicao_que_nao_e_letra():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--rotores", "I", "II", "III",
        "--posicoes", "1", "A", "A",
        "--aneis", "A", "A", "A",
        "--refletor", "B",
        "--texto", "ABC",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)


def test_cli_rejeita_mais_de_uma_letra_na_posicao():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--rotores", "I", "II", "III",
        "--posicoes", "AA", "A", "A",
        "--aneis", "A", "A", "A",
        "--refletor", "B",
        "--texto", "ABC",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)


def test_cli_rejeita_anel_que_nao_e_letra():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--rotores", "I", "II", "III",
        "--posicoes", "A", "A", "A",
        "--aneis", "@", "A", "A",
        "--refletor", "B",
        "--texto", "ABC",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)

def test_cli_sem_texto_mostra_mensagem(capsys):
    argumentos = cli.criar_parser().parse_args([])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert "Nenhum texto informado" in captura.out
    
def test_cli_help_contem_descricao():
    parser = cli.criar_parser()

    ajuda = parser.format_help()

    assert "Máquina Enigma" in ajuda
    assert "--texto" in ajuda
    assert "--rotores" in ajuda
    assert "--posicoes" in ajuda
    assert "--aneis" in ajuda
    assert "--refletor" in ajuda


def test_cli_help_contem_exemplos():
    parser = cli.criar_parser()

    ajuda = parser.format_help()

    assert 'python cli.py --texto "AAAAA"' in ajuda
    assert "python cli.py --modo m4" in ajuda
    
def test_cli_cifrar_e_decifrar_produzem_o_original():
    argumentos_cifrar = cli.criar_parser().parse_args([
        "--texto", "OLAMUNDO",
    ])

    cifrado = cli.executar(argumentos_cifrar)

    argumentos_decifrar = cli.criar_parser().parse_args([
        "--operacao", "decifrar",
        "--texto", cifrado,
    ])

    decifrado = cli.executar(argumentos_decifrar)

    assert decifrado == "OLAMUNDO"


def test_cli_operacao_padrao_e_cifrar():
    argumentos = cli.criar_parser().parse_args([
        "--texto", "AAAAA",
    ])

    assert argumentos.operacao == "cifrar"


def test_cli_aceita_operacao_decifrar():
    argumentos = cli.criar_parser().parse_args([
        "--operacao", "decifrar",
        "--texto", "BDZGO",
    ])

    assert argumentos.operacao == "decifrar"
    
def test_cli_rejeita_quantidade_errada_de_posicoes():
    argumentos = cli.criar_parser().parse_args([
        "--posicoes", "A", "B",
        "--texto", "AAAA",
    ])

    with pytest.raises(
        ValueError,
        match="A quantidade de posições deve ser igual à quantidade de rotores",
    ):
        cli.executar(argumentos)


def test_cli_rejeita_quantidade_errada_de_aneis():
    argumentos = cli.criar_parser().parse_args([
        "--aneis", "A", "B",
        "--texto", "AAAA",
    ])

    with pytest.raises(
        ValueError,
        match="A quantidade de configurações de anel deve ser igual à quantidade de rotores",
    ):
        cli.executar(argumentos)

def test_cli_rejeita_quatro_rotores_no_modo_m3():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--rotores", "I", "II", "III", "IV",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--texto", "AAAA",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)

def test_cli_rejeita_tres_rotores_no_modo_m4():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "I", "II", "III",
        "--posicoes", "A", "A", "A",
        "--aneis", "A", "A", "A",
        "--refletor", "B",
        "--texto", "AAAA",
    ])

    with pytest.raises(ValueError):
        cli.executar(argumentos)
        
def test_cli_m4_usa_quatro_rotores():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--refletor", "Bfino",
        "--texto", "ABC",
    ])

    resultado = cli.executar(argumentos)

    assert resultado == "BPF"
    
def test_main_mostra_erro_de_configuracao(capsys):
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "I", "II", "III",
        "--posicoes", "A", "A", "A",
        "--aneis", "A", "A", "A",
        "--refletor", "B",
        "--texto", "AAAA",
    ])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert "Erro:" in captura.out
    assert "M4" in captura.out


def test_main_mostra_erro_para_rotor_invalido(capsys):
    argumentos = cli.criar_parser().parse_args([
        "--rotores", "I", "II", "X",
        "--posicoes", "A", "A", "A",
        "--aneis", "A", "A", "A",
        "--texto", "AAAA",
    ])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert "Erro:" in captura.out
    assert "Rotor inválido" in captura.out
    
def test_cli_nao_mostra_configuracao_por_padrao(capsys):
    argumentos = cli.criar_parser().parse_args([
        "--texto", "AAAAA",
    ])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert captura.out.strip() == "BDZGO"


def test_cli_mostra_configuracao_quando_solicitado(capsys):
    argumentos = cli.criar_parser().parse_args([
        "--mostrar-configuracao",
        "--texto", "AAAAA",
    ])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert "Modo: M3" in captura.out
    assert "Operação: cifrar" in captura.out
    assert "Rotores: I II III" in captura.out
    assert "Posições: A A A" in captura.out
    assert "Anéis: A A A" in captura.out
    assert "Refletor: B" in captura.out
    assert "Plugboard: nenhum" in captura.out
    assert "Texto cifrado:" in captura.out
    assert "BDZGO" in captura.out
    
def test_cli_mostra_texto_decifrado_quando_operacao_e_decifrar(capsys):
    argumentos = cli.criar_parser().parse_args([
        "--operacao", "decifrar",
        "--mostrar-configuracao",
        "--texto", "BDZGO",
    ])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert "Modo: M3" in captura.out
    assert "Operação: decifrar" in captura.out
    assert "Texto decifrado:" in captura.out
    assert "AAAAA" in captura.out
    
def test_cli_m4_mostra_configuracao(capsys):
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "B", "C", "D",
        "--aneis", "A", "B", "C", "D",
        "--refletor", "Bfino",
        "--plugboard", "AB CD EF",
        "--mostrar-configuracao",
        "--texto", "ABC",
    ])

    cli.main_com_argumentos(argumentos)

    captura = capsys.readouterr()

    assert "Modo: M4" in captura.out
    assert "Rotores: Gamma III II I" in captura.out
    assert "Posições: A B C D" in captura.out
    assert "Anéis: A B C D" in captura.out
    assert "Refletor: Bfino" in captura.out
    assert "Plugboard: AB CD EF" in captura.out
    assert "Texto cifrado:" in captura.out
    
@pytest.mark.parametrize(
    "rotores, refletor",
    [
        (("gamma", "iii", "ii", "i"), "bfino"),
        (("GAMMA", "III", "II", "I"), "BFINO"),
        (("gAmMa", "iIi", "Ii", "i"), "BfInO"),
    ],
)

def test_cli_normaliza_nomes_de_rotores_e_refletor(rotores, refletor):
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", *rotores,
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--refletor", refletor,
        "--texto", "ABC",
    ])
    
    resultado = cli.executar(argumentos)
    
    assert resultado == "BPF"
    
def test_cli_help_contem_exemplos():
    parser = cli.criar_parser()

    ajuda = parser.format_help()

    assert "M3 com configuração padrão:" in ajuda
    assert "M4:" in ajuda
    assert "--modo m4" in ajuda
    assert "--rotores" in ajuda
    assert "--refletor" in ajuda
    
def test_cli_m4_usa_refletor_bfino_como_padrao():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--texto", "ABC",
    ])

    resultado = cli.executar(argumentos)

    assert argumentos.refletor == "Bfino"
    assert resultado == "BPF"
    
def test_cli_m3_mantem_refletor_b_como_padrao():
    argumentos = cli.criar_parser().parse_args([
        "--modo", "m3",
        "--texto", "AAAAA",
    ])

    resultado = cli.executar(argumentos)

    assert argumentos.refletor == "B"
    assert resultado == "BDZGO"
    
def test_cli_m4_cifra_e_decifra_produzem_o_original():
    argumentos_cifrar = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--texto", "OLAMUNDO",
    ])

    cifrado = cli.executar(argumentos_cifrar)

    argumentos_decifrar = cli.criar_parser().parse_args([
        "--modo", "m4",
        "--operacao", "decifrar",
        "--rotores", "Gamma", "III", "II", "I",
        "--posicoes", "A", "A", "A", "A",
        "--aneis", "A", "A", "A", "A",
        "--texto", cifrado,
    ])

    decifrado = cli.executar(argumentos_decifrar)

    assert decifrado == "OLAMUNDO"