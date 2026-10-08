# Task Breakdown: [US-001] Modelagem Física do Banco (SQLAlchemy)

## Backend Tasks

- [x] **[TASK-001] Configurar PostgreSQL via Docker Compose**
  - Estimativa: 1 hora
  - Dependencias: Nenhuma
  - Criterios de conclusao: `docker-compose.yml` criado rodando um `postgres:15-alpine` expondo porta 5432.

- [x] **[TASK-002] Criar infraestrutura de conexão do SQLAlchemy**
  - Estimativa: 1 hora
  - Dependencias: TASK-001
  - Criterios de conclusao: `src_etl/etl/database.py` criado contendo `engine`, `SessionLocal` e `Base` (SQLAlchemy 2.0).

- [x] **[TASK-003] Mapear classes do ORM (Modelos Relacionais)**
  - Estimativa: 2 horas
  - Dependencias: TASK-002
  - Criterios de conclusao: Criação dos modelos `Acao`, `Atividade`, `Pessoa`, `Participacao` refletindo o `DICIONARIO_DADOS_SRC.md`, incluindo Foreign Keys e restrições de nulidade. Função `init_db()` para criar schema.

## Testing Tasks

- [ ] **[TASK-004] Testar Inicialização do Banco**
  - Estimativa: 1 hora
  - Dependencias: TASK-003
  - Criterios de conclusao: Script/teste simples que roda `init_db()` com sucesso contra o Postgres no Docker, verificando se tabelas são criadas sem falhas de sintaxe/relacionamento.
