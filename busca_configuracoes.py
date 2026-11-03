"""Busca automática de configurações Enigma M3/M4.

Três modos (ver investigar()):

- "configurada": delega a criptoanalise.atacar_posicoes — todas as
  posições iniciais para rotores, anéis, refletor e plugboard informados.
- "ampliada": enumeração EXAUSTIVA das dimensões declaradas desconhecidas
  (ordem dos rotores, refletor, rotor grego e sua posição, posições
  iniciais e, opcionalmente, anéis central/direito). Plugboard conhecido
  ou vazio.
- "avancada": criptoanálise HEURÍSTICA para anéis e plugboard
  desconhecidos: (1) triagem exaustiva de ordem/refletor/posições com
  anéis provisórios, pontuada pelo índice de coincidência (robusto ao
  plugboard desconhecido); (2) refinamento de anéis nos melhores
  candidatos; (3) subida de encosta (hill climbing) no plugboard;
  (4) refinamento final. NÃO é enumeração de todas as chaves.

Precisão: o avaliador vetorizado reproduz o caminho elétrico do motor
(fiação, anéis, duplo passo, rotor grego estático + refletor fino,
plugboard) e é usado apenas para TRIAGEM. Toda configuração final é
decifrada pelo motor real (enigma.Enigma) e pontuada por
criptoanalise.pontuar_candidato; além disso, o prefixo decifrado pelo
avaliador é comparado ao do motor e qualquer divergência interrompe a
busca com erro (nunca se declara uma chave a partir de aproximação).

Equivalências documentadas (não reduzem a cobertura de textos):
- Anel do rotor ESQUERDO: deslocar posição e anel juntos produz a mesma
  máquina (o rotor esquerdo só avança pelo duplo passo e seu entalhe não
  aciona nada). Por isso, ao buscar anéis, o anel esquerdo fica em 1.
- Anel do rotor GREGO: o grego nunca avança; anel e posição são
  equivalentes. O anel grego fica em 1 e só a posição é buscada.
A chave recuperada pode, portanto, diferir da original nesses dois
parâmetros e ainda assim decifrar exatamente o mesmo texto.
"""

import heapq
import time
from itertools import permutations
from string import ascii_uppercase

import numpy as np

from criptoanalise import (
    BuscaCancelada,
    letras_para_pontuar,
    rotores_gregos,
    rotores_principais,
    vies_idioma,
    atacar_posicoes,
    pontuar_candidato,
)
from enigma import Enigma
from plugboard import Plugboard
from pontuacao import tabelas_quad, normalizar
from refletor import Refletor
from rotor import Rotor

alfabeto = ascii_uppercase
modos_busca = ("configurada", "ampliada", "avancada")
refletores_por_modelo = {"M3": ("B", "C"), "M4": ("Bfino", "Cfino")}
posicoes_por_bloco = 26 ** 3

# Orçamento da enumeração exaustiva (configurações completas avaliadas).
# Medido neste projeto: ~0,4-0,6 milhão de configurações/s com 150 letras
# (ver scripts/benchmark_busca_ampliada.py). 60 milhões ~ 2-3 minutos.
orcamento_exaustivo = 60_000_000
# O modo avançado faz uma triagem inicial exaustiva e refina anéis/plugboard
# apenas nos melhores candidatos. A triagem M4 sem parâmetros conhecidos tem
# 614.175.744 configurações; este teto permite esse caso em tarefa de fundo,
# sem permitir a enumeração completa das centenas de bilhões de chaves.
orcamento_triagem_avancada = 650_000_000

# Parâmetros da heurística (criptoanálise avançada).
candidatos_triagem = 40
candidatos_aneis = 8
letras_plugboard = 400
max_pares_plugboard = 10
min_letras_plugboard = 100

_quad = {
    idioma: np.frombuffer(tabela, dtype=np.int32).copy()
    for idioma, tabela in tabelas_quad.items()
}
_indices = np.indices((26, 26, 26)).reshape(3, -1).astype(np.int64)
_caches_passos = {}


# ----------------------------------------------------------------------
# Enumeração do espaço de busca
# ----------------------------------------------------------------------

def permutacoes_rotores(rotores_conhecidos=None):
    """Ordens dos três rotores principais (336 sem repetição entre I-VIII)."""
    if rotores_conhecidos:
        return [tuple(rotores_conhecidos)]
    return list(permutations(rotores_principais, 3))


def refletores_compativeis(modelo, refletor_conhecido=None):
    """Refletores compatíveis: M3 → B, C; M4 → Bfino, Cfino."""
    validos = refletores_por_modelo[modelo]
    if refletor_conhecido:
        if refletor_conhecido not in validos:
            raise ValueError(
                f"O refletor {refletor_conhecido} não é compatível com a {modelo}."
            )
        return [refletor_conhecido]
    return list(validos)


def gregos_compativeis(modelo, grego_conhecido=None):
    """Rotores gregos (somente M4): Beta e Gamma."""
    if modelo != "M4":
        return [None]
    if grego_conhecido:
        if grego_conhecido not in rotores_gregos:
            raise ValueError("Na M4, o rotor grego deve ser Beta ou Gamma.")
        return [grego_conhecido]
    return list(rotores_gregos)


