"""Implementa o funcionamento da máquina Enigma M3 e M4."""

from rotor import Rotor
from plugboard import Plugboard
from refletor import Refletor


class Enigma:
    """Representa uma máquina Enigma com três ou quatro rotores."""

    # Combinações históricas disponíveis
    rotores_padrao = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")
    rotores_gregos = ("Beta", "Gamma")
    refletores_m3 = ("B", "C")
    refletores_m4 = ("Bfino", "Cfino")

    def __init__(
        self,
        rotores,
        posicoes_rotores,
        configuracoes_anel,
        nome_refletor,
        conexoes_plugboard,
    ):
        """Valida a configuração e inicializa os componentes da máquina."""
        if len(rotores) not in (3, 4):
            raise ValueError("Use três ou quatro rotores.")
        if len(set(rotores)) != len(rotores):
            raise ValueError("Não use o mesmo rotor duas vezes.")

        # A M4 utiliza um rotor grego e um refletor fino.
        self.nome_refletor = nome_refletor
        if len(rotores) == 4:
            if rotores[0] not in self.rotores_gregos:
                raise ValueError("Na M4, o primeiro rotor deve ser Beta ou Gamma.")
            if nome_refletor not in self.refletores_m4:
                raise ValueError("Na M4, use o refletor Bfino ou Cfino.")
            rotores_normais = rotores[1:]
        else:
            if nome_refletor not in self.refletores_m3:
                raise ValueError("Na M3, use o refletor B ou C.")
            rotores_normais = rotores

        for nome in rotores_normais:
            if nome not in self.rotores_padrao:
                raise ValueError(f"Rotor inválido nesta posição: {nome!r}.")

        if len(posicoes_rotores) != len(rotores):
            raise ValueError(
                "A quantidade de posições deve ser igual à quantidade de rotores."
            )
        if len(configuracoes_anel) != len(rotores):
            raise ValueError(
                "A quantidade de configurações de anel deve ser igual "
                "à quantidade de rotores."
            )

        # Na M4, o rotor grego fica antes dos três rotores principais.
        self.rotor_grego = (
            Rotor.criar_rotor(
                rotores[0], posicoes_rotores[0], configuracoes_anel[0]
            )
            if len(rotores) == 4
            else None
        )
        indice = 1 if self.rotor_grego is not None else 0

        # Os rotores principais são organizados da esquerda para a direita.
        self.rotor_esquerdo = Rotor.criar_rotor(
            rotores[indice],
            posicoes_rotores[indice],
            configuracoes_anel[indice],
        )
        self.rotor_central = Rotor.criar_rotor(
            rotores[indice + 1],
            posicoes_rotores[indice + 1],
            configuracoes_anel[indice + 1],
        )
        self.rotor_direito = Rotor.criar_rotor(
            rotores[indice + 2],
            posicoes_rotores[indice + 2],
            configuracoes_anel[indice + 2],
        )

        self.refletor = Refletor.criar_refletor(nome_refletor)
        self.plugboard = Plugboard(conexoes_plugboard)

    def girar_rotores(self):
        """Avança os rotores conforme a posição dos entalhes."""
        central_no_entalhe = self.rotor_central.esta_na_posicao_do_entalhe()
        direito_no_entalhe = self.rotor_direito.esta_na_posicao_do_entalhe()

        if central_no_entalhe:
            # Duplo avanço: o rotor central e o esquerdo avançam juntos.
            self.rotor_esquerdo.rotacionar()
            self.rotor_central.rotacionar()
        elif direito_no_entalhe:
            self.rotor_central.rotacionar()

        # O rotor direito avança a cada letra processada.
        self.rotor_direito.rotacionar()

    def cifrar(self, numero):
        """Cifra um índice numérico de 0 a 25."""
        self.girar_rotores()

        # Ida pelo plugboard e pelos rotores principais.
        saida = self.plugboard.cifrar(numero)
        saida = self.rotor_direito.cifrar_direto(saida)
        saida = self.rotor_central.cifrar_direto(saida)
        saida = self.rotor_esquerdo.cifrar_direto(saida)

        # O rotor grego da M4 não participa do movimento dos rotores.
        if self.rotor_grego is not None:
            saida = self.rotor_grego.cifrar_direto(saida)

        saida = self.refletor.cifrar(saida)

        # Retorno pelos rotores em ordem inversa.
        if self.rotor_grego is not None:
            saida = self.rotor_grego.cifrar_reverso(saida)

        saida = self.rotor_esquerdo.cifrar_reverso(saida)
        saida = self.rotor_central.cifrar_reverso(saida)
        saida = self.rotor_direito.cifrar_reverso(saida)

        return self.plugboard.cifrar(saida)

    def cifrar_com_rastreamento(self, numero):
        """Cifra um índice numérico registrando cada etapa do percurso.

        Reproduz exatamente o caminho de Enigma.cifrar — inclusive o
        avanço dos rotores — apenas registrando a letra antes e depois de
        cada componente. Devolve (resultado, etapas). A posição listada
        em cada etapa é a do rotor NO MOMENTO da transformação, ou seja,
        depois do avanço desta tecla.
        """
        self.girar_rotores()
        etapas = []

        saida = self.plugboard.cifrar(numero)
        etapas.append({
            "componente": "Plugboard (entrada)",
            "antes": numero,
            "depois": saida,
        })

        for rotor, sentido in (
            (self.rotor_direito, "ida"),
            (self.rotor_central, "ida"),
            (self.rotor_esquerdo, "ida"),
        ):
            entrada = saida
            saida = rotor.cifrar_direto(saida)
            etapas.append({
                "componente": f"Rotor {rotor.nome}",
                "sentido": sentido,
                "antes": entrada,
                "depois": saida,
                "posicao": rotor.posicao_rotor,
            })

        if self.rotor_grego is not None:
            entrada = saida
            saida = self.rotor_grego.cifrar_direto(saida)
            etapas.append({
                "componente": f"Rotor grego {self.rotor_grego.nome}",
                "sentido": "ida",
                "antes": entrada,
                "depois": saida,
                "posicao": self.rotor_grego.posicao_rotor,
            })

        entrada = saida
        saida = self.refletor.cifrar(saida)
        etapas.append({
            "componente": f"Refletor {self.nome_refletor}",
            "antes": entrada,
            "depois": saida,
        })

        if self.rotor_grego is not None:
            entrada = saida
            saida = self.rotor_grego.cifrar_reverso(saida)
            etapas.append({
                "componente": f"Rotor grego {self.rotor_grego.nome}",
                "sentido": "volta",
                "antes": entrada,
                "depois": saida,
                "posicao": self.rotor_grego.posicao_rotor,
            })

        for rotor in (self.rotor_esquerdo, self.rotor_central, self.rotor_direito):
            entrada = saida
            saida = rotor.cifrar_reverso(saida)
            etapas.append({
                "componente": f"Rotor {rotor.nome}",
                "sentido": "volta",
                "antes": entrada,
                "depois": saida,
                "posicao": rotor.posicao_rotor,
            })

        entrada = saida
        saida = self.plugboard.cifrar(saida)
        etapas.append({
            "componente": "Plugboard (saída)",
            "antes": entrada,
            "depois": saida,
        })

        return saida, etapas

    def cifrar_texto(self, texto):
        """Cifra o texto, ignorando caracteres que não sejam letras A–Z."""
        resultado = []
        for caractere in texto.upper():
            if "A" <= caractere <= "Z":
                numero = ord(caractere) - ord("A")
                resultado.append(chr(self.cifrar(numero) + ord("A")))

        return "".join(resultado)