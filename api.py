"""API Flask para a máquina Enigma M3 e M4."""

import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from enigma import Enigma
from criptoanalise import atacar_posicoes
from tarefas import GerenciadorDeTarefas
from desafios import (
    modos,
    conquistas,
    catalogo_publico,
    configuracao_guiada,
    conquistas_catalogo,
    detalhe_publico,
    galeria_de,
    obter_dicas,
    verificar_resposta,
)

app = Flask(__name__)
CORS(app)

# Sessão assinada por cookie: guarda as missões concluídas e sustenta o
# desbloqueio de conquistas no BACKEND, sobrevivendo a recarregar a página
# e a reiniciar o processo (a limitação é por navegador, não por conta).
app.secret_key = os.environ.get(
    "ENIGMA_SECRET_KEY", "enigma-lab-chave-local-de-desenvolvimento"
)

gerenciador = GerenciadorDeTarefas()

max_mensagem = 5000

tabela_rotores = {
    nome.lower(): nome
    for nome in (
        "I", "II", "III", "IV", "V",
        "VI", "VII", "VIII", "Beta", "Gamma"
    )
}

refletores = {
    "b": "B", "c": "C",
    "bfino": "Bfino", "b-thin": "Bfino",
    "cfino": "Cfino", "c-thin": "Cfino",
}


class ErroDeEntrada(ValueError):
    """Erro de validação dos dados recebidos (resulta em HTTP 400)."""


def lista_de(dados, chave, padrao):
    valor = dados.get(chave, padrao)
    if not isinstance(valor, list):
        raise ErroDeEntrada(f"O campo '{chave}' deve ser uma lista.")
    return valor


def texto_de(dados, chave, padrao):
    valor = dados.get(chave, padrao)
    if not isinstance(valor, str):
        raise ErroDeEntrada(f"O campo '{chave}' deve ser um texto.")
    return valor


def nome_canonico(nome, tabela, rotulo):
    if not isinstance(nome, str) or nome.strip().lower() not in tabela:
        raise ErroDeEntrada(f"{rotulo} inválido: {nome!r}.")
    return tabela[nome.strip().lower()]


def converter_posicoes(posicoes):
    resultado = []
    for letra in posicoes:
        letra = str(letra).strip().upper()
        if len(letra) != 1 or not ("A" <= letra <= "Z"):
            raise ErroDeEntrada(f"Posição de rotor inválida: {letra!r}.")
        resultado.append(ord(letra) - ord("A"))
    return resultado


def converter_aneis(aneis):
    # A interface apresenta anéis de 1 a 26; o motor usa índices de 0 a 25.
    resultado = []
    for valor in aneis:
        if isinstance(valor, bool) or not isinstance(valor, (int, str)):
            raise ErroDeEntrada(f"Anel inválido: {valor!r}.")
        try:
            numero = int(valor)
        except ValueError:
            raise ErroDeEntrada(f"Anel inválido: {valor!r}.") from None
        if not 1 <= numero <= 26:
            raise ErroDeEntrada("Os anéis devem estar entre 1 e 26.")
        resultado.append(numero - 1)
    return resultado


@app.route("/api/health", methods=["GET"])
def health():
    """Verifica se a API está funcionando."""
    return jsonify({"status": "ok", "mensagem": "API Enigma funcionando."})


