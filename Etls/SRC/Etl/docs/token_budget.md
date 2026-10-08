# Token Budget — Política de Leitura de Contexto

Define quanto contexto carregar por tipo de tarefa.

Estes tres niveis (LIGHT/NORMAL/HEAVY CONTEXT) sao um eixo independente do Work Classification (`docs/work_classification.md`, LIGHT/NORMAL/HEAVY PROCESS): este arquivo decide quanto o agente le; aquele decide quanto processo de Discovery/Requirements a ideia do usuario percorre. Uma ideia HEAVY PROCESS pode ser implementada em modo LIGHT CONTEXT, e vice-versa.

---

## Modos de Operação

### 🟢 LIGHT CONTEXT — Tarefa simples e bem definida
**Exemplos:** corrigir um bug pontual, atualizar uma linha de template, criar um commit.

**Leia apenas:**
1. `docs/project_manifest.md`
2. O arquivo diretamente envolvido na tarefa

**Não leia:** README, backlog completo, sprints anteriores.

---

### 🟡 NORMAL CONTEXT — Tarefa de desenvolvimento padrão (US ou feature)
**Exemplos:** implementar uma user story, fazer code review, escrever testes.

**Leia:**
1. `docs/project_manifest.md`
2. `docs/sprints/sprint_planning_NN.md` (latest only)
3. `docs/stories/US-XXX.md` (story em foco)
4. `.agents/rules/coding-standards.md`

**Não leia:** sprints anteriores, todas as stories, README completo.

---

### 🔴 HEAVY CONTEXT — Planejamento ou decisão transversal
**Exemplos:** sprint planning, análise de exemplos Figma, decisão arquitetural, retrospectiva.

**Leia:**
1. `docs/project_manifest.md`
2. `docs/product_backlog.md`
3. `docs/sprints/sprint_planning_NN.md` (última sprint apenas)
4. `examples/figma/` (se existir e for relevante, pois normalmente só é importante no sprint_planning_01.md)
5. `docs/adr/` (se a tarefa envolver arquitetura)

---

## Regras Anti-Re-leitura

- **Não releia `README.md` durante operação** — use `project_manifest.md`
- **Não releia `AGENTS.md` uma vez que já foi processado na sessão**
- **Não leia sprints antigas** — leia apenas a sprint ativa
- **Não leia todos os templates** — leia apenas o que será usado
- **Prefira `context_summary.md` preenchido** a reler múltiplos arquivos
- **Não releia arquivos desnecessários** — Pare de ler arquivos adicionais assim que obtiver contexto suficiente.

## Limite por Tarefa (Guideline)

| Modo | Arquivos recomendados | Tokens estimados |
|---|---|---|
| LIGHT CONTEXT | ~2 | < 2k |
| NORMAL CONTEXT | ~4 | < 6k |
| HEAVY CONTEXT | ~6 | < 12k |

Esses valores são referências, não limites rígidos.

O agente pode expandir o contexto quando necessário,
mas deve sempre priorizar o menor contexto suficiente.
