"""Aula 4 · Exercício 2 — Avaliar o OpsPilot no golden dataset e aplicar o GATE.

Para cada caso de ``data/avaliacao/casos.jsonl``:
    1. roda a FSM com trace no Langfuse;
    2. aplica as regras determinísticas;
    3. pede nota ao LLM-juiz (fundamentação);
    4. envia os scores para o trace;
    5. no fim, gera ``workspace/relatorios/avaliacao.md`` e sai com código 1 se a
       nota geral ficar abaixo de ``--limite`` (é isso que reprova o PR no CI).

Como rodar::

    python -m aulas.aula4.a4_02_avaliar --limite 0.8
    python -m aulas.aula4.a4_02_avaliar --limite 0.8 --sem-juiz   # só regras (mais barato)
"""

from __future__ import annotations

import argparse
import sys
from statistics import mean

from langchain_core.messages import ToolMessage

from opspilot.avaliacao import avaliar_regras, carregar_casos, julgar_fundamentacao, salvar_relatorio
from opspilot.grafo import construir_grafo
from opspilot.observabilidade import finalizar, invocar_com_trace, registrar_nota
from opspilot.util import texto_de

PESO_JUIZ = 0.4  # 60% regras objetivas + 40% juiz


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limite", type=float, default=0.8, help="Nota mínima (0 a 1) para aprovar")
    parser.add_argument("--sem-juiz", action="store_true", help="Pula o LLM-as-a-judge")
    args = parser.parse_args()

    grafo = construir_grafo(aprovacao_humana=False)
    resultados = []

    try:
        for caso in carregar_casos():
            print(f"▶️  {caso.id}: {caso.pergunta[:70]}")
            saida = invocar_com_trace(
                grafo, caso.pergunta, nome=f"eval-{caso.id}", user_id="ci", tags=["eval"]
            )
            regras = avaliar_regras(caso, saida["resposta"], saida["estado"])
            nota_regras = mean(regras.values())
            resultado = {"id": caso.id, "regras": regras, "nota_regras": nota_regras, "trace_url": saida["trace_url"]}

            nota_final = nota_regras
            if not args.sem_juiz:
                evidencias = "\n".join(
                    texto_de(m) for m in saida["estado"]["messages"] if isinstance(m, ToolMessage)
                )
                juiz = julgar_fundamentacao(caso.pergunta, saida["resposta"], evidencias)
                resultado.update(nota_juiz=juiz.nota, justificativa_juiz=juiz.justificativa)
                nota_final = (1 - PESO_JUIZ) * nota_regras + PESO_JUIZ * (juiz.nota - 1) / 4
                registrar_nota(saida["trace_id"], "fundamentacao", juiz.nota, juiz.justificativa)

            for nome, valor in regras.items():
                registrar_nota(saida["trace_id"], nome, valor)
            resultado["nota_final"] = nota_final
            resultados.append(resultado)
            print(f"   regras={nota_regras:.2f} final={nota_final:.2f} {regras}")
    finally:
        finalizar()

    geral, md = salvar_relatorio(resultados, args.limite)
    print(f"\n📊 Nota geral: {geral:.2f} (limite {args.limite:.2f}) — relatório em {md}")
    return 0 if geral >= args.limite else 1


if __name__ == "__main__":
    sys.exit(main())
