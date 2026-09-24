# Requirements — Normalização e Cruzamento de Nomes: Extensão (SRC/Diretoria) ↔ Horizon

**Status:** APPROVED
**Discovery de origem:** docs/discovery/discovery_cruzamento_nomes_extensao_horizon.md
**Classificacao de Processo:** NORMAL PROCESS

## Intent Summary
Pipeline Python em `database/` que normaliza as 914 pessoas da extensão e as 10.089 pessoas do Horizon em slugs kebab-case, cruza as bases 1:1 e gera JSONs em listas divididas (confirmados, a validar, exclusivos de cada lado + auditoria), registrando a origem de cada indivíduo (SRC, DIRETORIA e/ou HORIZON).

## Functional Requirements
- **FR01** — Extrair as 914 pessoas da extensão de três fontes em ` bases/SRC/`: 757 catalogados de `api/extensionistas/index.json` (campos `slug`, `nome`, `funcoes`, `anos`, `coordena`, `equipe`, `imp_coord`, `imp_eq`, `impacto`) + pontuais deduplicadas de `api/atividades/*.json` (campo `coordenador_acao` string + array `equipe_execucao[].nome`) + pontuais que só coordenam ações, extraídas de `Coordenador(a)` em `api/acoes/*.json` — tudo deduplicado por nome normalizado (fonte de ações adicionada no ajuste pós-desvio de 2026-09-24; baseline 157/914 exige a fonte de ações).
- **FR02** — Normalizar nomes em slug kebab-case: minúsculas, sem acentos (NFD), sem caracteres especiais, espaços → hífen, colapso de hífens múltiplos, trim; unicidade de slug garantida em cada universo (erro explícito em caso de colisão).
- **FR03** — Ler ` bases/horizon/researchers_canonical.parquet` (10.089 linhas; **10.088 nomes válidos** — 1 registro com `name='-'` na linha 1631 é tratado como inválido e reportado, decisão de 2026-09-24) e normalizar com a mesma regra de FR02; `carregar_horizon()` é fail-fast por padrão e retorna `(pessoas_validas, registros_invalidos)` com `ignorar_invalidos=True`.
- **FR04** — Cruzar extensão ↔ Horizon por slug com validação estrita de cardinalidade 1:1; qualquer 1:N é tratado como erro explícito registrado na auditoria (nunca silenciado).
- **FR05** — Classificar cada match pelo número de termos (BR02): 3+ termos → match confirmado; 2 termos → match a validar.
- **FR06** — Gerar os JSONs de saída em `database/output/` na estrutura aprovada (seção "Estrutura de Saída"), com origem por pessoa (SRC, DIRETORIA e/ou HORIZON).
- **FR07** — Gerar `resumo_auditoria.json` com: totais por universo (914, 757, 157, 10.089), matches confirmados, matches a validar, exclusivos de cada lado, unicidade de slugs, cardinalidade e qualquer desvio vs baseline (BR05).

## Business / Domain Rules
- **BR01** — Partículas (`de`, `da`, `do`, `das`, `dos`, `e`) são mantidas no slug (padrão da análise consolidada: `leticia-comissario-da-silva`).
- **BR02** — A contagem de termos para o split de nomes curtos **exclui partículas** (`ana-da-silva` = 2 termos → lista de validação).
- **BR03** — A paridade 100% entre SRC e Diretoria é assumida e auditada: a extração usa apenas ` bases/SRC/` como fonte; toda pessoa da extensão registra origem `["SRC", "DIRETORIA"]` simultaneamente.
- **BR04** — O cruzamento usa exclusivamente ` bases/horizon/researchers_canonical.parquet` (nunca os 4 subconjuntos ou grafos; a coluna `classification` do próprio parquet cobre a categorização: researcher/student/outside_ifes/null).
- **BR05** — O baseline de 399 matches (342 nos 757 + 57 nas 157) é métrica de referência: desvios são reportados no `resumo_auditoria.json`, não silenciados nem tratados como falha fatal.
- **BR06** — Pessoas "a validar" não entram em nenhuma lista de exclusivos (são matches pendentes de validação humana).

## Non-Functional Requirements
- **NFR01** — Execução via venv do projeto em `database/` com `pandas` + `pyarrow` (aprovado no Discovery, regra 6 do AGENTS.md).
- **NFR02** — Paths das bases centralizados em constante única (diretório ` bases` possui espaço no nome).
- **NFR03** — Execução determinística e reexecutável; JSONs em UTF-8 com acentos preservados (`ensure_ascii=False`).
- **NFR04** — Auditoria sempre ativa (sem flag opcional); saída legível por máquina e por humano.

