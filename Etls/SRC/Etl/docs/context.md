# Context

Documento central para identificadores, caminhos e comandos operacionais do repositorio e dos projetos derivados.

## 1. Identificadores e Rastreabilidade

- `US-XX`: User Story de valor e negocio no backlog de produto.
- `F-001`, `B-001`, `R-001`, `T-001`: tarefas tecnicas, bugs, refactors ou tarefas genericas quando o projeto adotar esse nivel de granularidade.
- Specs podem nascer de uma US ou de uma decisao tecnica; quando nascerem de uma US, devem apontar para `US-XX`.
- Contracts podem nascer de uma US ou de uma decisao tecnica; quando nascerem de uma US, devem apontar para `US-XX`.

## 2. Caminhos Operacionais

- `docs/decisoes_governanca_us_spec_bdd.md`: regra canonica de US, Spec, Contract e BDD.
- `docs/maturity_model.md`: niveis 0-4 de adocao progressiva do framework.
- `docs/contracts/`: contratos governados em YAML para boundaries observaveis.
- `docs/contracts/contract_governance.md`: convencoes de contract-first por boundary.
- `docs/contracts/adapters.md`: adaptadores opcionais de contrato por stack.
- `docs/contracts/error_standard.yaml`: modelo padrao de erros compartilhado.
- `docs/github_planning.md`: convencoes de sincronizacao entre backlog local, sprint e GitHub Issues/Projects.
- `docs/git_workflow.md`: regra canonica de branch, commit, PR e merge.
- `docs/definition_of_done.md`: checklist final de conclusao.
- `docs/product_backlog.md`: backlog do produto quando o projeto estiver inicializado.
- `docs/todo.md`: backlog tecnico e tarefas operacionais.
- `docs/tasks/`: breakdowns tecnicos por User Story e rastreabilidade de execucao.
- `docs/specs/`: specs governadas e specs curtas.
- `docs/bdd/`: cenarios de comportamento.
- `docs/assumptions.md`: assumptions e decisoes ainda nao consolidadas.
- `templates/context_summary.md`: handoff curto para retomada de contexto e delegacao leve.
- `docs/templates_overrides/<nome>.md`: customizacao de um template especifico sem editar o canonico em `templates/` (ver regra 16 do `AGENTS.md`).
- `docs/sprints/`: planejamentos de sprint, usando `sprint_planning_NN.md`.
- `docs/stories/`: User Stories refinadas, usando `US-XXX.md` ou `US-XXX_titulo.md`.
- `docs/retrospectives/`: retrospectivas de sprint, usando `sprint_NN_retro.md`.

## 2.1. Bootstrap de Projeto Derivado

O ScrumAIDev é instanciado em um projeto (novo ou existente) via `scrumaidev config --harness opencode` (CLI instalável) e, quando a estrutura de pastas ainda não existir, seguido de `/init-project`.

Enquanto nenhuma stack de produto existir, checks locais devem se comportar por deteccao de capacidades: se nao houver `frontend/`, `backend/`, `database/` ou runner configurado, o gate deve explicar que ainda nao se aplica e retornar sucesso.

O `/init-project` deve ser idempotente e seguro. Em um projeto recem-configurado, ele deve diagnosticar primeiro e so entao inicializar a estrutura do projeto derivado. Ele nao deve sobrescrever artefatos preenchidos sem confirmacao.

Estrutura operacional recomendada para projetos derivados:

- `docs/sprints/`
- `docs/stories/`
- `docs/tasks/`
- `docs/retrospectives/`
- `docs/specs/`
- `docs/contracts/`
- `docs/bdd/`
- `frontend/` quando houver interface de cliente ou ZIP Figma funcional
- `backend/` quando houver servidor customizado
- `database/` quando houver migrations, schemas ou storage local

## 2.2. Niveis de Adoção do Framework

Use `docs/maturity_model.md` para decidir o menor nivel suficiente:

- Nivel 0: processo agil, agentes e templates.
- Nivel 1: Spec, BDD e Definition of Done governados.
- Nivel 2: Contract-first documentado em `docs/contracts/`.
- Nivel 3: validacao executavel de contratos/BDD quando a stack tiver runner.
- Nivel 4: CI, mocks, geracao de tipos e testes de contrato automatizados.

