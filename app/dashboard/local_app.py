"""Painel MVP local sem dependencias externas.

Serve uma tela HTML operacional e uma pequena API stdlib para acionar o fluxo
`IMPORT_TEXT`. O painel e externo/local: nao acessa o SEI, nao pesquisa
processo por numero e nao executa ato oficial.
"""

from __future__ import annotations

import base64
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from app.agent.agent19 import AgentRequest, run_agent19
from app.core.auth import AuthError, apply_auth_to_payload, authorize_dashboard_request
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger, log_event
from app.core.safety import assert_safe_environment
from app.intelligence.mission_control import MissionRequest, execute_mission
from app.intelligence.local_minutador import DraftRequest, generate_draft
from app.intelligence.local_triage import TriageRequest, analyze_triage
from app.intake.manual_text import ManualTextRequest
from app.intelligence.llm_gemini import analyze_with_gemini as analyze_text
from app.intake.pdf_upload import PdfUploadRequest, analyze_pdf
from app.storage.db import init_db
from app.dashboard.shadow_dashboard import SHADOW_HTML
from pathlib import Path


INDEX_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agente SEI Inteligente - 19 CRPM</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7f8;
      --ink: #1d252c;
      --muted: #64717d;
      --line: #d9e0e4;
      --panel: #ffffff;
      --accent: #1f6f5b;
      --accent-dark: #155342;
      --warn: #8a5a00;
      --warn-bg: #fff6db;
      --ok-bg: #e7f5ee;
      --shadow: 0 8px 22px rgba(21, 34, 44, .08);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 15px;
      line-height: 1.45;
      letter-spacing: 0;
    }

    header {
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      max-width: 1180px;
      margin: 0 auto;
      padding: 16px 20px;
    }

    h1 {
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
      font-weight: 700;
    }

    .mode {
      min-height: 32px;
      padding: 6px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      color: var(--muted);
      background: #fbfcfc;
      white-space: nowrap;
    }

    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 20px;
      display: grid;
      grid-template-columns: minmax(340px, 440px) minmax(0, 1fr);
      gap: 18px;
    }

    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .panel-head {
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    h2 {
      margin: 0;
      font-size: 16px;
      line-height: 1.2;
    }

    form, .result-body {
      padding: 16px;
    }

    label {
      display: block;
      margin: 0 0 6px;
      font-weight: 700;
      font-size: 13px;
    }

    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 11px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }

    input[type="file"] {
      padding: 8px;
    }

    textarea {
      min-height: 230px;
      resize: vertical;
    }

    .field {
      margin-bottom: 14px;
    }

    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    button {
      min-height: 40px;
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }

    button:hover { background: var(--accent-dark); }
    button:disabled { cursor: wait; opacity: .65; }

    .status {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
      background: var(--warn-bg);
      color: var(--warn);
    }

    .status.ok {
      background: var(--ok-bg);
      color: var(--accent-dark);
    }

    .placeholder {
      min-height: 260px;
      display: grid;
      place-items: center;
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 8px;
      text-align: center;
      padding: 20px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }

    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 76px;
      background: #fbfcfc;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 5px;
    }

    .metric strong {
      overflow-wrap: anywhere;
    }

    pre {
      margin: 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfc;
      overflow: auto;
      min-height: 130px;
      max-height: 330px;
      white-space: pre-wrap;
    }

    .error {
      color: #8d1f11;
      font-weight: 700;
    }

    @media (max-width: 860px) {
      main { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .mode { white-space: normal; }
    }

    @media (max-width: 540px) {
      main { padding: 12px; }
      .row, .grid { grid-template-columns: 1fr; }
      textarea { min-height: 180px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <h1>Agente SEI Inteligente - 19 CRPM</h1>
      <div style="display: flex; gap: 12px; align-items: center;">
        <a href="/shadow.html" style="color: var(--accent); font-weight: 600; text-decoration: none;">Analytics Sombra &rarr;</a>
        <div class="mode">MVP local</div>
      </div>
    </div>
  </header>
  <main>
    <section aria-labelledby="nova-demanda">
      <div class="panel-head">
        <h2 id="nova-demanda">Nova demanda</h2>
      </div>
      <form id="intake-form">
        <div class="row">
          <div class="field">
            <label for="processo">Numero do processo SEI</label>
            <input id="processo" name="processo_sei" autocomplete="off">
          </div>
          <div class="field">
            <label for="usuario">Usuario local</label>
            <input id="usuario" name="usuario_local" autocomplete="off">
          </div>
        </div>
        <div class="field">
          <label for="perfil">Perfil local</label>
          <select id="perfil" name="perfil_local">
            <option value="operador">Operador</option>
            <option value="revisor">Revisor</option>
            <option value="gestor">Gestor</option>
          </select>
        </div>
        <div class="field">
          <label for="titulo">Titulo</label>
          <input id="titulo" name="titulo" autocomplete="off" required>
        </div>
        <div class="row">
          <div class="field">
            <label for="unidade">Unidade/destinatario</label>
            <input id="unidade" name="unidade_destino" autocomplete="off">
          </div>
          <div class="field">
            <label for="tipo-minuta">Tipo de minuta</label>
            <select id="tipo-minuta" name="tipo_minuta">
              <option value="">Automatico</option>
              <option value="despacho">Despacho</option>
              <option value="oficio">Oficio</option>
              <option value="informacao">Informacao</option>
              <option value="encaminhamento">Encaminhamento</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label for="texto">Texto copiado</label>
          <textarea id="texto" name="texto"></textarea>
        </div>
        <div class="field">
          <label for="pdf">PDF</label>
          <input id="pdf" name="pdf" type="file" accept="application/pdf">
        </div>
        <button id="submit" type="submit">Analisar para o 19 CRPM</button>
      </form>
    </section>

    <section aria-labelledby="resultado">
      <div class="panel-head">
        <h2 id="resultado">Resultado</h2>
        <span id="badge" class="status">Aguardando</span>
      </div>
      <div class="result-body">
        <div id="empty" class="placeholder">Nenhuma demanda analisada.</div>
        <div id="result" hidden>
          <div class="grid">
            <div class="metric"><span>Status</span><strong id="status"></strong></div>
            <div class="metric"><span>Revisao humana</span><strong id="review"></strong></div>
            <div class="metric"><span>Confianca</span><strong id="confidence"></strong></div>
            <div class="metric"><span>Hash</span><strong id="hash"></strong></div>
            <div class="metric"><span>Leitura</span><strong id="reading"></strong></div>
            <div class="metric"><span>Paginas</span><strong id="pages"></strong></div>
          </div>
          <div class="field">
            <label>Resumo</label>
            <pre id="summary"></pre>
          </div>
          <div class="grid">
            <div class="metric"><span>Evento</span><strong id="event"></strong></div>
            <div class="metric"><span>Prazo</span><strong id="deadline"></strong></div>
          </div>
          <div class="field">
            <label>Campos pendentes</label>
            <pre id="pending"></pre>
          </div>
          <button id="draft-button" type="button" disabled>Gerar minuta local</button>
          <button id="triage-button" type="button" disabled>Triagem local</button>
          <button id="mission-button" type="button" disabled>Missao Agente 19</button>
          <button id="copy-draft" type="button" disabled>Copiar minuta</button>
          <div class="field">
            <label>Missao Agente 19</label>
            <pre id="mission"></pre>
          </div>
          <div class="field">
            <label>Triagem e roteamento</label>
            <pre id="triage"></pre>
          </div>
          <div class="field">
            <label>Minuta local</label>
            <pre id="draft"></pre>
          </div>
        </div>
        <div id="error" class="error" hidden></div>
      </div>
    </section>
  </main>
  <script>
    const form = document.getElementById("intake-form");
    const submit = document.getElementById("submit");
    const badge = document.getElementById("badge");
    const empty = document.getElementById("empty");
    const result = document.getElementById("result");
    const errorBox = document.getElementById("error");
    const draftButton = document.getElementById("draft-button");
    const triageButton = document.getElementById("triage-button");
    const missionButton = document.getElementById("mission-button");
    const copyDraft = document.getElementById("copy-draft");
    const draftBox = document.getElementById("draft");
    const triageBox = document.getElementById("triage");
    const missionBox = document.getElementById("mission");
    let lastAnalysis = null;

    function setText(id, value) {
      document.getElementById(id).textContent = value || "";
    }

    function showError(message) {
      errorBox.textContent = message;
      errorBox.hidden = false;
      badge.textContent = "Erro";
      badge.className = "status";
    }

    function requestHeaders() {
      return {
        "Content-Type": "application/json",
        "X-Agente19-User": document.getElementById("usuario").value,
        "X-Agente19-Role": document.getElementById("perfil").value
      };
    }

    function render(payload) {
      const data = payload.resultado || {};
      const event = data.evento || {};
      const deadline = data.prazo || {};
      empty.hidden = true;
      result.hidden = false;
      errorBox.hidden = true;
      badge.textContent = payload.status || "Recebido";
      badge.className = "status ok";
      lastAnalysis = payload;
      draftButton.disabled = false;
      triageButton.disabled = false;
      missionButton.disabled = false;
      setText("status", payload.status);
      setText("review", payload.revisao_humana_obrigatoria ? "Obrigatoria" : "Nao");
      setText("confidence", String(payload.confianca ?? ""));
      setText("hash", data.text_hash || data.file_hash || "");
      setText("reading", data.status_leitura || "texto_colado");
      setText("pages", data.page_count ? String(data.page_count) : "");
      setText("summary", data.resumo_executivo || "");
      setText("event", event.ha_evento ? `${event.data || ""} ${event.horario_inicio || ""} ${event.local || ""}` : "Nao confirmado");
      setText("deadline", deadline.ha_prazo ? `${deadline.data_limite || ""} ${deadline.hora_limite || ""} ${deadline.risco || ""}` : "Nao confirmado");
      setText("pending", (payload.campos_pendentes || []).join("\\n") || "Nenhum");
      setText("draft", "");
      setText("triage", "");
      setText("mission", "");
      copyDraft.disabled = true;
    }

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      submit.disabled = true;
      badge.textContent = "Analisando";
      badge.className = "status";
      const formData = new FormData(form);
      const file = document.getElementById("pdf").files[0];
      const body = Object.fromEntries(formData.entries());
      delete body.pdf;
      try {
        let endpoint = "/api/import-text";
        if (file) {
          endpoint = "/api/import-pdf";
          body.filename = file.name;
          body.content_base64 = await fileToBase64(file);
        }
        const response = await fetch(endpoint, {
          method: "POST",
          headers: requestHeaders(),
          body: JSON.stringify(body)
        });
        const payload = await response.json();
        if (!response.ok) {
          showError(payload.error?.message || "Falha ao analisar.");
          return;
        }
        render(payload);
      } catch (err) {
        showError("Falha de comunicacao com o painel local.");
      } finally {
        submit.disabled = false;
      }
    });

    draftButton.addEventListener("click", async () => {
      if (!lastAnalysis) return;
      draftButton.disabled = true;
      badge.textContent = "Gerando minuta";
      const data = lastAnalysis.resultado || {};
      const event = data.evento || {};
      const deadline = data.prazo || {};
      const payload = {
        processo_sei: document.getElementById("processo").value,
        usuario_local: document.getElementById("usuario").value,
        assunto: document.getElementById("titulo").value,
        unidade_destino: document.getElementById("unidade").value,
        destinatario: document.getElementById("unidade").value,
        tipo_minuta: document.getElementById("tipo-minuta").value,
        resumo: data.resumo_executivo || "",
        prazo: deadline.ha_prazo ? `${deadline.data_limite || ""} ${deadline.hora_limite || ""}` : "",
        evento: event.ha_evento ? `${event.data || ""} ${event.horario_inicio || ""} ${event.local || ""}` : ""
      };
      try {
        const response = await fetch("/api/generate-draft", {
          method: "POST",
          headers: requestHeaders(),
          body: JSON.stringify(payload)
        });
        const draftPayload = await response.json();
        if (!response.ok) {
          showError(draftPayload.error?.message || "Falha ao gerar minuta.");
          return;
        }
        draftBox.textContent = formatDraft(draftPayload);
        copyDraft.disabled = false;
        badge.textContent = "Minuta pronta";
        badge.className = "status ok";
      } catch (err) {
        showError("Falha de comunicacao ao gerar minuta.");
      } finally {
        draftButton.disabled = false;
      }
    });

    triageButton.addEventListener("click", async () => {
      if (!lastAnalysis) return;
      triageButton.disabled = true;
      badge.textContent = "Triando";
      const data = lastAnalysis.resultado || {};
      const payload = {
        processo_sei: document.getElementById("processo").value,
        usuario_local: document.getElementById("usuario").value,
        assunto: document.getElementById("titulo").value,
        texto: data.resumo_executivo || ""
      };
      try {
        const response = await fetch("/api/triage-local", {
          method: "POST",
          headers: requestHeaders(),
          body: JSON.stringify(payload)
        });
        const triagePayload = await response.json();
        if (!response.ok) {
          showError(triagePayload.error?.message || "Falha na triagem.");
          return;
        }
        triageBox.textContent = formatTriage(triagePayload);
        const result = triagePayload.resultado || {};
        if (result.unidade_sugerida) {
          document.getElementById("unidade").value = result.unidade_sugerida;
        }
        if (result.tipo_minuta_sugerido) {
          document.getElementById("tipo-minuta").value = result.tipo_minuta_sugerido;
        }
        badge.textContent = "Triagem pronta";
        badge.className = "status ok";
      } catch (err) {
        showError("Falha de comunicacao na triagem.");
      } finally {
        triageButton.disabled = false;
      }
    });

    missionButton.addEventListener("click", async () => {
      if (!lastAnalysis) return;
      missionButton.disabled = true;
      badge.textContent = "Orquestrando missao";
      const data = lastAnalysis.resultado || {};
      const payload = {
        processo_sei: document.getElementById("processo").value,
        usuario_local: document.getElementById("usuario").value,
        titulo: document.getElementById("titulo").value,
        texto: document.getElementById("texto").value || data.resumo_executivo || "",
        unidade_destino: document.getElementById("unidade").value,
        tipo_minuta: document.getElementById("tipo-minuta").value
      };
      try {
        const response = await fetch("/api/mission-control", {
          method: "POST",
          headers: requestHeaders(),
          body: JSON.stringify(payload)
        });
        const missionPayload = await response.json();
        if (!response.ok) {
          showError(missionPayload.error?.message || "Falha na missao.");
          return;
        }
        missionBox.textContent = formatMission(missionPayload);
        const result = missionPayload.resultado || {};
        const triage = result.triagem || {};
        const draft = result.minuta || {};
        if (triage.unidade_sugerida) {
          document.getElementById("unidade").value = triage.unidade_sugerida;
        }
        if (draft.tipo_minuta) {
          document.getElementById("tipo-minuta").value = draft.tipo_minuta;
        }
        if (draft.texto) {
          draftBox.textContent = formatDraft({
            resultado: draft,
            confianca: missionPayload.confianca,
            revisao_humana_obrigatoria: true,
            campos_pendentes: missionPayload.campos_pendentes || []
          });
          copyDraft.disabled = false;
        }
        badge.textContent = "Missao pronta";
        badge.className = "status ok";
      } catch (err) {
        showError("Falha de comunicacao na missao.");
      } finally {
        missionButton.disabled = false;
      }
    });

    copyDraft.addEventListener("click", async () => {
      const text = draftBox.textContent || "";
      if (!text) return;
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
      }
      badge.textContent = "Minuta copiada";
      badge.className = "status ok";
    });

    function fileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const value = String(reader.result || "");
          resolve(value.includes(",") ? value.split(",", 2)[1] : value);
        };
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
      });
    }

    function formatDraft(payload) {
      const data = payload.resultado || {};
      const lines = [
        `Tipo: ${data.tipo_minuta || ""}`,
        `Confianca: ${payload.confianca ?? ""}`,
        `Revisao humana: ${payload.revisao_humana_obrigatoria ? "obrigatoria" : "nao informada"}`,
        "",
        data.texto || "",
        "",
        `Providencia sugerida: ${data.providencia_sugerida || ""}`,
        `Campos pendentes: ${(payload.campos_pendentes || []).join(", ") || "nenhum"}`,
        `Alertas: ${(data.alertas || []).join(" | ")}`
      ];
      return lines.join("\\n");
    }

    function formatTriage(payload) {
      const data = payload.resultado || {};
      const lines = [
        `Interesse 19 CRPM: ${data.interesse_19crpm || ""}`,
        `Unidade sugerida: ${data.unidade_sugerida || "indefinida"}`,
        `Tipo de minuta: ${data.tipo_minuta_sugerido || "indefinido"}`,
        `Providencia: ${data.providencia_sugerida || ""}`,
        `Regra aplicada: ${data.regra_aplicada || "nenhuma"}`,
        `Confianca: ${payload.confianca ?? ""}`,
        `Revisao humana: ${payload.revisao_humana_obrigatoria ? "obrigatoria" : "nao informada"}`,
        `Campos pendentes: ${(payload.campos_pendentes || []).join(", ") || "nenhum"}`,
        "",
        data.justificativa || ""
      ];
      return lines.join("\\n");
    }

    function formatMission(payload) {
      const data = payload.resultado || {};
      const triage = data.triagem || {};
      const draft = data.minuta || {};
      const lines = [
        `Status: ${payload.status || ""}`,
        `Prontidao operacional: ${data.prontidao_operacional ?? ""}`,
        `Etapa recomendada: ${data.etapa_recomendada || ""}`,
        `Revisao humana: ${payload.revisao_humana_obrigatoria ? "obrigatoria" : "nao informada"}`,
        `Unidade sugerida: ${triage.unidade_sugerida || "indefinida"}`,
        `Tipo de minuta: ${draft.tipo_minuta || "indefinido"}`,
        `Campos pendentes: ${(payload.campos_pendentes || []).join(", ") || "nenhum"}`,
        `Riscos: ${(data.riscos || []).join(", ") || "nenhum"}`,
        "",
        "Plano operacional:",
        ...((data.plano_operacional || []).map((item, idx) => `${idx + 1}. ${item}`))
      ];
      return lines.join("\\n");
    }
  </script>
