---
description: Entrada inteligente do ScrumAIDev - classifica o trabalho e ativa somente o processo necessario
---

# Scope Idea Workflow

## Objetivo

Ser a **entrada publica preferencial para uma ideia ou mudanca ainda nao classificada**. O usuario pode fornecer uma ideia em linguagem natural sem conhecer os workflows internos.

Este workflow nao substitui `/init-project`: `/init-project` prepara a estrutura de um projeto novo uma unica vez; `/scope-idea` roda a cada ideia/mudanca nova ao longo da vida do projeto.

Exemplo:

```text
/scope-idea Quero um sistema para acompanhar a evolucao de agentes de IA.
```

## Principio

> Mais inteligencia interna, menos comandos para o usuario.

O agente orquestra `classify → discover → requirements → create-user-story` somente quando necessario.

## Passo 1 — Ler contexto minimo

1. `docs/project_manifest.md`
2. `AGENTS.md`
3. `docs/work_classification.md`
4. descricao fornecida pelo usuario

Nao leia o repositorio inteiro.

## Passo 2 — Recomendar Work Classification

Escolha o menor processo suficiente:

- **LIGHT PROCESS** — objetivo ja claro, mudanca pequena/localizada/baixo risco.
- **NORMAL PROCESS** — feature/mudanca delimitada que precisa de entendimento antes de Stories.
- **HEAVY PROCESS** — iniciativa ampla/nova, alto risco, multiplos stakeholders/boundaries/seguranca/incerteza relevante.

Mostre:

```text
Classificacao de Processo recomendada: NORMAL PROCESS
Motivo: ...
Processo ativado: Discovery compacto → Requirements → Stories.
```

### CHECKPOINT C0 — REVIEW & ADJUST

Antes de executar, permita:
- Aprovar;
- Alterar classificacao;
- Pedir explicacao.

Nunca trate a classificacao da IA como decisao final sem dar possibilidade de ajuste.

## Passo 3 — Roteamento

### LIGHT PROCESS

Nao crie Discovery/Requirements formais por padrao.

Se a tarefa estiver clara:

```text
execute → validate
```

Se surgir ambiguidade bloqueante, promova para NORMAL PROCESS e explique por que.

### NORMAL PROCESS

Execute internamente:

```text
/discover → review/adjust → /requirements → review/adjust → /create-user-story (Passo 0 - Modo Backlog) → review/adjust
```

Prefira artefatos compactos e no maximo 3 perguntas bloqueantes por checkpoint antes de consolidar uma proposta.

### HEAVY PROCESS

Execute a mesma experiencia publica, mas aprofunde internamente:
- stakeholders/context;
- feasibility/constraints;
- riscos/assumptions;
- success criteria;
- requisitos nas seis dimensoes definidas em `docs/discovery_requirements.md`.

Nao multiplique comandos nem documentos apenas por ser HEAVY PROCESS.

## Passo 4 — Encaminhamento

Depois das Stories aprovadas:
- atualizar backlog quando aplicavel;
- sugerir o primeiro vertical slice;
- perguntar se o usuario deseja iniciar `/sprint-planning`.

## Saida

O usuario deve perceber um fluxo conversacional curto:

```text
Ideia
 ↓
Classificacao proposta (editavel)
 ↓
Discovery proposto (editavel)
 ↓
Requirements propostos (editaveis)
 ↓
Stories propostas (editaveis)
 ↓
Sprint Planning
```

Inclua `Consumo de Contexto (Estimado)` conforme `docs/token_budget.md`.
