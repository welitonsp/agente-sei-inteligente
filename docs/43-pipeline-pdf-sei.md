# FASE 42 — Pipeline PDF e Sanitização

## Objetivo
Processar de maneira local, segura e controlada os arquivos PDF exportados do SEI, convertendo-os em texto para análise do Agente 19, assegurando que dados sensíveis não vazem.

## Fluxo
1. O servidor exporta o documento/processo PDF do SEI.
2. O PDF é enviado ao intake do Agente 19.
3. O PyMuPDF lê o arquivo, conta páginas, extrai caracteres e verifica se há necessidade de OCR.
4. São gerados hashes (SHA-256) do arquivo original e do texto extraído.
5. Um `safe_preview` é gerado, limitando caracteres e ocultando dados sensíveis via Regex.

## Limitações e Segurança
- **Uso Estritamente em Memória**: A chave `extracted_text` contém o texto bruto necessário para IAs/LLMs analisarem o caso, porém ela existe *exclusivamente* durante o ciclo de requisição. 
- **Sem Gravação Bruta**: O texto integral **não é persistido** no banco de dados e **não vai para os logs** (`audit.py` filtra essa chave).
- **Sem Automação Web**: Não baixamos o PDF navegando no SEI com Playwright, mantemos a premissa de o próprio humano entregar o arquivo.

## Por que não versionar PDFs reais?
PDFs reais contêm dados pessoais restritos, informações de segurança pública, inquéritos e trâmites sigilosos institucionais. Versioná-los em código fere as políticas de privacidade, LGPD e o sigilo militar. Os repositórios do código contêm apenas stubs (mock) de PDF para testes automatizados temporários gerados em memória pelo `tmp_path`.

## Exemplos de Sanitização de Preview
Os previews que trafegam na auditoria passam pelo `sanitizer.py`, que atua mitigando riscos:
- `123.456.789-00` vira `123.***.***-00`
- `teste@pm.go.gov.br` vira `t***@pm.go.gov.br`
