# Discovery — Retrabalho e Extração Final do ETL

**Status:** DRAFT
**Classificacao de Processo:** NORMAL PROCESS (Agilizado)
**Origem:** usuário

## Intent
Limpar inconsistências do código/banco e rodar a extração completa dos dados de Ações e Participações (equipes, público-alvo, atividades) para o Campus Serra hoje, sem mudar a estrutura atual do banco.

## Problem
Inconsistências anteriores (como o problema da constraint de unicidade no processo e o erro de schema com `nome_slug`) já foram alinhadas, mas precisamos assegurar que a base de dados final seja alimentada 100% de ponta a ponta.

## Users / Stakeholders relevantes
- Usuário (necessita dos dados extraídos o mais rápido possível hoje)

## Current Situation
O banco foi recriado com sucesso e contém 206 ações únicas, mas pode faltar a execução e validação da etapa de `run_participacoes` que preenche atividades, equipes e público-alvo, e garantia de que tudo roda num script de pipeline coeso.

## Desired Outcome
Um script final de execução que puxe as Ações e as Participações em uma tacada só, validando que os dados preencham as tabelas normalizadas com sucesso.

## Success Criteria
- ETL ponta-a-ponta extrai as ações e os detalhes (participações).
- Nenhuma falha de constraint ou silent error durante a persistência.
- Tabela Ação e tabelas associadas populadas com sucesso.

## Scope
### IN
- Consolidação do script de execução (`pipeline.run` e `pipeline.run_participacoes`).
- Execução do ETL para o Campus Serra hoje e carregamento local.

### OUT
- Mudar o modelo de dados atual do banco.
- Raspagem de outros campi.

### LATER
- Integrações ou automações agendadas (CI/Cron).

## Constraints / Feasibility
- O tempo é curto; a execução e validação precisam ser ágeis e diretas no código existente.

## Assumptions
- [ASSUMPTION] O modelo normalizado recém-criado em `database.py` já atende às necessidades.

## Risks
- A extração de participações no portal pode esbarrar em timeouts se os workers forem excessivos.

## Open Questions
- Nenhum bloqueante. Apenas agir rápido.

## Gate G0 — PROBLEM READY

**Status:** APPROVED
**Aprovado pelo usuario:** sim
