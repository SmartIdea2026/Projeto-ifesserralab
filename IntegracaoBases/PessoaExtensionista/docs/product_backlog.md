# Product Backlog

**Produto:** Cruzamento de Bases ifes-serra-lab (Extensão ↔ Horizon)  
**Product Owner:** A definir (usuária do projeto)  
**Ultima atualizacao:** 2026-09-24

---

## Visao do Produto

> Conectar nominativamente as pessoas da Extensão (SRC/Diretoria do Campus Serra) às da Pesquisa (Horizon estadual) a partir das bases do ifes-serra-lab, gerando listas JSON auditáveis que registram a origem de cada indivíduo (SRC, DIRETORIA e/ou HORIZON) e separam quem tem vínculo com a pesquisa de quem é exclusivo da extensão.

Use `Spec`, `Contract` e `BDD` para rastrear os artefatos tecnicos quando a User Story exigir governanca adicional. Quando nao se aplicar, use `-`.

---

## Backlog Items

### Alta Prioridade

#### [EPIC-001] Cruzamento Extensão ↔ Horizon

**Objetivo:** Normalizar os nomes das 914 pessoas da extensão e das 10.089 do Horizon em slugs kebab-case, cruzar as bases 1:1 e gerar 5 JSONs auditáveis (confirmados, a validar, exclusivos de cada lado, auditoria) em `database/output/`.
**Valor de negocio:** Alto
**Estimativa:** 10 pontos
**GitHub Epic Issue:** -

##### User Stories

| ID | Issue | Titulo | Story Points | Status | Sprint | Spec | Contract | BDD |
|----|-------|--------|--------------|--------|--------|------|----------|-----|
| US-001 | - | Módulo de normalização de nomes (slug kebab-case + contagem de termos) | 2 | Done | 1 | - | - | - |
| US-002 | - | Extração das 914 pessoas da extensão (SRC) | 3 | Done | 1 | - | - | - |
| US-003 | - | Carga e normalização do Horizon (researchers_canonical.parquet) | 2 | Done | 1 | - | - | - |
| US-004 | - | Cruzamento 1:1 e geração dos 5 JSONs com auditoria | 3 | Review | 1 | - | - | - |

**Dependências:** US-001 → US-002 e US-003 (paralelizáveis); US-004 depende de US-001, US-002 e US-003.
**Rastreabilidade Requirements:** FR01→US-002 · FR02→US-001 · FR03→US-003 · FR04/FR05/FR06/FR07→US-004 · BR01/BR02→US-001 · BR03→US-002 · BR04→US-003 · BR05/BR06→US-004.

---

## Technical Debt & Bugs

| ID | Descricao | Prioridade | Estimativa | Impacto |
|----|-----------|------------|------------|---------|
| - | - | - | - | - |

---

## Spikes & Research

| ID | Topico | Objetivo | Time-box | Status |
|----|--------|----------|----------|--------|
| - | - | - | - | - |

---

## Roadmap Overview

### Q4 2026

- [ ] EPIC-001 — pipeline de cruzamento completa (US-001 → US-004)
- [ ] LATER — validação de homônimos por campus para `matches_a_validar`
- [ ] LATER — enriquecimento mútuo de dados (seção 8 da análise consolidada)

---

## IA Insights

### Priorizacao Sugerida

Executar US-001 primeiro (fundação); US-002 e US-003 em paralelo; US-004 por último — é a story que gera valor de negócio (os 5 JSONs). US-001 sozinha não entrega valor de negócio.

### Riscos Identificados

- Nomes curtos (2 termos, ~8% dos matches) com risco residual de homônimo → mitigado pela lista separada `matches_a_validar.json`.
- Desvio do baseline 399 (342/57) deve ser investigado, não aceito silenciado (BR05).
- Alteração futura das bases invalida métricas → script versionado + auditoria em cada execução.

### Oportunidades

- A coluna `classification` do `researchers_canonical.parquet` dispensa a leitura dos 4 subconjuntos (BR04) — pipeline mais simples e rápida.
- `matches_a_validar.json` pode ser enriquecido no futuro com `citation_names` para validação humana de homônimos.

---

## Backlog Refinement Notes

**Ultima sessao:** 2026-09-24

### Decisoes

- Estrutura de saída: **somente listas divididas** (sem arquivo unificado) — checkpoint C2.
- BR02: partículas (`de/da/do/das/dos/e`) excluídas da contagem de termos — checkpoint C2.
- Campos dos 5 JSONs aprovados campo a campo; campos não aplicáveis sempre presentes com `null` — checkpoint C3.
- Governança: Nível ScrumAIDev 1 em todas as stories; sem Spec/Contract governados; schema dos JSONs documentado no Requirements — checkpoints C2/C3.
- Stack: Python + pandas + pyarrow, código em `database/` — checkpoint C1.

### Items Refinados

- [US-001] Módulo de normalização de nomes - Estimado em 2 pontos
- [US-002] Extração das 914 pessoas da extensão (SRC) - Estimado em 3 pontos
- [US-003] Carga e normalização do Horizon - Estimado em 2 pontos
- [US-004] Cruzamento 1:1 e geração dos 5 JSONs com auditoria - Estimado em 3 pontos
- [EPIC-001] Cruzamento Extensão ↔ Horizon - Spec - / Contract - / BDD -

### Proximas sessoes

- **Data:** A definir
- **Foco:** `/sprint-planning` com o primeiro vertical slice (sequência US-001 → US-002 → US-003 → US-004)

---

## Glossario e Definicoes

| Termo | Definicao |
|-------|-----------|
| Slug | Identificador textual kebab-case derivado do nome (minúsculas, sem acentos, sem caracteres especiais). |
| Extensionista catalogado | Pessoa com perfil próprio em `api/extensionistas/` (757 no total). |
| Pessoa pontual | Pessoa que atuou apenas em `equipe_execucao`/coordenação de atividades, sem perfil próprio (157 no total). |
| Horizon | Sistema de pesquisa/pós-graduação do ifes-serra-lab (base estadual, 23 campi). |
| SRC / Diretoria | Módulos de extensão do Campus Serra; base de pessoas idêntica (paridade 100%). |
| Classification | Coluna do parquet canônico do Horizon: `researcher`, `student`, `outside_ifes` ou null. |
| Match a validar | Match por slug com nome de 2 termos (partículas excluídas), pendente de validação humana. |
