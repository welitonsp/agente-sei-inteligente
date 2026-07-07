(function () {
  const ROOT_ID = "agente-sei-root";
  const MAX_TEXT_CHARS = 60000;
  const FORBIDDEN_TERMS = [
    "assinar",
    "enviar processo",
    "tramitar",
    "concluir",
    "dar ciencia",
    "dar ciência",
    "excluir",
    "cancelar",
    "alterar sigilo",
    "credencial"
  ];

  if (document.getElementById(ROOT_ID)) {
    return;
  }

  // Evita injetar o robozinho em frames pequenos (como o menu lateral ou barra superior do SEI)
  if (window.innerWidth < 450 || window.innerHeight < 400) {
    return;
  }

  const state = {
    capturedText: "",
    lastAnswer: "",
    busy: false
  };

  const root = document.createElement("div");
  root.id = ROOT_ID;
  root.innerHTML = `
    <button class="agente-sei-launch" type="button" title="Abrir Agente 19">
      <span class="agente-sei-launch-mark">19</span>
      <span class="agente-sei-launch-dot"></span>
    </button>
    <section class="agente-sei-chat" aria-label="Agente 19 - chat local">
      <header class="agente-sei-chat-head">
        <div class="agente-sei-brand">
          <div class="agente-sei-avatar">19</div>
          <div>
            <div class="agente-sei-title">Agente 19</div>
            <div class="agente-sei-subtitle">Assistente local do SEI</div>
          </div>
        </div>
        <button class="agente-sei-close" type="button" aria-label="Fechar">x</button>
      </header>





      <div id="agente-sei-messages" class="agente-sei-messages" role="log" aria-live="polite"></div>

      <div class="agente-sei-quick">
        <button id="agente-sei-capturar" class="agente-sei-chip" type="button">Capturar</button>
        <button data-intent="resumo" class="agente-sei-chip" type="button">Resumo</button>
        <button data-intent="prazo" class="agente-sei-chip" type="button">Prazos</button>
        <button data-intent="providencia" class="agente-sei-chip" type="button">Providencia</button>
        <button data-intent="minuta" class="agente-sei-chip" type="button">Minuta</button>
        <button data-intent="interesse_19crpm" class="agente-sei-chip agente-sei-chip-strong" type="button">19 CRPM</button>
      </div>

      <div class="agente-sei-composer">
        <textarea id="agente-sei-prompt" rows="2" placeholder="Pergunte sobre o processo aberto no SEI..."></textarea>
        <div class="agente-sei-composer-actions">
          <button id="agente-sei-copy" class="agente-sei-secondary" type="button">Copiar</button>
          <button id="agente-sei-enviar" class="agente-sei-primary" type="button">Enviar</button>
        </div>
      </div>
    </section>
  `;
  document.documentElement.appendChild(root);

  const launchButton = root.querySelector(".agente-sei-launch");
  const closeButton = root.querySelector(".agente-sei-close");
  const sendButton = root.querySelector("#agente-sei-enviar");
  const copyButton = root.querySelector("#agente-sei-copy");
  const promptInput = root.querySelector("#agente-sei-prompt");
  const messages = root.querySelector("#agente-sei-messages");

  launchButton.addEventListener("click", () => {
    root.classList.add("agente-sei-open");
    hydrateContext(false);
    if (!messages.children.length) {
      addMessage(
        "assistant",
        "Estou pronto. Posso resumir, apontar prazo, identificar assunto, sugerir providencia e filtrar o que interessa ao 19 CRPM com base no texto visivel ou selecionado."
      );
    }
  });

  closeButton.addEventListener("click", () => {
    root.classList.remove("agente-sei-open");
  });

  sendButton.addEventListener("click", () => {
    submitPrompt();
  });

  promptInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitPrompt();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && root.classList.contains("agente-sei-open")) {
      root.classList.remove("agente-sei-open");
    }
  });

  copyButton.addEventListener("click", () => {
    if (!state.lastAnswer) {
      addMessage("assistant", "Ainda nao ha resposta para copiar.");
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(state.lastAnswer);
      addMessage("assistant", "Resposta copiada para a area de transferencia.");
    } else {
      addMessage("assistant", "Copie manualmente a ultima resposta exibida.");
    }
  });

  // Gatilho de RPA (Leitura Autonoma) apos reload da pagina
  if (sessionStorage.getItem("agente_sei_auto_read") === "true") {
    sessionStorage.removeItem("agente_sei_auto_read");
    root.classList.add("agente-sei-open");
    addMessage("assistant", "Processo aberto! Lendo autonomamente TODOS os documentos do processo...");
    setBusy(true);
    scrapeEntireProcess().then(fullText => {
      setBusy(false);
      addMessage("assistant", "Leitura concluida. Analisando o contexto geral...");
      runAnalysis("Faca um resumo geral consolidado deste processo", "resumo", fullText);
    });
  }

  root.querySelectorAll("[data-intent]").forEach((button) => {
    button.addEventListener("click", () => {
      const intent = button.getAttribute("data-intent") || "analise";
      const label = button.textContent || "Analise";
      if (intent === "minuta") {
        runAnalysis("Gere um rascunho de minuta fora do SEI, indicando se parece despacho ou oficio e deixando claro que preciso revisar antes de usar.", intent);
      } else if (intent === "interesse_19crpm") {
        runAnalysis("Analise o processo aberto e informe somente o que interessa ao 19 CRPM.", intent);
      } else {
        runAnalysis(`Preciso de ${label.toLowerCase()} do processo.`, intent);
      }
    });
  });

  function submitPrompt() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      addMessage("assistant", "Digite uma pergunta ou use uma acao rapida.");
      return;
    }
    
    // Se o usuario digitou apenas um numero de processo (ex: 202600002080361)
    const justNumbers = prompt.replace(/\D/g, "");
    if (justNumbers.length >= 10 && justNumbers.length <= 25 && justNumbers === prompt.trim()) {
      promptInput.value = "";
      addMessage("user", prompt);
      addMessage("assistant", "Detectei um numero de processo. Iniciando busca automatica e leitura autonoma no SEI...");
      const searchInput = document.getElementById("txtPesquisaRapida") || document.querySelector("input[name='pesquisa_rapida']");
      if (searchInput) {
        sessionStorage.setItem("agente_sei_auto_read", "true");
        searchInput.value = prompt;
        const searchForm = searchInput.closest("form");
        if (searchForm) {
          setTimeout(() => searchForm.submit(), 800);
          return;
        }
      }
      sessionStorage.removeItem("agente_sei_auto_read");
      addMessage("assistant", "Nao consegui localizar a barra de pesquisa nesta tela para fazer a busca automatica.", true);
      return;
    }

    promptInput.value = "";
    runAnalysis(prompt, detectIntent(prompt));
  }

  function runAnalysis(prompt, intent, customText = null) {
    if (state.busy) {
      addMessage("assistant", "Estou concluindo a analise anterior.");
      return;
    }
    hydrateContext(false);
    const text = customText || state.capturedText || getVisibleText();
    if (!text.trim()) {
      addMessage("assistant", "Abra um processo/documento no SEI ou selecione um trecho antes de perguntar.");
      return;
    }
    if (containsForbiddenIntent(prompt)) {
      addMessage("assistant", "Pedido bloqueado: nao executo assinatura, tramitacao, envio, conclusao ou outro ato oficial.");
      return;
    }

    addMessage("user", prompt);
    setBusy(true);
    const isMission = intent === "interesse_19crpm";
    chrome.runtime.sendMessage(
      {
        type: isMission ? "AGENTE_SEI_MISSION" : "AGENTE_SEI_ANALYZE",
        payload: {
          titulo: document.title || "Pagina SEI",
          mensagem: prompt,
          texto: text,
          processo_sei: guessProcessNumber(),
          unidade_destino: isMission ? "PM/19 CRPM" : "",
          origem: "extensao_sei_chat_readonly",
          usuario_local: "extensao.sei",
          perfil_local: "operador",
          intent: intent
        }
      },
      (response) => {
        setBusy(false);
        if (chrome.runtime.lastError) {
          addMessage("assistant", `Backend local indisponivel: ${chrome.runtime.lastError.message}`, true);
          return;
        }
        if (!response || !response.ok) {
          addMessage("assistant", response && response.error ? response.error : "Falha na analise local.", true);
          return;
        }
        const answer = formatResult(response.result, intent);
        state.lastAnswer = answer;
        addMessage("assistant", answer);
      }
    );
  }

  function hydrateContext(forceText) {
    if (forceText || !state.capturedText) {
      state.capturedText = getVisibleText();
    }
  }

  function getVisibleText() {
    const selection = String(window.getSelection ? window.getSelection() : "").trim();
    const source = selection || document.body.innerText || "";
    return source.replace(/\s+\n/g, "\n").trim().slice(0, MAX_TEXT_CHARS);
  }

  function guessProcessNumber() {
    const text = `${document.title} ${document.body.innerText || ""}`;
    const match = text.match(/\b\d{10,20}\b/);
    return match ? match[0] : "";
  }

  function detectIntent(prompt) {
    const lower = prompt.toLowerCase();
    if (lower.includes("prazo")) return "prazo";
    if (lower.includes("provid")) return "providencia";
    if (lower.includes("resum")) return "resumo";
    if (lower.includes("19") || lower.includes("interesse")) return "interesse_19crpm";
    if (lower.includes("minuta") || lower.includes("despacho") || lower.includes("oficio")) return "minuta";
    return "analise";
  }

  function containsForbiddenIntent(text) {
    const lower = text.toLowerCase();
    return FORBIDDEN_TERMS.some((term) => lower.includes(term));
  }

  function formatResult(payload, intent) {
    const result = payload.resultado || {};
    const event = result.evento || {};
    const deadline = result.prazo || {};
    const summary = result.resumo_executivo || "Resumo nao gerado.";
    const lines = [];

    if (intent === "interesse_19crpm") {
      return formatMissionResult(payload);
    }
    if (intent === "prazo") {
      lines.push(`Prazo: ${deadline.ha_prazo ? `${deadline.data_limite || ""} ${deadline.hora_limite || ""} ${deadline.risco || ""}` : "nao confirmado"}`);
    } else if (intent === "providencia") {
      lines.push("Providencia sugerida: revisar o conteudo, confirmar unidade responsavel e praticar qualquer ato oficial manualmente no SEI.");
    } else if (intent === "minuta") {
      lines.push("Rascunho externo de minuta:");
      lines.push(formatDraftSuggestion(payload, summary));
    } else {
      lines.push(`Resumo: ${summary}`);
    }

    lines.push(`Evento: ${event.ha_evento ? `${event.data || ""} ${event.horario_inicio || ""} ${event.local || ""}` : "nao confirmado"}`);
    lines.push(`Revisao humana: ${payload.revisao_humana_obrigatoria ? "obrigatoria" : "nao informada"}`);
    lines.push(`Pendencias: ${(payload.campos_pendentes || []).join(", ") || "nenhuma"}`);
    lines.push("Limite: nao assino, nao tramito e nao altero o SEI.");
    return lines.join("\n");
  }

  function formatMissionResult(payload) {
    if (payload.agente && payload.resposta) {
      return [
        `${payload.agente.nome} (${payload.agente.tipo})`,
        payload.resposta,
        `Ferramentas: ${(payload.ferramentas_usadas || []).map((tool) => tool.ferramenta).join(", ") || "nenhuma"}`,
        "Limite: nao abro link sozinho, nao exporto PDF automaticamente, nao assino, nao tramito e nao altero o SEI."
      ].join("\n");
    }
    const result = payload.resultado || {};
    const analysis = result.analise || {};
    const triage = result.triagem || {};
    const draft = result.minuta || {};
    const interest = triage.interesse_19crpm && triage.interesse_19crpm !== "indefinido"
      ? triage.interesse_19crpm
      : "interesse a confirmar pelo 19 CRPM";
    const lines = [
      `Processo: ${processInput.value || guessProcessNumber() || "nao identificado"}`,
      `Interesse 19 CRPM: ${interest}`,
      `Assunto/tipo: ${analysis.tipo_provavel || "nao classificado"}`,
      `Resumo: ${analysis.resumo_curto || "resumo nao gerado"}`,
      `Prazo: ${formatMissionDeadline(analysis)}`,
      `Providencia sugerida: ${analysis.providencia_sugerida || triage.providencia_sugerida || "revisar manualmente"}`,
      `Unidade sugerida: ${triage.unidade_sugerida || "PM/19 CRPM, se confirmado pelo humano"}`,
      `Minuta: ${draft.tipo_minuta || "a confirmar"} disponivel como rascunho externo.`,
      `Prontidao: ${result.prontidao_operacional ?? payload.confianca ?? "nao informada"}`,
      `Riscos: ${(result.riscos || []).join(", ") || "nenhum"}`,
      `Pendencias: ${(payload.campos_pendentes || []).join(", ") || "nenhuma"}`,
      "Limite: nao abro link sozinho, nao exporto PDF automaticamente, nao assino, nao tramito e nao altero o SEI."
    ];
    return lines.join("\n");
  }

  function formatMissionDeadline(analysis) {
    const prazos = analysis.prazos || [];
    if (prazos.length) {
      const prazo = prazos[0] || {};
      return prazo.data_limite || prazo.descricao || "prazo detectado, revisar";
    }
    return analysis.prazo_detectado ? "prazo detectado, revisar" : "nao identificado";
  }

  function formatDraftSuggestion(payload, summary) {
    const draft = payload.minuta_sugerida || payload.rascunho_minuta || {};
    const docType = draft.tipo_documento || "Despacho ou oficio, a confirmar";
    const body = draft.texto || draft.conteudo || summary;
    return [
      `Tipo provavel: ${docType}`,
      "Texto base:",
      body,
      "Uso: copiar somente apos conferencia humana; a insercao no SEI permanece manual."
    ].join("\n");
  }

  function addMessage(role, text, isError) {
    const item = document.createElement("div");
    item.className = `agente-sei-message agente-sei-${role}`;
    if (isError) {
      item.classList.add("agente-sei-message-error");
    }
    item.textContent = text;
    messages.appendChild(item);
    messages.scrollTop = messages.scrollHeight;
  }

  async function scrapeEntireProcess() {
    return new Promise((resolve) => {
      let attempts = 0;
      const checkInterval = setInterval(async () => {
        attempts++;
        const ifrArvore = document.getElementById("ifrArvore");
        if (ifrArvore && ifrArvore.contentDocument && ifrArvore.contentDocument.querySelectorAll("a").length > 2) {
          clearInterval(checkInterval);
          
          const treeDoc = ifrArvore.contentDocument;
          const links = Array.from(treeDoc.querySelectorAll("a[href*='acao=documento_visualizar'], a.ancoraArvore[href*='controlador.php?acao=']"));
          const uniqueUrls = [...new Set(links.map(l => l.href))].filter(href => !href.includes("acao=procedimento_trabalhar"));
          
          if (uniqueUrls.length === 0) {
            resolve("Processo vazio ou estrutura nao reconhecida.");
            return;
          }
          
          let fullText = "";
          for (let i = 0; i < Math.min(uniqueUrls.length, 15); i++) {
            try {
              const res = await fetch(uniqueUrls[i]);
              const html = await res.text();
              const doc = new DOMParser().parseFromString(html, "text/html");
              fullText += "\\n\\n--- DOCUMENTO " + (i+1) + " ---\\n" + doc.body.innerText;
            } catch(e) {}
          }
          resolve(fullText.trim().slice(0, MAX_TEXT_CHARS));
        } else if (attempts > 30) {
          clearInterval(checkInterval);
          resolve("Tempo esgotado ao tentar carregar a arvore do processo.");
        }
      }, 500);
    });
  }

  function setBusy(isBusy) {
    state.busy = isBusy;
    sendButton.disabled = isBusy;
    root.classList.toggle("agente-sei-busy", isBusy);
    if (isBusy) {
      addMessage("assistant", "Analisando no backend local...");
    }
  }
})();
