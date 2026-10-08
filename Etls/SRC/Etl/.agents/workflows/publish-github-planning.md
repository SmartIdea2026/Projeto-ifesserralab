---
description: Publish backlog and sprint planning artifacts to GitHub using a 3-level planning model
---

# Publish GitHub Planning Workflow

Este workflow publica o planejamento local no GitHub sem criar duas fontes concorrentes de verdade.

## Objetivo

Sincronizar:

- Epics do backlog -> Epic issues
- User Stories -> User Story issues
- Tasks da sprint -> Task issues
- Sprint ativa -> Milestone ou Project Iteration, conforme o nivel adotado

## Regra principal

Este e o unico workflow publico para publicacao no GitHub.

Ele executa internamente duas fases:

1. `sync_backlog`
2. `sync_sprint`

Mesmo quando a intencao do usuario for "publicar apenas a sprint", a fase de backlog deve rodar primeiro para reconciliar o estado e evitar que a sprint referencie issues ausentes ou desatualizadas.

Para este workflow, a regra operacional e:

- um agente principal faz toda escrita local e remota de planning
- `explorer sidecars` podem ajudar apenas com leitura, inventario e verificacao
- `worker sidecars` nao devem escrever backlog, sprint, stories, tasks, contracts ou metadados remotos do GitHub neste fluxo

## Modelo operacional em 3 niveis

### Nivel 1 - Base

Use quando nao houver GitHub Project disponivel ou quando o repositorio for simples demais para justificar Project.

- Sprint: `Milestone`
- Tipagem: `labels`
- Hierarquia: `sub-issues`
- Labels recomendadas: `type:epic`, `type:user-story`, `type:task`

### Nivel 2 - Project pessoal

Use quando houver um user project ligado ao repositorio e o time quiser `Iteration`, sem depender de recursos organizacionais.

- Sprint: `Iteration`
- Milestone: opcional para entrega ou release
- Tipagem: `labels`
- Hierarquia: `sub-issues`
- Labels recomendadas: `type:epic`, `type:user-story`, `type:task`

### Nivel 3 - Organizacional

Use quando o time trabalhar em organization project com padrao compartilhado.

- Sprint: `Iteration`
- Milestone: opcional para entrega ou release
- Tipagem: `issue types`
- Hierarquia: `sub-issues`
- Labels complementares opcionais: `type:epic`, `type:user-story`, `type:task`

## Pre-requisitos

- `docs/product_backlog.md` atualizado
- `docs/project_manifest.md` atualizado com defaults de GitHub planning
- `docs/sprints/sprint_planning_NN.md` da sprint ativa atualizado
- `docs/stories/US-XXX.md` para as US relevantes
- `docs/tasks/breakdown_US-XXX.md` para as US da sprint que tenham tasks detalhadas
- Permissoes no GitHub para criar ou atualizar issues
- Permissoes para milestones se o nivel adotado usar `Milestone`
- Permissoes para project items se o nivel adotado usar `Project`
- Issue forms da `.github/ISSUE_TEMPLATE/` alinhados com a politica do repositorio quando houver criacao manual

## Fase 0 - Classificar o ambiente

Antes de publicar, identifique o nivel aplicavel.

Verifique:

- os defaults de `default_team`, `assignee_strategy` e `team_metadata_strategy` no manifesto
- os defaults de `milestone_auto_management`, `auto_managed_milestone_prefix` e `milestone_reopen_policy` no manifesto
- se existe GitHub Project para esse repositorio ou produto
- se a sprint sera controlada por `Milestone` ou `Iteration`
- se a tipagem sera feita por `labels` ou `issue types`
- se o projeto usa apenas board Kanban ou se tambem possui `Table`
- se a criacao manual via issue form esta usando templates genericos, sem time ou usuario hardcoded

Escolha:

1. `Nivel 1` quando nao houver Project disponivel ou desejado
2. `Nivel 2` quando houver user project simples com `Iteration`
3. `Nivel 3` quando houver organization project com padrao compartilhado

### Regra para Project template

Se existir GitHub Project, ele pode nascer de template Kanban, mas antes de publicar a sprint deve possuir pelo menos:

- uma view `Table` para backlog e sprint
- uma view `Board` para execucao diaria

`Roadmap` e opcional.

### Regra para milestone automation

Antes de publicar milestones:

- leia a estrategia de milestone do manifesto
- trate auto-close e auto-reopen como opt-in
- nao assuma que milestone opcional de `Nivel 2` ou `Nivel 3` deve ser auto-gerenciado
- mantenha a reconciliacao de milestones no agente principal

Default recomendado:

- `milestone_auto_management = opt_in_prefix`
- `auto_managed_milestone_prefix = Sprint:`
- `milestone_reopen_policy = auto_managed_only`

### Regra para issue forms

Se o repositorio usar issue forms:

- trate os forms como fallback manual
- nao use `assignees` hardcoded
- nao use labels de time ou pessoa
- mantenha foco em referencias aos artefatos locais
- nao use sidecars para editar templates de planning em paralelo com este workflow

### Regra para ownership e team

Resolva ownership antes de criar ou atualizar issues.

`assignee`:

1. usar owner explicito no artefato local, quando existir
2. se nao houver owner explicito, tentar `github.actor`
3. se o ator nao puder ser atribuido, deixar sem assignee

`team`:

1. usar team explicito no artefato local, quando existir
2. se nao houver, usar `default_team` do manifesto
3. se nao houver valor resolvido, nao gravar team metadata

Materializacao recomendada por nivel:

- `Nivel 1`: label opcional `team:<slug>`
- `Nivel 2`: label opcional `team:<slug>`
- `Nivel 3`: `issue field` ou campo de Project; label complementar apenas se o repositorio usar esse padrao

