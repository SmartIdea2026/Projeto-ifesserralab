# Discovery — Normalização e Cruzamento de Nomes: Extensão (SRC/Diretoria) ↔ Horizon

**Status:** APPROVED
**Classificacao de Processo:** NORMAL PROCESS
**Origem:** usuario

## Intent
Conectar nominativamente as pessoas da Extensão (SRC e Diretoria) às da Pesquisa (Horizon) a partir das bases do ifes-serra-lab, gerando arquivos JSON que registram a origem de cada indivíduo (SRC, DIRETORIA e/ou HORIZON) e separam quem tem vínculo com a pesquisa de quem é exclusivo da extensão.

Por que agora: as bases já foram analisadas e auditadas (`analise_conexao_pessoas_extensionistas.md`), mas o cruzamento ainda não está materializado em código versionado e saídas reutilizáveis.

## Problem
Os sistemas do ifes-serra-lab operam isolados. A mesma pessoa física aparece com grafias distintas entre SRC/Diretoria e Horizon (acentuação, partículas em maiúsculas), o que impede qualquer análise unificada entre extensão e pesquisa.

## Users / Stakeholders relevantes
- **Usuário/analista (project owner):** consome os JSONs para análises e enriquecimento mútuo entre extensão e pesquisa.
- **Consumidores futuros do dado unificado:** relatórios, dashboards ou pipelines que vierem a consumir as listas geradas.

## Current Situation
- Extensão: 914 pessoas (757 extensionistas catalogados + 157 pontuais em atividades), com paridade de 100% entre SRC e Diretoria (já auditada).
- Horizon: 10.089 pessoas em ` bases/horizon/researchers_canonical.parquet` (base mestre, união exata dos 4 subconjuntos).
- Análise consolidada aponta 399 matches 1:1 com normalização por slug (342 nos 757 + 57 nas 157).
- Nenhum script de normalização/cruzamento existe em repositório; diretório ` bases` possui espaço no nome (exige cuidado com paths).

## Desired Outcome
- Slugs kebab-case padronizados (minúsculas, sem acentos, sem caracteres especiais) para as 914 pessoas da extensão.
- Cruzamento 1:1 exclusivo contra `researchers_canonical.parquet`.
- JSONs de saída com origem por pessoa (SRC, DIRETORIA e/ou HORIZON) e divisão clara entre quem tem vínculo com a pesquisa e quem é exclusivo da extensão.

## Success Criteria
- As 914 pessoas da extensão normalizadas em slug, sem colisões internas de slug.
- Cruzamento exclusivo contra `researchers_canonical.parquet` (sem uso dos demais parquets do Horizon).
- Reprodução das métricas de referência da análise consolidada: total de matches igual a 399 (baseline), com auditória de unicidade e cardinalidade (nenhum 1:N).
- Matches com nomes de 2 termos (~8%) separados em lista própria de validação, fora do conjunto de confirmados.
- JSONs de saída gerados conforme estrutura aprovada no Requirements.

## Scope

### IN
- Normalização (slug kebab-case) das 914 pessoas: 757 perfis de `api/extensionistas/` + 157 nomes extraídos de `api/atividades/*.json` (`coordenador_acao`, `equipe_execucao`).
- Leitura de ` bases/horizon/researchers_canonical.parquet` (10.089 registros) e normalização equivalente dos nomes.
- Cruzamento 1:1 por slug entre Extensão e Horizon.
- Geração de JSONs de saída com origem por pessoa e divisão matched/exclusivos.
- Relatório/auditoria: contagens, unicidade, cardinalidade, split de nomes curtos (2 termos).

### OUT
- Outras bases do ifes-serra-lab (Egressos, Editais, GeDoc).
- Demais arquivos do Horizon (subconjuntos canônicos, grafos, initiatives/advisorships/research_groups etc.).
- Desambiguação externa (Lattes, biometria, e-mail institucional).
- Qualquer camada de visualização/frontend.

### LATER
- Validação de homônimos por campus/grande área para a lista de nomes curtos.
- Enriquecimento mútuo de dados (seção 8 da análise consolidada).
- Automatização/agendamento do pipeline.

## Constraints / Feasibility
- Python 3.14.4 disponível; `pandas` e `pyarrow` não instalados — **aprovados pelo usuário** neste Discovery (regra 6 do AGENTS.md).
- Local do código aprovado: `database/` (pipeline de dados) — regra 7 do AGENTS.md.
- Dados públicos do portal (sem sensibilidade adicional; nenhuma regra LGPD nova).

## Assumptions
- [ASSUMPTION] A métrica de 399 matches da análise consolidada é o baseline esperado do cruzamento (desvios devem ser investigados, não aceitos silenciosamente).
- [ASSUMPTION] Slugs gerados por esta pipeline são equivalentes aos da análise consolidada (mesma regra: minúsculas, sem acentos, sem caracteres especiais, kebab-case).
- [ASSUMPTION] A paridade 100% entre SRC e Diretoria permanece válida para as atuais versões dos arquivos.

## Risks
- Nomes curtos de 2 termos (~8% dos matches) com risco residual de homônimo → mitigado por lista separada de validação (decisão do usuário).
- Divergências cosméticas residuais (espaços duplos, hífens, apóstrofos) → regra de normalização determinística e reportada em auditoria.
- Alteração futura das bases invalida métricas → script versionado e contagens registradas na auditoria.
- Nome do diretório ` bases` com espaço inicial → paths sempre entre aspas/constante central no código.

## Open Questions
- ~~[BLOCKING? sim] Stack e local do processamento~~ → **Resolvido:** Python + pandas/pyarrow em `database/` (aprovado no checkpoint C1).
- [BLOCKING? não → Requirements] Estrutura exata dos JSONs de saída e divisão das listas.
- [BLOCKING? não → Requirements] Política para nomes de 2 termos → **Pré-decidida:** lista separada de validação (detalhar campos no Requirements).

## Review & Adjust

- [x] Usuario revisou a proposta completa
- [x] Alteracoes solicitadas foram incorporadas
- [x] Decisoes relevantes foram confirmadas
- [x] Nao existem perguntas bloqueantes abertas

### User adjustments
- Stack aprovada: Python + pandas + pyarrow, código em `database/` (regras 6 e 7 do AGENTS.md).
- Nomes curtos de 2 termos: irão para **lista separada de validação**, fora do conjunto final de matches confirmados.

## Gate G0 — PROBLEM READY

**Status:** APPROVED

**Aprovado pelo usuario:** sim (checkpoint C1 do workflow `/scope-idea`)
