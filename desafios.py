"""Catálogo de missões educacionais da seção Desafios históricos.

TODAS as mensagens cifradas foram geradas pelo motor Enigma real deste
projeto (enigma.py) e o teste testes/test_desafios.py re-verifica, a cada
execução, que a configuração oficial de cada missão decifra a mensagem de
volta para o texto claro esperado.

Precisão histórica: os contextos gerais (configuração diária da Enigma,
campanha do Norte da África, adoção da M4 pela Kriegsmarine em 1942,
Bletchley Park) são fatos documentados nas fontes citadas. As MENSAGENS e
os cenários específicos são RECONSTRUÇÕES EDUCACIONAIS; cada missão
identifica, no campo fato_verificado, o que é fato e o que é reconstrução.

modos de jogo: o multiplicador de pontos por modo é aplicado aqui
(pontos_por_modo) e validado no backend; o desbloqueio de conquistas é
controlado pela sessão do servidor (api.py), que impede pontuação duplicada.

galeria: apenas fotografias baixadas para o projeto (assets/galeria) são
exibidas como imagem; quando não houve confirmação de imagem verificável,
a missão apresenta LINK para o acervo oficial — nunca imagem sem fonte.

Convenção das configurações: na M4, posicoes e aneis incluem o rotor grego
na primeira posição (4 valores); na M3, referem-se apenas aos três rotores
principais (3 valores). aneis usam a escala 1-26 da interface.
"""

from enigma import Enigma
from pontuacao import normalizar


modos = ("guiado", "investigacao", "especialista")

# Pontuação por modo: guiado = metade, investigação = três quartos,
# especialista = valor integral da missão.
multiplicador_modo = {"guiado": 0.5, "investigacao": 0.75, "especialista": 1.0}


