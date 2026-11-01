"""Implementa os refletores da máquina Enigma."""


class Refletor:
    """Gerencia os mapeamentos dos refletores da Enigma."""

    dados_refletores = {
        # Refletores da Enigma M3
        "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
        "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
        # Refletores da Kriegsmarine — Enigma M4
        "Bfino": "ENKQAUYWJICOPBLMDXZVFTHRGS",
        "Cfino": "RDOBJNTKVEHMLFCWZAXGYIPSUQ",
        # Refletor de identificação
        "Identidade": "ZYXWVUTSRQPONMLKJIHGFEDCBA",
    }

    def __init__(self, codificacao):
        """Converte a fiação do refletor em índices numéricos."""
        self.mapeamento_direto = [ord(letra) - ord("A") for letra in codificacao]
        self._validar()

    def _validar(self):
        """Verifica se o refletor é válido e simétrico."""
        mapeamento = self.mapeamento_direto

        if len(mapeamento) != 26 or sorted(mapeamento) != list(range(26)):
            raise ValueError(
                "O refletor deve conter as 26 letras, sem repetição."
            )

        for indice, saida in enumerate(mapeamento):
            if saida == indice:
                raise ValueError(
                    f"Refletor inválido: {chr(indice + 65)} mapeia para si mesma."
                )

            if mapeamento[saida] != indice:
                raise ValueError(
                    f"Refletor inválido: {chr(indice + 65)} -> "
                    f"{chr(saida + 65)}, mas "
                    f"{chr(saida + 65)} -> {chr(mapeamento[saida] + 65)}."
                )

    def cifrar(self, numero):
        """Retorna a letra correspondente ao índice de entrada."""
        return self.mapeamento_direto[numero]

    @classmethod
    def criar_refletor(cls, nome):
        """Cria um refletor a partir do nome informado."""
        if nome not in cls.dados_refletores:
            opcoes = ", ".join(cls.dados_refletores)
            raise ValueError(f"Refletor desconhecido: {nome!r}. Opções: {opcoes}")

        return cls(cls.dados_refletores[nome])