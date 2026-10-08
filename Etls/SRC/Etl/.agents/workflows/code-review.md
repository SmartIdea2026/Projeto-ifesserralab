---
description: Conduct AI-assisted code review
---

# Code Review Workflow

Este workflow guia voce atraves de um code review completo com assistencia de IA.

## Quando usar

- Antes de criar ou aprovar Pull Request
- Durante desenvolvimento para feedback intermediario
- Para analise de codigo legado
- Para garantir qualidade antes de merge

Se util, use `templates/pr_review_template.md` como checklist complementar ao review.
Esse template e complementar e nao substitui este workflow.

## Passos

### 0. Checagem de Consistência entre Artefatos (condicional)

Execute este passo **apenas se** pelo menos uma condição for verdadeira:

- Nivel ScrumAIDev da US for 2, 3 ou 4
- `Behavior change` = YES
- Multiplas US, Specs ou Contracts foram tocados no mesmo PR

Caso nenhuma condicao se aplique, pule para o Passo 1 e registre "Checagem de consistencia: nao aplicavel" no relatorio final. Este passo existe para pegar contradicao entre artefatos antes do merge — nao rode por padrao em mudancas pequenas, pois isso aumenta o contexto lido sem necessidade (ver `docs/token_budget.md`).

**Prompt sugerido:**
```text
Compare os seguintes artefatos entre si e aponte contradicoes, duplicacoes ou lacunas de cobertura:
- User Story: docs/stories/US-XXX.md
- Sprint: docs/sprints/sprint_planning_NN.md
- Spec: docs/specs/<nome>.yaml (ou "US nao exige Spec")
- Contract: docs/contracts/<nome>.yaml (ou "US nao exige Contract")
- BDD: docs/bdd/<nome>.feature (ou N/A)

Classifique cada achado como:
- Duplicacao
- Contradicao
- Lacuna de Cobertura
- Ambiguidade

Nao aplique nenhuma correcao automaticamente aqui — apenas reporte. Correcoes entram nos passos seguintes deste review.
```

### 1. Preparar Contexto

Identifique o que sera revisado:

```text
Estou fazendo code review de:
- PR #[numero] / Branch [nome]
- Relacionado a [US-XXX]
- Spec: [arquivo YAML/MD ou "US nao exige Spec"]
- Contract: [arquivo YAML em docs/contracts/ ou "US nao exige Contract"]
- BDD: [arquivo .feature ou N/A]
- Nivel ScrumAIDev: [0 | 1 | 2 | 3 | 4]
- Behavior change: [YES/NO]
- Arquivos modificados: [lista]

Forneca um resumo das mudancas.
```

### 2. Review de Arquitetura

**Prompt sugerido:**
```text
Analise a arquitetura da solucao implementada:

Verifique:
- Aderencia aos padroes de arquitetura do projeto
- Separacao de responsabilidades
- Acoplamento e coesao
- Principios SOLID
- Design patterns apropriados
- Fronteiras entre Spec, Contract e implementacao

Sugira melhorias arquiteturais se necessario.
```

### 3. Review de Code Quality

**Prompt sugerido:**
```text
Revise a qualidade do codigo verificando:

CLEAN CODE:
- Nomes descritivos (variaveis, funcoes, classes)
- Funcoes pequenas e focadas
- Comentarios apenas onde necessario
- Ausencia de codigo duplicado
- Ausencia de magic numbers

DRY PRINCIPLE:
- Repeticao de logica
- Oportunidades de refatoracao

READABILITY:
- Codigo autoexplicativo
- Complexidade ciclomatica
- Aninhamento excessivo

Liste problemas encontrados com sugestoes especificas.
```

### 4. Review de Performance

**Prompt sugerido:**
```text
Analise performance do codigo:

Identifique:
- Loops desnecessarios ou otimizaveis
- Queries N+1 (se aplicavel)
- Carregamento desnecessario de dados
- Operacoes bloqueantes
- Memory leaks potenciais
- Oportunidades de caching

Priorize por impacto.
```

### 5. Review de Security

**Prompt sugerido:**
```text
Faca uma analise de seguranca:

OWASP TOP 10:
- Injection vulnerabilities
- Autenticacao/Autorizacao
- Exposicao de dados sensiveis
- Configuracoes inseguras
- XSS (Cross-Site Scripting)
- Desserializacao insegura
- Componentes vulneraveis
- Logging inadequado
- SSRF

Identifique vulnerabilidades e sugira correcoes.
```

### 6. Review de Error Handling

