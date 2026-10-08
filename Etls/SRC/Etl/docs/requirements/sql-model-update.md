# Requirements — Atualização do Modelo SQL

**Discovery Base:** [docs/discovery/sql-model-update.md]
**Status:** APPROVED

## 1. Regras de Negócio e Lógica
1. O modelo de banco de dados (`database.py`) deve seguir rigorosamente a especificação do diagrama lógico (logicoER) fornecido, mantendo as chaves necessárias para a operação do ETL (`acao_original_id`, `atividade_original_id`).
2. O comportamento de exclusão em cascata (ON DELETE) deve ser mapeado conforme especificado.
3. As conversões de tipos (`data_cadastro` de String para Date) devem ser tratadas no `crud.py` durante o UPSERT.

## 2. UI / UX
- N/A (Backend / Banco de dados)

## 3. Dados e Estado (Schemas/Models)
- **Tabela Pessoa:** Remover coluna `fk_Campus_id`. Coluna `tipo_vinculo` renomeada para `vinculo` (ou mantida mapeada corretamente).
- **Tabela Ação:** `fk_TipoAcao_id`, `fk_Fomento_id`, `fk_Campus_id`, `fk_Natureza_id` receberão `ondelete="CASCADE"`. `fk_Coordenador_id` receberá `ondelete="SET NULL"`. Campo `data_cadastro` passará a ser tipo `Date`.
- **Tabela Atividade:** `fk_Acao_id`, `fk_TipoAtividade_id` receberão `ondelete="CASCADE"`.
- **Tabela Vinculacao:** AcaoVinculante e AcaoVinculada já usam `CASCADE`.
- **Tabela EquipeExecucao:** `fk_Pessoa_id` recebe `RESTRICT`. `fk_Atividade_id` recebe `SET NULL`. `fk_Funcao_id` recebe default/RESTRICT.
- **Tabela PublicoAlvo:** `fk_Pessoa_id` e `fk_Atividade_id` recebem `SET NULL`.

## 4. Integrações e APIs (Contratos)
- N/A

## 5. Segurança, Permissões e Auditoria
- N/A

## 6. Desempenho e Escalabilidade
- N/A

## Gate G1 — REQUIREMENTS READY
**Status:** APPROVED
**Aprovado pelo usuario:** sim (Agilizado via chat)

