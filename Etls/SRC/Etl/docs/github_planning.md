# GitHub Planning Model

Convencoes para publicar backlog e sprint no GitHub sem criar fonte dupla de verdade.

## Principio central

O repositorio continua sendo a fonte primaria de planejamento.

- `docs/product_backlog.md` define Epics e User Stories
- `docs/sprints/sprint_planning_NN.md` define a sprint ativa
- `docs/tasks/breakdown_US-XXX.md` define as tasks da US

GitHub funciona como projecao operacional sincronizada desses artefatos.

Os defaults operacionais de ownership e team devem ficar em `docs/project_manifest.md`, nao hardcoded nos issue forms.

## Modelo em 3 niveis

O processo deve se adaptar ao nivel de capacidade disponivel no GitHub. A hierarquia `Epic -> US -> Task` continua igual; o que muda e o container de sprint e a forma de tipagem.

| Nivel | Quando usar | Recursos GitHub | Sprint | Tipagem |
|---|---|---|---|---|
| Nivel 1 - Base | Repositorio sem GitHub Projects, repo pessoal simples, ou time sem acesso a Projects | Issues, labels, sub-issues, dependencies, milestones | `Milestone` | `labels` |
| Nivel 2 - Project pessoal | Repo pessoal ou time pequeno que quer views e iteration, mas sem recursos organizacionais | Nivel 1 + user project ligado ao repositorio + iteration | `Iteration` | `labels` |
| Nivel 3 - Organizacional | Time com GitHub Projects organizacional, governanca compartilhada e padrao entre repositorios | Nivel 2 + issue types, project template e campos organizacionais | `Iteration` | `issue types` + labels complementares |

## Mapeamento por nivel

### Nivel 1 - Base

- `Epic` = issue com label `type:epic`
- `US` = issue com label `type:user-story`
- `Task` = issue com label `type:task`
- `Sprint` = `Milestone`

Esse e o fallback minimo e deve funcionar bem para dono do repositorio ou colaborador com permissao para gerenciar issues e milestones.

### Nivel 2 - Project pessoal

- `Epic` = issue com label `type:epic`
- `US` = issue com label `type:user-story`
- `Task` = issue com label `type:task`
- `Sprint` = `Iteration` no user project
- `Milestone` = opcional, use para entrega ou release da sprint

Esse nivel e o melhor padrao para repositorios pessoais que querem quadro de sprint sem depender de recursos organizacionais.

### Nivel 3 - Organizacional

- `Epic` = issue type `epic`
- `US` = issue type `user-story`
- `Task` = issue type `task`
- `Sprint` = `Iteration` no organization project
- `Milestone` = opcional, use para entrega, release ou marco maior

Use labels namespaced como `type:epic`, `type:user-story` e `type:task` como complemento para filtros operacionais, nao como substituto da tipagem principal.

## Hierarquia

```text
EPIC
`-- US
    `-- Task
```

No GitHub, a hierarquia deve ser refletida com sub-issues:

- `Epic -> US`
- `US -> Task`

## Regra de escolha do nivel

Antes de publicar, classifique o ambiente:

1. Se nao houver GitHub Project disponivel ou o time nao quiser manter um, use `Nivel 1`.
2. Se houver GitHub Project em conta pessoal ou projeto simples ligado ao repositorio, use `Nivel 2`.
3. Se houver GitHub Project organizacional com issue types e template compartilhado, use `Nivel 3`.

O workflow deve declarar no relatorio qual nivel foi usado.

## Regra de sincronizacao

Use um unico workflow publico: `/publish-github-planning`.

Ele possui duas fases internas:

1. **Sync backlog**
   - cria ou atualiza Epic issues
   - cria ou atualiza US issues
   - amarra `Epic -> US`
   - grava os links das issues de volta nos arquivos locais

2. **Sync sprint**
   - identifica a sprint ativa
   - usa o container da sprint conforme o nivel adotado
   - associa as US da sprint ao container correto
   - cria ou atualiza Task issues para as US selecionadas
   - amarra `US -> Task`
   - grava os links da sprint e das task issues de volta nos arquivos locais

## Como evitar backlog desatualizado

O workflow de sprint nunca deve assumir que o backlog ja esta publicado.

Por isso, o comando publico sempre executa primeiro a fase de backlog e so depois a fase de sprint.

Se o backlog nao mudou, a fase de backlog deve apenas reconciliar o estado e seguir em frente.

## Papel do GitHub Project

GitHub Project e recomendado, mas nao obrigatorio.

