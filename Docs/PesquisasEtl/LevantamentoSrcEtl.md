## 📋 Levantamento — Scripts ETL e Fontes de Dados da Base SRC


## 1. 🌐 Fontes de Dados de Origem

O ETL acessa **5 fontes distintas**:

| # | Fonte | Tipo | URL / Localização | Autenticação |
|---|-------|------|-------------------|-------------|
| 1 | **SRC — Consulta Pública de Ações** | Portal web (JSF/PrimeFaces) | `https://src.ifes.edu.br/src/public/consulta-acao.xhtml` | ❌ Pública |
| 2 | **SRC — Detalhe da Ação** | Página HTML | `https://src.ifes.edu.br/src/public/detalhe-acao.xhtml?id={acao_id}` | ❌ Pública |
| 3 | **SRC — Gerenciar (Público-Alvo)** | Área logada | `https://src.ifes.edu.br/src/pages/gerenciar/gerenciar-publico-alvo.xhtml?atividade={id}` | ✅ Login institucional |
| 4 | **SRC — Gerenciar (Equipe Execução)** | Área logada | `https://src.ifes.edu.br/src/pages/gerenciar/gerenciar-equipe-execucao.xhtml?atividade={id}` | ✅ Login institucional |
| 5 | **Mistral AI** (enriquecimento) | API externa | `https://api.mistral.ai/v1/chat/completions` | ✅ `MISTRAL_KEY` |

> **Obs.:** O campus é selecionável via parâmetro (`--campus Serra`, `--all`, etc.).  
> A fonte 1 usa **Playwright** (JavaScript renderizado). A fonte 2 usa **httpx direto** (HTML estático).

---

## 2. ⚙️ Scripts de ETL Identificados

O código-fonte está em `src/src_etl/` e divide-se em dois submódulos:

### 2.1 `src_etl/etl/` — Núcleo do ETL (Extract + Transform)

| Arquivo | Fase | Tamanho | Descrição |
|---------|------|---------|-----------|
| [`scraper.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/scraper.py) | **EXTRACT** | 7,7 KB | Playwright: navega o portal público SRC, seleciona campus no dropdown, percorre todas as páginas e coleta os `acao_id` de cada ação |
| [`detail.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/detail.py) | **EXTRACT** | 1,4 KB | httpx: para cada `acao_id`, faz GET na página de detalhe e extrai os campos (título, tipo, coordenador, área, processo, etc.) |
| [`gerenciar.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/gerenciar.py) | **EXTRACT** | 12,8 KB | Playwright + login: autentica no SRC, busca ação por nº de processo, coleta público-alvo e equipe executora por atividade |
| [`models.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/models.py) | **TRANSFORM** | 2,6 KB | Schemas Pydantic: `Acao`, `AcaoParticipacoes`, `AtividadeParticipacoes` — valida e tipifica cada registro extraído |
| [`enriquecer.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/enriquecer.py) | **TRANSFORM** | 8,6 KB | Chama Mistral AI para inferir `grande_area` e `area_tematica` quando o campo vem vazio do SRC |
| [`consolidar.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/consolidar.py) | **TRANSFORM** | 4,0 KB | Junta os JSONs de ações (`data/serra/`) + participações (`data/participacoes/`) em um único JSON consolidado por ação |
| [`vinculadas.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/vinculadas.py) | **TRANSFORM** | 3,1 KB | Resolve hierarquia programa → ações filhas (ex.: LAMPEX, LEDS, "Ifes para todos") anotando `filhas: [id1, id2]` |
| [`pipeline.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/etl/pipeline.py) | **ORQUESTRADOR** | 6,3 KB | Cola todas as etapas: resolve campi, aciona scraper + detail, salva JSONs, gerencia workers paralelos |

### 2.2 `src_etl/dashboard/` — Geração de Saídas (Load)

