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

      <div class="agente-sei-safety">Login, senha, cookie e atos oficiais ficam fora do Agente 19.</div>
      <div id="agente-sei-messages" class="agente-sei-messages" role="log" aria-live="polite"></div>

      <div class="agente-sei-quick">
        <button id="agente-sei-capturar" class="agente-sei-chip" type="button">Capturar</button>
        <button data-intent="resumo" class="agente-sei-chip" type="button">Resumo</button>
        <button data-intent="prazo" class="agente-sei-chip" type="button">Prazos</button>
        <button data-intent="providencia" class="agente-sei-chip" type="button">Providencia</button>
        <button data-intent="minuta" class="agente-sei-chip" type="button">Minuta</button>
        <button data-intent="interesse_19crpm" class="agente-sei-chip agente-sei-chip-strong" type="button">19 CRPM</button>
        <label id="agente-sei-upload-pdf" class="agente-sei-chip" for="agente-sei-file-input" role="button" title="Gere o processo em PDF no SEI e carregue aqui para leitura profunda">📎 Ler PDF do Processo</label>
      </div>
      <input type="file" id="agente-sei-file-input" accept=".pdf" style="display:none" />

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
  const fileInput = root.querySelector("#agente-sei-file-input");

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

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;
    addMessage("user", `📎 PDF anexado: ${file.name}`);
    setBusy(true);

    const reader = new FileReader();
    reader.onload = function (readerEvent) {
      const base64 = readerEvent.target.result.split(",")[1];

      chrome.runtime.sendMessage(
        {
          type: "AGENTE_SEI_IMPORT_PDF",
          payload: {
            filename: file.name,
            content_base64: base64,
            titulo: document.title || "Processo SEI Completo",
            processo_sei: guessProcessNumber() || "Desconhecido",
            usuario_local: "extensao.sei",
            origem: "extensao_sei_upload"
          }
        },
        (response) => {
          setBusy(false);
          fileInput.value = "";
          if (chrome.runtime.lastError) {
            addMessage("assistant", `Erro no backend: ${chrome.runtime.lastError.message}`, true);
            return;
          }
          if (!response || !response.ok) {
            addMessage("assistant", response && response.error ? response.error : "Falha na leitura do PDF. O backend local esta rodando?", true);
            return;
          }
          addMessage("assistant", formatResult(response.result, "interesse_19crpm"));
        }
      );
    };
    reader.readAsDataURL(file);
  });

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

  const captureButton = root.querySelector("#agente-sei-capturar");
  captureButton.addEventListener("click", () => {
    hydrateContext(true);
    if (!state.capturedText) {
      addMessage("assistant", "Nao encontrei texto visivel suficiente nesta tela.", true);
      return;
    }
    addMessage("assistant", `Texto capturado para analise local: ${state.capturedText.length} caracteres.`);
  });

  function submitPrompt() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      addMessage("assistant", "Digite uma pergunta ou use uma acao rapida.");
      return;
    }

    const justNumbers = prompt.replace(/\D/g, "");
    if (justNumbers.length >= 10 && justNumbers.length <= 25 && justNumbers === prompt.trim()) {
      addMessage(
        "assistant",
        "Detectei um numero de processo. Abra o processo manualmente no SEI ou carregue o PDF exportado; nao faço busca ou abertura automatica."
      );
      promptInput.value = "";
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
    let selection = String(window.getSelection ? window.getSelection() : "").trim();

    let iframeText = "";
    try {
      const iframe = document.getElementById("ifrVisualizacao");
      if (iframe && iframe.contentDocument && iframe.contentDocument.body) {
        iframeText = iframe.contentDocument.body.innerText;
        selection = selection || String(iframe.contentWindow.getSelection ? iframe.contentWindow.getSelection() : "").trim();
      }
    } catch (error) {
      console.warn("Aviso: iframe de visualizacao bloqueado ou nao encontrado.", error);
    }

    const source = selection || iframeText || document.body.innerText || "";
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
      `Processo: ${guessProcessNumber() || "nao identificado"}`,
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

  function setBusy(isBusy) {
    state.busy = isBusy;
    sendButton.disabled = isBusy;
    root.classList.toggle("agente-sei-busy", isBusy);
    if (isBusy) {
      addMessage("assistant", "Analisando no backend local...");
    }
  }
})();
