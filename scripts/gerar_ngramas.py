"""Gera tabelas de trigramas e quadrigramas a partir de corpora reais (Project Gutenberg)."""
import unicodedata, json, re
from collections import Counter

def limpar(caminho):
    with open(caminho, encoding="utf-8", errors="ignore") as arq:
        bruto = arq.read()
    # remove cabeçalho/rodapé do Gutenberg
    bruto = re.sub(r"\*\*\* ?START OF.*?\*\*\*", "", bruto, flags=re.S)
    bruto = re.sub(r"\*\*\* ?END OF.*?\*\*\*", "", bruto, flags=re.S)
    texto = unicodedata.normalize("NFKD", bruto.upper())
    texto = "".join(l for l in texto if not unicodedata.combining(l))
    return "".join(l for l in texto if "A" <= l <= "Z")

pt = "".join(limpar(f"corpora/pg{id}.txt") for id in (55752, 33056, 29040, 38496, 44540))
en = "".join(limpar(f"corpora/pg{id}.txt") for id in (1342, 84, 1661, 2701))

def contar(texto, n):
    return Counter(texto[i:i+n] for i in range(len(texto) - n + 1))

def pesos(contagem, top):
    total = sum(contagem.values())
    mais_comum = contagem.most_common(1)[0][1]
    saida = {}
    for seq, qtd in contagem.most_common(top):
        peso = max(1, round(9 * qtd / mais_comum))
        saida[seq] = peso
    return saida, total

tabelas = {}
for idioma, texto in (("pt", pt), ("en", en)):
    tri, _ = pesos(contar(texto, 3), 300)
    quad, _ = pesos(contar(texto, 4), 300)
    tabelas[idioma] = {"trigramas": tri, "quadrigramas": quad, "letras": len(texto)}
    print(idioma, "letras:", len(texto), "| top5 tri:", list(tri.items())[:5])

with open("corpora/tabelas.json", "w") as arq:
    json.dump(tabelas, arq)
