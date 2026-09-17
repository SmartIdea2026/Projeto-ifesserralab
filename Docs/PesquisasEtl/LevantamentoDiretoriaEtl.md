# Levantamento — ETL e fontes de dados da Diretoria

> **Documento de investigação** sobre a origem dos dados publicados no portal da Diretoria (`ifesserra-lab/diretoria`) e o pipeline de ETL que os gera.
>
> Cada afirmação abaixo vem acompanhada do **link direto para o arquivo/evidência** que a confirma.

---

## 1. Scripts de ETL identificados

A principal implementação de ETL está no repositório [`ifesserra-lab/src`](https://github.com/ifesserra-lab/src), no pacote [`src_etl`](https://github.com/ifesserra-lab/src/tree/main/src/src_etl).

### 1.1 Tabela de scripts

| Script/comando | Função | Origem → Destino | Evidência |
|---|---|---|---|
| `src-etl` | Extrai ações públicas do SRC por campus via Playwright | SRC público → `data/serra/` | [`etl/scraper.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/scraper.py), [`etl/detail.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/detail.py) |
| `src-etl-part` | Extrai participações, público-alvo e equipe (com login) | SRC autenticado → `data/participacoes/` | [`etl/gerenciar.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/gerenciar.py) |
| `src-etl-enrich` | Preenche categorias vazias (`Grande área` / `Área temática`) via IA/Mistral | Dados extraídos → dados enriquecidos | [`etl/enriquecer.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/enriquecer.py) |
| `src-etl-consolidate` | Consolida ações e participações em JSON único | `data/serra/` + `data/participacoes/` → `data/serra_consolidado.json` | [`etl/consolidar.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/consolidar.py) |
| `src-etl-vinculadas` | Identifica vínculos entre programas e ações filhas | Dados do SRC → relações entre ações | [`etl/vinculadas.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/vinculadas.py) (ou [`etl/pipeline.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/pipeline.py)) |
| `src-etl-export` | Gera a API JSON pública usada pelo painel | Dados consolidados → `docs/api/` | [`dashboard/export_json.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/export_json.py) |
| `src-etl-painel` | Gera o painel analítico | Dados consolidados → HTML | [`dashboard/`](https://github.com/ifesserra-lab/src/tree/main/src/src_etl/dashboard) |
| `src-etl-report` | Gera relatório agregado | Dados consolidados → relatório HTML | [`dashboard/relatorio.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/relatorio.py) |
| `src-etl-indicadores` | Gera indicadores derivados | Dados consolidados → indicadores | [`dashboard/indicadores.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/indicadores.py) |
| `src-etl-temas` | Gera análise de temas/categorias | Dados consolidados → análise temática | [`dashboard/temas.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/temas.py) |

### 1.2 Estrutura do pacote `src_etl`

Verificação direta da árvore de arquivos:

- **Pasta `etl/`** → https://github.com/ifesserra-lab/src/tree/main/src/src_etl/etl
- **Pasta `dashboard/`** → https://github.com/ifesserra-lab/src/tree/main/src/src_etl/dashboard
- **README do `src`** → https://github.com/ifesserra-lab/src/blob/main/README.md

O README descreve o fluxo como:
> **extração do SRC → participações → enriquecimento → consolidação → vínculos → painel/API JSON**

---

## 2. Automação do ETL

O workflow [`.github/workflows/atualizar.yml`](https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml) executa o pipeline automaticamente.

### 2.1 Etapas do workflow

| Ordem | Comando | Linha do YAML (evidência) |
|---|---|---|
| 1 | `src-etl --campus Serra --out data --workers 4` | [ver `atualizar.yml`](https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml) |
| 2 | `src-etl-part --from-index data/serra/_index.json` | idem |
| 3 | `src-etl-enrich --acoes data/serra --min-conf 0.6` | idem |
| 4 | `src-etl-consolidate --out data/serra_consolidado.json` | idem |
| 5 | `src-etl-vinculadas --acoes data/serra` | idem |
| 6 | `src-etl-export ... --out docs` | idem |
| 7 | `git add docs/api docs/llms.txt` + commit + push | idem |

### 2.2 Agendamento e secrets

- **Agendamento:** domingos às 06:00 UTC (03:00 BRT) — declarado no bloco `on.schedule.cron` do [workflow](https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml)
- **Secrets usados:** `SRC_USER`, `SRC_PASS`, `MISTRAL_KEY` — declarados no bloco `env` do mesmo arquivo
- **Observação sobre PII:** o próprio workflow registra que `data/formandos/*.xlsx` contém PII e **não vai ao runner do CI**

### 2.3 Onde o workflow publica

O `git push` do workflow ocorre **apenas no repositório `src`**, não no `diretoria`. Isso é verificável no bloco final:

```yaml
git push origin main
```

— presente no [`.github/workflows/atualizar.yml`](https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml).

---

## 3. Fontes dos dados

### 3.1 Fonte primária — SRC/Ifes

**Nome:** SRC/Ifes — Sistema de Registro e Emissão de Certificados
**URL:** https://src.ifes.edu.br
**Endpoint público:** https://src.ifes.edu.br/src/public/consulta-acao.xhtml

**Evidência no código:**

- O `scraper.py` referencia explicitamente o domínio do SRC → [`etl/scraper.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/scraper.py)
- O `gerenciar.py` faz login autenticado no SRC → [`etl/gerenciar.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/gerenciar.py)
- O próprio `llms.txt` publicado declara a fonte → [`diretoria/.../llms.txt`](https://github.com/ifesserra-lab/diretoria/blob/master/docs/relatorios/campus-serra/llms.txt)

**Tipos de acesso:**

- **SRC público:** ações e informações públicas das ações de extensão/ensino
- **SRC autenticado:** participações, público-alvo e equipe

**Credenciais:** `SRC_USER` e `SRC_PASS` (GitHub Secrets do repositório `src`).

### 3.2 Fonte secundária — Mistral AI (enriquecimento)

**Nome:** Mistral AI
**URL:** https://api.mistral.ai/v1/chat/completions
**Modelo:** `mistral-small-latest`
**Credencial:** `MISTRAL_KEY` (GitHub Secret)

**Evidência:** [`etl/enriquecer.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/enriquecer.py) — define `API_URL`, `MODELO_PADRAO` e o comportamento de inferência com confiança mínima.

**Importante:** o Mistral **não é uma fonte primária**. É uma transformação/enriquecimento aplicada aos dados já coletados do SRC. Os campos gerados ganham sufixo `(inferida)`.

### 3.3 Fonte terciária — Planilhas de formandos (PII)

**Local:** `data/formandos/*.xlsx`
**Status:** **não versionado** (contém PII)
**Uso:** seções `jornada`, `forproex`, `formados`, `comunidade`

**Evidência:** o bloco de comentário do [`atualizar.yml`](https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml) declara:

> os dados de FORMADOS (`data/formandos/*.xlsx`) contêm PII e NÃO ficam no repositório — logo não estão no runner.

---

## 4. Como os dados chegam à Diretoria

### 4.1 Ponto central

**O ETL não está dentro do repositório `diretoria`.** O repositório `diretoria` apenas **consome e publica** os JSONs gerados pelo `src`.

### 4.2 Fluxo completo

```text
SRC/Ifes (src.ifes.edu.br)
   │
   ▼
ifesserra-lab/src  ← ETL real (pacote src_etl)
   │
   ├── src-etl
   ├── src-etl-part
   ├── src-etl-enrich
   ├── src-etl-consolidate
   ├── src-etl-vinculadas
   └── src-etl-export
   │
   ▼
src/docs/api/
   │
   ▼
diretoria/docs/relatorios/campus-serra/api/
   │
   ▼
Portal da Diretoria (ifesserra-lab.github.io/diretoria)
```

### 4.3 Evidências por etapa

| Etapa | Evidência |
|---|---|
| ETL no `src` | [`src/src_etl/`](https://github.com/ifesserra-lab/src/tree/main/src/src_etl) |
| Saída do ETL | [`src/docs/api/`](https://github.com/ifesserra-lab/src/tree/main/docs/api) |
| Destino na Diretoria | [`diretoria/docs/relatorios/campus-serra/api/`](https://github.com/ifesserra-lab/diretoria/tree/master/docs/relatorios/campus-serra/api) |
| Declaração da origem no `llms.txt` | [`diretoria/.../llms.txt`](https://github.com/ifesserra-lab/diretoria/blob/master/docs/relatorios/campus-serra/llms.txt) |
| Script de cópia (não é ETL) | [`diretoria/web/scripts/copy-paineis.mjs`](https://github.com/ifesserra-lab/diretoria/blob/master/web/scripts/copy-paineis.mjs) |

### 4.4 O que o `llms.txt` da Diretoria diz

O arquivo [`docs/relatorios/campus-serra/llms.txt`](https://github.com/ifesserra-lab/diretoria/blob/master/docs/relatorios/campus-serra/llms.txt) declara explicitamente:

> Gerado pela biblioteca `src_etl` (github.com/ifesserra-lab/src).

Isso confirma que a Diretoria **reconhece** o `src` como gerador dos dados.

### 4.5 O que o `copy-paineis.mjs` faz

O script [`web/scripts/copy-paineis.mjs`](https://github.com/ifesserra-lab/diretoria/blob/master/web/scripts/copy-paineis.mjs) **apenas copia relatórios já existentes** de `../docs/relatorios` para a área pública do site durante o build. Ele **não**:

- Coleta dados do SRC
- Transforma dados
- Chama o ETL do `src`

Ou seja: é uma etapa de **publicação**, não de ETL.

---

## 5. Ausência de ETL na Diretoria — verificação

Foram verificados os seguintes locais no repositório `diretoria`:

| Local verificado | Resultado | Link |
|---|---|---|
| Pasta `scripts/` | Apenas `sync_activities.py`, `sync_repositories.py`, `generate_charts.py` | https://github.com/ifesserra-lab/diretoria/tree/master/scripts |
| Pasta `.github/workflows/` | Apenas `daily-sync.yml`, `deploy-web.yml`, `governance-report.yml`, `weekly-repository-catalog.yml` | https://github.com/ifesserra-lab/diretoria/tree/master/.github/workflows |
| Busca por `src_etl` no código | Nenhum hit | https://github.com/search?q=repo%3Aifesserra-lab%2Fdiretoria+src_etl&type=code |
| Busca por `ifesserra-lab/src` no código | Nenhum hit relevante | https://github.com/search?q=repo%3Aifesserra-lab%2Fdiretoria+ifesserra-lab%2Fsrc&type=code |

**Conclusão:** não existe workflow, script ou automação no `diretoria` que busque dados do `src` ou execute o ETL do SRC.

---

## 6. Evidência da transferência manual

Os commits que introduziram a API na Diretoria **não são de um bot de CI/CD** — são commits manuais assistidos por IA.

| Commit | Link | Estatísticas |
|---|---|---|
| `4a07c673...` | https://github.com/ifesserra-lab/diretoria/commit/4a07c6736b0abcc0bc49b84691c49b0bd093ce09 | 2.194 arquivos, 79.079 adições |
| `2c54cbcb...` | https://github.com/ifesserra-lab/diretoria/commit/2c54cbcb220b590a24131f019048a5d6c62fd0d4 | 3 arquivos, 29.092 adições |
| `72592313...` | https://github.com/ifesserra-lab/diretoria/commit/7259231324b714c3bdaed4efd67ca7940476058d | 519 arquivos, 491.596 adições |

**Assinatura presente nos commits:**
```
Co-Authored-By: Claude Opus 4.8 (1M context)
```

Isso indica que o conteúdo foi **gerado/copiado com auxílio de um modelo de linguagem**, não por um pipeline automatizado.

---

## 7. Prova do diff — `acao/108.json`

Comparação direta entre o mesmo arquivo nos dois repositórios:

| Versão | URL |
|---|---|
| SRC | https://raw.githubusercontent.com/ifesserra-lab/src/main/docs/api/acoes/108.json |
| Diretoria | https://raw.githubusercontent.com/ifesserra-lab/diretoria/master/docs/relatorios/campus-serra/api/acoes/108.json |

**Diferença observada:** exatamente **2 campos**, ambos gerados pelo `enriquecer.py`:

| Campo | SRC | Diretoria |
|---|---|---|
| `Grande área conhecimento (inferida)` | ❌ ausente | ✅ `"Ciências Sociais Aplicadas"` |
| `Área temática principal (inferida)` | ❌ ausente | ✅ `"Trabalho"` |

**Interpretação:** a versão da Diretoria foi gerada após a execução do enriquecimento por IA. Não há ETL diferente — é o mesmo pipeline, em momento diferente, com o `enriquecer.py` aplicado.

---

## 8. Conclusão

### 8.1 O que foi confirmado

| Item | Confirmação | Link de evidência |
|---|---|---|
| **Scripts de ETL** | Pacote `src_etl` no repositório `src` | https://github.com/ifesserra-lab/src/tree/main/src/src_etl |
| **Fonte primária** | SRC/Ifes (`src.ifes.edu.br`) | https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/scraper.py |
| **Fonte de enriquecimento** | Mistral AI | https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/enriquecer.py |
| **Destino intermediário** | `src/docs/api/` | https://github.com/ifesserra-lab/src/tree/main/docs/api |
| **Base consumida pela Diretoria** | `diretoria/docs/relatorios/campus-serra/api/` | https://github.com/ifesserra-lab/diretoria/tree/master/docs/relatorios/campus-serra/api |
| **Automação do ETL** | `.github/workflows/atualizar.yml` (semanal) | https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml |
| **Sem workflow no `diretoria` que execute ETL** | Verificado em `scripts/` e `.github/workflows/` | https://github.com/ifesserra-lab/diretoria/tree/master/.github/workflows |
| **Transferência manual assistida por IA** | Commits com `Co-Authored-By: Claude` | https://github.com/ifesserra-lab/diretoria/commit/4a07c6736b0abcc0bc49b84691c49b0bd093ce09 |

### 8.2 Conclusão arquitetural

O `src` é responsável por **extração, transformação, consolidação e exportação** dos dados. O `diretoria` atua principalmente como **repositório/portal de publicação e visualização**.

**Não foi identificado, no código atualmente analisado, um workflow do `diretoria` que execute o ETL do SRC.**

Portanto, a transferência `src → diretoria` deve ser tratada como uma **etapa separada do pipeline de ETL** — atualmente manual e assistida por IA — e merece **documentação e automação próprias** caso se queira eliminar sincronizações manuais.

---

## 9. Referências

### Repositórios

- `ifesserra-lab/src` — https://github.com/ifesserra-lab/src
- `ifesserra-lab/diretoria` — https://github.com/ifesserra-lab/diretoria

### ETL e pipeline

- Pacote `src_etl` — https://github.com/ifesserra-lab/src/tree/main/src/src_etl
- Módulo `etl/` — https://github.com/ifesserra-lab/src/tree/main/src/src_etl/etl
- Módulo `dashboard/` — https://github.com/ifesserra-lab/src/tree/main/src/src_etl/dashboard
- `export_json.py` — https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/export_json.py
- `enriquecer.py` — https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/enriquecer.py

### Workflows

- `atualizar.yml` (SRC) — https://github.com/ifesserra-lab/src/blob/main/.github/workflows/atualizar.yml
- Workflows da Diretoria — https://github.com/ifesserra-lab/diretoria/tree/master/.github/workflows

### Dados publicados

- API no SRC — https://github.com/ifesserra-lab/src/tree/main/docs/api
- API na Diretoria — https://github.com/ifesserra-lab/diretoria/tree/master/docs/relatorios/campus-serra/api

### Evidências da Diretoria

- `llms.txt` — https://github.com/ifesserra-lab/diretoria/blob/master/docs/relatorios/campus-serra/llms.txt
- `copy-paineis.mjs` — https://github.com/ifesserra-lab/diretoria/blob/master/web/scripts/copy-paineis.mjs
- Scripts — https://github.com/ifesserra-lab/diretoria/tree/master/scripts

### Commits de evidência

- Introdução da API — https://github.com/ifesserra-lab/diretoria/commit/4a07c6736b0abcc0bc49b84691c49b0bd093ce09
- Trava PII — https://github.com/ifesserra-lab/diretoria/commit/2c54cbcb220b590a24131f019048a5d6c62fd0d4
- Extensionistas — https://github.com/ifesserra-lab/diretoria/commit/7259231324b714c3bdaed4efd67ca7940476058d

### Comparação direta

- `108.json` no SRC — https://raw.githubusercontent.com/ifesserra-lab/src/main/docs/api/acoes/108.json
- `108.json` na Diretoria — https://raw.githubusercontent.com/ifesserra-lab/diretoria/master/docs/relatorios/campus-serra/api/acoes/108.json

### Portal publicado

- Site da Diretoria — https://ifesserra-lab.github.io/diretoria/
- SRC/Ifes oficial — https://src.ifes.edu.br

**Fim do documento.**