missoes = {'comboio-atlantico': {'aneis': (1, 8, 14, 21),
                       'aprendizado': 'Conceito aprendido: o rotor grego. Na M4, Beta ou Gamma '
                                      'ocupa a posição extra à esquerda: sua posição inicial muda '
                                      'o caminho elétrico do sinal, mas ele permanece parado '
                                      'durante toda a mensagem — exatamente como na máquina real.',
                       'contexto': 'A Batalha do Atlântico foi uma campanha prolongada: comboios '
                                   'aliados contra submarinos alemães (U-boats) que tentavam '
                                   'cortar as linhas de abastecimento. Em fevereiro de 1942, a '
                                   'Kriegsmarine introduziu a M4 com refletor fino; a leitura '
                                   'aliada do tráfego naval ficou interrompida por cerca de dez '
                                   'meses, retomada com técnicas como o Banburismus e material '
                                   'capturado. O esforço combinou matemática, procedimentos e '
                                   'coragem das tripulações.',
                       'dificuldade': 'dificil',
                       'fato_verificado': 'FATO DOCUMENTADO: a M4 entrou no tráfego naval em '
                                          'fevereiro de 1942 e a leitura aliada ficou interrompida '
                                          'por cerca de dez meses; o Banburismus, de Turing, é '
                                          'técnica documentada do período. RECONSTRUÇÃO '
                                          'EDUCACIONAL: a mensagem e o cenário do comboio são '
                                          'fictícios.',
                       'fontes': [{'titulo': 'Imperial War Museums — How Alan Turing Cracked the '
                                             'Enigma Code',
                                   'url': 'https://www.iwm.org.uk/history/how-alan-turing-cracked-the-enigma-code'},
                                  {'titulo': 'Bletchley Park — Our Story',
                                   'url': 'https://bletchleypark.org.uk/whats-on/our-story'}],
                       'id': 'comboio-atlantico',
                       'intro': 'Comboios cruzavam o Atlântico sob ataque de submarinos, e o '
                                'tráfego naval alemão usava a M4 — quatro posições, refletor fino, '
                                'muito mais difícil de quebrar. Esta é a missão mais exigente do '
                                'projeto: o rotor grego Beta não avança, mas participa do caminho '
                                'elétrico.',
                       'local': 'Oceano Atlântico Norte — cenário inspirado nos comboios aliados',
                       'mensagem_cifrada': 'BTMZKSCOPHZKUSIFZEVNAMMLQWPKX',
                       'modelo': 'M4',
                       'natureza': 'reconstrucao',
                       'pais_regiao': 'Kriegsmarine (Alemanha) × Marinha Mercante e Royal Navy',
                       'periodo': 'A partir de fevereiro de 1942 — introdução da M4 no tráfego '
                                  'naval (período em que a leitura aliada ficou interrompida)',
                       'plugboard': '',
                       'pontos': 150,
                       'posicoes': ('S', 'D', 'T', 'C'),
                       'quem_participava': 'Operadores de rádio em submarinos e navios de comboio; '
                                           'oficiais de sinais das marinhas; em terra, os '
                                           'analistas de Bletchley Park e as equipes que operavam '
                                           'as Bombes.',
                       'refletor': 'Bfino',
                       'rotor_grego': 'Beta',
                       'rotores': ('VI', 'II', 'VIII'),
                       'texto_claro': 'SUBMARINOSPARTEMDOPORTOANOITE',
                       'titulo': 'Comboio no Atlântico'},
 'estacao-de-escuta': {'aneis': (3, 1, 9),
                       'aprendizado': 'Conceito aprendido: o plugboard. Cada conexão troca um par '
                                      'de letras antes e depois do percurso pelos rotores; com 10 '
                                      'conexões, as configurações passam de 150 trilhões. É a '
                                      'camada que os criptoanalistas mais respeitavam.',
                       'contexto': 'A captura do sinal (estações de escuta, as Y Stations) e a '
                                   'quebra da cifra (Bletchley Park) eram trabalhos DIFERENTES e '
                                   'complementares: operadoras e operadores captavam e '
                                   'transcreviam; analistas e máquinas, como a Bombe, recuperavam '
                                   'as configurações do dia. Cerca de 10 mil pessoas passaram pela '
                                   'organização de Bletchley Park, e o trabalho permaneceu em '
                                   'segredo até os anos 1970.',
                       'dificuldade': 'dificil',
                       'fato_verificado': 'FATO DOCUMENTADO: a interceptação alimentava Bletchley '
                                          'Park, cujo trabalho envolvia milhares de pessoas e '
                                          'segredo de décadas. RECONSTRUÇÃO EDUCACIONAL: a '
                                          'mensagem abaixo NÃO é um documento original de '
                                          'Bletchley Park nem de qualquer estação de escuta.',
                       'fontes': [{'titulo': 'Bletchley Park — Our Story',
                                   'url': 'https://bletchleypark.org.uk/whats-on/our-story'},
                                  {'titulo': 'GCHQ — Bletchley Park and WWII',
                                   'url': 'https://www.gchq.gov.uk/section/history/bletchley-park-and-wwii'},
                                  {'titulo': 'Imperial War Museums — How Alan Turing Cracked the '
                                             'Enigma Code',
                                   'url': 'https://www.iwm.org.uk/history/how-alan-turing-cracked-the-enigma-code'}],
                       'id': 'estacao-de-escuta',
                       'intro': 'Você trabalha no lado aliado: uma interceptação acabou de chegar '
                                'com o plugboard ativo — a camada extra que multiplicava as '
                                'configurações. Com as pistas da estação, aplique a configuração e '
                                'leia o relatório.',
                       'local': 'Bletchley Park, Buckinghamshire, Reino Unido — local real',
                       'mensagem_cifrada': 'NRGEJEJGMGBOMPMLNTHBJEGTHNSNIDTLN',
                       'modelo': 'M3',
                       'natureza': 'reconstrucao',
                       'pais_regiao': 'Reino Unido',
                       'periodo': '1939–1945 — período de operação de Bletchley Park',
                       'plugboard': 'AV BS CG',
                       'pontos': 150,
                       'posicoes': ('K', 'E', 'Z'),
                       'quem_participava': 'Operadoras das Y Stations (grande parte do quadro era '
                                           'feminino), despachantes que levavam as interceptações '
                                           'a Bletchley, criptoanalistas e operadores das Bombes.',
                       'refletor': 'B',
                       'rotor_grego': None,
                       'rotores': ('I', 'III', 'IV'),
                       'texto_claro': 'RELATORIODAEQUADRILHAPRONTOAMANHA',
                       'titulo': 'Estação de escuta'},
 'primeira-leitura': {'aneis': (1, 1, 1),
                      'aprendizado': 'Conceito aprendido: a recíproca. Como o refletor devolve o '
                                     'sinal pelo mesmo caminho, a MESMA configuração cifra e '
                                     'decifra — basta a máquina estar na posição inicial correta.',
                      'contexto': 'A Enigma militar alemã operava com uma configuração trocada '
                                  'todos os dias, definida por listas de chaves distribuídas às '
                                  'unidades (folhas de chave, Schlüsseltafeln): rotores, anéis, '
                                  'posições iniciais e conexões do plugboard. Sem a folha do dia, '
                                  'decifrar exigia criptoanálise; com ela, qualquer operador '
                                  'treinado lia a mensagem em minutos. Esta missão simula o papel '
                                  'do operador que RECEBEU a folha do dia e precisa aplicá-la '
                                  'corretamente.',
                      'dificuldade': 'facil',
                      'fato_verificado': 'FATO DOCUMENTADO: a configuração diária era distribuída '
                                         'em folhas de chave e compartilhada por todas as unidades '
                                         'da mesma rede. RECONSTRUÇÃO EDUCACIONAL: a mensagem '
                                         'abaixo é fictícia e não corresponde a nenhum documento '
                                         'histórico autêntico.',
                      'fontes': [{'titulo': 'Bletchley Park — Our Story',
                                  'url': 'https://bletchleypark.org.uk/whats-on/our-story'},
                                 {'titulo': 'Crypto Museum — Enigma cipher machines',
                                  'url': 'https://www.cryptomuseum.com/crypto/enigma/index.htm'}],
                      'id': 'primeira-leitura',
                      'intro': 'Sua primeira leitura em uma Enigma. Uma mensagem de rotina saiu '
                               'pelo rádio com uma configuração simples — a mesma que as unidades '
                               'usavam quando os procedimentos ainda eram básicos. Configure a '
                               'máquina, digite a mensagem e leia o que ela diz.',
                      'local': 'Canal da Mancha — cenário hipotético, sem local específico',
                      'mensagem_cifrada': 'QIOYALCMMXMTOTGWTLEBAUZVF',
                      'modelo': 'M3',
                      'natureza': 'reconstrucao',
                      'pais_regiao': 'Norte da Europa, anos de guerra (cenário genérico)',
                      'periodo': '1939–1945 — sem data específica (cenário genérico)',
                      'plugboard': '',
                      'pontos': 50,
                      'posicoes': ('A', 'A', 'A'),
                      'quem_participava': 'Operadores de rádio (Funker) cifravam e decifravam o '
                                          'tráfego nas unidades; do lado aliado, operadores das '
                                          'estações de escuta (Y Stations) captavam o sinal e o '
                                          'enviavam aos centros de análise.',
                      'refletor': 'B',
                      'rotor_grego': None,
                      'rotores': ('I', 'II', 'III'),
                      'texto_claro': 'CONVOIANORTEPARTEAOAMANHA',
                      'titulo': 'Primeira leitura'},
 'radio-do-deserto': {'aneis': (1, 6, 14),
                      'aprendizado': 'Conceito aprendido: os rotores. Trocar a ordem muda '
                                     'completamente as substituições: IV-II-V não é II-IV-V. A '
                                     'ordem faz parte da chave do dia.',
                      'contexto': 'A campanha do Norte da África (1940–1943) opôs forças do Eixo '
                                  'às Aliadas em centenas de quilômetros de deserto. A distância e '
                                  'a mobilidade tornavam o rádio essencial — e o tráfego de rádio, '
                                  'abundante material de interceptação. As unidades alemãs usavam '
                                  'Enigma M3 portátil; cada rede tinha sua lista de chaves do mês. '
                                  'A análise do tráfego, junto com criptoanálise, alimentava o '
                                  'quadro de inteligência aliado.',
                      'dificuldade': 'media',
                      'fato_verificado': 'FATO DOCUMENTADO: o teatro do Norte da África usou '
                                         'comunicações por rádio em larga escala e unidades do '
                                         'Eixo operavam Enigma M3. RECONSTRUÇÃO EDUCACIONAL: a '
                                         'mensagem é fictícia; nenhuma interceptação real é aqui '
                                         'apresentada como prova.',
                      'fontes': [{'titulo': 'Imperial War Museums — How Alan Turing Cracked the '
                                            'Enigma Code',
                                  'url': 'https://www.iwm.org.uk/history/how-alan-turing-cracked-the-enigma-code'},
                                 {'titulo': 'Crypto Museum — Enigma cipher machines',
                                  'url': 'https://www.cryptomuseum.com/crypto/enigma/index.htm'}],
                      'id': 'radio-do-deserto',
                      'intro': 'No calor do deserto ocidental, unidades blindadas dependiam de '
                               'rádio para movimentar colunas em terreno sem referências. Esta '
                               'mensagem saiu de uma estação móvel com rotores trocados — e cabe a '
                               'você descobrir a configuração com as pistas disponíveis.',
                      'local': 'Deserto ocidental, Norte da África — cenário inspirado, sem '
                               'unidade ou batalha específica',
                      'mensagem_cifrada': 'VEPWQHFPZDSBVXQWVMSOWVNKVZMD',
                      'modelo': 'M3',
                      'natureza': 'reconstrucao',
                      'pais_regiao': 'Líbia e Egito — teatro de operações do Norte da África',
                      'periodo': '1941–1943 — período da campanha do Norte da África',
                      'plugboard': '',
                      'pontos': 100,
                      'posicoes': ('H', 'C', 'L'),
                      'quem_participava': 'Operadores de rádio em veículos de comando e estações '
                                          'móveis; do lado aliado, unidades de escuta do Exército '
                                          'e da RAF captavam as transmissões.',
                      'refletor': 'C',
                      'rotor_grego': None,
                      'rotores': ('IV', 'II', 'V'),
                      'texto_claro': 'PANZERAVANCAMPARAOESTEAMANHA',
                      'titulo': 'Rádio do deserto'}}

