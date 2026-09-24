# User Story: US-004 Cruzamento 1:1 e Geração dos 5 JSONs com Auditoria

**Epic:** Cruzamento Extensão ↔ Horizon
**GitHub Epic Issue:** -
**GitHub US Issue:** -
**Prioridade:** Alta
**Story Points:** 3
**Sprint:** -
**Status:** Review (aguardando validação da usuária para Done)
**Behavior Change Esperado:** NO (entrega final da pipeline; novos artefatos)

---

## Historia

**Como** analista de dados do ifes-serra-lab,
**Eu quero** cruzar os dois universos por slug com validação estrita 1:1, separar matches confirmados (3+ termos) de a validar (2 termos) e gerar os 5 JSONs em `database/output/` com auditoria completa,
**Para que** eu saiba quem tem vínculo com a pesquisa e quem é exclusivo da extensão, com origem registrada por indivíduo (SRC, DIRETORIA e/ou HORIZON).

### Contexto Adicionacional

Baseline da análise consolidada: 399 matches totais (342 nos 757 catalogados + 57 nas 157 pontuais), exclusivos 515 (extensão) e 9.690 (Horizon). Desvios são reportados, nunca silenciados (BR05). Pessoas "a validar" não entram em exclusivos (BR06).

### Pontos de Esclarecimento

Nenhum ponto pendente (decisões registradas no Discovery G0, Requirements G1 e revisão de campos do C3).

---

## Criterios de Aceitacao

- [x] **Criterio 1:** Join por slug entre extensão (914) e Horizon (10.089 lidas / 10.088 válidas — ajuste da US-003) com cardinalidade 1:1 validada; qualquer 1:N interrompe com erro explícito.
- [x] **Criterio 2:** Split por `contar_termos` (BR02): 3+ termos → `matches_confirmados.json` (388); <3 termos → `matches_a_validar.json` (14) com `motivo: "nome_curto_2_termos"` (e `nome_curto_1_termo` defensivo — não ocorre nos dados reais).
- [x] **Criterio 3:** `exclusivos_extensao.json` (512) e `exclusivos_horizon.json` (9.686) gerados; "a validar" fora de exclusivos (BR06). Referências históricas 515/9.689 preservadas via `desvios` (Opção A).
- [x] **Criterio 4:** `resumo_auditoria.json` completo: `gerado_em`, `insumos`, `universos` (914/757/157; Horizon 10.089 lidas, 10.088 válidas, 1 inválida), `cruzamento`, `baseline_analise_consolidada` (399/342/57 — Opção A) e `desvios` com explicação (total +3; pontuais +3; exclusivos −3/−3; **catalogados 342 = exato**).
- [x] **Criterio 5:** Os 5 JSONs são gerados em `database/output/` em UTF-8 com acentos preservados (`ensure_ascii=False`), com os campos exatamente como aprovados no C3 (política de null: chaves sempre presentes).
- [x] **Criterio 6:** Execução determinística e reexecutável (dados idênticos entre execuções; única variação: `gerado_em`), com resumo no console ao final.

---

## Governanca e Rastreabilidade

- **Nivel ScrumAIDev:** 1
- **Justificativa do nivel:** Saída observável por arquivos JSON validáveis; sem boundary técnico de API/evento.
- **US exige Spec governada?** Nao
- **Justificativa da Spec:** Validação por auditoria embutida e testes de integração vs baseline; sem API/evento.
- **Spec prevista:** N/A
- **US exige Contract governado?** Nao
- **Justificativa do Contract:** Os JSONs são artefatos de saída consumidos por humanos/análises; o schema completo está documentado no Requirements (Nível 1, decisão C3).
- **Contract previsto:** N/A
- **Padrao de erro aplicavel:** N/A
- **BDD previsto:** N/A
- **Gates opcionais aplicaveis:** N/A
- **Touch List preliminar:** `database/pipeline.py` (novo), `database/output/*.json` (gerados), `database/tests/test_pipeline.py` (novo)
- **Task Issues previstas:** N/A

---

## Mockups/Wireframes

N/A (pipeline de dados).

---

## Notas Tecnicas

### Arquitetura

- **Componentes afetados:** `database/pipeline.py` orquestrando US-001/002/003; geração dos artefatos em `database/output/`.
- **APIs necessarias:** Nenhuma.
- **Database changes:** Nenhum.
- **Referencias do modelo de dados:** Schemas aprovados no C3 (Requirements, seção Estrutura de Saída).
- **Erros observaveis esperados:** cardinalidade 1:N → erro explícito; colisão de slug → erro explícito; desvio de baseline → destaque em `resumo_auditoria.json` (não fatal).

