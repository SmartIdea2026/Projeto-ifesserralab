# Horizon ETL

Documento tecnico do projeto **Horizon ETL**, responsavel por baixar,
normalizar, persistir e exportar dados academicos e de pesquisa usados pelo
ecossistema Horizon.

## Objetivo

O Horizon ETL consolida dados de fontes institucionais e publicas em um banco
canonico local e em artefatos JSON para consumo por dashboards, auditorias e
marts analiticos.

O projeto tem **dois destinos de carga**:

- **PostgreSQL (banco Horizon)**: carga atual, no modelo de
  `../ModeloLogicoHorizon.sql` (33 tabelas em portugues), em um container
  Docker. Veja [Carga em PostgreSQL](#carga-em-postgresql-banco-horizon).
- **SQLite (legado)**: pipeline anterior, no modelo das bibliotecas
  `research-domain` e `eo_lib`. Continua funcionando e e o unico que gera
  exports, marts e grafos.

Fontes suportadas:

- **SigPesq**: grupos de pesquisa, projetos de pesquisa e planos de trabalho
  de bolsas/orientacoes.
- **Lattes**: curriculos, projetos, producoes, formacoes e orientacoes.
- **CNPq**: sincronizacao complementar de grupos e membros.

## Arquitetura

O projeto segue uma organizacao em camadas:

```text
src/
|-- adapters/
|   |-- database/      # clientes e integracoes de persistencia
|   |-- sinks/         # saidas: JSON e repositorios PostgreSQL (sinks/postgres/)
|   `-- sources/       # adaptadores de fontes externas
|-- core/
|   |-- logic/         # loaders, exporters, matchers e regras de negocio
|   |   `-- carga/     # carregadores do banco Horizon (PostgreSQL)
|   `-- ports/         # contratos para fontes, saidas e repositorios
|-- db/                # schema do banco Horizon (esquema_horizon.py e sql/)
|-- flows/
|   |-- cnpq/          # flows da fonte CNPq
|   |-- exports/       # exportacoes canonicas, marts e grafos
|   |-- lattes/        # flows da fonte Lattes
|   |-- pipelines/     # pipelines compostos
|   |-- sigpesq/       # flows da fonte SigPesq
|   `-- all.py         # orquestracao geral de ingestao
`-- scripts/           # auditoria, manutencao e diagnostico
```

Componentes principais:

- **Prefect** orquestra os flows e registra execucoes locais.
- **PostgreSQL** (servico `horizon-db` do Docker Compose, porta 5434) e o
  banco do Horizon.
- **SQLite** em `db/horizon.db` e o banco do pipeline legado.
- **research-domain** fornece entidades, controladores e repositorios de
  dominio.
- **agent_sigpesq** automatiza login e download de relatorios SigPesq.
- **Loaders e mapping strategies** transformam arquivos brutos em entidades
  canonicas.

## Modelo de dados

O banco Horizon (PostgreSQL) usa as 33 tabelas de `../ModeloLogicoHorizon.sql`:
pessoas (e e-mails, identificadores, perfil Lattes, formacoes, premios e
idiomas), organizacoes e unidades, vinculos, papeis, equipes e grupos de
pesquisa, iniciativas (com hierarquia, participantes e bolsas), producoes e
artigos, e areas de conhecimento.

Entidades do pipeline legado (SQLite):

- `persons`: pessoas consolidadas a partir das fontes.
- `research_groups`: grupos de pesquisa.
- `initiatives`: projetos e planos de trabalho.
- `initiative_types`: classifica `Research Project` e `Advisorship`.
- `advisorships`: dados especificos do plano de trabalho/bolsa.
- `fellowships`: programa de bolsa composto por nome e patrocinador.
- `organizations`: instituicoes, agencias e patrocinadores.

Regra importante:

- O cancelamento pertence ao plano de trabalho em `advisorships.cancelled` e
  `advisorships.cancellation_date`.
- `fellowships` representa o tipo/programa da bolsa. Uma bolsa como `PIVIC`
  com patrocinador `Voluntario` e diferente de `PIVIC` com patrocinador
  `CNPq`, porque o sponsor compoe a identidade do fellowship.

## Carga em PostgreSQL (banco Horizon)

A carga grava num PostgreSQL com as 33 tabelas de `../ModeloLogicoHorizon.sql`
(modelo logico em portugues, fora de `Etl/`; o codigo nunca o edita). Extracao,
parsing e casamento de pessoas sao os mesmos do pipeline legado; so a carga
mudou.

```bash
make horizon-db-up                      # sobe o PostgreSQL (servico horizon-db)
make pipeline-postgres                  # baixa o SigPesq e carrega todas as fontes
make pipeline-postgres SEM_DOWNLOAD=1   # usa as planilhas ja existentes em data/raw/sigpesq
make pipeline-postgres CAMPUS=          # sincroniza o CNPq de todos os campi (padrao: Serra)
make horizon-db-schema                  # so recria o schema, sem carregar
make horizon-db-stop                    # para o PostgreSQL
```

> Cada execucao recria o schema `public` do banco Horizon (recarga completa):
> os dados anteriores sao apagados.

Ordem da carga:

1. Recria o schema a partir do modelo logico e grava os dados iniciais (IFES,
   papeis e tipos).
2. **SigPesq**: grupos, projetos e bolsistas (planilhas mais recentes em
   `data/raw/sigpesq/`).
3. **CNPq**: nome, descricao, membros, lideres e linhas de pesquisa dos grupos
   que tem URL do espelho.
4. **Lattes**: pessoas, curriculos e orientacoes (JSON em `data/lattes_json/`).
   O download continua separado (`make ingest-lattes-download`).
5. **Documentos PJ** (`data/exports/project_sigpesq_files_json/`): preenchem
   descricoes vazias e criam projetos sem par.
6. Grava o relatorio em `data/reports/carga_postgres.json`.

Onde fica o codigo:

| Local | Funcao |
|---|---|
| `src/core/ports/repositorio_*.py` | contratos de gravacao por familia de tabelas |
| `src/adapters/sinks/postgres/` | repositorios PostgreSQL (psycopg 3), sem commit proprio |
| `src/core/logic/carga/` | carregadores por fonte, regras de mapeamento, relatorio e ordem da carga |
| `src/db/` | criacao do schema: `esquema_horizon.py` e `sql/` (ajustes e dados iniciais) |
| `src/flows/pipelines/horizon_postgres.py` | flow Prefect `Horizon Pipeline PostgreSQL` |

Comportamento tecnico:

- Cada passo faz commit no fim; cada registro roda em um savepoint. Um registro
  com erro e desfeito, entra em `pendencias` do relatorio e a carga continua.
- O relatorio traz contagens por passo, `pendencias` (registros pulados), campos
  descartados (`descartado:<campo>`) e `revisar` (itens gravados que pedem
  conferencia).
- E-mails sao gravados em hash (LGPD). A situacao das iniciativas usa
  `em_andamento`, `concluida`, `cancelada` e `desconhecida`.
- O `.sql` e aplicado com ajustes em `src/db/sql/`: `TIMESTAMP` no lugar de
  `DATETIME`, ids gerados pelo banco, textos sem limite de 255 caracteres e
  bolsa unica por nome e financiador.

Fora desta carga: exports canonicos, marts, grafos e tabelas de rastreamento
continuam apenas no pipeline legado (SQLite).

## Fluxo SigPesq

O flow completo de SigPesq fica em `src/flows/sigpesq/all.py` e deve ser
executado por:

```bash
make ingest-sigpesq
```

ou diretamente:

```bash
PREFECT_API_URL=http://127.0.0.1:4200/api \
PREFECT_CLIENT_SERVER_VERSION_CHECK_ENABLED=false \
HORIZON_QUIET_PREFECT=1 \
PREFECT_LOGGING_TO_API_ENABLED=false \
PYTHONPATH=. \
.venv/bin/python app.py sigpesq
```

Comportamento tecnico:

1. O `SigPesqAdapter` valida credenciais.
2. A pasta `data/raw/sigpesq` e limpa antes de qualquer novo download.
3. O agente faz um unico login no portal SigPesq.
4. Sao baixados relatorios de grupos, projetos e advisorships.
5. Os arquivos baixados sao persistidos no banco local.

A limpeza previa evita que relatorios antigos sejam misturados com a execucao
atual, principalmente em `data/raw/sigpesq/advisorships/<ano>/`.

Arquivos esperados apos uma execucao completa:

```text
data/raw/sigpesq/research_group/Relatorio_<data>.xlsx
data/raw/sigpesq/research_projects/Relatorio_<data>.xlsx
data/raw/sigpesq/advisorships/2016/Relatorio_<data>.xlsx
...
data/raw/sigpesq/advisorships/2026/Relatorio_<data>.xlsx
```

## Fluxo Lattes

O download de curriculos Lattes usa `scriptLattes`, que atualmente depende de
Selenium e de um `chromedriver` local. Antes da execucao, o flow valida se o
Chrome/Chromium encontrado tem a mesma versao major do `./chromedriver`.

Quando houver mais de uma instalacao de Chrome/Chromium, ou quando o Chromium do
sistema vier via Snap, informe um binario explicito:

```bash
CHROME_BINARY=/caminho/para/chrome make ingest-lattes-download
CHROME_BINARY=/caminho/para/chrome make ingest-lattes-full
```

O diretorio `data/lattes_json` e limpo de arquivos `.json` antes de cada novo
download. Isso evita misturar JSONs antigos com a lista atual de pesquisadores.
O cache bruto do `scriptLattes` em `cache/` nao e apagado pelo flow.

A carga em PostgreSQL le os JSONs de `data/lattes_json`; ela nao baixa
curriculos.

Por padrao, o flow faz um prefetch paralelo controlado dos curriculos ausentes
em `cache/` antes de chamar o `scriptLattes` para gerar os JSONs. O limite
padrao e de 3 downloads simultaneos:

```bash
HORIZON_LATTES_DOWNLOAD_WORKERS=4 CHROME_BINARY=/caminho/para/chrome make ingest-lattes-download
HORIZON_LATTES_PREFETCH=0 CHROME_BINARY=/caminho/para/chrome make ingest-lattes-download
```

## Execucao com Docker

Executa o sistema completo (Prefect DB + Prefect Server + banco Horizon + ETL app) com Docker Compose.

### Pre-requisitos

- Docker Engine com Compose v2 instalado
- Arquivo `.env` com as credenciais (copie `.env.example` → `.env` e preencha)

### Iniciar servicos

```bash
cp .env.example .env
# Edite .env: defina SIGPESQ_USERNAME, SIGPESQ_PASSWORD e opcionalmente tokens do Telegram
make docker-up
```

### Rodar pipelines

```bash
make docker-pipeline CAMPUS=Serra        # pipeline completo
make docker-ingest-sigpesq               # apenas SigPesq
make docker-sync-cnpq CAMPUS=Serra       # apenas CNPq
make docker-export-canonical CAMPUS=Serra OUTPUT_DIR=data/exports
make docker-full-refresh                 # recria banco e roda pipeline completo
make docker-pipeline-postgres CAMPUS=Serra   # carga no PostgreSQL (horizon-db)
```

Os arquivos exportados aparecem em `data/exports/` no host. O banco SQLite
fica em `db/horizon.db` e pode ser consultado diretamente com ferramentas locais.
O banco Horizon (PostgreSQL) fica no volume `horizon_db` e responde em
`localhost:5434`; o relatorio da carga aparece em `data/reports/`.

### Parar servicos

```bash
make docker-stop   # para containers; dados persistem nos volumes/bind-mounts
```

### Reconstruir a imagem apos mudancas de dependencias

```bash
make docker-build
```

Consulte `specs/002-docker-compose-app/quickstart.md` para cenarios de teste e
troubleshooting de containers.

## Fluxos e entrypoints

Comandos principais:

```bash
make setup
make db-reset
make prefect-server
make ingest-sigpesq
make ingest-lattes-full
make sync-cnpq CAMPUS=Serra
make export-canonical CAMPUS=Serra OUTPUT_DIR=data/exports
make full-refresh
make horizon-db-up
make pipeline-postgres CAMPUS=Serra
```

Entrypoint Python:

```bash
python app.py sigpesq
python app.py all_sources Serra
python app.py cnpq_sync Serra
python app.py export_canonical data/exports Serra
python app.py full_pipeline Serra data/exports
python -m src.flows.pipelines.horizon_postgres --campus Serra --sem-download
```

Execucao recomendada para limpar banco e rodar apenas SigPesq:

```bash
make db-reset
make prefect-server
make ingest-sigpesq
```

Execucao recomendada para reconstruir toda a base:

```bash
make full-refresh
```

## Banco e artefatos

Artefatos locais relevantes:

- Banco Horizon (PostgreSQL): volume `horizon_db` do Docker, em
  `localhost:5434`.
- `db/horizon.db`: banco SQLite local gerado pelo pipeline legado.
- `data/raw/`: arquivos brutos baixados das fontes.
- `data/exports/`: exports canonicos e marts.
- `data/reports/`: relatorios de auditoria e conciliacao, e
  `carga_postgres.json` (ultima carga PostgreSQL; ha tambem uma copia com data
  e hora no nome).
- `logs/`: logs locais de pipeline.

Arquivos gerados nao devem ser tratados como fonte de verdade do codigo. A
fonte de verdade e formada pelos flows, strategies, loaders e entidades de
dominio.

## Configuracao

Variaveis comuns:

```bash
SIGPESQ_USERNAME=<usuario>
SIGPESQ_PASSWORD=<senha>
PREFECT_API_URL=http://127.0.0.1:4200/api
PREFECT_CLIENT_SERVER_VERSION_CHECK_ENABLED=false
HORIZON_TELEGRAM_BOT_TOKEN=<token-do-bot>
HORIZON_TELEGRAM_CHAT_ID=<chat-id-do-grupo-horizon-messages>
```

O adapter tambem aceita `SIGPESQ_USER` como alias para `SIGPESQ_USERNAME`.

Banco Horizon (valores ficticios de desenvolvimento local, em `.env.example`):

```bash
HORIZON_DATABASE_URL=postgresql://horizon:horizon@localhost:5434/horizon
HORIZON_DB_USER=horizon
HORIZON_DB_PASSWORD=horizon
HORIZON_DB_NAME=horizon
HORIZON_DB_PORT=5434
```

`HORIZON_MODELO_SQL` (opcional) aponta para outro `ModeloLogicoHorizon.sql`; no
container `app` ele ja aponta para o arquivo montado.

## Notificacoes Telegram

Todos os flows Prefect registram hooks de conclusao para enviar um relatorio ao
Telegram quando terminam em estado `Completed`, `Failed`, `Crashed` ou
`Cancelled`.

O relatorio inclui:

- nome do flow
- nome/id da execucao
- estado final
- horario de conclusao em UTC
- parametros do flow
- URL local do run no Prefect quando `PREFECT_API_URL` ou `PREFECT_UI_URL`
  estiver configurado
- mensagem final do estado, quando houver

Configuracao para o grupo **Horizon Messages**:

```bash
HORIZON_TELEGRAM_BOT_TOKEN=<token-do-bot>
HORIZON_TELEGRAM_CHAT_ID=<chat-id-numerico-do-grupo>
```

Tambem sao aceitos os aliases genericos:

```bash
TELEGRAM_BOT_TOKEN=<token-do-bot>
TELEGRAM_CHAT_ID=<chat-id-numerico-do-grupo>
```

Observacao: a Bot API do Telegram envia mensagens por `chat_id`, nao pelo nome
visual do grupo. Adicione o bot ao grupo **Horizon Messages** e configure o ID
numerico em `HORIZON_TELEGRAM_CHAT_ID`.

## Validacao

Testes direcionados:

```bash
.venv/bin/python -m pytest tests/test_sigpesq_adapter.py tests/test_sigpesq_full_flow.py -q
```

Suite completa:

```bash
make test
```

Testes do banco Horizon (usam um schema temporario, apagado no fim; sem o
`horizon-db` no ar, os testes que dependem dele sao pulados):

```bash
HORIZON_DATABASE_URL=postgresql://horizon:horizon@localhost:5434/horizon \
PYTHONPATH=. .venv/bin/python -m pytest -q tests
```

Consulta rapida no PostgreSQL:

```bash
psql postgresql://horizon:horizon@localhost:5434/horizon \
  -c "select count(*) from iniciativas"
```

Auditorias uteis (pipeline legado):

```bash
make etl-report
make etl-report-md
make tracking-audit-report
make audit-duplicates
```

Consultas rapidas no SQLite (pipeline legado):

```bash
.venv/bin/python - <<'PY'
import sqlite3

conn = sqlite3.connect("db/horizon.db")
cur = conn.cursor()
for table in ["persons", "research_groups", "initiatives", "advisorships", "fellowships"]:
    count = cur.execute(f"select count(*) from {table}").fetchone()[0]
    print(f"{table}: {count}")
conn.close()
PY
```

## Troubleshooting

### Login SigPesq falha (HTTP 429 — rate limit)

O portal SigPesq aplica rate limit em logins rapidos consecutivos e retorna HTTP 429.

O adapter detecta automaticamente o 429 e reintenta com backoff exponencial:

| Tentativa | Espera antes |
|-----------|-------------|
| 1         | —           |
| 2         | 60s         |
| 3         | 120s        |

Configuravel via `.env`:

```env
SIGPESQ_429_WAIT_SECONDS=60   # base de espera (default: 60)
SIGPESQ_MAX_RETRIES=3         # maximo de tentativas (default: 3)
```

Se o 429 persistir apos todas as tentativas, verifique se ha outra instancia do
pipeline rodando em paralelo ou se o portal esta temporariamente bloqueando o IP.

### Relatorios antigos aparecem na carga

O comportamento esperado e limpar `data/raw/sigpesq` antes do download. Se
arquivos antigos aparecerem, confirme que a execucao passou por
`SigPesqAdapter.extract()` e nao chamou diretamente uma rotina parcial de
persistencia.

### Prefect nao responde

Use:

```bash
make prefect-status
make prefect-server
```

### Banco Horizon indisponivel

Suba o PostgreSQL e confira a URL no `.env`:

```bash
make horizon-db-up
docker compose ps horizon-db
```

Sem `HORIZON_DATABASE_URL`, o pipeline para com uma mensagem pedindo o bloco do
banco Horizon de `.env.example`.

### Registros pulados na carga PostgreSQL

Abra `data/reports/carga_postgres.json`: `pendencias` lista o que nao foi
gravado e o motivo; `revisar` lista o que foi gravado mas pede conferencia.

### Flow sem servidor Prefect falha

O modo temporario do Prefect pode quebrar com versoes novas de FastAPI e
Starlette. Use o servidor do Docker (`make prefect-server`), como os alvos do
`make` ja fazem.

### Banco local inconsistente (SQLite)

Recrie o banco e rode a fonte desejada:

```bash
make db-reset
make ingest-sigpesq
```

## Documentacao complementar

- `docs/flows-and-entrypoints.md`: organizacao dos flows e comandos.
- `docs/architecture.md`: visao arquitetural.
- `docs/outputs-and-artifacts.md`: artefatos produzidos.
- `docs/reports/`: relatorios e snapshots.
- `../ModeloLogicoHorizon.sql`: modelo logico do banco Horizon (33 tabelas).
