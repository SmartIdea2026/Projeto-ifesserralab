---
description: Plan a sprint with AI assistance
---

# Sprint Planning Workflow

Este workflow orienta você através do processo de planejamento de sprint com assistência de IA.

## Pré-requisitos

- Product backlog priorizado
- Velocity da sprint anterior (se aplicável)
- Capacidade do time conhecida
- 📂 **Pastas de Documentação Verificadas:** Padrão `/docs/sprints/` e `docs/product_backlog.md`

## Passos

### 0. Verificar Documentação Existente 🕵️‍♂️

Antes de qualquer coisa, a IA **deve** identificar qual sprint planejar:

**Prompt sugerido:**
```
Verifique a pasta /docs/sprints/ e liste todos os arquivos sprint_planning_*.md existentes.

1. Identifique o maior número de sprint já existente (ex: se sprint_planning_04.md existe, a próxima é Sprint 05).
2. Verifique se já existe um sprint_planning para a sprint que estamos prestes a iniciar.
   - Se JÁ EXISTE: use o arquivo existente como base, NÃO crie um novo. Salte o passo 1.
   - Se NÃO EXISTE: crie o arquivo novo com o número correto no passo 1.
3. Verifique o status atual do docs/product_backlog.md.
4. Liste quais user stories foram concluídas e quais ficaram pendentes.
5. Se houver retrospectiva da sprint anterior, resuma os action items para considerarmos neste planejamento.
```

> ⚠️ **IMPORTANTE:** Nunca crie `sprint_planning_N+2.md` pulando uma sprint. Sempre confirme o número correto antes de criar ou editar qualquer arquivo.

### 1. Preparar o ambiente

Copie o template de sprint planning para sua pasta de projeto:

```bash
mkdir -p docs/sprints
cp templates/sprint_planning.md docs/sprints/sprint_planning_NN.md
```

Substitua `NN` pelo proximo numero sequencial identificado no passo 0, por exemplo `docs/sprints/sprint_planning_01.md`.

### 1.5. Analisar Exemplos (Opcional e Condicional) 🚀

**Esta etapa é opcional e só deve ser executada se você tiver exemplos de design/código para analisar.**
Esta etapa NÃO deve ser executada automaticamente em todas as execuções.

---

#### 🔍 Verificação de contexto (OBRIGATÓRIA)

Antes de analisar exemplos, verifique `docs/project_manifest.md`:

- Existe `docs/product_backlog.md`?
- Qual o valor de **Contexto processado**?

---

#### 🧠 Regras de decisão

Se **Contexto processado = sim**:
- NÃO reanalise automaticamente os exemplos
- Use o backlog existente como fonte principal
- Pule para o passo 2

Se **Contexto processado = não**:
- Execute a análise completa dos exemplos

Se **Contexto processado = parcial**:
- Avalie necessidade de reanálise antes de executar

Se o usuário solicitar explicitamente:
- Execute a análise independentemente do estado

---

#### 🧪 Execução da análise (quando aplicável)

Peça à IA para analisar:

**Prompt sugerido:**
```
Analise os exemplos na pasta examples/figma/ e:

1. Se houver arquivo `.zip`, trate-o como fonte principal de contexto, extraia sua estrutura e analise o conteúdo do projeto antes dos demais arquivos
2. Identifique todas as features e funcionalidades visíveis, descritas ou implementadas
3. Crie uma lista completa de user stories necessárias para implementar o sistema
4. Organize as stories em epics lógicos
5. Sugira um roadmap inicial de sprints para implementação
6. Estime story points com base na complexidade aparente
7. Identifique dependências técnicas e funcionais entre as stories
8. Para cada story de UI derivada de telas já presentes no ZIP, classifique explicitamente a estratégia como `paridade_exata`, `adaptacao_controlada` ou `estrutural`. O padrão deve ser `paridade_exata`; qualquer exceção precisa ser justificada.
9. Se o ZIP contiver um frontend funcional e navegável, registre a estratégia de adoção como `copia_integral_frontend`.
10. Para cada story que corresponda a uma tela/rota já pronta no ZIP, declare se a implementação deve:
   - partir da cópia integral do frontend já trazido pelo ZIP
   - ajustar integrações, dependências, testes e contratos sobre essa base
   Simplificações visuais ou reinterpretações da UI só podem ocorrer com anuência explícita do usuário.
11. Gere um product_backlog.md completo baseado nesta análise em `docs/product_backlog.md`. Entretanto, se já existir `docs/product_backlog.md`, preserve o conteúdo relevante, identifique lacunas com base nos exemplos analisados e proponha uma atualização incremental antes de alterar o backlog.

Importante:
- Use o `.zip` como fonte principal quando existir
- Use imagens, PDFs, screenshots e documentos como contexto complementar

- Importante: Gere o backlog completo, mas mantenha o backlog editável para ajustes humanos
- Importante: Não transforme um frontend funcional do ZIP em backlog de placeholders. Se o produto espera reproduzir essa interface, planeje a entrada por cópia integral do frontend ou por fatias reais já existentes no ZIP.

```

