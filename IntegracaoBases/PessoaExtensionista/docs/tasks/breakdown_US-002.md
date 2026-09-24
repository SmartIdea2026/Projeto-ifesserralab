# Task Breakdown: US-002 Extração das 914 Pessoas da Extensão (SRC)

**Data:** 2026-09-24
**Participantes:** Usuária (PO/dev solo) + Agente IA (opencode)
**Estimativa total:** 5 horas / 3 story points
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
- **Justificativa do Nivel ScrumAIDev:** Extração interna de JSONs estáticos, validada por contagens vs baseline em testes de integração; sem API/UI/evento (regra 13 do AGENTS.md).
- **Justificativa:** Dispensas já registradas na story US-002, conforme `docs/decisoes_governanca_us_spec_bdd.md` (seções 1 e 2 — mudança puramente interna).
- **Touch List aplicavel:** `database/caminhos.py` (novo, fundação NFR02), `database/validacoes.py` (novo, compartilhado), `database/extracao_extensao.py`, `database/tests/test_extracao_extensao.py`, `docs/tasks/breakdown_US-002.md`, `docs/stories/US-002_extracao_pessoas_extensao.md`, `docs/product_backlog.md`
- **Runner BDD a executar:** N/A
- **Validacao de contrato a executar:** N/A
- **Teste de contrato a executar:** N/A
- **Teste de mock a executar:** N/A

---

## Checagem de Principios (condicional)

Nao aplicavel (Nível 1, behavior NO, 3 pontos ≤ 8).

---

## Tasks Tecnicas

### Backend Tasks

#### [TASK-001] Fundação de caminhos centrais

- **Descricao:** Criar `database/caminhos.py` (NFR02): constantes ancoradas na raiz do projeto via `Path(__file__)`, cobrindo o diretório ` bases` (espaço no nome) — SRC, atividades, **ações**, index de extensionistas, Horizon, parquet canônico e `database/output`.
- **GitHub Task Issue:** -
- **Estimativa:** 0,5h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Dependencias:** Nenhuma
- **Criterios de conclusao:**
  - [x] Constantes únicas para todos os insumos (nenhum path solto nos módulos)
  - [x] Independente do cwd de execução

#### [TASK-002] Módulo de extração da extensão

- **Descricao:** Criar `database/extracao_extensao.py`: `extrair_catalogados()` (757 de `index.json`), `extrair_pontuais()` (varredura de `api/atividades/*.json` — `coordenador_acao` + `equipe_execucao[].nome` — com dedupe por slug e exclusão de catalogados), `extrair_coordenacoes_acoes()` (`Coordenador(a)` em `api/acoes/*.json` — fonte adicionada pós-desvio, com aprovação da usuária), `extrair_pessoas_extensao()` (composição 914 + `_pessoas_so_acoes`) e `contagens()`; builder único `_registro_extensao` (DRY — evita triplicação do schema); registro no schema aprovado no C3 + campo `acoes` (regra uniforme); validação de unicidade via `database/validacoes.py`.
- **GitHub Task Issue:** -
- **Estimativa:** 2h (executado em ~2,5h com o desvio)
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Dependencias:** TASK-001
- **Criterios de conclusao:**
  - [x] Null policy: chaves sempre presentes; não aplicáveis como `null` (decisão C3)
  - [x] `funcoes` de pontuais = valores distintos de `funcao` (ordenados); coordenador sem função → lista vazia
  - [x] `atividades` = lista de `atividade_id` (ordenada) para pontuais; `null` para catalogados
  - [x] `acoes` = lista de `acao_id` para as 68 pessoas detectadas como coordenadoras (regra uniforme)
  - [x] Slug gerado sempre por `normalizar(nome)` (regra única US-001); colisão → erro explícito

---

### Testing Tasks

#### [TASK-003] Testes unitários e de integração

- **Descricao:** Criar `database/tests/test_extracao_extensao.py`: unitários com fixtures temporárias (dedupe, null policy, coordenador sem equipe, catalogado citado em atividade, slug duplicado, regra uniforme de `acoes`, pessoa só-de-ação) + integração com as bases reais (757/157/914; 68 com `acoes`).
- **GitHub Task Issue:** -
- **Estimativa:** 1,5h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Cobertura esperada:** funções do módulo cobertas; integração valida baseline BR05
- **Criterios de conclusao:**
  - [x] Unitários verdes com fixtures (sem depender das bases reais)
  - [x] Integração real: contagens iguais ao baseline 914/157 (desvio 154→157 investigado e resolvido)
  - [x] Suíte completa verde no venv do projeto (38/38)

---

### Documentation Tasks

#### [TASK-004] Rastreabilidade

- **Descricao:** Atualizar story US-002 (ACs, status), requisitos (FR01, schema, baselines), backlog e breakdown.
- **GitHub Task Issue:** -
- **Estimativa:** 1h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Criterios de conclusao:**
  - [x] ACs com evidência dos testes
  - [x] Status no backlog atualizado (Review)
  - [x] Dispensas de Spec/Contract visíveis no breakdown e na story
  - [x] FR01/schema/baselines atualizados nos requisitos (fonte acoes + campo acoes)

---

## Ordem de Execucao Sugerida

1. **Fase 1 - Fundacao** — [x] TASK-001
2. **Fase 2 - Implementacao** — [x] TASK-002
3. **Fase 3 - Validacao** — [x] TASK-003
4. **Fase 4 - Rastreabilidade** — [x] TASK-004

---

## Timeline Estimado

| Fase | Tasks | Estimativa | Data |
|------|-------|------------|------|
| 1 | TASK-001 | 0,5h | 2026-09-24 |
| 2 | TASK-002 | 2h | 2026-09-24 |
| 3 | TASK-003 | 1,5h | 2026-09-24 |
| 4 | TASK-004 | 1h | 2026-09-24 |

---

## Sugestoes IA

### Automacao Recomendada
- `database/.venv` (pandas + pyarrow, aprovado no C1) criado nesta US e reutilizado por US-003/004; futura entrada em `.gitignore` quando houver git.

### Possiveis Bloqueadores
- ~~Contagem de pontuais divergente de 157~~ **RESOLVIDO (2026-09-24):** desvio 154→157 era a fonte de ações ausente no FR01; usuária aprovou incluir `Coordenador(a)` de `api/acoes/*.json` + campo `acoes` com regra uniforme.

### Otimizacoes
- Builder único `_registro_extensao` aplicado após review (DRY) — mudanças futuras de schema tocam um só lugar.

---

## Notas

- **Desvio do baseline investigado (BR05):** teste de integração acusou 911/154 vs 914/157 → os 3 faltantes eram coordenadores de ação (Alexander Jeferson Nassau Borges/5546, Cibelle Zanforlin Cesconetto Toresani/2892, Lívia de Azevedo Silveira Rangel/3647). Decisões registradas nos requisitos e na story.
- Delegação (Passo 0.5): execução local — módulos irmãos (US-002/US-003) compartilham convenções novas; evita divergência.
- Sem git: Passos 3/4 e 10–12 N/A (decisão da usuária).
- `vinculo` dos membros de equipe existe na fonte mas não entra na saída (schema C3 não o inclui).
