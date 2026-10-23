"""Aula 4 · Exercício 1 — Rodar a FSM com tracing no Langfuse.

Pré-requisito: secrets ``LANGFUSE_PUBLIC_KEY``, ``LANGFUSE_SECRET_KEY`` e
``LANGFUSE_BASE_URL`` (ex.: https://us.cloud.langfuse.com) no Codespace.

Como rodar::

    python -m aulas.aula4.a4_01_tracing
    python -m aulas.aula4.a4_01_tracing "A fila de notificações está enorme"

Depois abra o link impresso e explore: árvore de nós do grafo, cada chamada ao
modelo (tokens, custo, latência) e cada ferramenta com entrada/saída.
"""

from __future__ import annotations

import sys

from opspilot.config import tem_langfuse
from opspilot.grafo import construir_grafo
from opspilot.observabilidade import finalizar, invocar_com_trace

def main() -> None:
    pergunta = " ".join(sys.argv[1:]) or "O checkout está lento e dando erro 503 desde as 18h."
    if not tem_langfuse():
        print("⚠️  Langfuse não configurado: vou rodar SEM trace. Veja o passo 4.1 do guia.\n")

    grafo = construir_grafo(aprovacao_humana=False)  # sem interrupt: execução de ponta a ponta
    try:
        saida = invocar_com_trace(
            grafo,
            pergunta,
            nome="opspilot-fsm",
            tags=["aula4", "demo"],
        )
    finally:
        finalizar()  # envia o buffer antes do script terminar

    print(saida["resposta"])
    if saida["trace_url"]:
        print(f"\n🔎 Trace: {saida['trace_url']}")


if __name__ == "__main__":
    main()
