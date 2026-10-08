---
description: Develop a feature from user story to completion
---

# Feature Development Workflow

Este workflow guia o desenvolvimento completo de uma feature, desde o breakdown ate a conclusao.

## Quando usar

- Ao iniciar desenvolvimento de uma user story
- Durante uma sprint
- Para garantir que nada seja esquecido no processo

## Passos

### 0. Confirmar publicacao do planejamento no GitHub

Antes de iniciar a implementacao da sprint, confirme que:

- a US possui GitHub US Issue
- a sprint possui GitHub Iteration ou Milestone registrados
- o breakdown tecnico possui Task Issues quando a US ja entrou na sprint

Se isso ainda nao existir, execute antes:

```text
/publish-github-planning
```

### 0.5 Avaliar delegacao segura

Antes de delegar qualquer parte da implementacao:

- mantenha um agente principal como dono do fluxo, da integracao final e do relatorio
- use `explorer sidecars` apenas para leitura, pesquisa e inventario paralelo
- use `worker sidecars` apenas quando houver write scope exclusivo
- nao permita escrita concorrente em artefatos canonicos como:
  - `docs/project_manifest.md`
  - `docs/product_backlog.md`
  - `docs/sprints/`
  - `docs/stories/`
  - `docs/tasks/`
  - `docs/specs/`
  - `docs/contracts/`
  - `docs/bdd/`
  - `.agents/workflows/`
- se a proxima acao do fluxo depender imediatamente do resultado, faca localmente em vez de delegar
- se houver handoff relevante, registre-o em `templates/context_summary.md`

Casos seguros para delegacao:

- exploracao de frontend, backend e testes em paralelo
- inventario de touch list
- revisao especializada por lente
- implementacao em fatias com arquivos diferentes

Casos a evitar:

- task pequena e sequencial
- multiplos agentes alterando o mesmo modulo
- atualizacao concorrente de artefato de governanca

### 1. Revisar User Story e Insumos do Figma (Prioridade)

Certifique-se de entender completamente a US e **sempre verifique se o escopo dela ja existe no codigo-fonte exportado pelo Figma** (ex: `examples/figma/extracted/src/`).

Se o codigo React do Figma ja existir para esta feature:

- Nao recrie do zero.
- Se o ZIP trouxer um frontend funcional completo, o default e **copiar o frontend completo para `frontend/`** e so depois ajustar dependencias, imports, testes, integracoes e estrutura local.
- Se a tela ou rota ja existir no ZIP e a expectativa da story for visual, o default e **paridade visual maxima** com o Figma exportado.
- Se multiplas telas da mesma feature ja existirem no ZIP e formarem um frontend navegavel coerente, o default e **copiar o frontend completo**.
- Nao substitua a tela existente por placeholder, versao resumida ou redesign para "caber na sprint" sem realinhar a story ou sprint e registrar a decisao explicitamente.
- Nao converter uma pagina pronta do ZIP em "shell + placeholder" se a expectativa da sprint ou story for demonstrar a interface do Figma.
- Nao usar estrategia alternativa de adocao quando o ZIP trouxer um app navegavel completo.
- Nao alterar a interface copiada do ZIP sem anuencia explicita do usuario registrada nos artefatos da entrega.

```text
Revise a user story [US-XXX] e resuma:
- O objetivo de negocio
- Se o codigo ja existe no ZIP do Figma e deve ser migrado
- Qual o nivel de fidelidade esperado (`paridade_exata`, `adaptacao_controlada` ou `estrutural`)
- Qual o modo de adocao esperado (`copia_integral_frontend`)
- Quais ajustes sao estritamente necessarios sobre a base ja copiada do ZIP
- Criterios de aceitacao
- Restricoes tecnicas
- Definition of Done aplicavel
```

### 2. Validar Governanca e Fazer Task Breakdown

Antes do breakdown, decida a governanca da US:

- Escolha o menor Nivel ScrumAIDev suficiente, conforme `docs/maturity_model.md`.
- Se a US exigir Spec governada, crie ou atualize a Spec em YAML em `docs/specs/`.
- Se a US exigir Contract governado, crie ou atualize o Contract em YAML em `docs/contracts/` antes de implementar o boundary.
- Se houver erros observaveis, alinhe-os a `docs/contracts/error_standard.yaml`.
- Se a Spec ou o Contract forem relevantes para comportamento observavel, derive BDD em `docs/bdd/`.
- Se a US nao exigir Spec ou Contract, registre no breakdown e no PR as dispensas explicitas.
- Use `docs/decisoes_governanca_us_spec_bdd.md` como fonte canonica dessas decisoes.
- Use `docs/contracts/adapters.md` apenas quando o projeto derivado decidir ativar validadores, mocks, tipos gerados ou testes de contrato.

**Prompt sugerido:**
```text
Avalie a user story [US-XXX] e responda:
- Nivel ScrumAIDev recomendado: [0 | 1 | 2 | 3 | 4]
- Justificativa do nivel e por que niveis mais altos nao sao necessarios agora
- Exige Spec governada? [sim/nao]
- Exige Contract governado? [sim/nao]
- Justificativa objetiva
- Spec esperada: [docs/specs/<nome>.yaml ou N/A]
- Contract esperado: [docs/contracts/<nome>.yaml ou N/A]
- BDD esperado: [docs/bdd/<nome>.feature ou N/A]
- Erros observaveis que precisam de `docs/contracts/error_standard.yaml`
- Gates opcionais aplicaveis: [validate-contract | test-contract | test-bdd | test-mock | N/A]
- Comandos reais ja configurados em `docs/context.md`: [sim/nao]
- A UI desta story deve ser reproduzida com paridade visual exata do ZIP? [sim/nao]
- Touch List preliminar: [arquivos/pastas afetados]
```

Se Nivel ScrumAIDev for 2+, `Behavior change` for YES, ou a estimativa passar de 8 pontos, preencha tambem a secao "Checagem de Principios" do breakdown antes de detalhar as tasks.

**Prompt sugerido (apenas quando a condicao acima se aplicar):**
```text
Antes de detalhar as tasks de [US-XXX], responda:
- Esta e a abordagem mais simples que atende a US? Se nao, qual e a mais simples e por que foi rejeitada?
- Ha alguma dependencia externa nova sendo introduzida? Se sim, ela ja foi aprovada?
- O escopo respeita a Touch List da Spec (quando houver)?

Preencha a tabela de Complexidade Aceita apenas se alguma resposta indicar desvio da abordagem mais simples.
```

Crie o arquivo de breakdown:

```bash
mkdir -p docs/tasks
cp templates/task_breakdown.md ./docs/tasks/breakdown_[US-XXX].md
```

Como o breakdown e um artefato de planejamento e rastreabilidade, ele deve ficar em `docs/tasks/` e nao em uma pasta `tasks/` na raiz, a menos que o projeto documente explicitamente outra convencao.

**Prompt sugerido:**
```text
Faca o breakdown tecnico da user story [US-XXX] em tasks especificas.

Organize por:
- Backend tasks
- Frontend tasks
- Testing tasks
- Documentation tasks
- DevOps/Infrastructure tasks

Se houver UI ja existente no ZIP do Figma:
- crie uma task explicita de copia do frontend completo ou da fatia real correspondente
- crie tasks separadas apenas para os ajustes necessarios apos a copia (imports, dependencias, testes, integracao)
- se alguma simplificacao for realmente necessaria, registre a justificativa no breakdown antes de implementar

Se houver boundary governado:
- crie uma task explicita de Contract antes da implementacao
- crie tasks para validar requests, responses e erros observaveis
- se houver delegacao, marque explicitamente quais tasks sao elegiveis para `explorer sidecar` e quais podem ir para `worker sidecar`
- para `worker sidecar`, registre o write scope esperado no breakdown antes de implementar

Para cada task inclua:
- Estimativa em horas
- Dependencias
- Criterios de conclusao especificos
- Relacao com Spec, Contract, BDD e Touch List quando aplicavel
```

