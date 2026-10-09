# ETL SRC/Ifes

Pipeline de extração (scraping), transformação e carga dos dados do **SRC (Sistema de Registro de Ações de Extensão) do Ifes** para um banco **PostgreSQL** normalizado.

## Sumário

- [Visão geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Início rápido](#início-rápido)
- [Instalação detalhada](#instalação-detalhada)
  - [1. Ambiente virtual (venv)](#1-ambiente-virtual-venv)
  - [2. Dependências e navegador](#2-dependências-e-navegador)
  - [3. Credenciais (.env)](#3-credenciais-env)
  - [4. Banco de dados (Docker)](#4-banco-de-dados-docker)
- [Executando o ETL](#executando-o-etl)
- [Visualizando os dados (VS Code)](#visualizando-os-dados-vs-code)
- [Recriar o banco do zero](#recriar-o-banco-do-zero)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Solução de problemas](#solução-de-problemas)
- [Documentação relacionada](#documentação-relacionada)

## Visão geral

1. Raspa as Ações do campus configurado (hoje: **Serra**) com Playwright (Chromium headless).
2. Grava no PostgreSQL via SQLAlchemy (UPSERT, pode rodar várias vezes).
3. Se houver credenciais no `.env`, também extrai Equipe Executora e Público-Alvo.

**As tabelas são criadas automaticamente** ao rodar `run_etl_final.py` (ele espera o Postgres ficar pronto e executa `create_all`).

## Pré-requisitos

| Software | Versão mínima | Verificar |
|---|---|---|
| Python | 3.10 (testado em 3.14) | `python3 --version` |
| `python3-venv` / pip | pip ≥ 25 | `python3 -m venv --help` |
| Docker Engine | 24+ | `docker --version` |
| Docker Compose (plugin v2) | 2.20+ | `docker compose version` |
| Git | qualquer | `git --version` |
| Chromium (Playwright) | instalado no passo 2 | — |
| VS Code + extensão **PostgreSQL Explorer** | recente | para visualizar os dados |

Porta livre: **5432** (PostgreSQL).
Em Linux/Debian/Ubuntu, se faltar o venv: `sudo apt install python3-venv`.
Seu usuário deve conseguir rodar Docker sem `sudo` (`sudo usermod -aG docker $USER`, depois relogar).

## Início rápido

Todos os comandos são executados **na pasta do ETL** (a que contém este README).

```bash
python3 -m venv venv
source venv/bin/activate            # Windows (PowerShell): .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
cp .env.example .env                # opcional, edite com seu login do SRC
docker compose up -d
python run_etl_final.py
```

## Instalação detalhada

### 1. Ambiente virtual (venv)

O venv isola as dependências do projeto das do sistema.

```bash
python3 -m venv venv
```

**Ativação** (precisa ser refeita a cada novo terminal):

| Sistema | Comando |
|---|---|
| Linux / macOS | `source venv/bin/activate` |
| Windows PowerShell | `.\venv\Scripts\Activate.ps1` |
| Windows CMD | `venv\Scripts\activate.bat` |

Ativado, o prompt mostra `(venv)` e `which python` (Linux/macOS) aponta para `.../venv/bin/python`. Para sair: `deactivate`.

> No PowerShell, se a ativação for bloqueada: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
> Alternativa sem ativar: chame direto `venv/bin/python run_etl_final.py` (Windows: `venv\Scripts\python.exe`).

### 2. Dependências e navegador

Com o venv ativo:

```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

As versões estão fixas em [requirements.txt](requirements.txt). O segundo comando baixa o Chromium usado no scraping; no Linux, se faltarem bibliotecas do sistema:

```bash
playwright install --with-deps chromium    # pede sudo
```

### 3. Credenciais (.env)

Necessárias apenas para **Equipe Executora** e **Público-Alvo** (áreas restritas do SRC). Sem elas, o ETL carrega só os dados públicos das Ações e avisa no log.

```bash
cp .env.example .env
```

Edite o `.env`:

```env
USER=seu_usuario_do_portal_src
PASSWORD=sua_senha_do_portal_src
```

O `.env` está no `.gitignore`; **nunca o commite**.

### 4. Banco de dados (Docker)

```bash
docker compose up -d
docker compose ps        # postgres deve aparecer como "healthy"
```

Sobe o PostgreSQL 15 em `localhost:5432`. Os dados persistem no volume `postgres_data`.

Credenciais do banco (fixas, ambiente local de desenvolvimento):

| Campo | Valor |
|---|---|
| Servidor | `localhost` |
| Porta | `5432` |
| Usuário | `etl_user` |
| Senha | `etl_password` |
| Base | `src_db` |

## Executando o ETL

Com venv ativo e Docker rodando:

```bash
python run_etl_final.py
```

O script:
1. aguarda o PostgreSQL aceitar conexões e **cria as tabelas** se não existirem;
2. extrai e grava as Ações do campus Serra;
3. se houver `.env`, extrai Equipe/Público-Alvo (3 workers paralelos);
4. finaliza com `🏁 Processo de carga 100% Finalizado!`.

É seguro reexecutar: a carga é idempotente (UPSERT).

## Visualizando os dados (VS Code)

Use a extensão **PostgreSQL Explorer** (ID `ckolkman.vscode-postgres`, ou busque "PostgreSQL" por Chris Kolkman na aba Extensões).

1. Instale a extensão e abra o painel **PostgreSQL** na barra lateral.
2. Clique em **+ (Add Connection)** e informe, na ordem pedida:
   - Hostname: `localhost`
   - Usuário: `etl_user`
   - Senha: `etl_password`
   - Porta: `5432`
   - SSL: `Standard Connection` (sem SSL)
   - Database: `src_db`
   - Nome da conexão: livre (ex.: `SRC Local`)
3. Expanda `SRC Local` → `src_db` → `public` → `Tables` para ver as tabelas; clique com o botão direito numa tabela para "Select Top 1000".
4. Para consultas: botão direito na conexão → **New Query** e execute (`Ctrl+Enter`):

```sql
-- Ações e o campus a que pertencem
SELECT a.titulo, c.nome AS campus
FROM acao a
JOIN local_acao la ON a.id = la."fk_Acao_id"
JOIN campus c ON la."fk_Campus_id" = c.id;
```

> O banco precisa estar de pé (`docker compose ps`) e o ETL já executado para haver dados.
> Alternativa por terminal: `docker exec -it src_etl_postgres psql -U etl_user -d src_db`.

## Recriar o banco do zero

> ⚠️ **Apaga todos os dados** do schema `public`.

```bash
python recreate_db.py
```

Para destruir também o volume do Docker: `docker compose down -v`.

## Estrutura do projeto

```
.
├── run_etl_final.py     # orquestrador principal (cria tabelas + carga)
├── recreate_db.py       # reseta schema e recria tabelas
├── docker-compose.yml   # PostgreSQL
├── requirements.txt     # dependências Python (versões fixas)
├── .env.example         # modelo de credenciais
├── src_etl/
│   ├── etl/             # scraper, pipeline, modelos e acesso ao banco
│   └── dashboard/       # geração de painéis/relatórios
├── docs/                # documentação de projeto
└── DICIONARIO_DADOS_SRC.md
```

## Solução de problemas

| Sintoma | Causa / solução |
|---|---|
| `command not found: python` / `externally-managed-environment` | Venv não ativado. Rode `source venv/bin/activate`. |
| `ModuleNotFoundError` | Venv inativo ou `pip install -r requirements.txt` não executado. |
| `BrowserType.launch: Executable doesn't exist` | Rode `playwright install chromium`. |
| `Host system is missing dependencies` | `playwright install --with-deps chromium`. |
| `Aguardando PostgreSQL...` e falha ao final | Docker parado: `docker compose up -d` e confira `docker compose ps`. |
| `port is already allocated` (5432) | Outro serviço usa a porta; pare-o ou altere `ports` no compose (e `DATABASE_URL` em `src_etl/etl/database.py`). |
| `permission denied ... docker.sock` | Adicione seu usuário ao grupo `docker` e relogue. |
| Participações ignoradas | `.env` ausente ou sem `USER`/`PASSWORD`. |
| Falha de login no SRC | Confira usuário/senha no portal; o site aceita uma sessão por vez. |

## Documentação relacionada

- [DICIONARIO_DADOS_SRC.md](DICIONARIO_DADOS_SRC.md) — dicionário de dados
- [docs/](docs) — descoberta, requisitos e histórias de usuário