</body>
</html>
"""


def create_import_text_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Executa `IMPORT_TEXT` e devolve o contrato serializavel."""
    request = ManualTextRequest(
        titulo=str(payload.get("titulo", "")),
        texto=str(payload.get("texto", "")),
        processo_sei=str(payload.get("processo_sei", "")),
        usuario_local=str(payload.get("usuario_local", "")),
        estacao=str(payload.get("estacao", "")),
        origem=str(payload.get("origem") or "dashboard_local"),
    )
    return analyze_text(request).to_contract()


def create_import_pdf_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Executa upload de PDF local e devolve o contrato serializavel."""
    raw_b64 = str(payload.get("content_base64", ""))
    content = base64.b64decode(raw_b64, validate=True) if raw_b64 else b""
    request = PdfUploadRequest(
        filename=str(payload.get("filename", "")),
        content=content,
        titulo=str(payload.get("titulo", "")),
        processo_sei=str(payload.get("processo_sei", "")),
        usuario_local=str(payload.get("usuario_local", "")),
        estacao=str(payload.get("estacao", "")),
        origem=str(payload.get("origem") or "dashboard_local"),
    )
    return analyze_pdf(request).to_contract()


def create_draft_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Gera minuta local por template, sem salvar ou escrever no SEI."""
    request = DraftRequest(
        assunto=str(payload.get("assunto") or payload.get("titulo") or ""),
        resumo=str(payload.get("resumo", "")),
        texto_base=str(payload.get("texto_base", "")),
        processo_sei=str(payload.get("processo_sei", "")),
        tipo_minuta=str(payload.get("tipo_minuta", "")),
        unidade_destino=str(payload.get("unidade_destino", "")),
        destinatario=str(payload.get("destinatario", "")),
        providencia=str(payload.get("providencia", "")),
        prazo=str(payload.get("prazo", "")),
        evento=str(payload.get("evento", "")),
        usuario_local=str(payload.get("usuario_local", "")),
        estacao=str(payload.get("estacao", "")),
        origem=str(payload.get("origem") or "dashboard_local"),
    )
    return generate_draft(request).to_contract()


