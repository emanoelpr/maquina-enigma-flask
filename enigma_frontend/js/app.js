(() => {
    "use strict";

    // ============================================================
    // FUNÇÕES BÁSICAS E SELETORES
    // ============================================================

    const $ = (seletor) => document.querySelector(seletor);
    const $$ = (seletor) => [...document.querySelectorAll(seletor)];

    const screens = $$(".screen");
    const nav = $$(".nav-item");

    const titles = Object.fromEntries(
        screens.map((screen) => [
            screen.id.replace("screen-", ""),
            screen.dataset.title
        ])
    );

    const visited = new Set(["dashboard"]);
    const activities = [];

    let points = 0;
    let completed = 0;
    let attempts = 0;
    let correct = 0;
    let activeChallenge = "intro";
    let toastTimer;

    // ============================================================
    // NOTIFICAÇÕES
    // ============================================================

    function toast(msg) {
        const elemento = $("#toast");

        elemento.textContent = msg;
        elemento.classList.add("show");

        clearTimeout(toastTimer);

        toastTimer = setTimeout(() => {
            elemento.classList.remove("show");
        }, 3000);
    }

    // ============================================================
    // SEGURANÇA E REGISTRO DE ATIVIDADES
    // ============================================================

    function safe(texto) {
        return texto.replace(/[&<>"']/g, (caractere) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[caractere]);
    }

    function activity(mensagem) {
        activities.unshift({
            msg: mensagem,
            time: new Date().toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit"
            })
        });

        activities.splice(8);

        renderProfile();
    }

    // ============================================================
    // NAVEGAÇÃO ENTRE TELAS
    // ============================================================

    function go(name) {
        const target = $("#screen-" + name);

        if (!target) {
            return;
        }

        screens.forEach((screen) => {
            const isTarget = screen === target;
            screen.classList.toggle("active", isTarget);
            screen.hidden = !isTarget;
        });

        nav.forEach((item) => {
            item.classList.toggle(
                "active",
                item.dataset.screen === name
            );
        });

        $("#currentSection").textContent =
            titles[name] || "Laboratório";

        visited.add(name);

        $("#sidebar").classList.remove("open");

        renderProfile();
        if (name === "profile") {
            void carregarProgresso();
        }

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

        history.replaceState(null, "", "#" + name);

        if (name !== "dashboard") {
            activity("Módulo acessado: " + titles[name]);
        }
    }

    document.addEventListener("click", (evento) => {
        const navegacao = evento.target.closest("[data-screen]");
        const destino = evento.target.closest("[data-go]");

        if (navegacao) {
            go(navegacao.dataset.screen);
        } else if (destino) {
            go(destino.dataset.go);
        }
    });

    $("#mobileMenu").addEventListener("click", () => {
        $("#sidebar").classList.toggle("open");
    });

    window.addEventListener("hashchange", () => {
        const name = location.hash.slice(1);

        if (titles[name]) {
            go(name);
        }
    });

    // ============================================================
    // TRATAMENTO DE TEXTO
    // ============================================================

    function letters(texto) {
        return texto.toUpperCase().replace(/[^A-Z]/g, "");
    }

    // ============================================================
    // CONFIGURAÇÃO E VISUALIZAÇÃO DOS ROTORES
    // ============================================================

    function updateRotors() {
        const posicoes = letters($("#positions").value)
            .slice(0, 3)
            .padEnd(3, "A");

        $("#positions").value = posicoes;

        ["Left", "Middle", "Right"].forEach((lado, indice) => {
            $("#display" + lado).textContent = posicoes[indice];

            $("#displayRotor" + lado).textContent =
                $("#rotor" + lado).value;

            const roda = $(`[data-wheel="${indice}"] b`);

            if (roda) {
                roda.textContent = posicoes[indice];
            }
        });

        const aneis = $("#rings").value
            .split(/[-, ]+/)
            .map((numero) => {
                return Math.max(
                    1,
                    Math.min(26, parseInt(numero, 10) || 1)
                );
            });

        $("#rings").value = aneis.slice(0, 3).join("-");

        aneis.slice(0, 3).forEach((numero, indice) => {
            const elemento = $(`[data-ring="${indice}"] b`);

            if (elemento) {
                elemento.textContent = String(numero).padStart(2, "0");
            }
        });

        $("#modelBadge").textContent =
            $("#modelType").value + " · DEMO";

        const modeloM4 = $("#modelType").value === "M4";

        $("#greekField").classList.toggle("hidden", !modeloM4);
        $(".greek-position-wheel").classList.toggle("hidden", !modeloM4);
        $(".greek-position-wheel b").textContent =
            letters($("#greekPosition").value).slice(0, 1) || "A";

        const refletor = $("#reflector");

        [...refletor.options].forEach((opcao) => {
            opcao.hidden =
                $("#modelType").value === "M3" &&
                opcao.value.endsWith("Thin");
        });

        if (
            $("#modelType").value === "M4" &&
            !refletor.value.endsWith("Thin")
        ) {
            refletor.value = "B-Thin";
        }

        if (
            $("#modelType").value === "M3" &&
            refletor.value.endsWith("Thin")
        ) {
            refletor.value = "B";
        }
    }

    [
        "rotorLeft",
        "rotorMiddle",
        "rotorRight",
        "positions",
        "rings",
        "reflector",
        "modelType",
        "rotorGreek"
    ].forEach((id) => {
        $("#" + id).addEventListener("change", updateRotors);
    });

    // ============================================================
    // CONTROLES DAS POSIÇÕES DOS ROTORES
    // ============================================================

    $("#positionWheels").addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-step]");

        if (!botao) {
            return;
        }

        const roda = botao.closest("[data-wheel]");
        if (!roda) return;
        const indice = Number(roda.dataset.wheel);

        const posicoes = letters($("#positions").value)
            .slice(0, 3)
            .padEnd(3, "A")
            .split("");

        const codigo = posicoes[indice].charCodeAt(0) - 65;

        posicoes[indice] = String.fromCharCode(
            65 + (
                codigo +
                Number(botao.dataset.step) +
                26
            ) % 26
        );

        $("#positions").value = posicoes.join("");

        updateRotors();
    });

    // ============================================================
    // CONTROLE DA POSIÇÃO INICIAL DO ROTOR GREGO — M4
    // ============================================================

    const greekWheel = document.querySelector("[data-greek-wheel]");

    if (greekWheel) {
        greekWheel.addEventListener("click", (evento) => {
            const botao = evento.target.closest("button[data-step]");

            if (!botao) {
                return;
            }

            const campo = $("#greekPosition");
            const atual = letters(campo.value).slice(0, 1) || "A";
            const codigo = atual.charCodeAt(0) - 65;
            const passo = Number(botao.dataset.step);
            const proximoCodigo = (codigo + passo + 26) % 26;

            campo.value = String.fromCharCode(65 + proximoCodigo);

            updateRotors();
        });
    }

    // ============================================================
    // CONTROLES DOS ANÉIS
    // ============================================================

    $("#ringWheels").addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-step]");

        if (!botao) {
            return;
        }

        const indice = Number(
            botao.closest("[data-ring]").dataset.ring
        );

        const aneis = $("#rings").value
            .split(/[-, ]+/)
            .map((numero) => parseInt(numero, 10) || 1);

        while (aneis.length < 3) {
            aneis.push(1);
        }

        aneis[indice] = (
            (aneis[indice] - 1 + Number(botao.dataset.step) + 26) % 26
        ) + 1;

        $("#rings").value = aneis.slice(0, 3).join("-");

        updateRotors();
    });

    // ============================================================
    // OPERAÇÃO REAL COM A API PYTHON
    // ============================================================

    async function operate(direcao) {
        const mensagem = letters($("#operationText").value);

        if (!mensagem) {
            toast("Digite uma mensagem com letras de A a Z.");
            return;
        }

        const modelo = $("#modelType").value;

        const rotores = [
            $("#rotorLeft").value,
            $("#rotorMiddle").value,
            $("#rotorRight").value
        ];

        const posicoes = letters($("#positions").value)
            .slice(0, 3)
            .padEnd(3, "A")
            .split("");

        const aneis = $("#rings").value
            .split(/[-, ]+/)
            .map((numero) => {
                return Math.max(
                    1,
                    Math.min(26, parseInt(numero, 10) || 1)
                );
            });

        const dados = {
            modelo: modelo,
            mensagem: mensagem,
            idioma: document.getElementById("analysisLanguage").value,
            rotores: rotores,
            posicoes: posicoes,
            aneis: aneis,
            refletor: $("#reflector").value,
            plugboard: $("#plugboard").value.trim(),
            rotor_grego: $("#rotorGreek").value
        };

        if (modelo === "M4") {
            dados.posicoes.unshift(
                letters($("#greekPosition").value).slice(0, 1) || "A"
            );
            dados.aneis.unshift(1);
        }

        const botaoCifrar = $("#machineForm button[type='submit']");
        const botaoDecifrar = $("#decryptDemo");

        botaoCifrar.disabled = true;
        botaoDecifrar.disabled = true;

        $("#outputHeading").textContent = "Processando...";
        $("#outputText").textContent =
            "Aguardando resposta do motor Python.";

        try {
            const resposta = await fetch(
                "http://127.0.0.1:5000/api/cifrar",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(dados)
                }
            );

            const resultado = await resposta.json();

            if (!resposta.ok) {
                throw new Error(
                    resultado.erro ||
                    "Falha ao processar a mensagem."
                );
            }

            $("#outputHeading").textContent =
                direcao === "encrypt"
                    ? "Mensagem cifrada"
                    : "Mensagem processada";

            $("#outputText").textContent = resultado.resultado;

            $("#outputCount").textContent =
                resultado.quantidade_caracteres + " CARACTERES";

            $("#modelBadge").textContent = modelo + " · PYTHON";

            $(".machine-side .panel .tag").textContent = "MOTOR REAL";

            activity(
                direcao === "encrypt"
                    ? "Mensagem cifrada pelo motor Python"
                    : "Mensagem processada pelo motor Python"
            );

            toast("Operação concluída pelo motor Enigma Python.");

        } catch (erro) {
            console.error(
                "Erro na integração com a API:",
                erro
            );

            $("#outputHeading").textContent =
                "Não foi possível processar";

            $("#outputText").textContent = erro.message;
            $("#outputCount").textContent = "ERRO";

            toast(
                "Não foi possível conectar ao Python. " +
                "Confira se a API está executando."
            );

        } finally {
            botaoCifrar.disabled = false;
            botaoDecifrar.disabled = false;
        }
    }

    // ============================================================
    // EVENTOS DOS BOTÕES DE CIFRAGEM E DESCRIPTografia
    // Estes eventos ficam dentro da função principal para que
    // consigam acessar operate().
    // ============================================================

    $("#machineForm").addEventListener("submit", async (evento) => {
        evento.preventDefault();
        await operate("encrypt");
    });

    $("#decryptDemo").addEventListener("click", async (evento) => {
        evento.preventDefault();
        await operate("decrypt");
    });

    // ============================================================
    // COPIAR RESULTADO DA CIFRAGEM
    // ============================================================

    $("#copyOutput").addEventListener("click", async () => {
        const texto = $("#outputText").textContent.trim();

        if (!texto || texto === "A saída aparecerá aqui." ||
            texto === "Aguardando mensagem.") {
            toast("Não há resultado para copiar.");
            return;
        }

        try {
            await navigator.clipboard.writeText(texto);
            toast("Resultado copiado para a área de transferência.");
        } catch (erro) {
            console.error("Erro ao copiar resultado:", erro);
            toast("Não foi possível copiar. Verifique as permissões do navegador.");
        }
    });


    // ============================================================
    // PERCURSO REAL DA LETRA — MOTOR PYTHON
    // Cada etapa vem de /api/percurso, calculada pelo mesmo Enigma
    // que cifra as mensagens. Nada é pré-desenhado em JavaScript.
    // ============================================================

    const ROTORES_PERCURSO = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"];

    ["traceRotorLeft", "traceRotorMiddle", "traceRotorRight"].forEach((id) => {
        const select = $("#" + id);

        ROTORES_PERCURSO.forEach((nome) => {
            const opcao = document.createElement("option");

            opcao.value = nome;
            opcao.textContent = nome;

            select.append(opcao);
        });
    });

    $("#traceRotorLeft").value = "I";
    $("#traceRotorMiddle").value = "II";
    $("#traceRotorRight").value = "III";

    let posicoesIniciaisPercurso = "AAA";

    function guardarPosicoesIniciais() {
        posicoesIniciaisPercurso = $("#tracePositions").value;
    }

    function ajustarPercursoModelo() {
        const modeloM4 = $("#traceModelType").value === "M4";

        $("#traceGreekField").classList.toggle("hidden", !modeloM4);

        [...$("#traceReflector").options].forEach((opcao) => {
            opcao.hidden = !modeloM4 && opcao.value.endsWith("Thin");
        });

        if (modeloM4 && !$("#traceReflector").value.endsWith("Thin")) {
            $("#traceReflector").value = "B-Thin";
        }

        if (!modeloM4 && $("#traceReflector").value.endsWith("Thin")) {
            $("#traceReflector").value = "B";
        }

        $("#traceModelBadge").textContent =
            modeloM4 ? "M4 · REAL" : "M3 · REAL";

        guardarPosicoesIniciais();
    }

    function lerConfigPercurso() {
        const modelo = $("#traceModelType").value;
        const maximo = modelo === "M4" ? 4 : 3;

        const posicoes = letters($("#tracePositions").value)
            .slice(0, maximo)
            .padEnd(maximo, "A")
            .split("");

        $("#tracePositions").value = posicoes.join("");

        const aneis = $("#traceRings").value
            .split(/[-, ]+/)
            .map((numero) => Math.max(1, Math.min(26, parseInt(numero, 10) || 1)));

        while (aneis.length < maximo) {
            aneis.push(1);
        }

        const config = {
            modelo: modelo,
            rotores: [
                $("#traceRotorLeft").value,
                $("#traceRotorMiddle").value,
                $("#traceRotorRight").value
            ],
            posicoes: posicoes,
            aneis: aneis.slice(0, maximo),
            refletor: $("#traceReflector").value,
            plugboard: $("#tracePlugboard").value.trim().toUpperCase()
        };

        if (modelo === "M4") {
            config.rotor_grego = $("#traceRotorGreek").value;
        }

        return config;
    }

    function atualizarDisplaysPercurso(dados, config) {
        const finais = dados.posicoes_finais;
        let indice = 0;

        if (config.modelo === "M4") {
            $("#traceDisplayGreek").textContent = finais[indice++];
            $("#traceDisplayRotorGreek").textContent = config.rotor_grego;
        } else {
            $("#traceDisplayGreek").textContent = "—";
            $("#traceDisplayRotorGreek").textContent = "—";
        }

        $("#traceDisplayLeft").textContent = finais[indice++];
        $("#traceDisplayRotorLeft").textContent = config.rotores[0];
        $("#traceDisplayMiddle").textContent = finais[indice++];
        $("#traceDisplayRotorMiddle").textContent = config.rotores[1];
        $("#traceDisplayRight").textContent = finais[indice];
        $("#traceDisplayRotorRight").textContent = config.rotores[2];
    }

    function renderEtapas(dados) {
        const painel = $("#traceSteps");

        painel.innerHTML = "";

        const resumo = document.createElement("div");
        resumo.className = "trace-summary";
        resumo.innerHTML = `
            <small>ENTRADA</small><b class="trace-let saida"></b>
            <span>→</span>
            <b class="trace-let saida destaque"></b><small>SAÍDA</small>
        `;
        const letras = resumo.querySelectorAll(".trace-let");
        letras[0].textContent = dados.letra_entrada;
        letras[1].textContent = dados.letra_saida;
        painel.append(resumo);

        dados.etapas.forEach((etapa) => {
            const linha = document.createElement("div");
            linha.className = "trace-step-row";

            linha.innerHTML = `
                <b class="trace-let a"></b>
                <div><strong></strong><small></small></div>
                <b class="trace-let b"></b>
            `;

            linha.querySelector("strong").textContent = etapa.componente;
            linha.querySelector("small").textContent = etapa.sentido
                ? `Sentido: ${etapa.sentido} · posição usada na transformação: ${etapa.posicao}`
                : "Painel de conexões";
            linha.querySelector(".a").textContent = etapa.antes;
            linha.querySelector(".b").textContent = etapa.depois;

            painel.append(linha);
        });

        return painel;
    }

    async function animarEtapas(painel) {
        const linhas = [...painel.querySelectorAll(".trace-step-row")];

        linhas.forEach((linha) => linha.classList.remove("is-done"));

        for (const linha of linhas) {
            await new Promise((resolver) => setTimeout(resolver, 600));
            linha.classList.add("is-done");
        }
    }

    async function enviarLetraPercurso(evento) {
        evento.preventDefault();

        const letra = letters($("#traceLetterInput").value).slice(0, 1);

        if (!letra) {
            toast("Digite uma letra de A a Z.");
            return;
        }

        $("#traceLetterInput").value = letra;

        const config = lerConfigPercurso();
        const corpo = { ...config, letra: letra };
        const botao = $("#runTrace");

        botao.disabled = true;
        $("#traceStatusTag").textContent = "PROCESSANDO";

        try {
            const resposta = await apiFetch(`${API_BASE}/api/percurso`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(corpo)
            });

            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(
                    dados.erro || "A API recusou a solicitação."
                );
            }

            const painel = renderEtapas(dados);

            $("#traceHeading").textContent =
                `Percurso da letra ${dados.letra_entrada}`;
            $("#traceStatusTag").textContent = "MOTOR REAL";

            atualizarDisplaysPercurso(dados, config);

            // As posições evoluem: a próxima letra parte daqui.
            $("#tracePositions").value = dados.posicoes_finais.join("");

            await animarEtapas(painel);

            activity(
                "Percurso real da letra " + dados.letra_entrada +
                " → " + dados.letra_saida
            );

        } catch (erro) {
            console.error("Erro no percurso da letra:", erro);
            $("#traceStatusTag").textContent = "ERRO";
            $("#traceHeading").textContent = "Não foi possível calcular";
            toast(erro.message + " Verifique se a API está executando.");
        } finally {
            botao.disabled = false;
        }
    }

    function reiniciarPercurso() {
        $("#tracePositions").value = posicoesIniciaisPercurso;
        $("#traceSteps").innerHTML = "";
        $("#traceHeading").textContent = "Envie uma letra";
        $("#traceStatusTag").textContent = "AGUARDANDO";
        toast("Posições reiniciadas para o início da sequência.");
    }

    $("#traceForm").addEventListener("submit", enviarLetraPercurso);
    $("#traceReset").addEventListener("click", reiniciarPercurso);
    $("#traceModelType").addEventListener("change", ajustarPercursoModelo);

    ["traceRotorLeft", "traceRotorMiddle", "traceRotorRight", "traceRotorGreek", "traceReflector", "traceRings", "tracePlugboard"]
        .forEach((id) => {
            $("#" + id).addEventListener("change", () => {
                guardarPosicoesIniciais();
                $("#traceSteps").innerHTML = "";
                $("#traceHeading").textContent = "Envie uma letra";
                $("#traceStatusTag").textContent = "AGUARDANDO";
            });
        });

    $("#tracePositions").addEventListener("input", guardarPosicoesIniciais);

    ajustarPercursoModelo();

    // ============================================================
    // CRIPTOANÁLISE REAL PELA API PYTHON
    // Três modos: configurada (todas as posições para uma configuração
    // informada), ampliada (enumeração exaustiva do que o usuário declarou
    // desconhecido) e avançada (heurística para anéis e plugboard).
    // ============================================================

    const API_BASE = "http://127.0.0.1:5000";

    const AJUDA_MODOS = {
        configurada: "Busca configurada: você informa rotores, anéis, refletor e plugboard; o sistema testa TODAS as posições iniciais (17.576 na M3; 456.976 na M4, com a posição grega). Exaustiva.",
        ampliada: "Busca ampliada: investiga automaticamente ordem dos rotores (336 permutações de I–VIII), refletores compatíveis, rotor grego e TODAS as posições — mantendo fixo só o que você marcar como conhecido. Exaustiva no escopo declarado; espaços acima do limite são recusados.",
        avancada: "Criptoanálise avançada: anéis e plugboard desconhecidos por busca HEURÍSTICA (triagem exaustiva + refinamento dos melhores candidatos + subida de encosta no plugboard). Não enumera todas as chaves e pode não achar a correta; precisa de textos longos (100+ letras) com plugboard desconhecido."
    };
    const ROTORES_UI = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"];

    function formatarNumero(valor) {
        return Number(valor || 0).toLocaleString("pt-BR");
    }

    function preencherSeletoresAnalise() {
        ["#anRotor1", "#anRotor2", "#anRotor3"].forEach((seletor, indice) => {
            $(seletor).innerHTML = ROTORES_UI.map((r) => `<option>${r}</option>`).join("");
            $(seletor).value = ROTORES_UI[indice];
        });
        atualizarRefletoresAnalise();
    }

    function atualizarRefletoresAnalise() {
        const m4 = $("#analysisModel").value === "M4";
        const opcoes = m4 ? ["Bfino", "Cfino"] : ["B", "C"];
        $("#anReflector").innerHTML = opcoes.map((r) => `<option value="${r}">${r === "Bfino" ? "B fino" : r === "Cfino" ? "C fino" : r}</option>`).join("");
        $$(".m4-only").forEach((linha) => linha.classList.toggle("hidden", !m4));
    }

    function atualizarControlesAnalise() {
        const modo = $("#analysisMode").value;
        $("#analysisModeHelp").textContent = AJUDA_MODOS[modo];
        const configurada = modo === "configurada";
        // Na busca configurada todos os parâmetros são obrigatórios.
        ["#knowRotors", "#knowReflector", "#knowGreek", "#knowRings"].forEach((s) => {
            if (configurada) { $(s).checked = true; }
            $(s).disabled = configurada;
        });
        const plugDesconhecido = $("#anPlugMode").querySelector('option[value="desconhecido"]');
        plugDesconhecido.disabled = modo !== "avancada";
        if (modo !== "avancada" && $("#anPlugMode").value === "desconhecido") {
            $("#anPlugMode").value = "vazio";
        }
        [["#knowRotors", ["#anRotor1", "#anRotor2", "#anRotor3"]], ["#knowReflector", ["#anReflector"]],
         ["#knowGreek", ["#anGreek"]], ["#knowRings", ["#anRings"]]].forEach(([caixa, campos]) => {
            campos.forEach((c) => { $(c).disabled = !$(caixa).checked; });
        });
        $("#anPlug").classList.toggle("hidden", $("#anPlugMode").value !== "conhecido");
        atualizarEscopo();
    }

    function montarCorpoAnalise() {
        const modelo = $("#analysisModel").value;
        const corpo = {
            modo: $("#analysisMode").value,
            modelo,
            mensagem: letters($("#cipherInput").value),
            idioma: $("#analysisLanguage").value,
            limite: 5,
            plugboard_modo: $("#anPlugMode").value
        };
        if ($("#knowRotors").checked) {
            corpo.rotores = [$("#anRotor1").value, $("#anRotor2").value, $("#anRotor3").value];
        }
        if ($("#knowReflector").checked) { corpo.refletor = $("#anReflector").value; }
        if (modelo === "M4" && $("#knowGreek").checked) { corpo.rotor_grego = $("#anGreek").value; }
        if ($("#knowRings").checked) {
            corpo.aneis = $("#anRings").value.split(/[^0-9]+/).filter(Boolean).map(Number);
        }
        if (corpo.plugboard_modo === "conhecido") { corpo.plugboard = $("#anPlug").value; }
        return corpo;
    }

    let temporizadorEscopo = null;
    function atualizarEscopo() {
        clearTimeout(temporizadorEscopo);
        temporizadorEscopo = setTimeout(async () => {
            const caixa = $("#analysisScope");
            try {
                const corpo = montarCorpoAnalise();
                corpo.mensagem = corpo.mensagem || "AAAA";
                const resposta = await fetch(`${API_BASE}/api/criptoanalise/escopo`, {
                    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo)
                });
                const dados = await resposta.json();
                if (!resposta.ok) {
                    caixa.innerHTML = `<b>ESCOPO</b><p class="scope-erro"></p>`;
                    caixa.querySelector("p").textContent = dados.erro;
                    $("#startAnalysis").disabled = true;
                    return;
                }
                $("#startAnalysis").disabled = false;
                const linhas = dados.dimensoes.map((d) => {
                    const tamanho = d.tamanho === null ? "—" : formatarNumero(d.tamanho);
                    return `<li><span>${safe(d.nome)}</span><em class="tipo-${d.tipo === "heurística" ? "heur" : d.tipo}">${tamanho} · ${d.tipo}</em></li>`;
                }).join("");
                caixa.innerHTML = `<b>ESCOPO DA BUSCA</b><ul>${linhas}</ul>
                    <p>${dados.heuristica
                        ? `Triagem exaustiva de ${formatarNumero(dados.configuracoes_exaustivas)} configurações, seguida de refinamento HEURÍSTICO.`
                        : `${formatarNumero(dados.configuracoes_exaustivas)} configurações avaliadas exaustivamente.`}</p>`;
            } catch (erro) {
                caixa.innerHTML = `<b>ESCOPO</b><p>Não foi possível calcular o escopo — verifique a API.</p>`;
            }
        }, 250);
    }

    function textoConfiguracao(candidato) {
        const partes = [`${candidato.modelo || "—"}`];
        if (candidato.rotor_grego) {
            partes.push(`Grego ${candidato.rotor_grego} @ ${candidato.posicao_grega || "—"}`);
        }
        partes.push(`Rotores ${(candidato.rotores || []).join("–")}`);
        partes.push(`Posições ${candidato.posicoes || "—"}`);
        partes.push(`Anéis ${(candidato.aneis || []).join("–")}`);
        partes.push(`Refletor ${candidato.refletor || "—"}`);
        partes.push(`Plugboard ${candidato.plugboard ? candidato.plugboard + (candidato.plugboard_recuperado ? " (recuperado)" : "") : "vazio"}`);
        return partes.join(" · ");
    }

    function renderCandidatos(painel, candidatos, resultado) {
        candidatos.forEach((candidato, indice) => {
            const item = document.createElement("div");
            item.className = "candidate";
            const pontuacao = Number(candidato.pontuacao || 0);
            item.innerHTML = `
                <b>${String(indice + 1).padStart(2, "0")}</b>
                <div class="candidate-content">
                    <strong class="candidate-text"></strong>
                    <small class="candidate-config"></small>
                    <small class="candidate-method"></small>
                </div>
                <em>índice ${pontuacao.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</em>
            `;
            item.querySelector(".candidate-text").textContent = candidato.texto || "(sem texto)";
            item.querySelector(".candidate-config").textContent = textoConfiguracao(candidato);
            const metodo = candidato.metodo === "heuristica" ? "Heurística" : "Exaustiva";
            item.querySelector(".candidate-method").textContent =
                `Método: ${metodo}${candidato.verificado_no_motor ? " · verificado no motor real" : ""} · Idioma ${candidato.idioma || resultado.idioma || "—"}`;
            item.title = candidato.escopo || "";
            painel.append(item);
        });
    }

    function renderAnalysisResults(resultado) {
        const candidatos = Array.isArray(resultado.candidatos) ? resultado.candidatos : [];
        const painel = $("#analysisResult");
        painel.innerHTML = "";

        const metricas = document.createElement("div");
        metricas.className = "metric-grid";
        metricas.innerHTML = `
            <div><small>CANDIDATOS</small><b>${candidatos.length}</b></div>
            <div><small>TEMPO</small><b>${Number(resultado.tempo_segundos || 0).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} s</b></div>
            <div><small>CONFIGURAÇÕES AVALIADAS</small><b>${formatarNumero(resultado.combinacoes_testadas)}</b></div>
        `;
        painel.append(metricas);

        const metodo = document.createElement("p");
        metodo.className = "muted tiny";
        const nomeModo = { configurada: "Busca configurada", ampliada: "Busca ampliada", avancada: "Criptoanálise avançada" }[resultado.modo] || "Busca configurada";
        metodo.textContent = `${nomeModo} · método ${resultado.metodo === "heuristica" ? "HEURÍSTICO (não exaustivo)" : "exaustivo no escopo declarado"}` +
            (resultado.cobertura_completa ? " · escopo coberto integralmente." : ".");
        painel.append(metodo);

        if (!candidatos.length) {
            const vazio = document.createElement("p");
            vazio.className = "muted";
            vazio.textContent = "A busca terminou, mas não retornou candidatos.";
            painel.append(vazio);
            return;
        }
        renderCandidatos(painel, candidatos, resultado);

        const nota = document.createElement("p");
        nota.className = "muted tiny";
        nota.textContent = resultado.aviso ||
            "A pontuação é uma estimativa linguística. O melhor candidato estatístico não é necessariamente a mensagem correta, principalmente em textos curtos.";
        painel.append(nota);
    }

    const analysisModel = $("#analysisModel");
    let tarefaCriptoEmAndamento = null;

    preencherSeletoresAnalise();
    atualizarControlesAnalise();
    ["#analysisMode", "#knowRotors", "#knowReflector", "#knowGreek", "#knowRings", "#anPlugMode",
     "#anRotor1", "#anRotor2", "#anRotor3", "#anReflector", "#anGreek"].forEach((s) => {
        $(s).addEventListener("change", atualizarControlesAnalise);
    });
    analysisModel.addEventListener("change", () => { atualizarRefletoresAnalise(); atualizarControlesAnalise(); });
    $("#anRings").addEventListener("input", atualizarEscopo);
    $("#anPlug").addEventListener("input", atualizarEscopo);

    function finalizarAnimacaoAnalise() {
        $("#lupaAnalise").classList.remove("lupa-analisando");
        $("#cancelAnalysis").classList.add("hidden");
        tarefaCriptoEmAndamento = null;
    }

    function descreverProgresso(estado) {
        const tempo = `${Number(estado.tempo_decorrido || 0).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} s`;
        if (estado.porcentagem === undefined) {
            return `EXECUTANDO · ${formatarNumero(estado.combinacoes_testadas)} configurações · ${tempo}`;
        }
        const etapa = `ETAPA ${estado.fase_numero}/${estado.total_fases} · ${String(estado.fase || "").toUpperCase()}`;
        if (estado.tipo_progresso === "real" && estado.porcentagem !== null) {
            return `${etapa} · ${Number(estado.porcentagem).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% · ` +
                `${formatarNumero(estado.combinacoes_testadas)} / ${formatarNumero(estado.total_combinacoes)} configurações · ${tempo}`;
        }
        const daEtapa = estado.fase_total
            ? ` · ${formatarNumero(estado.fase_feitas)} / ${formatarNumero(estado.fase_total)} nesta etapa`
            : "";
        return `${etapa}${daEtapa} · ${formatarNumero(estado.combinacoes_testadas)} avaliações (progresso por etapa) · ${tempo}`;
    }

    $("#startAnalysis").addEventListener("click", async () => {
        const corpo = montarCorpoAnalise();

        if (corpo.mensagem.length < 4) {
            toast("Insira pelo menos quatro letras no texto cifrado.");
            return;
        }

        const modelo = corpo.modelo;
        const botao = $("#startAnalysis");

        $("#analysisEmpty").classList.add("hidden");
        $("#analysisResult").classList.add("hidden");
        $("#analysisStatus").textContent = "BUSCA EM EXECUÇÃO";
        botao.disabled = true;
        $("#cancelAnalysis").classList.remove("hidden");
        $("#lupaAnalise").classList.add("lupa-analisando");

        const carregando = document.createElement("div");
        carregando.id = "analysisLoading";
        carregando.className = "empty";
        carregando.setAttribute("role", "status");
        carregando.innerHTML = `<b>⌕</b><strong>Investigando a Enigma ${modelo}</strong><p class="progresso-detalhe">O progresso exibido reflete o trabalho realmente executado pelo backend Python.</p><div class="parciais"></div>`;
        $("#analysisResult").before(carregando);

        try {
            const resposta = await fetch(`${API_BASE}/api/criptoanalise/tarefas`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(corpo)
            });
            const criacao = await resposta.json();
            if (!resposta.ok) {
                throw new Error(criacao.erro || "A API recusou a solicitação.");
            }
            tarefaCriptoEmAndamento = criacao.id_tarefa;

            while (true) {
                await new Promise((resolver) => setTimeout(resolver, 500));

                const consulta = await fetch(`${API_BASE}/api/criptoanalise/tarefas/${tarefaCriptoEmAndamento}`);
                const estado = await consulta.json();
                if (!consulta.ok) {
                    throw new Error(estado.erro || "Falha ao consultar a tarefa.");
                }

                if (estado.estado === "executando") {
                    $("#analysisStatus").textContent = descreverProgresso(estado);
                    const caixaParciais = carregando.querySelector(".parciais");
                    if (Array.isArray(estado.parciais) && estado.parciais.length) {
                        caixaParciais.innerHTML = "<small>MELHORES ATÉ AGORA (verificados no motor; busca em andamento)</small>";
                        renderCandidatos(caixaParciais, estado.parciais.slice(0, 3), estado);
                    }
                    continue;
                }

                if (estado.estado === "concluida") {
                    carregando.remove();
                    renderAnalysisResults(estado.resultado);
                    $("#analysisResult").classList.remove("hidden");
                    $("#analysisStatus").textContent = "BUSCA CONCLUÍDA · " + modelo;
                    activity(`Criptoanálise ${modelo} concluída: ${formatarNumero(estado.resultado.combinacoes_testadas)} configurações`);
                    toast(`Criptoanálise ${modelo} concluída pelo motor Python.`);
                    break;
                }

                if (estado.estado === "cancelada") {
                    carregando.remove();
                    $("#analysisStatus").textContent = "BUSCA CANCELADA";
                    $("#analysisEmpty").classList.remove("hidden");
                    $("#analysisEmpty").querySelector("strong").textContent = "Análise cancelada.";
                    $("#analysisEmpty").querySelector("p").textContent =
                        `A busca foi interrompida no backend após ${formatarNumero(estado.combinacoes_testadas)} configurações avaliadas; as demais NÃO foram examinadas.`;
                    toast("Criptoanálise cancelada.");
                    break;
                }

                throw new Error(estado.erro || "A busca terminou com erro.");
            }
        } catch (erro) {
            console.error("Erro na criptoanálise:", erro);
            carregando.remove();
            $("#analysisStatus").textContent = "ERRO";
            $("#analysisEmpty").classList.remove("hidden");
            $("#analysisEmpty").querySelector("strong").textContent = "Não foi possível concluir a análise.";
            $("#analysisEmpty").querySelector("p").textContent =
                erro.message + " Confira se a API Flask está executando em http://127.0.0.1:5000.";
            toast("Falha na criptoanálise. Verifique a API Python.");
        } finally {
            botao.disabled = false;
            finalizarAnimacaoAnalise();
        }
    });

    $("#cancelAnalysis").addEventListener("click", async () => {
        if (!tarefaCriptoEmAndamento) {
            return;
        }
        try {
            await fetch(`${API_BASE}/api/criptoanalise/tarefas/${tarefaCriptoEmAndamento}/cancelar`, { method: "POST" });
            toast("Cancelamento solicitado. Aguardando o backend confirmar...");
        } catch (erro) {
            console.error("Erro ao cancelar a criptoanálise:", erro);
            toast("Não foi possível enviar o cancelamento à API.");
        }
    });

    // ============================================================
    // DESAFIOS HISTÓRICOS — JORNADA DE INVESTIGAÇÃO
    // Etapa A (conheça a missão) → B (preparação e modo) →
    // C (resolução) → D (conclusão com conquista e galeria).
    // Cada etapa só fica visível quando a anterior é concluída;
    // voltar nunca apaga configuração, modo escolhido ou progresso.
    // Catálogo, pontuação por modo e conquistas ficam no backend
    // (sessão assinada); a validação usa o motor Enigma real.
    // ============================================================

    let challenges = {};
    const estadoDesafios = {};
    const ETAPAS = [
        { numero: 1, rotulo: "Conheça a missão" },
        { numero: 2, rotulo: "Prepare-se" },
        { numero: 3, rotulo: "Resolução" },
        { numero: 4, rotulo: "Conclusão" },
    ];
    const MODOS_INFO = {
        guiado: {
            rotulo: "Guiado · iniciante",
            descricao: "A máquina recebe a configuração completa da missão. Você aprende a operar a Enigma e a ler a saída.",
        },
        investigacao: {
            rotulo: "Investigação · intermediário",
            descricao: "Pistas passo a passo ensinam rotores, anéis e plugboard; você configura sozinho com apoio.",
        },
        especialista: {
            rotulo: "Especialista · avançado",
            descricao: "Configuração manual e uma única orientação. A criptoanálise é opcional. Vale a pontuação máxima.",
        },
    };
    let conquistasDesbloqueadas = [];

    function rotuloDificuldade(chave) {
        return { facil: "Fácil", media: "Média", dificil: "Difícil" }[chave] || chave;
    }

    function rotuloModo(chave) {
        return MODOS_INFO[chave] ? MODOS_INFO[chave].rotulo : chave;
    }

    function indicarEtapa(numero) {
        const info = ETAPAS[numero - 1];
        const painel = $("#challengeSteps");
        if (painel && info) {
            painel.textContent = `ETAPA ${info.numero} DE 4 · ${info.rotulo.toUpperCase()}`;
        }
    }

    function mostrarEtapa(numero) {
        "ABCD".split("").forEach((letra, indice) => {
            const secao = $(`#challengeStage${letra}`);
            if (secao) {
                secao.classList.toggle("hidden", indice + 1 !== numero);
            }
        });
        indicarEtapa(numero);
    }

    async function carregarProgresso() {
        try {
            const resposta = await apiFetch(`${API_BASE}/api/desafios/progresso`);
            const dados = await resposta.json();

            if (!resposta.ok) {
                return;
            }

            Object.keys(dados.concluidas || {}).forEach((id) => {
                estadoDesafios[id] = Object.assign(estadoDesafios[id] || {}, {
                    concluida: true,
                    modo: dados.concluidas[id].modo,
                    pontos: dados.concluidas[id].pontos,
                    dicasLiberadas: estadoDesafios[id] ? estadoDesafios[id].dicasLiberadas : 0,
                    dicas: estadoDesafios[id] ? estadoDesafios[id].dicas : [],
                });
            });

            points = Number(dados.pontos_total || 0);
            completed = Object.keys(dados.concluidas || {}).length;
            conquistasDesbloqueadas = dados.conquistas || [];

            renderConquistas();
            renderProfile();
        } catch (erro) {
            // Sem API no ar: a seção informa e segue funcionando.
        }
    }

    function renderCatalogoDesafios() {
        const grade = $("#challengeGrid");

        grade.innerHTML = "";

        Object.keys(challenges).forEach((id) => {
            const missao = challenges[id];
            const estado = estadoDesafios[id] || {};

            const estadoTexto = estado.concluida
                ? "CONCLUÍDA · " + rotuloModo(estado.modo).toUpperCase()
                : (estado.dicasLiberadas
                    ? `EM ANDAMENTO · ${estado.dicasLiberadas}/${missao.total_dicas} PISTAS`
                    : "PENDENTE");

            const cartao = document.createElement("article");
            cartao.className = "challenge-card";

            cartao.innerHTML = `
                <small>${missao.modelo} · ${rotuloDificuldade(missao.dificuldade)} · até +${missao.pontos} PTS</small>
                <h3>${safe(missao.titulo)}</h3>
                <p>${safe(missao.local || "")}</p>
                <span class="challenge-state ${estado.concluida ? "done" : ""}">${estadoTexto}</span>
                <button class="link" data-challenge="${id}">Abrir missão ↗</button>
            `;

            grade.append(cartao);
        });
    }

    function renderEtapaA(id_missao, detalhe) {
        // Uma única linha compacta de metadados — modelo, natureza,
        // dificuldade e pontuação aparecem uma única vez, aqui.
        const meta = [
            detalhe.modelo,
            detalhe.natureza === "reconstrucao" ? "Reconstrução educacional" : "Documento histórico",
            rotuloDificuldade(detalhe.dificuldade),
            `até +${detalhe.pontos} pontos`,
        ].join(" · ");

        $("#challengeStageA").innerHTML = `
            <p class="challenge-meta-linha">${meta}</p>
            <div class="cenario-card">
                <div class="cenario-titulo">CENÁRIO HISTÓRICO</div>
                <dl class="cenario-dados">
                    <div><dt>Onde</dt><dd>${safe(detalhe.local)}</dd></div>
                    <div><dt>Região</dt><dd>${safe(detalhe.pais_regiao)}</dd></div>
                    <div><dt>Quando</dt><dd>${safe(detalhe.periodo)}</dd></div>
                </dl>
                <p class="cenario-resumo">${safe(detalhe.intro)}</p>
            </div>
            <details class="challenge-details">
                <summary>Conheça o contexto histórico</summary>
                <p>${safe(detalhe.contexto)}</p>
                <p><b>Quem participava:</b> ${safe(detalhe.quem_participava)}</p>
                <p><small>${safe(detalhe.fato_verificado)}</small></p>
                <ul class="source-list">
                    ${detalhe.fontes.map((fonte) => `<li><a href="${fonte.url}" target="_blank" rel="noopener">${safe(fonte.titulo)}</a></li>`).join("")}
                </ul>
            </details>
            <div class="actions"><button class="btn primary" id="goStageB">Preparar a missão →</button></div>
        `;

        $("#goStageB").addEventListener("click", () => mostrarEtapa(2));
    }

    function renderEtapaB(id_missao, detalhe) {
        const estado = estadoDesafios[id_missao] || (estadoDesafios[id_missao] = { dicasLiberadas: 0, dicas: [] });

        $("#challengeStageB").innerHTML = `
            <p class="challenge-objetivo"><b>Objetivo:</b> ${safe(detalhe.objetivo)}</p>
            <ol class="edu-list">
                <li><b>O que você recebe:</b> a mensagem cifrada (abaixo) e, nas pistas, tudo o que for necessário.</li>
                <li><b>O que você faz:</b> configurar a máquina na tela "Máquina & cifra", digitar a mensagem e copiar a saída.</li>
                <li><b>O que falta descobrir:</b> depende do modo escolhido no próximo passo.</li>
                <li><b>Precisa de ajuda?</b> Use as pistas — a qualquer momento, sem penalização.</li>
            </ol>
            <div class="challenge-cipher">${safe(detalhe.mensagem_cifrada)}</div>
            <div class="field"><label>Mensagem cifrada <small>copie para a máquina</small></label><input readonly value="${safe(detalhe.mensagem_cifrada)}" id="challengeCopySource"></div>
            <div class="modo-cards">
                ${Object.keys(MODOS_INFO).map((chave) => `
                    <button type="button" class="modo-card${estado.modoSelecionado === chave ? " selecionado" : ""}" data-modo="${chave}">
                        <b>${MODOS_INFO[chave].rotulo}</b>
                        <small>${MODOS_INFO[chave].descricao}</small>
                        <em>Pontuação: ${chave === "guiado" ? "50%" : chave === "investigacao" ? "75%" : "100%"}</em>
                    </button>
                `).join("")}
            </div>
            <div class="actions">
                <button class="btn outline" id="backStageA">← Voltar à missão</button>
                <button class="btn primary" id="iniciarResolucao" ${estado.modoSelecionado ? "" : "disabled"}>Iniciar resolução →</button>
            </div>
        `;

        $$("#challengeStageB .modo-card").forEach((cartao) => {
            cartao.addEventListener("click", () => {
                $$("#challengeStageB .modo-card").forEach((outro) => outro.classList.remove("selecionado"));
                cartao.classList.add("selecionado");
                estado.modoSelecionado = cartao.dataset.modo;
                $("#iniciarResolucao").disabled = false;
            });
        });

        $("#backStageA").addEventListener("click", () => mostrarEtapa(1));

        $("#iniciarResolucao").addEventListener("click", () => {
            if (!estado.modoSelecionado) {
                return;
            }
            renderEtapaC(id_missao, detalhe, estado.modoSelecionado);
            mostrarEtapa(3);
        });
    }

    function renderEtapaC(id_missao, detalhe, modo) {
        const painel = $("#challengeStageC");
        const limiteDicas = modo === "especialista" ? 1 : detalhe.total_dicas;

        painel.innerHTML = `
            <div class="panel-title"><div><div class="eyebrow">ETAPA C · ${rotuloModo(modo).toUpperCase()}</div><h3>Resolução</h3></div></div>
        `;

        const instrucoes = document.createElement("p");

        if (modo === "guiado") {
            instrucoes.innerHTML = `<b>Modo guiado:</b> a máquina será preparada automaticamente com a configuração desta missão. Depois, digite a mensagem cifrada e copie a saída.`;
        } else if (modo === "investigacao") {
            instrucoes.innerHTML = `<b>Modo investigação:</b> configure a máquina você mesmo. Cada pista é um relato da equipe — use o botão abaixo quantas vezes precisar.`;
        } else {
            instrucoes.innerHTML = `<b>Modo especialista:</b> configure manualmente com base no que aprendeu. Uma única orientação; a <button class="link" data-go="cryptanalysis">criptoanálise</button> é opcional.`;
        }

        painel.append(instrucoes);

        if (modo === "guiado") {
            const botaoPreparar = document.createElement("button");
            botaoPreparar.type = "button";
            botaoPreparar.className = "btn primary";
            botaoPreparar.id = "aplicarConfigGuiada";
            botaoPreparar.textContent = "Preparar máquina para esta missão ↗";
            painel.append(botaoPreparar);

            const aviso = document.createElement("p");
            aviso.className = "muted tiny";
            aviso.textContent = "A configuração vem dos dados oficiais da missão (backend) e é aplicada à tela Máquina & cifra.";
            painel.append(aviso);
        } else {
            const botaoDica = document.createElement("button");
            botaoDica.type = "button";
            botaoDica.className = "btn outline";
            botaoDica.id = "challengeHintC";
            botaoDica.textContent = modo === "especialista"
                ? "Pedir orientação ao analista"
                : "Revelar pista 1/" + detalhe.total_dicas;
            painel.append(botaoDica);

            const conteinerDicas = document.createElement("div");
            conteinerDicas.id = "challengeHints";
            conteinerDicas.className = "challenge-hints";
            painel.append(conteinerDicas);
        }

        const area = document.createElement("div");
        area.innerHTML = `
            <div class="field"><label for="challengeAnswer">Texto que você leu na máquina</label><input id="challengeAnswer" placeholder="Cole aqui o texto decifrado..."></div>
            <div class="actions">
                <button class="btn outline" id="backStageB">← Voltar à preparação</button>
                <button class="btn primary" id="submitChallenge">Verificar com o motor ↗</button>
            </div>
            <p id="challengeFeedback" class="feedback" aria-live="polite"></p>
        `;
        painel.append(area);

        if (modo === "guiado") {
            $("#aplicarConfigGuiada").addEventListener("click", async () => {
                $("#aplicarConfigGuiada").disabled = true;
                try {
                    const resposta = await apiFetch(`${API_BASE}/api/desafios/${id_missao}/configuracao-guiada`);
                    const config = await resposta.json();
                    if (!resposta.ok) {
                        throw new Error(config.erro || "Não foi possível preparar a máquina.");
                    }
                    aplicarConfigNaMaquina(config);
                    toast("Máquina preparada com a configuração da missão. Cole a mensagem e copie a saída.");
                } catch (erro) {
                    toast(erro.message + " Verifique a API Python.");
                } finally {
                    $("#aplicarConfigGuiada").disabled = false;
                }
            });
        } else {
            $("#challengeHintC").addEventListener("click", () => liberarDica(id_missao, limiteDicas));
        }

        $("#submitChallenge").addEventListener("click", () => verificarRespostaMissao(id_missao, modo));
        $("#backStageB").addEventListener("click", () => mostrarEtapa(2));
    }

    async function liberarDica(id_missao, limite) {
        const estado = estadoDesafios[id_missao] || (estadoDesafios[id_missao] = { dicasLiberadas: 0, dicas: [] });
        const missao = challenges[id_missao];
        const maximo = limite === undefined || limite === null ? missao.total_dicas : Math.min(limite, missao.total_dicas);

        if (estado.dicasLiberadas >= maximo) {
            return;
        }

        const botao = $("#challengeHintC");
        if (botao) {
            botao.disabled = true;
        }

        try {
            const resposta = await apiFetch(`${API_BASE}/api/desafios/${id_missao}/dica`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nivel: estado.dicasLiberadas + 1 })
            });
            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(dados.erro || "Não foi possível obter a pista.");
            }

            estado.dicas = dados.dicas;
            estado.dicasLiberadas = dados.dicas.length;

            const conteiner = $("#challengeHints");
            conteiner.innerHTML = "";
            estado.dicas.forEach((dica, indice) => {
                const linha = document.createElement("p");
                linha.className = "hint";
                const origem = document.createElement("small");
                origem.className = "hint-origem";
                origem.textContent = `PISTA ${indice + 1} DE ${maximo}`;
                const texto = document.createElement("span");
                texto.textContent = dica;
                linha.append(origem, texto);
                conteiner.append(linha);
            });

            const esgotadas = estado.dicasLiberadas >= maximo;
            if (botao) {
                botao.disabled = esgotadas;
                botao.textContent = esgotadas
                    ? (maximo < missao.total_dicas ? "Orientação única no modo especialista" : "Sem mais pistas")
                    : `Revelar pista ${estado.dicasLiberadas + 1}/${maximo}`;
            }
            renderCatalogoDesafios();
        } catch (erro) {
            toast(erro.message + " Verifique a API Python.");
            if (botao) {
                botao.disabled = false;
            }
        }
    }

    function aplicarConfigNaMaquina(config) {
        $("#modelType").value = config.modelo;
        $("#rotorLeft").value = config.rotores[0];
        $("#rotorMiddle").value = config.rotores[1];
        $("#rotorRight").value = config.rotores[2];

        const mapaRefletor = { "B": "B", "C": "C", "Bfino": "B-Thin", "Cfino": "C-Thin" };
        $("#reflector").value = mapaRefletor[config.refletor] || "B";

        $("#plugboard").value = config.plugboard || "";

        if (config.modelo === "M4") {
            $("#rotorGreek").value = config.rotor_grego || "Beta";
            $("#greekPosition").value = config.posicoes[0];
            $("#positions").value = config.posicoes.slice(1).join("");
            $("#rings").value = config.aneis.slice(1).join("-");
        } else {
            $("#positions").value = config.posicoes.join("");
            $("#rings").value = config.aneis.join("-");
        }

        updateRotors();
        go("machine");
    }

    async function verificarRespostaMissao(id_missao, modo) {
        const resposta = $("#challengeAnswer").value.trim();
        const feedback = $("#challengeFeedback");

        if (!resposta) {
            feedback.textContent = "Digite o texto que você leu na máquina.";
            return;
        }

        attempts++;

        const botao = $("#submitChallenge");
        botao.disabled = true;
        feedback.textContent = "Verificando com o motor Python...";

        try {
            const respostaApi = await apiFetch(`${API_BASE}/api/desafios/${id_missao}/verificar`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ resposta: resposta, modo: modo })
            });
            const dados = await respostaApi.json();

            if (!respostaApi.ok) {
                throw new Error(dados.erro || "A API recusou a verificação.");
            }

            if (!dados.correto) {
                attempts++;
                feedback.textContent = dados.feedback;
                return;
            }

            await renderConclusao(id_missao, dados, modo);
        } catch (erro) {
            console.error("Erro ao verificar a missão:", erro);
            feedback.textContent = erro.message + " Confira se a API está executando.";
        } finally {
            botao.disabled = false;
        }
    }

    async function renderConclusao(id_missao, dados, modo) {
        mostrarEtapa(4);
        const painel = $("#challengeStageD");

        const conquista = dados.nova_conquista;
        const config = dados.config || {};
        const partes = [];
        if (config.rotor_grego) {
            partes.push(`Rotor grego ${config.rotor_grego}`);
        }
        partes.push(`Rotores ${(config.rotores || []).join("-")}`);
        partes.push(`Posições ${(config.posicoes || []).join("")}`);
        partes.push(`Anéis ${(config.aneis || []).join("-")}`);
        partes.push(`Refletor ${config.refletor || "—"}`);
        partes.push(`Plugboard ${config.plugboard || "nenhum"}`);

        painel.innerHTML = `
            <div class="panel-title"><div><div class="eyebrow">ETAPA D</div><h3>Missão concluída ✓</h3></div><span class="tag">${rotuloModo(modo)}</span></div>
            <p><b>Mensagem decifrada:</b> ${safe(dados.mensagem_decifrada)}</p>
            <p>${dados.primeira_conclusao === false
                ? "Você já havia concluído esta missão — nenhuma pontuação adicional foi registrada."
                : `+${dados.pontos} pontos registrados no backend.`}</p>
            <div id="challengeSolution"><b>CONFIGURAÇÃO UTILIZADA</b><p>${partes.join(" · ")}</p></div>
            <p>${safe(dados.aprendizado || "")}</p>
            <div class="achievement-banner">
                <span class="achievement-icone">${conquista ? conquista.icone : "✓"}</span>
                <div>
                    <b>${conquista ? "Conquista desbloqueada: " + conquista.nome : "Conquista já registrada nesta sessão"}</b>
                    <p>${conquista ? safe(conquista.descricao) : "A conquista desta missão já constava do seu progresso."}</p>
                </div>
            </div>
            <h4>Galeria do cenário histórico</h4>
            <div id="challengeGallery" class="galeria-grid" aria-live="polite"><p class="muted">Carregando galeria...</p></div>
            <div class="actions">
                <button class="btn primary" id="nextChallengeBtn">Próxima missão →</button>
                <button class="btn outline" id="reviewChallengeBtn">Rever a missão</button>
            </div>
        `;

        await carregarGaleria(id_missao);
        await carregarProgresso();
        renderCatalogoDesafios();

        const ordem = Object.keys(challenges);
        const indiceAtual = ordem.indexOf(id_missao);
        const proxima = ordem[indiceAtual + 1];

        $("#nextChallengeBtn").addEventListener("click", () => {
            $("#challengeWorkspace").classList.add("hidden");
            if (proxima) {
                openChallenge(proxima);
            } else {
                go("profile");
            }
        });

        $("#reviewChallengeBtn").addEventListener("click", () => {
            openChallenge(id_missao);
        });

        toast("Missão concluída. Conquista e galeria liberadas.");
    }

    async function carregarGaleria(id_missao) {
        const conteiner = $("#challengeGallery");

        try {
            const resposta = await apiFetch(`${API_BASE}/api/desafios/${id_missao}/galeria`);
            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(dados.erro || "Galeria indisponível.");
            }

            const itens = dados.itens || [];
            conteiner.innerHTML = "";

            if (!itens.length) {
                conteiner.innerHTML = `<p class="muted">Não foi possível confirmar fotografias verificáveis para este cenário. Consulte o acervo indicado nas fontes da missão.</p>`;
                return;
            }

            itens.forEach((item) => {
                const figura = document.createElement("figure");
                figura.className = "galeria-item";

                const legenda = `
                    <figcaption>
                        <b>${safe(item.titulo_legenda)}</b>
                        <small>${safe(item.local)} · ${safe(item.data)} · ${item.tipo === "atual" ? "FOTO ATUAL" : "FOTO DA ÉPOCA"}</small>
                        <small>Autoria: ${safe(item.autoria)} · ${safe(item.credito_licenca)}</small>
                        <small>Relação com a missão: ${safe(item.relacao)}</small>
                    </figcaption>
                `;

                if (item.arquivo) {
                    figura.innerHTML = `
                        <a href="${item.arquivo}" target="_blank" rel="noopener" class="galeria-link">
                            <img src="${item.arquivo}" alt="${safe(item.titulo_legenda)}" loading="lazy">
                        </a>
                        ${legenda}
                        <small class="galeria-fonte">Fonte: <a href="${item.fonte_url}" target="_blank" rel="noopener">${safe(item.fonte_url)}</a></small>
                    `;

                    const imagem = figura.querySelector("img");
                    imagem.addEventListener("error", () => {
                        const alternativa = document.createElement("a");
                        alternativa.href = item.fonte_url;
                        alternativa.target = "_blank";
                        alternativa.rel = "noopener";
                        alternativa.className = "galeria-fallback";
                        alternativa.textContent = "Imagem temporariamente indisponível — abra o acervo original";
                        imagem.replaceWith(alternativa);
                    });
                } else {
                    figura.innerHTML = `
                        <a href="${item.fonte_url}" target="_blank" rel="noopener" class="galeria-fallback">
                            Não foi possível confirmar uma fotografia verificável — abra o acervo oficial indicado
                        </a>
                        ${legenda}
                    `;
                }

                conteiner.append(figura);
            });
        } catch (erro) {
            conteiner.innerHTML = `<p class="muted">${erro.message}</p>`;
        }
    }

    function openChallenge(id) {
        if (!challenges[id]) {
            return;
        }

        activeChallenge = id;

        const estado = estadoDesafios[id] || (estadoDesafios[id] = { dicasLiberadas: 0, dicas: [] });

        // Detalhe completo da Etapa A vem da API (contexto, fontes etc.).
        apiFetch(`${API_BASE}/api/desafios/${id}`)
            .then((resposta) => resposta.json())
            .then((detalhe) => {
                $("#challengeTitle").textContent = detalhe.titulo;

                renderEtapaA(id, detalhe);
                renderEtapaB(id, detalhe);

                $("#challengeStageC").innerHTML = "";
                $("#challengeStageD").innerHTML = "";

                // Estado inicial: SOMENTE a Etapa A fica visível. A Etapa B
                // só aparece depois do botão "Preparar a missão".
                mostrarEtapa(1);

                $("#challengeWorkspace").classList.remove("hidden");
                $("#challengeWorkspace").scrollIntoView({ behavior: "smooth", block: "start" });
            })
            .catch((erro) => {
                console.error("Erro ao abrir a missão:", erro);
                toast("Não foi possível carregar a missão. Verifique a API Python.");
            });

        renderCatalogoDesafios();
    }

    document.addEventListener("click", (evento) => {
        const botao = evento.target.closest("[data-challenge]");
        if (botao) {
            openChallenge(botao.dataset.challenge);
        }
    });

    $("#closeChallenge").addEventListener("click", () => {
        $("#challengeWorkspace").classList.add("hidden");
    });

    async function carregarCatalogoDesafios() {
        const aviso = $("#challengeCatalogStatus");

        try {
            const resposta = await apiFetch(`${API_BASE}/api/desafios`);
            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(dados.erro || "Falha ao carregar o catálogo.");
            }

            challenges = {};
            (dados.missoes || []).forEach((missao) => {
                challenges[missao.id] = missao;
            });

            aviso.textContent = `${(dados.missoes || []).length} MISSÕES · VALIDADAS PELO MOTOR PYTHON`;
            renderCatalogoDesafios();
            await carregarProgresso();
        } catch (erro) {
            console.error("Erro ao carregar o catálogo de desafios:", erro);
            aviso.textContent = "CATÁLOGO INDISPONÍVEL — VERIFIQUE A API";
        }
    }

    carregarCatalogoDesafios();

    // ============================================================
    // DOCUMENTAÇÃO
    // ============================================================

    const docs = {
        history: `
            <div class="eyebrow">DOCUMENTAÇÃO / 01</div>
            <h2>Contexto histórico</h2>
            <p>
                A Enigma foi uma família de máquinas eletromecânicas
                de cifragem, com diferentes modelos e configurações.
            </p>
            <h3>O princípio da cifra</h3>
            <p>
                O movimento dos rotores alterava o mapeamento aplicado
                às letras. O refletor encaminhava o sinal de volta,
                e o plugboard podia acrescentar trocas de pares.
            </p>
            <div class="notice">
                <b>REFERÊNCIAS</b>
                <p>
                    A versão final deverá incluir fontes históricas
                    verificadas.
                </p>
            </div>
        `,

        components: `
            <div class="eyebrow">DOCUMENTAÇÃO / 02</div>
            <h2>Componentes da máquina</h2>
            <h3>Rotores</h3>
            <p>
                Os rotores implementam substituições que dependem
                da posição e da configuração do anel.
            </p>
            <h3>Refletor e plugboard</h3>
            <p>
                O refletor encaminha o sinal de volta. O plugboard
                permite trocas adicionais entre pares de letras.
            </p>
        `,

        python: `
            <div class="eyebrow">DOCUMENTAÇÃO / 03</div>
            <h2>Implementação em Python</h2>
            <p>
                O projeto já possui módulos Python para os componentes
                centrais. A interface será conectada a eles por uma API,
                evitando duplicar a lógica criptográfica em JavaScript.
            </p>
            <h3>Integração planejada</h3>
            <p>
                O frontend enviará configurações e textos; o backend
                validará os dados e devolverá os resultados. A
                criptoanálise deverá reportar status e progresso.
            </p>
        `,

        architecture: `
            <div class="eyebrow">DOCUMENTAÇÃO / 04</div>
            <h2>Arquitetura prevista</h2>
            <p>
                O frontend usará HTML, CSS e JavaScript. A API Python
                ficará responsável pela cifragem, descriptografia,
                rastreamento e criptoanálise.
            </p>
            <h3>Arquivos iniciais</h3>
            <p>
                <code>frontend/index.html</code>,
                <code>frontend/css/style.css</code> e
                <code>frontend/js/app.js</code>.
            </p>
        `
    };

    $$(".docs-tab").forEach((botao) => {
        botao.addEventListener("click", () => {
            $$(".docs-tab").forEach((aba) => {
                aba.classList.toggle("active", aba === botao);
            });

            $("#docsContent").innerHTML = docs[botao.dataset.doc];
        });
    });

    // ============================================================
    // PERFIL E PROGRESSO
    // ============================================================

    function renderProfile() {
        const quantidade = visited.size;
        const progresso = Math.round((quantidade / 9) * 100);

        // O anel de progresso foi removido do dashboard (sem números
        // fictícios); o perfil continua listando os módulos visitados.
        const anelProgresso = $("#dashboardProgress");

        if (anelProgresso) {
            anelProgresso.textContent = progresso + "%";
            $("#progressBar").style.width = progresso + "%";
            $(".ring").style.background =
                `conic-gradient(var(--olive) ${progresso * 3.6}deg, #444a3c ${progresso * 3.6}deg)`;
        }

        $("#visitedCount").innerHTML =
            String(quantidade).padStart(2, "0") +
            " <span>/ 09</span>";

        $("#completedCount").textContent =
            String(completed).padStart(2, "0");

        $("#profilePoints").textContent =
            String(points).padStart(3, "0");

        $("#accuracyRate").textContent = attempts
            ? Math.round((correct / attempts) * 100) + "%"
            : "—";

        $("#achievementCount").textContent =
            String(conquistasDesbloqueadas.length).padStart(2, "0");

        const nomes = [
            ["dashboard", "Visão geral"],
            ["intro", "Conheça a Enigma"],
            ["machine", "Máquina & cifra"],
            ["trace", "Percurso da letra"],
            ["cryptanalysis", "Criptoanálise"],
            ["challenges", "Desafios históricos"],
            ["docs", "Documentação"],
            ["comparison", "Ontem & hoje"],
            ["profile", "Meu progresso"]
        ];

        $("#moduleProgressList").innerHTML = nomes
            .map(([id, nome], indice) => {
                const foiVisitado = visited.has(id);

                return `
                    <div class="module-progress-item">
                        <span>${String(indice + 1).padStart(2, "0")}</span>
                        <b>${nome}</b>
                        <span class="${foiVisitado ? "visited" : ""}">
                            ${foiVisitado ? "✓" : "—"}
                        </span>
                    </div>
                `;
            })
            .join("");

        $("#activityList").innerHTML = activities.length
            ? activities.map((item) => `
                <div class="activity-entry">
                    <time>${item.time}</time>
                    <span>${safe(item.msg)}</span>
                </div>
            `).join("")
            : '<p class="muted">Suas atividades aparecerão aqui.</p>';
    }

    async function renderConquistas() {
        const grade = $("#achievementsGrid");

        if (!grade) {
            return;
        }

        try {
            const resposta = await apiFetch(`${API_BASE}/api/desafios/conquistas`);
            const dados = await resposta.json();
            const catalogo = (dados.conquistas || []);

            $("#achievementsCount").textContent =
                `${conquistasDesbloqueadas.length} / ${catalogo.length}`;

            grade.innerHTML = "";

            catalogo.forEach((conquista) => {
                const desbloqueada = conquistasDesbloqueadas.includes(conquista.id);
                const estado = estadoDesafios[conquista.missao] || {};
                const cartao = document.createElement("div");
                cartao.className = "achievement " + (desbloqueada ? "unlocked" : "locked");

                const visualConquista = desbloqueada && conquista.imagem
                    ? `<img class="achievement-imagem" src="${safe(conquista.imagem)}" alt="" loading="lazy">`
                    : `<span class="achievement-icone">${safe(conquista.icone)}</span>`;

                cartao.innerHTML = `
                    ${visualConquista}
                    <div>
                        <b>${safe(conquista.nome)}</b>
                        <p>${safe(conquista.descricao)}</p>
                        <small>${desbloqueada
                            ? "DESBLOQUEADA" + (estado.modo ? " · " + rotuloModo(estado.modo) : "")
                            : "BLOQUEADA — conclua a missão correspondente"}</small>
                    </div>
                `;

                const imagemConquista = cartao.querySelector(".achievement-imagem");
                if (imagemConquista) {
                    imagemConquista.addEventListener("error", () => {
                        const fallback = document.createElement("span");
                        fallback.className = "achievement-icone";
                        fallback.textContent = conquista.icone || "◇";
                        imagemConquista.replaceWith(fallback);
                    }, { once: true });
                }

                grade.append(cartao);
            });
        } catch (erro) {
            grade.innerHTML = '<p class="muted">Conquistas indisponíveis sem a API.</p>';
        }
    }

    // ============================================================
    // REINICIAR PROGRESSO
    // ============================================================

    $("#resetProgress").addEventListener("click", () => {
        visited.clear();
        visited.add("dashboard");

        activities.length = 0;

        points = 0;
        completed = 0;
        attempts = 0;
        correct = 0;

        renderProfile();

        toast("Progresso local reiniciado.");
    });

