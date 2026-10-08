# Engineering Playbook

## 1. Objetivo
Padronizar a colaboração de times pequenos (3 pessoas) de forma agnóstica de IDE, editor ou agente.

## 2. Princípios Operacionais
- Agile + Spec-Anchored: toda mudança nasce de story, spec, ticket ou ADR rastreável.
- Trunk-based leve: `main` é a única trunk e deve permanecer verde.
- Branches curtas, PRs pequenos e feedback rápido.
- O framework não depende de uma IDE específica; integrações por ferramenta são adaptadores, não a fonte canônica.
- Adoção progressiva: use o menor nivel suficiente do `docs/maturity_model.md` e so ative mocks, tipos gerados, Docker ou testes de contrato quando a stack pedir.
- Um agente principal deve ser dono do fluxo, da integracao final e do relatorio ao usuario.
- Sidecars so entram quando o trabalho puder ser paralelizado com risco baixo.
- Artefatos canonicos de planejamento e governanca devem seguir politica de single writer.

## 3. Governança de User Story, Spec, Contract e BDD
- Use este playbook como visão geral do processo.
- A regra canônica de quando uma US exige Spec, quando BDD é obrigatório e como usar Touch List está em `docs/decisoes_governanca_us_spec_bdd.md`.
- A regra de niveis 0-4 está em `docs/maturity_model.md`.
- Antes da implementação, trate a decisão `US exige Spec?` como um gate obrigatório do fluxo.
- Antes de alterar qualquer boundary observavel, trate a decisao `US exige Contract?` como gate obrigatorio. Se exigir Contract, comece documentado em Nivel 2 e so suba para Nivel 3/4 quando houver runner real.

## 4. Fluxo Padrão para Times Pequenos
- Ninguém commita ou faz push direto em `main`.
- Toda mudança sai de `main`, vive pouco tempo e volta por PR.
- Use `feat/<id>-<slug>`, `fix/<id>-<slug>` ou `refactor/<id>-<slug>`.
- Para processo/documentação, `docs/<id>-<slug>` e `chore/<id>-<slug>` são aceitáveis.
- Quando o time usar GitHub Issues/Projects para planejamento, publique backlog e sprint com um único workflow de sincronização antes do desenvolvimento da sprint.
- Quando houver delegacao entre agentes, defina o write scope antes de paralelizar trabalho.
- Prefira paralelismo de leitura primeiro; paralelismo de escrita so com escopos exclusivos.

## 5. Delegacao Leve
- Modelo padrao: `1 agente principal + sidecars pontuais`.
- `Explorer sidecars`: leitura, analise, inventario, code search e review especializado.
- `Worker sidecars`: implementacao apenas com write scope exclusivo e delimitado.
- Nao use multiplos agentes escrevendo no mesmo artefato canonico.
- Nao delegue trabalho que bloqueia a proxima acao imediata do agente principal.
- Nao delegue tarefas pequenas, sequenciais ou altamente acopladas.
- Use `templates/context_summary.md` para handoff curto antes de delegacao relevante.
- Adocao recomendada: piloto controlado, depois expansao seletiva baseada em ganho real.

## 6. Commits
- Use Conventional Commits com scope: `feat(api): ...`, `fix(etl): ...`, `docs(repo): ...`.
- Inclua o ID da US, Spec, ticket ou tarefa na descrição do commit ou no título do PR.
- Prefira commits pequenos e frequentes na branch.

## 7. Pull Requests
- PR é obrigatório para merge em `main`.
- Todo PR deve conter: link da US, spec ou ticket; o que mudou; como testar; riscos/rollback; `Behavior change: YES/NO`.
- Quando houver Spec governada, o PR deve linkar a Spec e o BDD correspondente quando existir.
- Quando a US não exigir Spec, o PR deve declarar isso explicitamente.
- Quando a US já tiver issue publicada no GitHub, o PR deve linkar a issue correspondente.
- Regra padrão: mínimo de 1 reviewer aprovado.
- Para arquitetura, segurança, impacto transversal ou mudança relevante de comportamento, solicite um segundo reviewer.

## 8. CI e Qualidade
- O merge só acontece com CI verde.
- Os gates padrão do framework são: `lint`, `test`, `typecheck` e `build`.
- Em repositórios derivados deste template, esses gates devem ser expostos no root como `make lint`, `make test`, `make typecheck` e `make build`.
- Gates opcionais de rastreabilidade tecnica sao `validate-contract`, `test-contract`, `test-bdd`, `test-mock` e `test-all`.
- Comandos locais, validadores de contrato e runner BDD devem ser documentados em `docs/context.md`.

## 9. Merge
- Estratégia padrão: `Squash & Merge`.
- Se houver mudança de comportamento, isso deve estar explícito no PR e na Spec quando aplicável.
- Branches devem ser removidas após o merge.

## 10. Fluxo Operacional Resumido
1. Refinar a US e seus critérios de aceite.
2. Escolher o nivel ScrumAIDev minimo para a mudanca.
3. Decidir se a US exige Spec governada.
4. Decidir se a US exige Contract governado.
5. Se exigir, criar ou atualizar a Spec YAML e derivar BDD quando a Spec for relevante.
6. Se exigir Contract, criar ou atualizar YAML em `docs/contracts/` antes de implementar o boundary.
7. Se nao exigir Spec ou Contract, registrar a dispensa com justificativa curta.
8. Planejar a sprint.
9. Publicar backlog e sprint no GitHub quando o time usar Issues/Projects.
10. Se houver delegacao, definir agente principal, sidecars e write scopes antes de paralelizar.
11. Criar branch curta a partir de `main`.
12. Implementar respeitando Touch List, Contract e padrao de erro quando existirem.
13. Rodar checks locais, validadores de contrato e runner BDD quando aplicavel.
14. Abrir PR com links para US, Spec, Contract, issue e BDD ou com justificativas de dispensa.
15. Fazer merge via squash apos CI verde, aprovacao e conversas resolvidas.

## 11. Release Policy do Framework
- `main` representa integração contínua do framework.
- Releases estáveis do processo/template devem ser marcadas por tag semântica.
- Nem todo merge em `main` precisa gerar release.

## 12. Configuração Obrigatória no GitHub
- Bloquear push direto em `main`.
- Exigir PR para merge.
- Exigir 1 aprovação mínima.
- Exigir conversas resolvidas.
- Exigir checks `lint`, `test`, `typecheck` e `build`.
- Habilitar apenas `Squash & Merge` se o time quiser enforcement total.
