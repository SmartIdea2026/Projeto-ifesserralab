# Discovery & Requirements — Operating Model

## Objetivo

Evitar o salto prematuro `Ideia → User Story` sem transformar ScrumAIDev em um processo pesado.

A experiencia publica recomendada e:

```text
/scope-idea "ideia"
   ↓
Work Classification
   ↓
LIGHT PROCESS | NORMAL PROCESS | HEAVY PROCESS
   ↓
[Discovery/Requirements quando necessario]
   ↓
Stories
   ↓
Agile Delivery
   ↓
Engineering as Needed
   ↓
Agentic Execution
```

## Tres momentos antes da User Story

Para trabalhos NORMAL PROCESS/HEAVY PROCESS, o usuario percebe apenas:

1. **Discovery** — entendemos o problema certo?
2. **Requirements** — o que precisa ser verdadeiro/entregue?
3. **Stories** — qual fatia de valor entra no backlog?

Intent, Problem, Context, Scope, Constraints, Success, FR, BR, NFR, scenarios e assumptions sao analisados **internamente** e consolidados nesses tres momentos.

## Review & Adjust e obrigatorio

Uma proposta da IA nunca vira `PROBLEM READY`, `REQUIREMENTS READY` ou backlog aprovado apenas porque foi gerada.

Em cada checkpoint o agente deve:

1. mostrar o que propoe de forma legivel;
2. destacar decisoes importantes e assumptions;
3. permitir ao usuario:
   - aprovar;
   - alterar texto;
   - adicionar item;
   - remover item;
   - reclassificar item;
   - responder duvidas;
4. aplicar as mudancas;
5. mostrar um resumo/diff do que mudou;
6. somente entao marcar o gate como aprovado.

### Exemplo — Requirements Review

```text
Derivei:
- 7 requisitos funcionais;
- 5 regras de negocio;
- 3 requisitos nao funcionais.

Decisao importante proposta:
- criar uma nova versao nao altera automaticamente a versao estavel.

A proposta completa esta abaixo e em docs/requirements/requirements.md.
Voce pode aprovar, editar, adicionar, remover ou reclassificar qualquer item.
```

O usuario nunca deve ser limitado a "sim/nao".

## Inspiracao externa, adaptada ao ScrumAIDev

Discovery incorpora de forma compacta mecanismos usados pelo AI-DLC (AWS) em Ideation: intent framing, problem, stakeholders/context, feasibility/constraints, scope e success criteria.

Requirements incorpora de forma compacta a analise de completude em seis perspectivas usada pelo AI-DLC: functional, non-functional, user scenarios, business/domain context, technical context e quality attributes.

Esses conceitos (Discovery, Requirements Analysis, completude de requisitos) sao vocabulario padrao de engenharia de requisitos e produto (BABOK, Design Thinking, Dual-Track Agile) — nao sao exclusivos do AI-DLC, mas foi a leitura do AI-DLC que motivou trazer esse rigor para o ScrumAIDev de forma explicita. Ver `docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md` para o registro completo da decisao, incluindo por que os nomes de comando (`/scope-idea` em vez de `/start`, sem um `/stories` separado) foram escolhidos deliberadamente diferentes do AI-DLC.

ScrumAIDev deliberadamente **nao copia a quantidade de stages/artefatos, o codigo ou o texto** do AI-DLC. O valor e absorvido em dois artefatos compactos e checkpoints editaveis, com nomenclatura e granularidade proprias do ScrumAIDev.

## Artefatos canonicos

- `docs/discovery/<slug>.md`
- `docs/requirements/<slug>.md`
- `docs/stories/US-XXX_<slug>.md`

Para um projeto novo, os primeiros arquivos podem usar `project` como slug.

## Exemplo completo

Veja `examples/agent-evolution/README.md` para uma interação ilustrativa completa de `/scope-idea` até a proposta de Stories, usando um domínio real (um sistema para acompanhar a evolução de agentes de IA).

## Gates internos

### G0 — PROBLEM READY

Somente quando:
- intent e problema estao claros;
- publico/contexto relevante e conhecido;
- IN/OUT/LATER foram delimitados quando necessario;
- restricoes criticas foram registradas;
- sucesso pode ser reconhecido;
- nenhuma pergunta bloqueante permanece aberta;
- usuario revisou/ajustou e aprovou a proposta.

### G1 — REQUIREMENTS READY

Somente quando:
- requisitos possuem IDs estaveis;
- FR/BR/NFR relevantes estao claros;
- scenarios/edge cases essenciais foram considerados;
- assumptions e constraints estao explicitos;
- open questions bloqueantes foram resolvidas;
- usuario revisou/ajustou e aprovou a proposta.

## Compatibilidade com Scrum

Discovery e Requirements alimentam o backlog, mas nao substituem:
- User Story;
- refinement;
- Sprint Planning;
- Definition of Done;
- Retrospective.

Depois de `REQUIREMENTS_READY`, o Passo 0 (Modo Backlog) de `/create-user-story` produz um backlog proposto e sugere o primeiro vertical slice. O usuario pode reorganizar, dividir, unir, adicionar ou remover stories antes da aprovacao.
