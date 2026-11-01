"""Gera contagens de trigramas e quadrigramas a partir dos corpora Gutenberg."""
import re, unicodedata, json
from collections import Counter

def limpar(caminho):
    with open(caminho, encoding="utf-8", errors="ignore") as arq:
        bruto = arq.read()
    bruto = re.sub(r"\*\*\* ?START OF.*?\*\*\*", "", bruto, flags=re.S)
    bruto = re.sub(r"\*\*\* ?END OF.*?\*\*\*", "", bruto, flags=re.S)
    texto = unicodedata.normalize("NFKD", bruto.upper())
    texto = "".join(l for l in texto if not unicodedata.combining(l))
    return "".join(l for l in texto if "A" <= l <= "Z")

def chaves(texto, n):
    return [((a*26+b)*26+c)[0] if n == 3 else None for a in [0]]  # placeholder

def contar(texto, n):
    codigos = [ord(c) - 65 for c in texto]
    contagem = Counter()
    chave = 0
    for i, v in enumerate(codigos):
        chave = (chave * 26 + v) % (26 ** n)
        if i >= n - 1:
            contagem[chave] += 1
    return contagem

saida = {}
for idioma, arquivos in (
    ("pt", (55752, 33056, 29040, 38496, 44540)),
    ("en", (1342, 84, 1661, 2701)),
):
    texto = "".join(limpar(f"corpora/pg{id}.txt") for id in arquivos)
    tri = contar(texto, 3)
    quad = contar(texto, 4)
    saida[idioma] = {
        "trigramas": {str(k): v for k, v in tri.items()},
        "total_trigramas": sum(tri.values()),
        "quadrigramas": {str(k): v for k, v in quad.items()},
        "total_quadrigramas": sum(quad.values()),
        "letras": len(texto),
    }
    print(idioma, "letras", len(texto), "| trigramas distintos", len(tri), "| quadrigramas distintos", len(quad))

with open("corpora/modelo_ngramas.json", "w") as arq:
    json.dump(saida, arq)
print("salvo em corpora/modelo_ngramas.json")
