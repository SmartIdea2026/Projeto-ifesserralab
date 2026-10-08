# ScrumAIDev Maturity Model

Este modelo permite evoluir rastreabilidade tecnica sem transformar o framework em um projeto fullstack especifico.

## Niveis

| Nivel | Nome | Objetivo | Artefatos minimos | Gates |
|---|---|---|---|---|
| 0 | Processo agil + agentes + templates | Organizar trabalho, papeis, workflows e templates | `AGENTS.md`, `.agents/`, `templates/`, `docs/project_manifest.md` | `make lint/test/typecheck/build` podem ser no-op |
| 1 | Spec/BDD/DoD governados | Registrar comportamento, escopo e conclusao | `docs/decisoes_governanca_us_spec_bdd.md`, `docs/specs/`, `docs/bdd/`, `docs/definition_of_done.md` | BDD pode ser revisao manual |
| 2 | Contract-first documentado | Rastrear boundaries observaveis sem exigir stack | `docs/contracts/*.yaml`, `docs/contracts/error_standard.yaml`, `docs/contracts/contract_governance.md` | `make validate-contract` pode ser docs-only |
| 3 | Contract-first executavel | Validar contratos quando a stack escolher ferramentas | validador OpenAPI/AsyncAPI/Pact/Schemathesis/MSW ou equivalente | `make validate-contract`, `make test-contract`, `make test-bdd` |
| 4 | CI, mocks, tipos e testes de contrato | Automatizar rastreabilidade ponta a ponta | CI executando gates, mocks/fixtures/tipos gerados quando aplicavel | CI verde com gates executaveis |

## Regra de Leveza

O framework base permanece no Nivel 0-2. Niveis 3 e 4 so devem ser ativados quando o projeto derivado registrar a decisao de stack e os comandos reais em `docs/project_manifest.md` e `docs/context.md`.

Nao copie artefatos especificos de um produto para o framework base, como OpenAPI completo de dominio, fixtures reais, tipos gerados, Docker obrigatorio ou CI acoplado a uma stack. Esses itens pertencem ao projeto derivado.

## Como Escolher o Nivel de Uma User Story

1. Se a US apenas organiza processo, template ou documentacao, use Nivel 0.
2. Se altera comportamento observavel, regra de negocio ou fluxo de usuario, use pelo menos Nivel 1.
3. Se altera API, evento, webhook, payload, erro observavel ou schema compartilhado, use pelo menos Nivel 2.
4. Se o projeto ja possui validador/runner configurado, eleve para Nivel 3.
5. Se CI, mocks, tipos gerados e testes de contrato ja existem, mantenha Nivel 4.

## Politica de Decisao Rapida

Use esta sequencia antes de criar a story, fazer o breakdown ou abrir o PR:

1. Esta mudanca altera apenas processo, documentacao, templates ou organizacao?
   - Sim: Nivel 0.

2. Esta mudanca altera comportamento percebido por usuario, cliente, regra de negocio ou fluxo de UI?
   - Sim: pelo menos Nivel 1.

3. Esta mudanca altera interface entre sistemas, frontend/backend, payload, status code, erro externo, evento, webhook, schema compartilhado, upload, download ou integracao?
   - Sim: pelo menos Nivel 2.

4. Existe comando real e reproduzivel para validar contrato, executar BDD ou testar provider/consumer?
   - Sim: use Nivel 3 e registre o comando em `docs/context.md`.

5. Esse comando ja roda no CI junto com mocks, fixtures, geracao de tipos ou testes de contrato?
   - Sim: use Nivel 4.

Se mais de uma resposta for "sim", use o maior nivel aplicavel. Se a automacao ainda nao existir, nao force Nivel 3/4; registre a ausencia do runner e mantenha a mudanca no menor nivel documentado suficiente.

## O Que E Obrigatorio

Sempre:

- Registrar o Nivel ScrumAIDev escolhido.
- Justificar por que ele e o menor nivel suficiente.
- Declarar se a mudanca exige Spec governada.
- Declarar se a mudanca exige Contract governado.
- Linkar ou dispensar BDD quando houver comportamento observavel.
- No PR, informar quais gates foram executados ou por que ainda nao se aplicam.

Por condicao:

- Mudanca de comportamento observavel exige pelo menos Nivel 1.
- Mudanca de boundary tecnico exige pelo menos Nivel 2.
- Runner real configurado exige execucao dos gates de Nivel 3 aplicaveis.
- CI configurado para esses gates exige Nivel 4 verde antes do merge.

## Evidencia Esperada no PR

- Nivel adotado para a mudanca.
- Links para US, Spec, Contract e BDD quando aplicavel.
- Dispensa explicita quando Spec, Contract ou BDD nao forem necessarios.
- Comandos executados ou justificativa de gate ainda nao aplicavel.