#### c) Revise e ajuste o backlog gerado

- ✏️ Edite user stories para maior clareza
- 📊 Ajuste estimativas se necessário
- 🎯 Reorganize prioridades conforme estratégia de negócio
- ➕ Adicione stories adicionais que possam estar faltando
- 🧭 Marque explicitamente quando uma story exige **paridade visual exata** com uma tela exportada do Figma
- 🧱 Marque explicitamente quando a sprint exige **cópia do frontend completo do ZIP** ou **cópia da tela/página original do ZIP** em vez de recriação manual

**📚 Consulte:** `examples/figma/readme.md` para guia completo de uso.

**Se não tiver exemplos, pule para o passo 2.**

### 2. Revisar Product Backlog

Peça à IA para analisar o product backlog:

**Prompt sugerido:**
```
Analise o product_backlog.md e sugira quais user stories devem ser priorizadas
para a próxima sprint considerando:
- Dependências entre stories
- Valor de negócio
- Complexidade técnica
- Capacidade estimada do time de [X] pontos
```

### 3. Definir Sprint Goal

Trabalhe com a IA para criar um objetivo claro:

**Prompt sugerido:**
```
Baseado nas user stories selecionadas [US-XXX, US-YYY, US-ZZZ],
sugira um Sprint Goal conciso e inspirador que una todas essas histórias.
```

### 4. Estimar Story Points

Para cada user story, peça estimativas:

**Prompt sugerido:**
```
Analise a user story [US-XXX] e sugira uma estimativa em story points
considerando:
- Complexidade técnica
- Incertezas
- Esforço necessário
- Riscos conhecidos
```

### 5. Identificar Riscos e Dependências

**Prompt sugerido:**
```
Analise as user stories selecionadas e identifique:
- Dependências entre elas
- Riscos técnicos
- Possíveis bloqueadores
- Sugestões de mitigação
```

### 6. Criar Task Breakdown (opcional)

Para stories complexas, faça o breakdown imediatamente:

```
Use o workflow /feature-development para fazer o breakdown 
da user story [US-XXX]
```

### 7. Validar Capacidade

**Prompt sugerido:**
```
Temos capacidade de [X] story points. Selecionamos stories totalizando [Y] pontos.
Avalie se essa sprint está balanceada ou se devemos ajustar o escopo.
```

### 8. Finalizar Documentação

- Preencha todos os campos de `docs/sprints/sprint_planning_NN.md`
- Revise com o time
- Commit no repositório

```bash
git add docs/sprints/sprint_planning_NN.md
git commit -m "docs: Sprint [NUMERO] planning"
```

### 8.5. Publicar Planejamento no GitHub

Depois que backlog e sprint estiverem revisados localmente, publique a estrutura no GitHub antes de começar a implementação da sprint:

```text
Execute o workflow /publish-github-planning para:
- criar ou atualizar Epic issues
- criar ou atualizar User Story issues
- amarrar Epic -> US
- criar ou atualizar a Iteration da sprint
- criar Task issues para as US selecionadas
- amarrar US -> Task
- gravar os links de volta nos arquivos locais
```

> Regra recomendada: use um unico workflow publico de publicacao. Nao separe backlog e sprint em comandos independentes para uso normal do time, pois isso aumenta o risco de sincronizacao parcial.

### 9. Atualizar Project Manifest 🧠

Após finalizar o sprint planning, atualize o `docs/project_manifest.md`:

- Status do projeto → DEFINED
- Nome do projeto → baseado no domínio identificado
- Origem do contexto → ex: examples/figma/NOME_DO_ARQUIVO.zip ou backlog manual
- Confiança do contexto → média ou alta
- Última atualização → docs/sprints/sprint_planning_NN.md

## Outputs Esperados

- ✅ `docs/sprints/sprint_planning_NN.md` preenchido
- ✅ Sprint goal definido
- ✅ User stories estimadas e priorizadas
- ✅ Riscos identificados
- ✅ Time alinhado sobre o escopo

## Consumo de Contexto (Estimado)
- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimização: [Breve descrição]

## Arquivos Utilizados
- Arquivos lidos para contexto: [...]
- Arquivos alterados: [se houver]
- Arquivos criados: [se houver]
- Leitura parcial relevante: [se aplicável]

## Dicas

- Mantenha o sprint goal focado e inspirador
- Seja conservador nas estimativas iniciais
- Reserve 20% da capacidade para imprevistos
- Revise a Definition of Done antes de comprometer
