---
description: Entende o problema e delimita o MVP antes de transformar a ideia em requisitos
---

# Discover Workflow

## Objetivo

Transformar uma ideia bruta em **entendimento compartilhado e editavel do problema**, usando um unico artefato de Discovery.

## Pre-condicao

- Work Classification NORMAL PROCESS ou HEAVY PROCESS; ou invocacao explicita do usuario.

## Passo 1 — Ler contexto minimo

- `docs/project_manifest.md`
- descricao do usuario
- `docs/work_classification.md`
- fontes explicitamente relevantes (codigo/design/documentos), somente quando necessarias

## Passo 2 — Analisar internamente

Consolide no minimo:
- Intent
- Problem
- Users/stakeholders relevantes
- Current Situation
- Desired Outcome
- Success Criteria
- Scope: IN / OUT / LATER
- Constraints/Feasibility
- Assumptions
- Risks
- Open Questions

HEAVY PROCESS aprofunda esses itens; NORMAL PROCESS permanece compacto.

## Passo 3 — Perguntas

Nao transforme o fluxo em entrevista longa.

- Pergunte somente o que muda escopo, valor, restricao critica ou criterio de sucesso.
- NORMAL PROCESS: priorize ate 3 perguntas bloqueantes por rodada.
- HEAVY PROCESS: pode fazer nova rodada quando respostas revelarem risco/contradicao relevante.
- Se algo puder permanecer como assumption nao bloqueante, registre como `[ASSUMPTION]` em vez de interromper.

## Passo 4 — Gerar proposta DRAFT

Crie/atualize `docs/discovery/<slug>.md` a partir de `templates/discovery.md`.

Nao marque `PROBLEM READY` ainda.

## Passo 5 — CHECKPOINT D1: REVIEW & ADJUST

Apresente ao usuario o conteudo proposto de forma legivel, incluindo:
- problema;
- resultado desejado;
- IN / OUT / LATER;
- criterios de sucesso;
- restricoes;
- assumptions;
- decisoes importantes.

Diga explicitamente:

```text
Esta e uma proposta editavel. Voce pode:
- aprovar;
- alterar qualquer secao;
- adicionar/remover item;
- mover item entre IN/OUT/LATER;
- corrigir assumptions;
- responder perguntas pendentes.
```

Aceite ajustes em linguagem natural. Aplique-os no arquivo e mostre um resumo das alteracoes.

## Passo 6 — Gate G0: PROBLEM READY

Somente marque `Status: PROBLEM_READY` quando:
- nenhuma pergunta bloqueante permanecer;
- o usuario tiver revisado a proposta;
- ajustes tiverem sido incorporados;
- o usuario tiver aprovado explicitamente.

## Proximo passo

NORMAL PROCESS/HEAVY PROCESS → `/requirements`.

Inclua `Consumo de Contexto (Estimado)` conforme `docs/token_budget.md`.