@app.route("/api/cifrar", methods=["POST"])
def cifrar():
    """Cifra (ou decifra) uma mensagem usando o motor Enigma existente."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um JSON válido."}), 400

    try:
        modelo = texto_de(dados, "modelo", "M3").strip().upper()
        mensagem = texto_de(dados, "mensagem", "")

        if not mensagem.strip():
            raise ErroDeEntrada("Digite uma mensagem.")
        if len(mensagem) > max_mensagem:
            raise ErroDeEntrada(
                f"A mensagem deve ter no máximo {max_mensagem} caracteres."
            )

        mensagem = "".join(c for c in mensagem.upper() if "A" <= c <= "Z")
        if not mensagem:
            raise ErroDeEntrada("A mensagem precisa conter letras de A a Z.")

        rotores = lista_de(dados, "rotores", ["I", "II", "III"])
        posicoes = lista_de(dados, "posicoes", ["A"] * (4 if modelo == "M4" else 3))
        aneis = lista_de(dados, "aneis", [1] * (4 if modelo == "M4" else 3))

        refletor = nome_canonico(
            texto_de(dados, "refletor", "Bfino" if modelo == "M4" else "B"),
            refletores, "Refletor",
        )
        plugboard = texto_de(dados, "plugboard", "")

        if modelo == "M4":
            rotor_grego = texto_de(dados, "rotor_grego", "Beta")
            nomes_rotores = [rotor_grego] + rotores
        elif modelo == "M3":
            nomes_rotores = rotores
        else:
            raise ErroDeEntrada("Modelo inválido. Use M3 ou M4.")

        nomes_rotores = tuple(
            nome_canonico(nome, tabela_rotores, "Rotor")
            for nome in nomes_rotores
        )

        if len(nomes_rotores) != len(posicoes):
            raise ErroDeEntrada(
                "A quantidade de posições não corresponde aos rotores."
            )
        if len(nomes_rotores) != len(aneis):
            raise ErroDeEntrada(
                "A quantidade de anéis não corresponde aos rotores."
            )

        maquina = Enigma(
            rotores=nomes_rotores,
            posicoes_rotores=converter_posicoes(posicoes),
            configuracoes_anel=converter_aneis(aneis),
            nome_refletor=refletor,
            conexoes_plugboard=plugboard,
        )

        resultado = maquina.cifrar_texto(mensagem)

        return jsonify({
            "modelo": modelo,
            "mensagem_original": mensagem,
            "resultado": resultado,
            "quantidade_caracteres": len(resultado),
        })

    except ValueError as erro:  # inclui ErroDeEntrada e erros do motor
        return jsonify({"erro": str(erro)}), 400

    except Exception:
        app.logger.exception("Erro interno ao cifrar mensagem.")
        return jsonify({
            "erro": "Ocorreu um erro interno ao processar a mensagem."
        }), 500


def _parametros_criptoanalise(dados):
    """Valida o corpo da requisição e devolve os parâmetros da busca."""
    modelo = texto_de(dados, "modelo", "M3").strip().upper()
    if modelo not in ("M3", "M4"):
        raise ErroDeEntrada("Modelo inválido. Use M3 ou M4.")

    mensagem = texto_de(dados, "mensagem", "")
    if not mensagem.strip():
        raise ErroDeEntrada("Digite o texto cifrado.")
    if len(mensagem) > max_mensagem:
        raise ErroDeEntrada(
            f"O texto cifrado deve ter no máximo {max_mensagem} caracteres."
        )

    rotores_recebidos = lista_de(dados, "rotores", ["I", "II", "III"])
    if len(rotores_recebidos) != 3:
        raise ErroDeEntrada("Informe exatamente três rotores principais.")
    rotores = tuple(
        nome_canonico(nome, tabela_rotores, "Rotor")
        for nome in rotores_recebidos
    )

    aneis_recebidos = lista_de(dados, "aneis", [1, 1, 1])
    if len(aneis_recebidos) != 3:
        raise ErroDeEntrada("Informe exatamente três configurações de anel.")
    aneis = []
    for valor in aneis_recebidos:
        if isinstance(valor, bool) or not isinstance(valor, (int, str)):
            raise ErroDeEntrada(f"Anel inválido: {valor!r}.")
        try:
            numero = int(valor)
        except ValueError:
            raise ErroDeEntrada(f"Anel inválido: {valor!r}.") from None
        if not 1 <= numero <= 26:
            raise ErroDeEntrada("Os anéis devem estar entre 1 e 26.")
        aneis.append(numero)

    refletor_padrao = "Bfino" if modelo == "M4" else "B"
    refletor = nome_canonico(
        texto_de(dados, "refletor", refletor_padrao),
        refletores,
        "Refletor",
    )
    rotor_grego = nome_canonico(
        texto_de(dados, "rotor_grego", "Beta"),
        {"beta": "Beta", "gamma": "Gamma"},
        "Rotor grego",
    )
    idioma = texto_de(dados, "idioma", "pt").strip().lower()
    if idioma not in ("pt", "en"):
        raise ErroDeEntrada("Idioma inválido. Use 'pt' ou 'en'.")

    limite = dados.get("limite", 10)
    if isinstance(limite, bool) or not isinstance(limite, int):
        raise ErroDeEntrada("O limite deve ser um número inteiro positivo.")
    if not 1 <= limite <= 100:
        raise ErroDeEntrada("O limite deve estar entre 1 e 100.")

    return {
        "texto_cifrado": mensagem,
        "rotores": rotores,
        "aneis": aneis,
        "refletor": refletor,
        "idioma": idioma,
        "limite": limite,
        "modelo": modelo,
        "rotor_grego": rotor_grego,
    }


@app.route("/api/criptoanalise", methods=["POST"])
def criptoanalise():
    """Busca síncrona de posições iniciais (mantida por compatibilidade).

    A interface usa o fluxo de tarefas em segundo plano, que permite
    acompanhar o progresso real e cancelar; esta rota continua
    funcionando exatamente como antes.
    """
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um JSON válido."}), 400

    try:
        resultado = atacar_posicoes(**_parametros_criptoanalise(dados))
        return jsonify(resultado)

    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    except Exception:
        app.logger.exception("Erro interno durante a criptoanálise.")
        return jsonify({
            "erro": "Ocorreu um erro interno durante a criptoanálise."
        }), 500


@app.route("/api/criptoanalise/tarefas", methods=["POST"])
def criar_tarefa_criptoanalise():
    """Cria uma tarefa de busca em segundo plano e devolve o identificador."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um JSON válido."}), 400

    try:
        parametros = _parametros_criptoanalise(dados)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    return jsonify(gerenciador.iniciar(parametros))


