# User Story: US-003 Carga e Normalização do Horizon (researchers_canonical)

**Epic:** Cruzamento Extensão ↔ Horizon
**GitHub Epic Issue:** -
**GitHub US Issue:** -
**Prioridade:** Alta
**Story Points:** 2
**Sprint:** -
**Status:** Done (aprovada pela usuária em 2026-09-24)
**Behavior Change Esperado:** NO (módulo novo)

---

## Historia

**Como** analista de dados do ifes-serra-lab,
**Eu quero** carregar ` bases/horizon/researchers_canonical.parquet` (10.089 registros) com `classification`, `campus` (parse do JSON serializado) e `cnpq_url` normalizados,
**Para que** a base de pesquisa esteja pronta para o cruzamento 1:1 com a extensão.

### Contexto Adicional

Regra BR04: o cruzamento usa exclusivamente o parquet canônico (união exata dos 4 subconjuntos — 2.472 + 6.519 + 849 + 249 = 10.089). A coluna `classification` replica a categorização dos subconjuntos (`researcher`/`student`/`outside_ifes`/null), dispensando qualquer leitura adicional. Unicidade de `name` já confirmada: 10.089/10.089.

### Pontos de Esclarecimento

Nenhum ponto pendente (decisões registradas no Discovery G0 e Requirements G1).

---

## Criterios de Aceitacao

- [x] **Criterio 1:** O parquet é lido integralmente (10.089 linhas) e qualquer outra fonte do Horizon é ignorada (BR04).
- [x] **Criterio 2:** Unicidade de `name`/slug validada em runtime; slug duplicado gera erro explícito. *(Ajuste 2026-09-24: detectado 1 registro com `name='-'` na linha 1631 — dado lixo contado como válido pela análise consolidada; tratado como inválido e reportado.)*
- [x] **Criterio 3:** `campus` (string JSON `{"id": <int>, "name": "<str>"}`) é parseado e persistido como apenas o `name` (ex.: `"Serra"`); campus ausente → `null`.
- [x] **Criterio 4:** `classification` com `NaN` é persistido como `null` (política C3); nos 10.088 registros válidos: 248 com `null` (o registro inválido também era NaN).
- [x] **Criterio 5:** Campos preservados no registro: `nome` (name), `classification`, `campus`, `cnpq_url`, `was_student`, `was_staff`; demais colunas do parquet são ignoradas (out of scope).
- [x] **Criterio 6:** Todos os nomes passam pela mesma função de normalização da US-001.
- [x] **Criterio 7:** *(novo, 2026-09-24)* `carregar_horizon()` é fail-fast por padrão (raise em nome inválido) e com `ignorar_invalidos=True` retorna `(10.088 pessoas válidas, 1 registro inválido reportado)` — universos e auditoria da US-004 usam os válidos.

---

## Governanca e Rastreabilidade

- **Nivel ScrumAIDev:** 1
- **Justificativa do nivel:** Comportamento observável por contagens validáveis, sem boundary técnico.
- **US exige Spec governada?** Nao
- **Justificativa da Spec:** Carga de dado local com validação por contagens; sem API/evento.
- **Spec prevista:** N/A
- **US exige Contract governado?** Nao
- **Justificativa do Contract:** Sem boundary de runtime.
- **Contract previsto:** N/A
- **Padrao de erro aplicavel:** N/A
- **BDD previsto:** N/A
- **Gates opcionais aplicaveis:** N/A
- **Touch List preliminar:** `database/extracao_horizon.py` (novo), `database/tests/test_extracao_horizon.py` (novo)
- **Task Issues previstas:** N/A

---

## Mockups/Wireframes

N/A (pipeline de dados).

---

## Notas Tecnicas

### Arquitetura

