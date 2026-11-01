""" Pontuação linguística para a criptoanálise da Enigma.

As tabelas de trigramas foram geradas a partir de corpora de domínio
público (Project Gutenberg), normalizados como o resto do projeto:

- pt (~870 mil letras): Machado de Assis — "Dom Casmurro" (ebook 55752),
  "Histórias sem Data" (33056), "Cinco minutos" (44540),
  "Como e porque sou romancista" (29040); José de Alencar —
  "Ubirajara" (38496).
- en (~2,3 milhões de letras): "Pride and Prejudice" (1342),
  "Frankenstein" (84), "The Adventures of Sherlock Holmes" (1661),
  "Moby Dick" (2701).

Cada tabela guarda os 300 trigramas mais frequentes, com peso inteiro
de 1 a 10 proporcional à frequência no corpus (trigrama mais comum = 10).
A pontuação é a média dos pesos ao longo do texto — a função
pontuar_normalizacao é quem define esse cálculo, e as demais funções
apenas validam o idioma e delegam.

O idioma deve ser escolhido explicitamente: 'pt' ou 'en'."""

import unicodedata

trigramas = {
    "pt": {
        "QUE": 9, "ENT": 5, "ARA": 4, "ADE": 4, "COM": 4, "NAO": 4,
        "ERA": 4, "NTE": 3, "EST": 3, "ACA": 3, "ADO": 3, "AND": 3,
        "AVA": 3, "ODE": 3, "PAR": 3, "AMA": 3, "ELL": 3, "SSE": 3,
        "OSE": 3, "STA": 3, "DES": 3, "ACO": 3, "ASE": 3, "NDO": 3,
        "CON": 3, "UMA": 2, "MEN": 2, "MAS": 2, "OME": 2, "OQU": 2,
        "RES": 2, "AQU": 2, "NHA": 2, "ESE": 2, "DOS": 2, "ADA": 2,
        "EDE": 2, "INH": 2, "ESS": 2, "TRA": 2, "ANT": 2, "ARE": 2,
        "EQU": 2, "ASS": 2, "ASA": 2, "SDE": 2, "RAM": 2, "RAN": 2,
        "ENA": 2, "EIR": 2, "RIA": 2, "LHE": 2, "ORA": 2, "OCO": 2,
        "POR": 2, "AME": 2, "ECO": 2, "EME": 2, "OMO": 2, "CAO": 2,
        "ANA": 2, "RAS": 2, "OMA": 2, "PRO": 2, "IRA": 2, "NTA": 2,
        "OSA": 2, "SCO": 2, "NTO": 2, "TER": 2, "SEN": 2, "RAC": 2,
        "ERE": 2, "SEM": 2, "PER": 2, "IDA": 2, "ESP": 2, "LLE": 2,
        "ORE": 2, "AOS": 2, "UEE": 2, "EDI": 2, "EMA": 2, "SSA": 2,
        "SQU": 2, "DAD": 2, "MIN": 1, "REC": 1, "ESC": 1, "LLA": 1,
        "OES": 1, "ODO": 1, "OCA": 1, "RAD": 1, "MOS": 1, "OSO": 1,
        "MAI": 1, "AMO": 1, "EUM": 1, "TEN": 1, "STO": 1, "IAS": 1,
        "ONT": 1, "THE": 1, "ICA": 1, "ARI": 1, "DAS": 1, "IST": 1,
        "TIN": 1, "IRO": 1, "TRO": 1, "NOS": 1, "TOD": 1, "OSD": 1,
        "OSS": 1, "PRE": 1, "ATE": 1, "OUT": 1, "DIA": 1, "ONA": 1,
        "NDE": 1, "APA": 1, "SER": 1, "AMI": 1, "AES": 1, "CIA": 1,
        "OST": 1, "INA": 1, "ITO": 1, "AVE": 1, "SPE": 1, "VER": 1,
        "ROS": 1, "NDA": 1, "CAS": 1, "ENC": 1, "QUA": 1, "ODA": 1,
        "LHO": 1, "UER": 1, "ISS": 1, "EPO": 1, "ECE": 1, "ITA": 1,
        "AIS": 1, "ALA": 1, "AOD": 1, "DEM": 1, "DIS": 1, "ERI": 1,
        "SSO": 1, "ASD": 1, "TAR": 1, "ANC": 1, "FOR": 1, "DEU": 1,
        "UTR": 1, "OPA": 1, "MES": 1, "DEC": 1, "ASO": 1, "CAR": 1,
        "REI": 1, "RRE": 1, "END": 1, "DEP": 1, "STR": 1, "ERR": 1,
        "EES": 1, "IME": 1, "TES": 1, "EMP": 1, "AOE": 1, "OLH": 1,
        "MAN": 1, "APE": 1, "ECT": 1, "EDO": 1, "IND": 1, "CAN": 1,
        "ECA": 1, "STE": 1, "NTR": 1, "PRI": 1, "NCI": 1, "IDO": 1,
        "AVI": 1, "NCA": 1, "NTI": 1, "GUE": 1, "EPA": 1, "MAR": 1,
        "ANO": 1, "ESA": 1, "ELH": 1, "RAO": 1, "RAA": 1, "CAD": 1,
        "EMO": 1, "IAM": 1, "TAN": 1, "DOA": 1, "ASC": 1, "ATI": 1,
        "AOP": 1, "TOS": 1, "GRA": 1, "NHO": 1, "MOR": 1, "TEM": 1,
        "APO": 1, "SEU": 1, "URA": 1, "ODI": 1, "AIN": 1, "TAS": 1,
        "IAD": 1, "UEM": 1, "RAR": 1, "UEA": 1, "DEI": 1, "INT": 1,
        "RAV": 1, "DOE": 1, "DEA": 1, "SAS": 1, "ORT": 1, "RDE": 1,
        "ENO": 1, "VAM": 1, "TRE": 1, "UEN": 1, "OPO": 1, "IMA": 1,
        "SPA": 1, "ASP": 1, "ION": 1, "TAD": 1, "CHA": 1, "RQU": 1,
        "SEA": 1, "SPO": 1, "SMA": 1, "ALE": 1, "COR": 1, "OUM": 1,
        "ATA": 1, "ONO": 1, "RIO": 1, "TAV": 1, "AUM": 1, "OUS": 1,
        "SES": 1, "EUS": 1, "SSI": 1, "TED": 1, "APR": 1, "BER": 1,
        "EIT": 1, "ERG": 1, "ESD": 1, "EDA": 1, "RAE": 1, "SCA": 1,
        "SAN": 1, "DER": 1, "ECI": 1, "UAN": 1, "OSP": 1, "STI": 1,
        "UES": 1, "TAO": 1, "SED": 1, "AOC": 1, "EVE": 1, "LHA": 1,
        "HOR": 1, "CHE": 1, "ORD": 1, "OSC": 1, "MPO": 1, "IVE": 1,
        "ING": 1, "CAP": 1, "BRA": 1, "ORI": 1, "OIS": 1, "DOC": 1,
        "SIM": 1, "ELA": 1, "ENS": 1, "HOS": 1, "OMP": 1, "EPE": 1,
        "EAS": 1, "EPR": 1, "REM": 1, "SNA": 1, "TAM": 1, "SOU": 1,
    },
    "en": {
        "THE": 9, "AND": 4, "ING": 3, "HER": 3, "THA": 2, "HAT": 2,
        "ERE": 2, "HIS": 2, "ETH": 2, "ENT": 2, "NTH": 2, "FOR": 1,
        "THI": 1, "INT": 1, "YOU": 1, "TER": 1, "ITH": 1, "DTH": 1,
        "VER": 1, "ALL": 1, "HES": 1, "OTH": 1, "WAS": 1, "ION": 1,
        "TTH": 1, "OFT": 1, "FTH": 1, "WIT": 1, "STH": 1, "EST": 1,
        "NOT": 1, "ATI": 1, "SHE": 1, "REA": 1, "GHT": 1, "ERS": 1,
        "EDT": 1, "EVE": 1, "EAR": 1, "TIO": 1, "ESS": 1, "AST": 1,
        "BUT": 1, "EAN": 1, "RTH": 1, "AVE": 1, "OUR": 1, "RES": 1,
        "NCE": 1, "OME": 1, "TIN": 1, "HEN": 1, "ONE": 1, "TED": 1,
        "DIN": 1, "OUL": 1, "HOU": 1, "HEM": 1, "WHI": 1, "ATE": 1,
        "HIN": 1, "SOF": 1, "HEA": 1, "HEW": 1, "ONT": 1, "EOF": 1,
        "WHA": 1, "THO": 1, "AIN": 1, "STO": 1, "ERT": 1, "ORE": 1,
        "MAN": 1, "HAD": 1, "STA": 1, "SAN": 1, "EDA": 1, "ULD": 1,
        "ATT": 1, "EDI": 1, "NDT": 1, "IGH": 1, "NGT": 1, "SIN": 1,
        "EIN": 1, "TAN": 1, "ATH": 1, "ILL": 1, "ERA": 1, "HAV": 1,
        "OUT": 1, "ORT": 1, "CON": 1, "HAN": 1, "NTO": 1, "ETO": 1,
        "IST": 1, "OUN": 1, "NDE": 1, "RED": 1, "ARE": 1, "ERI": 1,
        "RAN": 1, "EEN": 1, "HAL": 1, "INE": 1, "HIM": 1, "HEC": 1,
        "NDI": 1, "TOT": 1, "OUS": 1, "EAT": 1, "DTO": 1, "ISH": 1,
        "ELI": 1, "NIN": 1, "EAS": 1, "HED": 1, "ONS": 1, "ESE": 1,
        "UGH": 1, "MEN": 1, "ECT": 1, "WHE": 1, "TOF": 1, "BLE": 1,
        "RIN": 1, "ROM": 1, "ERY": 1, "STE": 1, "ESA": 1, "FRO": 1,
        "ANT": 1, "CHA": 1, "NDS": 1, "RET": 1, "PER": 1, "HIC": 1,
        "COM": 1, "YTH": 1, "LES": 1, "ECO": 1, "EWH": 1, "LIN": 1,
        "ICH": 1, "EFO": 1, "STR": 1, "HEI": 1, "WER": 1, "NOW": 1,
        "IVE": 1, "IND": 1, "TEN": 1, "EWA": 1, "ESO": 1, "UND": 1,
        "DAN": 1, "ART": 1, "EMA": 1, "HTH": 1, "STI": 1, "OVE": 1,
        "HEL": 1, "ARD": 1, "LEA": 1, "NDA": 1, "OUG": 1, "NES": 1,
        "NTE": 1, "EHA": 1, "GTH": 1, "INS": 1, "HEH": 1, "COU": 1,
        "URE": 1, "NGA": 1, "EME": 1, "PRO": 1, "IDE": 1, "EAD": 1,
        "DER": 1, "ASS": 1, "UST": 1, "END": 1, "SHA": 1, "ENE": 1,
        "ALE": 1, "SOM": 1, "HEP": 1, "SEL": 1, "INA": 1, "ANC": 1,
        "TTE": 1, "OSE": 1, "NTI": 1, "SEE": 1, "OWN": 1, "ITI": 1,
        "TUR": 1, "ELL": 1, "ESH": 1, "SHO": 1, "NED": 1, "HET": 1,
        "NAN": 1, "TLE": 1, "WHO": 1, "ENO": 1, "MET": 1, "EHE": 1,
        "ABL": 1, "SSI": 1, "TIS": 1, "DON": 1, "PRE": 1, "MOR": 1,
        "NGS": 1, "EDO": 1, "ROU": 1, "ENC": 1, "ITT": 1, "VEN": 1,
        "LED": 1, "ONA": 1, "ONO": 1, "UCH": 1, "ANY": 1, "DIS": 1,
        "ESI": 1, "HEF": 1, "TRA": 1, "MIN": 1, "DNO": 1, "HEY": 1,
        "LET": 1, "LAN": 1, "HEB": 1, "SHI": 1, "ISE": 1, "RIE": 1,
        "KIN": 1, "SED": 1, "DHE": 1, "ERO": 1, "SPE": 1, "ONG": 1,
        "AME": 1, "ASI": 1, "EDH": 1, "TTO": 1, "SON": 1, "NGE": 1,
        "OST": 1, "RST": 1, "ISA": 1, "ISS": 1, "LTH": 1, "SIT": 1,
        "SAI": 1, "PAR": 1, "WIL": 1, "ASA": 1, "DBE": 1, "SSE": 1,
        "OFA": 1, "BEE": 1, "ECA": 1, "LIT": 1, "ITS": 1, "ENS": 1,
        "OFH": 1, "TIM": 1, "NST": 1, "SNO": 1, "AGE": 1, "REC": 1,
        "EDB": 1, "TWA": 1, "ERM": 1, "IME": 1, "BET": 1, "REE": 1,
        "EWI": 1, "UTT": 1, "EMO": 1, "RAT": 1, "LON": 1, "ITE": 1,
        "SEA": 1, "MES": 1, "NGI": 1, "NDW": 1, "HAR": 1, "EAL": 1,
        "SWE": 1, "ELF": 1, "AID": 1, "MTH": 1, "DEA": 1, "USE": 1,
    },
}