**Prompt sugerido:**
```text
Revise o tratamento de erros:

Verifique:
- Excecoes sao capturadas apropriadamente
- Mensagens de erro sao claras
- Nao ha exposicao de informacoes sensiveis em erros
- Logs adequados em casos de erro
- Fallbacks definidos
- Validacao de inputs
- Aderencia a `docs/contracts/error_standard.yaml` quando houver Contract
- Ausencia de mensagens genericas quando a causa e conhecida

Liste melhorias necessarias.
```

### 7. Review de Testes

**Prompt sugerido:**
```text
Analise a cobertura e qualidade dos testes:

COBERTURA:
- Porcentagem de cobertura atual
- Gaps de cobertura importantes
- Edge cases nao testados

QUALIDADE:
- Testes sao independentes
- Testes sao deterministicos
- Nomes descritivos
- Assertions apropriadas
- Setup/Teardown adequados

TIPOS:
- Testes unitarios suficientes
- Testes de integracao (se necessario)
- Testes de contract quando houver boundary governado
- Testes E2E (se necessario)
- Se houver BDD, cenarios criticos cobertos e runner executado
- Gates opcionais executados ou dispensados com justificativa (validate-contract/test-contract/test-bdd/test-mock)

Sugira testes adicionais necessarios.
```

### 8. Review de Documentacao

**Prompt sugerido:**
```text
Verifique a documentacao:

CODIGO:
- Comentarios onde necessario (logica complexa)
- Docstrings em funcoes publicas
- README atualizado

APIs:
- Endpoints documentados
- Parametros e respostas descritos
- Exemplos de uso
- Contract atualizado quando houver boundary governado

GOVERNANCA:
- Spec atualizada quando exigida
- Nao ha mudanca de comportamento fora da Spec
- Nao ha mudanca de boundary fora do Contract
- BDD alinhado a Spec quando aplicavel
- Touch List respeitada quando houver Spec governada

Identifique gaps de documentacao.
```

### 9. Verificar Definition of Done

```text
Compare as mudancas com nossa Definition of Done (`docs/definition_of_done.md`):

Liste quais criterios:
- Foram atendidos
- Foram parcialmente atendidos
- Nao foram atendidos

Para cada item nao atendido, sugira acao corretiva.
```

### 10. Gerar Relatorio de Review

**Prompt sugerido:**
```text
Gere um relatorio consolidado do code review incluindo:

## Resumo Executivo
- Status geral: [Aprovar/Aprovar com ressalvas/Requer mudancas]
- Principais pontos positivos
- Principais problemas encontrados

## Detalhamento

### Critico (Must Fix)
- [Lista de problemas criticos]

### Importante (Should Fix)
- [Lista de problemas importantes]

### Sugestoes (Nice to Have)
- [Lista de melhorias sugeridas]

## Checklist Final
- [ ] Rastreabilidade entre US, Spec, Contract, BDD e PR adequada
- [ ] Arquitetura adequada
- [ ] Code quality satisfatoria
- [ ] Performance aceitavel
- [ ] Sem vulnerabilidades criticas
- [ ] Error handling adequado
- [ ] Testes suficientes
- [ ] Documentacao completa
- [ ] Definition of Done atendida

## Comentarios Adicionais
[Notas finais]
```

### 11. Aplicar Feedback (se voce e o autor)

Para cada item do review:

```text
Implemente a correcao para: [item especifico do review]

Explique a abordagem e valide se resolve o problema apontado.
```

### 12. Re-review (se necessario)

Apos correcoes:

```text
Revise as mudancas aplicadas em resposta ao code review.
Verifique se todos os pontos foram adequadamente enderecados.
```

## Outputs Esperados

- Relatorio completo de code review
- Lista priorizada de issues
- Sugestoes concretas de melhoria
- Decisao clara (aprovar ou requer mudancas)

## Consumo de Contexto (Estimado)

- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimizacao: [Breve descricao]

## Templates de Comentarios

### Para aprovar:
```text
LGTM

Code review aprovado.

Destaques positivos:
- [Ponto positivo 1]
- [Ponto positivo 2]

Sugestoes menores para futuro:
- [Sugestao 1]
```

### Para solicitar mudancas:
```text
Requer mudancas

Encontrei alguns pontos que precisam ser enderecados:

CRITICO:
- [Problema critico 1]

IMPORTANTE:
- [Problema importante 1]

Apos as correcoes, solicite novo review.
```

## Dicas

- Seja construtivo, nao apenas critico
- Priorize feedback (critico vs sugestoes)
- Forneca exemplos de codigo quando possivel
- Considere o contexto do projeto
- Equilibre perfeicao com pragmatismo
- Elogie boas praticas encontradas