- **Componentes afetados:** novo módulo `database/extracao_horizon.py`.
- **APIs necessarias:** Nenhuma.
- **Database changes:** Nenhum (leitura de parquet).
- **Referencias do modelo de dados:** Schema do bloco `horizon` aprovado no C3 (Requirements, Estrutura de Saída).
- **Erros observaveis esperados:** slug duplicado → erro explícito; `campus` malformado → erro apontando a linha.

### Dependencias

- [ ] US-001 (funções de normalização).
- [ ] venv com pandas/pyarrow (aprovado no C1).

### Consideracoes de Performance

10k linhas — leitura trivial com pandas/pyarrow.

---

## Plano de Testes

### Testes Unitarios

- [ ] Parse de `campus` serializado (`{"id": 6, "name": "Serra"}` → `"Serra"`).
- [ ] `classification` NaN → `null`.

### Testes de Integracao

- [ ] Execução sobre o parquet real: 10.089 linhas, 0 slugs duplicados, distribuição de `classification` igual a {student: 6519, researcher: 2472, outside_ifes: 849, null: 249}.

### Testes de Contract

- [ ] N/A.

### Testes Manuais

- [ ] Inspeção de um registro no console.

### BDD / Cenarios de Comportamento

- [ ] N/A.

---

## Tasks (Breakdown)

- [ ] **[TASK-001]** Leitor do parquet com seleção de colunas
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir
- [ ] **[TASK-002]** Parses de `campus`/`classification` + normalização de nomes + testes
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir

---

## IA Insights

### Sugestoes de Implementacao

Ler apenas as colunas necessárias (`columns=` no `read_parquet`); validar a distribuição de `classification` contra os valores esperados como sanity check de integridade.

### Riscos Identificados

Atualização futura do parquet pode mudar a distribuição — desvios aparecem nos testes de integração e no `resumo_auditoria.json` (US-004).

### Alternativas Consideradas

Unir os 4 subconjuntos manualmente (rejeitado — BR04; o canônico já é a união exata e tem `classification`).

---

## Notas e Comentarios

**Execução (2026-09-24, via `/feature-development`):**
- Implementação: `database/extracao_horizon.py` (leitura com `columns=` das 6 colunas, `parse_campus` puro, import tardio de pandas, `(validos, invalidos)` com fail-fast padrão) e testes em `database/tests/test_extracao_horizon.py`.
- Desvio detectado pelo teste de integração: registro `name='-'` (linha 1631; classification/campus/cnpq NaN; was_student/was_staff False) — a análise consolidada o contava como nome válido. Usuária aprovou: pular com contagem explícita na auditoria (universo válido 10.088; exclusivos_horizon baseline 9.690 → 9.689; baseline 399 inalterado).
- Testes: 38/38 OK no venv do projeto (`database/.venv`): `database/.venv/bin/python -m unittest discover -s database/tests -t .`
- Branch/commit/PR: N/A — sem git.
- Breakdown: `docs/tasks/breakdown_US-003.md` (tasks Done).

---

## Definition of Done Checklist

- [x] Codigo implementado conforme criterios de aceitacao
- [x] Decisao sobre Spec governada foi registrada (Não)
- [x] Decisao sobre Contract governado foi registrada (Não)
- [x] Nivel ScrumAIDev foi registrado (1)
- [x] Spec, Contract e BDD foram atualizados quando aplicavel (N/A)
- [x] Gates opcionais executados ou dispensados com justificativa (N/A)
- [x] Error handling observavel segue o padrao compartilhado quando aplicavel (N/A — erros internos explícitos)
- [x] Code review aprovado (review IA no desenvolvimento; aprovação da usuária em 2026-09-24)
- [x] Testes unitarios com cobertura adequada (fixtures + integração real; suíte 38/38)
- [x] Testes de integracao e contract passando (integração com base real)
- [x] Documentacao atualizada
- [x] Build/CI passando (N/A — sem CI no nível 1)
- [x] `Behavior change` documentado (NO; N/A PR — sem git)
- [x] Aprovacao do Product Owner (2026-09-24)
