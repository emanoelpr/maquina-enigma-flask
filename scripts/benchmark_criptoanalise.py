"""Benchmark comparativo da criptoanálise M4: caminho original vs. acelerado.

Executa o MESMO caso de teste pelas duas implementações, no mesmo ambiente:

- Original: cópia fiel do laço de busca anterior ao P1 de desempenho
  (motor Enigma letra a letra + pontuar_candidato).
- Acelerado: atacar_posicoes atual (avaliador com tabelas pré-calculadas).

Uso:  python scripts/benchmark_criptoanalise.py [repetições]

A configuração de referência recupera ATAQUEAOAMANHECERNOLITORALNORTE-
CONFIRMADO com posições D-T-C e rotor grego na posição L.
"""

import sys
import time
from heapq import nlargest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from criptoanalise import (  # noqa: E402
    letras_para_pontuar,
    rotores_gregos,
    rotores_principais,
    atacar_posicoes,
    pontuar_candidato,
)
from enigma import Enigma  # noqa: E402
from string import ascii_uppercase  # noqa: E402

ALFABETO = ascii_uppercase
from pontuacao import normalizar  # noqa: E402

# Caso de teste idêntico para as duas versões
CONFIG_VERDADEIRA = {
    "rotores": ("Beta", "IV", "II", "V"),
    "posicoes_rotores": (11, 3, 19, 2),      # L, D, T, C
    "configuracoes_anel": (0, 7, 13, 20),    # anéis 1, 8, 14, 21
    "nome_refletor": "Bfino",
    "conexoes_plugboard": "",
}
MENSAGEM = "ATAQUEAOAMANHECERNOLITORALNORTECONFIRMADO"
BUSCA = {
    "rotores": ("IV", "II", "V"),
    "aneis": [8, 14, 21],
    "refletor": "Bfino",
    "idioma": "pt",
    "limite": 5,
    "modelo": "M4",
    "rotor_grego": "Beta",
}


def executar_original(texto_cifrado, rotores, aneis, refletor, idioma, limite, rotor_grego, modelo=None):
    """Cópia fiel do laço anterior ao P1 de desempenho (não é usada pela API)."""
    inicio = time.perf_counter()
    texto = normalizar(texto_cifrado)
    aneis_motor = [anel - 1 for anel in aneis]
    nomes_rotores = (rotor_grego, *rotores)
    aneis_motor = [0, *aneis_motor]
    total = 26 ** 4
    combinacoes = product(range(26), repeat=4)

    maquina = Enigma(
        rotores=nomes_rotores,
        posicoes_rotores=[0] * 4,
        configuracoes_anel=aneis_motor,
        nome_refletor=refletor,
        conexoes_plugboard="",
    )
    principais = (maquina.rotor_esquerdo, maquina.rotor_central, maquina.rotor_direito)
    trecho = texto[:letras_para_pontuar]
    tempo_cifra = 0.0
    tempo_pontuacao = 0.0

    def pontuar_posicoes(posicoes):
        nonlocal tempo_cifra, tempo_pontuacao
        marca = time.perf_counter()
        maquina.rotor_grego.posicao_rotor = posicoes[0]
        for rotor, posicao in zip(principais, posicoes[1:]):
            rotor.posicao_rotor = posicao
        texto_teste = maquina.cifrar_texto(trecho)
        tempo_cifra += time.perf_counter() - marca
        marca = time.perf_counter()
        valor = pontuar_candidato(texto_teste, idioma)
        tempo_pontuacao += time.perf_counter() - marca
        return valor

    melhores = nlargest(limite, combinacoes, key=pontuar_posicoes)
    tempo_total = time.perf_counter() - inicio
    return {
        "tempo": tempo_total,
        "combinações": total,
        "letras_por_combinação": len(trecho),
        "tempo_cifra": tempo_cifra,
        "tempo_pontuação": tempo_pontuacao,
        # ordem igual à da API: três rotores principais + rotor grego
        "melhores": ["".join(ALFABETO[i] for i in pos[1:] + pos[:1]) for pos in melhores],
    }


def executar_acelerado(texto_cifrado, limite, **busca):
    """Chama a implementação atual do projeto."""
    inicio = time.perf_counter()
    resultado = atacar_posicoes(texto_cifrado, limite=limite, **busca)
    return {
        "tempo": time.perf_counter() - inicio,
        "combinações": resultado["combinacoes_testadas"],
        "letras_por_combinação": min(letras_para_pontuar, len(normalizar(texto_cifrado))),
        "tempo_cifra": None,
        "tempo_pontuação": None,
        "melhores": [c["posicoes"] + c["posicao_grega"] for c in resultado["candidatos"]],
    }


def main():
    repeticoes = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    cifrado = Enigma(**CONFIG_VERDADEIRA).cifrar_texto(MENSAGEM)
    esperado = "DTC" + "L"  # posições D-T-C + rotor grego L

    print(f"Mensagem: {MENSAGEM} ({len(MENSAGEM)} letras)")
    print(f"Configuração verdadeira: posições DTC, rotor grego L, "
          f"anéis 1-8-14-21, refletor Bfino, plugboard vazio")
    print(f"Repetições por versão: {repeticoes}\n")

    for nome, funcao in (
        ("original (antes do P1)", lambda: executar_original(cifrado, **BUSCA)),
        ("acelerado (atual)", lambda: executar_acelerado(cifrado, **BUSCA)),
    ):
        execuções = [funcao() for _ in range(repeticoes)]
        tempos = [execução["tempo"] for execução in execuções]
        melhor = min(tempos)
        media = sum(tempos) / len(tempos)
        por_comb = melhor / execuções[0]["combinações"] * 1e6
        achou = esperado in [m if isinstance(m, str) else m for m in execuções[-1]["melhores"]]
        posicao = (
            execuções[-1]["melhores"].index(esperado) + 1 if achou else None
        )
        print(f"[{nome}]")
        print(f"  tempo: mínimo {melhor:.2f} s | média {media:.2f} s")
        print(f"  combinações: {execuções[0]['combinações']} | "
              f"letras/combinação: {execuções[0]['letras_por_combinação']} | "
              f"{por_comb:.1f} µs/combinação")
        if execuções[0]["tempo_cifra"] is not None:
            ref = execuções[0]
            print(f"  divisão do tempo (última execução): cifra "
                  f"{ref['tempo_cifra']:.2f} s | pontuação {ref['tempo_pontuação']:.2f} s")
        print(f"  candidato correto ({esperado}) no ranking: "
              f"{f'posição {posicao}' if posicao else 'AUSENTE'}\n")


if __name__ == "__main__":
    main()