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

galeria = {
    "primeira-leitura": [
        {
            "arquivo": "assets/galeria/m1-enigma-em-uso.jpg",
            "autoria": "Grupp / Bundesarchiv",
            "credito_licenca": (
                "Bundesarchiv, Bild 101I-241-2173-06 / Grupp / CC BY-SA 3.0 DE. "
                "Licença: https://creativecommons.org/licenses/by-sa/3.0/de/deed.en"
            ),
            "data": "1943",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_101I-241-2173-06,_Russland,_Verschlüsselungsgerät_Enigma.jpg",
            "local": "Frente Oriental, território da então União Soviética (descrição do Bundesarchiv)",
            "relacao": "Fotografia histórica de uma Enigma em uso operacional; não é a mensagem fictícia desta missão.",
            "tipo": "historica",
            "titulo_legenda": "Máquina Enigma em uso operacional, fotografada na Rússia em 1943.",
        },
        {
            "arquivo": "assets/galeria/m1-enigma-museu.jpg",
            "autoria": "Infrogmation of New Orleans",
            "credito_licenca": "Infrogmation of New Orleans, GNU Free Documentation License 1.2 ou posterior; preserve a licença e o crédito.",
            "data": "Setembro de 2007",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:DDayMuseumEnigmaMach.jpg",
            "local": "The National WWII Museum, Nova Orleans, Estados Unidos",
            "relacao": "Fotografia de uma máquina Enigma preservada em exposição; imagem atual de um artefato histórico.",
            "tipo": "atual",
            "titulo_legenda": "Máquina Enigma preservada em exposição no National WWII Museum.",
        },
    ],
    "radio-do-deserto": [
        {
            "arquivo": "assets/galeria/m2-afrika-korps-comboio.jpg",
            "autoria": "Forças armadas australianas / Australian War Memorial",
            "credito_licenca": "Australian War Memorial, coleção P03091.004; imagem marcada como domínio público por expiração dos direitos autorais.",
            "data": "1942",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:Afrika_Korps_vehicle_convoy_in_1942.jpg",
            "local": "Deserto do Norte da África",
            "relacao": "Mostra uma coluna de veículos do Afrika Korps no deserto, relacionada ao teatro de operações da missão.",
            "tipo": "historica",
            "titulo_legenda": "Coluna de veículos do Afrika Korps atravessando o deserto, 1942.",
        },
        {
            "arquivo": "assets/galeria/m2-soldado-deserto.jpg",
            "autoria": "Otto / Bundesarchiv",
            "credito_licenca": "Bundesarchiv, Bild 101I-785-0285-14A / Otto / CC BY-SA 3.0 DE. Licença: https://creativecommons.org/licenses/by-sa/3.0/de/deed.en",
            "data": "Abril de 1941",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_101I-785-0285-14A,_Nordafrika,_Soldat_mit_Sandschutz.jpg",
            "local": "Norte da África",
            "relacao": "Fotografia de um soldado do Afrika Korps usando proteção contra areia e poeira; contexto visual da campanha no deserto.",
            "tipo": "historica",
            "titulo_legenda": "Soldado do Afrika Korps com proteção contra areia e poeira, Norte da África, 1941.",
        },
    ],
    "comboio-atlantico": [
        {
            "arquivo": "assets/galeria/m3-escolta-atlantico.jpg",
            "autoria": "H. A. Mason (Lt), fotógrafo oficial da Royal Navy / Imperial War Museums",
            "credito_licenca": "Imperial War Museums, fotografia A 20973; marcada como domínio público por expiração do Crown Copyright britânico.",
            "data": "Segunda Guerra Mundial, 1939–1945 (dia exato não confirmado)",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:The_Battle_of_the_Atlantic_1939-1945_A20973.jpg",
            "local": "Atlântico Norte",
            "relacao": "Mostra um navio de escolta navegando em mar agitado durante a proteção de um comboio.",
            "tipo": "historica",
            "titulo_legenda": "Navio de escolta atravessa mar agitado durante a Batalha do Atlântico.",
        },
        {
            "arquivo": "assets/galeria/m3-comboio-tropas.jpg",
            "autoria": "R. G. Coote (Lt), fotógrafo oficial da Royal Navy / Imperial War Museums",
            "credito_licenca": "Imperial War Museums, fotografia A 12883; marcada como domínio público por expiração do Crown Copyright britânico.",
            "data": "Segunda Guerra Mundial, 1939–1945 (dia exato não confirmado)",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:The_Battle_of_the_Atlantic_1939-1945_A12883.jpg",
            "local": "Atlântico; comboio com destino ao Norte da África",
            "relacao": "Registra um comboio de tropas em rota para o Norte da África, ilustrando a logística marítima da guerra.",
            "tipo": "historica",
            "titulo_legenda": "Comboio de tropas a caminho do Norte da África durante a Segunda Guerra Mundial.",
        },
    ],
    "estacao-de-escuta": [
        {
            "arquivo": "assets/galeria/m4-bombe-1945.jpg",
            "autoria": "Autor desconhecido; fotografia governamental de GC&CS",
            "credito_licenca": "Fotografia de 1945 do Government Code and Cypher School; Wikimedia Commons indica domínio público sob as regras de Crown Copyright do Reino Unido.",
            "data": "1945",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:Wartime_picture_of_a_Bletchley_Park_Bombe.jpg",
            "local": "Bletchley Park, Buckinghamshire, Reino Unido",
            "relacao": "Mostra uma Bombe usada no trabalho de criptoanálise; não é uma máquina Enigma nem uma estação de interceptação de rádio.",
            "tipo": "historica",
            "titulo_legenda": "Fotografia de época de uma Bombe em Bletchley Park, 1945.",
        },
        {
            "arquivo": "assets/galeria/m4-bletchley-park-atual.jpg",
            "autoria": "Matt Crypto",
            "credito_licenca": "Fotografia publicada por Matt Crypto em domínio público (CC0 / dedicação ao domínio público, conforme a página do arquivo).",
            "data": "2005",
            "fonte_url": "https://commons.wikimedia.org/wiki/File:Bletchley_Park.jpg",
            "local": "Bletchley Park, Buckinghamshire, Reino Unido",
            "relacao": "Fotografia atual do edifício histórico onde funcionou o centro britânico de criptoanálise.",
            "tipo": "atual",
            "titulo_legenda": "A mansão de Bletchley Park em fotografia de 2005.",
        },
    ],
}


