---
name: scrumaidev-scope-idea
description: Run the ScrumAIDev `scope-idea` workflow for this repository. Use when the user explicitly asks for `scope-idea` or when that ScrumAIDev process step is the appropriate next action.
---

# ScrumAIDev — scope-idea

Execute the canonical ScrumAIDev workflow for `scope-idea`.

1. Read `.agents/workflows/scope-idea.md` completely before acting.
2. Treat that workflow file as the canonical process definition; do not replace it with this skill facade.
3. Follow the project `AGENTS.md` chain and `.scrumaidev/AGENTS.md` as the ScrumAIDev operating contract.
4. Use the user's current request and the active conversation as the workflow input; preserve any constraints already stated.
5. Preserve the model and configuration already selected in the current Antigravity session. This skill does not select or override a model.
6. If the canonical workflow requires an explicit human review/approval gate, stop at that gate and ask for the required decision instead of auto-approving it.
7. When the canonical workflow refers to another workflow as `/<workflow>`, the Antigravity invocation is `/scrumaidev-<workflow>`.

Canonical workflow: `.agents/workflows/scope-idea.md`