### Regra para delegacao leve

Se houver sidecars neste workflow:

- `explorer sidecars` podem validar backlog, sprint, links e consistencia
- o agente principal continua responsavel por atualizar arquivos locais e GitHub Issues/Projects
- nao distribua a escrita de `docs/product_backlog.md`, `docs/sprints/`, `docs/stories/`, `docs/tasks/` ou contratos governados

**Prompt sugerido:**
```text
Analise `docs/product_backlog.md`, a sprint ativa em `docs/sprints/`, os breakdowns de `docs/tasks/` e o contexto GitHub do repositorio.

Responda:
- Qual a sprint ativa?
- Quais Epics existem?
- Quais US existem por Epic?
- Quais US estao selecionadas para a sprint?
- Quais breakdowns ja possuem tasks detalhadas?
- O ambiente usa Nivel 1, Nivel 2 ou Nivel 3?
- O container da sprint sera Milestone, Iteration, ou Iteration com Milestone opcional?
```

## Fase 1 - Sync Backlog

### 1.1 Publicar Epics

Para cada Epic:

- criar issue se nao existir
- aplicar tipagem conforme o nivel:
  - `Nivel 1` e `Nivel 2`: label `type:epic`
  - `Nivel 3`: issue type `epic` e label complementar `type:epic` quando o repositorio adotar esse padrao
- resolver `assignee` e `team` conforme a regra do workflow
- atualizar issue existente se titulo ou descricao mudaram
- gravar o link da issue no backlog

### 1.2 Publicar User Stories

Para cada US:

- criar issue se nao existir
- aplicar tipagem conforme o nivel:
  - `Nivel 1` e `Nivel 2`: label `type:user-story`
  - `Nivel 3`: issue type `user-story` e label complementar `type:user-story` quando o repositorio adotar esse padrao
- resolver `assignee` e `team` conforme a regra do workflow
- atualizar issue existente se titulo, descricao ou acceptance criteria mudaram
- associar a US como sub-issue da Epic correspondente
- gravar o link da issue no backlog e na story

### 1.3 Validar hierarquia

Ao final da fase:

- toda US deve apontar para uma Epic
- toda issue de US deve apontar para sua Epic parent
- links devem estar refletidos de volta nos arquivos locais

## Fase 2 - Sync Sprint

### 2.1 Publicar container da sprint

Use o container conforme o nivel:

- `Nivel 1`: criar ou atualizar `Milestone` da sprint
- `Nivel 2`: associar a sprint a uma `Iteration`
- `Nivel 3`: associar a sprint a uma `Iteration`

Se o nivel for `Nivel 2` ou `Nivel 3`, `Milestone` e opcional e deve ser usado apenas para entrega, release ou marco maior.

Se houver auto-management de milestone:

- milestones de sprint auto-gerenciados devem seguir o prefixo definido no manifesto
- milestones de release ficam manuais por padrao, salvo opt-in explicito

Gravar o link do container da sprint em `docs/sprints/sprint_planning_NN.md`.

### 2.2 Associar US da sprint

Para cada US selecionada:

- garantir que a US issue ja exista
- associar a US ao container da sprint
- se houver milestone complementar, associar tambem
- gravar o link da US issue no arquivo de sprint

### 2.3 Publicar Tasks da sprint

Para cada task dos breakdowns das US selecionadas:

- criar ou atualizar issue
- aplicar tipagem conforme o nivel:
  - `Nivel 1` e `Nivel 2`: label `type:task`
  - `Nivel 3`: issue type `task` e label complementar `type:task` quando o repositorio adotar esse padrao
- resolver `assignee` e `team` conforme a regra do workflow
- associar a task como sub-issue da US correspondente
- associar a task ao mesmo container da sprint
- gravar o link da task issue no breakdown tecnico

## Fase 3 - Validacao final

Verifique:

- backlog local e GitHub estao coerentes
- toda Epic tem suas US
- toda US da sprint tem suas tasks
- toda US e task da sprint esta no container correto
- os links do GitHub voltaram para os arquivos locais
- o nivel adotado foi registrado no relatorio

## Regras de atualizacao

- Nao crie issue duplicada se ja existir link local valido
- Se houver divergencia entre arquivo local e issue remota, trate o arquivo local como fonte primaria e notifique o usuario para decisao
- Nao remova historico sem explicitar no relatorio
- Se uma US sair da sprint, remova sua associacao com o container atual, mas nao apague a issue
- Se o ambiente migrar de `Nivel 1` para `Nivel 2` ou `Nivel 3`, preserve os links existentes e apenas enriqueca a estrutura remota

## Outputs esperados

- Epics publicados como issues do GitHub
- User Stories publicadas como issues do GitHub
- Tasks da sprint publicadas como issues do GitHub
- Hierarquia `Epic -> US -> Task` refletida no GitHub
- Sprint ligada ao container correto do nivel adotado
- Links de issues e sprint gravados nos arquivos locais

## Dicas

- Comece pelo menor nivel que atenda o time
- Nao trate GitHub Project como obrigatorio
- Se houver Project, nao use apenas `Board`; mantenha tambem uma view `Table`
- Prefira `Milestone` para sprint apenas no `Nivel 1`
- Nao comece `/feature-development` antes de publicar a sprint no GitHub

## Consumo de Contexto (Estimado)

- Modo: [NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimizacao: [Breve descricao]

## Arquivos Utilizados

- Arquivos lidos para contexto: [...]
- Arquivos alterados: [...]
- Arquivos criados: [se houver]
- Leitura parcial relevante: [se aplicavel]