conquistas = {'comboio-atlantico': {'descricao': 'Concluiu a missão Comboio no Atlântico operando a Enigma M4.',
                       'icone': '◇',
                       'id': 'conquista-comboio-atlantico',
                       'nome': 'Guardião das comunicações'},
 'estacao-de-escuta': {'descricao': 'Concluiu a missão Estação de escuta com o plugboard ativo.',
                       'icone': '⌕',
                       'id': 'conquista-estacao-de-escuta',
                       'nome': 'Ouvidos atentos'},
 'primeira-leitura': {'descricao': 'Concluiu a missão Primeira leitura e leu sua primeira mensagem '
                                   'na Enigma.',
                      'icone': '⌘',
                      'id': 'conquista-primeira-leitura',
                      'nome': 'Operador em treinamento'},
 'radio-do-deserto': {'descricao': 'Concluiu a missão Rádio do deserto descobrindo a configuração '
                                   'do dia.',
                      'icone': '◎',
                      'id': 'conquista-radio-do-deserto',
                      'nome': 'Sinal decifrado'}}

galeria = {'comboio-atlantico': [{'arquivo': None,
                        'autoria': 'Não registrada pela busca',
                        'credito_licenca': 'Acervo do National Museum of the United States Navy '
                                           '(link de acervo; não acessível do ambiente de '
                                           'desenvolvimento — confirme no site).',
                        'data': 'Segunda Guerra Mundial (data exata não confirmada)',
                        'fonte_url': 'https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-atlantic/battle-of-the-atlantic.html',
                        'local': 'Oceano Atlântico',
                        'relacao': 'Representa os comboios que a mensagem da missão pretendia '
                                   'informar.',
                        'tipo': 'historica',
                        'titulo_legenda': 'Navios mercantes em comboio no Atlântico, a formação '
                                          'que reduzia as perdas para submarinos.'},
                       {'arquivo': 'assets/galeria/m3-submarino.jpg',
                        'autoria': 'Museum of Science and Industry, Chicago (instituição '
                                   'identificada na busca; autoria individual não registrada)',
                        'credito_licenca': 'Uso educacional não comercial; confira as condições no '
                                           'site do museu.',
                        'data': 'Fotografia atual do submarino de 1944',
                        'fonte_url': 'https://www.msichicago.org/',
                        'local': 'Museum of Science and Industry, Chicago, Estados Unidos',
                        'relacao': 'Submarino preservado do tipo que usava a Enigma M4 no '
                                   'Atlântico.',
                        'tipo': 'atual',
                        'titulo_legenda': 'U-505, submarino alemão capturado em 1944 e hoje '
                                          'preservado no Museu de Ciência e Indústria de '
                                          'Chicago.'}],
 'estacao-de-escuta': [{'arquivo': None,
                        'autoria': 'Não registrada pela busca',
                        'credito_licenca': 'Consulte o acervo do Imperial War Museums para crédito '
                                           'e condições de uso.',
                        'data': 'Segunda Guerra Mundial (data exata não confirmada)',
                        'fonte_url': None,
                        'local': 'Não confirmado',
                        'relacao': 'Representa o trabalho dos operadores de rádio e de escuta '
                                   'retratado na missão.',
                        'tipo': 'historica',
                        'titulo_legenda': 'Operador de rádio em serviço durante a Segunda Guerra '
                                          'Mundial.'},
                       {'arquivo': None,
                        'autoria': 'Não registrada pela busca',
                        'credito_licenca': 'Consulte o acervo oficial do Bletchley Park Trust.',
                        'data': 'Data não confirmada',
                        'fonte_url': None,
                        'local': 'Bletchley Park, Buckinghamshire, Reino Unido',
                        'relacao': 'O local real onde as interceptações eram analisadas.',
                        'tipo': 'atual',
                        'titulo_legenda': 'Bletchley Park hoje: o sítio histórico é museu aberto à '
                                          'visita.'}],
 'primeira-leitura': [{'arquivo': 'assets/galeria/m1-maquina.jpg',
                       'autoria': 'The National Museum of Computing (instituição identificada na '
                                  'busca; autoria individual não registrada)',
                       'credito_licenca': 'Uso educacional não comercial; condições completas no '
                                          'site do museu.',
                       'data': 'Fotografia atual (data exata não registrada pela busca)',
                       'fonte_url': 'https://www.tnmoc.org/',
                       'local': 'The National Museum of Computing, Bletchley Park, Reino Unido',
                       'relacao': 'É a mesma máquina que você opera na simulação: teclado, '
                                  'plugboard e painel de lâmpadas.',
                       'tipo': 'atual',
                       'titulo_legenda': 'Máquina Enigma em exposição no The National Museum of '
                                         'Computing (Bletchley, Reino Unido).'},
                      {'arquivo': None,
                       'autoria': 'Não registrada pela busca',
                       'credito_licenca': 'Consulte o acervo oficial do Bletchley Park Trust para '
                                          'uso e créditos.',
                       'data': 'Data não confirmada',
                       'fonte_url': None,
                       'local': 'Bletchley Park, Buckinghamshire, Reino Unido',
                       'relacao': 'Local real onde mensagens interceptadas eram analisadas.',
                       'tipo': 'atual',
                       'titulo_legenda': 'A mansão de Bletchley Park, quartel-general da '
                                         'decifração britânica na Segunda Guerra.'}],
 'radio-do-deserto': [{'arquivo': None,
                       'autoria': 'Não registrada pela busca',
                       'credito_licenca': 'Consulte o acervo do Imperial War Museums para crédito '
                                          'e condições de uso.',
                       'data': 'Período da campanha (data exata não confirmada)',
                       'fonte_url': None,
                       'local': 'Deserto ocidental, Norte da África',
                       'relacao': 'Ilustra as condições em que estações de rádio móveis operavam '
                                  'com Enigma portátil.',
                       'tipo': 'historica',
                       'titulo_legenda': 'Blindados em operação no deserto ocidental, cenário das '
                                         'comunicações móveis do Norte da África.'}]}

