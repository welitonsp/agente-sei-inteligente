from typing import TypedDict, Annotated, List, Optional
import operator

class MissionState(TypedDict):
    """
    Memoria de Curto Prazo do Agente.
    Mantem o estado do fluxo de trabalho e contexto do SEI.
    """
    processo_sei: str
    titulo: str
    texto_original: str
    usuario_local: str
    unidade_destino: str
    tipo_minuta: str
    
    # Gerados pelo Cérebro
    resumo: str
    campos_pendentes: Annotated[list[str], operator.add]
    minuta_texto: str
    alertas: Annotated[list[str], operator.add]
    confianca: float
    revisao_humana_obrigatoria: bool
    status: str
    tentativas_critica: int
