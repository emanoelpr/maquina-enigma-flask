"""Busca posições iniciais prováveis para Enigma M3 e M4."""

import heapq
from itertools import product
from string import ascii_uppercase
from time import perf_counter

from enigma import Enigma
from pontuacao import normalizar, pontuar_quadrigramas, tabelas_quad

alfabeto = ascii_uppercase
letras_para_pontuar = 150
palavras_frequentes = {
    "en": ("THE", "AND", "THAT", "WITH", "HAVE", "THIS", "FROM", "THEY", "WERE", "BEEN", "YOUR", "WHAT", "WHEN", "THEN", "THERE", "THEIR", "ABOUT", "WOULD", "COULD", "WHICH", "QUICK", "BROWN", "JUMPS", "OVER", "LAZY", "MESSAGE", "ATTACK", "SECRET", "MEETING", "REPORT", "RETURN", "NORTH", "SOUTH", "AFTER", "BEFORE", "WORLD", "HELLO"),
    "pt": ("QUE", "PARA", "COMO", "ESTA", "ESTE", "ESSA", "ISSO", "SUA", "SEU", "UMA", "DOS", "DAS", "POR", "COM", "NÃO", "NAO", "MAIS", "MUITO", "QUANDO", "ONDE", "ENTRE", "SOBRE", "MENSAGEM", "ATAQUE", "SECRETO", "RELATORIO", "RETORNO", "DEPOIS", "ANTES", "MUNDO", "HELLO"),
}
rotores_principais = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")
rotores_gregos = ("Beta", "Gamma")

# Viés por letra a favor do idioma selecionado quando os dois modelos
# empate ou ficarem muito próximos (ver pontuar_candidato).
vies_idioma = 0.01

# Busca em duas etapas para textos longos: a etapa 1 classifica todas as
# combinações com um PREFIXO do texto; a etapa 2 reavalia os melhores
# candidatos com o texto completo. O espaço de combinações é o mesmo;
# apenas o número de letras usadas na classificação inicial muda.
comprimento_duas_etapas = 60
letras_etapa1 = 50
candidatos_etapa1 = 2048
frequencia_progresso = 2048


class BuscaCancelada(Exception):
    """Sinaliza que a busca foi interrompida a pedido do chamador."""

    def __init__(self, combinacoes_testadas):
        super().__init__("Busca cancelada.")
        self.combinacoes_testadas = combinacoes_testadas


def pontuar_candidato(texto, idioma):
    """Pontua um candidato com o modelo de quadrigramas.

    Avalia o texto nos DOIS idiomas e devolve o maior valor, com um viés
    pequeno (vies_idioma por letra) a favor do idioma selecionado. Assim,
    estrangeirismos, marcas e nomes próprios não derrubam um texto que,
    no restante, é do idioma escolhido — sem depender de listas de
    palavras específicas. O bônus de palavras frequentes é mantido e
    aplicado junto ao valor final.
    """
    texto = normalizar(texto)
    outro_idioma = "en" if idioma == "pt" else "pt"

    bonus = 0.0
    for palavra in palavras_frequentes[idioma]:
        if len(palavra) >= 4:
            bonus += texto.count(palavra) * (len(palavra) ** 1.35)
    bonus /= max(len(texto), 1)

    valor_selecionado = pontuar_quadrigramas(texto, idioma) + vies_idioma * len(texto)
    valor_outro = pontuar_quadrigramas(texto, outro_idioma)
    return max(valor_selecionado, valor_outro) + bonus


def _tabelas_rotor(fiacao, anel):
    """Prepara 26 tabelas de substituição, uma por posição do rotor.

    Cada tabela já embute o deslocamento (posição - anel) da fiação:
    tabela[posicao][entrada] devolve a saída numérica do rotor naquela
    posição. Isso evita recalcular deslocamentos letra por letra.
    """
    tabelas = []
    for posicao in range(26):
        deslocamento = (posicao - anel) % 26
        tabelas.append(tuple(
            (fiacao[(entrada + deslocamento) % 26] - deslocamento) % 26
            for entrada in range(26)
        ))
    return tuple(tabelas)


