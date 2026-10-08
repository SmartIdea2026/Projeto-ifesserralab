# Decisoes de governanca US, Spec, Contract e BDD

Referencia central das decisoes para o fluxo Agile + Spec-and-Contract-Anchored do framework.

## Decisoes diretas

| Tema | Decisao |
|---|---|
| Formato das Specs governadas | YAML em `docs/specs/` |
| Formato dos contratos governados | YAML em `docs/contracts/` |
| Estilo default para contratos HTTP | OpenAPI 3.1 |
| Tarefas sem Spec governada | Spec curta em Markdown ou criterios claros no backlog/task |
| Modelo de erro padrao | `docs/contracts/error_standard.yaml` |
| Runner de BDD | Executado diretamente por runner do projeto; comando documentado em `docs/context.md` |
| Spec relevante exige BDD | Sim, quando descreve comportamento observavel |
| Touch List | Fica na propria Spec YAML e define o escopo permitido |
| Maturidade progressiva | `docs/maturity_model.md` define Niveis 0-4 |

## Regras de decisao

### 1. Quando uma User Story exige Spec governada

Crie ou atualize uma Spec governada quando a US alterar pelo menos um destes pontos:

- comportamento observavel de API, UI ou regra de negocio
- regras de negocio, autorizacao, seguranca ou rollback sensivel
- multiplas areas do codigo que pedem escopo explicito
- comportamento assinado entre frontend, backend e integracoes que precisa de Touch List

Se nenhum desses pontos se aplicar, a US pode seguir sem Spec governada. Nesse caso, registre `US nao exige Spec` com justificativa curta.

### 2. Quando uma User Story exige Contract governado

Crie ou atualize um contrato governado quando a US alterar pelo menos um destes pontos de boundary:

- request, response, headers, query params ou status codes de API
- payloads de eventos, webhooks, filas ou jobs assincronos
- formatos de upload, download, exportacao ou integracoes externas
- erros observaveis por clientes, incluindo validacao e conflitos de negocio
- schemas compartilhados entre frontend, backend e consumidores externos

Se a mudanca for puramente interna, estrutural ou apenas visual, o contrato pode ser `N/A`. Nesse caso, registre `US nao exige Contract` com justificativa curta.

O Contract governado nasce documentado em Nivel 2. Ele so vira executavel em Nivel 3 quando houver validador ou runner real documentado em `docs/context.md`, e so vira Nivel 4 quando os gates entrarem no CI.

### 3. Relacao entre US, tarefas tecnicas, Spec, Contract e BDD

- `US-XX`: item de valor e negocio no backlog de produto
- `F-001`, `B-001`, `R-001`, `T-001`: itens tecnicos no backlog operacional
- `Spec`: descreve comportamento, escopo, restricoes e Touch List
- `Contract`: descreve a interface consumivel por sistemas, UI ou integracoes
- `BDD`: materializa comportamento observavel descrito na Spec e, quando aplicavel, no Contract
- Uma mesma US pode exigir Spec e Contract ao mesmo tempo
- Quando Spec ou Contract nascerem de uma US, registre `user_story: US-XX`

### 4. Como derivar um Contract da US e do modelo de dados

- Comece pelo objetivo da US e pelo fluxo observavel, nao pelas tabelas internas.
- Use o modelo de dados para validar nomes de entidades, cardinalidade, enums, ids e estados do ciclo de vida.
- Nao exponha colunas, chaves internas, nomes de tabelas ou estruturas acidentais do banco sem necessidade.
- Modele requests e responses a partir do que o consumidor precisa enviar, receber e interpretar.
- Inclua exemplos de sucesso, validacao, conflito e nao encontrado quando esses cenarios forem observaveis.

### 5. Padrao para mensagens de erro

- Use `docs/contracts/error_standard.yaml` como fonte canonica para o envelope e os principios de erro.
- Nao use mensagens genericas quando a causa for conhecida.
- Cada erro observavel deve ter `code` estavel e legivel por maquina.
- `title` deve ser curto e estavel; `detail` deve explicar o problema real de forma segura.
- Erros de validacao devem apontar parametros invalidos sempre que possivel.
- Logs internos podem conter mais contexto tecnico, mas a resposta externa nao deve expor stack trace, SQL, segredos, ids sensiveis ou caminhos internos.

### 6. Quando BDD e obrigatorio

BDD e obrigatorio quando a Spec ou o Contract descreverem comportamento observavel, por exemplo:

- fluxos de UI
- regras de negocio visiveis ao usuario
- comportamento de API
- contratos e integracoes com efeito observavel
- erros de validacao, autorizacao, conflito ou processamento que mudem a experiencia do consumidor

BDD pode ser dispensado com justificativa quando a mudanca for puramente interna ou estrutural e nao descrever comportamento observavel.

### 7. Nomenclatura de arquivos

- Spec: `docs/specs/<nome>.yaml`
- Contract: `docs/contracts/<nome>.yaml`
- Padrao de erro: `docs/contracts/error_standard.yaml`
- BDD principal: `docs/bdd/<nome>.feature`
- Excecao: quando a mesma Spec cobrir dominios distintos, pode haver mais de um `.feature`, por exemplo `docs/bdd/<nome>_api.feature` e `docs/bdd/<nome>_ui.feature`
- Todo `.feature` deve referenciar a Spec no topo com `# Spec: docs/specs/<nome>.yaml`
- Todo Contract deve registrar, em metadata, o caminho da US, da Spec e do modelo de dados relevante quando existirem

### 8. Touch List

- A Touch List da Spec YAML e a fonte unica de verdade para o escopo permitido
- Arquivos fora da Touch List nao devem ser alterados sem autorizacao explicita
- Areas protegidas podem ser declaradas na propria Spec
- Quando houver Contract governado, a Touch List deve cobrir os pontos de implementacao impactados pelo boundary

### 9. Modelo de Persistencia de User Stories e Specs

- Enquanto `Status` da US for diferente de `Done`: a US e a Spec/Contract associados sao documentos **vivos** — podem ser editados in-place conforme o entendimento evolui.
- Quando `Status` da US virar `Done`: o arquivo da US vira **historico congelado**. Nao reabra nem reescreva uma US concluida para acomodar um requisito novo.
- Um requisito novo ou uma mudanca de comportamento apos `Done` exige uma **nova US**, mesmo que o tema seja o mesmo. A nova US pode referenciar a antiga (`Relacionada a: US-XX`).
- Excecao: correcoes de erro factual (typo, link quebrado, formatacao) em uma US `Done` sao permitidas sem virar nova US.

## Fluxo operacional resumido

1. Refinar a User Story
2. Escolher o nivel ScrumAIDev minimo para a mudanca
3. Decidir se a US exige Spec governada
4. Decidir se a US exige Contract governado
5. Se exigir, criar ou atualizar a Spec YAML em `docs/specs/`
6. Se exigir, criar ou atualizar o Contract YAML em `docs/contracts/`
7. Se Spec ou Contract forem relevantes para comportamento observavel, derivar BDD em `docs/bdd/`
8. Implementar respeitando a Touch List e o padrao de erro
9. Rodar testes, validar exemplos do Contract e o runner BDD quando aplicavel
10. Abrir PR com links para US, Spec, Contract e BDD, ou com as dispensas explicitas
