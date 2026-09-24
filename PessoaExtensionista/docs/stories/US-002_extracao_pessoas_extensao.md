# User Story: US-002 Extração das 914 Pessoas da Extensão (SRC)

**Epic:** Cruzamento Extensão ↔ Horizon
**GitHub Epic Issue:** -
**GitHub US Issue:** -
**Prioridade:** Alta
**Story Points:** 3
**Sprint:** -
**Status:** Done (aprovada pela usuária em 2026-09-24)
**Behavior Change Esperado:** NO (módulo novo)

---

## Historia

**Como** analista de dados do ifes-serra-lab,
**Eu quero** extrair e deduplicar as 914 pessoas da extensão (757 catalogados + 157 pontuais) a partir de ` bases/SRC/`,
**Para que** o universo de pessoas da extensão esteja materializado, validado e pronto para o cruzamento com o Horizon.

### Contexto Adicional

Paridade 100% entre SRC e Diretoria já auditada (Discovery): a extração usa apenas ` bases/SRC/` e registra origem `["SRC", "DIRETORIA"]` para toda pessoa (BR03). Os 157 pontuais vêm de `coordenador_acao` e `equipe_execucao[].nome` dos 525 arquivos de `api/atividades/`.

### Pontos de Esclarecimento

Nenhum ponto pendente (decisões registradas no Discovery G0 e Requirements G1).

---

## Criterios de Aceitacao

- [x] **Criterio 1:** Os 757 registros de ` bases/SRC/api/extensionistas/index.json` são lidos com todos os campos (`slug`, `nome`, `funcoes`, `anos`, `coordena`, `equipe`, `imp_coord`, `imp_eq`, `impacto`).
- [x] **Criterio 2:** Os nomes de `coordenador_acao` e `equipe_execucao[].nome` dos 525 arquivos de atividades são extraídos e deduplicados por slug; pessoas já presentes nos 757 não são contadas como pontuais. *(Ajuste 2026-09-24: `Coordenador(a)` de `api/acoes/*.json` também é fonte — os 3 faltantes do baseline eram coordenadores de ação; campo `acoes` com regra uniforme: 68 pessoas.)*
- [x] **Criterio 3:** Total de pontuais igual a 157 e total geral igual a 914 (baseline da análise consolidada); desvio é reportado no log, não silenciado (BR05).
- [x] **Criterio 4:** Toda pessoa registra `origem: ["SRC", "DIRETORIA"]` (BR03) e `tipo: "catalogado" | "pontual"`.
- [x] **Criterio 5:** Política de null aprovada no C3: campos não aplicáveis a pontuais (`anos`, `coordena`, `equipe`, `imp_coord`, `imp_eq`, `impacto`) são sempre presentes com valor `null`; `atividades` é `null` para catalogados e lista de `atividade_id` para pontuais; `acoes` é `null` para quem não coordena ação.
- [x] **Criterio 6:** `funcoes` de pontuais contém os valores distintos de `funcao` encontrados nas atividades (ex.: `["MENTOR(A)"]`); colisão de slug gera erro explícito interrompendo a execução.
- [x] **Criterio 7:** *(novo, 2026-09-24)* Os 3 pontuais que só coordenam ações (`alexander-jeferson-nassau-borges`, `cibelle-zanforlin-cesconetto-toresani`, `livia-de-azevedo-silveira-rangel`) entram no universo com `funcoes=[]`, `atividades=null` e `acoes` preenchido; 68 pessoas no total têm `acoes` não nulo.

---

## Governanca e Rastreabilidade

- **Nivel ScrumAIDev:** 1
- **Justificativa do nivel:** Comportamento observável por contagens validáveis, sem boundary técnico.
- **US exige Spec governada?** Nao
- **Justificativa da Spec:** Extração interna com validação por contagens vs baseline; sem API/evento.
- **Spec prevista:** N/A
- **US exige Contract governado?** Nao
- **Justificativa do Contract:** Sem boundary de runtime; fontes são arquivos estáticos locais.
- **Contract previsto:** N/A
- **Padrao de erro aplicavel:** N/A
- **BDD previsto:** N/A
- **Gates opcionais aplicaveis:** N/A
- **Touch List preliminar:** `database/extracao_extensao.py` (novo), `database/tests/test_extracao_extensao.py` (novo)
- **Task Issues previstas:** N/A

---

## Mockups/Wireframes

N/A (pipeline de dados).

---

## Notas Tecnicas

### Arquitetura

