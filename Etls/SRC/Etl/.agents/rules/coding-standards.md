---
trigger: always_on
description: Padrões de código do framework ScrumAIDev
---

# Coding Standards

## Regras Globais (aplicam a qualquer stack)

- Prefira seguir padrões já existentes no repositório antes de introduzir novas convenções.
- Faça mudanças pequenas, coerentes com o contexto atual e fáceis de revisar.
- Validação redundante: Frontend + Backend.
- Testes: ao criar um componente ou módulo, sugira o arquivo de teste correspondente.
- Em documentação Markdown, prefira tabelas para dados estruturados e links internos consistentes.
- Se a mudança alterar comportamento observável, boundary, regra de negócio ou erro externo, verifique se há Spec, Contract, BDD ou dispensa explícita conforme `docs/decisoes_governanca_us_spec_bdd.md`.
- Quando houver Contract governado, status codes, schemas e mensagens de erro devem seguir `docs/contracts/` e `docs/contracts/error_standard.yaml`.

---

## Regras por Stack

### TypeScript
- Nunca use `any` sem justificativa explícita; prefira tipos definidos.

### React
- Prefira componentes funcionais.
- Extraia lógica complexa para custom hooks.
- Prefira `getByRole` / `getByLabel` nos testes.
- Garanta acessibilidade em elementos interativos.

### Vue 3
- Use Composition API com `<script setup>` em código novo.
- Extraia lógica complexa para composables.
- Garanta acessibilidade em elementos interativos.

### Python (FastAPI / Django)
- Type hints obrigatórios; use `pydantic` para validação de entrada.
- Organize responsabilidades de forma clara (por exemplo: Router → Service → Repository, quando aplicável).
- Trate exceções de forma explícita e consistente.

---

## Estrutura de Pastas Padrão (gerada pelo `/init-project`)
Use a estrutura gerada pelo workflow `/init-project` como ponto de partida, mas adapte ao contexto do repositório e às decisões arquiteturais existentes.
