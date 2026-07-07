const LOCAL_TEXT_API = "http://127.0.0.1:8000/api/import-text";
const LOCAL_AGENT_API = "http://127.0.0.1:8000/api/agent19";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || !["AGENTE_SEI_ANALYZE", "AGENTE_SEI_MISSION"].includes(message.type)) {
    return false;
  }

  const endpoint = message.type === "AGENTE_SEI_MISSION" ? LOCAL_AGENT_API : LOCAL_TEXT_API;
  callLocalApi(endpoint, message.payload)
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) => sendResponse({
      ok: false,
      error: error && error.message ? error.message : "Falha ao chamar backend local."
    }));

  return true;
});

async function callLocalApi(endpoint, payload) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Agente19-User": "extensao.sei",
      "X-Agente19-Role": "operador"
    },
    body: JSON.stringify(payload || {})
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data && data.error && data.error.message ? data.error.message : "Falha na analise.");
  }
  return data;
}
