# Postmortem: [Título Descritivo do Incidente]

**Data do Incidente:** YYYY-MM-DD
**Autores:** [Seu Nome], [Outros Participantes]
**Status:** [Draft / Review / Final]
**Severidade:** [SEV-1 (Crítico) / SEV-2 (Alto) / SEV-3 (Médio)]

---

## 📝 Resumo Executivo
*Uma descrição breve e não técnica do que aconteceu, o impacto e a resolução. Deve ser compreensível para stakeholders de negócio.*

> [Descreva aqui o incidente em 2-3 frases.]

---

## 💥 Impacto
*Métricas quantificáveis sobre o impacto do incidente.*

- **Duração:** [X horas/minutos] (Downtime total ou degradação)
- **Usuários Afetados:** [Número ou % de usuários]
- **Perda de Dados:** [Sim/Não/Detalhes]
- **Impacto Financeiro/Reputacional:** [Descrição breve se aplicável]

---

## 🔍 Causa Raiz (Root Cause Analysis)
*Identificação da causa fundamental do problema. Use a técnica dos 5 Porquês.*

**Causa Imediata:**
> [O que desencadeou o erro diretamente? Ex: O servidor DB ficou sem memória.]

**5 Porquês:**
1. **Por que?** [Ex: O processo do banco consumiu toda a RAM disponível.]
2. **Por que?** [Ex: Uma query não otimizada foi executada repetidamente.]
3. **Por que?** [Ex: O novo endpoint de relatório não tinha paginação.]
4. **Por que?** [Ex: O code review focou na lógica de negócio e não na performance.]
5. **Por que?** [Ex: Não temos checklis de performance para novos endpoints.]

**Causa Raiz:**
> [Conclusão final. Ex: Falta de guidelines de performance e testes de carga para novas features.]

---

## ⏱️ Linha do Tempo (Timeline)
*Cronologia dos eventos, desde o início do problema até a resolução final. Use o fuso horário local.*

- **[HH:MM]** - Início do incidente (ex: deploy da versão v1.2.3).
- **[HH:MM]** - Primeiro alerta disparado / Reporte de usuário.
- **[HH:MM]** - Time de engenharia começa investigação.
- **[HH:MM]** - Identificada a causa (query lenta).
- **[HH:MM]** - Ação de mitigação (rollback ou hotfix).
- **[HH:MM]** - Serviço restabelecido (resolução).
- **[HH:MM]** - Monitoramento pós-incidente concluído.

---

## 🎓 Lições Aprendidas

### O que correu bem? (What went well)
*Coisas que funcionaram como esperado (ex: monitoramento, comunicação, rollback rápido).*
- [ ] O alerta disparou em menos de 5 minutos.
- [ ] O sistema de rollback funcionou perfeitamente.

### O que correu mal? (What went wrong)
*Coisas que falharam ou podem ser melhoradas (ex: demora na detecção, falta de logs).*
- [ ] Demoramos 30min para achar os logs relevantes.
- [ ] A pessoa on-call não tinha acesso à ferramenta X.

### Onde tivemos sorte? (Where we got lucky)
*Fatores aleatórios que ajudaram (ex: aconteceu num horário de baixo tráfego).*
- [ ] Ocorreu durante o almoço, com baixo volume de usuários.

---

## 🚀 Action Items (Plano de Ação)
*Tarefas específicas para corrigir a causa raiz e prevenir reincidência. Devem ter donos e prazos.*

| Tarefa | Tipo | Prioridade | Responsável | Prazo | Status |
|--------|------|------------|-------------|-------|--------|
| Adicionar paginação na API de relatórios | Correção | Alta | @dev1 | DD/MM | TODO |
| Criar checklist de performance para Code Review | Processo | Média | @techlead | DD/MM | TODO |
| Adicionar alerta de memória no DB | Monitoramento | Alta | @sre | DD/MM | TODO |

---

## 📚 Referências
*Links para tickets do Jira, logs, dashboards, PRs, etc.*

- [Jira Ticket-123](#)
- [Dashboad Datadog/Grafana](#)
- [Pull Request #456](#)