def _montar_avaliador(maquina, idioma, trecho_numeros, usa_grego):
    """Cria a função de avaliação acelerada usada somente pela busca.

    Reproduz exatamente o caminho elétrico de Enigma.cifrar — incluindo o
    avanço com duplo passo — e a pontuação de pontuar_candidato, mas sem
    chamadas de método por letra e sem renormalizar texto que o motor já
    devolve normalizado. A equivalência com o motor original é verificada
    pelos testes de regressão (testes/test_busca_rapida.py).
    """
    rotor_esquerdo = maquina.rotor_esquerdo
    rotor_central = maquina.rotor_central
    rotor_direito = maquina.rotor_direito

    ida_esq = _tabelas_rotor(
        rotor_esquerdo.mapeamento_direto, rotor_esquerdo.configuracao_anel
    )
    ida_cen = _tabelas_rotor(
        rotor_central.mapeamento_direto, rotor_central.configuracao_anel
    )
    ida_dir = _tabelas_rotor(
        rotor_direito.mapeamento_direto, rotor_direito.configuracao_anel
    )
    volta_esq = _tabelas_rotor(
        rotor_esquerdo.mapeamento_reverso, rotor_esquerdo.configuracao_anel
    )
    volta_cen = _tabelas_rotor(
        rotor_central.mapeamento_reverso, rotor_central.configuracao_anel
    )
    volta_dir = _tabelas_rotor(
        rotor_direito.mapeamento_reverso, rotor_direito.configuracao_anel
    )

    entalhes_cen = rotor_central.entalhes
    entalhes_dir = rotor_direito.entalhes
    refletor = tuple(maquina.refletor.mapeamento_direto)
    plugboard = tuple(maquina.plugboard.mapeamento)

    # Caminho fixo entre o rotor esquerdo e o retorno: refletor sozinho na
    # M3; na M4, rotor grego + refletor combinados em uma única tabela.
    if usa_grego:
        rotor_grego = maquina.rotor_grego
        caminho_fixo = []
        for posicao in range(26):
            deslocamento = (posicao - rotor_grego.configuracao_anel) % 26
            ida_grego = tuple(
                (rotor_grego.mapeamento_direto[(entrada + deslocamento) % 26] - deslocamento) % 26
                for entrada in range(26)
            )
            volta_grego = tuple(
                (rotor_grego.mapeamento_reverso[(entrada + deslocamento) % 26] - deslocamento) % 26
                for entrada in range(26)
            )
            caminho_fixo.append(tuple(
                volta_grego[refletor[ida_grego[entrada]]]
                for entrada in range(26)
            ))
        caminho_fixo = tuple(caminho_fixo)
    else:
        caminho_fixo = (refletor,) * 26

    quad_selecionado = tabelas_quad[idioma]
    quad_outro = tabelas_quad["en" if idioma == "pt" else "pt"]
    bonus_pares = tuple(
        (palavra, len(palavra) ** 1.35)
        for palavra in palavras_frequentes[idioma]
        if len(palavra) >= 4
    )

    def avaliar(posicoes):
        """Devolve a pontuação da combinação, idêntica a pontuar_candidato."""
        if usa_grego:
            tabela_reflexao = caminho_fixo[posicoes[0]]
            p_esq, p_cen, p_dir = posicoes[1], posicoes[2], posicoes[3]
        else:
            tabela_reflexao = caminho_fixo[0]
            p_esq, p_cen, p_dir = posicoes

        saida = []
        acrescentar = saida.append
        for numero in trecho_numeros:
            # Avanço idêntico a Enigma.girar_rotores (duplo passo incluso).
            if p_cen in entalhes_cen:
                p_esq += 1
                p_cen += 1
                if p_esq == 26:
                    p_esq = 0
                if p_cen == 26:
                    p_cen = 0
            elif p_dir in entalhes_dir:
                p_cen += 1
                if p_cen == 26:
                    p_cen = 0
            p_dir += 1
            if p_dir == 26:
                p_dir = 0

            numero = plugboard[numero]
            numero = ida_dir[p_dir][numero]
            numero = ida_cen[p_cen][numero]
            numero = ida_esq[p_esq][numero]
            numero = tabela_reflexao[numero]
            numero = volta_esq[p_esq][numero]
            numero = volta_cen[p_cen][numero]
            numero = volta_dir[p_dir][numero]
            acrescentar(plugboard[numero])

        texto = "".join(alfabeto[indice] for indice in saida)

        # Pontuação idêntica a pontuar_candidato: quadrigramas nos dois
        # idiomas, máximo com viés a favor do selecionado, mais bônus.
        if len(saida) < 4:
            return vies_idioma * len(saida)

        chave = ((saida[0] * 26 + saida[1]) * 26 + saida[2]) * 26 + saida[3]
        soma_selecionado = quad_selecionado[chave]
        soma_outro = quad_outro[chave]
        for letra in saida[4:]:
            chave = (chave % 17576) * 26 + letra
            soma_selecionado += quad_selecionado[chave]
            soma_outro += quad_outro[chave]
        quantidade = len(saida) - 3
        valor_selecionado = soma_selecionado / quantidade + vies_idioma * len(saida)
        valor_outro = soma_outro / quantidade
        base = max(valor_selecionado, valor_outro)

        bonus = 0.0
        for palavra, peso in bonus_pares:
            ocorrencias = texto.count(palavra)
            if ocorrencias:
                bonus += ocorrencias * peso
        return base + bonus / len(texto)

    return avaliar


