"""Mede a busca ampliada/avançada com vetores cifrados pelo motor real.

Uso: python scripts/benchmark_busca_ampliada.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from busca_configuracoes import investigar  # noqa: E402
from enigma import Enigma  # noqa: E402

texto = ("OATAQUEAONORTEACONTECERAOAMANHECERCONFIRMADAPORNOSSASRADASRELATORIOS"
         "DAESQUADRILHAAEREAINDICAMQUEOFORTINHAPROVISOESCOMIDASPARAOINIMIGO"
         "OCOMANDANTEDETERMINOUQUEASTROPASAVANCEMPELAESTRADADOLITORALASSIMQUE"
         "AMANHECERESEMQUALQUERCOMUNICACAOPORRADIOATEACHEGADA")

casos = [
    ("Ampliada M3 · ordem+refletor+posições desconhecidos", "ampliada", "M3",
     (("V", "I", "VII"), (7, 20, 3), (0, 4, 11), "C", ""), {"aneis": (1, 5, 12)}, texto[:133]),
    ("Ampliada M4 · grego+pos. grega+refletor desconhecidos, plug conhecido", "ampliada", "M4",
     (("Gamma", "II", "IV", "VI"), (9, 1, 15, 22), (0, 2, 7, 19), "Cfino", "AV BS CG DT"),
     {"rotores": ("II", "IV", "VI"), "aneis": (3, 8, 20), "plugboard_modo": "conhecido", "plugboard": "AV BS CG DT"}, texto[:133]),
    ("Avançada M3 · tudo menos plug desconhecido (anéis heurísticos)", "avancada", "M3",
     (("IV", "I", "II"), (5, 12, 20), (0, 6, 17), "B", ""), {}, texto),
    ("Avançada M3 · anéis + plugboard (6 pares) desconhecidos", "avancada", "M3",
     (("V", "II", "VIII"), (4, 11, 23), (0, 9, 15), "B", "AM BX CQ DL EV FZ"),
     {"rotores": ("V", "II", "VIII"), "plugboard_modo": "desconhecido"}, texto),
    ("Avançada M3 · anéis + plugboard (8 pares) desconhecidos", "avancada", "M3",
     (("III", "VII", "II"), (20, 5, 13), (0, 21, 2), "C", "AE BJ CY DK FO GW HU LT"),
     {"rotores": ("III", "VII", "II"), "plugboard_modo": "desconhecido"}, texto),
]

for nome, modo, modelo, (rot, pos, an, refl, plug), conhecidos, texto in casos:
    cifra = Enigma(rot, pos, an, refl, plug).cifrar_texto(texto)
    inicio = time.perf_counter()
    r = investigar(modo, cifra, modelo, "pt", conhecidos, limite=3)
    dt = time.perf_counter() - inicio
    melhor = r["candidatos"][0]
    acertos = sum(a == b for a, b in zip(melhor["texto"], texto))
    print(f"{nome}\n  {dt:6.1f} s · {r['combinacoes_testadas']:>11,} avaliações · "
          f"{r['combinacoes_testadas']/dt/1e6:.2f} M/s · método {r['metodo']} · "
          f"texto recuperado {acertos}/{len(texto)}".replace(",", "."))
