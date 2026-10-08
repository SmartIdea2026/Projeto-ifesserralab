# Context Summary Template

> Use ao retomar trabalho pausado ou em sessoes longas.
> Evita releitura desnecessaria.

---

**Projeto:** [nome]  
**Data:** YYYY-MM-DD  
**Sprint atual:** Sprint NN  
**Branch ativa:** `feat/<id>-<slug>`

## Estado Resumido

| Item | Valor |
|---|---|
| Sprint goal | [copie do sprint_planning_NN.md] |
| Story em andamento | US-XXX - [titulo] |
| US issue | [#123 ou URL] |
| Spec em uso | [docs/specs/<nome>.yaml ou "US nao exige Spec"] |
| Contract em uso | [docs/contracts/<nome>.yaml ou "US nao exige Contract"] |
| BDD relacionado | [docs/bdd/<nome>.feature ou N/A] |
| Sprint iteration/milestone | [URL ou N/A] |
| Delegation mode | [single-agent / read-parallel / write-parallel-exclusive] |
| Principal agent | [nome ou N/A] |
| Active sidecars | [nenhum / lista curta] |
| Behavior change | [YES/NO] |
| Bloqueadores | [nenhum / descreva] |

## Contexto Tecnico

- Stack ativa: [Vue 3 / React / FastAPI / outro]
- Arquivos modificados hoje: [lista curta]
- Write scope atual: [arquivos ou pastas que podem receber escrita]
- Artefatos protegidos: [lista curta de artefatos canonicos]
- Decisao arquitetural recente: [se houver, ou "nenhuma"] -> ADR-NNN
- Runner BDD utilizado: [comando ou N/A]
- Validador de Contract utilizado: [comando ou N/A]
- Handoff para sidecar: [nenhum / objetivo curto + escopo]

## Proxima Acao

```text
[descreva exatamente o que o agente deve fazer a seguir]
```

---

> **Instrucao ao agente:** use este arquivo como contexto principal para retomar o trabalho.
> Expanda apenas se necessario, comecando por `docs/project_manifest.md`.