dicas = {'comboio-atlantico': ['Esta é a M4: rotor grego Beta, rotores VI-II-VIII e refletor B fino '
                       '(Bfino).',
                       'Os anéis são 1-8-14-21 — na interface informe os quatro valores; o '
                       'primeiro pertence ao rotor grego.',
                       'As posições iniciais são S-D-T-C (a primeira é a do rotor grego).'],
 'estacao-de-escuta': ['O modelo é M3 com rotores I-III-IV e refletor B.',
                       'As posições iniciais são K-E-Z e os anéis 3-1-9. Falta a camada extra.',
                       'O plugboard tem três conexões: AV BS CG.'],
 'primeira-leitura': ['Abra a Máquina & cifra. Escolha o modelo M3 e os rotores I-II-III, na '
                      'ordem: esquerdo I, central II, direito III.',
                      'Confira o refletor B e deixe os anéis em 1-1-1. Falta só um detalhe: as '
                      'posições iniciais das três janelas.',
                      'As posições iniciais são A-A-A. Digite a mensagem cifrada na máquina e cole '
                      'a saída na resposta.'],
 'radio-do-deserto': ['O modelo é M3 e a ordem dos rotores importa: esquerdo IV, central II, '
                      'direito V, com o refletor C.',
                      'Os anéis são 1-6-14 e o plugboard está vazio. As posições iniciais variam '
                      'de H a M nas três janelas.',
                      'As posições exatas são H-C-L. Prepare a máquina e decifre.']}


