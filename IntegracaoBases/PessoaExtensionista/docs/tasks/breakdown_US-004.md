# Task Breakdown: US-004 Cruzamento 1:1 e Geração dos 5 JSONs com Auditoria

**Data:** 2026-09-24
**Participantes:** Usuária (PO/dev solo) + Agente IA (opencode)
**Estimativa total:** 4 horas / 3 story points
**Nivel ScrumAIDev:** 1
**Spec governada:** N/A
**Contract governado:** N/A
**Padrao de erro:** N/A (exceções Python explícitas; sem boundary externo)
**BDD associado:** N/A
**Behavior change:** NO (entrega final; novos artefatos)
**GitHub Epic Issue:** -
**GitHub Parent US Issue:** -
**GitHub Sprint Container:** -

---

## Pre-Flight de Governanca

- **US exige Spec governada?** Nao
- **US exige Contract governado?** Nao
- **Justificativa do Nivel ScrumAIDev:** Saída observável por arquivos JSON locais validáveis por testes de integração e auditoria embutida; sem API/evento/UI (regra 13 do AGENTS.md).
- **Justificativa:** Dispensa registrada na story US-004, conforme `docs/decisoes_governanca_us_spec_bdd.md` (seções 1 e 2); schema dos JSONs documentado nos requisitos (fonte única de verdade do schema).
- **Touch List aplicavel:** `database/pipeline.py` (novo), `database/tests/test_pipeline.py` (novo), `database/output/*.json` (gerados), `docs/tasks/breakdown_US-004.md`, `docs/stories/US-004_cruzamento_geracao_jsons_auditoria.md`, `docs/product_backlog.md`
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

#### [TASK-001] Módulo de cruzamento e auditoria

- **Descricao:** Criar `database/pipeline.py`: `cruzar(extensao, horizon)` (join por slug com validação estrita de duplicidades — erro explícito defensivo mesmo com validação a montante; split por `contar_termos`: 3+ → confirmados, <3 → a validar com `motivo`), blocos aninhados `extensao`/`horizon` sem slug interno, `auditar()` (universos, cruzamento, baseline 399/342/57 — Opção A, desvios explicados, unicidade, partículas, invalidos do Horizon) e `gerar_outputs()` (5 JSONs em `database/output/`, UTF-8, `ensure_ascii=False`, indent=2, ordenação determinística por slug; entrypoint `python -m database.pipeline`).
- **GitHub Task Issue:** -
- **Estimativa:** 2h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Dependencias:** US-001, US-002, US-003 (todas Done)
- **Criterios de conclusao:**
  - [x] BR02/BR05/BR06 aplicados (split por termos; desvios reportados e explicados; "a validar" fora de exclusivos)
  - [x] Baselines comparados: 399/342/57 e exclusivos 515/9.689 (Opção A: referência histórica mantida, desvios preenchidos)
  - [x] Saída ordenada por slug (determinística exceto `gerado_em`)

---

### Testing Tasks

#### [TASK-002] Testes unitários e de integração

- **Descricao:** Criar `database/tests/test_pipeline.py`: unitários com pessoas sintéticas (split por termos e motivos, BR06, blocos sem slug interno, erro de duplicidade) + integração real (universos, invariâncias de contagem, baseline/desvios, auditoria, 5 arquivos gerados com UTF-8/acentos, idempotência dos dados).
- **GitHub Task Issue:** -
- **Estimativa:** 1,5h (executado em ~2h com correção de `addClassCleanup` e type hints de ids)
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Cobertura esperada:** funções do módulo cobertas; integração valida invariâncias e baselines
- **Criterios de conclusao:**
  - [x] Unitários verdes com fixtures sintéticas
  - [x] Integração real verde com invariâncias (388 + 14 = 402; exclusivos = universo − matches)
  - [x] Suíte completa verde no venv do projeto (48/48)

---

### Documentation Tasks

#### [TASK-003] Rastreabilidade

- **Descricao:** Atualizar story US-004 (ACs ajustados ao resultado auditado, status), requisitos (Opção A), backlog e breakdown.
- **GitHub Task Issue:** -
- **Estimativa:** 0,5h
- **Assignee:** Usuária (com assistência IA)
- **Status:** Done
- **Criterios de conclusao:**
  - [x] ACs com evidência dos testes e números auditados
  - [x] Status no backlog atualizado (Review)
  - [x] Opção A registrada nos requisitos (baseline histórico + desvios)

---

## Ordem de Execucao Sugerida

1. **Fase 1 - Levantamento** — [x] números reais do cruzamento (402/342/60; desvios investigados)
2. **Fase 2 - Implementacao** — [x] TASK-001
3. **Fase 3 - Validacao** — [x] TASK-002
4. **Fase 4 - Rastreabilidade** — [x] TASK-003

---

## Timeline Estimado

| Fase | Atividade | Estimativa | Data |
|------|-----------|------------|------|
| 1 | Levantamento | 0,5h | 2026-09-24 |
| 2 | TASK-001 | 2h | 2026-09-24 |
| 3 | TASK-002 | 1,5h | 2026-09-24 |
| 4 | TASK-003 | 0,5h | 2026-09-24 |

---

## Sugestoes IA

### Automacao Recomendada
- Comando único: `database/.venv/bin/python -m database.pipeline` para regenerar os 5 JSONs a qualquer momento (aplicado).

### Possiveis Bloqueadores
- ~~Contagens divergentes do baseline 399/342/57~~ **RESOLVIDO (2026-09-24):** desvios investigados (Opção A) — 2 coordenadores de ação da fonte nova + 1 adicional; decomposição por `classification` da análise consolidada não reproduzível em detalhe; documentado em `desvios` do `resumo_auditoria.json` e nos requisitos.

### Otimizacoes
- Join via dict do Horizon (O(1) por slug); ordenação estável por slug em todas as saídas (aplicado).

---

## Notas

- Delegação (Passo 0.5): execução local — módulo depende das convenções das US-001/002/003.
- Sem git: Passos 3/4 e 10–12 N/A (decisão da usuária).
- Motivo `nome_curto_1_termo` implementado defensivamente; não ocorre nos dados reais (verificado na integração).
- Regeneração de saída após qualquer ajuste: `database/.venv/bin/python -m database.pipeline`.
