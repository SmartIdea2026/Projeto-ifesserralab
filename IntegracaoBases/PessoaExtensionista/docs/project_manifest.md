# Project Manifest

**Framework:** ScrumAIDev
**Status do projeto:** DEFINED
**Projeto atual:** Cruzamento de Bases ifes-serra-lab (Extensão ↔ Horizon)
**Origem do contexto:** usuário (bases do ifes-serra-lab; backlog manual)
**Confiança do contexto:** alta
**Contexto processado:** sim
**Estado operacional:** Sprint 01 ativa (2026-09-24 a 2026-10-01) — backlog gerado, 4 US planejadas
**Última atualização:** 2026-09-24 (docs/sprints/sprint_planning_01.md)

## GitHub Planning Defaults

- `default_team`: `project_team`
- `assignee_strategy`: `artifact_owner_then_github_actor_then_none`
- `team_metadata_strategy`: `project_field_then_label_then_none`
- `type_label_strategy`: `type:epic`, `type:user-story`, `type:task`
- `milestone_auto_management`: `opt_in_prefix`
- `auto_managed_milestone_prefix`: `Sprint:`
- `milestone_reopen_policy`: `auto_managed_only`

## Framework Maturity Defaults

- `agileaidev_level`: `0`
- `spec_bdd_governance`: `available`
- `contract_first`: `docs_only`
- `contract_validation`: `not_configured`
- `contract_test_runner`: `not_configured`
- `bdd_runner`: `manual_review`
- `mock_strategy`: `not_configured`
- `type_generation`: `not_configured`
- `ci_contract_gates`: `optional_noop`
- `frontend_stack`: `undefined`
- `backend_stack`: `undefined`
- `database_stack`: `undefined`

## Agent Delegation Defaults

- `delegation_mode`: `principal_agent_with_sidecars`
- `explorer_policy`: `read_only_parallel_allowed`
- `worker_policy`: `exclusive_write_scope_only`
- `canonical_artifacts_policy`: `single_writer`
- `delegation_rollout_stage`: `pilot`
- `handoff_artifact`: `templates/context_summary.md`

## Leitura Inicial do Agente

| Arquivo | Ler quando |
|---|---|
| Este arquivo | Primeira leitura da sessão ou quando o contexto for incerto |
| `AGENTS.md` | Antes de qualquer ação |
| `docs/maturity_model.md` | Ao decidir quanto de Spec, Contract, BDD, mocks e CI ativar |
| `docs/sprints/sprint_planning_NN.md` | Quando existir sprint ativa |
| `docs/product_backlog.md` | Ao planejar, priorizar ou continuar desenvolvimento |

**Não leia `README.md` para operar.** Ele é voltado a humanos e onboarding.

## Estrutura Operacional

```text
.agents/rules/       → padrões de código (leia ao gerar código)
.agents/skills/      → personas (use quando o workflow pedir)
.agents/workflows/   → processos (ativados por /slash-command)
templates/           → referência para criação de artefatos
docs/                → artefatos gerados (consulte, não reescreva sem necessidade)
docs/maturity_model.md → niveis 0-4 de adocao progressiva
examples/figma/      → insumos de análise (priorizar no /sprint-planning)
```


## Regras de Interpretação
Este repositório é a base do **framework ScrumAIDev**, mas este manifesto descreve o estado do **projeto derivado** que será iniciado a partir do framework.
Se Status do projeto = **UNDEFINED**, o projeto derivado ainda não foi formalmente consolidado; isso é esperado enquanto o framework está sendo refinado ou antes do primeiro `/init-project` de um produto real.
Se "Contexto processado" = sim:
- NÃO reanalizar automaticamente os insumos em examples/figma/
- Utilizar o backlog como fonte principal
Se "Contexto processado" = não:
- Permitir análise dos insumos para geração inicial do backlog
- Nesse caso, o próximo passo recomendado é /sprint-planning.
Se "Contexto processado" = parcial:
- Permitir reanálise controlada para refinamento
O nome do projeto derivado pode ser inferido provisoriamente a partir dos insumos encontrados e consolidado depois.
Após o primeiro /sprint-planning de um projeto derivado, atualizar este manifesto com nome, origem, confiança e novo estado.

## Estado Atual do Projeto

- Sprint ativa: **Sprint 01** (2026-09-24 a 2026-10-01) — EPIC-001 completo, 10 pts
- Backlog: **gerado** (`docs/product_backlog.md` — EPIC-001, 4 US)
- Próximo passo sugerido: executar US-001 (primeira story da Sprint 01, via `/feature-development`)

> Atualize apenas ao final de cada sprint ou mudança relevante. Evite atualizações desnecessárias.
