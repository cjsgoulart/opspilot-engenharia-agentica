# Aula 4 · Avaliação & Deploy

**Resultado:** repositório pronto para o dia a dia — observável, avaliado e com gate de CI.

| Passo | Arquivo | Lacunas |
|---|---|---|
| 1. Tracing | `opspilot/observabilidade.py` | concluído |
| 2. Regras determinísticas | `opspilot/avaliacao.py` | A4-L3 |
| 3. LLM-as-a-judge | `opspilot/avaliacao.py` | A4-L4 |
| 4. Scores no trace | `opspilot/observabilidade.py` | concluído |
| 5. Gate de CI | `.github/workflows/agentic-ci.yml` | A4-L6 |

```bash
make aula4               # imprime o link do trace no Langfuse
make avaliar             # golden dataset + juiz + gate (sai com código 1 se reprovar)
git add -A && git commit -m "OpsPilot completo" && git push
```

**Checkpoint:** a aba *Actions* do seu fork mostra `agentic-ci` verde e o relatório no *Summary*.

Com as credenciais configuradas, o trace registra a pergunta, a resposta e as
chamadas ao modelo/ferramentas. Não inclua segredos nem dados pessoais nos
prompts; sem credenciais do Langfuse, o agente continua funcionando sem tracing.