### 3. Validar Branch e Estado do Worktree

Antes da primeira alteracao de codigo ou documentacao da US, execute uma checagem explicita:

```bash
git status --short --branch
```

Regras obrigatorias:

- Se a branch atual for `main` ou `develop`, **crie a branch tematica antes de editar qualquer arquivo**.
- Se a branch atual ja for uma branch tematica compativel com a US, siga normalmente.
- Se o worktree estiver limpo, prossiga para criacao da branch quando necessario.
- Se o worktree estiver sujo com mudancas nao relacionadas a US, **nao misture a entrega automaticamente**:
  - registre o bloqueio no relatorio
  - explique quais arquivos ja estavam modificados
  - alinhe com o usuario se deve seguir em nova branch, separar o escopo ou concluir primeiro o que ja esta em andamento

Convencoes:

- `feat/<id>-<slug>` para feature
- `fix/<id>-<slug>` para correcao
- `refactor/<id>-<slug>` para refatoracao
- `docs/<id>-<slug>` ou `chore/<id>-<slug>` para mudancas documentais ou processuais

### 4. Criar Branch

```bash
git checkout -b feat/[ID]-[titulo-curto]
```

Se a branch ja existir e estiver correta para a US, nao recrie; apenas registre essa condicao e prossiga.

### 5. Implementacao Iterativa

Para cada task no breakdown:

**Prompt de implementacao:**
```text
Implemente a task [TASK-XXX]: [descricao]

Requisitos:
- Seguir padroes de codigo do projeto
- Incluir tratamento de erros
- Adicionar logs adequados
- Comentar logica complexa
- Respeitar a Touch List quando houver Spec governada
- Respeitar o Contract quando houver boundary governado
- Nao usar mensagens de erro genericas quando a causa for conhecida
- Se a task for delegada, respeitar estritamente o write scope definido para o sidecar
```

**Apos cada implementacao:**
```text
Revise o codigo implementado para [TASK-XXX] verificando:
- Aderencia aos padroes
- Possiveis bugs
- Otimizacoes
- Edge cases nao tratados
- Aderencia a Spec, Contract e error standard quando existirem
```

### 6. Escrever Testes e Validar Cenarios

**Prompt para testes unitarios:**
```text
Crie testes unitarios para [componente/funcao] cobrindo:
- Casos de sucesso
- Casos de erro/excecao
- Edge cases
- Validacoes de input

Meta: > 80% de cobertura
```

**Executar testes:**
```bash
npm test
# ou
pytest
# ou o comando apropriado do seu projeto
```

Quando houver Contract governado:

- valide se requests, responses, status codes e exemplos batem com `docs/contracts/<nome>.yaml`
- valide erros observaveis contra `docs/contracts/error_standard.yaml`
- rode `make validate-contract` e `make test-contract` quando houver validador/runner real
- se o projeto ainda estiver em Nivel 2, registre que a validacao e documental e que a automacao ainda nao se aplica
- documente o comando do validador em `docs/context.md` quando houver automacao

Quando houver Spec ou Contract relevantes com BDD executavel:

- atualize os cenarios em `docs/bdd/`
- execute o runner documentado em `docs/context.md`
- registre o resultado na validacao da task ou do PR

### 7. Verificar Definition of Done e Governanca

```text
Compare a implementacao atual com a Definition of Done (`docs/definition_of_done.md`) e liste os itens que:
- Ja foram completados
- Estao em progresso
- Ainda nao foram iniciados
```

Verifique tambem:

- Se o nivel ScrumAIDev escolhido continua adequado
- Se a US exigia Spec e ela foi atualizada
- Se a US exigia Contract e ele foi atualizado
- Se o BDD foi criado ou atualizado quando aplicavel
- Se a Touch List foi respeitada
- Se as dispensas de Spec e Contract foram registradas quando cabiveis

