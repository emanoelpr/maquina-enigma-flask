
"""Implementa o plugboard da máquina Enigma."""

import re


class Plugboard:
    """Gerencia as conexões entre pares de letras."""

    max_conexoes = 13

    def __init__(self, conexoes=None):
        self.mapeamento = self.converter_plugboard(conexoes)

    @staticmethod
    def plugboard_identidade():
        """Cria o mapeamento padrão, sem trocas de letras."""
        return list(range(26))

    def converter_plugboard(self, conexoes):
        """Converte os pares de letras em um mapeamento numérico."""
        mapeamento = self.plugboard_identidade()
        if not conexoes:
            return mapeamento

        pares = re.findall(r"[A-Za-z]+", conexoes)
        if len(pares) > self.max_conexoes:
            raise ValueError(
                f"Muitas conexões: {len(pares)} "
                f"(máximo {self.max_conexoes})."
            )

        conectadas = set()
        for par in pares:
            if len(par) != 2:
                raise ValueError(
                    f"Conexão inválida: {par!r} (use exatamente 2 letras)."
                )

            primeira, segunda = (ord(letra.upper()) - ord("A") for letra in par)

            if primeira == segunda:
                raise ValueError(
                    f"Conexão inválida: {par!r} liga a letra a ela mesma."
                )
            if primeira in conectadas or segunda in conectadas:
                raise ValueError(
                    f"Conexão {par!r} usa uma letra que já está conectada."
                )

            conectadas.update((primeira, segunda))
            mapeamento[primeira], mapeamento[segunda] = segunda, primeira

        return mapeamento

    def obter_caracteres_desconectados(self):
        """Retorna os índices das letras sem conexão."""
        return [
            indice
            for indice, destino in enumerate(self.mapeamento)
            if indice == destino
        ]

    def cifrar(self, numero):
        """Aplica a troca correspondente a um índice de 0 a 25."""
        return self.mapeamento[numero]


def criar_conexoes(conexoes):
    """Cria um plugboard a partir das conexões informadas."""
    return Plugboard(conexoes)
