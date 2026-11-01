
"""Cria o dicionário de configuração da máquina Enigma."""


def criar_configuracao(
    rotores=("I", "II", "III"),
    posicoes_rotores=(0, 0, 0),
    configuracoes_anel=(0, 0, 0),
    nome_refletor="B",
    conexoes_plugboard="",
):
    """Reúne os parâmetros necessários para inicializar a Enigma."""
    return {
        "rotores": rotores,
        "posicoes_rotores": posicoes_rotores,
        "configuracoes_anel": configuracoes_anel,
        "nome_refletor": nome_refletor,
        "conexoes_plugboard": conexoes_plugboard,
    }
