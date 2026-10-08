---
description: Deploy da aplicação para ambiente de staging ou produção
---

# Deploy Workflow

Este workflow guia o processo completo de deploy, desde a validação pré-deploy até a confirmação pós-deploy.

## Quando usar

- Ao finalizar uma sprint e querer publicar as entregas
- Para deploy em ambiente de staging para validação com o PO
- Para release em produção após aprovação
- Após correção de bug crítico em produção

## Passos

### 1. Definir Escopo do Deploy

Identifique o que será deployado:

```
Estou preparando deploy para o ambiente [staging/produção]:
- Branch de origem: [nome]
- Sprint/Release: [numero]
- Principais mudanças: [lista resumida]
- Existe rollback plan? [sim/não]
```

---

### 2. Checklist Pré-Deploy

Valide todos os itens antes de prosseguir:

```
Verifique o checklist pré-deploy:

CODE:
- [ ] Branch correta e atualizada com `main`
- [ ] Build local passando sem erros
- [ ] Sem console.error ou warnings críticos
- [ ] Code review concluído e aprovado

CONFIGURAÇÃO:
- [ ] Variáveis de ambiente configuradas no servidor
- [ ] Arquivos .env.production criados (nunca commitar)
- [ ] API_BASE aponta para URL de produção/staging
- [ ] CORS configurado para o domínio de destino

BANCO/BACKEND:
- [ ] Migrações de banco aplicadas (se houver)
- [ ] Conexão com banco de dados testada
- [ ] Dependências instaladas (requirements.txt / package.json)

SEGURANÇA:
- [ ] Nenhum segredo hardcoded no código
- [ ] JWT_SECRET forte definido via variável de ambiente
- [ ] HTTPS habilitado (produção)
```

---

### 3. Preparar Artefatos de Deploy

**Frontend — Build de produção:**
```bash
# Gerar build otimizada
cd frontend
npm run build

# Verificar tamanho e erros
ls -lh dist/
```

**Backend — Verificar dependências:**
```bash
cd backend
pip install -r requirements.txt
# ou
pip freeze > requirements.txt  # se atualizado
```

---

### 4. Deploy por Ambiente

#### Staging (validação com PO)

```bash
# Frontend: copiar dist/ para servidor web ou CDN
# Backend: reiniciar serviço
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Verificar logs de inicialização
tail -f logs/app.log
```

#### Produção

```bash
# Frontend: CDN / Nginx
# Backend: Gunicorn com workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Confirmar que backend está rodando
curl http://[HOST]:8001/health
```

---

### 5. Smoke Tests Pós-Deploy

**Prompt sugerido:**
```
Execute smoke tests básicos no ambiente [staging/produção]:

AUTENTICAÇÃO:
- [ ] Tela de login carrega em < 2s
- [ ] Login com credenciais válidas redireciona para dashboard
- [ ] Login com credenciais inválidas exibe mensagem de erro
- [ ] Logout limpa sessão e redireciona para /login

FUNCIONALIDADES CORE:
- [ ] Dashboard carrega KPIs com dados reais
- [ ] Filtros de ano/área funcionam
- [ ] Top 10 projetos exibido corretamente
- [ ] Chat estratégico responde perguntas

APIs:
- [ ] GET /api/kpis retorna 200
- [ ] GET /api/charts retorna 200
- [ ] POST /api/chat retorna resposta da IA

Registre qualquer anomalia encontrada.
```

---

### 6. Rollback Plan

Se algo der errado:

```
Caso o deploy apresente problemas críticos:

FRONTEND:
- Reverter para build anterior no servidor/CDN
- git revert [commit] && npm run build && redeploy

BACKEND:
- Parar serviço atual
- git checkout [tag/commit anterior]
- Reiniciar com versão anterior

COMUNICAR:
- Notificar stakeholders sobre indisponibilidade
- Estimar tempo de resolução
- Documentar o incidente
```

---

### 7. Documentar o Deploy

Registre no repositório:

```bash
# Criar tag de release
git tag -a v[MAJOR.MINOR.PATCH] -m "Release Sprint [NUMERO]: [descrição breve]"
git push origin v[MAJOR.MINOR.PATCH]

# Commit do changelog/release notes (se houver)
git add CHANGELOG.md
git commit -m "docs: release notes v[versão]"
```

**Prompt sugerido:**
```
Gere as release notes para a versão [X.Y.Z]:

## 🚀 Novidades
- [Feature 1]
- [Feature 2]

## 🐛 Correções
- [Fix 1]

## ⚠️ Breaking Changes
- [Se houver]

## 📋 Como atualizar
[Instruções para o time/usuários]
```

---

### 8. Notificar Stakeholders

Após deploy bem-sucedido:

```
Comunique ao time/PO:

✅ Deploy [staging/produção] concluído com sucesso!

Versão: [X.Y.Z]
Data/Hora: [timestamp]
Ambiente: [URL]
Principais entregas:
- [Feature 1]
- [Feature 2]

Smoke tests: ✅ Todos passando
Próximos passos: [o que esperar / o que testar]
```

---

## Outputs Esperados

- ✅ Aplicação rodando no ambiente alvo
- ✅ Smoke tests passando
- ✅ Tag de release criada no repositório
- ✅ Stakeholders notificados
- ✅ Rollback plan documentado

## Consumo de Contexto (Estimado)
- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimização: [Breve descrição]

## Dicas

- **Nunca** commitar `.env` ou segredos no repositório
- Deploy em **staging primeiro**, sempre — mesmo que pareça simples
- Mantenha o **rollback plan** pronto antes de começar
- Registre **data, versão e responsável** em toda release
- Em produção, prefira deploys em **horários de baixo tráfego**
- Use **feature flags** para ativar funcionalidades gradualmente