@app.route("/api/criptoanalise/tarefas/<id_tarefa>", methods=["GET"])
def estado_tarefa_criptoanalise(id_tarefa):
    """Devolve o estado e o progresso real de uma tarefa de busca."""
    estado = gerenciador.estado(id_tarefa)
    if estado is None:
        return jsonify({"erro": "Tarefa não encontrada."}), 404
    return jsonify(estado)


@app.route("/api/criptoanalise/tarefas/<id_tarefa>/cancelar", methods=["POST"])
def cancelar_tarefa_criptoanalise(id_tarefa):
    """Solicita o cancelamento real da busca no backend."""
    estado = gerenciador.cancelar(id_tarefa)
    if estado is None:
        return jsonify({"erro": "Tarefa não encontrada."}), 404
    return jsonify(estado)


@app.route("/api/percurso", methods=["POST"])
def percurso():
    """Calcula o percurso elétrico de UMA letra com o motor Enigma real.

    A máquina é criada com a configuração recebida (posições já evoluídas,
    quando o frontend estiver processando letras sucessivas) e o resultado
    inclui a letra final e as posições após o avanço, permitindo que a
    próxima requisição continue exatamente de onde a anterior parou.
    """
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um JSON válido."}), 400

    try:
        modelo = texto_de(dados, "modelo", "M3").strip().upper()
        if modelo not in ("M3", "M4"):
            raise ErroDeEntrada("Modelo inválido. Use M3 ou M4.")

        letra = texto_de(dados, "letra", "").strip().upper()
        if len(letra) != 1 or not ("A" <= letra <= "Z"):
            raise ErroDeEntrada("Informe exatamente uma letra de A a Z.")

        rotores = lista_de(dados, "rotores", ["I", "II", "III"])
        posicoes = lista_de(dados, "posicoes", ["A"] * (4 if modelo == "M4" else 3))
        aneis = lista_de(dados, "aneis", [1] * (4 if modelo == "M4" else 3))

        refletor = nome_canonico(
            texto_de(dados, "refletor", "Bfino" if modelo == "M4" else "B"),
            refletores, "Refletor",
        )
        plugboard = texto_de(dados, "plugboard", "")

        if modelo == "M4":
            rotor_grego = texto_de(dados, "rotor_grego", "Beta")
            nomes_rotores = [rotor_grego] + rotores
        else:
            nomes_rotores = rotores

        nomes_rotores = tuple(
            nome_canonico(nome, tabela_rotores, "Rotor")
            for nome in nomes_rotores
        )

        if len(nomes_rotores) != len(posicoes) or len(nomes_rotores) != len(aneis):
            raise ErroDeEntrada(
                "A quantidade de posições e anéis deve corresponder aos rotores."
            )

        maquina = Enigma(
            rotores=nomes_rotores,
            posicoes_rotores=converter_posicoes(posicoes),
            configuracoes_anel=converter_aneis(aneis),
            nome_refletor=refletor,
            conexoes_plugboard=plugboard,
        )

        resultado, etapas = maquina.cifrar_com_rastreamento(ord(letra) - ord("A"))

        def letra_de(valor):
            return chr(valor + ord("A"))

        etapas_formatadas = []
        for etapa in etapas:
            formatada = {
                "componente": etapa["componente"],
                "antes": letra_de(etapa["antes"]),
                "depois": letra_de(etapa["depois"]),
            }
            if "sentido" in etapa:
                formatada["sentido"] = etapa["sentido"]
                formatada["posicao"] = letra_de(etapa["posicao"])
            etapas_formatadas.append(formatada)

        # Ordem das posições finais igual à ordem de entrada: rotor grego
        # primeiro na M4, depois esquerdo, central e direito.
        posicoes_finais = []
        if maquina.rotor_grego is not None:
            posicoes_finais.append(letra_de(maquina.rotor_grego.posicao_rotor))
        posicoes_finais.extend(
            letra_de(rotor.posicao_rotor)
            for rotor in (maquina.rotor_esquerdo, maquina.rotor_central, maquina.rotor_direito)
        )

        return jsonify({
            "modelo": modelo,
            "letra_entrada": letra,
            "letra_saida": letra_de(resultado),
            "etapas": etapas_formatadas,
            "posicoes_finais": posicoes_finais,
        })

    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    except Exception:
        app.logger.exception("Erro interno ao calcular o percurso da letra.")
        return jsonify({
            "erro": "Ocorreu um erro interno ao calcular o percurso."
        }), 500