O projeto derivado deve registrar o nivel atual e as capacidades no `docs/project_manifest.md`. Niveis 3 e 4 exigem comando real documentado neste arquivo; caso contrario, os gates devem retornar sucesso com mensagem explicita.

## 3. Delegacao e Handoff

Modelo recomendado:

- um agente principal coordena o fluxo e integra o resultado final
- `explorer sidecars` podem ler em paralelo
- `worker sidecars` so podem escrever com write scope exclusivo

Artefatos canonicos com single writer:

- `docs/project_manifest.md`
- `docs/product_backlog.md`
- `docs/sprints/`
- `docs/stories/`
- `docs/tasks/`
- `docs/specs/`
- `docs/contracts/`
- `docs/bdd/`
- `.agents/workflows/`

Antes de delegar:

- registrar objetivo curto do sidecar
- definir write scope explicito
- registrar artefatos protegidos
- preencher ou atualizar `templates/context_summary.md` quando o handoff for relevante

Use paralelismo principalmente para:

- exploracao de codigo
- investigacao tecnica
- revisao especializada
- implementacao em escopos claramente separados

Evite delegacao para:

- tarefas pequenas ou sequenciais
- escrita concorrente em artefato canonico
- sincronizacao de backlog, sprint e contratos governados

## 4. Checks Locais

Todos os projetos derivados devem expor no root, diretamente ou por delegacao no `Makefile`:

```bash
make lint
make test
make typecheck
make build
make validate-contract
make test-contract
make test-bdd
make test-mock
```

Antes de a stack existir, esses targets podem retornar sucesso com mensagem explicita. Quando a stack existir, os targets devem delegar para a ferramenta real do projeto conforme arquivos detectados:

```bash
make lint
make test
make typecheck
make build
```

Exemplos de delegacao possivel:

```bash
npm --prefix frontend run lint
pnpm --dir frontend run test
yarn --cwd frontend run typecheck
make -C backend test
```

Os targets podem apenas delegar para a ferramenta real do projeto (`npm`, `pnpm`, `uv`, `poetry`, `pytest`, `ruff`, `mypy`, etc.). Quando um gate nao existir para a stack atual, o target deve explicar isso e retornar sucesso.

Gates opcionais para rastreabilidade tecnica:

```bash
make validate-contract  # lint/validacao dos contratos quando houver validador
make test-contract      # testes provedor/consumidor quando houver runner
make test-bdd           # runner BDD quando houver automacao
make test-mock          # testes com mocks/fixtures quando a stack usar essa camada
make test-all           # agrega gates padrao e opcionais
```

Quando o projeto adotar BDD executavel, documente tambem aqui o comando do runner, por exemplo:

```bash
npx cucumber-js docs/bdd
behave docs/bdd
npx playwright test --grep @bdd
```

Quando o projeto adotar validacao automatica de contratos, documente tambem aqui o comando do validador, por exemplo:

```bash
spectral lint docs/contracts/*.yaml
npx @redocly/cli lint docs/contracts/*.yaml
```

Estado atual dos cenarios em `docs/bdd/`: usados como rastreabilidade e revisao de comportamento; runner dedicado de BDD ainda nao foi configurado.

## 5. Regra para Projetos sem um Gate

Se um gate nao se aplicar ao projeto, o target ainda deve existir e retornar sucesso com mensagem explicita.

## 6. Referencias Rapidas

- Para branch, commit, PR e merge, consulte `docs/git_workflow.md`.
- Para decidir se a US exige Spec, Contract e quando BDD e obrigatorio, consulte `docs/decisoes_governanca_us_spec_bdd.md`.
- Para decidir o nivel 0-4 adequado, consulte `docs/maturity_model.md`.
- Para estruturar contratos e mensagens de erro, consulte `docs/contracts/contract_governance.md`.
- Para escolher adaptadores executaveis sem acoplar stack ao framework, consulte `docs/contracts/adapters.md`.
- Para publicar planejamento em Issues, Iterations e Milestones do GitHub, consulte `docs/github_planning.md`.
- Para retomada de contexto e handoff entre agente principal e sidecars, consulte `templates/context_summary.md`.
