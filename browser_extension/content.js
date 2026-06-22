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

  const root = document.createElement("div");
  root.id = ROOT_ID;
  root.innerHTML = `
    <button class="agente-sei-button" type="button" title="Agente SEI 19 CRPM">Agente<br>19</button>
    <section class="agente-sei-panel" aria-label="Agente SEI 19 CRPM">
      <div class="agente-sei-head">
        <div class="agente-sei-title">Agente SEI 19 CRPM</div>
        <button class="agente-sei-close" type="button" aria-label="Fechar">×</button>
      </div>
      <div class="agente-sei-body">
        <div class="agente-sei-warning">Modo leitura. Atos oficiais continuam manuais no SEI.</div>
        <div class="agente-sei-field">
          <label>Processo SEI</label>
          <input id="agente-sei-processo" autocomplete="off">
        </div>
        <div class="agente-sei-field">
          <label>Título</label>
          <input id="agente-sei-titulo" autocomplete="off">
        </div>
        <div class="agente-sei-field">
          <label>Texto visível ou selecionado</label>
          <textarea id="agente-sei-texto"></textarea>
        </div>
        <div class="agente-sei-actions">
          <button id="agente-sei-capturar" class="agente-sei-secondary" type="button">Capturar página atual</button>
          <button id="agente-sei-analisar" class="agente-sei-primary" type="button">Analisar aqui</button>
        </div>
        <div id="agente-sei-resultado" class="agente-sei-result">Aguardando análise.</div>
      </div>
    </section>
  `;
  document.documentElement.appendChild(root);

  const openButton = root.querySelector(".agente-sei-button");
  const closeButton = root.querySelector(".agente-sei-close");
  const captureButton = root.querySelector("#agente-sei-capturar");
  const analyzeButton = root.querySelector("#agente-sei-analisar");
  const processInput = root.querySelector("#agente-sei-processo");
  const titleInput = root.querySelector("#agente-sei-titulo");
  const textInput = root.querySelector("#agente-sei-texto");
  const resultBox = root.querySelector("#agente-sei-resultado");

  openButton.addEventListener("click", () => {
    root.classList.add("agente-sei-open");
    hydrateFields();
  });

  closeButton.addEventListener("click", () => {
    root.classList.remove("agente-sei-open");
  });

  captureButton.addEventListener("click", () => {
    hydrateFields(true);
  });

  analyzeButton.addEventListener("click", () => {
    analyzeCurrentText();
  });

  function hydrateFields(forceText) {
    const processo = guessProcessNumber();
    if (processo && !processInput.value.trim()) {
      processInput.value = processo;
    }
    if (!titleInput.value.trim()) {
      titleInput.value = document.title.replace(/\s+/g, " ").trim() || "Página SEI";
    }
    if (forceText || !textInput.value.trim()) {
      textInput.value = getVisibleText();
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

  function analyzeCurrentText() {
    const text = textInput.value.trim();
    if (!text) {
      showResult("Informe ou capture texto visível antes da análise.", true);
      return;
    }
    if (containsForbiddenIntent(text)) {
      showResult("Pedido bloqueado: o assistente não executa ato oficial no SEI.", true);
      return;
    }

    analyzeButton.disabled = true;
    showResult("Analisando no backend local...");
    chrome.runtime.sendMessage(
      {
        type: "AGENTE_SEI_ANALYZE",
        payload: {
          titulo: titleInput.value || document.title || "Página SEI",
          texto: text,
          processo_sei: processInput.value || guessProcessNumber(),
          origem: "extensao_sei_readonly",
          usuario_local: ""
        }
      },
      (response) => {
        analyzeButton.disabled = false;
        if (chrome.runtime.lastError) {
          showResult(`Backend local indisponível: ${chrome.runtime.lastError.message}`, true);
          return;
        }
        if (!response || !response.ok) {
          showResult(response && response.error ? response.error : "Falha na análise.", true);
          return;
        }
        showResult(formatResult(response.result));
      }
    );
  }

  function containsForbiddenIntent(text) {
    const lower = text.toLowerCase();
    return FORBIDDEN_TERMS.some((term) => lower.includes(term));
  }

  function formatResult(payload) {
    const result = payload.resultado || {};
    const event = result.evento || {};
    const deadline = result.prazo || {};
    const lines = [
      `Status: ${payload.status || ""}`,
      `Revisão humana: ${payload.revisao_humana_obrigatoria ? "obrigatória" : "não"}`,
      `Confiança: ${payload.confianca ?? ""}`,
      "",
      result.resumo_executivo || "",
      "",
      `Evento: ${event.ha_evento ? `${event.data || ""} ${event.horario_inicio || ""} ${event.local || ""}` : "não confirmado"}`,
      `Prazo: ${deadline.ha_prazo ? `${deadline.data_limite || ""} ${deadline.hora_limite || ""} ${deadline.risco || ""}` : "não confirmado"}`,
      `Pendências: ${(payload.campos_pendentes || []).join(", ") || "nenhuma"}`,
      "",
      "Atos oficiais devem ser praticados manualmente pelo servidor."
    ];
    return lines.join("\n");
  }

  function showResult(message, isError) {
    resultBox.textContent = message;
    resultBox.classList.toggle("agente-sei-error", Boolean(isError));
  }
})();
