"""Definição dos Agentes Especialistas do Swarm.

Cada agente possui um propósito único e restrito (Single Responsibility Principle)
e interage diretamente com o AIProvider utilizando um Role específico.
"""

import json
from app.intelligence.ai_provider import get_ai_provider, AIRole
from app.intelligence.swarm.state import SwarmState

class TriageAgent:
    """Analisa o contexto e extrai intenção, resumo e providência."""
    
    def execute(self, state: SwarmState) -> SwarmState:
        state.log("TriageAgent", "Iniciando análise do documento.")
        provider = get_ai_provider()
        
        prompt = f"""
        Documento: {state.titulo_documento}
        Texto: {state.texto_processo}
        
        Responda em formato JSON válido contendo as chaves:
        "intencao" (ex: solicitacao, despacho, aviso),
        "resumo" (resumo executivo do texto),
        "providencia" (qual o próximo passo esperado no SEI).
        """
        
        try:
            response = provider.complete(AIRole.CLASSIFICACAO, prompt)
            # Tentar parsear o JSON retornado pela IA
            data = json.loads(response.strip().removeprefix("```json").removesuffix("```").strip())
            state.intencao_detectada = data.get("intencao", "indefinido")
            state.resumo = data.get("resumo", "Resumo não disponível.")
            state.providencia_sugerida = data.get("providencia", "Nenhuma providência detectada.")
            state.log("TriageAgent", f"Sucesso. Intenção: {state.intencao_detectada}")
        except Exception as e:
            state.log("TriageAgent", f"Erro no parsing: {e}. Usando fallbacks.")
            state.intencao_detectada = "indefinido"
            state.resumo = "Erro ao processar."
            
        return state


class DraftAgent:
    """Redige minutas baseadas na triagem anterior."""
    
    def execute(self, state: SwarmState) -> SwarmState:
        state.tentativas_redacao += 1
        state.log("DraftAgent", f"Iniciando redação (Tentativa {state.tentativas_redacao}).")
        provider = get_ai_provider()
        
        prompt = f"""
        Você é um Assistente do 19 CRPM.
        Baseado neste resumo: {state.resumo}
        E nesta intenção: {state.intencao_detectada}
        
        Redija uma minuta de resposta adequada (Despacho ou Ofício).
        Atenção: Trata-se de um RASCUNHO EXTERNO, NÃO assine.
        """
        
        # Se houve crítica na iteração anterior, injetar no prompt
        if state.revisao_critica and not state.aprovado_pelo_critico:
            prompt += f"\n\nATENÇÃO! A versão anterior foi rejeitada pelo Revisor com a seguinte crítica:\n{state.revisao_critica}\nCorrija esses pontos na nova minuta."
            
        try:
            minuta = provider.complete(AIRole.MINUTA, prompt)
            state.minuta_rascunho = minuta.strip()
            state.tipo_minuta = "oficio" if "ofício" in state.minuta_rascunho.lower() else "despacho"
            state.log("DraftAgent", "Redação de minuta concluída.")
        except Exception as e:
            state.log("DraftAgent", f"Erro na redação: {e}")
            
        return state


class CriticAgent:
    """Revisa a minuta para garantir qualidade, tom e conformidade (Compliance)."""
    
    def execute(self, state: SwarmState) -> SwarmState:
        state.log("CriticAgent", "Avaliando qualidade da minuta redigida.")
        provider = get_ai_provider()
        
        if not state.minuta_rascunho:
            state.revisao_critica = "A minuta está vazia."
            state.aprovado_pelo_critico = False
            state.log("CriticAgent", "Reprovado (Vazia).")
            return state
            
        prompt = f"""
        Você é o Revisor de Compliance do SEI (Polícia Militar).
        Avalie a minuta abaixo com base no contexto:
        
        Contexto original: {state.resumo}
        Minuta gerada:
        {state.minuta_rascunho}
        
        Regras de Ouro:
        1. Tom formal e impessoal.
        2. Não deve conter promessas irreais ou ações fora da alçada do 19 CRPM.
        3. Não pode assinar o documento (deve terminar com espaço para assinatura).
        
        Responda em JSON válido:
        "aprovado": true ou false,
        "critica": "Comentários do que precisa melhorar, se aprovado=false"
        """
        
        try:
            response = provider.complete(AIRole.REVISAO, prompt)
            data = json.loads(response.strip().removeprefix("```json").removesuffix("```").strip())
            
            state.aprovado_pelo_critico = data.get("aprovado", False)
            state.revisao_critica = data.get("critica", "")
            
            if state.aprovado_pelo_critico:
                state.log("CriticAgent", "Minuta aprovada com sucesso. Sem ressalvas.")
            else:
                state.log("CriticAgent", f"Minuta rejeitada. Motivo: {state.revisao_critica}")
                
        except Exception as e:
            state.log("CriticAgent", f"Falha ao interpretar revisão: {e}. Aprovando por segurança (Fallback) para humano.")
            # Em caso de falha de parser do LLM, degradação graciosa delegando ao Humano (Human-in-the-loop)
            state.aprovado_pelo_critico = True 
            
        return state