dicas = {
    # Pistas em estilo narrativo: personagens genéricos e fictícios
    # (operador de rádio, técnico, analista) relatam a configuração real
    # de cada missão, revelando-a progressivamente. Nenhum dado técnico
    # foi alterado: cada pista permanece fiel à configuração validada.
    'primeira-leitura': [
        'O operador de rádio se aproxima e fala em voz baixa: "Pelo padrão '
        'do equipamento, esta mensagem saiu de uma Enigma M3. Os rotores na '
        'máquina são, da esquerda para a direita, I, II e III."',
        'O técnico aponta para o painel: "Refletor B e anéis 1-1-1 — nada '
        'alterado nesse setor. Falta o detalhe que muda tudo: as posições '
        'iniciais das três janelas."',
        'Uma anotação chega à mesa: "As posições são A-A-A. Monte a máquina, '
        'digite a mensagem cifrada e cole aqui o que as lâmpadas '
        'soletrarem."',
    ],
    'radio-do-deserto': [
        'O sargento de sinais examina a fita do rádio: "É uma M3, sem '
        'dúvida. E hoje a ordem dos rotores foi trocada: IV à esquerda, II '
        'no centro, V à direita. O refletor é o C."',
        'O técnico aponta para o painel: "Anéis 1-6-14 e o plugboard está '
        'livre — nenhuma conexão hoje. Só não sabemos ainda as posições das '
        'janelas."',
        'Um colega da equipe desliza um bilhete sobre a mesa: "As posições '
        'iniciais são H-C-L. Prepare a máquina e devolva esta mensagem ao '
        'nosso idioma."',
    ],
    'estacao-de-escuta': [
        'A operadora da estação de escuta sussurra ao telefone: "Confirmado: '
        'é uma M3 com os rotores I, III e IV, nessa ordem, e refletor B. O '
        'resto é com você."',
        'O analista aponta para a margem da folha de chaves: "Posições K-E-Z '
        'e anéis 3-1-9. Mas atenção: há algo a mais entre o teclado e os '
        'rotores."',
        'Uma nova anotação chega à mesa: "Há três conexões no plugboard — '
        'AV, BS e CG. Pares de letras trocam de lugar antes mesmo de o '
        'sinal entrar nos rotores."',
    ],
    'comboio-atlantico': [
        'O analista naval aponta a fotografia do submarino: "Esta é a M4 de '
        'quatro rotores: o grego Beta à esquerda, depois VI, II e VIII. E o '
        'refletor é o fino, o Bfino."',
        'O técnico aponta para o painel: "Os anéis são 1-8-14-21 — na '
        'interface, informe os quatro valores: o primeiro pertence ao rotor '
        'grego."',
        'Uma cópia interceptada chega à mesa: "As posições iniciais são '
        'S-D-T-C — a primeira é a do rotor grego. Ele não avança durante a '
        'mensagem; não se esqueça disso."',
    ],
}



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
            "imagem": next(
                (
                    item["arquivo"]
                    for item in galeria.get(id_missao, [])
                    if item.get("arquivo")
                ),
                None,
            ),
            "missao": id_missao,
        }
        for id_missao, info in conquistas.items()
    ]


def obter_dicas(id_missao, ate_nivel):
    """Devolve as dicas 1..ate_nivel (liberação progressiva)."""
    if id_missao not in missoes:
        raise ValueError("Missão não encontrada.")
    dicas_missao = dicas[id_missao]
    if (
        isinstance(ate_nivel, bool)
        or not isinstance(ate_nivel, int)
        or not 1 <= ate_nivel <= len(dicas_missao)
    ):
        raise ValueError(
            f"O nível da dica deve ser um número entre 1 e {len(dicas_missao)}."
        )
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
