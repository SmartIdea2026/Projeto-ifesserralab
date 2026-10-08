# Governance Changelog — ScrumAIDev

Referência de apoio para `AGENTS.md`. Não é leitura obrigatória em operação normal — consulte apenas quando precisar localizar onde um princípio é governado, ou entender a origem/motivo de uma das regras numeradas em `AGENTS.md` (Regras Globais).

Este arquivo foi extraído do `AGENTS.md` deliberadamente: `AGENTS.md` é lido em toda tarefa, mesmo classificada como LIGHT CONTEXT; este índice e este log são referência histórica/de apoio, não instrução operacional do dia a dia.

## Documentos de Governança (Índice)

| Documento | Governa |
|---|---|
| `AGENTS.md` | Regras operacionais do agente |
| `docs/definition_of_done.md` | Critérios de conclusão |
| `docs/decisoes_governanca_us_spec_bdd.md` | Regras de Spec, Contract e BDD |
| `docs/maturity_model.md` | Níveis 0-4 de rastreabilidade técnica |
| `docs/git_workflow.md` | Branch, commit, PR e merge |

## Log de Mudanças de Governança

Registro de alterações nas regras numeradas de `AGENTS.md` (Regras Globais), para auditoria.

| Data | Item | Mudança | Motivo |
|---|---|---|---|
| 2026-09-08 | Regra 14 | Adicionada: proibição de `Co-authored-by:` de IA em commits | Créditos de autoria em `main` devem ser humanos |
| 2026-09-08 | Regra 14 | Ajustada: exige trailer `Assisted-by:` no commit final de squash-merge | Registro mais durável que a descrição do PR, sem acionar semântica de coautoria do GitHub |
| 2026-09-08 | Regra 15 | Adicionada: marcador `[PRECISA CLARIFICAR]` com limite de 3 por story | Tornar ambiguidade explícita e auditável em vez de implícita na conversa |
| 2026-09-08 | Regra 16 | Adicionada: pasta `docs/templates_overrides/` para customização sem editar o canônico | Facilitar atualização do framework em projetos derivados sem conflito manual |
| 2026-09-17 | Regras 14-16 | Restauradas na distribuição instalável (0.1.0rc3), junto com a checagem de consistência do `/code-review`, a checagem de princípios do `/feature-development` e o ADR-001 | Essas regras existiam no snapshot fonte do framework mas não haviam sido incluídas no empacotamento em CLI (0.1.0rc1/rc2) |
| 2026-09-17 | Regras 17-21 | Adicionadas: `/scope-idea`, Work Classification (LIGHT/NORMAL/HEAVY), Discovery/Requirements com gates G0/G1 e Review & Adjust obrigatório | Preencher a fragilidade real da fase de investigação/requisitos do ScrumAIDev antes da User Story; ver `docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md` para a proveniência da ideia e o racional de nomenclatura |
| 2026-09-17 | Regras 14-21, Índice de Governança | Extraídos de `AGENTS.md` para este arquivo (`docs/governance_changelog.md`) | `AGENTS.md` é lido em toda tarefa (mesmo LIGHT CONTEXT); índice e log de auditoria não são operacionalmente necessários no dia a dia e só crescem com o tempo — mantê-los embutidos aumentava o piso de tokens de qualquer operação indefinidamente |
| 2026-09-17 | Regra 17, Regra 21, `docs/work_classification.md`, `docs/token_budget.md` | Renomeado LIGHT/NORMAL/HEAVY para LIGHT PROCESS/NORMAL PROCESS/HEAVY PROCESS (Work Classification) e LIGHT CONTEXT/NORMAL CONTEXT/HEAVY CONTEXT (Token Budget) | Os dois eixos usavam os mesmos três rótulos para conceitos diferentes (quantidade de processo da ideia vs. quantidade de contexto lido pelo agente), risco real de ambiguidade fora do documento de origem |
