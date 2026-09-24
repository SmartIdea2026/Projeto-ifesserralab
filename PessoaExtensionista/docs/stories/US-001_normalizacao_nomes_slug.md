# User Story: US-001 Módulo de Normalização de Nomes

**Epic:** Cruzamento Extensão ↔ Horizon
**GitHub Epic Issue:** -
**GitHub US Issue:** -
**Prioridade:** Alta
**Story Points:** 2
**Sprint:** -
**Status:** Done (aprovada pela usuária em 2026-09-24)
**Behavior Change Esperado:** NO (módulo novo, sem alteração de comportamento existente)

---

## Historia

**Como** analista de dados do ifes-serra-lab,
**Eu quero** funções puras que convertam nomes de pessoas em slugs kebab-case padronizados e contem termos excluindo partículas,
**Para que** o cruzamento entre as bases seja determinístico, reprodutível e auditável.

### Contexto Adicional

A análise consolidada (`analise_conexao_pessoas_extensionistas.md`) demonstrou que a normalização por slug foi determinante: elevou os matches de 312 (string pura) para 399. Exemplos reais: `Leticia Comissario da Silva` (SRC) ↔ `Letícia Comissário da Silva` (Horizon) → `leticia-comissario-da-silva`.

### Pontos de Esclarecimento

Nenhum ponto pendente (decisões registradas no Discovery G0 e Requirements G1).

---

## Criterios de Aceitacao

- [x] **Criterio 1:** `normalizar("Letícia Comissário da Silva")` retorna `"leticia-comissario-da-silva"` (minúsculas, acentos removidos, espaços → hífen).
- [x] **Criterio 2:** Partículas são mantidas no slug (BR01): `normalizar("Juliana Yuri Kanezaki De Souza")` retorna `"juliana-yuri-kanezaki-de-souza"`.
- [x] **Criterio 3:** Caracteres especiais, apóstrofos e hífens/espaços múltiplos são colapsados em hífen único, sem hífens nas pontas.
- [x] **Criterio 4:** `contar_termos(slug)` exclui partículas `de, da, do, das, dos, e` (BR02): `"ana-da-silva"` → 2; `"leticia-comissario-da-silva"` → 3.
- [x] **Criterio 5:** Nome vazio ou `None` gera erro explícito (`ValueError`), nunca slug vazio silencioso.
- [x] **Criterio 6:** Funções puras (sem I/O), com testes unitários cobrindo os exemplos reais das duas bases.

---

## Governanca e Rastreabilidade

- **Nivel ScrumAIDev:** 1
- **Justificativa do nivel:** Comportamento observável via função/testes, sem boundary técnico (API/evento).
- **US exige Spec governada?** Nao
- **Justificativa da Spec:** Não há API/UI/evento; comportamento é capturado por testes unitários com exemplos reais.
- **Spec prevista:** N/A
- **US exige Contract governado?** Nao
- **Justificativa do Contract:** Não há boundary de runtime compartilhado; o schema dos JSONs de saída está documentado no Requirements.
- **Contract previsto:** N/A
- **Padrao de erro aplicavel:** N/A (erros internos via exceções Python explícitas)
- **BDD previsto:** N/A
- **Gates opcionais aplicaveis:** N/A
- **Touch List preliminar:** `database/normalizacao.py` (novo), `database/tests/test_normalizacao.py` (novo)
- **Task Issues previstas:** N/A

---

## Mockups/Wireframes

N/A (pipeline de dados).

---

## Notas Tecnicas

### Arquitetura

- **Componentes afetados:** novo módulo `database/normalizacao.py`.
- **APIs necessarias:** Nenhuma.
- **Database changes:** Nenhum.
- **Referencias do modelo de dados:** N/A.
- **Erros observaveis esperados:** `ValueError` para nome vazio/None.

### Dependencias

- [ ] venv do projeto com pandas/pyarrow (NFR01 do Requirements) — criado na primeira story executada.

### Consideracoes de Performance

Funções O(n) sobre strings; sem risco para 10k registros.

---

## Plano de Testes

