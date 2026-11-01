"""Implementa os rotores da máquina Enigma."""

alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Rotor:
    """Representa um rotor, sua fiação, posição e configuração do anel."""

    # Dados dos rotores: (fiação, letras dos entalhes)
    # VI, VII e VIII possuem dois entalhes: Z e M.
    dados_rotores = {
        "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
        "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
        "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
        "IV": ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
        "V": ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
        "VI": ("JPGVOUMFYQBENHZRDKASXLICTW", "ZM"),
        "VII": ("NZJHGRCXMYSWBOUFAIVLPEKQDT", "ZM"),
        "VIII": ("FKQHTLXOCBJSPDZRAMEWNIUYGV", "ZM"),
        "Beta": ("LEYJVCNIXWPBQMDRTAKZGFUHOS", ""),
        "Gamma": ("FSOKANUERHMBTIYCWLQPZXVGJD", ""),
        "Identidade": (alfabeto, ""),
    }

    def __init__(
        self, nome, mapeamento, posicao_rotor, entalhes, configuracao_anel
    ):
        """Inicializa a fiação, a posição, os entalhes e o anel do rotor."""
        self.nome = nome
        self.mapeamento_direto = [ord(letra) - ord("A") for letra in mapeamento]
        self.mapeamento_reverso = self._inverter(self.mapeamento_direto)
        self.posicao_rotor = int(posicao_rotor) % 26
        self.entalhes = tuple(ord(letra) - ord("A") for letra in entalhes)
        self.configuracao_anel = int(configuracao_anel) % 26

    @staticmethod
    def _inverter(mapeamento):
        """Cria a tabela inversa da fiação do rotor."""
        inverso = [0] * 26
        for entrada, saida in enumerate(mapeamento):
            inverso[saida] = entrada
        return inverso

    def _cifrar(self, numero, tabela):
        """Aplica a fiação considerando a posição e a configuração do anel."""
        deslocamento = self.posicao_rotor - self.configuracao_anel
        entrada = (numero + deslocamento) % 26
        saida = tabela[entrada]
        return (saida - deslocamento) % 26

    def cifrar_direto(self, numero):
        """Percorre a fiação do rotor no sentido direto."""
        return self._cifrar(numero, self.mapeamento_direto)

    def cifrar_reverso(self, numero):
        """Percorre a fiação do rotor no sentido inverso."""
        return self._cifrar(numero, self.mapeamento_reverso)

    def esta_na_posicao_do_entalhe(self):
        """Verifica se o rotor está em uma posição de entalhe."""
        return self.posicao_rotor in self.entalhes

    def rotacionar(self):
        """Avança o rotor uma posição."""
        self.posicao_rotor = (self.posicao_rotor + 1) % 26

    @classmethod
    def criar_rotor(cls, nome, posicao_rotor=0, configuracao_anel=0):
        """Cria um rotor a partir do nome e das configurações informadas."""
        if nome not in cls.dados_rotores:
            opcoes = ", ".join(cls.dados_rotores)
            raise ValueError(f"Rotor desconhecido: {nome!r}. Opções: {opcoes}")

        mapeamento, entalhes = cls.dados_rotores[nome]
        return cls(nome, mapeamento, posicao_rotor, entalhes, configuracao_anel)