def combinacoes_aneis(aneis_conhecidos=None):
    """Anéis (1-26). Conhecidos → 1 combinação; buscados → 676 (central ×
    direito), anel esquerdo em 1 por equivalência (ver docstring)."""
    if aneis_conhecidos:
        return [tuple(aneis_conhecidos)]
    return [(1, m, d) for m in range(1, 27) for d in range(1, 27)]


def descrever_espaco(modelo, conhecidos, modo):
    """Dimensões, tamanhos e natureza (exaustiva/heurística/fixa) da busca."""
    ordens = len(permutacoes_rotores(conhecidos.get("rotores")))
    refls = len(refletores_compativeis(modelo, conhecidos.get("refletor")))
    gregos = len(gregos_compativeis(modelo, conhecidos.get("rotor_grego")))
    pos_grego = 26 if modelo == "M4" else 1
    aneis_buscados = conhecidos.get("aneis") is None
    plug = conhecidos.get("plugboard_modo", "vazio")

    dimensoes = [
        {"nome": "Ordem dos rotores", "tamanho": ordens,
         "tipo": "fixa" if ordens == 1 else "exaustiva"},
        {"nome": "Refletor", "tamanho": refls,
         "tipo": "fixa" if refls == 1 else "exaustiva"},
    ]
    if modelo == "M4":
        dimensoes.append({"nome": "Rotor grego", "tamanho": gregos,
                          "tipo": "fixa" if gregos == 1 else "exaustiva"})
        dimensoes.append({"nome": "Posição do rotor grego", "tamanho": 26,
                          "tipo": "exaustiva"})
    dimensoes.append({"nome": "Posições iniciais (3 rotores)",
                      "tamanho": posicoes_por_bloco, "tipo": "exaustiva"})

    blocos_por_anel = ordens * refls * gregos * pos_grego
    if not aneis_buscados:
        dimensoes.append({"nome": "Anéis", "tamanho": 1, "tipo": "fixa"})
        fator_aneis = 1
    elif modo == "ampliada":
        dimensoes.append({"nome": "Anéis central × direito (esquerdo=1, equivalente)",
                          "tamanho": 676, "tipo": "exaustiva"})
        fator_aneis = 676
    else:
        base = blocos_por_anel * posicoes_por_bloco
        if base * 26 <= orcamento_exaustivo:
            dimensoes.append({"nome": "Anel direito (triagem)", "tamanho": 26, "tipo": "exaustiva",
                              "detalhe": "varrido na triagem por controlar o avanço do rotor central"})
            dimensoes.append({"nome": "Anel central", "tamanho": 26, "tipo": "heurística",
                              "detalhe": f"refinado apenas nos {candidatos_triagem} melhores candidatos"})
            fator_aneis = 26
        else:
            dimensoes.append({"nome": "Anéis central × direito", "tamanho": 676, "tipo": "heurística",
                              "detalhe": f"triagem com anéis 1-1-1; refinados apenas nos {candidatos_triagem} melhores candidatos"})
            fator_aneis = 1

    if plug == "desconhecido":
        dimensoes.append({"nome": "Plugboard", "tamanho": None, "tipo": "heurística",
                          "detalhe": f"subida de encosta até {max_pares_plugboard} pares nos melhores candidatos"})
    else:
        dimensoes.append({"nome": "Plugboard", "tamanho": 1, "tipo": "fixa",
                          "detalhe": "conhecido" if plug == "conhecido" else "vazio"})

    total_exaustivo = blocos_por_anel * fator_aneis * posicoes_por_bloco
    heuristica = modo == "avancada" and (aneis_buscados or plug == "desconhecido")
    orcamento_aplicavel = (
        orcamento_triagem_avancada if modo == "avancada" else orcamento_exaustivo
    )
    return {
        "modelo": modelo,
        "modo": modo,
        "dimensoes": dimensoes,
        "configuracoes_exaustivas": total_exaustivo,
        "orcamento": orcamento_aplicavel,
        "dentro_do_orcamento": total_exaustivo <= orcamento_aplicavel,
        "heuristica": heuristica,
        "nota_escopo": (
            "No modo avançado, esta contagem cobre a triagem inicial; anéis e/ou plugboard "
            "podem ser refinados heuristicamente nos melhores candidatos. Não é uma enumeração "
            "de todas as chaves completas."
            if modo == "avancada" and heuristica else None
        ),
    }


# ----------------------------------------------------------------------
# Avaliador vetorizado (TRIAGEM) — equivalente ao motor, verificado
# ----------------------------------------------------------------------

def _fiacao(nome):
    fiacao, entalhes = Rotor.dados_rotores[nome]
    direto = np.array([ord(c) - 65 for c in fiacao], dtype=np.int64)
    reverso = np.argsort(direto)
    return direto, reverso, tuple(ord(c) - 65 for c in entalhes)


