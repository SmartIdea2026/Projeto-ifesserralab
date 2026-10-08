# Task Breakdown: [US-XXX] [Nome da User Story]

**Data:** [Data do breakdown]
**Participantes:** [Desenvolvedores envolvidos]
**Estimativa total:** [Horas/Story Points]
**Nivel ScrumAIDev:** [0 | 1 | 2 | 3 | 4]
**Spec governada:** [docs/specs/<nome>.yaml | N/A]
**Contract governado:** [docs/contracts/<nome>.yaml | N/A]
**Padrao de erro:** [docs/contracts/error_standard.yaml | N/A]
**BDD associado:** [docs/bdd/<nome>.feature | N/A]
**Behavior change:** [YES/NO]
**GitHub Epic Issue:** [#123 | URL | -]
**GitHub Parent US Issue:** [#234 | URL | -]
**GitHub Sprint Container:** [Iteration URL | Milestone URL | -]

---

## Pre-Flight de Governanca

- **US exige Spec governada?** [Sim/Nao]
- **US exige Contract governado?** [Sim/Nao]
- **Justificativa do Nivel ScrumAIDev:** [Menor nivel suficiente e limites de automacao]
- **Justificativa:** [Resumo curto]
- **Touch List aplicavel:** [Arquivos/pastas permitidos ou N/A]
- **Runner BDD a executar:** [Comando ou N/A]
- **Validacao de contrato a executar:** [Comando ou N/A]
- **Teste de contrato a executar:** [Comando ou N/A]
- **Teste de mock a executar:** [Comando ou N/A]

---

## Checagem de Principios (condicional)

Preencha esta secao **apenas se** pelo menos uma condicao for verdadeira: Nivel ScrumAIDev 2, 3 ou 4; `Behavior change` = YES; ou Estimativa total > 8 pontos. Caso contrario, registre "Nao aplicavel" e siga direto para Tasks Tecnicas — este passo existe para pegar decisao arquitetural arriscada antes do codigo, nao para todo breakdown pequeno.

- [ ] Esta e a abordagem mais simples que atende a User Story? Se nao, justifique na tabela abaixo.
- [ ] A abordagem esta alinhada com `docs/definition_of_done.md` e com as regras de `AGENTS.md`?
- [ ] Nenhuma dependencia externa nova esta sendo introduzida sem aprovacao (regra 6 do `AGENTS.md`)?
- [ ] O escopo respeita a Touch List quando houver Spec governada?

**Complexidade Aceita** (preencha apenas se algum item acima precisar de excecao):

| Desvio | Por que e necessario | Alternativa mais simples rejeitada porque |
|---|---|---|
| [Ex: nova dependencia X] | [Motivo] | [Motivo da rejeicao] |

---

## Tasks Tecnicas

### Backend Tasks

#### [TASK-001] Contrato governado

- **Descricao:** Criar ou atualizar `docs/contracts/<nome>.yaml` antes da implementacao do boundary.
- **GitHub Task Issue:** [#345 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Dependencias:** [Lista de tasks que precisam ser completadas antes]
- **Criterios de conclusao:**
  - [ ] Contract alinhado com US, Spec e modelo de dados
  - [ ] Requests, responses e status codes definidos
  - [ ] Erros observaveis referenciam `docs/contracts/error_standard.yaml`

#### [TASK-002] Implementacao backend

- **Descricao:** [Descricao detalhada]
- **GitHub Task Issue:** [#346 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Dependencias:** [Lista de tasks que precisam ser completadas antes]
- **Criterios de conclusao:**
  - [ ] [Criterio 1]
  - [ ] [Criterio 2]

---

### Frontend Tasks

#### [TASK-003] Consumo do boundary

- **Descricao:** [Descricao detalhada]
- **GitHub Task Issue:** [#347 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Dependencias:** [Lista de tasks que precisam ser completadas antes]
- **Criterios de conclusao:**
  - [ ] Frontend alinhado ao Contract
  - [ ] Estados de erro observaveis renderizam mensagens especificas e seguras

---

### Testing Tasks

#### [TASK-004] Testes Unitarios

- **Descricao:** Implementar testes unitarios para [componente/funcao]
- **GitHub Task Issue:** [#348 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Cobertura esperada:** [%]
- **Criterios de conclusao:**
  - [ ] Testes de casos de sucesso
  - [ ] Testes de casos de erro
  - [ ] Testes de edge cases
  - [ ] Cobertura > 80%
  - [ ] Alinhamento com criterios de aceite e com a Spec quando existir

#### [TASK-005] Testes de Integracao e Contract

- **Descricao:** Implementar testes de integracao para [fluxo/API] e validar exemplos do Contract.
- **GitHub Task Issue:** [#349 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Criterios de conclusao:**
  - [ ] [Cenario 1]
  - [ ] [Cenario 2]
  - [ ] Requests e responses batem com o Contract
  - [ ] Runner BDD executado quando aplicavel

---

### Documentation Tasks

#### [TASK-006] Documentacao

- **Descricao:** Atualizar documentacao tecnica e de usuario
- **GitHub Task Issue:** [#350 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Criterios de conclusao:**
  - [ ] API docs atualizados
  - [ ] Spec, Contract e BDD atualizados quando aplicavel
  - [ ] Comentarios no codigo
  - [ ] User guide atualizado (se aplicavel)

---

### DevOps/Infrastructure Tasks

#### [TASK-007] [Nome da Task]

- **Descricao:** [Ex: Configurar CI/CD, migrations, validacao de contrato, etc.]
- **GitHub Task Issue:** [#351 | URL | -]
- **Estimativa:** [Horas]
- **Assignee:** [Nome]
- **Status:** [To Do/In Progress/Done]
- **Criterios de conclusao:**
  - [ ] [Criterio 1]
  - [ ] [Criterio 2]

---

## Ordem de Execucao Sugerida

1. **Fase 1 - Fundacao**
   - [ ] [TASK-001]
   - [ ] [TASK-002]

2. **Fase 2 - Implementacao**
   - [ ] [TASK-003]
   - [ ] [TASK-004]

3. **Fase 3 - Validacao**
   - [ ] [TASK-005]
   - [ ] [TASK-006]

4. **Fase 4 - Deploy**
   - [ ] [TASK-007]

---

## Timeline Estimado

| Fase | Tasks | Estimativa | Data Inicio | Data Fim |
|------|-------|------------|-------------|----------|
| Fase 1 | TASK-001, TASK-002 | [X horas] | [Data] | [Data] |
| Fase 2 | TASK-003, TASK-004 | [X horas] | [Data] | [Data] |
| Fase 3 | TASK-005, TASK-006 | [X horas] | [Data] | [Data] |
| Fase 4 | TASK-007 | [X horas] | [Data] | [Data] |

---

## Sugestoes IA

### Automacao Recomendada

- [Sugestoes de scripts ou automacoes que podem ajudar]

### Possiveis Bloqueadores

- [Riscos identificados pela IA que podem atrasar as tasks]

### Otimizacoes

- [Sugestoes de como otimizar o trabalho ou paralelizar tasks]

---

## Notas

[Anotacoes adicionais sobre o breakdown, decisoes tecnicas, etc.]