## Estrutura de Saída (aprovada — "somente listas divididas", campos revisados no C3)
Arquivos em `database/output/`, sem arquivo unificado. **Política de null (C3): todas as chaves sempre presentes; valores não aplicáveis como `null`.**

Bloco `extensao` (nível raiz nos exclusivos; aninhado nos matches):
`{nome, origem: ["SRC","DIRETORIA"], tipo: "catalogado"|"pontual", funcoes, anos, coordena, equipe, imp_coord, imp_eq, impacto, atividades, acoes}` — `anos/coordena/equipe/imp_*`: só catalogados (`null` para pontuais); `atividades`: lista de `atividade_id` só para pontuais vindos de atividades (`null` caso contrário); `acoes` (regra uniforme, decisão de 2026-09-24): lista de `acao_id` para **qualquer** pessoa detectada como `Coordenador(a)` nos 202 arquivos de `api/acoes/` (56 catalogados + 9 pontuais + 3 novos), `null` para quem não coordena; `funcoes` de pontuais = valores distintos de `funcao` nas atividades (vazia para quem só coordena ação).

Bloco `horizon` (nível raiz em `exclusivos_horizon`; aninhado nos matches):
`{nome, classification: "researcher"|"student"|"outside_ifes"|null, campus: <name>|null (parse do JSON serializado), cnpq_url, was_student, was_staff}`.

1. **`matches_confirmados.json`** — matches com 3+ termos:
   `{slug, termo_count, extensao: {bloco extensao}, horizon: {bloco horizon}}`
2. **`matches_a_validar.json`** — matches com 2 termos: mesma estrutura + `motivo: "nome_curto_2_termos"`.
3. **`exclusivos_extensao.json`** — pessoas da extensão sem match confirmado nem a validar (baseline: 515): `{slug, nome, origem, tipo, funcoes, anos, coordena, equipe, imp_coord, imp_eq, impacto, atividades, acoes}`.
4. **`exclusivos_horizon.json`** — pessoas do Horizon sem match confirmado nem a validar (baseline: 9.689 sobre 10.088 válidos): `{slug, nome, classification, campus, cnpq_url, was_student, was_staff}`.
5. **`resumo_auditoria.json`** — `{gerado_em, insumos, universos: {extensao_total: 914, catalogados: 757, pontuais: 157, horizon_lidas: 10089, horizon_validas: 10088, horizon_invalidas: 1}, cruzamento: {matches_confirmados, matches_a_validar, exclusivos_extensao, exclusivos_horizon}, baseline_analise_consolidada: {total: 399, catalogados: 342, pontuais: 57}, desvios, auditoria: {slug_unico_extensao, slug_unico_horizon, cardinalidade_1_1, particulas_excluidas, registros_invalidos_horizon}}` (FR07).

Campos do parquet deliberadamente fora da saída: `resume`, `google_scholar_url`, `citation_names`, `identification_id`, `birthday`.

## User Scenarios
### Main flow
1. Usuário executa o script da pipeline (`database/`).
2. Script lê ` bases/SRC/` (extensionistas + atividades) e ` bases/horizon/researchers_canonical.parquet`.
3. Normaliza nomes → slugs; valida unicidade.
4. Cruza por slug; separa confirmados (3+ termos) e a validar (2 termos).
5. Gera os 5 JSONs em `database/output/` e imprime resumo no console.

### Alternative / Error / Edge cases
- Colisão de slug dentro de um universo → erro explícito, execução interrompida com mensagem apontando o registro.
- Match 1:N (slug repetido entre bases) → erro explícito registrado na auditoria.
- Nome pontual repetido em múltiplas atividades → deduplicado por slug (uma única pessoa).
- `classification` ausente (NaN, ~249 registros) → persistido como `null` no JSON.
- Desvio do baseline 399 → pipeline conclui, mas o desvio aparece destacado no `resumo_auditoria.json`.

## Business / Domain Context
- SRC e Diretoria compartilham exatamente a mesma base de pessoas (auditoria da análise consolidada: 100% de paridade).
- Horizon é base estadual multicampus (23 campi); o campo `campus` do parquet identifica a unidade de cada pessoa.
- A análise consolidada registrou 399 matches 1:1 e unicidade total de nomes/slugs nas duas bases.