### Dependencias

- [ ] US-001 (normalização/contagem)
- [ ] US-002 (extensão 914)
- [ ] US-003 (Horizon 10.089)

### Consideracoes de Performance

Join sobre ~11k registros — trivial.

---

## Plano de Testes

### Testes Unitarios

- [ ] Split 2 vs 3+ termos com exemplos reais (`ana-da-silva` → validar; `leticia-comissario-da-silva` → confirmado).
- [ ] Montagem dos blocos `extensao`/`horizon` com política de null.

### Testes de Integracao

- [ ] Pipeline completa sobre as bases reais: contagens vs baseline (399/342/57; 515; 9.690) com desvios reportados; cardinalidade 1:1 confirmada; 5 arquivos gerados e reexecução idempotente.

### Testes de Contract

- [ ] N/A (sem Contract governado; schema validado nos testes de integração).

### Testes Manuais

- [ ] Inspeção de 3 registros reais (confirmado, a validar, exclusivo) contra `analise_conexao_pessoas_extensionistas.md`.

### BDD / Cenarios de Comportamento

- [ ] N/A.

---

## Tasks (Breakdown)

- [ ] **[TASK-001]** Join por slug + validação de cardinalidade
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir
- [ ] **[TASK-002]** Split confirmados/a validar + montagem das listas de exclusivos
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir
- [ ] **[TASK-003]** Geração dos 5 JSONs + `resumo_auditoria.json` + testes de integração
  - GitHub Task Issue: N/A - Estimativa: 2h - Assignee: A definir

---

## IA Insights

### Sugestoes de Implementacao

Centralizar os caminhos de saída e das bases em constantes (NFR02); comparar contagens com baseline em uma única função `auditar()` reutilizada no resumo e nos logs.

### Riscos Identificados

Matches com nomes curtos podem inflar `matches_a_validar` acima do esperado — o split garante que confirmados permaneçam de alta confiança; desvios vs 399 aparecem no resumo.

### Alternativas Consideradas

Arquivo unificado de 10.604 pessoas (rejeitado no C2 — usuário optou por somente listas divididas).

---

## Notas e Comentarios

Entrega de valor final da Epic: origem por pessoa (SRC, DIRETORIA e/ou HORIZON) e separação pesquisa-vinculados × exclusivos da extensão.

**Execução (2026-09-24, via `/feature-development`):**
- Implementação: `database/pipeline.py` (`cruzar`, `auditar`, `gerar_outputs`, entrypoint `python -m database.pipeline`) e testes em `database/tests/test_pipeline.py`.
- Resultado auditado: **402 matches** (388 confirmados 3+ termos; 14 a validar 2 termos; zero com 1 termo), exclusivos 512 (extensão) e 9.686 (Horizon); **catalogados 342 = exato** vs baseline.
- Desvios vs análise consolidada (Opção A aprovada): mantém `baseline_analise_consolidada` (399/342/57) e preenche `desvios` com explicação — 2 coordenadores de ação (fonte nova) + 1 adicional; decomposição por `classification` da análise (27/22/8) não reproduz a classificação real do parquet (34/23/2 + 1 sem classificação). Matches de exemplo validados contra casos citados na análise (Vinícius Secchin de Melo, Adrianna Machado Meneguelli ✓).
- Testes: **48/48 OK** no venv do projeto (`database/.venv/bin/python -m unittest discover -s database/tests -t .`), incluindo idempotência dos dados entre execuções.
- Branch/commit/PR: N/A — sem git.
- Breakdown: `docs/tasks/breakdown_US-004.md` (tasks Done).

---

## Definition of Done Checklist

- [ ] Codigo implementado conforme criterios de aceitacao
- [ ] Decisao sobre Spec governada foi registrada (Não)
- [ ] Decisao sobre Contract governado foi registrada (Não)
- [ ] Nivel ScrumAIDev foi registrado (1)
- [ ] Spec, Contract e BDD foram atualizados quando aplicavel (N/A)
- [ ] Gates opcionais executados ou dispensados com justificativa (N/A)
- [ ] Error handling observavel segue o padrao compartilhado quando aplicavel (N/A)
- [ ] Code review aprovado
- [ ] Testes unitarios com cobertura adequada
- [ ] Testes de integracao e contract passando (integração com bases reais)
- [ ] Documentacao atualizada
- [ ] Build/CI passando (N/A — sem CI no nível 1)
- [ ] `Behavior change` documentado no PR
- [ ] Aprovacao do Product Owner
