
"""Interface de linha de comando para a máquina Enigma M3 e M4."""

import argparse

from configuracao import criar_configuracao
from enigma import Enigma

alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
rotores_validos = {
    nome.lower(): nome
    for nome in (
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII",
        "Beta", "Gamma",
    )
}
refletores_validos = {
    nome.lower(): nome for nome in ("B", "C", "Bfino", "Cfino")
}


def criar_argumentos_padrao():
    """Retorna os valores padrão usados pela interface."""
    return {
        "modo": "m3",
        "operacao": "cifrar",
        "mostrar_configuracao": False,
        "rotores": ("I", "II", "III"),
        "posicoes": ("A", "A", "A"),
        "aneis": ("A", "A", "A"),
        "refletor": "B",
        "plugboard": "",
        "texto": "",
    }


def converter_letras_para_numeros(valores):
    """Converte letras A–Z em índices de 0 a 25."""
    resultado = []

    for valor in valores:
        if len(valor) != 1 or valor.upper() not in alfabeto:
            raise ValueError(
                f"Valor inválido: {valor!r}. Use uma única letra de A a Z."
            )
        resultado.append(ord(valor.upper()) - ord("A"))

    return tuple(resultado)


def normalizar_nomes_configuracao(argumentos):
    """Padroniza maiúsculas e minúsculas nos nomes dos rotores e refletor."""
    try:
        argumentos.rotores = [
            rotores_validos[nome.lower()] for nome in argumentos.rotores
        ]
    except KeyError as erro:
        raise ValueError(
            f"Rotor inválido nesta posição: {erro.args[0]!r}."
        ) from None

    try:
        argumentos.refletor = refletores_validos[
            argumentos.refletor.lower()
        ]
    except KeyError:
        raise ValueError(
            f"Refletor inválido: {argumentos.refletor!r}."
        ) from None


def criar_parser():
    """Define as opções e os exemplos de uso da CLI."""
    padrao = criar_argumentos_padrao()
    parser = argparse.ArgumentParser(
        description="Máquina Enigma - Interface de Linha de Comando.",
        epilog='''\
Exemplos:
  M3 com configuração padrão:
    python cli.py --texto "AAAAA"

  M4:
    python cli.py --modo m4 --rotores Gamma III II I --posicoes A A A A --aneis A A A A --refletor Bfino --texto "ABC"
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--modo", choices=("m3", "m4"), default=padrao["modo"],
        help="Modelo da máquina: M3 ou M4.",
    )
    parser.add_argument(
        "--operacao", choices=("cifrar", "decifrar"),
        default=padrao["operacao"],
        help="Operação realizada: cifrar ou decifrar.",
    )
    parser.add_argument(
        "--mostrar-configuracao", action="store_true",
        help="Mostra a configuração antes do resultado.",
    )
    parser.add_argument(
        "--rotores", nargs="+", default=padrao["rotores"],
        help="Rotores usados na máquina.",
    )
    parser.add_argument(
        "--posicoes", nargs="+", default=padrao["posicoes"],
        help="Posições iniciais dos rotores, de A a Z.",
    )
    parser.add_argument(
        "--aneis", nargs="+", default=padrao["aneis"],
        help="Configurações dos anéis, de A a Z.",
    )
    parser.add_argument(
        "--refletor", default=None,
        help="Refletor utilizado. Padrão: B no M3 e Bfino no M4.",
    )
    parser.add_argument(
        "--plugboard", default=padrao["plugboard"],
        help="Conexões do plugboard, por exemplo: 'AB CD EF'.",
    )
    parser.add_argument(
        "--texto", default=padrao["texto"],
        help="Texto que será processado.",
    )
    return parser


def executar(argumentos):
    """Valida os argumentos, cria a máquina e processa o texto."""
    if argumentos.refletor is None:
        argumentos.refletor = "Bfino" if argumentos.modo == "m4" else "B"

    normalizar_nomes_configuracao(argumentos)
    quantidade_rotores = len(argumentos.rotores)
    quantidade_esperada = 3 if argumentos.modo == "m3" else 4

    if quantidade_rotores != quantidade_esperada:
        raise ValueError(
            f"O modo {argumentos.modo.upper()} exige exatamente "
            f"{quantidade_esperada} rotores."
        )
    if len(argumentos.posicoes) != quantidade_rotores:
        raise ValueError(
            "A quantidade de posições deve ser igual à quantidade de rotores."
        )
    if len(argumentos.aneis) != quantidade_rotores:
        raise ValueError(
            "A quantidade de configurações de anel deve ser igual "
            "à quantidade de rotores."
        )

    configuracao = criar_configuracao(
        rotores=tuple(argumentos.rotores),
        posicoes_rotores=converter_letras_para_numeros(argumentos.posicoes),
        configuracoes_anel=converter_letras_para_numeros(argumentos.aneis),
        nome_refletor=argumentos.refletor,
        conexoes_plugboard=argumentos.plugboard,
    )

    # A Enigma é recíproca: a mesma configuração permite cifrar e decifrar.
    return Enigma(**configuracao).cifrar_texto(argumentos.texto)


def mostrar_configuracao(argumentos):
    """Exibe a configuração utilizada no processamento."""
    print(f"Modo: {argumentos.modo.upper()}")
    print(f"Operação: {argumentos.operacao}")
    print(f"Rotores: {' '.join(argumentos.rotores)}")
    print(f"Posições: {' '.join(argumentos.posicoes)}")
    print(f"Anéis: {' '.join(argumentos.aneis)}")
    print(f"Refletor: {argumentos.refletor}")
    print(f"Plugboard: {argumentos.plugboard or 'nenhum'}")


def main_com_argumentos(argumentos):
    """Executa a CLI com argumentos já interpretados pelo argparse."""
    if not argumentos.texto:
        print("Nenhum texto informado.")
        print("Use --texto 'SEU TEXTO' para cifrar uma mensagem.")
        return

    try:
        resultado = executar(argumentos)
    except ValueError as erro:
        print(f"Erro: {erro}")
        return

    if argumentos.mostrar_configuracao:
        mostrar_configuracao(argumentos)
        rotulo = (
            "Texto decifrado:"
            if argumentos.operacao == "decifrar"
            else "Texto cifrado:"
        )
        print(rotulo)

    print(resultado)


def main():
    """Ponto de entrada da interface de linha de comando."""
    main_com_argumentos(criar_parser().parse_args())


if __name__ == "__main__":
    main()