def normalizar(texto):
    # Mantém somente as letras A-Z
    texto = unicodedata.normalize("NFKD", texto.upper())
    
    sem_acentos = "".join(
        letra
        for letra in texto
        if not unicodedata.combining(letra) 
    )
    
    return "".join(
        letra
        for letra in sem_acentos
        if "A" <= letra <= "Z"
    )
    
def validar_idioma(idioma):
    if not isinstance(idioma, str):
        raise ValueError("Idioma inválido. Use 'pt' ou 'en'.")
    
    idioma = idioma.strip().lower()
    
    if idioma not in trigramas:
        raise ValueError("Idioma inválido. Use 'pt' ou 'en'.")

    return idioma

def pontuar_normalizacao(texto, tabela):
    quantidade = len(texto) - 2
    
    if quantidade < 1:
        return 0.0
    
    total = sum(tabela.get(texto[i:i + 3], 0) for i in range(quantidade))
    
    return total / quantidade

def pontuar_idioma(texto, idioma):
    # Pontua trigramas para um idioma
    idioma = validar_idioma(idioma)
    texto = normalizar(texto)
       
    return pontuar_normalizacao(texto, trigramas[idioma])

def pontuar(texto, idioma=None):
    # Retorna a pontuação do idioma selecionado.
    idioma = validar_idioma(idioma)
   
    return {
        "idioma": idioma,
        "pontuacao": pontuar_idioma(texto, idioma),
    }
