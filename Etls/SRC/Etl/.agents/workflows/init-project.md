---
description: Guia de instalação e bootstrap do framework ScrumAIDev em um novo projeto
---

# Init Project Workflow

## Objetivo

Este workflow atua como **gateway de contexto do projeto**.

Ele deve:
- Detectar o estado atual do repositório
- Interpretar corretamente o `project_manifest.md`
- Identificar se o projeto é novo ou já está em andamento
- Priorizar insumos corretos (especialmente `examples/figma/`)
- Recomendar o próximo workflow adequado
- Inicializar a estrutura mínima de projeto derivado de forma idempotente, sem assumir stack quando ela ainda nao estiver definida

❗ NÃO executar ações prematuras (como gerar README ou backlog) sem diagnóstico.

---

## 🔷 BLOCO 1 — Leitura obrigatória (State Entry)

Antes de qualquer ação, o agente deve:

### 1. Ler fonte primária de contexto
- `docs/project_manifest.md` (OBRIGATÓRIO)

### 2. Ler regras do sistema
- `AGENTS.md`

---

## 🔷 BLOCO 2 — Diagnóstico estrutural do repositório

O agente deve verificar:

### 🔹 Estrutura de processo
- Existe `docs/`?
- Existe `docs/product_backlog.md`?
- Existem arquivos `docs/sprints/sprint_planning_*.md`?
- Existem stories `docs/stories/US-*.md`?
- Existe `docs/maturity_model.md`?
- Existem contratos em `docs/contracts/*.yaml`?
- Ha runners reais para `validate-contract`, `test-contract`, `test-bdd` ou `test-mock`?

### 🔹 Insumos de produto (PRIORIDADE MÁXIMA)

Verificar `examples/figma/`:

- Existe `examples/figma/`?
- Existem arquivos `.zip`, imagens, PDFs ou protótipos?
- O conteúdo parece representar um sistema/produto?

⚠️ Regra crítica:

> Se existir `.zip` em `examples/figma/`, considerar como **insumo prioritário de contexto**.


#### Contexto adicional
- Existem arquivos relevantes (código, documentos)?
- README existe? (NÃO usar como fonte principal)

---

## 🔷 BLOCO 3 — Interpretação do estado (State Detection)

O agente deve combinar:

- `Status do projeto` (no `project_manifest.md`)
- `agileaidev_level` e capacidades registradas no `project_manifest.md`
- Presença de backlog/sprints
- Presença de insumos em `examples/figma/`

---
O agente deve classificar o projeto em um dos estados:

### 🔹 Estado 1 — DESIGN_DRIVEN_NEW_PROJECT

Condições:

- `Status do projeto = UNDEFINED`
- Existe `.zip` ou insumos relevantes em `examples/figma/`
- NÃO existe `docs/product_backlog.md`
- NÃO existem arquivos `docs/sprints/sprint_planning_*.md`

👉 Interpretação:

Projeto novo orientado por design (Figma-first)

---

### 🔹 Estado 2 — EMPTY_PROJECT

Condições:

- `Status do projeto = UNDEFINED`
- NÃO existe `examples/figma/` com conteúdo útil
- NÃO existe backlog
- NÃO existem arquivos `docs/sprints/sprint_planning_*.md`

---

### 🔹 Estado 3 — STRUCTURED_NO_SPRINT

Condições:

- Existe `docs/product_backlog.md`
- NÃO existem arquivos `docs/sprints/sprint_planning_*.md`

---

### 🔹 Estado 4 — ACTIVE_SPRINT

Condições:

- Existem arquivos `docs/sprints/sprint_planning_*.md`

---


## 🔷 BLOCO 4 — Decisão e encaminhamento

---

### 🔹 Caso: DESIGN_DRIVEN_NEW_PROJECT
Ação:

- NÃO gerar README ainda
- NÃO criar backlog manualmente
- NÃO alterar estrutura prematuramente
- **AVALIAÇÃO DE CÓDIGO FONTE DO FIGMA:** Se o ZIP descompactado do Figma contiver uma base de código funcional (ex: pasta `src/`, `package.json`, rotas configuradas), a prioridade absoluta será **cópia integral do frontend exportado** para a estrutura alvo do repositório, ajustando apenas o necessário para rodar localmente e integrar com o restante do projeto.
- **PARIDADE VISUAL COMO DEFAULT:** Se o ZIP do Figma já contiver telas/componentes navegáveis, a interpretação padrão do projeto deve ser reproduzir a interface com fidelidade visual máxima. Simplificações visuais, placeholders ou redesigns só podem ocorrer com decisão explícita registrada nos artefatos seguintes.
- **MODO DE ADOÇÃO OBRIGATÓRIO:** Registrar já no diagnóstico qual destes modos se aplica:
  - `copia_integral_frontend`