@app.route("/api/desafios", methods=["GET"])
def listar_desafios():
    """Catálogo público de missões (sem resposta nem configuração)."""
    return jsonify({"missoes": catalogo_publico()})


@app.route("/api/desafios/<id_missao>", methods=["GET"])
def detalhar_desafio(id_missao):
    try:
        return jsonify(detalhe_publico(id_missao))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 404


@app.route("/api/desafios/<id_missao>/dica", methods=["POST"])
def dica_desafio(id_missao):
    """Libera as dicas progressivas 1..n de uma missão."""
    dados = request.get_json(silent=True) or {}
    try:
        return jsonify({"dicas": obter_dicas(id_missao, dados.get("nivel", 1))})
    except ValueError as erro:
        mensagem = str(erro)
        return jsonify({"erro": mensagem}), 404 if "não encontrada" in mensagem else 400


@app.route("/api/desafios/<id_missao>/verificar", methods=["POST"])
def verificar_desafio(id_missao):
    """Valida a resposta com o motor real e controla o desbloqueio no backend.

    A pontuação pelo modo e a conquista são decididas AQUI, na sessão do
    servidor: repetir a mesma resposta correta não gera pontos nem nova
    conquista, e o frontend não consegue declarar missão concluída sem
    passar por esta validação.
    """
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um JSON válido."}), 400

    modo = dados.get("modo", "especialista")
    if modo not in MODOS:
        return jsonify({"erro": f"Modo inválido. Use: {', '.join(MODOS)}."}), 400

    try:
        resultado = verificar_resposta(id_missao, dados.get("resposta", ""), modo)
    except ValueError as erro:
        mensagem = str(erro)
        return jsonify({"erro": mensagem}), 404 if "não encontrada" in mensagem else 400

    if resultado["correto"]:
        concluidas = session.setdefault("missoes_concluidas", {})
        if id_missao in concluidas:
            resultado["primeira_conclusao"] = False
            resultado["pontos"] = 0
            resultado["nova_conquista"] = None
        else:
            concluidas[id_missao] = {"modo": modo, "pontos": resultado["pontos"]}
            session.modified = True
            resultado["primeira_conclusao"] = True
    return jsonify(resultado)


@app.route("/api/desafios/progresso", methods=["GET"])
def progresso_desafios():
    """Estado persistente do participante (sessão assinada do servidor)."""
    concluidas = session.get("missoes_concluidas", {})
    return jsonify({
        "concluidas": concluidas,
        "pontos_total": sum(registro["pontos"] for registro in concluidas.values()),
        "conquistas": [
            ACHIEVEMENTS[id_missao]["id"]
            for id_missao in concluidas
            if id_missao in ACHIEVEMENTS
        ],
    })


@app.route("/api/desafios/conquistas", methods=["GET"])
def listar_conquistas():
    """Catálogo completo de conquistas (estado fica no progresso)."""
    return jsonify({"conquistas": conquistas_catalogo()})


@app.route("/api/desafios/<id_missao>/configuracao-guiada", methods=["GET"])
def configuracao_guiada_desafio(id_missao):
    """Configuração oficial da missão — prevista para o MODO GUIADO.

    Projeto educacional sem contas: este endpoint não exige autenticação
    e a limitação é assumida e documentada no módulo desafios.py.
    """
    try:
        return jsonify(configuracao_guiada(id_missao))
    except ValueError:
        return jsonify({"erro": "Missão não encontrada."}), 404


@app.route("/api/desafios/<id_missao>/galeria", methods=["GET"])
def galeria_desafio(id_missao):
    """Galeria histórica liberada SOMENTE após a conclusão da missão."""
    concluidas = session.get("missoes_concluidas", {})
    if id_missao not in concluidas:
        return jsonify({"erro": "Conclua a missão para abrir a galeria histórica."}), 403
    try:
        return jsonify({"itens": galeria_de(id_missao)})
    except ValueError:
        return jsonify({"erro": "Missão não encontrada."}), 404

if __name__ == "__main__":
    # O modo debug só deve ser ligado de propósito: ENIGMA_DEBUG=1.
    # threaded=True permite consultar o progresso (e cancelar) enquanto
    # uma busca roda no backend.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.environ.get("ENIGMA_DEBUG") == "1",
        threaded=True,
    )