# ------------------------------------------------------------------
# Modelo de quadrigramas — usado pela criptoanálise (pontuar_candidato
# e o avaliador acelerado). As funções originais acima continuam
# disponíveis e inalteradas para os demais usos e testes.
#
# As contagens vêm do arquivo modelo_ngramas.json, gerado por
# scripts/gerar_modelo.py a partir dos mesmos corpora do Project
# Gutenberg documentados na docstring do módulo. Cada quadrigrama é
# convertido em um valor inteiro proporcional a log10 da frequência
# (escala 1000); quadrigramas ausentes no corpus recebem um piso
# fixo, o que penaliza sequências improváveis.
# ------------------------------------------------------------------

import array as _array
import json as _json
import math as _math
import os as _os

tabelas_quad = {}


def _carregar_modelo_quadrigramas():
    """Carrega modelo_ngramas.json e monta as tabelas indexadas por inteiro."""
    if tabelas_quad:
        return
    caminho = _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "modelo_ngramas.json"
    )
    with open(caminho, encoding="utf-8") as _arq:
        _dados = _json.load(_arq)
    for _idioma, _bloco in _dados.items():
        _total = _bloco["total_quadrigramas"]
        _piso = round(1000 * _math.log10(0.1 / _total))
        _tabela = _array.array("i", [_piso]) * (26 ** 4)
        for _chave, _contagem in _bloco["quadrigramas"].items():
            _tabela[int(_chave)] = round(
                1000 * _math.log10((_contagem + 0.1) / _total)
            )
        tabelas_quad[_idioma] = _tabela


_carregar_modelo_quadrigramas()


def pontuar_quadrigramas(texto, idioma):
    """Média dos valores dos quadrigramas do texto no modelo do idioma.

    Valores mais próximos de zero (menos negativos) indicam texto mais
    parecido com o idioma. Textos com menos de 4 letras valem 0.0.
    """
    idioma = validar_idioma(idioma)
    texto = normalizar(texto)
    if len(texto) < 4:
        return 0.0

    tabela = tabelas_quad[idioma]
    codigo = [ord(letra) - 65 for letra in texto]

    chave = ((codigo[0] * 26 + codigo[1]) * 26 + codigo[2]) * 26 + codigo[3]
    soma = tabela[chave]
    for letra in codigo[4:]:
        chave = (chave % 17576) * 26 + letra
        soma += tabela[chave]

    return soma / (len(codigo) - 3)
