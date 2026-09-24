# Sprint Planning - Sprint 01

**Data:** 2026-09-24  
**Participantes:** Usuária (PO/dev solo) + Agente IA (opencode)  
**Sprint Duration:** 1 semana (2026-09-24 a 2026-10-01)  
**Sprint Goal:** Conectar nominativamente a Extensão (Campus Serra) à Pesquisa (Horizon): entregar a pipeline completa que normaliza as 914 pessoas da extensão e as 10.089 do Horizon em slugs, cruza as bases 1:1 e gera os 5 JSONs auditáveis em `database/output/`, registrando a origem de cada indivíduo (SRC, DIRETORIA e/ou HORIZON).  
**GitHub Project:** - (sem repositório git/GitHub no momento)  
**GitHub Sprint Iteration:** -  
**GitHub Sprint Milestone:** -  

---

## Sprint Capacity

- **Velocity anterior:** N/A (primeira sprint)
- **Capacidade estimada:** 10 story points
- **Dias uteis disponiveis:** 6 (24/09 a 01/10/2026)
- **Impedimentos conhecidos:** Nenhum. Reserva de ~20% da capacidade para imprevistos considerada viável (tasks somam ~14h estimadas).

---

## Sprint Goal

> Conectar nominativamente a Extensão (Campus Serra) à Pesquisa (Horizon): entregar a pipeline completa que normaliza as 914 pessoas da extensão e as 10.089 do Horizon em slugs, cruza as bases 1:1 e gera os 5 JSONs auditáveis em `database/output/`, registrando a origem de cada indivíduo (SRC, DIRETORIA e/ou HORIZON).

---

## User Stories Selecionadas

### [US-001] Módulo de Normalização de Nomes

- **Prioridade:** Alta
- **GitHub Epic Issue:** -
- **GitHub US Issue:** -
- **Story Points:** 2
- **Assignee:** Usuária (com assistência IA)
- **Nivel ScrumAIDev:** 1
- **Exige Spec governada?** Nao
- **Spec:** -
- **Exige Contract governado?** Nao
- **Contract:** -
- **BDD:** -
- **Behavior change esperado:** NO
- **Dependencias:** Nenhuma (primeira da cadeia)
- **Criterios de Aceitacao:**
  - [ ] `normalizar("Letícia Comissário da Silva")` → `leticia-comissario-da-silva` (minúsculas, acentos removidos, espaços → hífen)
  - [ ] Partículas mantidas no slug (BR01); especiais/hífens múltiplos colapsados
  - [ ] `contar_termos` exclui partículas (BR02): `ana-da-silva` → 2; `leticia-comissario-da-silva` → 3
  - [ ] Nome vazio/None → `ValueError`; funções puras com testes unitários

### [US-002] Extração das 914 Pessoas da Extensão (SRC)

- **Prioridade:** Alta
- **GitHub Epic Issue:** -
- **GitHub US Issue:** -
- **Story Points:** 3
- **Assignee:** Usuária (com assistência IA)
- **Nivel ScrumAIDev:** 1
- **Exige Spec governada?** Nao
- **Spec:** -
- **Exige Contract governado?** Nao
- **Contract:** -
- **BDD:** -
- **Behavior change esperado:** NO
- **Dependencias:** US-001
- **Criterios de Aceitacao:**
  - [ ] 757 catalogados de `api/extensionistas/index.json` + 157 pontuais deduplicados de `api/atividades/*.json` = 914 (desvios reportados, BR05)
  - [ ] Origem `["SRC", "DIRETORIA"]` em toda pessoa (BR03); `tipo` catalogado/pontual
  - [ ] Política de null aprovada no C3 (chaves sempre presentes)
  - [ ] Colisão de slug → erro explícito

### [US-003] Carga e Normalização do Horizon (researchers_canonical.parquet)

- **Prioridade:** Alta
- **GitHub Epic Issue:** -
- **GitHub US Issue:** -
- **Story Points:** 2
- **Assignee:** Usuária (com assistência IA)
- **Nivel ScrumAIDev:** 1
- **Exige Spec governada?** Nao
- **Spec:** -
- **Exige Contract governado?** Nao
- **Contract:** -
- **BDD:** -
- **Behavior change esperado:** NO
- **Dependencias:** US-001 (paralelizável com US-002)
- **Criterios de Aceitacao:**
  - [ ] 10.089 linhas lidas exclusivamente de `researchers_canonical.parquet` (BR04); unicidade validada
  - [ ] `campus` parseado (JSON serializado → `name`); `classification` NaN → `null` (249 registros)
  - [ ] Campos preservados: nome, classification, campus, cnpq_url, was_student, was_staff
  - [ ] Distribuição de `classification` validada: {student: 6519, researcher: 2472, outside_ifes: 849, null: 249}

### [US-004] Cruzamento 1:1 e Geração dos 5 JSONs com Auditoria

