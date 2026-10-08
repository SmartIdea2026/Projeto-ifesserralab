# Definition of Done

Uma mudanca so esta pronta quando atende os criterios abaixo.

## 1. Rastreabilidade e Escopo

- Ha story, spec, contract, ticket ou ADR vinculada e atualizada.
- O Nivel ScrumAIDev da mudanca foi registrado e justificado.
- Quando o time usar GitHub Planning, Epic, US e Task issues relevantes estao vinculadas nos artefatos locais.
- Se a User Story exigir Spec governada, a Spec YAML foi criada ou atualizada e esta referenciada no PR.
- Se a User Story exigir Contract governado, o Contract YAML foi criado ou atualizado em `docs/contracts/` e esta referenciado no PR.
- Se a Spec ou o Contract forem relevantes para comportamento observavel, o BDD correspondente foi criado ou atualizado, ou existe dispensa explicita registrada.
- Se a User Story nao exigir Spec ou Contract, isso foi declarado com justificativa curta no backlog, na task ou no PR.
- Quando houver Spec com Touch List, a implementacao respeitou esse escopo.

## 2. Comportamento, Testes e Validacao

- `Behavior change` foi marcado como `YES` ou `NO`.
- Todos os criterios de aceite foram atendidos.
- Existe plano de teste reproduzivel.
- Testes e documentacao foram atualizados quando aplicavel.
- Quando houver Contract governado, requests, responses, exemplos e status codes implementados batem com o YAML versionado.
- Quando o projeto estiver em Nivel 3 ou 4, `make validate-contract` e/ou `make test-contract` foram executados.
- Quando o projeto ainda estiver em Nivel 2, a validacao de contrato foi documental e a ausencia de runner foi registrada.
- Mensagens de erro observaveis seguem `docs/contracts/error_standard.yaml` quando aplicavel e nao sao genericas quando a causa e conhecida.
- Quando houver BDD executavel, o runner foi executado e o comando esta documentado em `docs/context.md`.
- O CI esta verde em `lint`, `test`, `typecheck` e `build`, mais gates opcionais aplicaveis.

## 3. Review, PR e Merge

- A branch segue a convencao do repositorio.
- Os commits seguem Conventional Commits com scope.
- O PR foi aberto com o template completo.
- Quando a sprint foi publicada no GitHub, o PR referencia a issue da US correspondente.
- Spec, Contract e BDD foram linkados no PR quando existirem.
- Assumptions relevantes foram registradas em `docs/assumptions.md` quando aplicavel.
- Ha pelo menos 1 reviewer aprovado.
- Se houver alto risco, arquitetura, seguranca ou mudanca relevante de comportamento, um segundo reviewer foi solicitado.
- Todas as conversas do PR foram resolvidas.
- Existe nota de risco e rollback quando aplicavel.
- O merge esta pronto para `Squash & Merge`.
