# Product Backlog

## Visão Geral
Este backlog contém as histórias de usuário para a refatoração do pipeline ETL do SRC/Ifes, com o objetivo de migrar de um modelo de saída JSON para a inserção direta em um banco de dados relacional OLTP via SQLAlchemy.

## Histórias

| ID | Título | Status | Prioridade |
|---|---|---|---|
| [US-001](./stories/US-001.md) | Modelagem Física do Banco (SQLAlchemy) | TODO | Alta |
| [US-002](./stories/US-002.md) | Lógica de Mapeamento (Pydantic ➡️ SQLAlchemy) e UPSERT | TODO | Alta |
| [US-003](./stories/US-003.md) | Refatoração do Orquestrador ETL (`pipeline.py`) | TODO | Alta |