def _tabelas(nome, anel_motor):
    """Tabelas [posição][entrada] de ida e volta já com o anel (0-25)."""
    direto, reverso, _ = _fiacao(nome)
    pos = np.arange(26)[:, None]
    ent = np.arange(26)[None, :]
    desl = (pos - anel_motor) % 26
    return (direto[(ent + desl) % 26] - desl) % 26, (reverso[(ent + desl) % 26] - desl) % 26


def _caminho_fixo(refletor, grego, pos_grego):
    """Refletor (M3) ou rotor grego estático + refletor fino (M4)."""
    refl = np.array(Refletor.criar_refletor(refletor).mapeamento_direto, dtype=np.int64)
    if grego is None:
        return refl
    ida, volta = _tabelas(grego, 0)  # anel grego 1 (equivalente — docstring)
    return volta[pos_grego][refl[ida[pos_grego]]]


def _tabela_embaralhador(ordem, aneis_motor, fixo):
    """S[(pl*26+pm)*26+pr][x]: saída do embaralhador (sem plugboard)."""
    pl, pm, pr = _indices
    (fl, rl), (fm, rm), (fr, rr) = (
        _tabelas(nome, anel) for nome, anel in zip(ordem, aneis_motor)
    )
    x = np.arange(26)[None, :]
    v = fr[pr[:, None], x]
    v = fm[pm[:, None], v]
    v = fl[pl[:, None], v]
    v = fixo[v]
    v = rl[pl[:, None], v]
    v = rm[pm[:, None], v]
    v = rr[pr[:, None], v]
    return v.astype(np.int64).ravel()


def _passos(entalhes_central, entalhes_direito, n):
    """Índice da janela (pl,pm,pr) em cada passo, para as 17.576 partidas.

    Mesmo avanço de Enigma.girar_rotores: central no entalhe → esquerdo e
    central avançam (duplo passo); senão, direito no entalhe → central
    avança; o direito avança sempre. Depende só dos entalhes (janela).
    """
    chave = (entalhes_central, entalhes_direito, n)
    if chave in _caches_passos:
        return _caches_passos[chave]
    pl, pm, pr = (eixo.copy() for eixo in _indices)
    saida = np.empty((posicoes_por_bloco, n), dtype=np.int64)
    ent_c = np.array(entalhes_central)
    ent_d = np.array(entalhes_direito)
    for t in range(n):
        no_central = np.isin(pm, ent_c)
        no_direito = np.isin(pr, ent_d)
        pl = (pl + no_central) % 26
        pm = (pm + (no_central | no_direito)) % 26
        pr = (pr + 1) % 26
        saida[:, t] = ((pl * 26 + pm) * 26 + pr) * 26
    if len(_caches_passos) > 24:
        _caches_passos.clear()
    _caches_passos[chave] = saida
    return saida


def decifrar_bloco(ordem, aneis, refletor, grego, pos_grego, plug, cifra):
    """Decifra as 17.576 posições iniciais de uma configuração (triagem)."""
    aneis_motor = [a - 1 for a in aneis]
    fixo = _caminho_fixo(refletor, grego, pos_grego)
    tabela = _tabela_embaralhador(ordem, aneis_motor, fixo)
    passos = _passos(_fiacao(ordem[1])[2], _fiacao(ordem[2])[2], len(cifra))
    entrada = plug[cifra]
    return plug[tabela[passos + entrada[None, :]]]


def pontuar_quad(matriz, idioma):
    """Média de quadrigramas (máximo entre idiomas, viés ao selecionado) —
    mesma base de pontuar_candidato, sem o bônus de palavras (a pontuação
    final exata é sempre feita por pontuar_candidato)."""
    n = matriz.shape[1]
    if n < 4:
        return np.zeros(matriz.shape[0])
    chaves = ((matriz[:, :-3] * 26 + matriz[:, 1:-2]) * 26 + matriz[:, 2:-1]) * 26 + matriz[:, 3:]
    outro = "en" if idioma == "pt" else "pt"
    sel = _quad[idioma][chaves].sum(axis=1) / (n - 3) + vies_idioma * n
    out = _quad[outro][chaves].sum(axis=1) / (n - 3)
    return np.maximum(sel, out)


def indice_coincidencia(matriz):
    """Índice de coincidência por linha (insensível a permutações de letras,
    por isso útil com plugboard desconhecido)."""
    linhas, n = matriz.shape
    plano = (matriz + (np.arange(linhas) * 26)[:, None]).ravel()
    contagens = np.bincount(plano, minlength=linhas * 26).reshape(linhas, 26)
    return (contagens * (contagens - 1)).sum(axis=1) / max(n * (n - 1), 1)