### 8. Code Review com IA

**Prompt para review:**
```text
Faca um code review completo das mudancas para [US-XXX]:

Verifique:
- Code quality e clean code principles
- Performance issues
- Security vulnerabilities
- Best practices
- Documentacao adequada
- Testes suficientes
- Aderencia a Spec, Contract e BDD quando existirem
- Mensagens de erro observaveis especificas e seguras

Seja critico e sugira melhorias especificas.
```

### 9. Refatorar baseado no feedback

Aplique as sugestoes do review:

```text
Refatore o codigo conforme as sugestoes:
[liste as sugestoes especificas do review]

Mantenha os testes passando.
```

### 10. Commit & Push

```bash
git add .
git commit -m "feat(api): implementar [descricao curta] [US-XXX]"
```

```bash
git push origin <tipo>/[ID]-[titulo-curto]
```

### 11. Criar Pull Request

O formato oficial de PR vive em `.github/pull_request_template.md`.
O bloco abaixo e uma referencia operacional local e nao substitui o template versionado do repositorio.

**Template de PR:**
```markdown
## User Story
[US-XXX] [Titulo]

## Spec / Contract / Ticket
[link ou ID rastreavel]
- Spec: [docs/specs/<nome>.yaml ou "US nao exige Spec"]
- Contract: [docs/contracts/<nome>.yaml ou "US nao exige Contract"]
- BDD: [docs/bdd/<nome>.feature ou N/A]
- Nivel ScrumAIDev: [0 | 1 | 2 | 3 | 4]

## Mudancas
- [Mudanca 1]
- [Mudanca 2]

## Riscos / Rollback
- Riscos:
- Rollback:

## Behavior change
- [ ] YES
- [ ] NO

## Checklist
- [ ] Todos criterios de aceitacao atendidos
- [ ] Commits seguem Conventional Commits com scope
- [ ] CI verde (lint/test/typecheck/build)
- [ ] Gates opcionais executados ou dispensados com justificativa (validate-contract/test-contract/test-bdd/test-mock)
- [ ] 1 reviewer aprovado
- [ ] Se houver impacto arquitetural, seguranca ou `Behavior change = YES`, segundo reviewer solicitado
- [ ] Spec, Contract e BDD atualizados quando aplicavel
- [ ] Se a US nao exige Spec ou Contract, as dispensas foram registradas
- [ ] Definition of Done completa
- [ ] Documentacao atualizada

## Como testar
1. [Passo 1]
2. [Passo 2]

## Screenshots (se aplicavel)
[Imagens]
```

### 12. Validacao Final

Peca a IA para validar o PR:

```text
Analise o Pull Request para [US-XXX] e verifique se:
- Todos os criterios de aceitacao foram atendidos
- Definition of Done esta completa
- Nao ha regressoes
- Codigo esta pronto para producao
- Spec, Contract e BDD estao coerentes
```

## Outputs Esperados

- Feature completamente implementada
- Testes com boa cobertura
- Spec, Contract e BDD atualizados quando aplicavel
- Documentacao atualizada
- Pull Request criado
- Definition of Done completa

## Consumo de Contexto (Estimado)

- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimizacao: [Breve descricao]

## Arquivos Utilizados

- Arquivos lidos para contexto: [...]
- Arquivos alterados: [...]
- Arquivos criados: [se houver]
- Leitura parcial relevante: [se aplicavel]

## Dicas

- Faca commits pequenos e frequentes
- Execute testes localmente antes de push
- Use a convencao de branch `feat/`, `fix/` ou `refactor/`
- Nao introduza mudanca de comportamento sem Spec ou dispensa explicita
- Nao introduza mudanca de boundary sem Contract ou dispensa explicita
- Peca review de IA em etapas intermediarias
- Mantenha o Definition of Done sempre visivel
- Atualize o task breakdown conforme progride
