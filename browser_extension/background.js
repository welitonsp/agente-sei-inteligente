const LOCAL_API = "http://127.0.0.1:8000/api/import-text";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || message.type !== "AGENTE_SEI_ANALYZE") {
    return false;
  }

  analyze(message.payload)
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) => sendResponse({
      ok: false,
      error: error && error.message ? error.message : "Falha ao chamar backend local."
    }));

  return true;
});

async function analyze(payload) {
  const response = await fetch(LOCAL_API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data && data.error && data.error.message ? data.error.message : "Falha na analise.");
  }
  return data;
}