def decifrar_variantes(ordem, aneis, posicoes, refletor, grego, pos_grego, plug, cifra):
    """Decifra M configurações explícitas da MESMA ordem (vetorizado em M).

    aneis e posicoes: arrays (M, 3) em 0-25. Usado no refinamento de anéis.
    """
    (fd_l, fr_l, _), (fd_m, fr_m, ent_m), (fd_r, fr_r, ent_r) = (_fiacao(n) for n in ordem)
    fixo = _caminho_fixo(refletor, grego, pos_grego)
    pl, pm, pr = (posicoes[:, i].copy() for i in range(3))
    al, am, ar = (aneis[:, i] for i in range(3))
    ent_m, ent_r = np.array(ent_m), np.array(ent_r)
    saida = np.empty((posicoes.shape[0], len(cifra)), dtype=np.int64)
    for t, letra in enumerate(cifra):
        no_central = np.isin(pm, ent_m)
        no_direito = np.isin(pr, ent_r)
        pl = (pl + no_central) % 26
        pm = (pm + (no_central | no_direito)) % 26
        pr = (pr + 1) % 26
        dr, dm, dl = (pr - ar) % 26, (pm - am) % 26, (pl - al) % 26
        v = np.full(posicoes.shape[0], plug[letra], dtype=np.int64)
        v = (fd_r[(v + dr) % 26] - dr) % 26
        v = (fd_m[(v + dm) % 26] - dm) % 26
        v = (fd_l[(v + dl) % 26] - dl) % 26
        v = fixo[v]
        v = (fr_l[(v + dl) % 26] - dl) % 26
        v = (fr_m[(v + dm) % 26] - dm) % 26
        v = (fr_r[(v + dr) % 26] - dr) % 26
        saida[:, t] = plug[v]
    return saida


def permutacoes_por_passo(ordem, aneis, posicoes, refletor, grego, pos_grego, n):
    """Permutação do embaralhador (sem plugboard) em cada passo: (n, 26).

    Mesmo avanço e caminho elétrico do motor; usada pela subida de encosta
    do plugboard, que só troca as letras antes/depois do embaralhador.
    """
    (fd_l, fr_l, _), (fd_m, fr_m, ent_m), (fd_r, fr_r, ent_r) = (_fiacao(nome) for nome in ordem)
    fixo = _caminho_fixo(refletor, grego, pos_grego)
    pl, pm, pr = posicoes
    al, am, ar = (a - 1 for a in aneis)
    identidade = np.arange(26)
    sequencia = np.empty((n, 26), dtype=np.int64)
    for t in range(n):
        if pm in ent_m:
            pl, pm = (pl + 1) % 26, (pm + 1) % 26
        elif pr in ent_r:
            pm = (pm + 1) % 26
        pr = (pr + 1) % 26
        dr, dm, dl = (pr - ar) % 26, (pm - am) % 26, (pl - al) % 26
        v = (fd_r[(identidade + dr) % 26] - dr) % 26
        v = (fd_m[(v + dm) % 26] - dm) % 26
        v = (fd_l[(v + dl) % 26] - dl) % 26
        v = fixo[v]
        v = (fr_l[(v + dl) % 26] - dl) % 26
        v = (fr_m[(v + dm) % 26] - dm) % 26
        v = (fr_r[(v + dr) % 26] - dr) % 26
        sequencia[t] = v
    return sequencia


# ----------------------------------------------------------------------
# Plugboard: conversões e subida de encosta (heurística)
# ----------------------------------------------------------------------

def plug_de_texto(conexoes):
    return np.array(Plugboard(conexoes or "").mapeamento, dtype=np.int64)


def texto_de_plug(plug):
    pares = sorted(
        alfabeto[a] + alfabeto[b] for a, b in enumerate(plug) if a < b
    )
    return " ".join(pares)


_PARES = [(a, b) for a in range(26) for b in range(a + 1, 26)]


