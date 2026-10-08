# Contract Adapters

Contract-first no ScrumAIDev e um conceito, nao uma stack obrigatoria. Escolha o adaptador conforme o projeto derivado.

## HTTP / REST

- Formato recomendado: OpenAPI 3.1 em `docs/contracts/<bounded_context>_<resource>.yaml`.
- Validadores possiveis: Spectral, Redocly CLI, openapi-cli.
- Geracao opcional: TypeScript types, Pydantic schemas, clients SDK.
- Mocks opcionais: MSW, Prism, WireMock.

## Eventos e Mensageria

- Formato recomendado: AsyncAPI ou schema YAML versionado.
- Validadores possiveis: AsyncAPI CLI, schema registry, testes de consumidor.
- Inclua exemplos de payload, versao do evento, produtor, consumidor e regra de compatibilidade.

## GraphQL

- Fonte de verdade: schema GraphQL versionado ou SDL.
- Validadores possiveis: graphql-schema-linter, checks de breaking change.
- Relacione queries/mutations relevantes com US, Spec e BDD.

## Consumer-Driven Contracts

- Use Pact ou equivalente quando consumidores e provedores evoluirem separadamente.
- O contrato deve registrar consumidor, provedor, cenarios e compatibilidade esperada.

## Frontend Mocks

- Use MSW, fixtures ou mocks de camada de service apenas quando o projeto precisar desenvolver UI sem backend real.
- Fixtures devem refletir o contrato documentado, nao dados internos acidentais.
- Nao adicione mocks ao framework base; adicione ao projeto derivado quando ele atingir Nivel 3 ou 4.

## Backend Contract Tests

- Use Schemathesis, Dredd, Pact provider tests ou testes de integracao que validem request/response contra o contrato.
- O comando real deve ser documentado em `docs/context.md`.

## Criterio de Ativacao

Um adaptador sai de documentado para executavel quando:

- a stack foi registrada no manifesto;
- existe comando local reproduzivel;
- o gate correspondente existe no `Makefile`;
- o PR mostra evidencia de execucao ou de dispensa.