// ============================================================
// RESETAR A MÁQUINA ENIGMA
// ============================================================

$("#resetMachine").addEventListener("click", () => {
    // Restaurar modelo
    $("#modelType").value = "M3";

    // Restaurar rotores
    $("#rotorLeft").value = "I";
    $("#rotorMiddle").value = "II";
    $("#rotorRight").value = "III";

    // Restaurar posições e anéis
    $("#positions").value = "AAA";
    $("#rings").value = "1-1-1";

    // Restaurar refletor e plugboard
    $("#reflector").value = "B";
    $("#plugboard").value = "";

    // Restaurar rotor grego
    $("#rotorGreek").selectedIndex = 0;
    $("#greekPosition").value = "A";

    // Limpar mensagem e resultado
    $("#operationText").value = "";
    $("#outputHeading").textContent = "Resultado";
    $("#outputText").textContent = "Aguardando mensagem.";
    $("#outputCount").textContent = "0 CARACTERES";

    // Atualizar a representação visual da máquina
    updateRotors();

    // Restaurar identificação de demonstração
    $("#modelBadge").textContent = "M3 · DEMO";
    $(".machine-side .panel .tag").textContent = "DEMONSTRAÇÃO";

    toast("Máquina restaurada à configuração inicial.");
});

    // ============================================================
    // INICIALIZAÇÃO
    // ============================================================

    updateRotors();
    renderProfile();

    const initial = location.hash.slice(1);
    const initialScreen = titles[initial] ? initial : "dashboard";

    screens.forEach((screen) => {
        screen.hidden = true;
        screen.classList.remove("active");
    });

    go(initialScreen);
})();