## Technical Context & Constraints
- Python 3.14.4 + venv com pandas/pyarrow; código em `database/` (regras 6 e 7 do AGENTS.md).
- Insumos: ` bases/SRC/api/extensionistas/index.json` (757), ` bases/SRC/api/atividades/*.json` (525 arquivos), ` bases/horizon/researchers_canonical.parquet` (10.089).
- Sem dependências externas além de pandas/pyarrow.

## Quality Attributes
- **Confiabilidade:** auditoria embutida; erros explícitos de cardinalidade/unicidade.
- **Manutenibilidade:** regra de normalização isolada em função única; paths em constante central.
- **Testabilidade:** funções puras de normalização e contagem de termos (BR02) testáveis isoladamente.

## Assumptions
- **A01** — Baseline de 399 matches permanece válido para as versões atuais das bases.
- **A02** — Paridade 100% SRC=Diretoria vigente (auditada na análise consolidada).
- **A03** — Slugs da pipeline equivalem aos da análise consolidada (mesma regra de normalização).

## Out of Scope
- Outras bases do ifes-serra-lab (Egressos, Editais, GeDoc); demais arquivos do Horizon; desambiguação externa; visualização/frontend; automatização/agendamento (LATER do Discovery).

## Open Questions
- Nenhuma pergunta bloqueante aberta.

## Key Decisions Proposed
- Estrutura de saída **"somente listas divididas"** (decisão do usuário no C2): 5 arquivos listados na seção "Estrutura de Saída", sem arquivo unificado.
- BR02 aprovada: exclusão de partículas na contagem de termos.
- Código em `database/` com pandas/pyarrow (C1).

## Review & Adjust

O usuario pode **aprovar, editar, adicionar, remover ou reclassificar** qualquer requisito/regra antes do gate.

- [x] Proposta completa apresentada ao usuario
- [x] Ajustes solicitados incorporados
- [x] IDs estabilizados depois da revisao
- [x] Nenhuma pergunta bloqueante aberta

### User adjustments
- Estrutura de saída alterada para **somente listas divididas**: `matches_confirmados.json`, `matches_a_validar.json`, `exclusivos_extensao.json` (baseline 515), `exclusivos_horizon.json` (baseline 9.690) e `resumo_auditoria.json` — sem `pessoas_unificadas.json`.
- BR02 confirmada: exclusão de partículas (`de/da/do/das/dos/e`) na contagem de termos.
- Checkpoint C3 (revisão de campos): especificação campo a campo dos 5 JSONs aprovada pelo usuário; política de null definida — chaves não aplicáveis sempre presentes com valor `null` (ex.: `imp_*` de pessoa pontual). Campos `was_student`/`was_staff`/`cnpq_url` incluídos no bloco `horizon` para auxiliar validação de homônimos.
- Ajustes pós-testes de integração (2026-09-24, `/feature-development` US-002/US-003): (1) fonte `Coordenador(a)` de `api/acoes/*.json` adicionada ao FR01 — os 3 faltantes do baseline 157 eram coordenadores de ação; campo `acoes` criado no bloco `extensao` com regra uniforme (68 pessoas); (2) registro `name='-'` (linha 1631 do parquet) tratado como inválido: 10.088 válidos + 1 reportado na auditoria; exclusivos_horizon baseline 9.690 → 9.689; (3) baseline 399 do cruzamento permanece inalterado.
- Cruzamento auditado (2026-09-24, `/feature-development` US-004, **Opção A**): `baseline_analise_consolidada` mantém os números publicados da análise (399/342/57) e o bloco `desvios` do `resumo_auditoria.json` documenta os valores auditados com explicação — 402 matches (388 confirmados 3+ termos; 14 a validar 2 termos), 60 pontuais (+3: 2 coordenadores de ação + 1 adicional), exclusivos 512/9.686 (−3); matches_catalogados 342 = exato; decomposição por `classification` da análise (27/22/8) não reproduz a classificação real do parquet (34/23/2 + 1 sem classificação). Motivo defensivo `nome_curto_1_termo` definido para o split (não ocorre nos dados reais).

## Gate G1 — REQUIREMENTS READY

**Status:** APPROVED

**Aprovado pelo usuario:** sim (checkpoint C2 do workflow `/scope-idea`)
