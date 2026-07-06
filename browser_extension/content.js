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

      <div class="agente-sei-context">
        <label class="agente-sei-context-field">
          <span>Processo</span>
          <input id="agente-sei-processo" autocomplete="off" placeholder="Detectar">
        </label>
        <label class="agente-sei-context-field">
          <span>Titulo</span>
          <input id="agente-sei-titulo" autocomplete="off" placeholder="Pagina SEI">
        </label>
      </div>



      <div id="agente-sei-messages" class="agente-sei-messages" role="log" aria-live="polite"></div>



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
  const processInput = root.querySelector("#agente-sei-processo");
  const titleInput = root.querySelector("#agente-sei-titulo");
  const promptInput = root.querySelector("#agente-sei-prompt");
  const messages = root.querySelector("#agente-sei-messages");

  launchButton.addEventListener("click", () => {
    root.classList.add("agente-sei-open");
    hydrateContext(false);
    if (!messages.children.length) {
      addMessage(
        "assistant",
        "Estou pronto. Posso resumir, apontar prazo, identificar assunto e sugerir providencia com base no texto visivel ou selecionado."
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

  function submitPrompt() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      addMessage("assistant", "Digite uma pergunta ou use uma acao rapida.");
      return;
    }
    promptInput.value = "";
    runAnalysis(prompt, detectIntent(prompt));
  }

  function runAnalysis(prompt, intent) {
    if (state.busy) {
      addMessage("assistant", "Estou concluindo a analise anterior.");
      return;
    }
    hydrateContext(false);
    const text = state.capturedText || getVisibleText();
    if (!text.trim()) {
      addMessage("assistant", "Abra um processo/documento no SEI ou selecione um trecho antes de perguntar.");
      return;
    }
    if (containsForbiddenIntent(prompt) || containsForbiddenIntent(text)) {
      addMessage("assistant", "Pedido bloqueado: nao executo assinatura, tramitacao, envio, conclusao ou outro ato oficial.");
      return;
    }

    addMessage("user", prompt);
    setBusy(true);
    chrome.runtime.sendMessage(
      {
        type: "AGENTE_SEI_ANALYZE",
        payload: {
          titulo: titleInput.value || document.title || "Pagina SEI",
          texto: text,
          processo_sei: processInput.value || guessProcessNumber(),
          origem: "extensao_sei_chat_readonly",
          usuario_local: "",
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
    const processo = guessProcessNumber();
    if (processo && !processInput.value.trim()) {
      processInput.value = processo;
    }
    if (!titleInput.value.trim()) {
      titleInput.value = document.title.replace(/\s+/g, " ").trim() || "Pagina SEI";
    }
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

  function setBusy(isBusy) {
    state.busy = isBusy;
    sendButton.disabled = isBusy;
    root.classList.toggle("agente-sei-busy", isBusy);
    if (isBusy) {
      addMessage("assistant", "Analisando no backend local...");
    }
  }
})();
