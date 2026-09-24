# Task Breakdown: US-003 Carga e Normalização do Horizon (researchers_canonical)

**Data:** 2026-09-24
**Participantes:** Usuária (PO/dev solo) + Agente IA (opencode)
**Estimativa total:** 4 horas / 2 story points
**Nivel ScrumAIDev:** 1
**Spec governada:** N/A
**Contract governado:** N/A
**Padrao de erro:** N/A (exceções Python explícitas; sem boundary externo)
**BDD associado:** N/A
**Behavior change:** NO
**GitHub Epic Issue:** -
**GitHub Parent US Issue:** -
**GitHub Sprint Container:** -

---

## Pre-Flight de Governanca

- **US exige Spec governada?** Nao
- **US exige Contract governado?** Nao
- **Justificativa do Nivel ScrumAIDev:** Carga de parquet local com validação por contagens/distribuição em teste de integração; sem API/UI/evento (regra 13 do AGENTS.md).
- **Justificativa:** Dispensas já registradas na story US-003, conforme `docs/decisoes_governanca_us_spec_bdd.md` (seções 1 e 2 — mudança puramente interna).
- **Touch List aplicavel:** `database/extracao_horizon.py` (novo), `database/tests/test_extracao_horizon.py` (novo), `database/.venv` (ambiente, NFR01), `docs/tasks/breakdown_US-003.md`, `docs/stories/US-003_carga_horizon_canonical.md`, `docs/product_backlog.md`
- **Runner BDD a executar:** N/A
- **Validacao de contrato a executar:** N/A
- **Teste de contrato a executar:** N/A
- **Teste de mock a executar:** N/A

---

## Checagem de Principios (condicional)

Nao aplicavel (Nível 1, behavior NO, 2 pontos ≤ 8).

---

## Tasks Tecnicas

### Backend Tasks

#### [TASK-001] Módulo de carga do Horizon

- **Descricao:** Criar `database/extracao_horizon.py`: `carregar_horizon(parquet, ignorar_invalidos=False)` lendo exclusivamente ` bases/horizon/researchers_canonical.parquet` (BR04) com `columns=` das 6 colunas do schema C3; parse de `campus` (JSON serializado → `name`), `classification`/`cnpq_url`/`was_student`/`was_staff` NaN → `null`; slug por `normalizar(nome)`; unicidade via `database/validacoes.py`; fail-fast padrão e retorno `(validos, invalidos)` com `ignorar_invalidos=True` (ajuste pós-desvio aprovado pela usuária); `parse_campus()` puro e testável; import de pandas tardio.
- **GitHub Task Issue:** -
- **Estimativa:** 1,5h (executado em ~2h com o desvio)
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Dependencias:** `database/caminhos.py` e `database/validacoes.py` (criados na US-002); venv com pandas/pyarrow
- **Criterios de conclusao:**
  - [x] Somente `researchers_canonical.parquet` (nenhum subconjunto/grafos — BR04)
  - [x] Distribuição de `classification` preservada nos válidos ({student: 6519, researcher: 2472, outside_ifes: 849, null: 248})
  - [x] Política de null: NaN → `null` em todos os campos previstos
  - [x] Registro inválido (`name='-'`) pulado e reportado quando `ignorar_invalidos=True`; fail-fast por padrão

---

### Testing Tasks

#### [TASK-002] Testes unitários e de integração

- **Descricao:** Criar `database/tests/test_extracao_horizon.py`: unitários de `parse_campus` (string JSON, dict, None/NaN, formato inesperado) + integração com o parquet real (10.088 válidos + 1 inválido, unicidade, distribuição, tipos dos campos, fail-fast padrão).
- **GitHub Task Issue:** -
- **Estimativa:** 1,5h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Cobertura esperada:** módulo coberto; integração valida baseline (BR05)
- **Criterios de conclusao:**
  - [x] Unitários verdes sem depender do parquet real
  - [x] Integração real: 10.088 válidos + 1 inválido, 0 slugs duplicados, distribuição igual ao baseline ajustado
  - [x] Suíte completa verde no venv do projeto (38/38)

---

### Documentation Tasks

#### [TASK-003] Rastreabilidade

- **Descricao:** Atualizar story US-003 (ACs, status), requisitos (FR03, baselines), backlog e breakdown.
- **GitHub Task Issue:** -
- **Estimativa:** 1h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Criterios de conclusao:**
  - [x] ACs com evidência dos testes
  - [x] Status no backlog atualizado (Review)
  - [x] FR03/baselines atualizados nos requisitos (10.088 válidos + 1 inválido)

---

## Ordem de Execucao Sugerida

1. **Fase 1 - Ambiente** — [x] venv `database/.venv` (criado junto à US-002)
2. **Fase 2 - Implementacao** — [x] TASK-001
3. **Fase 3 - Validacao** — [x] TASK-002
4. **Fase 4 - Rastreabilidade** — [x] TASK-003

---

## Timeline Estimado

| Fase | Tasks | Estimativa | Data |
|------|-------|------------|------|
| 1 | venv (US-002) | 0,5h | 2026-09-24 |
| 2 | TASK-001 | 1,5h | 2026-09-24 |
| 3 | TASK-002 | 1,5h | 2026-09-24 |
| 4 | TASK-003 | 0,5h | 2026-09-24 |

---

## Sugestoes IA

### Automacao Recomendada
- `setUpClass` para carregar o parquet real uma única vez nos testes de integração (aplicado).

### Possiveis Bloqueadores
- ~~Divergência da distribuição de `classification`~~ **RESOLVIDO (2026-09-24):** registro lixo `name='-'` (linha 1631) identificado; usuária aprovou pular com reporte na auditoria (universo válido 10.088; distribuição dos válidos: null 248).

### Otimizacoes
- `read_parquet(columns=...)` para carregar apenas as 6 colunas do schema (aplicado).

---

## Notas

- **Desvio investigado (BR05):** `name='-'` (linha 1631, classification/campus/cnpq NaN, was_student/was_staff False) era contado como nome válido pela análise consolidada; usuário aprovou tratar como inválido + reporte.
- Delegação (Passo 0.5): execução local — mesma razão da US-002.
- Sem git: Passos 3/4 e 10–12 N/A (decisão da usuária).
- Colunas do parquet fora do schema C3 (`resume`, `google_scholar_url`, `citation_names`, `identification_id`, `birthday`, métricas, grafos) são ignoradas por design.
