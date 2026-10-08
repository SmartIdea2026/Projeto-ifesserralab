---
description: Executar testes End-to-End com Playwright para validar fluxos críticos da aplicação
---

# E2E Test Workflow (Playwright)

Este workflow guia a criação e execução de testes End-to-End usando **Playwright**, cobrindo os fluxos críticos definidos nas User Stories da sprint atual.

## Quando usar

- Antes de um deploy (staging ou produção)
- Ao finalizar uma feature que impacta fluxos de usuário
- Como parte do code review de US com interface visual

## Pré-requisitos

- Playwright instalado (`npx playwright install`)
- Aplicação rodando localmente
- User Stories da sprint com critérios de aceitação definidos

---

## Passos

### 1. Verificar Ambiente

// turbo
```bash
# Instalar Playwright se necessário
npx playwright install --with-deps chromium

# Confirmar que a aplicação está rodando
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
```

### 2. Identificar Fluxos para Testar

Peça à IA para identificar os fluxos prioritários:

**Prompt sugerido:**
```
Com base nas User Stories concluídas nesta sprint (verifique docs/sprints/sprint_planning_NN.md),
identifique os 3-5 fluxos mais críticos para cobrir com testes E2E.

Priorize:
- Fluxos de autenticação (login/logout)
- Fluxo principal de negócio (happy path)
- Fluxos com validação de dados
- Fluxos que envolvem persistência (criar, editar, excluir)
```

### 3. Gerar Testes Playwright

**Prompt sugerido:**
```
Gere testes Playwright para o fluxo: [nome do fluxo]

Requisitos:
- Use Page Object Model (POM) para organizar seletores
- Prefira seletores semânticos: getByRole, getByLabel, getByText
- Evite seletores frágeis (CSS classes, XPath)
- Inclua assertions claras após cada ação
- Cubra: Happy Path + pelo menos 1 cenário de erro
- Adicione comentários explicando o cenário

Estrutura de arquivo esperada:
tests/e2e/[nome-do-fluxo].spec.ts
```

**Exemplo de teste gerado:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('login com credenciais válidas redireciona para dashboard', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByLabel('Email').fill('usuario@exemplo.com');
    await page.getByLabel('Senha').fill('senha_segura');
    await page.getByRole('button', { name: 'Entrar' }).click();
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('credenciais inválidas exibem mensagem de erro', async ({ page }) => {
    await page.goto('/login');

    await page.getByLabel('Email').fill('usuario@exemplo.com');
    await page.getByLabel('Senha').fill('senha_errada');
    await page.getByRole('button', { name: 'Entrar' }).click();

    await expect(page.getByRole('alert')).toContainText('Credenciais inválidas');
  });
});
```

### 4. Criar Configuração Playwright (primeira vez)

Se ainda não existir `playwright.config.ts` no projeto:

**Prompt sugerido:**
```
Crie o arquivo playwright.config.ts para este projeto.

Configurações necessárias:
- baseURL: http://localhost:5173
- Browser: Chromium (padrão), Firefox e WebKit opcionais
- Timeout por teste: 30s
- Retries em CI: 2
- Reporter: HTML (local) e List (CI)
- Screenshots: apenas em falha
- Pasta de testes: tests/e2e/
```

### 5. Executar os Testes

// turbo
```bash
# Executar todos os testes E2E
npx playwright test

# Executar apenas um arquivo específico
npx playwright test tests/e2e/login.spec.ts

# Executar com interface visual (útil para debug)
npx playwright test --ui

# Gerar relatório HTML
npx playwright show-report
```

### 6. Analisar Resultados

Se houver falhas, peça à IA para ajudar:

**Prompt sugerido:**
```
O teste [nome] falhou com o erro:
[cole o erro do terminal]

Analise:
- Qual é a causa raiz da falha?
- É um bug no código ou no teste?
- Se for no teste: sugira a correção do seletor ou assertion
- Se for no código: descreva o comportamento esperado vs. atual
```

### 7. Documentar Cobertura E2E

Após os testes passarem:

**Prompt sugerido:**
```
Com base nos testes E2E executados, gere um resumo de cobertura:

| Fluxo | Cenários Cobertos | Status |
|-------|-------------------|--------|

Inclua os fluxos ainda sem cobertura E2E para priorizar na próxima sprint.
```

// turbo
```bash
# Commit dos testes
git add tests/e2e/ playwright.config.ts
git commit -m "test: E2E tests for [sprint/feature]"
```

---

## Estrutura de Pastas Recomendada

```
tests/
└── e2e/
    ├── fixtures/          ← Dados de teste reutilizáveis
    ├── pages/             ← Page Object Models (POM)
    │   ├── LoginPage.ts
    │   └── DashboardPage.ts
    ├── login.spec.ts
    ├── main-flow.spec.ts
    └── ...
playwright.config.ts
```

## Outputs Esperados

- ✅ Testes E2E cobrindo os fluxos críticos das User Stories
- ✅ Relatório de resultados gerado (`playwright-report/`)
- ✅ Testes commitados no repositório
- ✅ Resumo de cobertura documentado

## Consumo de Contexto (Estimado)
- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimização: [Breve descrição]

## Dicas

- **Prefira `getByRole` e `getByLabel`** — são resilientes a mudanças de CSS
- **Use `test.describe` para agrupar** cenários do mesmo fluxo
- **Nunca use `page.waitForTimeout`** — use `waitFor` com assertions
- **Page Object Model** facilita manutenção quando a UI muda
- **Testes E2E são lentos** — mantenha focados nos fluxos realmente críticos
- **Rode em CI com `--reporter=list`** para output limpo em logs
