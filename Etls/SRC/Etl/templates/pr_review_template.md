# PR Review Template

Use antes de abrir o PR ou antes de aprovar o merge.

## Dados do PR

- **ID relacionado:** _(ex: F-001, US-42)_
- **Branch:** _(ex: feat/F-001-login-form)_
- **Epic Issue:** _(URL ou N/A)_
- **US Issue:** _(URL ou N/A)_
- **Spec:** _(arquivo em docs/specs/ ou "US nao exige Spec")_
- **Contract:** _(arquivo em docs/contracts/ ou "US nao exige Contract")_
- **BDD:** _(arquivo em docs/bdd/ ou N/A)_
- **Behavior change:** YES | NO

## Checklist de revisao

### Comportamento e rastreabilidade

- [ ] As alteracoes estao alinhadas com a US, com a Spec e com o Contract quando houver
- [ ] A issue da US corresponde ao escopo realmente entregue
- [ ] Nao ha mudanca silenciosa de comportamento
- [ ] Se nao houver Spec, a dispensa esta registrada
- [ ] Se nao houver Contract, a dispensa esta registrada

### Codigo e seguranca

- [ ] Codigo segue `docs/context.md`
- [ ] Nao ha segredos, `.env` ou dados sensiveis commitados
- [ ] Refatoracoes preservam comportamento externo
- [ ] Mensagens de erro observaveis nao expem dados sensiveis

### Testes e validacao

- [ ] Testes relevantes foram executados
- [ ] Contrato e exemplos foram validados quando aplicavel
- [ ] Runner BDD foi executado quando aplicavel
- [ ] Comandos usados estao claros no PR ou em `docs/context.md`

### Documentacao e DoD

- [ ] Documentacao afetada foi atualizada
- [ ] Assumptions foram registradas em `docs/assumptions.md` quando aplicavel
- [ ] Checklist de `docs/definition_of_done.md` foi atendido

## Resultado

- [ ] Aprovado
- [ ] Ajustes necessarios

**Ajustes:**

_(listar itens a corrigir)_
