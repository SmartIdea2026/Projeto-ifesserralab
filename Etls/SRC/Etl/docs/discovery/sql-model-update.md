# Discovery — Atualização do Modelo SQL

**Status:** DRAFT
**Classificacao de Processo:** NORMAL PROCESS
**Origem:** usuário

## Intent
Adaptar o esquema do banco de dados (SQLAlchemy) gerado pelo ETL para bater exatamente com o diagrama lógico (logicoER) fornecido pelo usuário.

## Problem
O modelo atual do ETL (definido em `database.py`) tem divergências estruturais em relação ao modelo idealizado pelo usuário, principalmente em:
- Regras de `ON DELETE` (ex: CASCADE para lookups de Ação em vez de RESTRICT).
- Colunas ausentes ou diferentes (ex: `Pessoa` não possui `fk_Campus_id` no ER fornecido; `vinculo` em vez de `tipo_vinculo`).
- Relacionamentos incompletos no script do usuário (ex: `fk_Atividade_id???`).

## Users / Stakeholders relevantes
- Desenvolvedores / Analistas de Dados consumindo o banco de dados.

## Current Situation
O banco atual possui restrições `RESTRICT` para evitar deleções acidentais de domínio, possui a coluna `fk_Campus_id` em `Pessoa`, e possui campos como `acao_original_id` necessários para a raspagem de dados do sistema do IFES.

## Desired Outcome
Um modelo `database.py` atualizado que reflita as tabelas e regras de Deleção do script do usuário, com o ETL ainda sendo capaz de realizar os UPSERTs sem quebrar.

## Success Criteria
- O arquivo `database.py` é alterado.
- As regras de Foreign Key acompanham o script (CASCADE, SET NULL, RESTRICT).
- O banco local é recriado e o ETL funciona carregando os dados na nova estrutura.

## Scope

### IN
- Atualização do `database.py` e `crud.py` para refletir as nomenclaturas e chaves estrangeiras.
- Resolução dos "???" no script para apontar corretamente para a chave primária de `Atividade`.

### OUT
- Remover chaves de origem (`acao_original_id`, `atividade_original_id`). O ETL web depende intrinsecamente delas para fazer o UPSERT (evitar duplicatas). Elas serão mantidas como colunas de controle ocultas do negócio principal.

### LATER
- N/A

## Constraints / Feasibility
- O script do usuário definiu `data_cadastro` como `DATE`. Como a fonte retorna uma string (ex: "10/05/2023"), o `crud.py` precisará converter isso para `datetime.date` antes de inserir.

## Assumptions
- [ASSUMPTION] As colunas `id` (Primary Key) que faltaram na declaração de `Atividade`, `EquipeExecucao` e `PublicoAlvo` no logicoER devem ser mantidas para garantir a integridade no SQLAlchemy.
- [ASSUMPTION] Manteremos `acao_original_id` e `atividade_original_id`, pois sem elas o web scraper vai duplicar dados a cada execução.

## Risks
- `ON DELETE CASCADE` em tabelas de domínio (como `TipoAcao` e `Campus`): se alguém apagar um "Campus Serra" da tabela `Campus`, **todas as Ações associadas serão apagadas**.

## Open Questions
- Nenhum bloqueante, os pressupostos resolvem os conflitos.

## Gate G0 — PROBLEM READY

**Status:** APPROVED
**Aprovado pelo usuario:** sim