- **Prioridade:** Alta
- **GitHub Epic Issue:** -
- **GitHub US Issue:** -
- **Story Points:** 3
- **Assignee:** Usuária (com assistência IA)
- **Nivel ScrumAIDev:** 1
- **Exige Spec governada?** Nao
- **Spec:** -
- **Exige Contract governado?** Nao
- **Contract:** -
- **BDD:** -
- **Behavior change esperado:** NO (entrega final; novos artefatos)
- **Dependencias:** US-001, US-002, US-003
- **Criterios de Aceitacao:**
  - [ ] Join por slug com cardinalidade 1:1 validada (1:N → erro explícito)
  - [ ] Split: 3+ termos → `matches_confirmados.json`; 2 termos → `matches_a_validar.json` com `motivo` (BR02)
  - [ ] `exclusivos_extensao.json` (baseline 515) e `exclusivos_horizon.json` (baseline 9.690) gerados (BR06: "a validar" fora de exclusivos)
  - [ ] `resumo_auditoria.json` completo com baseline 399/342/57 e desvios destacados (BR05)
  - [ ] 5 JSONs em `database/output/`, UTF-8 com acentos, campos conforme schema aprovado no C3; execução determinística

---

## Rastreabilidade da Sprint

- **Backlog fonte:** docs/product_backlog.md
- **TODO tecnico:** N/A (tasks detalhadas nas próprias stories US-001..US-004)
- **GitHub Sprint Container em uso:** N/A (sem GitHub)
- **Specs a criar/atualizar:** Nenhuma (decisão Nível 1 — C2/C3)
- **Contracts a criar/atualizar:** Nenhum (schema dos JSONs documentado em docs/requirements/requirements_cruzamento_nomes_extensao_horizon.md)
- **BDD a criar/atualizar:** Nenhum
- **Gates opcionais da sprint:** N/A
- **Task Issues a criar/atualizar:** N/A (sem GitHub; ver seção Tasks de cada story)

## Definition of Done

- [ ] Codigo revisado (code review — revisão da usuária com apoio IA)
- [ ] Decisao sobre Spec governada registrada para cada US (sim — todas "Não")
- [ ] Decisao sobre Contract governado registrada para cada US (sim — todas "Não")
- [ ] Nivel ScrumAIDev registrado para cada US (sim — todas nível 1)
- [ ] Specs, Contracts e BDD atualizados quando aplicavel (N/A nesta sprint)
- [ ] Testes unitarios implementados (funções puras de normalização, extração e split)
- [ ] Testes de integracao passando (pipeline sobre bases reais com contagens vs baseline)
- [ ] Documentacao atualizada
- [ ] Build em CI/CD passando (N/A — sem CI no nível 1)
- [ ] Deploy em ambiente de staging (N/A — pipeline local)
- [ ] Validacao do Product Owner

---

## Riscos e Dependencias

| Risco/Dependencia | Impacto | Mitigacao |
|-------------------|---------|-----------|
| Desvio do baseline 399 (342/57) | Médio | BR05: desvios reportados em `resumo_auditoria.json` e investigados antes de fechar a sprint |
| Homônimos em nomes de 2 termos (~8% dos matches) | Baixo | Lista separada `matches_a_validar.json` (decisão C1 do scope-idea) |
| Path ` bases` com espaço no nome | Baixo | Constante central única para paths (NFR02) |
| Sem repositório git | Médio | Rastreabilidade por arquivos versionáveis; commits/passos 8 e 8.5 do workflow adiados até existir repo |
| Cadeia US-001 → US-002/003 → US-004 | Baixo | Ordem de execução definida; US-002 e US-003 paralelizáveis após US-001 |

---

## Notas e Decisoes

- Sprint 01 cobre o EPIC-001 completo (10 pts): decisão da usuária no checkpoint de planejamento.
- Duração de 1 semana (2026-09-24 a 2026-10-01): decisão da usuária; tasks somam ~14h estimadas.
- Stack aprovada (C1 do scope-idea): Python + pandas + pyarrow; código em `database/` com venv próprio (NFR01); pandas 3.0.6 / pyarrow 25.0.1 já validados em ambiente temporário.
- Saída: somente listas divididas (C2), com política de null aprovada e campos revisados no C3.
- Commits do planning não executados (Passo 8 do workflow): diretório não é repositório git.
- `/publish-github-planning` (Passo 8.5): não aplicável — sem GitHub. Publicar quando o repo existir.

---

## Assistencia IA Utilizada

- [x] Refinamento de user stories (via `/scope-idea` — checkpoints C0–C3)
- [x] Estimativa de complexidade (2/3/2/3 pts, revisada no C3)
- [x] Identificacao de riscos tecnicos
- [x] Sugestoes de arquitetura (módulos em `database/`, venv, constantes de path)
- [x] Definicao de Spec e Contract (decisão: Nível 1, sem governança adicional)
- [ ] Outros: -
