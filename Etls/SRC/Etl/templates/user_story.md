# User Story: [US-XXX] [Titulo Descritivo]

**Epic:** [Nome do Epic relacionado]
**GitHub Epic Issue:** [#123 | URL | -]
**GitHub US Issue:** [#234 | URL | -]
**Prioridade:** [Alta/Media/Baixa]
**Story Points:** [Pontos estimados]
**Sprint:** [Numero da sprint]
**Status:** [Backlog/To Do/In Progress/Review/Done]
**Behavior Change Esperado:** [YES/NO]

---

## Historia

**Como** [tipo de usuario]
**Eu quero** [realizar alguma acao]
**Para que** [alcancar algum beneficio/valor]

### Contexto Adicional

[Forneca contexto adicional sobre o problema ou necessidade que esta historia resolve]

### Pontos de Esclarecimento

Marque incertezas explicitamente em vez de assumir — maximo de 3 por story. Resolva todas antes de iniciar a implementacao.

- [ ] [PRECISA CLARIFICAR: pergunta especifica]

Se nao houver incerteza, remova esta subsecao ou registre "Nenhum ponto pendente".

---

## Criterios de Aceitacao

- [ ] **Criterio 1:** [Descricao especifica e testavel]
- [ ] **Criterio 2:** [Descricao especifica e testavel]
- [ ] **Criterio 3:** [Descricao especifica e testavel]
- [ ] **Criterio 4:** [Descricao especifica e testavel]

---

## Governanca e Rastreabilidade

- **Nivel ScrumAIDev:** [0 | 1 | 2 | 3 | 4]
- **Justificativa do nivel:** [Menor nivel suficiente para esta story]
- **US exige Spec governada?** [Sim/Nao]
- **Justificativa da Spec:** [Explique por que a story exige ou nao uma Spec tecnica]
- **Spec prevista:** [docs/specs/<nome>.yaml | N/A]
- **US exige Contract governado?** [Sim/Nao]
- **Justificativa do Contract:** [Explique por que a story exige ou nao um Contract]
- **Contract previsto:** [docs/contracts/<nome>.yaml | N/A]
- **Padrao de erro aplicavel:** [docs/contracts/error_standard.yaml | N/A]
- **BDD previsto:** [docs/bdd/<nome>.feature | N/A]
- **Gates opcionais aplicaveis:** [validate-contract | test-contract | test-bdd | test-mock | N/A]
- **Touch List preliminar:** [Arquivos/pastas que devem ser alterados ou N/A]
- **Task Issues previstas:** [#345, #346 ou N/A]

---

## Mockups/Wireframes

[Cole imagens, links para Figma, ou desenhos de interface se aplicavel]

---

## Notas Tecnicas

### Arquitetura

- **Componentes afetados:** [Lista de componentes/modulos]
- **APIs necessarias:** [Endpoints ou integracoes]
- **Database changes:** [Migracoes ou novos modelos]
- **Referencias do modelo de dados:** [database/... ou N/A]
- **Erros observaveis esperados:** [Lista de codes e cenarios ou N/A]

### Dependencias

- [ ] [Dependencia 1]
- [ ] [Dependencia 2]

### Consideracoes de Performance

- [Pontos de atencao relacionados a performance]

---

## Plano de Testes

### Testes Unitarios

- [ ] [Cenario de teste 1]
- [ ] [Cenario de teste 2]

### Testes de Integracao

- [ ] [Cenario de teste 1]
- [ ] [Cenario de teste 2]

### Testes de Contract

- [ ] [Exemplo de request/response validado ou N/A]
- [ ] [Erros observaveis validados ou N/A]

### Testes Manuais

- [ ] [Cenario de teste 1]
- [ ] [Cenario de teste 2]

### BDD / Cenarios de Comportamento

- [ ] [Cenario BDD 1 ou N/A]
- [ ] [Cenario BDD 2 ou N/A]

---

## Tasks (Breakdown)

- [ ] **[TASK-001]** [Nome da task]
  - GitHub Task Issue: [#345 | URL | N/A]
  - Estimativa: [horas]
  - Assignee: [nome]
- [ ] **[TASK-002]** [Nome da task]
  - GitHub Task Issue: [#346 | URL | N/A]
  - Estimativa: [horas]
  - Assignee: [nome]
- [ ] **[TASK-003]** [Nome da task]
  - GitHub Task Issue: [#347 | URL | N/A]
  - Estimativa: [horas]
  - Assignee: [nome]

---

## IA Insights

### Sugestoes de Implementacao

[Sugestoes geradas por IA sobre como implementar esta feature]

### Riscos Identificados

[Riscos tecnicos ou de negocio identificados pela IA]

### Alternativas Consideradas

[Outras abordagens sugeridas pela IA]

---

## Notas e Comentarios

[Espaco para discussoes, decisoes e anotacoes durante o desenvolvimento]

---

## Definition of Done Checklist

- [ ] Codigo implementado conforme criterios de aceitacao
- [ ] Decisao sobre Spec governada foi registrada
- [ ] Decisao sobre Contract governado foi registrada
- [ ] Nivel ScrumAIDev foi registrado
- [ ] Spec, Contract e BDD foram atualizados quando aplicavel
- [ ] Gates opcionais executados ou dispensados com justificativa
- [ ] Error handling observavel segue o padrao compartilhado quando aplicavel
- [ ] Code review aprovado
- [ ] Testes unitarios com cobertura adequada
- [ ] Testes de integracao e contract passando
- [ ] Documentacao atualizada
- [ ] Build/CI passando
- [ ] `Behavior change` documentado no PR
- [ ] Aprovacao do Product Owner