def atacar_posicoes(
    texto_cifrado,
    rotores,
    aneis,
    refletor,
    idioma,
    limite=10,
    modelo="M3",
    rotor_grego="Beta",
    progresso=None,
    cancelado=None,
):
    """Testa posições iniciais; mantém fixos rotores, anéis e refletor recebidos.

    Na M3, busca as 26³ posições dos três rotores principais.
    Na M4, busca também a posição inicial do rotor grego: 26⁴ combinações.
    O plugboard é mantido vazio nesta versão da busca.

    Parâmetros opcionais:
    - progresso: função chamada como progresso(feitas, total) durante a
      busca, com contagens reais de combinações avaliadas.
    - cancelado: função sem argumentos; quando devolve Verdadeiro em um
      ponto seguro do laço, a busca levanta BuscaCancelada.
    """
    texto = normalizar(texto_cifrado)
    idioma = idioma.strip().lower() if isinstance(idioma, str) else idioma
    modelo = modelo.strip().upper() if isinstance(modelo, str) else modelo

    if len(texto) < 3:
        raise ValueError("O texto cifrado precisa ter pelo menos três letras.")
    if idioma not in ("pt", "en"):
        raise ValueError("Idioma inválido. Use 'pt' ou 'en'.")
    if modelo not in ("M3", "M4"):
        raise ValueError("Modelo inválido. Use M3 ou M4.")
    if len(rotores) != 3:
        raise ValueError("Informe exatamente três rotores principais.")
    if any(rotor not in rotores_principais for rotor in rotores):
        raise ValueError("Rotor principal inválido.")
    if len(set(rotores)) != 3:
        raise ValueError("Os três rotores principais devem ser diferentes.")
    if len(aneis) != 3:
        raise ValueError("Informe exatamente três configurações de anel.")
    if any(isinstance(anel, bool) or not isinstance(anel, int) or not 1 <= anel <= 26 for anel in aneis):
        raise ValueError("Cada anel deve ser um número inteiro entre 1 e 26.")
    if modelo == "M3" and refletor not in ("B", "C"):
        raise ValueError("A Enigma M3 aceita os refletores B ou C.")
    if modelo == "M4" and refletor not in ("Bfino", "Cfino"):
        raise ValueError("A Enigma M4 aceita os refletores Bfino ou Cfino.")
    if modelo == "M4" and rotor_grego not in rotores_gregos:
        raise ValueError("Na M4, selecione o rotor grego Beta ou Gamma.")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= 100:
        raise ValueError("O limite deve ser um inteiro entre 1 e 100.")

    inicio = perf_counter()
    aneis_motor = [anel - 1 for anel in aneis]
    if modelo == "M4":
        nomes_rotores = (rotor_grego, *rotores)
        aneis_motor = [0, *aneis_motor]  # rotor grego usa anel fixo 1 nesta implementação
        total = 26 ** 4
        combinacoes = product(range(26), repeat=4)  # grego, esquerdo, central, direito
    else:
        nomes_rotores = tuple(rotores)
        total = 26 ** 3
        combinacoes = product(range(26), repeat=3)

    # Máquina auxiliar apenas para validar a configuração e fornecer as
    # fiações ao avaliador acelerado; a busca não a utiliza por letra.
    maquina = Enigma(
        rotores=nomes_rotores,
        posicoes_rotores=[0] * len(nomes_rotores),
        configuracoes_anel=aneis_motor,
        nome_refletor=refletor,
        conexoes_plugboard="",
    )
    trecho = texto[:letras_para_pontuar]
    trecho_numeros = [ord(letra) - ord("A") for letra in trecho]

    avaliar = _montar_avaliador(maquina, idioma, trecho_numeros, modelo == "M4")

    # Busca em duas etapas para textos longos: a etapa 1 classifica o
    # espaço inteiro com um PREFIXO do texto; a etapa 2 reavalia os
    # melhores candidatos com o texto completo. O espaço de combinações
    # e o modelo linguístico são os mesmos; muda apenas quantas letras
    # são usadas na classificação inicial (documentado acima).
    if len(trecho_numeros) > comprimento_duas_etapas:
        etapa1 = _montar_avaliador(
            maquina, idioma, trecho_numeros[:letras_etapa1], modelo == "M4"
        )
        capacidade = candidatos_etapa1
    else:
        etapa1 = avaliar
        capacidade = limite

    if progresso is not None:
        progresso(0, total)

    # Laço com progresso real e cancelamento: mantém os melhores
    # candidatos em um heap, com desempate pela ordem de visita
    # (idêntico ao heapq.nlargest anterior).
    monte = []
    contador = 0
    for posicoes in combinacoes:
        valor = etapa1(posicoes)
        contador += 1
        item = (valor, -contador, posicoes)
        if len(monte) < capacidade:
            heapq.heappush(monte, item)
        elif item > monte[0]:
            heapq.heapreplace(monte, item)
        if contador % frequencia_progresso == 0:
            if cancelado is not None and cancelado():
                raise BuscaCancelada(contador)
            if progresso is not None:
                progresso(contador, total)

    if cancelado is not None and cancelado():
        raise BuscaCancelada(contador)
    if progresso is not None:
        progresso(total, total)

    if capacidade == limite:
        melhores = [posicoes for _, _, posicoes in sorted(monte, reverse=True)]
    else:
        refinados = sorted(
            ((avaliar(posicoes), ordem, posicoes) for _, ordem, posicoes in monte),
            reverse=True,
        )
        melhores = [posicoes for _, _, posicoes in refinados[:limite]]
    candidatos = []

    for posicoes in melhores:
        if modelo == "M4":
            posicao_grega = posicoes[0]
            posicoes_principais = posicoes[1:]
            nomes = nomes_rotores
            posicoes_motor = list(posicoes)
        else:
            posicao_grega = None
            posicoes_principais = posicoes
            nomes = nomes_rotores
            posicoes_motor = list(posicoes)

        maquina_candidata = Enigma(
            rotores=nomes,
            posicoes_rotores=posicoes_motor,
            configuracoes_anel=aneis_motor,
            nome_refletor=refletor,
            conexoes_plugboard="",
        )
        texto_decifrado = maquina_candidata.cifrar_texto(texto)
        candidato = {
            "texto": texto_decifrado,
            "posicoes": "".join(alfabeto[indice] for indice in posicoes_principais),
            "rotores": list(rotores),
            "aneis": list(aneis),
            "refletor": refletor,
            "idioma": idioma,
            "modelo": modelo,
            "pontuacao": pontuar_candidato(texto_decifrado, idioma),
        }
        if modelo == "M4":
            candidato["rotor_grego"] = rotor_grego
            candidato["posicao_grega"] = alfabeto[posicao_grega]
        candidatos.append(candidato)

    candidatos.sort(key=lambda candidato: candidato["pontuacao"], reverse=True)
    return {
        "modelo": modelo,
        "combinacoes_testadas": total,
        "idioma": idioma,
        "tempo_segundos": round(perf_counter() - inicio, 3),
        "candidatos": candidatos[:limite],
    }
