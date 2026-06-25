"""Agente 19 flutuante: ícone sempre-no-topo que abre um chat (FASE 38).

Quando o usuário já está logado no SEI (login manual, na página oficial), este
ícone fica flutuando na tela. Ao clicar, abre um chat com o Agente 19. O usuário
manda o número do processo e cola o conteúdo; o agente analisa, resume, acha
prazos, sugere o tipo de documento e gera um rascunho — além de um resumo para
WhatsApp/Telegram. O agente NUNCA assina, envia ou tramita.

A interface é fina: toda a lógica vive em `agent_chat.AgentChatController`. O
Tkinter é importado de forma tardia para não ser dependência do CI headless.
"""

from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.core.safety import assert_safe_environment
from app.desktop.agent_chat import AgentChatController


SECURITY_NOTICE = (
    "Login feito por você na página oficial do SEI. O Agente 19 não captura "
    "senha nem sessão e não assina/envia."
)


class FloatingAgentApp:
    """Janela flutuante + chat. GUI fina sobre o controlador."""

    def __init__(self, controller: AgentChatController | None = None) -> None:
        import tkinter as tk

        self.tk = tk
        self.controller = controller or AgentChatController()
        self.chat_window: Any | None = None
        self.transcript: Any | None = None
        self.entry: Any | None = None
        self._drag = (0, 0)
        self._moved = False

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self._posicionar_canto()

        self.badge = tk.Label(
            self.root,
            text="🤖 19",
            bg="#1f6f5b",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=14,
            pady=10,
            cursor="hand2",
        )
        self.badge.pack()
        self.badge.bind("<ButtonPress-1>", self._press)
        self.badge.bind("<B1-Motion>", self._drag_move)
        self.badge.bind("<ButtonRelease-1>", self._release)
        self.badge.bind("<Button-3>", lambda _e: self.root.destroy())  # botão direito fecha

    # --- posicionamento / arrasto -------------------------------------------

    def _posicionar_canto(self) -> None:
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw - 120}+{sh - 140}")

    def _press(self, event: Any) -> None:
        self._drag = (event.x, event.y)
        self._moved = False

    def _drag_move(self, event: Any) -> None:
        self._moved = True
        x = self.root.winfo_x() + event.x - self._drag[0]
        y = self.root.winfo_y() + event.y - self._drag[1]
        self.root.geometry(f"+{x}+{y}")

    def _release(self, _event: Any) -> None:
        if not self._moved:
            self._toggle_chat()

    # --- chat ----------------------------------------------------------------

    def _toggle_chat(self) -> None:
        if self.chat_window is not None and self.chat_window.winfo_exists():
            self.chat_window.destroy()
            self.chat_window = None
            return
        self._abrir_chat()

    def _abrir_chat(self) -> None:
        tk = self.tk
        from tkinter import scrolledtext

        win = tk.Toplevel(self.root)
        win.title("Agente 19")
        win.attributes("-topmost", True)
        win.geometry("520x620")
        self.chat_window = win

        tk.Message(
            win, text=SECURITY_NOTICE, width=480, bg="#fff6db", fg="#3b3425", padx=10, pady=8
        ).pack(fill="x", padx=8, pady=(8, 4))

        self.transcript = scrolledtext.ScrolledText(win, wrap="word", state="disabled")
        self.transcript.pack(fill="both", expand=True, padx=8, pady=4)

        bottom = tk.Frame(win)
        bottom.pack(fill="x", padx=8, pady=(0, 8))
        self.entry = tk.Entry(bottom)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda _e: self._enviar())
        tk.Button(bottom, text="Enviar", command=self._enviar).pack(side="left", padx=(6, 0))

        self._mostrar(self.controller.saudacao().text)

    def _enviar(self) -> None:
        if self.entry is None:
            return
        mensagem = self.entry.get().strip()
        if not mensagem:
            return
        self.entry.delete(0, "end")
        self._mostrar(mensagem, autor="Você")
        for reply in self.controller.responder(mensagem):
            self._mostrar(reply.text)

    def _mostrar(self, texto: str, autor: str = "Agente 19") -> None:
        if self.transcript is None:
            return
        self.transcript.configure(state="normal")
        self.transcript.insert("end", f"{autor}: {texto}\n\n")
        self.transcript.configure(state="disabled")
        self.transcript.see("end")

    def mainloop(self) -> None:
        self.root.mainloop()


def run() -> None:
    """Sobe o ambiente seguro e abre o ícone flutuante do Agente 19."""
    settings = get_settings()
    assert_safe_environment(settings)
    from app.storage.db import init_db

    init_db()

    # Leitura automática (Frente 2): ligada ao chat, porém gated. Com a flag
    # desligada ou seletores não homologados, o leitor devolve um status que o
    # chat usa para pedir o texto colado — inerte até a homologação.
    from app.sei.process_reader import read_current_process

    controller = AgentChatController(ler_processo=lambda numero: read_current_process(numero))
    FloatingAgentApp(controller).mainloop()


if __name__ == "__main__":
    run()