- No `Nivel 1`, o processo continua funcional sem Project.
- No `Nivel 2`, use Project para planejar sprint com `Iteration`.
- No `Nivel 3`, use Project como padrao do time.

## Papel dos issue forms

Os arquivos em `.github/ISSUE_TEMPLATE/` devem servir como fallback manual e nao como fonte primaria de planejamento.

Regras:

- nao hardcode `assignees`
- nao hardcode labels de time, squad ou pessoa
- use labels genericas e portaveis, como `type:epic`, `type:user-story` e `type:task`
- mantenha os forms curtos, com foco em referencia aos artefatos locais
- se o ambiente usar `issue type` ou `issue fields`, complete isso no sidebar ou por automacao apos a criacao da issue

## Defaults de ownership e team

Os defaults de ownership devem ser resolvidos a partir do manifesto do projeto e do contexto de execucao.

Regras:

- `default_team` deve viver em `docs/project_manifest.md`
- `assignee` nao deve ser hardcoded no template YAML
- `team` nao deve ser hardcoded no template YAML

Ordem recomendada para `assignee`:

1. owner explicito no artefato local
2. `github.actor`, quando a automacao estiver rodando e o usuario puder ser atribuido
3. nenhum assignee

Ordem recomendada para `team`:

1. valor explicito no artefato local, quando existir
2. `default_team` do manifesto
3. nenhum team metadata

Forma de materializar `team` por nivel:

- `Nivel 1`: label opcional `team:<slug>`
- `Nivel 2`: label opcional `team:<slug>`
- `Nivel 3`: `issue field` ou campo de Project; label `team:<slug>` apenas como complemento se o repositorio adotar esse padrao

Se a automacao precisar atualizar configuracoes de GitHub planning, ela deve primeiro verificar o manifesto e o usuario em execucao antes de propor ou aplicar defaults.

## Politica de milestone automation

Milestone automation deve respeitar o papel semantico do milestone em cada nivel.

Regras:

- em `Nivel 1`, milestone pode ser o container da sprint e pode ser auto-gerenciado
- em `Nivel 2` e `Nivel 3`, milestone continua opcional e deve ser tratado como entrega ou release por padrao
- milestones de release nao devem ser auto-fechados ou reabertos sem opt-in explicito

Defaults recomendados no manifesto:

- `milestone_auto_management = opt_in_prefix`
- `auto_managed_milestone_prefix = Sprint:`
- `milestone_reopen_policy = auto_managed_only`

Com esse default:

- milestones com prefixo `Sprint:` podem ser auto-fechados quando nao houver mais itens abertos
- milestones sem esse prefixo ficam sob controle manual
- reabertura automatica vale apenas para milestones auto-gerenciados

O workflow `.github/workflows/close-milestone.yml` deve consumir esses defaults e ignorar milestones fora da politica de auto-management.

## Papel do template Kanban

O template de Kanban pode ser um bom ponto de partida, mas nao deve ser a unica estrutura do projeto.

Recomendacao:

- `Table` = visao canonica de backlog e sprint
- `Board` = execucao diaria em estilo Kanban
- `Roadmap` = opcional para releases e marcos maiores

Se o Project nascer de um template Kanban, ajuste-o para incluir pelo menos uma view de `Table` antes de usa-lo como fonte operacional.

## O que pode ser editado direto no GitHub

Pode ser editado diretamente no GitHub:

- status
- assignees
- comentarios
- dependencias
- links de PR

Nao deve virar fonte primaria no GitHub:

- nome oficial da US
- criterios de aceite
- composicao da sprint
- estrutura `Epic -> US -> Task`

Esses pontos devem nascer ou ser consolidados primeiro nos artefatos locais.

## Momento correto do workflow

Fluxo recomendado:

1. Refinar backlog
2. Executar `/sprint-planning`
3. Executar `/publish-github-planning`
4. Iniciar `/feature-development`

Nao inicie desenvolvimento de sprint sem que as US da sprint e suas task issues estejam publicadas e vinculadas.

## Campos minimos a registrar nos arquivos

- Link da Epic issue no backlog
- Link da US issue no backlog, na story e na sprint
- Link do container da sprint no GitHub
- Link das task issues no breakdown tecnico
- Nivel de publicacao adotado, quando necessario

## Recomendacao final

Adote o nivel mais simples que resolva o contexto atual:

- Comece em `Nivel 1` se o repositorio nao usa Projects.
- Suba para `Nivel 2` quando quiser iteration e views operacionais em repo pessoal.
- Suba para `Nivel 3` quando houver padrao organizacional entre times ou repositorios.

O processo deve evoluir sem quebrar a rastreabilidade ja existente.