# ------------------------------------------------------------------
# Fontes de referência por acervo. Quando a busca não registrou a página
# original da fotografia, o item aponta para o acervo institucional
# correspondente (URLs verificadas) — nunca fica sem fonte.
# ------------------------------------------------------------------
acervos_padrao = {
    "Bletchley": "https://bletchleypark.org.uk/whats-on/our-story",
    "Turing": "https://www.iwm.org.uk/history/how-alan-turing-cracked-the-enigma-code",
    "deserto": "https://www.iwm.org.uk/history/how-alan-turing-cracked-the-enigma-code",
    "comboio": "https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-atlantic/battle-of-the-atlantic.html",
    "operador": "https://www.iwm.org.uk/history/how-alan-turing-cracked-the-enigma-code",
    "U-505": "https://www.msichicago.org/",
    "Enigma em exposição": "https://www.tnmoc.org/",
}

for _itens in galeria.values():
    for _item in _itens:
        if not _item["fonte_url"]:
            _item["fonte_url"] = next(
                (
                    url
                    for palavra, url in acervos_padrao.items()
                    if palavra.lower() in _item["titulo_legenda"].lower()
                ),
                "https://bletchleypark.org.uk/whats-on/our-story",
            )


def _maquina_de(missao):
    """Cria uma máquina NOVA na configuração da missão — a recíproca exige
    o ponto de partida exato; nunca reutilize uma máquina já avançada."""
    grego = missao["rotor_grego"]
    nomes = (grego, *missao["rotores"]) if grego else missao["rotores"]
    return Enigma(
        rotores=nomes,
        posicoes_rotores=tuple(ord(l) - ord("A") for l in missao["posicoes"]),
        configuracoes_anel=tuple(a - 1 for a in missao["aneis"]),
        nome_refletor=missao["refletor"],
        conexoes_plugboard=missao["plugboard"],
    )


