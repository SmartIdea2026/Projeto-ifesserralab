# 🌿 Git Workflow — ScrumAIDev

Política Git/PR do framework, agnóstica de IDE, editor ou agente.

## Estratégia de Branches

Fluxo padrão para times pequenos (3 pessoas), escalável para times maiores.

```text
main
├── feat/F-001-login-usuario
├── fix/B-014-validacao-email
├── refactor/ARCH-003-separar-servicos
└── docs/OPS-001-atualizar-playbook
```

| Branch | Uso | Criado por |
|---|---|---|
| `main` | Trunk estável e sempre verde | Merge via PR |
| `feat/<id>-<slug>` | Nova funcionalidade ancorada em spec/ticket | Dev ou agente |
| `fix/<id>-<slug>` | Correção de bug | Dev ou agente |
| `refactor/<id>-<slug>` | Refatoração sem mudança funcional intencional | Dev ou agente |
| `docs/<id>-<slug>` | Documentação, playbooks e artefatos de processo | Dev ou agente |
| `chore/<id>-<slug>` | Infra/configuração sem mudança de produto | Dev ou agente |

## Convenção de Commits

Formato: `<tipo>(<escopo>): <descrição>`

Regras:
- use escopo semântico (`api`, `etl`, `ui`, `docs`, `repo`, `story`, `ci`)
- mantenha o ID da spec/ticket na descrição do commit ou no título do PR
- prefira commits pequenos e frequentes dentro da branch
- quando houver Spec governada, versione Spec e BDD no mesmo PR do código ou de forma rastreável

```bash
feat(api): adicionar validação de email no login [F-003]
fix(etl): corrigir redirecionamento após timeout [B-005]
docs(repo): adicionar retrospectiva da sprint 2 [OPS-002]
test(api): adicionar casos de teste para validação de email [F-003]
chore(ci): ajustar pipeline de validação [OPS-003]
```

> Configure o template local: `git config commit.template .gitmessage`

## Fluxo de uma Feature

```bash
# 1. Criar branch curta a partir de main
git checkout -b feat/F-003-validacao-email

# 2. Desenvolver seguindo o workflow /feature-development
# (commits pequenos e frequentes)

# 3. Antes de desenvolver uma sprint planejada, publique backlog/sprint
#    no GitHub com /publish-github-planning quando o time usar Issues/Projects

# 4. Push e abrir PR obrigatório
git push origin feat/F-003-validacao-email

# 5. Preencher PR com link da US/spec/ticket, Behavior change YES/NO,
#    como testar, riscos/rollback e links para Issue/Spec/BDD quando existirem

# 6. Merge somente com CI verde, 1 aprovação e conversas resolvidas
#    Para arquitetura, segurança ou mudança de comportamento,
#    solicite um segundo reviewer

# 7. Merge preferencialmente via Squash & Merge
#    e exclusão da branch após merge
```

## Releases e Tags

Para este framework/template, `main` recebe integração contínua; releases estáveis devem ser versionadas por tag quando houver um baseline pronto para reuso:

```bash
git tag -a v1.0.0 -m "Release Sprint 01: autenticação e dashboard"
git push origin v1.0.0
```

Versionamento semântico: `MAJOR.MINOR.PATCH`
- **MAJOR:** mudança disruptiva (breaking change)
- **MINOR:** nova feature (backward compatible)
- **PATCH:** bug fix

## Regras Invioláveis

- ❌ **Nunca** commite ou faça push diretamente em `main`
- ❌ **Nunca** commite arquivos `.env` ou segredos
- ✅ **Sempre** use PRs para merge em `main`
- ✅ **Sempre** linke Spec e BDD no PR quando a mudança for governada por esses artefatos
- ✅ **Sempre** linke a issue da US no PR quando o planejamento estiver publicado no GitHub
- ✅ **Sempre** exija CI verde, 1 aprovação e conversas resolvidas antes do merge
- ✅ **Prefira** `Squash & Merge` para manter a trunk limpa
- ✅ **Sempre** verifique o número correto da sprint antes de criar arquivos
