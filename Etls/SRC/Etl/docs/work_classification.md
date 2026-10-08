# Work Classification — LIGHT PROCESS / NORMAL PROCESS / HEAVY PROCESS

ScrumAIDev usa **classificacao de trabalho** para escolher o menor processo suficiente.
Ela e diferente do Nivel de Maturidade ScrumAIDev 0-4 (rigor tecnico/rastreabilidade) e do Token Budget (`docs/token_budget.md`, LIGHT/NORMAL/HEAVY CONTEXT — quanto o agente le na sessao). Os nomes se parecem de proposito (mesma logica de "menor suficiente"), mas sao tres eixos independentes; nao assuma que coincidem.

## LIGHT PROCESS

Use quando a mudanca e pequena, localizada, de baixo risco e com objetivo ja claro.

Exemplos:
- correcao de documentacao;
- bug trivial com causa conhecida;
- ajuste pequeno sem mudanca de boundary;
- manutencao operacional simples.

Fluxo padrao:

```text
classify → execute → validate
```

Discovery e Requirements formais sao pulados, salvo quando surgir ambiguidade bloqueante.

## NORMAL PROCESS

Use para features e mudancas de produto com escopo delimitado, mas que exigem entendimento do problema antes da Story.

Fluxo padrao:

```text
classify
  ↓
discover (compacto)
  ↓
review/adjust
  ↓
requirements
  ↓
review/adjust
  ↓
create-user-story (Modo Backlog)
  ↓
review/adjust
  ↓
agile delivery
  ↓
engineering as needed
  ↓
agentic execution
```

Limite recomendado: ate 3 perguntas bloqueantes por checkpoint antes de consolidar uma proposta.

## HEAVY PROCESS

Use para iniciativas novas, escopo amplo, alto risco, multiplos stakeholders, boundaries, seguranca, dados sensiveis, integracoes relevantes ou grande incerteza.

O fluxo continua simples para o usuario, mas a analise interna e mais profunda:
- intent/problem/context ampliados;
- stakeholders relevantes;
- viabilidade e restricoes;
- riscos e assumptions;
- criterios de sucesso;
- completude de requisitos em seis dimensoes;
- perguntas adicionais somente quando necessarias.

Fluxo padrao:

```text
classify
  ↓
discovery+
  ↓
review/adjust
  ↓
requirements+
  ↓
review/adjust
  ↓
create-user-story (Modo Backlog)
  ↓
review/adjust
  ↓
agile delivery
  ↓
engineering as needed
  ↓
agentic execution
```

## Human override

A IA recomenda a classificacao e explica a justificativa, mas o usuario pode trocar LIGHT PROCESS/NORMAL PROCESS/HEAVY PROCESS antes de prosseguir.

Formato minimo de saida:

```text
Classificacao de Processo recomendada: NORMAL PROCESS
Motivo: nova feature com regras ainda parcialmente abertas.
Processo ativado: Discovery compacto → Requirements → Stories.

Opcoes: [Aprovar] [Alterar classificacao] [Explicar melhor]
```

## Principio

> Mais inteligencia interna, menos comandos para o usuario.

O usuario nao deve conhecer todos os mecanismos internos para obter um bom processo. `/scope-idea` orquestra a classificacao e ativa somente as capacidades necessarias.