- **Componentes afetados:** novo módulo `database/extracao_extensao.py`.
- **APIs necessarias:** Nenhuma (leitura de JSONs estáticos).
- **Database changes:** Nenhum.
- **Referencias do modelo de dados:** Schema do bloco `extensao` aprovado no C3 (ver Requirements, seção Estrutura de Saída).
- **Erros observaveis esperados:** slug duplicado → erro explícito; arquivo de atividade malformado → erro apontando o arquivo.

### Dependencias

- [ ] US-001 (funções de normalização e contagem de termos).

### Consideracoes de Performance

1.3k arquivos JSON pequenos — leitura simples; sem risco.

---

## Plano de Testes

### Testes Unitarios

- [ ] Deduplicação de nome repetido em múltiplas atividades → 1 pessoa pontual.
- [ ] Pessoa dos 757 citada em atividades não entra como pontual.
- [ ] Campos não aplicáveis → `null` conforme política C3.

### Testes de Integracao

- [ ] Execução sobre ` bases/SRC/` real: 757 catalogados, 157 pontuais, 914 total (desvios reportados).

### Testes de Contract

- [ ] N/A.

### Testes Manuais

- [ ] Inspeção de uma pessoa catalogada e uma pontual no console/estrutura gerada.

### BDD / Cenarios de Comportamento

- [ ] N/A.

---

## Tasks (Breakdown)

- [ ] **[TASK-001]** Leitor de `api/extensionistas/index.json` (757 catalogados)
  - GitHub Task Issue: N/A - Estimativa: 1h - Assignee: A definir
- [ ] **[TASK-002]** Varredura de `api/atividades/*.json` (coordenador + equipe) com dedupe
  - GitHub Task Issue: N/A - Estimativa: 2h - Assignee: A definir
- [ ] **[TASK-003]** Montagem do registro padronizado (null policy) + testes
  - GitHub Task Issue: N/A - Estimativa: 2h - Assignee: A definir

---

## IA Insights

### Sugestoes de Implementacao

Usar `pathlib.Path.glob` para varrer atividades; coletar `atividade_id` por pessoa durante a varredura; validar contagens contra baseline no final da extração.

### Riscos Identificados

Arquivos de atividade não expõem campo de ano no nível top-level — `anos` de pontuais permanece `null` (campo previsto, valor indisponível nas fontes atuais); se um campo de data for identificado nas fontes, registrar desvio e ajustar.

### Alternativas Consideradas

Extrair também de ` bases/diretoria/` (rejeitado — paridade 100% já auditada, BR03).

---

## Notas e Comentarios

**Execução (2026-09-24, via `/feature-development`):**
- Implementação: `database/extracao_extensao.py` (+ fundação `database/caminhos.py` NFR02 e `database/validacoes.py` compartilhada) e testes em `database/tests/test_extracao_extensao.py`.
- Desvio do baseline detectado pelo teste de integração: 154 pontuais (911 total) vs 157/914 esperados → investigação revelou que os 3 faltantes são coordenadores de ação (`Coordenador(a)` em `api/acoes/*.json`), fonte listada na análise consolidada mas omissa no FR01. Usuária aprovou incluir a fonte com regra uniforme para o campo `acoes` (68 pessoas: 56 catalogados + 9 pontuais + 3 novos).
- Testes: 38/38 OK no venv do projeto (`database/.venv`, pandas 3.0.6 / pyarrow 25.0.1): `database/.venv/bin/python -m unittest discover -s database/tests -t .`
- Código venv/`__pycache__`: entrar em `.gitignore` quando o repositório git existir (decisão da usuária: não inicializar git por enquanto).
- Branch/commit/PR: N/A — sem git.
- Breakdown: `docs/tasks/breakdown_US-002.md` (tasks Done).

---

## Definition of Done Checklist

- [x] Codigo implementado conforme criterios de aceitacao
- [x] Decisao sobre Spec governada foi registrada (Não)
- [x] Decisao sobre Contract governado foi registrada (Não)
- [x] Nivel ScrumAIDev foi registrado (1)
- [x] Spec, Contract e BDD foram atualizados quando aplicavel (N/A)
- [x] Gates opcionais executados ou dispensados com justificativa (N/A)
- [x] Error handling observavel segue o padrao compartilhado quando aplicavel (N/A — erros internos explícitos)
- [x] Code review aprovado (review IA no desenvolvimento — achado DRY corrigido; aprovação da usuária em 2026-09-24)
- [x] Testes unitarios com cobertura adequada (fixtures + integração real; suíte 38/38)
- [x] Testes de integracao e contract passando (integração com base real)
- [x] Documentacao atualizada
- [x] Build/CI passando (N/A — sem CI no nível 1)
- [x] `Behavior change` documentado (NO; N/A PR — sem git)
- [x] Aprovacao do Product Owner (2026-09-24)