def _vizinhos(plug, max_pares):
    """Plugboards vizinhos: conectar, desconectar ou reconectar um par."""
    vizinhos = []
    pares_atuais = int((plug != np.arange(26)).sum() // 2)
    for a, b in _PARES:
        novo = plug.copy()
        if plug[a] == b:
            novo[a], novo[b] = a, b
        else:
            x, y = plug[a], plug[b]
            if x != a:
                novo[x], novo[a] = x, a
            if y != b:
                novo[y], novo[b] = y, b
            novo[a], novo[b] = b, a
            liberados = (x != a) + (y != b)
            if pares_atuais + 1 - liberados > max_pares:
                continue
        vizinhos.append(novo)
    return np.array(vizinhos)


def _decifrar_com_plugs(sequencia, cifra, plugs):
    """Decifra o mesmo trecho com K plugboards (K, n)."""
    entrada = plugs[:, cifra]
    meio = sequencia[np.arange(len(cifra))[None, :], entrada]
    return np.take_along_axis(plugs, meio, axis=1)


def subir_encosta_plugboard(sequencia, cifra, idioma, plug_inicial=None,
                            max_pares=max_pares_plugboard, cancelado=None):
    """Hill climbing no plugboard: IC primeiro, depois quadrigramas.

    Heurística: não garante o ótimo global e não enumera plugboards.
    Devolve (plug, pontuação, avaliações realizadas).
    """
    plug = np.arange(26) if plug_inicial is None else plug_inicial.copy()
    avaliacoes = 0
    for medida in (indice_coincidencia, lambda m: pontuar_quad(m, idioma)):
        atual = medida(_decifrar_com_plugs(sequencia, cifra, plug[None, :]))[0]
        for _ in range(40):
            if cancelado is not None and cancelado():
                raise BuscaCancelada(avaliacoes)
            vizinhos = _vizinhos(plug, max_pares)
            notas = medida(_decifrar_com_plugs(sequencia, cifra, vizinhos))
            avaliacoes += len(vizinhos)
            melhor = int(np.argmax(notas))
            if notas[melhor] <= atual + 1e-12:
                break
            plug, atual = vizinhos[melhor], notas[melhor]
    return plug, float(atual), avaliacoes


# ----------------------------------------------------------------------
# Verificação final pelo motor real
# ----------------------------------------------------------------------

def _maquina(cfg):
    if cfg["grego"]:
        nomes = (cfg["grego"], *cfg["ordem"])
        posicoes = [cfg["pos_grego"], *cfg["posicoes"]]
        aneis = [0, *[a - 1 for a in cfg["aneis"]]]
    else:
        nomes = tuple(cfg["ordem"])
        posicoes = list(cfg["posicoes"])
        aneis = [a - 1 for a in cfg["aneis"]]
    return Enigma(nomes, posicoes, aneis, cfg["refletor"], cfg["plugboard"])


def verificar_no_motor(cfg, texto, idioma, metodo, escopo, prefixo_triagem=None):
    """Decifra com o motor real; confere a triagem; monta o candidato."""
    decifrado = _maquina(cfg).cifrar_texto(texto)
    if prefixo_triagem is not None:
        esperado = "".join(alfabeto[i] for i in prefixo_triagem)
        if decifrado[: len(esperado)] != esperado:
            raise RuntimeError(
                "Divergência entre o avaliador de triagem e o motor Enigma real; "
                "a busca foi interrompida para não declarar uma chave incorreta."
            )
    candidato = {
        "texto": decifrado,
        "modelo": "M4" if cfg["grego"] else "M3",
        "rotores": list(cfg["ordem"]),
        "posicoes": "".join(alfabeto[p] for p in cfg["posicoes"]),
        "aneis": list(cfg["aneis"]),
        "refletor": cfg["refletor"],
        "plugboard": cfg["plugboard"],
        "plugboard_recuperado": bool(cfg.get("plug_recuperado")),
        "idioma": idioma,
        "pontuacao": pontuar_candidato(decifrado, idioma),
        "metodo": metodo,
        "escopo": escopo,
        "verificado_no_motor": True,
    }
    if cfg["grego"]:
        candidato["rotor_grego"] = cfg["grego"]
        candidato["posicao_grega"] = alfabeto[cfg["pos_grego"]]
    return candidato


def _resumo_escopo(espaco):
    partes = []
    for d in espaco["dimensoes"]:
        tamanho = "?" if d["tamanho"] is None else f"{d['tamanho']:,}".replace(",", ".")
        partes.append(f"{d['nome']}: {tamanho} ({d['tipo']})")
    return "; ".join(partes)


# ----------------------------------------------------------------------
# Busca ampliada (exaustiva no escopo declarado)
# ----------------------------------------------------------------------

def _blocos(modelo, conhecidos):
    for ordem in permutacoes_rotores(conhecidos.get("rotores")):
        for refletor in refletores_compativeis(modelo, conhecidos.get("refletor")):
            for grego in gregos_compativeis(modelo, conhecidos.get("rotor_grego")):
                for pos_grego in (range(26) if grego else [None]):
                    yield ordem, refletor, grego, pos_grego


def _parciais_verificados(monte, plug_texto, texto, idioma, metodo, quantidade=3):
    """Melhores candidatos ATÉ AGORA, decifrados pelo motor real."""
    melhores = heapq.nlargest(quantidade, monte)
    return [
        verificar_no_motor(_cfg_de_item(item, plug_texto), texto, idioma, metodo,
                           "parcial — busca em andamento")
        for item in melhores
    ]


def _triagem(modelo, conhecidos, aneis_lista, plug, cifra, idioma, medida,
             capacidade, progresso, cancelado, fase, total, texto=None, plug_texto=""):
    """Percorre exaustivamente os blocos e mantém os melhores (heap)."""
    monte = []
    feitas = 0
    sequencia = 0
    ultimo_relato = 0.0
    for aneis in aneis_lista:
        for ordem, refletor, grego, pos_grego in _blocos(modelo, conhecidos):
            if cancelado is not None and cancelado():
                raise BuscaCancelada(feitas)
            matriz = decifrar_bloco(ordem, aneis, refletor, grego, pos_grego or 0, plug, cifra)
            notas = indice_coincidencia(matriz) if medida == "ic" else pontuar_quad(matriz, idioma)
            k = min(capacidade, len(notas))
            melhores = np.argpartition(notas, -k)[-k:]
            for indice in melhores:
                sequencia += 1
                item = (float(notas[indice]), -sequencia, (ordem, aneis, refletor, grego, pos_grego, int(indice)))
                if len(monte) < capacidade:
                    heapq.heappush(monte, item)
                elif item > monte[0]:
                    heapq.heapreplace(monte, item)
            feitas += posicoes_por_bloco
            agora = time.perf_counter()
            if progresso is not None and (agora - ultimo_relato > 0.5 or feitas == total):
                ultimo_relato = agora
                # Parciais só quando a medida é linguística (com plugboard
                # desconhecido o texto da triagem ainda é ilegível).
                parciais = (_parciais_verificados(monte, plug_texto, texto, idioma, "exaustiva")
                            if medida == "quad" and texto and monte else None)
                progresso({"fase": fase, "fase_feitas": feitas, "fase_total": total,
                           "avaliadas": feitas, "parciais": parciais})
            time.sleep(0)  # cede a vez a outras threads (servidor responsivo)
    return sorted(monte, reverse=True), feitas


def _cfg_de_item(item, plug_texto):
    _, _, (ordem, aneis, refletor, grego, pos_grego, indice) = item
    pl, pm, pr = indice // 676, (indice // 26) % 26, indice % 26
    return {"ordem": ordem, "aneis": tuple(aneis), "refletor": refletor,
            "grego": grego, "pos_grego": pos_grego if grego else None,
            "posicoes": (int(pl), int(pm), int(pr)), "plugboard": plug_texto}


def busca_ampliada(texto_cifrado, modelo, idioma, conhecidos, limite=10,
                   progresso=None, cancelado=None):
    """Enumeração exaustiva no escopo declarado (anéis e plugboard conhecidos
    ou anéis buscados exaustivamente; plugboard conhecido ou vazio)."""
    texto = normalizar(texto_cifrado)
    espaco = descrever_espaco(modelo, conhecidos, "ampliada")
    if conhecidos.get("plugboard_modo") == "desconhecido":
        raise ValueError("Plugboard desconhecido exige a criptoanálise avançada (heurística).")
    if not espaco["dentro_do_orcamento"]:
        raise ValueError(
            f"Escopo exaustivo de {espaco['configuracoes_exaustivas']:,} configurações excede o "
            f"limite de {orcamento_exaustivo:,} desta aplicação. Declare mais parâmetros como "
            "conhecidos (por exemplo, a ordem dos rotores ou os anéis) ou use a criptoanálise avançada."
            .replace(",", ".")
        )
    inicio = time.perf_counter()
    cifra = np.array([ord(c) - 65 for c in texto[:letras_para_pontuar]], dtype=np.int64)
    plug_texto = conhecidos.get("plugboard") or ""
    plug = plug_de_texto(plug_texto)
    total = espaco["configuracoes_exaustivas"]
    if progresso:
        progresso({"fase": ("Enumeração exaustiva", 1, 2), "fase_feitas": 0, "fase_total": total,
                   "avaliadas": 0, "parciais": []})
    capacidade = max(60, limite * 6)
    itens, feitas = _triagem(modelo, conhecidos, combinacoes_aneis(conhecidos.get("aneis")),
                             plug, cifra, idioma, "quad", capacidade, progresso, cancelado,
                             ("Enumeração exaustiva", 1, 2), total, texto, plug_texto)
    if progresso:
        progresso({"fase": ("Verificação no motor real", 2, 2), "fase_feitas": 0,
                   "fase_total": len(itens), "avaliadas": feitas, "parciais": None})
    escopo = _resumo_escopo(espaco)
    candidatos = []
    for item in itens:
        cfg = _cfg_de_item(item, plug_texto)
        prefixo = decifrar_variantes(cfg["ordem"], np.array([[a - 1 for a in cfg["aneis"]]]),
                                     np.array([cfg["posicoes"]]), cfg["refletor"], cfg["grego"],
                                     cfg["pos_grego"] or 0, plug, cifra[:40])[0]
        candidatos.append(verificar_no_motor(cfg, texto, idioma, "exaustiva", escopo, prefixo))
    candidatos.sort(key=lambda c: c["pontuacao"], reverse=True)
    return {
        "modo": "ampliada", "metodo": "exaustiva", "modelo": modelo, "idioma": idioma,
        "espaco": espaco, "combinacoes_testadas": feitas, "cobertura_completa": feitas == total,
        "tempo_segundos": round(time.perf_counter() - inicio, 3),
        "candidatos": _sem_duplicatas(candidatos)[:limite],
        "aviso": AVISO_ESTATISTICO,
    }


AVISO_ESTATISTICO = (
    "O melhor candidato é o mais provável segundo o modelo linguístico, não "
    "necessariamente a mensagem correta — sobretudo em textos curtos. "
    "Chaves equivalentes (anel esquerdo/grego deslocados junto com a posição) "
    "produzem exatamente o mesmo texto."
)


def _sem_duplicatas(candidatos):
    vistos, unicos = set(), []
    for c in candidatos:
        if c["texto"] in vistos:
            continue
        vistos.add(c["texto"])
        unicos.append(c)
    return unicos


# ----------------------------------------------------------------------
# Criptoanálise avançada (heurística)
# ----------------------------------------------------------------------

def criptoanalise_avancada(texto_cifrado, modelo, idioma, conhecidos, limite=10,
                           progresso=None, cancelado=None):
    texto = normalizar(texto_cifrado)
    plug_desconhecido = conhecidos.get("plugboard_modo") == "desconhecido"
    aneis_desconhecidos = conhecidos.get("aneis") is None
    if plug_desconhecido and len(texto) < min_letras_plugboard:
        raise ValueError(
            f"Com plugboard desconhecido, a heurística precisa de pelo menos "
            f"{min_letras_plugboard} letras (o índice de coincidência não discrimina "
            "candidatos em textos curtos)."
        )
    espaco = descrever_espaco(modelo, conhecidos, "avancada")
    if not espaco["dentro_do_orcamento"]:
        raise ValueError(
            f"A triagem exaustiva da fase 1 teria {espaco['configuracoes_exaustivas']:,} "
            f"configurações (limite {espaco['orcamento']:,}). Declare mais parâmetros conhecidos "
            "ou reduza o escopo da busca."
            .replace(",", ".")
        )
    inicio = time.perf_counter()
    letras = letras_plugboard if plug_desconhecido else letras_para_pontuar
    cifra_total = np.array([ord(c) - 65 for c in texto[:letras]], dtype=np.int64)
    cifra = cifra_total[:max(letras_para_pontuar, 0)] if not plug_desconhecido else cifra_total[:300]
    plug_texto = "" if plug_desconhecido else (conhecidos.get("plugboard") or "")
    plug = plug_de_texto(plug_texto)
    medida = "ic" if plug_desconhecido else "quad"
    if not aneis_desconhecidos:
        aneis_base = [tuple(conhecidos["aneis"])]
    elif any(d["nome"] == "Anel direito (triagem)" for d in espaco["dimensoes"]):
        aneis_base = [(1, 1, d) for d in range(1, 27)]
    else:
        aneis_base = [(1, 1, 1)]
    total_fases = 2 + int(aneis_desconhecidos) + int(plug_desconhecido)
    total1 = espaco["configuracoes_exaustivas"]
    fase_n = 1

    itens, feitas = _triagem(modelo, conhecidos, aneis_base, plug, cifra, idioma, medida,
                             candidatos_triagem, progresso, cancelado,
                             ("Triagem exaustiva de ordem, refletor e posições", 1, total_fases), total1,
                             texto, plug_texto)
    avaliadas = feitas
    cfgs = [_cfg_de_item(item, plug_texto) for item in itens]

    # Fase 2 — anéis (heurística: só nos melhores candidatos da triagem).
    if aneis_desconhecidos:
        fase_n += 1
        deltas = np.array([(0, m, d) for m in range(26) for d in range(26)])
        refinados = []
        for numero, cfg in enumerate(cfgs, 1):
            if cancelado is not None and cancelado():
                raise BuscaCancelada(avaliadas)
            base_an = np.array([a - 1 for a in cfg["aneis"]])
            posicoes = (np.array(cfg["posicoes"])[None, :] + deltas) % 26
            aneis_v = (base_an[None, :] + deltas) % 26
            matriz = decifrar_variantes(cfg["ordem"], aneis_v, posicoes, cfg["refletor"],
                                        cfg["grego"], cfg["pos_grego"] or 0, plug, cifra)
            notas = indice_coincidencia(matriz) if medida == "ic" else pontuar_quad(matriz, idioma)
            avaliadas += len(deltas)
            for indice in np.argsort(notas)[-3:]:
                novo = dict(cfg)
                novo["posicoes"] = tuple(int(v) for v in posicoes[indice])
                novo["aneis"] = tuple(int(v) + 1 for v in aneis_v[indice])
                refinados.append((float(notas[indice]), novo))
            if progresso:
                progresso({"fase": ("Refinamento de anéis (heurístico)", fase_n, total_fases),
                           "fase_feitas": numero, "fase_total": len(cfgs),
                           "avaliadas": avaliadas, "parciais": None})
        refinados.sort(key=lambda par: par[0], reverse=True)
        cfgs = [cfg for _, cfg in refinados[:candidatos_aneis]]
    else:
        cfgs = cfgs[:candidatos_aneis]

    # Fase 3 — plugboard (subida de encosta).
    if plug_desconhecido:
        fase_n += 1
        recuperados = []
        for numero, cfg in enumerate(cfgs, 1):
            sequencia = permutacoes_por_passo(cfg["ordem"], cfg["aneis"], cfg["posicoes"],
                                              cfg["refletor"], cfg["grego"], cfg["pos_grego"] or 0,
                                              len(cifra_total))
            plug_r, nota, n_aval = subir_encosta_plugboard(sequencia, cifra_total, idioma,
                                                           cancelado=cancelado)
            avaliadas += n_aval
            # Refinamento: anéis de novo, agora com o plugboard recuperado.
            if aneis_desconhecidos:
                # Anéis central/direito (com a posição deslocada junto) e a
                # posição do rotor esquerdo ±1, que o duplo passo pode
                # desalinhar quando o anel central muda.
                deltas = np.array([(0, m, d) for m in range(26) for d in range(26)])
                base_an = np.array([a - 1 for a in cfg["aneis"]])
                ajustes = np.array([(e, m, 0) for e in (0, 1, 25) for m in (0, 1, 25)])
                aneis_v = np.tile((base_an[None, :] + deltas) % 26, (len(ajustes), 1))
                ajuste_pos = np.repeat(ajustes, len(deltas), axis=0)
                posicoes = (np.array(cfg["posicoes"])[None, :] + np.tile(deltas, (len(ajustes), 1)) + ajuste_pos) % 26
                deltas = aneis_v
                matriz = decifrar_variantes(cfg["ordem"], aneis_v, posicoes, cfg["refletor"],
                                            cfg["grego"], cfg["pos_grego"] or 0, plug_r, cifra_total)
                notas = pontuar_quad(matriz, idioma)
                avaliadas += len(deltas)
                melhor = int(np.argmax(notas))
                cfg = dict(cfg)
                cfg["aneis"] = tuple(int(v) + 1 for v in aneis_v[melhor])
                cfg["posicoes"] = tuple(int(v) for v in posicoes[melhor])
                sequencia = permutacoes_por_passo(cfg["ordem"], cfg["aneis"], cfg["posicoes"],
                                                  cfg["refletor"], cfg["grego"], cfg["pos_grego"] or 0,
                                                  len(cifra_total))
                plug_r, nota, n_aval = subir_encosta_plugboard(sequencia, cifra_total, idioma,
                                                               plug_inicial=plug_r, cancelado=cancelado)
                avaliadas += n_aval
            cfg = dict(cfg)
            cfg["plugboard"] = texto_de_plug(plug_r)
            cfg["plug_recuperado"] = True
            recuperados.append(cfg)
            if progresso:
                progresso({"fase": ("Plugboard por subida de encosta (heurístico)", fase_n, total_fases),
                           "fase_feitas": numero, "fase_total": len(cfgs),
                           "avaliadas": avaliadas, "parciais": None})
        cfgs = recuperados

    fase_n += 1
    if progresso:
        progresso({"fase": ("Verificação no motor real", fase_n, total_fases), "fase_feitas": 0,
                   "fase_total": len(cfgs), "avaliadas": avaliadas, "parciais": None})
    escopo = _resumo_escopo(espaco)
    metodo = "heuristica" if espaco["heuristica"] else "exaustiva"
    candidatos = [verificar_no_motor(cfg, texto, idioma, metodo, escopo) for cfg in cfgs]
    candidatos.sort(key=lambda c: c["pontuacao"], reverse=True)
    return {
        "modo": "avancada", "metodo": metodo, "modelo": modelo, "idioma": idioma,
        "espaco": espaco, "combinacoes_testadas": avaliadas, "cobertura_completa": False,
        "tempo_segundos": round(time.perf_counter() - inicio, 3),
        "candidatos": _sem_duplicatas(candidatos)[:limite],
        "aviso": AVISO_ESTATISTICO + (
            " Este resultado vem de busca HEURÍSTICA (anéis/plugboard refinados apenas nos "
            "melhores candidatos): ele não enumera todas as chaves e pode não encontrar a "
            "configuração correta." if espaco["heuristica"] else ""
        ),
    }


# ----------------------------------------------------------------------
# Ponto de entrada único
# ----------------------------------------------------------------------

def investigar(modo, texto_cifrado, modelo, idioma, conhecidos, limite=10,
               progresso=None, cancelado=None):
    """Despacha para o modo pedido. progresso recebe um dicionário."""
    if modo not in modos_busca:
        raise ValueError("Modo de busca inválido. Use configurada, ampliada ou avancada.")
    if modo == "configurada":
        def relatar(feitas, total):
            if progresso:
                progresso({"fase": ("Posições iniciais", 1, 1), "fase_feitas": feitas,
                           "fase_total": total, "avaliadas": feitas, "parciais": None})
        grego = conhecidos.get("rotor_grego") or "Beta"
        resultado = atacar_posicoes(
            texto_cifrado, conhecidos["rotores"], list(conhecidos["aneis"]),
            conhecidos["refletor"], idioma, limite=limite, modelo=modelo,
            rotor_grego=grego, plugboard=conhecidos.get("plugboard") or "",
            progresso=relatar, cancelado=cancelado,
        )
        espaco = descrever_espaco(modelo, {
            "rotores": conhecidos["rotores"], "refletor": conhecidos["refletor"],
            "rotor_grego": grego, "aneis": conhecidos["aneis"],
            "plugboard_modo": "conhecido" if conhecidos.get("plugboard") else "vazio",
        }, "configurada")
        escopo = _resumo_escopo(espaco)
        for candidato in resultado["candidatos"]:
            candidato.update({"metodo": "exaustiva", "escopo": escopo,
                              "verificado_no_motor": True})
        resultado.update({"modo": "configurada", "metodo": "exaustiva", "espaco": espaco,
                          "cobertura_completa": True, "aviso": AVISO_ESTATISTICO})
        return resultado
    funcao = busca_ampliada if modo == "ampliada" else criptoanalise_avancada
    return funcao(texto_cifrado, modelo, idioma, conhecidos, limite=limite,
                  progresso=progresso, cancelado=cancelado)
