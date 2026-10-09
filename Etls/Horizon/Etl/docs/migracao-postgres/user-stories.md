# Épico e User Stories: carga do Horizon em PostgreSQL

Formato dos modelos em `.agent/templates/`. Os números de issue ficam como `#[a definir]` até a criação no GitHub. A coluna "Commits" mostra o que já está entregue na branch `feat/32-horizon-etl-base`.

# [Epic] #[a definir]: Carga do ETL Horizon em PostgreSQL

## 🎯 Goal
Gravar os dados do SigPesq, CNPq e Lattes num PostgreSQL em Docker com o modelo lógico do Horizon, para unir a base às demais no painel do Campus Serra.

## 📋 User Stories
- [x] US-1 Banco do Horizon no Docker
- [x] US-2 Schema a partir do modelo lógico
- [x] US-3 Repositórios por família de tabelas
- [x] US-4 Carga do SigPesq
- [x] US-5 Sincronização com o CNPq
- [x] US-6 Carga dos currículos Lattes
- [x] US-7 Pipeline de carga com relatório
- [ ] US-8 Verificação com dados reais
- [ ] US-9 Exports a partir do banco novo

## ⚙️ Engineering Standards
Arquitetura em portas e adaptadores · Persistência SQL (PostgreSQL) · TDD · black, isort, flake8.

---

# [US] #[a definir]: US-1 Banco do Horizon no Docker
**Epic**: #[a definir] · **Commits**: `7dd38a5`

## 📝 Persona & Need
Como desenvolvedor, quero um PostgreSQL separado do Prefect, para gravar os dados do Horizon sem misturar bancos.

## 📋 Sub-Tasks
- [x] Serviço `horizon-db` com volume e healthcheck
- [x] Variáveis `HORIZON_*` no `.env.example`

## ✅ Definition of Ready
- [x] Requisitos entendidos · [x] Abordagem definida · [x] Critérios definidos

## 🏁 Acceptance Criteria
1. `docker compose up -d horizon-db` deixa o serviço `healthy`.
2. O banco do Prefect (porta 5433) não muda.

---

# [US] #[a definir]: US-2 Schema a partir do modelo lógico
**Epic**: #[a definir] · **Commits**: `7c27d67`

## 📝 Persona & Need
Como desenvolvedor, quero criar as 33 tabelas a partir de `ModeloLogicoHorizon.sql` de forma repetível, para que o modelo continue sendo a fonte da verdade.

## 📋 Sub-Tasks
- [x] Script de criação (`src/db/esquema_horizon.py`) e `make horizon-db-schema`
- [x] Ajustes para o PostgreSQL (`TIMESTAMP`, ids gerados, textos sem limite, unicidade de bolsa)
- [x] Dados iniciais (tipos)
- [x] Testes do schema

## 🏁 Acceptance Criteria
1. O `.sql` não é editado.
2. Aplicar duas vezes dá o mesmo resultado, com 33 tabelas.

---

# [US] #[a definir]: US-3 Repositórios por família de tabelas
**Epic**: #[a definir] · **Commits**: `f121c03`, `ebfb0cb`, `2c4d8b4`, `8fb9d19`, `d905cda`

## 📝 Persona & Need
Como desenvolvedor, quero gravar por repositórios atrás de portas, para trocar a carga sem depender das libs antigas.

## 📋 Sub-Tasks
- [x] Pessoas · [x] Organizações e formações · [x] Equipes e áreas · [x] Iniciativas · [x] Produções

## 🏁 Acceptance Criteria
1. Todas as 33 tabelas têm repositório testado no PostgreSQL.
2. Repositórios não fazem commit e não derrubam a transação em casos esperados.

---

# [US] #[a definir]: US-4 Carga do SigPesq
**Epic**: #[a definir] · **Commits**: `e395062`, `937028a`, `3e18162`, `67db017`

## 📝 Persona & Need
Como analista do campus, quero grupos, projetos e bolsistas do SigPesq no banco novo, para ver a pesquisa e a extensão do campus.

## 📋 Sub-Tasks
- [x] Base da carga (contexto, relatório, regras)
- [x] Grupos · [x] Projetos e bolsistas · [x] Enriquecimento pelos documentos PJ

## 🏁 Acceptance Criteria
1. Só projetos aprovados entram; a situação usa os 4 valores em português.
2. Bolsistas viram orientações filhas do projeto, com bolsa e financiadora.
3. O que não pôde ser gravado aparece no relatório.

---

# [US] #[a definir]: US-5 Sincronização com o CNPq
**Epic**: #[a definir] · **Commits**: `f1603cf`

## 📝 Persona & Need
Como analista, quero membros, líderes e linhas de pesquisa dos grupos vindos do CNPq, para completar os grupos.

## 🏁 Acceptance Criteria
1. Papéis fixos de equipe; egresso é o papel base com data de fim.
2. Filtro opcional por campus.

---

# [US] #[a definir]: US-6 Carga dos currículos Lattes
**Epic**: #[a definir] · **Commits**: `8ab7008`

## 📝 Persona & Need
Como analista, quero perfis, formações, produções e projetos do Lattes, para ligar pessoas às suas produções.

## 🏁 Acceptance Criteria
1. Dono do currículo casado pelo ID Lattes e depois pelo nome; homônimo vira pessoa separada e vai para revisão.
2. Projetos e orientações já existentes são juntados sem sobrescrever dados do SigPesq.
3. Coautores só quando casam com pessoa já existente.

---

# [US] #[a definir]: US-7 Pipeline de carga com relatório
**Epic**: #[a definir] · **Commits**: `071204e`

## 📝 Persona & Need
Como operador, quero um comando único que recria o banco e carrega tudo, para repetir a carga com segurança.

## 🏁 Acceptance Criteria
1. `make pipeline-postgres` termina em `Completed` e grava `data/reports/carga_postgres.json`.
2. O relatório é gravado mesmo quando a carga falha.
3. O pipeline antigo (SQLite) continua funcionando.

---

# [US] #[a definir]: US-8 Verificação com dados reais *(pendente)*
**Epic**: #[a definir]

## 📝 Persona & Need
Como responsável pelo ETL, quero rodar com dados reais e comparar com o pipeline antigo, para confiar nas contagens.

## 📋 Sub-Tasks
- [ ] Obter dados (credenciais do SigPesq em `Etl/.env` ou arquivos em `Etl/data/`)
- [ ] Rodar `make pipeline-postgres` e comparar contagens com o SQLite
- [ ] Conferir chaves e restrições
- [ ] Fechar a lista de pendências (itens descartados e pulados)

## 🏁 Acceptance Criteria
1. Contagens por tabela comparadas e diferenças explicadas.
2. Relatório sem pendências inesperadas.

---

# [US] #[a definir]: US-9 Exports a partir do banco novo *(pendente)*
**Epic**: #[a definir]

## 📝 Persona & Need
Como consumidor do `horizon_dashboard`, quero os exports (JSON, marts, grafos) gerados a partir do banco novo.

## 🏁 Acceptance Criteria
1. Os 4 leitores do banco (`canonical_exporter`, `research_group_exporter`, `export_campus_resolver`, `mart_generator`) leem o schema novo.
2. O formato dos arquivos atuais é mantido, ou as mudanças são acordadas com o dashboard.
