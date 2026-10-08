---
description: Deriva requisitos estruturados de um Discovery aprovado e permite revisao/edicao antes de Stories
---

# Requirements Workflow

## Objetivo

Transformar um problema aprovado em requisitos suficientes para orientar Stories sem pular direto para solucao tecnica.

## Pre-condicao

Preferencialmente, Discovery com `PROBLEM_READY`.

Se nao existir e o trabalho for NORMAL PROCESS/HEAVY PROCESS, recomende `/discover` antes de prosseguir.

## Passo 1 — Ler somente

- Discovery aprovado;
- `docs/discovery_requirements.md`;
- contexto tecnico estritamente necessario quando brownfield.

## Passo 2 — Completeness Scan

Analise seis perspectivas:

1. Functional requirements
2. Non-functional requirements
3. User scenarios / edge/error cases
4. Business/domain context e rules
5. Technical context / constraints / integration points
6. Quality attributes relevantes

Nao force requisito em uma categoria quando ela nao se aplica.

## Passo 3 — Clarificacao adaptativa

- Extraia primeiro tudo que ja esta conhecido.
- Pergunte somente lacunas relevantes.
- NORMAL PROCESS: ate 3 perguntas bloqueantes por rodada.
- HEAVY PROCESS: aprofunde ambiguidade, contradicoes e riscos quando necessario.
- Nao invente resposta para lacuna bloqueante.

## Passo 4 — Gerar proposta DRAFT

Crie/atualize `docs/requirements/<slug>.md` com IDs estaveis:
- FRxx
- BRxx
- NFRxx
- Axx para assumptions, quando necessario.

Inclua key decisions propostas.

## Passo 5 — CHECKPOINT R1: REVIEW & ADJUST

Nunca responda apenas:

> Derivei 7 FR, 5 BR e 3 NFR. Posso prosseguir?

Em vez disso:

1. informe as contagens;
2. destaque decisoes importantes;
3. **mostre a proposta completa de requisitos** (ou secoes em blocos legiveis quando longa);
4. indique o arquivo salvo;
5. permita ao usuario:
   - editar texto;
   - adicionar requisito;
   - remover requisito;
   - reclassificar FR ↔ BR ↔ NFR;
   - dividir/unir requisito;
   - alterar prioridade/escopo;
   - corrigir assumption;
6. aplique os ajustes;
7. mostre resumo/diff das mudancas.

Exemplo:

```text
Derivei 7 FR, 5 BR e 3 NFR.
Decisao importante proposta: criar uma versao nao altera automaticamente a versao estavel.

A proposta completa esta abaixo e em docs/requirements/agent-evolution.md.
Voce pode aprovar, editar, adicionar, remover ou reclassificar qualquer item.
```

## Passo 6 — Gate G1: REQUIREMENTS READY

Somente marque `REQUIREMENTS_READY` quando:
- perguntas bloqueantes resolvidas;
- inconsistencias relevantes resolvidas;
- usuario revisou/ajustou a proposta;
- usuario aprovou explicitamente.

## Proximo passo

`/create-user-story` — Passo 0 (Modo Backlog) transforma os requisitos aprovados em Stories.

Inclua `Consumo de Contexto (Estimado)` conforme `docs/token_budget.md`.