def pontos_por_modo(missao, modo):
    """Aplica o multiplicador do modo (regra validada no backend)."""
    if modo not in modos:
        raise ValueError(f"Modo inválido. Use: {', '.join(modos)}.")
    return int(round(missao["pontos"] * multiplicador_modo[modo]))


def catalogo_publico():
    """Lista de missões sem texto claro nem configuração."""
    return [
        {
            "id": missao["id"],
            "titulo": missao["titulo"],
            "dificuldade": missao["dificuldade"],
            "pontos": missao["pontos"],
            "natureza": missao["natureza"],
            "modelo": missao["modelo"],
            "local": missao["local"],
            "periodo": missao["periodo"],
            "mensagem_cifrada": missao["mensagem_cifrada"],
            "total_dicas": len(dicas[missao["id"]]),
            "conquista": {
                "id": conquistas[missao["id"]]["id"],
                "nome": conquistas[missao["id"]]["nome"],
                "icone": conquistas[missao["id"]]["icone"],
            },
        }
        for missao in missoes.values()
    ]


def detalhe_publico(id_missao):
    """Dados completos da missão para a Etapa A — sem resposta nem config."""
    if id_missao not in missoes:
        raise ValueError("Missão não encontrada.")
    missao = missoes[id_missao]
    conquista = conquistas[id_missao]
    return {
        "id": missao["id"],
        "titulo": missao["titulo"],
        "dificuldade": missao["dificuldade"],
        "pontos": missao["pontos"],
        "natureza": missao["natureza"],
        "modelo": missao["modelo"],
        "local": missao["local"],
        "pais_regiao": missao["pais_regiao"],
        "periodo": missao["periodo"],
        "intro": missao["intro"],
        "contexto": missao["contexto"],
        "quem_participava": missao["quem_participava"],
        "fato_verificado": missao["fato_verificado"],
        "aprendizado": missao["aprendizado"],
        "fontes": [dict(fonte) for fonte in missao["fontes"]],
        "mensagem_cifrada": missao["mensagem_cifrada"],
        "objetivo": "Decifre a mensagem acima com a máquina (tela Máquina & cifra) e cole aqui o texto que leu.",
        "total_dicas": len(dicas[id_missao]),
        "conquista": {"id": conquista["id"], "nome": conquista["nome"], "icone": conquista["icone"]},
    }