| Arquivo | Descrição |
|---------|-----------|
| [`painel.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/painel.py) | Gera `docs/index.html` — painel principal com 4 abas (visão geral, indicadores, rede, formados) |
| [`site.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/site.py) | Gera `docs/acoes/{id}.html` — página individual de cada ação |
| [`export_json.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/export_json.py) | Gera `docs/api/acoes.json` — API JSON pública sem PII |
| [`indicadores.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/indicadores.py) | Calcula indicadores: alunos únicos, recorrência, tamanho de turma, aprovação por tipo |
| [`impacto.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/impacto.py) | Métricas de impacto das ações |
| [`investimento.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/investimento.py) | Análise de fomento e investimento por ação |
| [`rede.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/rede.py) | Gera grafo de colaboração entre coordenadores |
| [`extensionistas.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/extensionistas.py) | Consolida carreira e atuação dos extensionistas ao longo dos anos |
| [`formados.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/formados.py) | Cruza formandos com participações em extensão |
| [`jornada.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/jornada.py) | Análise da jornada/trajetória dos participantes |
| [`forproex.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/forproex.py) | Dados para relatório FORPROEX |
| [`relatorio.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/relatorio.py) | Gera relatório HTML completo |
| [`temas.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/dashboard/temas.py) | Análise temática das ações por área |

### 2.3 Entrypoints CLI e Scripts de Automação

| Arquivo | Comando | Descrição |
|---------|---------|-----------|
| [`cli.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/cli.py) | `src-etl` | Interface principal: `--campus Serra`, `--all`, `--workers 4`, `--out data/` |
| [`cli_part.py`](https://github.com/ifesserra-lab/src/blob/main/src/src_etl/cli_part.py) | `src-etl-part` | CLI da etapa autenticada — recebe processo ou lê `_index.json` |
| [`scripts/atualizar.sh`](https://github.com/ifesserra-lab/src/blob/main/scripts/atualizar.sh) | `bash scripts/atualizar.sh` | Roda o pipeline completo + commit + push. Agendado via GitHub Actions todo domingo |

---

## 3. 🔄 Fluxo do Pipeline (visão geral)

```
SRC público (Playwright)
  └── scraper.py → coleta acao_ids por campus
        └── detail.py (httpx) → extrai campos de cada ação → data/serra/{id}.json

SRC autenticado (Playwright + login)
  └── gerenciar.py → coleta público-alvo + equipe por atividade → data/participacoes/{proc}.json

Mistral AI (opcional)
  └── enriquecer.py → preenche grande_area/area_tematica vazias

consolidar.py → une ação + participações → data/serra_consolidado.json
vinculadas.py → resolve programa → ações filhas

dashboard/ → gera:
  ├── docs/index.html        (painel 4 abas)
  ├── docs/acoes/{id}.html   (páginas individuais)
  └── docs/api/acoes.json    (API pública sem PII)
```

---

## 4. 🗃️ Modelo de Dados (schema das entidades)

```
ACAO (acao_id PK, processo, natureza, tipo, titulo, coordenador,
       fomento, grande_area, area_tematica, acao_vinculante FK→ACAO)
  └── ATIVIDADE (atividade_id PK, acao_id FK, num, nome)
        ├── PUBLICO_ALVO (total, aprovados, certificados, situacao)
        │   ⚠️ Apenas contagens — sem nome/CPF/e-mail dos alunos
        └── EQUIPE (nome, funcao, vinculo)
              └── → EXTENSIONISTA (nome PK, funcoes, anos_ativos)
```

---

## 5. 🔒 Observações sobre Privacidade

- **Dados brutos** (`data/`) estão no `.gitignore` e nunca são commitados — contêm PII (nome, CPF, e-mail dos alunos)
- **Painel e API** (`docs/`) são seguros para publicação — contêm apenas contagens e dados públicos
- Coordenadores/equipe são **crédito público** (nome + função)

---

## 6. ⚙️ Automação (GitHub Actions)

| Workflow | Gatilho | O que faz |
|----------|---------|-----------|
| `atualizar.yml` | Todo domingo + manual | Executa pipeline completo com credenciais (Secrets), commita JSONs, faz push |
| `pages-astro.yml` | Push em `docs/` | Rebuilda site Astro e publica no GitHub Pages |
| `ci.yml` | Todo PR | Roda testes pytest |

---

## 7. 📦 Instalação e Uso Rápido

```bash
# Instalar
pip install "git+https://github.com/ifesserra-lab/src.git"
playwright install chromium

# Configurar credenciais (nunca commitar)
echo "USER=seu_usuario_src" >> .env
echo "PASSWORD=sua_senha_src" >> .env
echo "MISTRAL_KEY=chave_opcional" >> .env

# Rodar o pipeline completo
src-etl --campus Serra --out data
src-etl-part --from-index data/serra/_index.json --out data/participacoes
src-etl-consolidate --out data/serra_consolidado.json
src-etl-painel --out docs/index.html
```

---