- **REGRA DEFAULT E OBRIGATÓRIA:** Se o ZIP trouxer um app navegável completo, o modo deve ser `copia_integral_frontend`.
- **ALTERAÇÕES POSTERIORES SÓ COM ANUÊNCIA:** Qualquer simplificação, redesign ou mudança relevante da interface copiada do ZIP só pode ocorrer em etapa posterior com anuência explícita do usuário registrada nos artefatos.

Saída:

> Projeto novo baseado em design identificado.  
> Insumos (e possível código-fonte) encontrados em `examples/figma/`.  
> Próximo passo recomendado: `/sprint-planning` (com foco em confirmar `copia_integral_frontend` como estratégia padrão e mapear apenas os ajustes necessários para o frontend exportado entrar no repositório).

---

### 🔹 Caso: EMPTY_PROJECT

Ação:

- Criar estrutura mínima idempotente, sem sobrescrever artefatos preenchidos:
  - `docs/`
  - `docs/sprints/`
  - `docs/stories/`
  - `docs/tasks/`
  - `docs/retrospectives/`
  - `docs/specs/`
  - `docs/contracts/`
  - `docs/bdd/`
  - `frontend/` somente quando houver UI, ZIP Figma funcional ou decisão explícita de stack frontend
  - `backend/` somente quando houver servidor customizado ou decisão explícita de stack backend
  - `database/` somente quando houver migrations, schemas, storage local ou decisão explícita de persistência

Saída:

> Projeto vazio detectado.  
> Estrutura mínima criada.  
> Próximo passo: fornecer insumos (ex: examples/figma/) OU criar um backlog inicial e executar `/sprint-planning`.


---

### 🔹 Caso: STRUCTURED_NO_SPRINT

Saída:

> Backlog identificado, mas nenhuma sprint iniciada.  
> Próximo passo recomendado: `/sprint-planning`

---

### 🔹 Caso: ACTIVE_SPRINT

Ação:

- Identificar sprint atual
- Verificar progresso
- Identificar pendências
- Identificar riscos

Saída:

- resumo da sprint
- stories pendentes
- riscos e bloqueadores
- próximos passos sugeridos

---

### 🔹 Caso: EXISTING_PROJECT_NO_PROCESS

Ação:

- Analisar arquivos existentes
- Inferir objetivo do sistema
- NÃO estruturar docs automaticamente ainda

Saída:

> Projeto existente sem processo estruturado identificado.  
> Recomenda-se estruturar documentação caso necessário e iniciar `/sprint-planning`.

---

## 🔷 BLOCO 5 — Regras fundamentais

- NÃO usar `README.md` como fonte principal
- SEMPRE priorizar `project_manifest.md`
- Se existir `figma.zip` e NÃO houver backlog/sprint, ele tem prioridade como fonte de contexto
- NÃO gerar README antes de entender o domínio do sistema
- NÃO gerar backlog sem insumos suficientes
- NÃO assumir que ausência de docs significa ausência de contexto
- NÃO criar `frontend/`, `backend/` ou `database/` automaticamente quando a stack ainda nao estiver definida
- Se o trabalho atual for refinamento do framework ScrumAIDev, não altere `Status do projeto = UNDEFINED` apenas para "resolver" o manifesto
- Nao promova o projeto para Nivel 3 ou 4 sem comandos reais registrados em `docs/context.md`
- Nao criar `contracts/`, mocks, fixtures, tipos gerados, Docker ou CI acoplado a stack no framework base; esses artefatos pertencem ao projeto derivado quando a stack pedir

---

## 🔷 BLOCO 6 — Formato padrão de saída

O agente deve SEMPRE responder neste formato:
## Diagnóstico do Projeto
Estado: [CLASSIFICAÇÃO]

## Nome e Objetivo (se inferível)
- Nome: ...
- Objetivo: ...

## Estratégia de Adoção do Figma
- ZIP contém frontend funcional? [sim/não]
- Modo recomendado: `copia_integral_frontend`
- Justificativa: ...

## Nivel ScrumAIDev e Capacidades
- Nivel atual: [0 | 1 | 2 | 3 | 4]
- Contract-first: [none | docs_only | executable | ci_enforced]
- BDD runner: [manual_review | configured]
- Contract validator/test runner: [not_configured | configured]
- Mock/type generation: [not_configured | configured]
- Proxima evolucao recomendada: ...

## Evidências
- ...
- ...

## Resumo do Contexto
- ...

## Situação Atual
- Sprint atual: ...
- Backlog: ...
- Próximas histórias (se existirem): ...

## Riscos e Bloqueadores
- ...

## Próximo Passo Recomendado
/comando

## Consumo de Contexto (Estimado)
- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimização: [Breve descrição]

## Arquivos Utilizados
- Arquivos lidos para contexto: [...]
- Arquivos alterados: [se houver]
- Arquivos criados: [se houver]
- Leitura parcial relevante: [se aplicável]

---

## 🔷 Objetivo final

Garantir que:

- O agente entenda o contexto antes de agir
- O início do projeto seja consistente
- O uso de tokens seja otimizado
- O backlog seja gerado com base em insumos reais
- O README seja gerado apenas após entendimento adequado do sistema

---