def configuracao_guiada(id_missao):
    """Configuração oficial — usada APENAS pelo modo guiado (ver api.py).

    Projeto educacional sem contas de usuário: este endpoint não exige
    autenticação, e a limitação é assumida e documentada. O modo
    investigação deve se guiar pelas dicas, não por este endpoint.
    """
    if id_missao not in missoes:
        raise ValueError("Missão não encontrada.")
    missao = missoes[id_missao]
    return {
        "modelo": missao["modelo"],
        "rotores": list(missao["rotores"]),
        "posicoes": list(missao["posicoes"]),
        "aneis": list(missao["aneis"]),
        "refletor": missao["refletor"],
        "plugboard": missao["plugboard"],
        "rotor_grego": missao["rotor_grego"],
    }


def galeria_de(id_missao):
    if id_missao not in galeria:
        raise ValueError("Missão não encontrada.")
    return [dict(item) for item in galeria[id_missao]]


def conquistas_catalogo():
    """Catálogo completo de conquistas (estado fica no progresso)."""
    return [
        {
            "id": info["id"],
            "nome": info["nome"],
            "descricao": info["descricao"],
            "icone": info["icone"],
            "missao": id_missao,
        }
        for id_missao, info in conquistas.items()
    ]


def obter_dicas(id_missao, ate_nivel):
    """Devolve as dicas 1..ate_nivel (liberação progressiva)."""
    if id_missao not in missoes:
        raise ValueError("Missão não encontrada.")
    dicas_missao = dicas[id_missao]
    if isinstance(ate_nivel, bool) or not isinstance(ate_nivel, int) or not 1 <= ate_nivel <= len(dicas):
        raise ValueError(f"O nível da dica deve ser um número entre 1 e {len(dicas)}.")
    return dicas_missao[:ate_nivel]


def verificar_resposta(id_missao, resposta, modo="especialista"):
    """Valida a resposta com o motor real e calcula a pontuação do modo.

    O controle de repetição (não duplicar pontos) é feito pela sessão do
    servidor, em api.py; aqui devolvemos o valor do modo e os dados da
    conquista correspondente, que só é válida quando a resposta acerta.
    """
    if id_missao not in missoes:
        raise ValueError("Missão não encontrada.")
    if modo not in modos:
        raise ValueError(f"Modo inválido. Use: {', '.join(modos)}.")
    if not isinstance(resposta, str):
        raise ValueError("A resposta deve ser um texto.")

    missao = missoes[id_missao]
    candidato = normalizar(resposta)

    if not candidato:
        return {"correto": False, "feedback": "Digite o texto que você leu na máquina."}

    decifrado = _maquina_de(missao).cifrar_texto(missao["mensagem_cifrada"])
    assert decifrado == missao["texto_claro"]

    if candidato == missao["texto_claro"]:
        config_publica = {
            "modelo": missao["modelo"],
            "rotores": list(missao["rotores"]),
            "posicoes": list(missao["posicoes"]),
            "aneis": list(missao["aneis"]),
            "refletor": missao["refletor"],
            "plugboard": missao["plugboard"] or "nenhum",
        }
        if missao["rotor_grego"]:
            config_publica["rotor_grego"] = missao["rotor_grego"]
        conquista = conquistas[id_missao]
        return {
            "correto": True,
            "feedback": "Mensagem correta! Confira a configuração e o que esta missão ensinou.",
            "config": config_publica,
            "pontos": pontos_por_modo(missao, modo),
            "modo": modo,
            "mensagem_decifrada": missao["texto_claro"],
            "aprendizado": missao["aprendizado"],
            "nova_conquista": {
                "id": conquista["id"],
                "nome": conquista["nome"],
                "descricao": conquista["descricao"],
                "icone": conquista["icone"],
            },
        }

    if modo == "especialista" and abs(len(candidato) - len(missao["texto_claro"])) > 3:
        dica_extra = " Dica: o comprimento do texto parece diferente da mensagem da missão."
    else:
        dica_extra = " Reveja as posições ou peça uma dica."
    return {
        "correto": False,
        "feedback": "A resposta não corresponde ao texto decifrado pela configuração da missão." + dica_extra,
    }
