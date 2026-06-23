"""FASE 5A - escrita controlada de minuta, ainda simulada.

`MinutaWriter` e o chokepoint para qualquer tentativa futura de criar minuta no
SEI. Ele nao expoe pagina crua, exige token de confirmacao e mantem a escrita
real como `NotImplementedError` ate a FASE 5B homologada.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core import audit
from app.core.config import Settings, get_settings
from app.sei.minuta_token import text_hash, verify_minuta_token


CONTROLLED_WRITE_ACTIONS = frozenset(
    {
        "INSERIR_TEXTO_MINUTA",
        "SALVAR_MINUTA",
    }
)


@dataclass(frozen=True)
class MinutaWriteResult:
    """Resultado serializavel da FASE 5A."""

    status: str
    processo_sei: str
    tipo_documento: str
    text_hash: str
    mensagem: str


class MinutaWriter:
    """Chokepoint de minuta controlada.

    A classe opera com valores confirmados e nao recebe `page` Playwright crua.
    """

    def __init__(
        self,
        *,
        processo_confirmado: str,
        processo_aberto: str,
        tipo_documento: str,
        texto_final: str,
        usuario_local: str = "",
        settings: Settings | None = None,
    ) -> None:
        self.__settings = settings or get_settings()
        self.__processo_confirmado = str(processo_confirmado).strip()
        self.__processo_aberto = str(processo_aberto).strip()
        self.__tipo_documento = str(tipo_documento).strip()
        self.__texto = str(texto_final)
        self.__usuario_local = str(usuario_local).strip()

        if not self.__processo_confirmado:
            raise ValueError("Processo confirmado e obrigatorio.")
        if not self.__tipo_documento:
            raise ValueError("Tipo de documento existente no SEI e obrigatorio.")
        if _digits(self.__processo_confirmado) != _digits(self.__processo_aberto):
            raise ValueError("Processo aberto nao confere com processo confirmado.")

    @property
    def processo_confirmado(self) -> str:
        return self.__processo_confirmado

    @property
    def tipo_documento(self) -> str:
        return self.__tipo_documento

    @property
    def hash_texto(self) -> str:
        return text_hash(self.__texto)

    def inserir_texto_minuta(self, *, confirmation_token: str) -> MinutaWriteResult:
        """Simula insercao do texto e audita apenas o hash.

        Escrita real permanece em stub para a FASE 5B.
        """
        self.__assert_token(confirmation_token)
        self.__audit("INSERIR_TEXTO_MINUTA", "simulado")
        if self.__settings.enable_minuta_creation:
            return self.__inserir_texto_minuta_real()
        return self.__simulated_result("Texto validado para minuta simulada.")

    def salvar_minuta(self, *, confirmation_token: str) -> MinutaWriteResult:
        """Simula salvamento de minuta e audita apenas o hash."""
        self.__assert_token(confirmation_token)
        self.__audit("SALVAR_MINUTA", "simulado")
        if self.__settings.enable_minuta_creation:
            return self.__salvar_minuta_real()
        return self.__simulated_result("Salvamento de minuta simulado.")

    def __assert_token(self, token: str) -> None:
        if not verify_minuta_token(
            processo_sei=self.__processo_confirmado,
            tipo_documento=self.__tipo_documento,
            texto=self.__texto,
            token=token,
            secret=self.__settings.minuta_token_secret,
        ):
            raise PermissionError("Token de confirmacao da minuta invalido.")

    def __audit(self, action: str, result: str) -> None:
        if action not in CONTROLLED_WRITE_ACTIONS:
            raise PermissionError("Acao de escrita controlada fora da allow-list.")
        audit.record(
            action=action,
            result=result,
            actor_type="usuario_local",
            actor_id=self.__usuario_local or None,
            target_type="processo_sei",
            target_id=self.__processo_confirmado,
            reason="FASE 5A - minuta controlada simulada.",
            metadata={
                "tipo_documento": self.__tipo_documento,
                "text_hash": self.hash_texto,
                "fase": "5A",
                "real_write_enabled": self.__settings.enable_minuta_creation,
            },
        )

    def __simulated_result(self, mensagem: str) -> MinutaWriteResult:
        return MinutaWriteResult(
            status="simulado",
            processo_sei=self.__processo_confirmado,
            tipo_documento=self.__tipo_documento,
            text_hash=self.hash_texto,
            mensagem=mensagem,
        )

    def __inserir_texto_minuta_real(self) -> MinutaWriteResult:
        raise NotImplementedError(
            "FASE 5B nao homologada: insercao real de texto no SEI esta bloqueada."
        )

    def __salvar_minuta_real(self) -> MinutaWriteResult:
        raise NotImplementedError(
            "FASE 5B nao homologada: salvamento real de minuta no SEI esta bloqueado."
        )


def _digits(value: str) -> str:
    return "".join(ch for ch in str(value) if ch.isdigit())
