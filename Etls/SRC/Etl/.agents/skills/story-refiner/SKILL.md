---
name: Story Refiner
description: Transforma ideias brutas em User Stories completas seguindo o padrão INVEST e os templates do projeto.
---

# Story Refiner Skill

Esta skill especializa o agente em atuar como um **Product Owner Técnico**.
Seu objetivo é pegar uma frase simples (ex: "Quero login com Google") e transformar em um arquivo de User Story completo.

## 🧠 Capability
Ao ser invocado para refinar uma história, você deve:

1. **Análise INVEST**:
   - **I**ndependent: A história pode ser feita sozinha?
   - **N**egotiable: O escopo está aberto a conversa?
   - **V**aluable: Qual o valor de negócio real?
   - **E**stimable: É possível estimar?
   - **S**mall: Cabe em uma sprint?
   - **T**estable: Tem critérios de aceitação claros?

2. **Geração de Arquivo**:
   - Use o template padrão de User Story do projeto (`docs/stories/US-XXX_titulo.md`).
   - Preencha:
     - **The Why**: "Como <Persona>, Quero <Ação>, Para <Valor>"
     - **Acceptance Criteria**: Lista de checkboxes verificáveis.
     - **Tech Notes**: Sugestões de implementação (Frontend/Backend/DB).

## 🔗 Relação com Work Classification

- **LIGHT PROCESS:** use este roteiro diretamente, ideia → Story, como descrito abaixo.
- **NORMAL PROCESS/HEAVY PROCESS:** esta skill é acionada a partir do Passo 0 (Modo Backlog) de `/create-user-story`, usando um `docs/requirements/<slug>.md` com `REQUIREMENTS_READY` já aprovado como insumo — não a partir da ideia bruta. Ver `docs/discovery_requirements.md`.

## 📝 Instruções de Uso

Quando o usuário pedir "Refine a história X" ou "Crie uma skill para Y", siga este roteiro:

1. **Identifique a Próxima ID**:
   - Verifique a pasta `docs/stories/` e `docs/product_backlog.md`, quando existir, para achar o próximo número (ex: US-004).

2. **Crie o Arquivo**:
   - Caminho: `docs/stories/US-XXX_nome_da_story.md`.

3. **Valide**:
   - Antes de finalizar, pergunte a si mesmo: "Um dev Junior conseguiria implementar isso só lendo este arquivo?"

---

## Exemplo de Input/Output

**Input:** "O aluno precisa ver as notas dele."

**Output (Conteúdo do Arquivo):**
```markdown
# User Story: Visualização de Notas
**Como** Aluno
**Quero** visualizar minhas notas lançadas
**Para que** eu possa acompanhar meu desempenho acadêmico

## Critérios de Aceitação
- [ ] Deve exibir lista de matérias e notas
- [ ] Deve destacar notas abaixo da média em vermelho
```