def create_triage_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Executa triagem/roteamento local por regras, sem inventar unidade."""
    request = TriageRequest(
        assunto=str(payload.get("assunto") or payload.get("titulo") or ""),
        texto=str(payload.get("texto", "")),
        processo_sei=str(payload.get("processo_sei", "")),
        usuario_local=str(payload.get("usuario_local", "")),
        estacao=str(payload.get("estacao", "")),
        origem=str(payload.get("origem") or "dashboard_local"),
    )
    return analyze_triage(request).to_contract()


def create_mission_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Executa a missao supervisionada: analise + triagem + minuta."""
    request = MissionRequest(
        titulo=str(payload.get("titulo") or payload.get("assunto") or ""),
        texto=str(payload.get("texto", "")),
        processo_sei=str(payload.get("processo_sei", "")),
        usuario_local=str(payload.get("usuario_local", "")),
        estacao=str(payload.get("estacao", "")),
        unidade_destino=str(payload.get("unidade_destino", "")),
        tipo_minuta=str(payload.get("tipo_minuta", "")),
        origem=str(payload.get("origem") or "dashboard_local"),
    )
    return execute_mission(request).to_contract()


def create_agent19_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Executa o Agente 19 como agente de IA supervisionado."""
    request = AgentRequest(
        mensagem=str(payload.get("mensagem") or payload.get("prompt") or ""),
        titulo=str(payload.get("titulo") or payload.get("assunto") or ""),
        texto=str(payload.get("texto", "")),
        processo_sei=str(payload.get("processo_sei", "")),
        usuario_local=str(payload.get("usuario_local", "")),
        perfil_local=str(payload.get("perfil_local", "")),
        unidade_destino=str(payload.get("unidade_destino") or "PM/19 CRPM"),
        origem=str(payload.get("origem") or "dashboard_local"),
        trace_id=str(payload.get("trace_id", "")),
    )
    return run_agent19(request).to_contract()


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "AgenteSeiDashboard/0.1"

    def do_GET(self) -> None:  # noqa: N802 - API stdlib
        if self.path in ("/", "/index.html"):
            self._send_html(INDEX_HTML)
            return
        if self.path == "/shadow.html":
            self._send_html(SHADOW_HTML)
            return
        if self.path == "/api/shadow-logs":
            log_path = Path(".shadow_logs/shadow_trials.jsonl")
            logs = []
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except Exception:
                                pass
            self._send_json(logs)
            return
        if self.path == "/health":
            self._send_json({"status": "ok"})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - API stdlib
        if self.path not in (
            "/api/import-text",
            "/api/import-pdf",
            "/api/generate-draft",
            "/api/triage-local",
            "/api/mission-control",
            "/api/agent19",
        ):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            payload = self._read_json()
            auth = authorize_dashboard_request(self.path, self.headers, payload)
            payload = apply_auth_to_payload(payload, auth)
            if self.path == "/api/agent19":
                result = create_agent19_response(payload)
            elif self.path == "/api/mission-control":
                result = create_mission_response(payload)
            elif self.path == "/api/triage-local":
                result = create_triage_response(payload)
            elif self.path == "/api/generate-draft":
                result = create_draft_response(payload)
            elif self.path == "/api/import-pdf":
                result = create_import_pdf_response(payload)
            else:
                result = create_import_text_response(payload)
        except json.JSONDecodeError:
            self._send_json(
                {"error": {"code": "INVALID_JSON", "message": "JSON invalido."}},
                status=HTTPStatus.BAD_REQUEST,
            )
            return
        except ValueError as exc:
            msg = str(exc)
            code = "INVALID_FILE" if "PDF" in msg else "VALIDATION_ERROR"
            self._send_json(
                {"error": {"code": code, "message": msg}},
                status=HTTPStatus.BAD_REQUEST,
            )
            return
        except RuntimeError as exc:
            self._send_json(
                {"error": {"code": "RUNTIME_ERROR", "message": str(exc)}},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return
        except AuthError as exc:
            self._send_json(exc.to_error(), status=exc.status)
            return
        except Exception:
            self._send_json(
                {"error": {"code": "FAILED", "message": "Falha tecnica."}},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return
        self._send_json(result)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        if not raw:
            return {}
        parsed = json.loads(raw.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else {}

    def _send_html(self, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, body: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run(host: str | None = None, port: int | None = None) -> None:
    settings = get_settings()
    assert_safe_environment(settings)
    configure_logging(settings.log_level)
    init_db()

    bind_host = host or settings.app_host
    bind_port = port or settings.app_port
    httpd = ThreadingHTTPServer((bind_host, bind_port), DashboardHandler)
    logger = get_logger("dashboard")
    log_event(
        logger,
        20,
        "painel local iniciado",
        url=f"http://{bind_host}:{bind_port}",
    )
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
