# BDD

Cenarios Gherkin derivados das Specs. Eles materializam comportamento descrito na Spec e nao devem inventar regra nova.

## Regras

- Todo `.feature` deve referenciar a Spec no topo: `# Spec: docs/specs/<nome>.yaml`
- Nao crie ou edite BDD sem Spec correspondente
- Nomenclatura principal: `docs/specs/<nome>.yaml` -> `docs/bdd/<nome>.feature`
- Quando a mesma Spec cobrir dominios distintos, permita mais de um `.feature`, todos apontando para a mesma Spec
- Idioma: portugues
- O comando do runner deve estar documentado em `docs/context.md`

## Template

Use `docs/bdd/bdd_template.feature` como base.
