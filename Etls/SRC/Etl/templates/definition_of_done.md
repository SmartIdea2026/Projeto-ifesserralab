# Definition of Done

Este documento define os criterios que devem ser atendidos para que uma **User Story** ou **Task** seja considerada "Done" (concluida).

---

## 1. Rastreabilidade e Governanca

- [ ] A tarefa esta ligada a uma User Story, Spec, Contract, ticket ou ADR rastreavel.
- [ ] Quando o time usar GitHub Planning, as issues relevantes de Epic, US e Task estao vinculadas.
- [ ] Foi decidido explicitamente se a US exige Spec governada.
- [ ] Foi decidido explicitamente se a US exige Contract governado.
- [ ] Se a US exigir Spec, a Spec YAML foi criada ou atualizada.
- [ ] Se a US exigir Contract, o Contract YAML foi criado ou atualizado.
- [ ] Se a Spec ou o Contract forem relevantes para comportamento observavel, o BDD correspondente foi criado ou atualizado.
- [ ] Se a US nao exigir Spec ou Contract, a dispensa foi registrada com justificativa.
- [ ] Quando houver Spec governada, a Touch List foi respeitada.

---

## 2. Codigo, Review e Seguranca

- [ ] Codigo segue os padroes de codificacao do projeto.
- [ ] Codigo esta limpo, legivel e bem estruturado.
- [ ] Nao ha segredos, `.env` ou dados sensiveis expostos.
- [ ] Tratamento adequado de erros foi implementado.
- [ ] Mensagens de erro observaveis seguem o padrao compartilhado quando aplicavel.
- [ ] Code review foi solicitado.
- [ ] Ha pelo menos 1 aprovacao de outro desenvolvedor.
- [ ] Todos os comentarios do review foram resolvidos.
- [ ] Se houver alto risco, arquitetura, seguranca ou mudanca relevante de comportamento, um segundo reviewer foi solicitado.

---

## 3. Testes e Validacao

- [ ] Testes unitarios escritos e passando.
- [ ] Testes de integracao ou e2e passando quando aplicavel.
- [ ] Testes existentes nao foram quebrados.
- [ ] Edge cases relevantes foram testados.
- [ ] Existe plano de teste reproduzivel.
- [ ] Quando houver Contract governado, requests, responses e exemplos foram validados.
- [ ] Quando houver BDD executavel, o runner foi executado e o comando esta documentado.
- [ ] Build local e CI estao passando.

---

## 4. Comportamento e Documentacao

- [ ] Todos os criterios de aceitacao da User Story foram atendidos.
- [ ] `Behavior change` foi marcado como `YES` ou `NO`.
- [ ] O comportamento alterado esta descrito na Spec, no Contract ou no PR quando aplicavel.
- [ ] README, `docs/context.md` e documentacao afetada foram atualizados quando necessario.
- [ ] Risco e rollback foram documentados quando aplicavel.

---

## 5. Checklist Final

- [ ] Branch segue a convencao do repositorio.
- [ ] Commits seguem Conventional Commits com scope.
- [ ] PR esta completo com links para US, Spec, Contract e BDD quando aplicavel.
- [ ] Quando a sprint foi publicada no GitHub, o PR linka a issue da US correspondente.
- [ ] Todas as conversas foram resolvidas.
- [ ] Nenhum bloqueador ativo impede o merge.

---

## Notas

- Nem toda User Story exige Spec governada.
- Nem toda User Story exige Contract governado.
- Alguns itens podem nao se aplicar, mas a dispensa deve ser explicita.
- Revise este DoD regularmente nas retrospectivas.
