# Task Breakdown: US-001 Módulo de Normalização de Nomes

**Data:** 2026-09-24
**Participantes:** Usuária (PO/dev solo) + Agente IA (opencode)
**Estimativa total:** 3 horas / 2 story points
**Nivel ScrumAIDev:** 1
**Spec governada:** N/A
**Contract governado:** N/A
**Padrao de erro:** N/A (erros internos via exceções Python explícitas; sem boundary externo)
**BDD associado:** N/A
**Behavior change:** NO
**GitHub Epic Issue:** -
**GitHub Parent US Issue:** -
**GitHub Sprint Container:** -

---

## Pre-Flight de Governanca

- **US exige Spec governada?** Nao
- **US exige Contract governado?** Nao
- **Justificativa do Nivel ScrumAIDev:** Menor nível suficiente — funções puras sem API/UI/evento; comportamento observável capturado por testes unitários. Níveis 2+ exigiriam boundary técnico que não existe nesta US (regra 13 do AGENTS.md).
- **Justificativa:** Dispensas de Spec/Contract já registradas na story US-001 (docs/stories/US-001_normalizacao_nomes_slug.md), conforme `docs/decisoes_governanca_us_spec_bdd.md` (seção 1 e 2 — mudança puramente interna).
- **Touch List aplicavel:** `database/` (módulo e testes), `docs/tasks/breakdown_US-001.md`, `docs/stories/US-001_normalizacao_nomes_slug.md`, `docs/product_backlog.md`
- **Runner BDD a executar:** N/A
- **Validacao de contrato a executar:** N/A
- **Teste de contrato a executar:** N/A
- **Teste de mock a executar:** N/A

---

## Checagem de Principios (condicional)

Nao aplicavel (Nível ScrumAIDev 1, `Behavior change` = NO, estimativa 2 pontos ≤ 8).

---

## Tasks Tecnicas

### Backend Tasks

#### [TASK-001] Implementar módulo de normalização

- **Descricao:** Criar `database/normalizacao.py` com `normalizar(nome) -> str` (slug kebab-case: minúsculas, NFD sem acentos, não-alfanumérico → hífen, colapso de hífens, trim, `ValueError` para vazio/None/sem alfanuméricos) e `contar_termos(slug) -> int` (exclui partículas `de/da/do/das/dos/e` via constante `PARTICULAS`). Incluir `database/__init__.py` e `database/tests/__init__.py` (marcadores de pacote para imports `database.*`).
- **GitHub Task Issue:** -
- **Estimativa:** 1h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Dependencias:** Nenhuma
- **Criterios de conclusao:**
  - [x] ACs 1–5 da US-001 atendidos pela implementação
  - [x] Type hints obrigatórios (coding standards Python)
  - [x] Erros explícitos e específicos (nunca genéricos)

---

### Testing Tasks

#### [TASK-002] Testes unitários

- **Descricao:** Criar `database/tests/test_normalizacao.py` com `unittest` (stdlib — zero dependências novas, regra 6 do AGENTS.md; pytest é migração futura opcional). Cobrir exemplos reais das duas bases (ACs da story).
- **GitHub Task Issue:** -
- **Estimativa:** 1h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Cobertura esperada:** 100% das duas funções (módulo pequeno e puro)
- **Criterios de conclusao:**
  - [x] Casos de sucesso (acentos, partículas, especiais, trim, minúsculas)
  - [x] Casos de erro (vazio, None, só especiais)
  - [x] Edge cases (partículas excluídas na contagem, hífens múltiplos, slug só de partículas → 0)
  - [x] Comando executado e verde: `python3 -m unittest database.tests.test_normalizacao -v` (17/17 OK)

---

### Documentation Tasks

#### [TASK-003] Atualização de rastreabilidade

- **Descricao:** Atualizar story US-001 (ACs, status), `docs/product_backlog.md` (status da US) e registrar decisão do framework de testes (unittest stdlib).
- **GitHub Task Issue:** -
- **Estimativa:** 1h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Criterios de conclusao:**
  - [x] ACs da story marcadas com evidência dos testes
  - [x] Status da US atualizado no backlog
  - [x] Dispensas de Spec/Contract visíveis no breakdown e na story

---

## Ordem de Execucao Sugerida

1. **Fase 1 - Fundacao/Implementacao**
   - [x] TASK-001
2. **Fase 2 - Validacao**
   - [x] TASK-002
3. **Fase 3 - Rastreabilidade**
   - [x] TASK-003

---

## Timeline Estimado

| Fase | Tasks | Estimativa | Data Inicio | Data Fim |
|------|-------|------------|-------------|----------|
| Fase 1 | TASK-001 | 1h | 2026-09-24 | 2026-09-24 |
| Fase 2 | TASK-002 | 1h | 2026-09-24 | 2026-09-24 |
| Fase 3 | TASK-003 | 1h | 2026-09-24 | 2026-09-24 |

---

## Sugestoes IA

### Automacao Recomendada

- Quando o projeto adotar git/CI: rodar `python3 -m unittest database.tests.test_normalizacao` em pipeline; migrar para pytest se aprovado (regra 6).

### Possiveis Bloqueadores

- Nenhum — módulo puro, sem dependências externas.

### Otimizacoes

- `PARTICULAS` como `frozenset` compartilhada entre normalização/contagem e reutilizável pelas US-002/003/004.

---

## Notas

- Sem git: Passos 3/4 (branch) e 10–12 (commit/push/PR) não aplicáveis — bloqueio registrado; entrega é por arquivos.
- venv pandas/pyarrow não é necessário nesta US (stdlib only); será criado em `database/.venv` na US-002/003.
- Delegação (Passo 0.5): execução local — task pequena e sequencial.
