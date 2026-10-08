# 📐 Architecture Decision Records (ADR)

Esta pasta registra as **decisões arquiteturais** tomadas no projeto.

## Por que ADRs?

Código novo é escrito por quem não estava presente nas decisões originais. ADRs respondem "por que foi feito assim?" antes que alguém precise perguntar.

## Formato

Cada ADR é um arquivo Markdown: `ADR-NNN_titulo-da-decisao.md`.

Use `docs/adr/adr_template.md` como base. O template inclui rastreabilidade para US, Spec, Contract, BDD e Nivel ScrumAIDev.

```markdown
# ADR-001: Título da Decisão

**Status:** Proposto | Aceito | Substituído por ADR-XXX | Depreciado
**Data:** YYYY-MM-DD
**Decisores:** [nomes ou @handles]

## Contexto
Por que essa decisão precisou ser tomada? Qual era o problema?

## Opções Consideradas
1. Opção A — prós e contras
2. Opção B — prós e contras

## Decisão
Qual opção foi escolhida e por quê.

## Consequências
O que muda positivamente e o que se torna mais difícil com essa decisão.
```

## Como criar um novo ADR

```
Crie um ADR para a decisão: [descreva a decisão]

Use o template de `docs/adr/adr_template.md` e salve como `ADR-NNN_titulo.md`
```

## Índice

| ADR | Título | Status |
|---|---|---|
| *(nenhum ainda — crie o primeiro!)* | | |
