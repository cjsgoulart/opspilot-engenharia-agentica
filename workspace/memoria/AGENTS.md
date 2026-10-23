# Memória longa do OpsPilot (AGENTS.md)

> Este arquivo é carregado no system prompt do Deep Agent a CADA execução
> (parâmetro `memory=["/memoria/AGENTS.md"]`). O próprio agente pode editá-lo
> para registrar aprendizados. Revise as mudanças no `git diff` como faria com
> um PR de um colega.

## Padrões da MercadoNimbus
- Fuso horário oficial dos relatórios: UTC (os logs já estão em UTC).
- Severidades: SEV1 = clientes sem conseguir comprar; SEV2 = degradação relevante; SEV3 = risco sem impacto.
- Toda afirmação em relatório precisa de evidência (métrica ou linha de log).

## Formato padrão de post-mortem (obrigatório)
```
# Post-mortem <ID> — <título>
## Resumo executivo (3 linhas, para diretoria)
## Linha do tempo (UTC)
## Causa raiz
## Evidências
## Sintomas e efeitos colaterais (o que NÃO era a causa)
## Mitigação aplicada / recomendada
## Ações de prevenção (com dono sugerido)
## Lições aprendidas
```

## Lições aprendidas (o agente acrescenta abaixo, 1 linha por lição)
- Fila de notificações crescendo costuma ser efeito colateral de retries da API produtora.
- Mudança recente na configuração do pool de banco é uma suspeita forte quando checkout passa a gerar PoolTimeout e 503 com CPU baixa na API.
- Antes de escalar checkout por 503 com CPU baixa, verifique o pool de conexões do banco e compare com o baseline configurado.
- Quando o checkout apresentar 503 com CPU baixa e `PoolTimeout`, valide primeiro o `DB_POOL_SIZE`/`conexoes_max_pool` do `pagamentos-db` antes de investigar deploy da API.
- Se o `checkout-api` estiver com CPU baixa e `PoolTimeout`, compare o pool do `pagamentos-db` com o baseline antes de escalar a API ou culpar o deploy.
- Redução recente do pool de conexões do banco pode ser a causa raiz de checkout 503 mesmo com CPU baixa na API; compare sempre com o baseline antes de concluir problema na aplicação.
- Quando houver `PoolTimeout` no checkout com CPU baixa, valide primeiro a configuração do pool da dependência (ex.: `DB_POOL_SIZE`/`default_pool_size`) antes de culpar o deploy da API.
