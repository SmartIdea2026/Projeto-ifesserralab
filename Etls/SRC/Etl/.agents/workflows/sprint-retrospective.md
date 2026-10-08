---
description: Conduct sprint retrospective with AI insights
---

# Sprint Retrospective Workflow

Este workflow guia a condução de uma retrospectiva de sprint produtiva com assistência de IA.

## Quando usar

- Ao final de cada sprint
- Quando o time identifica necessidade de melhoria
- Como ritual regular de continuous improvement

## Preparação (antes da reunião)

### 1. Coletar Dados da Sprint

**Prompt sugerido:**
```
Analise a sprint [NUMERO] que acabou de finalizar:

Colete métricas de:
- Story points planejados vs completados
- Número de stories concluídas
- Bugs encontrados
- Tempo médio de code review
- Build failures
- Deployment frequency

Fontes: commits, PRs, issues, CI/CD logs
```

### 2. Identificar Padrões

**Prompt sugerido:**
```
Com base nos dados da sprint [NUMERO], identifique:

PADRÕES POSITIVOS:
- Práticas que funcionaram bem
- Melhorias em relação à sprint anterior
- Momentos de alta produtividade

PADRÕES NEGATIVOS:
- Bloqueios recorrentes
- Gargalos identificados
- Onde perdemos tempo

ANOMALIAS:
- Eventos únicos que impactaram a sprint
```

### 3. Preparar Template

```bash
mkdir -p docs/retrospectives
cp templates/retrospective.md docs/retrospectives/sprint_NN_retro.md
```

Substitua `NN` pelo numero da sprint encerrada, por exemplo `docs/retrospectives/sprint_01_retro.md`.

## Durante a Reunião

### 4. Review de Métricas (5 min)

Apresente as métricas coletadas:

```
Crie uma visualização resumida das métricas da sprint para apresentar ao time:
- Story points: planejado vs realizado
- Velocity trend (últimas 3 sprints)
- Quality metrics (bugs, test coverage, etc.)

Formato: tabela markdown
```

### 5. What Went Well? (10 min)

Facilite a discussão:

**Prompt para cada item levantado:**
```
O time mencionou que [item positivo] funcionou bem.

Analise:
- Por que isso funcionou?
- Como podemos replicar em outras áreas?
- Há oportunidade de amplificar esse sucesso?
```

### 6. What Didn't Go Well? (10 min)

**Prompt para cada item levantado:**
```
O time identificou que [item negativo] não funcionou bem.

Analise:
- Qual foi a root cause?
- Já aconteceu antes?
- Há um padrão subjacente?
- Quais são possíveis soluções?
```

### 7. Generate Insights (5 min)

**Prompt sugerido:**
```
Baseado no que discutimos (positivos e negativos), 
identifique:

TOP 3 OPORTUNIDADES DE MELHORIA:
1. [Com maior impacto potencial]
2. [Mais fácil de implementar]
3. [Prevenção de problemas futuros]

Para cada uma, sugira:
- Ação específica
- Responsável sugerido
- Métrica de sucesso
```

### 8. Votação e Priorização (5 min)

Priorize as melhorias:

```
Temos estas sugestões de melhoria:
[lista as sugestões]

Ajude a priorizá-las usando matriz de impacto vs esforço:

| Melhoria | Impacto (1-5) | Esforço (1-5) | Score |
|----------|---------------|---------------|-------|

Recomende quais devemos focar primeiro.
```

### 9. Criar Action Items (10 min)

Para cada melhoria priorizada:

**Prompt sugerido:**
```
Para a melhoria "[descrição]", crie um action item SMART:

- Specific: O que exatamente faremos?
- Measurable: Como mediremos sucesso?
- Achievable: É realista?
- Relevant: Por que é importante?
- Time-bound: Quando será concluído?

Formato:
- [ ] [Ação específica]
  - Responsável: [nome]
  - Prazo: [data]
  - Métrica de sucesso: [como medir]
```

### 10. Review de Action Items Anteriores (5 min)

```
Revise os action items da retrospectiva anterior (sprint [NUMERO-1]):

Para cada item:
- Status: Concluído/Em progresso/Não iniciado
- Se concluído: impacto observado
- Se não concluído: por quê? ainda é relevante?

Recomende quais manter, arquivar ou escalar.
```

## Pós-Reunião

### 11. IA-Generated Summary

**Prompt sugerido:**
```
Gere um resumo executivo da retrospectiva da sprint [NUMERO]:

## 📊 Highlights
- Velocity: [X] pontos
- Principais conquistas: [lista]
- Principais desafios: [lista]

## 🎯 Top 3 Action Items
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

## 💡 Key Insights
- [Insight 1]
- [Insight 2]

## 📈 Trend Analysis
[Comparação com sprints anteriores]

Este resumo será compartilhado com stakeholders.
```

### 12. Documentar e Compartilhar

```bash
# Finalizar documento de retrospectiva
# Commit
git add docs/retrospectives/sprint_NN_retro.md
git commit -m "docs: Sprint [NUMERO] retrospective"
git push
```

### 13. Criar Lembretes

**Prompt sugerido:**
```
Baseado nos action items da retrospectiva, 
crie lembretes/tarefas para:

1. Check-in no meio da sprint
2. Validação antes da próxima retrospectiva

Formato: checklist ou calendar events
```

## Outputs Esperados

- ✅ Retrospectiva documentada
- ✅ Métricas da sprint analisadas
- ✅ 3-5 action items específicos e atribuídos
- ✅ Insights sobre melhorias de processo
- ✅ Time alinhado sobre próximos passos

## Consumo de Contexto (Estimado)
- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimização: [Breve descrição]

## Formatos Alternativos

### Mad/Sad/Glad
```
Categorize o feedback em:
- 😠 Mad: O que nos frustrou
- 😢 Sad: O que nos desapontou
- 😊 Glad: O que nos alegrou

E gere insights para cada categoria.
```

### Start/Stop/Continue
```
Organize o feedback em:
- ▶️ Start: O que devemos começar a fazer
- ⏹️ Stop: O que devemos parar de fazer
- ▶️ Continue: O que devemos continuar fazendo
```

### Timeline
```
Crie uma timeline da sprint marcando:
- Momentos de alta energia
- Momentos de bloqueio
- Eventos importantes
- Entregas chave

E analise os padrões.
```

## Dicas

- Mantenha a retrospectiva psicologicamente segura
- Foque em ações, não em culpa
- Limite action items a 3-5 (menos é mais)
- Acompanhe action items anteriores
- Varie o formato para manter engajamento
- Celebre as vitórias!
- Use dados, não apenas opiniões
- IA ajuda com insights, mas time decide as ações