### Testes Unitarios

- [ ] Acentuação removida (NFD): `Leticia Comissario da Silva` → `leticia-comissario-da-silva`.
- [ ] Partículas mantidas: `Juliana Yuri Kanezaki De Souza` → `juliana-yuri-kanezaki-de-souza`.
- [ ] Especiais colapsados: `José  O'Brien-Netto` → `jose-o-brien-netto`.
- [ ] `contar_termos`: 2 termos com partícula (`ana-da-silva`); 3 termos (`leticia-comissario-da-silva`); 0/1 termo edge.
- [ ] Nome vazio/None → `ValueError`.

### Testes de Integracao

- [ ] N/A nesta story (a pipeline integra na US-004).

### Testes de Contract

- [ ] N/A (sem Contract governado).

### Testes Manuais

- [ ] N/A.

### BDD / Cenarios de Comportamento

- [ ] N/A.

---

## Tasks (Breakdown)

- [x] **[TASK-001]** Implementar `normalizar(nome) -> str` em `database/normalizacao.py`
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir
- [x] **[TASK-002]** Implementar `contar_termos(slug) -> int` com constante de partículas
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir
- [x] **[TASK-003]** Testes unitários com exemplos reais das duas bases
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir

---

## IA Insights

### Sugestoes de Implementacao

Usar `unicodedata.normalize("NFD", ...)` + categoria unicode para remoção de acentos; constante `PARTICULAS = {"de","da","do","das","dos","e"}` compartilhada entre normalização e contagem.

### Riscos Identificados

Divergências residuais de grafia (espaços duplos, hífens) já cobertas pelo Criterio 3; qualquer caso novo deve virar teste.

### Alternativas Consideradas

Contagem bruta de tokens do slug (rejeitada no C2 — menos fiel à análise consolidada).

---

## Notas e Comentarios

Regra 13 do AGENTS.md: nível 1 suficiente; sem mocks/CI acoplados.

**Execução (2026-09-24, via `/feature-development`):**
- Implementação: `database/normalizacao.py` (`normalizar`, `contar_termos`, `PARTICULAS`) + pacote `database/tests/`.
- Framework de testes: `unittest` (stdlib) — zero dependências novas (regra 6); migração para pytest fica como opção futura a aprovar.
- Testes: 17/17 OK (`python3 -m unittest database.tests.test_normalizacao -v`), incluindo exemplos reais da análise consolidada.
- Code review IA: 1 achado (nome bruto com espaço aceito silenciosamente por `contar_termos`) → corrigido com guarda `ValueError` + teste novo.
- `/code-review` formal (2026-09-24): APROVAR — zero itens críticos/importantes; 3 sugestões nice-to-have avaliadas (docstrings aplicadas; `re.compile` e double-strip rejeitados com justificativa); testes revalidados 17/17.
- Branch/commit/PR: N/A — diretório não é repositório git (bloqueio registrado no breakdown).
- Breakdown: `docs/tasks/breakdown_US-001.md` (TASK-001/002/003 Done).

---

## Definition of Done Checklist

- [x] Codigo implementado conforme criterios de aceitacao
- [x] Decisao sobre Spec governada foi registrada (Não)
- [x] Decisao sobre Contract governado foi registrada (Não)
- [x] Nivel ScrumAIDev foi registrado (1)
- [x] Spec, Contract e BDD foram atualizados quando aplicavel (N/A)
- [x] Gates opcionais executados ou dispensados com justificativa (N/A)
- [x] Error handling observavel segue o padrao compartilhado quando aplicavel (N/A — erros internos explícitos)
- [x] Code review aprovado (`/code-review` formal — APROVAR, 2026-09-24)
- [x] Testes unitarios com cobertura adequada (17/17)
- [x] Testes de integracao e contract passando (N/A nesta US)
- [x] Documentacao atualizada
- [x] Build/CI passando (N/A — sem CI no nível 1)
- [x] `Behavior change` documentado (NO; N/A PR — sem git)
- [x] Aprovacao do Product Owner (2026-09-24)
