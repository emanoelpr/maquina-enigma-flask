"""Execução de criptoanálise em segundo plano, com progresso e cancelamento.

O progresso reportado é o trabalho real da busca (combinacoes_testadas
atualizado por atacar_posicoes); o cancelamento interrompe o laço em
pontos seguros e frequentes. Nada aqui é simulado com temporizadores.
"""

import threading
import time
import uuid

from criptoanalise import BuscaCancelada, atacar_posicoes


class GerenciadorDeTarefas:
    """Mantém as tarefas de busca e o estado compartilhado entre threads.

    Cada tarefa roda em uma thread daemon. O estado é protegido por uma
    trava única; leituras devolvem um retrato (snapshot) do momento.
    """

    def __init__(self):
        self._tarefas = {}
        self._trava = threading.Lock()

    def iniciar(self, parametros):
        """Cria a tarefa, inicia a thread e devolve o estado inicial."""
        total = 26 ** 4 if parametros["modelo"] == "M4" else 26 ** 3
        id_tarefa = uuid.uuid4().hex[:12]
        tarefa = {
            "id_tarefa": id_tarefa,
            "estado": "executando",
            "combinacoes_testadas": 0,
            "total_combinacoes": total,
            "inicio": time.time(),
            "resultado": None,
            "erro": None,
            "cancelamento": threading.Event(),
        }

        def executar():
            try:
                resultado = atacar_posicoes(
                    progresso=self._registrar_progresso(tarefa),
                    cancelado=tarefa["cancelamento"].is_set,
                    **parametros,
                )
                with self._trava:
                    tarefa["estado"] = "concluida"
                    tarefa["resultado"] = resultado
            except BuscaCancelada:
                with self._trava:
                    tarefa["estado"] = "cancelada"
            except Exception as erro:  # registrada e devolvida ao usuário
                with self._trava:
                    tarefa["estado"] = "erro"
                    tarefa["erro"] = str(erro)

        thread = threading.Thread(target=executar, daemon=True)
        with self._trava:
            self._tarefas[id_tarefa] = tarefa
        thread.start()
        return self.estado(id_tarefa)

    def _registrar_progresso(self, tarefa):
        """Devolve a função de progresso que atualiza o estado da tarefa."""

        def progresso(feitas, total):
            with self._trava:
                tarefa["combinacoes_testadas"] = feitas
                tarefa["total_combinacoes"] = total

        return progresso

    def estado(self, id_tarefa):
        """Retrato do estado atual da tarefa (ou None se inexistente)."""
        with self._trava:
            tarefa = self._tarefas.get(id_tarefa)
            if tarefa is None:
                return None
            total = tarefa["total_combinacoes"] or 1
            retrato = {
                "id_tarefa": id_tarefa,
                "estado": tarefa["estado"],
                "combinacoes_testadas": tarefa["combinacoes_testadas"],
                "total_combinacoes": tarefa["total_combinacoes"],
                "porcentagem": round(
                    100 * tarefa["combinacoes_testadas"] / total, 1
                ),
                "tempo_decorrido": round(time.time() - tarefa["inicio"], 2),
            }
            if tarefa["estado"] == "concluida":
                retrato["resultado"] = tarefa["resultado"]
            if tarefa["estado"] == "erro":
                retrato["erro"] = tarefa["erro"]
            return retrato

    def cancelar(self, id_tarefa):
        """Solicita cancelamento; devolve o estado atual (None se inexistente)."""
        with self._trava:
            tarefa = self._tarefas.get(id_tarefa)
            if tarefa is None:
                return None
            tarefa["cancelamento"].set()
        return self.estado(id_tarefa)