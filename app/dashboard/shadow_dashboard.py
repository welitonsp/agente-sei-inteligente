"""Interface rica para visualizacao dos logs de Shadow Mode.
"""

SHADOW_HTML = """<!doctype html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shadow Mode Analytics - Agente 19</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --bg-panel: #1e293b;
      --border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.2);
      --success: #10b981;
      --danger: #ef4444;
      --font-main: 'Inter', sans-serif;
    }

    * { box-sizing: border-box; }
    
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text-main);
      font-family: var(--font-main);
      -webkit-font-smoothing: antialiased;
      line-height: 1.5;
    }

    header {
      background: rgba(30, 41, 59, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 40px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .logo-container {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .pulse-dot {
      width: 10px;
      height: 10px;
      background: var(--success);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--success);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
      100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    h1 {
      margin: 0;
      font-size: 22px;
      font-weight: 600;
      letter-spacing: -0.5px;
      background: linear-gradient(90deg, #f8fafc, #94a3b8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    main {
      max-width: 1400px;
      margin: 40px auto;
      padding: 0 40px;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
      margin-bottom: 40px;
    }

    .kpi-card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      border-color: var(--accent);
    }

    .kpi-title {
      color: var(--text-muted);
      font-size: 14px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }

    .kpi-value {
      font-size: 36px;
      font-weight: 700;
      color: var(--text-main);
    }

    .table-container {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    th, td {
      padding: 16px 24px;
      border-bottom: 1px solid var(--border);
    }

    th {
      background: rgba(15, 23, 42, 0.5);
      font-weight: 600;
      font-size: 13px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    tr:last-child td {
      border-bottom: none;
    }

    tr:hover td {
      background: rgba(56, 189, 248, 0.05);
    }

    .badge {
      display: inline-flex;
      align-items: center;
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      background: rgba(148, 163, 184, 0.1);
      color: var(--text-muted);
      border: 1px solid rgba(148, 163, 184, 0.2);
    }

    .badge.match {
      background: rgba(16, 185, 129, 0.1);
      color: var(--success);
      border-color: rgba(16, 185, 129, 0.2);
    }

    .badge.mismatch {
      background: rgba(239, 68, 68, 0.1);
      color: var(--danger);
      border-color: rgba(239, 68, 68, 0.2);
    }

    .confidence-bar {
      height: 6px;
      background: var(--border);
      border-radius: 999px;
      overflow: hidden;
      margin-top: 8px;
    }

    .confidence-fill {
      height: 100%;
      background: var(--accent);
      border-radius: 999px;
    }
    
    .empty-state {
      text-align: center;
      padding: 60px;
      color: var(--text-muted);
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div class="logo-container">
        <div class="pulse-dot"></div>
        <h1>Agente 19: Shadow Mode Analytics</h1>
      </div>
      <div>
        <a href="/" style="color: var(--accent); text-decoration: none; font-weight: 500;">&larr; Voltar ao Painel</a>
      </div>
    </div>
  </header>

  <main>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">Total de Missões Sombra</div>
        <div class="kpi-value" id="kpi-total">0</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Média de Confiança</div>
        <div class="kpi-value" id="kpi-confidence">0%</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Ações Validadas (Match)</div>
        <div class="kpi-value" id="kpi-match">0</div>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Data/Hora</th>
            <th>Processo SEI</th>
            <th>Intenção</th>
            <th>Ação Proposta (IA)</th>
            <th>Confiança</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="table-body">
          <tr><td colspan="6" class="empty-state">Carregando logs...</td></tr>
        </tbody>
      </table>
    </div>
  </main>

  <script>
    async function loadLogs() {
      try {
        const res = await fetch('/api/shadow-logs');
        if (!res.ok) throw new Error('Falha ao carregar');
        const logs = await res.json();
        
        const tbody = document.getElementById('table-body');
        
        if (logs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Nenhuma missão em Shadow Mode registrada ainda.</td></tr>';
          return;
        }

        let totalConf = 0;
        let matches = 0;
        let validConf = 0;

        tbody.innerHTML = logs.reverse().map(log => {
          if (log.confidence_score) {
             totalConf += log.confidence_score;
             validConf++;
          }
          if (log.match) matches++;

          const date = new Date(log.timestamp).toLocaleString('pt-BR');
          let statusBadge = '<span class="badge">Aguardando Humano</span>';
          if (log.acao_real_humano) {
             statusBadge = log.match ? '<span class="badge match">Match!</span>' : '<span class="badge mismatch">Desvio</span>';
          }

          return `
            <tr>
              <td style="color: var(--text-muted); font-size: 14px;">${date}</td>
              <td style="font-family: monospace; color: var(--accent);">${log.processo_sei}</td>
              <td>${log.intencao_detectada}</td>
              <td style="font-weight: 500;">${log.acao_proposta_ia}</td>
              <td>
                <div style="font-weight: 600;">${log.confidence_score}%</div>
                <div class="confidence-bar">
                  <div class="confidence-fill" style="width: ${log.confidence_score}%"></div>
                </div>
              </td>
              <td>${statusBadge}</td>
            </tr>
          `;
        }).join('');

        document.getElementById('kpi-total').textContent = logs.length;
        if (validConf > 0) {
           document.getElementById('kpi-confidence').textContent = (totalConf / validConf).toFixed(1) + '%';
        }
        document.getElementById('kpi-match').textContent = matches;

      } catch (err) {
        document.getElementById('table-body').innerHTML = `<tr><td colspan="6" class="empty-state" style="color: var(--danger)">Erro: ${err.message}</td></tr>`;
      }
    }

    loadLogs();
    // Auto-refresh a cada 10 segundos para efeito de sala de comando
    setInterval(loadLogs, 10000);
  </script>
</body>
</html>
"""
