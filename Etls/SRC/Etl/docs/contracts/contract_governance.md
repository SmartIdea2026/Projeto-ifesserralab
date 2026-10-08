# Contract Governance

Esta pasta concentra contratos governados para boundaries observaveis do sistema.

O ScrumAIDev trata contract-first como uma camada progressiva. No framework base, contratos ficam documentados em `docs/contracts/` (Nivel 2). Validadores, mocks, tipos gerados e testes de contrato so entram quando o projeto derivado escolher a stack e registrar comandos reais (Niveis 3 e 4).

## O que fica em `docs/contracts/`

- `docs/contracts/<nome>.yaml`: contrato real versionado para API, evento, webhook ou integracao
- `docs/contracts/http_api_contract_template.yaml`: base para contratos HTTP em OpenAPI 3.1
- `docs/contracts/error_standard.yaml`: schema compartilhado e respostas padrao para erros
- `docs/contracts/adapters.md`: guia de adaptadores opcionais por stack

Nao coloque aqui contratos completos de um produto exemplo, fixtures reais, tipos gerados ou mocks acoplados a stack. Esses artefatos pertencem ao projeto derivado quando ele ativar Nivel 3 ou 4.

## Quando usar Contract-first

Adote contract-first por boundary quando a US alterar:

- request ou response de API
- parametros, filtros, paginacao ou ordenacao observaveis
- upload, download, exportacao ou importacao
- payloads de eventos, jobs assincronos ou webhooks
- erros observaveis por clientes
- schemas compartilhados entre frontend, backend e integracoes

Nao use contrato governado para mudancas puramente internas, estruturais ou apenas visuais.

## Niveis de contract-first

| Nivel | Uso | Evidencia |
|---|---|---|
| 2 | Contrato documentado | YAML governado em `docs/contracts/` e linkado na US/PR |
| 3 | Contrato executavel | `make validate-contract` ou `make test-contract` delega para validador real |
| 4 | Contrato automatizado em CI | CI executa validacao, mocks/tipos/testes quando configurados |

Se um projeto ainda nao tem runner, mantenha o contrato no Nivel 2 e registre a dispensa de automacao no PR.

## Papel de cada artefato

| Artefato | Papel principal |
|---|---|
| US | valor de negocio e criterio de aceite |
| Spec | comportamento, escopo, restricoes e Touch List |
| Contract | interface consumivel por clientes e integracoes |
| BDD | evidencia do comportamento observavel |

## Como derivar o contrato da US e do modelo de dados

1. Comece pelo objetivo da US e pelo fluxo observado pelo consumidor.
2. Liste os recursos, comandos, estados e erros que o consumidor precisa entender.
3. Use o modelo de dados para validar nomes de entidades, cardinalidade, ids, enums e estados.
4. Modele requests e responses a partir da necessidade do cliente, nao a partir da estrutura interna do banco.
5. Defina exemplos de sucesso, validacao, conflito, nao encontrado e erro de processamento quando forem observaveis.

## Regras para mensagens de erro

- Nao use mensagens genericas quando a causa for conhecida.
- Cada erro observavel deve ter `code` estavel e legivel por maquina.
- `title` deve ser curto e estavel.
- `detail` deve explicar o problema real de forma segura, sem expor internals.
- Quando houver validacao de campos, use `invalidParams`.
- Use `docs/contracts/error_standard.yaml` como base compartilhada.

## Convencao sugerida de nomes

- HTTP: `docs/contracts/<bounded_context>_<resource>.yaml`
- Eventos: `docs/contracts/<bounded_context>_<event>_event.yaml`
- Webhooks: `docs/contracts/<bounded_context>_<webhook>.yaml`

## Checklist minimo do contrato

- Metadata com `user_story`, `spec` e referencias ao modelo de dados quando existirem
- Schemas de request e response
- Exemplos minimos de sucesso e erro
- Reuso do padrao de erro compartilhado
- Status codes observaveis e coerentes
- Mensagens de erro especificas e seguras
