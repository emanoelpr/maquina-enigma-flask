"""Gerenciamento de tarefas de criptoanálise em segundo plano.

Suporta tanto a API legada (atacar_posicoes) quanto os novos modos
(configurada, ampliada e avançada) de busca. O progresso é baseado em
callbacks reais dos algoritmos, nunca em temporizadores simulados.
"""

import threading
import time
import uuid

from criptoanalise import BuscaCancelada, atacar_posicoes
from busca_configuracoes import investigar


class ServidorOcupado(RuntimeError):
    """Indica que o limite de buscas simultâneas foi atingido."""


class GerenciadorDeTarefas:
    """Executa buscas em threads e fornece snapshots seguros para consulta."""

    def __init__(self, max_concorrentes=1):
        if isinstance(max_concorrentes, bool) or not isinstance(max_concorrentes, int) or max_concorrentes < 1:
            raise ValueError("max_concorrentes deve ser um inteiro positivo.")
        self._tarefas = {}
        self._trava = threading.Lock()
        self._max_concorrentes = max_concorrentes

    def iniciar(self, parametros):
        """Valida capacidade, registra a tarefa e inicia a execução."""
        parametros = dict(parametros)
        modo_novo = "modo" in parametros
        espaco = parametros.pop("espaco", None)
        modelo = parametros.get("modelo", "M3")
        total_inicial = (
            int((espaco or {}).get("configuracoes_exaustivas") or 0)
            if modo_novo
            else (26 ** 4 if modelo == "M4" else 26 ** 3)
        )
        id_tarefa = uuid.uuid4().hex[:12]
        agora = time.time()
        tarefa = {
            "id_tarefa": id_tarefa,
            "estado": "executando",
            "modo": parametros.get("modo", "configurada" if modo_novo else "legada"),
            "modelo": modelo,
            "combinacoes_testadas": 0,
            "total_combinacoes": total_inicial,
            "porcentagem": 0.0,
            "avaliadas_total": 0,
            "fase_nome": "Preparando busca",
            "fase_numero": 1,
            "fases_total": 1,
            "fase_feitas": 0,
            "fase_total": total_inicial,
            "inicio": agora,
            "resultado": None,
            "erro": None,
            "cancelamento": threading.Event(),
        }

        with self._trava:
            ativas = sum(1 for t in self._tarefas.values() if t["estado"] == "executando")
            if ativas >= self._max_concorrentes:
                raise ServidorOcupado(
                    "Já existe uma criptoanálise em execução. Aguarde sua conclusão ou cancele-a antes de iniciar outra."
                )
            self._tarefas[id_tarefa] = tarefa

        def executar():
            progresso = self._registrar_progresso(tarefa)
            try:
                if modo_novo:
                    # 'espaco' é metadado da API, não argumento de investigar().
                    resultado = investigar(
                        progresso=progresso,
                        cancelado=tarefa["cancelamento"].is_set,
                        **parametros,
                    )
                else:
                    resultado = atacar_posicoes(
                        progresso=progresso,
                        cancelado=tarefa["cancelamento"].is_set,
                        **parametros,
                    )
                with self._trava:
                    tarefa["estado"] = "concluida"
                    tarefa["resultado"] = resultado
                    tarefa["porcentagem"] = 100.0
                    tarefa["fase_nome"] = "Concluída"
                    tarefa["tempo_total"] = round(time.time() - tarefa["inicio"], 3)
            except BuscaCancelada as erro:
                with self._trava:
                    tarefa["estado"] = "cancelada"
                    tarefa["erro"] = None
                    tarefa["avaliadas_total"] = max(
                        tarefa["avaliadas_total"],
                        getattr(erro, "combinacoes_testadas", 0),
                    )
                    tarefa["fase_nome"] = "Cancelada"
                    tarefa["tempo_total"] = round(time.time() - tarefa["inicio"], 3)
            except Exception as erro:  # snapshot expõe a falha para diagnóstico
                with self._trava:
                    tarefa["estado"] = "erro"
                    tarefa["erro"] = str(erro)
                    tarefa["fase_nome"] = "Erro"
                    tarefa["tempo_total"] = round(time.time() - tarefa["inicio"], 3)

        thread = threading.Thread(target=executar, daemon=True, name=f"cripto-{id_tarefa}")
        thread.start()
        return self.estado(id_tarefa)

    def _registrar_progresso(self, tarefa):
        """Aceita callbacks legados (feitas,total) e eventos estruturados."""
        def progresso(*args):
            with self._trava:
                if len(args) == 1 and isinstance(args[0], dict):
                    evento = args[0]
                    fase = evento.get("fase")
                    if isinstance(fase, (tuple, list)):
                        tarefa["fase_nome"] = str(fase[0])
                        if len(fase) > 1:
                            tarefa["fase_numero"] = int(fase[1])
                        if len(fase) > 2:
                            tarefa["fases_total"] = int(fase[2])
                    feitas = int(evento.get("fase_feitas", 0) or 0)
                    total = int(evento.get("fase_total", 0) or 0)
                    avaliadas = int(evento.get("avaliadas", feitas) or 0)
                    tarefa["fase_feitas"] = feitas
                    tarefa["fase_total"] = total
                    tarefa["combinacoes_testadas"] = feitas
                    tarefa["total_combinacoes"] = total
                    tarefa["avaliadas_total"] = max(tarefa["avaliadas_total"], avaliadas)
                    tarefa["porcentagem"] = round(100 * feitas / total, 1) if total else 0.0
                    parciais = evento.get("parciais")
                    tarefa["parciais"] = parciais if parciais is not None else None
                elif len(args) == 2:
                    feitas, total = int(args[0]), int(args[1])
                    tarefa["fase_nome"] = "Posições iniciais"
                    tarefa["fase_numero"] = 1
                    tarefa["fases_total"] = 1
                    tarefa["fase_feitas"] = feitas
                    tarefa["fase_total"] = total
                    tarefa["combinacoes_testadas"] = feitas
                    tarefa["total_combinacoes"] = total
                    tarefa["avaliadas_total"] = feitas
                    tarefa["porcentagem"] = round(100 * feitas / total, 1) if total else 0.0
                else:
                    raise TypeError("Formato inesperado do callback de progresso.")
        return progresso

    def estado(self, id_tarefa):
        """Retorna um snapshot sem expor objetos de thread ou eventos."""
        with self._trava:
            tarefa = self._tarefas.get(id_tarefa)
            if tarefa is None:
                return None
            retrato = {
                "id_tarefa": id_tarefa,
                "estado": tarefa["estado"],
                "modo": tarefa["modo"],
                "modelo": tarefa["modelo"],
                "fase_nome": tarefa["fase_nome"],
                "fase_numero": tarefa["fase_numero"],
                "fases_total": tarefa["fases_total"],
                "fase_feitas": tarefa["fase_feitas"],
                "fase_total": tarefa["fase_total"],
                "combinacoes_testadas": tarefa["combinacoes_testadas"],
                "total_combinacoes": tarefa["total_combinacoes"],
                "avaliadas_total": tarefa["avaliadas_total"],
                "porcentagem": tarefa["porcentagem"],
                "tempo_decorrido": round(time.time() - tarefa["inicio"], 2),
            }
            if tarefa.get("parciais") is not None:
                retrato["parciais"] = tarefa["parciais"]
            if tarefa["estado"] == "concluida":
                retrato["resultado"] = tarefa["resultado"]
            if tarefa["estado"] == "erro":
                retrato["erro"] = tarefa["erro"]
            if tarefa.get("tempo_total") is not None:
                retrato["tempo_total"] = tarefa["tempo_total"]
            return retrato

    def cancelar(self, id_tarefa):
        """Solicita cancelamento cooperativo da tarefa."""
        with self._trava:
            tarefa = self._tarefas.get(id_tarefa)
            if tarefa is None:
                return None
            if tarefa["estado"] == "executando":
                tarefa["cancelamento"].set()
        return self.estado(id_tarefa)
